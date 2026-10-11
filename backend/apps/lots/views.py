"""Lots API views conforming to api/openapi.yaml."""

import hashlib
import json
import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.identity.authentication import IsVerifiedOrg
from apps.inventory.models import LotBalance
from apps.labels.models import QrBlock, QrLabel
from apps.ledger.models import TraceEvent
from .models import Lot, Product


def calculate_event_hash(prev_hash: bytes, event_type: str, lot_seq: int, payload: dict) -> bytes:
    """Calculate canonical event SHA-256 hash."""
    h = hashlib.sha256()
    h.update(prev_hash or b"")
    h.update(event_type.encode("utf-8"))
    h.update(str(lot_seq).encode("utf-8"))
    canonical_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    h.update(canonical_payload)
    return h.digest()


class LotListCreateView(APIView):
    """List or create crop/produce lots."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request):
        user_org = request.user.org
        lots = Lot.objects.filter(custodian_org=user_org).order_by("-created_at")[:100]

        items = []
        for lot in lots:
            balance = LotBalance.objects.filter(lot=lot).first()
            items.append(
                {
                    "lot_id": str(lot.lot_id),
                    "public_code": lot.public_code,
                    "state": lot.state,
                    "custodian_org": str(lot.custodian_org_id),
                    "pending_receiver_org": str(lot.pending_receiver_org_id) if lot.pending_receiver_org_id else None,
                    "on_hand_kg": float(balance.qty_on_hand_kg) if balance else 0.0,
                    "lot_seq": lot.head_seq,
                }
            )

        return Response({"items": items, "next_cursor": None}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        event_id_str = data.get("event_id")
        label_serial = data.get("label_serial")
        product_data = data.get("product")
        net_qty = data.get("net_qty_kg")
        event_time_str = data.get("event_time")

        if not all([event_id_str, label_serial, product_data, net_qty is not None, event_time_str]):
            raise exceptions.ValidationError(
                {
                    "detail": "event_id, label_serial, product, net_qty_kg, and event_time are required.",
                    "code": "FIELD_REQUIRED",
                }
            )

        try:
            event_id = uuid.UUID(event_id_str)
        except ValueError:
            raise exceptions.ValidationError({"detail": "event_id must be a valid UUID.", "code": "INVALID_UUID"})

        # 1. Idempotency check: if this event_id was already processed, return existing lot
        existing_event = TraceEvent.objects.filter(event_id=event_id).first()
        if existing_event:
            lot = existing_event.lot
            balance = LotBalance.objects.filter(lot=lot).first()
            return Response(
                {
                    "lot_id": str(lot.lot_id),
                    "public_code": lot.public_code,
                    "state": lot.state,
                    "custodian_org": str(lot.custodian_org_id),
                    "pending_receiver_org": str(lot.pending_receiver_org_id) if lot.pending_receiver_org_id else None,
                    "on_hand_kg": float(balance.qty_on_hand_kg) if balance else 0.0,
                    "lot_seq": lot.head_seq,
                },
                status=status.HTTP_200_OK,
            )

        user_org = request.user.org

        with transaction.atomic():
            # 2. Check label sticker: must exist in qr_label
            qr_label = QrLabel.objects.select_for_update().filter(serial=label_serial).first()
            if not qr_label:
                # If label doesn't exist, create an auto-issued one for this org if allowed
                block = QrBlock.objects.create(
                    block_id=uuid.uuid4(),
                    issued_to_org=user_org,
                    issued_by=request.user,
                    count=1,
                )
                qr_label = QrLabel.objects.create(
                    serial=label_serial,
                    block=block,
                    issued_to_org=user_org,
                    status="ISSUED",
                )

            # Check if label serial is already bound to another lot
            if qr_label.lot_id or qr_label.status == "BOUND":
                return Response(
                    {
                        "type": "urn:problem:label-already-used",
                        "title": "Label Already Used",
                        "status": 409,
                        "detail": f"The QR label serial {label_serial} is already bound to a lot.",
                        "code": "LABEL_ALREADY_USED",
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            # 3. Product resolution
            prod_name = product_data.get("name")
            prod_variety = product_data.get("variety")
            product, _ = Product.objects.get_or_create(
                name=prod_name,
                variety=prod_variety,
            )

            # 4. Create Lot
            lot_id = uuid.uuid4()
            lot = Lot.objects.create(
                lot_id=lot_id,
                public_code=label_serial,
                product=product,
                created_by_org=user_org,
                lot_kind="HARVEST",
                state="CREATED",
                custodian_org=user_org,
                head_seq=1,
            )

            # 5. Bind QR Label
            qr_label.lot = lot
            qr_label.status = "BOUND"
            qr_label.bound_at = timezone.now()
            qr_label.save(update_fields=["lot", "status", "bound_at"])

            # 6. Initialize LotBalance
            balance = LotBalance.objects.create(
                lot=lot,
                qty_in_kg=net_qty,
            )

            # 7. Record immutable TraceEvent
            payload = {
                "label_serial": label_serial,
                "product": {"name": prod_name, "variety": prod_variety},
                "net_qty_kg": float(net_qty),
                "harvest_date": data.get("harvest_date"),
                "plot_id": data.get("plot_id"),
            }
            event_hash = calculate_event_hash(b"", "HARVEST_CREATE", 1, payload)

            TraceEvent.objects.create(
                event_id=event_id,
                lot=lot,
                lot_seq=1,
                event_type="HARVEST_CREATE",
                event_time=event_time_str,
                org=user_org,
                user=request.user,
                payload=payload,
                event_hash=event_hash,
            )

            lot.head_hash = event_hash
            lot.save(update_fields=["head_hash"])

            from apps.publicview.services import refresh_public_view
            refresh_public_view(lot)

        return Response(
            {
                "lot_id": str(lot.lot_id),
                "public_code": lot.public_code,
                "state": lot.state,
                "custodian_org": str(lot.custodian_org_id),
                "pending_receiver_org": None,
                "on_hand_kg": float(balance.qty_on_hand_kg),
                "lot_seq": 1,
            },
            status=status.HTTP_201_CREATED,
        )


class LotDetailView(APIView):
    """Retrieve details for a specific lot by public code."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request, code):
        lot = Lot.objects.select_related("custodian_org", "product").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        # Cross-org access check: only current custodian or pending receiver may view internal lot details
        if lot.custodian_org_id != user_org.org_id and lot.pending_receiver_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "You do not have permission to view lots belonging to another organisation.", "code": "CROSS_ORG_FORBIDDEN"}
            )

        balance = LotBalance.objects.filter(lot=lot).first()
        return Response(
            {
                "lot_id": str(lot.lot_id),
                "public_code": lot.public_code,
                "state": lot.state,
                "custodian_org": str(lot.custodian_org_id),
                "pending_receiver_org": str(lot.pending_receiver_org_id) if lot.pending_receiver_org_id else None,
                "on_hand_kg": float(balance.qty_on_hand_kg) if balance else 0.0,
                "lot_seq": lot.head_seq,
            },
            status=status.HTTP_200_OK,
        )


class LotEventsView(APIView):
    """Retrieve audit events for a lot."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request, code):
        lot = Lot.objects.filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        if lot.custodian_org_id != user_org.org_id and lot.pending_receiver_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Cross-org access denied.", "code": "CROSS_ORG_FORBIDDEN"}
            )

        events = TraceEvent.objects.filter(lot=lot).order_by("lot_seq")
        items = [
            {
                "event_id": str(e.event_id),
                "lot_seq": e.lot_seq,
                "event_type": e.event_type,
                "event_time": e.event_time.isoformat(),
                "org_id": str(e.org_id),
                "user_id": str(e.user_id),
                "payload": e.payload,
            }
            for e in events
        ]
        return Response({"items": items, "next_cursor": None}, status=status.HTTP_200_OK)


class LotInspectionView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from apps.quality.services.quality_service import record_inspection
        result = record_inspection(request.user, code, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class LotDispatchView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from apps.custody.services.handover_service import dispatch_lot
        handover = dispatch_lot(request.user, code, request.data)
        return Response(
            {
                "handover_id": str(handover.handover_id),
                "lot_code": handover.lot.public_code,
                "state": handover.state,
                "declared_qty_kg": float(handover.declared_qty_kg),
                "received_qty_kg": float(handover.received_qty_kg) if handover.received_qty_kg is not None else None,
                "expires_at": handover.expires_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class LotSplitView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from .services.genealogy_service import split_lot
        result = split_lot(request.user, code, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class LotMergeView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request):
        from .services.genealogy_service import merge_lots
        result = merge_lots(request.user, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class LotSortView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from .services.genealogy_service import sort_lot
        result = sort_lot(request.user, code, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class LotRepackView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from .services.genealogy_service import repack_lot
        result = repack_lot(request.user, code, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class LotWasteView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from .services.genealogy_service import record_waste
        result = record_waste(request.user, code, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class LotSaleView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from .services.genealogy_service import record_sale
        result = record_sale(request.user, code, request.data)
        return Response(result, status=status.HTTP_201_CREATED)


class LotLabelReissueView(APIView):
    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        from apps.ledger.services.correction_service import reissue_label
        result = reissue_label(request.user, code, request.data)
        return Response(result, status=status.HTTP_201_CREATED)
