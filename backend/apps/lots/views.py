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
import secrets
from django.db import models

CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

def generate_crockford_serial(length: int = 12) -> str:
    """Generate unguessable 12-character Crockford Base32 serial code."""
    return "".join(secrets.choice(CROCKFORD_ALPHABET) for _ in range(length))


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
    """List or create crop/produce lots with rich agricultural and settlement fields."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request):
        user_org = request.user.org
        qs = Lot.objects.select_related("product", "origin_plot").filter(custodian_org=user_org)

        # Filters
        crop_filter = request.query_params.get("crop")
        if crop_filter and crop_filter.upper() != "ALL":
            qs = qs.filter(product__name__iexact=crop_filter)

        plot_filter = request.query_params.get("plot")
        if plot_filter and plot_filter.upper() != "ALL":
            qs = qs.filter(origin_plot_id=plot_filter)

        state_filter = request.query_params.get("state")
        if state_filter and state_filter.upper() != "ALL":
            qs = qs.filter(state=state_filter)

        search_query = request.query_params.get("q")
        if search_query:
            qs = qs.filter(
                models.Q(public_code__icontains=search_query)
                | models.Q(product__name__icontains=search_query)
                | models.Q(product__variety__icontains=search_query)
            )

        sort_by = request.query_params.get("sort", "-created_at")
        if sort_by in ("created_at", "-created_at"):
            qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by("-created_at")

        lots = qs[:150]

        items = []
        for lot in lots:
            balance = LotBalance.objects.filter(lot=lot).first()
            create_event = TraceEvent.objects.filter(lot=lot, event_type__in=["HARVEST_CREATE", "LOT_UPDATE"]).order_by("-lot_seq").first()
            payload = create_event.payload if create_event else {}

            qty_val = float(balance.qty_on_hand_kg) if balance else float(payload.get("net_qty_kg", 0.0))

            items.append(
                {
                    "lot_id": str(lot.lot_id),
                    "public_code": lot.public_code,
                    "state": lot.state,
                    "custodian_org": str(lot.custodian_org_id),
                    "pending_receiver_org": str(lot.pending_receiver_org_id) if lot.pending_receiver_org_id else None,
                    "on_hand_kg": qty_val,
                    "net_qty_kg": qty_val,
                    "unit": payload.get("unit", "Kg"),
                    "packages_count": payload.get("packages_count", 1),
                    "package_type": payload.get("package_type", "Plastic Crates"),
                    "crop": lot.product.name if lot.product else payload.get("product", {}).get("name", ""),
                    "variety": lot.product.variety if lot.product else payload.get("product", {}).get("variety", ""),
                    "category": payload.get("category", "Vegetable"),
                    "harvest_date": payload.get("harvest_date") or lot.created_at.isoformat(),
                    "sowing_date": payload.get("sowing_date", ""),
                    "shelf_life_days": payload.get("shelf_life_days", 14),
                    "origin_plot_id": str(lot.origin_plot_id) if lot.origin_plot_id else payload.get("plot_id", ""),
                    "origin_plot_name": lot.origin_plot.plot_name if lot.origin_plot else payload.get("plot_name", ""),
                    "plot_area_acres": float(lot.origin_plot.area_acres) if (lot.origin_plot and lot.origin_plot.area_acres) else payload.get("plot_area_acres"),
                    "grade": payload.get("grade", "Grade A"),
                    "farming_method": payload.get("farming_method", "Conventional"),
                    "soil_type": payload.get("soil_type", ""),
                    "irrigation_type": payload.get("irrigation_type", ""),
                    "fertilizers": payload.get("fertilizers", ""),
                    "last_spray_date": payload.get("last_spray_date", ""),
                    "moisture_pct": payload.get("moisture_pct"),
                    "cold_wash_applied": payload.get("cold_wash_applied", False),
                    "base_price_per_unit": payload.get("base_price_per_unit"),
                    "estimated_value": payload.get("estimated_value"),
                    "payment_status": payload.get("payment_status", "PENDING"),
                    "intended_buyer": payload.get("intended_buyer", "APMC Mandi Aggregator"),
                    "remarks": payload.get("remarks", ""),
                    "is_editable": lot.state in ("CREATED", "IN_CUSTODY"),
                    "lot_seq": lot.head_seq,
                    "created_at": lot.created_at.isoformat(),
                }
            )

        return Response({"items": items, "next_cursor": None}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        event_id_str = data.get("event_id")
        label_serial = data.get("label_serial")
        product_data = data.get("product")
        net_qty = data.get("net_qty_kg")
        event_time_str = data.get("event_time") or timezone.now().isoformat()

        # Handle simplified crop string in product_data if passed from simple form
        if isinstance(product_data, str):
            product_data = {"name": product_data, "variety": data.get("variety", "")}
        elif not product_data and data.get("crop"):
            product_data = {"name": data.get("crop"), "variety": data.get("variety", "")}

        # Auto-generate label serial if not supplied
        if not label_serial:
            while True:
                candidate = generate_crockford_serial(12)
                if not Lot.objects.filter(public_code=candidate).exists() and not QrLabel.objects.filter(serial=candidate).exists():
                    label_serial = candidate
                    break

        # Auto-generate event_id if not supplied
        if not event_id_str:
            event_id = uuid.uuid4()
            event_id_str = str(event_id)
        else:
            try:
                event_id = uuid.UUID(event_id_str)
            except ValueError:
                raise exceptions.ValidationError({"detail": "event_id must be a valid UUID.", "code": "INVALID_UUID"})

        if not product_data or net_qty is None:
            raise exceptions.ValidationError(
                {
                    "detail": "product and net_qty_kg are required.",
                    "code": "FIELD_REQUIRED",
                }
            )

        try:
            net_qty = float(net_qty)
        except (ValueError, TypeError):
            raise exceptions.ValidationError({"detail": "net_qty_kg must be a valid number.", "code": "INVALID_QTY"})

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
                    "is_editable": lot.state in ("CREATED", "IN_CUSTODY"),
                },
                status=status.HTTP_200_OK,
            )

        user_org = request.user.org

        with transaction.atomic():
            # 2. Check label sticker: must exist in qr_label or auto-issue
            qr_label = QrLabel.objects.select_for_update().filter(serial=label_serial).first()
            if not qr_label:
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

            # 4. Resolve origin plot if provided
            plot_obj = None
            plot_id_val = data.get("plot_id") or data.get("origin_plot_id")
            if plot_id_val:
                try:
                    from apps.organisations.models import Plot
                    plot_obj = Plot.objects.filter(plot_id=plot_id_val, org=user_org).first()
                except Exception:
                    pass

            # 5. Create Lot
            lot_id = uuid.uuid4()
            lot = Lot.objects.create(
                lot_id=lot_id,
                public_code=label_serial,
                product=product,
                origin_plot=plot_obj,
                created_by_org=user_org,
                lot_kind="HARVEST",
                state="CREATED",
                custodian_org=user_org,
                head_seq=1,
            )

            # 6. Bind QR Label
            qr_label.lot = lot
            qr_label.status = "BOUND"
            qr_label.bound_at = timezone.now()
            qr_label.save(update_fields=["lot", "status", "bound_at"])

            # 7. Initialize LotBalance
            balance = LotBalance.objects.create(
                lot=lot,
                qty_in_kg=net_qty,
            )

            # 8. Record immutable TraceEvent with all possible harvest fields
            payload = {
                "label_serial": label_serial,
                "product": {"name": prod_name, "variety": prod_variety, "category": data.get("category", "Vegetable")},
                "net_qty_kg": float(net_qty),
                "unit": data.get("unit", "Kg"),
                "packages_count": int(data.get("packages_count", 1)),
                "package_type": data.get("package_type", "Plastic Crates"),
                "harvest_date": data.get("harvest_date") or event_time_str,
                "sowing_date": data.get("sowing_date"),
                "shelf_life_days": int(data.get("shelf_life_days", 14)),
                "plot_id": str(plot_obj.plot_id) if plot_obj else None,
                "plot_name": plot_obj.plot_name if plot_obj else data.get("plot_name", ""),
                "plot_area_acres": float(plot_obj.area_acres) if (plot_obj and plot_obj.area_acres) else None,
                "grade": data.get("grade", "Grade A"),
                "farming_method": data.get("farming_method", "Conventional"),
                "soil_type": data.get("soil_type", ""),
                "irrigation_type": data.get("irrigation_type", ""),
                "fertilizers": data.get("fertilizers", ""),
                "last_spray_date": data.get("last_spray_date", ""),
                "moisture_pct": float(data["moisture_pct"]) if data.get("moisture_pct") is not None else None,
                "cold_wash_applied": bool(data.get("cold_wash_applied", False)),
                "base_price_per_unit": float(data["base_price_per_unit"]) if data.get("base_price_per_unit") is not None else None,
                "estimated_value": float(data["estimated_value"]) if data.get("estimated_value") is not None else None,
                "payment_status": data.get("payment_status", "PENDING"),
                "intended_buyer": data.get("intended_buyer", "APMC Mandi Aggregator"),
                "remarks": data.get("remarks", ""),
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
                "crop": prod_name,
                "variety": prod_variety,
                "is_editable": True,
            },
            status=status.HTTP_201_CREATED,
        )


class LotDetailView(APIView):
    """Retrieve or update details for a specific lot by public code."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request, code):
        lot = Lot.objects.select_related("custodian_org", "product", "origin_plot").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        # Cross-org access check: only current custodian or pending receiver may view internal lot details
        if lot.custodian_org_id != user_org.org_id and lot.pending_receiver_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "You do not have permission to view lots belonging to another organisation.", "code": "CROSS_ORG_FORBIDDEN"}
            )

        balance = LotBalance.objects.filter(lot=lot).first()
        create_event = TraceEvent.objects.filter(lot=lot, event_type__in=["HARVEST_CREATE", "LOT_UPDATE"]).order_by("-lot_seq").first()
        payload = create_event.payload if create_event else {}

        qty_val = float(balance.qty_on_hand_kg) if balance else float(payload.get("net_qty_kg", 0.0))

        return Response(
            {
                "lot_id": str(lot.lot_id),
                "public_code": lot.public_code,
                "state": lot.state,
                "custodian_org": str(lot.custodian_org_id),
                "pending_receiver_org": str(lot.pending_receiver_org_id) if lot.pending_receiver_org_id else None,
                "on_hand_kg": qty_val,
                "net_qty_kg": qty_val,
                "unit": payload.get("unit", "Kg"),
                "packages_count": payload.get("packages_count", 1),
                "package_type": payload.get("package_type", "Plastic Crates"),
                "crop": lot.product.name if lot.product else payload.get("product", {}).get("name", ""),
                "variety": lot.product.variety if lot.product else payload.get("product", {}).get("variety", ""),
                "category": payload.get("category", "Vegetable"),
                "harvest_date": payload.get("harvest_date") or lot.created_at.isoformat(),
                "sowing_date": payload.get("sowing_date", ""),
                "shelf_life_days": payload.get("shelf_life_days", 14),
                "origin_plot_id": str(lot.origin_plot_id) if lot.origin_plot_id else payload.get("plot_id", ""),
                "origin_plot_name": lot.origin_plot.plot_name if lot.origin_plot else payload.get("plot_name", ""),
                "plot_area_acres": float(lot.origin_plot.area_acres) if (lot.origin_plot and lot.origin_plot.area_acres) else payload.get("plot_area_acres"),
                "grade": payload.get("grade", "Grade A"),
                "farming_method": payload.get("farming_method", "Conventional"),
                "soil_type": payload.get("soil_type", ""),
                "irrigation_type": payload.get("irrigation_type", ""),
                "fertilizers": payload.get("fertilizers", ""),
                "last_spray_date": payload.get("last_spray_date", ""),
                "moisture_pct": payload.get("moisture_pct"),
                "cold_wash_applied": payload.get("cold_wash_applied", False),
                "base_price_per_unit": payload.get("base_price_per_unit"),
                "estimated_value": payload.get("estimated_value"),
                "payment_status": payload.get("payment_status", "PENDING"),
                "intended_buyer": payload.get("intended_buyer", "APMC Mandi Aggregator"),
                "remarks": payload.get("remarks", ""),
                "is_editable": lot.state in ("CREATED", "IN_CUSTODY"),
                "lot_seq": lot.head_seq,
                "created_at": lot.created_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, code):
        """Update an editable harvest lot before next custody approval."""
        lot = Lot.objects.select_related("custodian_org", "product").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        if lot.custodian_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "You do not have permission to edit lots belonging to another organisation.", "code": "CROSS_ORG_FORBIDDEN"}
            )

        # Enforce custody lock rule: only editable before approving/initiating next custody handover
        if lot.state not in ("CREATED", "IN_CUSTODY"):
            raise exceptions.PermissionDenied(
                {
                    "detail": "This harvest lot is locked because custody handover has already been initiated or approved. Records are immutable.",
                    "code": "LOT_LOCKED",
                }
            )

        data = request.data
        prod_data = data.get("product") or {}
        if isinstance(prod_data, str):
            prod_data = {"name": prod_data, "variety": data.get("variety", "")}
        elif not prod_data and data.get("crop"):
            prod_data = {"name": data.get("crop"), "variety": data.get("variety", "")}

        net_qty = data.get("net_qty_kg")
        if net_qty is not None:
            try:
                net_qty = float(net_qty)
            except (ValueError, TypeError):
                net_qty = None

        with transaction.atomic():
            # Update product if changed
            if prod_data.get("name"):
                product, _ = Product.objects.get_or_create(
                    name=prod_data.get("name"),
                    variety=prod_data.get("variety", ""),
                )
                lot.product = product

            # Update origin plot if provided
            plot_id_val = data.get("plot_id") or data.get("origin_plot_id")
            if plot_id_val:
                try:
                    from apps.organisations.models import Plot
                    plot_obj = Plot.objects.filter(plot_id=plot_id_val, org=user_org).first()
                    if plot_obj:
                        lot.origin_plot = plot_obj
                except Exception:
                    pass

            # Update balance if quantity changed
            balance = LotBalance.objects.filter(lot=lot).first()
            if net_qty is not None and balance:
                balance.qty_in_kg = net_qty
                balance.save(update_fields=["qty_in_kg"])

            # Append new TraceEvent
            lot.head_seq += 1
            payload = {
                "label_serial": lot.public_code,
                "product": {"name": lot.product.name, "variety": lot.product.variety or ""},
                "net_qty_kg": float(balance.qty_on_hand_kg if balance else (net_qty or 0.0)),
                "unit": data.get("unit", "Kg"),
                "packages_count": int(data.get("packages_count", 1)),
                "package_type": data.get("package_type", "Plastic Crates"),
                "harvest_date": data.get("harvest_date"),
                "sowing_date": data.get("sowing_date"),
                "shelf_life_days": int(data.get("shelf_life_days", 14)),
                "plot_id": str(lot.origin_plot_id) if lot.origin_plot_id else None,
                "plot_name": lot.origin_plot.plot_name if lot.origin_plot else data.get("plot_name", ""),
                "grade": data.get("grade", "Grade A"),
                "farming_method": data.get("farming_method", "Conventional"),
                "soil_type": data.get("soil_type", ""),
                "irrigation_type": data.get("irrigation_type", ""),
                "fertilizers": data.get("fertilizers", ""),
                "last_spray_date": data.get("last_spray_date", ""),
                "moisture_pct": float(data["moisture_pct"]) if data.get("moisture_pct") is not None else None,
                "cold_wash_applied": bool(data.get("cold_wash_applied", False)),
                "base_price_per_unit": float(data["base_price_per_unit"]) if data.get("base_price_per_unit") is not None else None,
                "estimated_value": float(data["estimated_value"]) if data.get("estimated_value") is not None else None,
                "payment_status": data.get("payment_status", "PENDING"),
                "intended_buyer": data.get("intended_buyer", "APMC Mandi Aggregator"),
                "remarks": data.get("remarks", ""),
            }
            event_hash = calculate_event_hash(bytes(lot.head_hash or b""), "LOT_UPDATE", lot.head_seq, payload)
            TraceEvent.objects.create(
                event_id=uuid.uuid4(),
                lot=lot,
                lot_seq=lot.head_seq,
                event_type="LOT_UPDATE",
                event_time=timezone.now().isoformat(),
                org=user_org,
                user=request.user,
                payload=payload,
                event_hash=event_hash,
            )
            lot.head_hash = event_hash
            lot.save(update_fields=["product", "origin_plot", "head_seq", "head_hash"])

            from apps.publicview.services import refresh_public_view
            refresh_public_view(lot)

        return Response(
            {
                "lot_id": str(lot.lot_id),
                "public_code": lot.public_code,
                "state": lot.state,
                "crop": lot.product.name,
                "variety": lot.product.variety or "",
                "net_qty_kg": float(balance.qty_on_hand_kg if balance else (net_qty or 0.0)),
                "is_editable": True,
                "message": "Harvest lot updated successfully.",
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
