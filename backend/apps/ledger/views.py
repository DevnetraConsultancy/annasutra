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
        from .services.correction_service import correct_event
        result = correct_event(request.user, event_id, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class SyncBatchView(APIView):
    """Processes batches of queued events uploaded by mobile/web clients (up to 100)."""

    permission_classes = [IsVerifiedOrg]

    def post(self, request):
        from apps.lots.services.genealogy_service import (
            split_lot,
            merge_lots,
            sort_lot,
            repack_lot,
            record_waste,
            record_sale,
        )
        from apps.quality.services.quality_service import record_inspection
        from apps.ledger.services.correction_service import correct_event, reissue_label

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

                # 6. Split route: /v1/lots/{code}/split
                split_match = re.search(r"^/v1/lots/([^/]+)/split$", path)
                if split_match:
                    lot_code = split_match.group(1)
                    split_lot(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Split completed.",
                        }
                    )
                    continue

                # 7. Merge route: /v1/lots/merge
                if path in ["/v1/lots/merge", "/v1/lots/merge/"]:
                    merge_lots(request.user, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Merge completed.",
                        }
                    )
                    continue

                # 8. Sort route: /v1/lots/{code}/sort
                sort_match = re.search(r"^/v1/lots/([^/]+)/sort$", path)
                if sort_match:
                    lot_code = sort_match.group(1)
                    sort_lot(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Sort completed.",
                        }
                    )
                    continue

                # 9. Repack route: /v1/lots/{code}/repack
                repack_match = re.search(r"^/v1/lots/([^/]+)/repack$", path)
                if repack_match:
                    lot_code = repack_match.group(1)
                    repack_lot(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Repack recorded.",
                        }
                    )
                    continue

                # 10. Waste route: /v1/lots/{code}/waste
                waste_match = re.search(r"^/v1/lots/([^/]+)/waste$", path)
                if waste_match:
                    lot_code = waste_match.group(1)
                    record_waste(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Waste recorded.",
                        }
                    )
                    continue

                # 11. Sales route: /v1/lots/{code}/sales
                sales_match = re.search(r"^/v1/lots/([^/]+)/sales$", path)
                if sales_match:
                    lot_code = sales_match.group(1)
                    record_sale(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Sale recorded.",
                        }
                    )
                    continue

                # 12. Inspection route: /v1/lots/{code}/inspections
                inspect_match = re.search(r"^/v1/lots/([^/]+)/inspections$", path)
                if inspect_match:
                    lot_code = inspect_match.group(1)
                    record_inspection(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Inspection recorded.",
                        }
                    )
                    continue

                # 13. Label reissue route: /v1/lots/{code}/label-reissue
                reissue_match = re.search(r"^/v1/lots/([^/]+)/label-reissue$", path)
                if reissue_match:
                    lot_code = reissue_match.group(1)
                    reissue_label(request.user, lot_code, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Label reissued.",
                        }
                    )
                    continue

                # 14. Correction route: /v1/events/{event_id}/corrections
                corr_match = re.search(r"^/v1/events/([^/]+)/corrections$", path)
                if corr_match:
                    target_event_id = corr_match.group(1)
                    correct_event(request.user, target_event_id, body)
                    event = TraceEvent.objects.get(event_id=event_uuid)
                    results.append(
                        {
                            "event_id": str(event_uuid),
                            "status": "ACCEPTED",
                            "lot_seq": event.lot_seq,
                            "reason_code": None,
                            "message": "Correction appended.",
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
                    "CYCLIC_GENEALOGY",
                    "MASS_BALANCE_VIOLATION",
                    "INSUFFICIENT_STOCK",
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
