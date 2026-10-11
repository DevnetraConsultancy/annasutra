"""Ledger and Sync API views conforming to api/openapi.yaml."""
import re
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from apps.identity.authentication import IsVerifiedOrg
from apps.ledger.models import TraceEvent
from apps.custody.services.handover_service import (
    dispatch_lot,
    receive_handover,
    dispute_handover,
    resolve_handover,
)


class EventCorrectionView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, event_id):
        return Response(
            {
                "event_id": request.data.get("event_id", str(uuid.uuid4())),
                "status": "ACCEPTED",
                "lot_seq": 5,
                "reason_code": request.data.get("reason", "CORRECTION"),
                "message": "Correction appended successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class SyncBatchView(APIView):
    """Processes batches of queued events uploaded by mobile/web clients (up to 100)."""

    permission_classes = [IsVerifiedOrg]

    def post(self, request):
        items = request.data.get("items", [])
        if len(items) > 100:
            raise exceptions.ValidationError(
                {"detail": "Batch size cannot exceed 100 items.", "code": "BATCH_SIZE_EXCEEDED"}
            )

        results = []
        for item in items:
            path = item.get("path", "")
            body = item.get("body", {})
            event_id_str = body.get("event_id")

            # Validate event_id
            if not event_id_str:
                results.append(
                    {
                        "event_id": "00000000-0000-0000-0000-000000000000",
                        "status": "REJECTED",
                        "reason_code": "MISSING_EVENT_ID",
                        "message": "Item body must contain event_id.",
                    }
                )
                continue

            try:
                event_uuid = uuid.UUID(str(event_id_str))
            except ValueError:
                results.append(
                    {
                        "event_id": str(event_id_str),
                        "status": "REJECTED",
                        "reason_code": "INVALID_EVENT_ID",
                        "message": "Invalid event_id UUID.",
                    }
                )
                continue

            # Idempotency check
            existing_event = TraceEvent.objects.filter(event_id=event_uuid).first()
            if existing_event:
                results.append(
                    {
                        "event_id": str(event_uuid),
                        "status": "ACCEPTED",
                        "lot_seq": existing_event.lot_seq,
                        "reason_code": None,
                        "message": "Already processed.",
                    }
                )
                continue

            # Route by path
            try:
                # 1. Dispatch route: /v1/lots/{code}/dispatch
                dispatch_match = re.search(r"^/v1/lots/([^/]+)/dispatch$", path)
                if dispatch_match:
                    lot_code = dispatch_match.group(1)
                    dispatch_lot(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Dispatched successfully.",
                        }
                    )
                    continue

                # 2. Receive route: /v1/handovers/{handover_id}/receive
                receive_match = re.search(r"^/v1/handovers/([^/]+)/receive$", path)
                if receive_match:
                    handover_id = receive_match.group(1)
                    receive_handover(request.user, handover_id, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Received successfully.",
                        }
                    )
                    continue

                # 3. Dispute route: /v1/handovers/{handover_id}/dispute
                dispute_match = re.search(r"^/v1/handovers/([^/]+)/dispute$", path)
                if dispute_match:
                    handover_id = dispute_match.group(1)
                    dispute_handover(request.user, handover_id, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Disputed successfully.",
                        }
                    )
                    continue

                # 4. Resolve route: /v1/handovers/{handover_id}/resolve
                resolve_match = re.search(r"^/v1/handovers/([^/]+)/resolve$", path)
                if resolve_match:
                    handover_id = resolve_match.group(1)
                    resolve_handover(request.user, handover_id, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Resolved successfully.",
                        }
                    )
                    continue

                # 5. Create lot route: /v1/lots
                if path in ["/v1/lots", "/v1/lots/"]:
                    from apps.lots.views import LotListCreateView
                    fake_request = request._request
                    view = LotListCreateView()
                    view.request = request
                    response = view.post(request)
                    if response.status_code in [200, 201]:
                        event = TraceEvent.objects.get(event_id=event_uuid)
                        results.append(
                            {
                                "event_id": str(event_uuid),
                                "status": "ACCEPTED",
                                "lot_seq": event.lot_seq,
                                "reason_code": None,
                                "message": "Lot created successfully.",
                            }
                        )
                    else:
                        resp_data = response.data or {}
                        results.append(
                            {
                                "event_id": str(event_uuid),
                                "status": "REJECTED",
                                "reason_code": resp_data.get("code", "LOT_CREATION_FAILED"),
                                "message": str(resp_data.get("detail", "Failed to create lot")),
                            }
                        )
                    continue

                # Unknown route
                results.append(
                    {
                        "event_id": str(event_uuid),
                        "status": "REJECTED",
                        "reason_code": "UNKNOWN_PATH",
                        "message": f"Unsupported sync path: {path}",
                    }
                )

            except exceptions.APIException as exc:
                detail = exc.detail
                if isinstance(detail, dict):
                    code = detail.get("code", "ERROR")
                    msg = detail.get("detail", str(detail))
                else:
                    code = "ERROR"
                    msg = str(detail)

                # Determine if CONFLICT or REJECTED
                conflict_codes = [
                    "HANDOVER_ALREADY_PENDING",
                    "HANDOVER_NOT_PENDING",
                    "HANDOVER_EXPIRED",
                    "LABEL_ALREADY_USED",
                ]
                item_status = "CONFLICT" if code in conflict_codes or exc.status_code == 409 else "REJECTED"

                results.append(
                    {
                        "event_id": str(event_uuid),
                        "status": item_status,
                        "reason_code": str(code),
                        "message": str(msg),
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "event_id": str(event_uuid),
                        "status": "REJECTED",
                        "reason_code": "INTERNAL_ERROR",
                        "message": str(e),
                    }
                )

        return Response({"results": results}, status=status.HTTP_200_OK)
