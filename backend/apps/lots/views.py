"""Lots API views conforming to AnnaSutra Entity Console Architecture."""

from decimal import Decimal
import hashlib
import json
import re
import secrets
import uuid

from django.db import models, transaction
from django.utils import timezone
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.custody.models import Handover
from apps.identity.authentication import IsVerifiedOrg
from apps.identity.models import AppUser, EntityPlot, EntityProfile
from apps.identity.services.crypto import CryptoService
from apps.identity.services.entity_allocation import get_or_mint_farmer_uid, resolve_identity_segment
from apps.inventory.models import LotBalance
from apps.labels.models import QrBlock, QrLabel
from apps.ledger.models import TraceEvent
from apps.organisations.models import Organisation
from .models import Lot, LotEdge, Product

CROCKFORD_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
ISO7064_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ*"

# Mentor's 10-Category Product Code Taxonomy
PRODUCT_CATEGORY_CATALOG = {
    "FG": "Food grains & cereals",
    "PU": "Pulses",
    "OI": "Oilseeds",
    "FR": "Fruits",
    "VG": "Vegetables",
    "SP": "Spices",
    "CC": "Commercial Crops",
    "LS": "Livestock",
    "SC": "Special Crops",
    "OT": "Others",
}


def compute_iso7064_check_char(payload: str) -> str:
    """Compute 1-character ISO 7064 Mod 37,2 check character for alphanumeric Lot Code."""
    p = 0
    for ch in str(payload or "").upper():
        val = ISO7064_ALPHABET.find(ch)
        if val < 0:
            val = 0
        p = ((p + val) * 2) % 37
    check_val = (38 - p) % 37
    return "X" if check_val == 36 else ISO7064_ALPHABET[check_val]


def resolve_product_category(category_raw: str, crop_raw: str = "") -> tuple[str, str]:
    """Resolve category string/code or crop name to (2-letter code, standard category name)."""
    cat_up = str(category_raw or "").strip().upper()
    crop_up = str(crop_raw or "").strip().upper()

    if cat_up in PRODUCT_CATEGORY_CATALOG:
        return cat_up, PRODUCT_CATEGORY_CATALOG[cat_up]

    keyword_map = [
        ("FG", ["FOOD GRAIN", "CEREAL", "GRAIN", "RICE", "PADDY", "WHEAT", "MAIZE", "CORN", "MILLET", "BAJRA", "JOWAR", "RAGI", "BARLEY", "OATS"]),
        ("PU", ["PULSE", "LENTIL", "DAL", "CHICKPEA", "GRAM", "MOONG", "URAD", "TOOR", "ARHAR", "MASOOR", "RAJMA", "COWPEA"]),
        ("OI", ["OILSEED", "MUSTARD", "GROUNDNUT", "PEANUT", "SOYBEAN", "SOYA", "SUNFLOWER", "SESAME", "TIL", "CASTOR", "LINSEED", "SAFFLOWER"]),
        ("FR", ["FRUIT", "MANGO", "APPLE", "BANANA", "ORANGE", "CITRUS", "GRAPE", "PAPAYA", "GUAVA", "POMEGRANATE", "LITCHI", "PINEAPPLE", "WATERMELON", "LEMON", "BER"]),
        ("VG", ["VEGETABLE", "VEG", "TOMATO", "POTATO", "ONION", "BRINJAL", "EGGPLANT", "CABBAGE", "CAULIFLOWER", "OKRA", "BHINDI", "SPINACH", "CHILLI", "GARLIC", "GINGER", "CARROT", "RADISH", "GOURD", "PUMPKIN", "CUCUMBER", "CAPSICUM", "BEANS", "PEAS"]),
        ("SP", ["SPICE", "TURMERIC", "HALDI", "CARDAMOM", "PEPPER", "CUMIN", "JEERA", "CORIANDER", "DHANIYA", "CLOVE", "CINNAMON", "FENUGREEK", "METHI", "FENNEL", "NUTMEG", "TAMARIND"]),
        ("CC", ["COMMERCIAL", "CASH CROP", "COTTON", "JUTE", "SUGARCANE", "TEA", "COFFEE", "RUBBER", "TOBACCO", "COCONUT", "ARECANUT", "BETEL"]),
        ("LS", ["LIVESTOCK", "LIVE STOCK", "DAIRY", "MILK", "POULTRY", "EGG", "MEAT", "HONEY", "BEE", "FISH", "AQUA", "SHRIMP", "PRAWN", "GOAT", "SHEEP", "CATTLE", "BUFFALO", "WOOL"]),
        ("SC", ["SPECIAL", "MEDICINAL", "AROMATIC", "HERB", "MUSHROOM", "BAMBOO", "FLORICULTURE", "FLOWER", "ROSE", "MARIGOLD", "ASHWAGANDHA", "ALOE", "TULSI", "STEVIA", "LEMONGRASS", "SAFFRON"]),
        ("OT", ["OTHER", "FOREST", "FODDER", "SEED", "BYPRODUCT"]),
    ]

    for code, keywords in keyword_map:
        if any(k in cat_up for k in keywords):
            return code, PRODUCT_CATEGORY_CATALOG[code]
    for code, keywords in keyword_map:
        if any(k in crop_up for k in keywords):
            return code, PRODUCT_CATEGORY_CATALOG[code]

    return "OT", PRODUCT_CATEGORY_CATALOG["OT"]


def generate_crockford_serial(length: int = 12) -> str:
    """Generate unguessable 12-character Crockford Base32 serial code."""
    return "".join(secrets.choice(CROCKFORD_ALPHABET) for _ in range(length))


def generate_mentor_batch_id(user, cat_code: str, user_org, dt=None) -> str:
    """Generate 32-character Batch/Lot ID per Section 3.2 & Decision 29:
    YYYYMMDDHHMMSS (14) + 91 (2) + IdentitySegment(10) + CropClass(2) + Seq(3) + Check(1) = 32 chars.
    """
    now = dt or timezone.now()
    ts_part = now.strftime("%Y%m%d%H%M%S")
    identity_seg = resolve_identity_segment(user)
    digits = f"91{identity_seg}"

    clean_cat = cat_code if cat_code in PRODUCT_CATEGORY_CATALOG else "OT"
    seq = (Lot.objects.filter(created_by_org=user_org).count() if user_org else 0) + 1

    while True:
        seq_3 = ((seq - 1) % 999) + 1
        base_31 = f"{ts_part}{digits}{clean_cat}{seq_3:03d}"
        check_ch = compute_iso7064_check_char(base_31)
        candidate = f"{base_31}{check_ch}"
        if not Lot.objects.filter(public_code=candidate).exists() and not QrLabel.objects.filter(serial=candidate).exists():
            return candidate
        seq += 1


def calculate_event_hash(prev_hash: bytes, event_type: str, lot_seq: int, payload: dict) -> bytes:
    """Calculate canonical event SHA-256 hash."""
    h = hashlib.sha256()
    h.update(prev_hash or b"")
    h.update(event_type.encode("utf-8"))
    h.update(str(lot_seq).encode("utf-8"))
    canonical_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    h.update(canonical_payload)
    return h.digest()


def _extract_origin_coords_for_lot(lot, create_payload: dict) -> tuple[float, float, str]:
    """Resolve farm origin GPS coordinates and coarse location name for a lot."""
    lat = create_payload.get("origin_lat") or create_payload.get("lat")
    lng = create_payload.get("origin_lng") or create_payload.get("lng")
    loc_name = create_payload.get("origin_location") or create_payload.get("plot_name") or ""

    if lat is not None and lng is not None:
        try:
            return float(lat), float(lng), str(loc_name or "Origin Farm Plot")
        except (ValueError, TypeError):
            pass

    creator_user = AppUser.objects.filter(org_id=lot.created_by_org_id).first()
    if creator_user:
        profile = (
            EntityProfile.objects.filter(user_id=creator_user.user_id).first()
            or (EntityProfile.objects.filter(phone_e164=creator_user.phone_e164).first() if creator_user.phone_e164 else None)
        )
        if profile:
            if not loc_name:
                parts = [p for p in [profile.village_town, profile.district, profile.state] if p]
                loc_name = ", ".join(parts)
            e_plot = EntityPlot.objects.filter(entity=profile).first()
            if e_plot and e_plot.geojson_enc:
                try:
                    raw = CryptoService.decrypt(bytes(e_plot.geojson_enc), entity_id=str(profile.entity_id))
                    gj = json.loads(raw)
                    coords = gj.get("coordinates", [[]])[0]
                    if coords and isinstance(coords[0], (list, tuple)) and len(coords[0]) >= 2:
                        c0, c1 = float(coords[0][0]), float(coords[0][1])
                        if 6.0 <= c1 <= 38.0 and 68.0 <= c0 <= 98.0:
                            return c1, c0, str(loc_name or e_plot.plot_name)
                        return c0, c1, str(loc_name or e_plot.plot_name)
                except Exception:
                    pass

    return 23.2324, 87.8615, str(loc_name or "Purba Bardhaman, West Bengal")


def _build_lot_item(lot: Lot, _depth: int = 0) -> dict:
    """Serialize a Lot with full traceability checkpoints, custody status, and parent/child packet batch lineage."""
    balance = LotBalance.objects.filter(lot=lot).first()
    events = list(TraceEvent.objects.filter(lot=lot).order_by("lot_seq"))

    create_payload = {}
    for ev in events:
        if ev.event_type in ("HARVEST_CREATE", "LOT_UPDATE", "PACKET_BATCH_CREATED", "SPLIT_CHILD"):
            if not create_payload or ev.event_type in ("HARVEST_CREATE", "LOT_UPDATE"):
                create_payload = ev.payload or {}

    qty_val = float(balance.qty_on_hand_kg) if balance else float(create_payload.get("net_qty_kg", 0.0))
    crop_name = lot.product.name if lot.product else create_payload.get("product", {}).get("name", "")
    variety_name = lot.product.variety if lot.product else create_payload.get("product", {}).get("variety", "")
    raw_cat = create_payload.get("product_category_code") or create_payload.get("category") or create_payload.get("product", {}).get("category", "VG")
    cat_code, cat_name = resolve_product_category(raw_cat, crop_name)

    origin_lat, origin_lng, origin_loc = _extract_origin_coords_for_lot(lot, create_payload)

    # Resolve producer's farmer_uid
    farmer_uid = create_payload.get("farmer_uid") or ""
    if not farmer_uid:
        creator_user = AppUser.objects.filter(org_id=lot.created_by_org_id).first()
        if creator_user:
            prof = (
                EntityProfile.objects.filter(user_id=creator_user.user_id).first()
                or (EntityProfile.objects.filter(phone_e164=creator_user.phone_e164).first() if creator_user.phone_e164 else None)
            )
            farmer_uid = get_or_mint_farmer_uid(prof if prof else creator_user)

    checkpoints = []
    # If this is a child packet batch with upstream checkpoints stored or a parent lot edge, inherit parent checkpoints
    upstream_cps = create_payload.get("upstream_checkpoints")
    if isinstance(upstream_cps, list) and upstream_cps:
        for cp in upstream_cps:
            checkpoints.append(dict(cp))
    else:
        checkpoints.append(
            {
                "step": 1,
                "event_type": "HARVEST_CREATE",
                "role": "PRODUCER",
                "actor_name": create_payload.get("farmer_name") or (lot.created_by_org.name if lot.created_by_org else "Producer Farm"),
                "location_name": origin_loc,
                "lat": origin_lat,
                "lng": origin_lng,
                "weight_kg": float(create_payload.get("net_qty_kg", qty_val)),
                "condition": f"Fresh Harvest ({create_payload.get('grade', 'Grade A')})",
                "storage_temp": "Pre-Cooled (4°C)" if create_payload.get("cold_wash_applied") else "Farm Ambient",
                "photo_url": create_payload.get("harvest_photo_url") or None,
                "vehicle_no": None,
                "remarks": create_payload.get("remarks", ""),
                "timestamp": create_payload.get("harvest_date") or lot.created_at.isoformat(),
            }
        )

    current_custodian_role = create_payload.get("actor_role") or "PRODUCER"
    current_custodian_name = lot.custodian_org.name if lot.custodian_org else "Producer Farm"
    is_retailer_verified = False
    pending_handover = None

    step_num = len(checkpoints) + 1
    for ev in events:
        p = ev.payload or {}
        if ev.event_type == "HANDOVER_REQUEST":
            pending_handover = {
                "event_id": str(ev.event_id),
                "status": "PENDING_ACCEPTANCE",
                "from_role": p.get("from_role", current_custodian_role),
                "from_name": p.get("from_name", current_custodian_name),
                "target_role": p.get("target_role", "AGGREGATOR"),
                "target_phone": p.get("target_phone", ""),
                "target_email": p.get("target_email", ""),
                "target_role_id": p.get("target_role_id", ""),
                "target_name": p.get("target_name", ""),
                "declared_qty_kg": float(p.get("declared_qty_kg", qty_val)),
                "vehicle_no": p.get("vehicle_no", ""),
                "handover_pin": p.get("handover_pin", ""),
                "location_name": p.get("location_name", ""),
                "lat": p.get("lat"),
                "lng": p.get("lng"),
                "remarks": p.get("remarks", ""),
                "requested_at": ev.event_time.isoformat(),
            }
        elif ev.event_type in ("HANDOVER_ACCEPT", "RECEIVE"):
            actor_role = str(p.get("actor_role") or "AGGREGATOR").upper()
            actor_name = p.get("actor_name") or (ev.org.name if ev.org else actor_role.title())
            current_custodian_role = actor_role
            current_custodian_name = actor_name
            pending_handover = None
            if actor_role == "RETAILER" or p.get("retail_ready"):
                is_retailer_verified = True
            checkpoints.append(
                {
                    "step": step_num,
                    "event_type": "HANDOVER_ACCEPT",
                    "role": actor_role,
                    "actor_name": actor_name,
                    "location_name": p.get("location_name") or f"{actor_role.title()} Facility",
                    "lat": float(p["lat"]) if p.get("lat") is not None else origin_lat + (0.04 * step_num),
                    "lng": float(p["lng"]) if p.get("lng") is not None else origin_lng + (0.04 * step_num),
                    "weight_kg": float(p.get("received_qty_kg") or p.get("current_weight_kg") or qty_val),
                    "condition": p.get("condition", "Good / Accepted"),
                    "storage_temp": p.get("storage_temp", "Ambient"),
                    "photo_url": p.get("photo_url") or None,
                    "vehicle_no": p.get("vehicle_no") or None,
                    "remarks": p.get("remarks", "Custody verified and accepted via QR scan."),
                    "timestamp": ev.event_time.isoformat(),
                }
            )
            step_num += 1
        elif ev.event_type in ("CUSTODY_APPEND", "INSPECT", "SALE", "PACKET_BATCH_CREATED"):
            actor_role = str(p.get("actor_role") or current_custodian_role).upper()
            actor_name = p.get("actor_name") or current_custodian_name
            current_custodian_role = actor_role
            current_custodian_name = actor_name
            if actor_role == "RETAILER" or p.get("retail_ready") or ev.event_type == "SALE":
                is_retailer_verified = True
            checkpoints.append(
                {
                    "step": step_num,
                    "event_type": ev.event_type,
                    "role": actor_role,
                    "actor_name": actor_name,
                    "location_name": p.get("location_name") or f"{actor_role.title()} Checkpoint",
                    "lat": float(p["lat"]) if p.get("lat") is not None else checkpoints[-1]["lat"],
                    "lng": float(p["lng"]) if p.get("lng") is not None else checkpoints[-1]["lng"],
                    "weight_kg": float(p.get("current_weight_kg") or p.get("net_qty_kg") or qty_val),
                    "condition": p.get("condition") or p.get("action_stage") or "Quality Checked",
                    "storage_temp": p.get("storage_temp", "Ambient"),
                    "photo_url": p.get("photo_url") or None,
                    "vehicle_no": p.get("vehicle_no") or None,
                    "action_stage": p.get("action_stage", ""),
                    "remarks": p.get("remarks", ""),
                    "timestamp": ev.event_time.isoformat(),
                }
            )
            step_num += 1

    if lot.state != "IN_TRANSIT":
        pending_handover = None

    is_editable = (
        lot.state in ("CREATED", "IN_CUSTODY")
        and lot.custodian_org_id == lot.created_by_org_id
        and lot.pending_receiver_org_id is None
        and current_custodian_role == "PRODUCER"
        and lot.lot_kind == "HARVEST"
    )

    parent_lots = []
    child_packet_batches = []
    if _depth == 0:
        for pe in LotEdge.objects.select_related("parent_lot").filter(child_lot=lot):
            parent_lots.append({
                "lot_id": str(pe.parent_lot.lot_id),
                "public_code": pe.parent_lot.public_code,
                "qty_kg": float(pe.qty_kg),
            })
        for ce in LotEdge.objects.select_related("child_lot").filter(parent_lot=lot):
            c_lot = ce.child_lot
            c_ev = TraceEvent.objects.filter(lot=c_lot, event_type__in=["PACKET_BATCH_CREATED", "SPLIT_CHILD"]).first()
            c_pay = (c_ev.payload if c_ev else {}) or {}
            child_packet_batches.append({
                "lot_id": str(c_lot.lot_id),
                "public_code": c_lot.public_code,
                "batch_id": c_lot.public_code,
                "qty_kg": float(ce.qty_kg),
                "packet_weight_g": c_pay.get("packet_weight_g"),
                "packet_count": c_pay.get("packet_count"),
                "package_label": c_pay.get("package_label", "Retail Packet"),
                "qr_url": f"https://annasutra.in/l/{c_lot.public_code}",
                "state": c_lot.state,
                "created_at": c_lot.created_at.isoformat(),
            })

    return {
        "lot_id": str(lot.lot_id),
        "batch_id": lot.public_code,
        "public_code": lot.public_code,
        "lot_kind": lot.lot_kind,
        "farmer_uid": farmer_uid,
        "product_category_code": cat_code,
        "product_category_name": cat_name,
        "state": lot.state,
        "custodian_org": str(lot.custodian_org_id),
        "created_by_org": str(lot.created_by_org_id),
        "pending_receiver_org": str(lot.pending_receiver_org_id) if lot.pending_receiver_org_id else None,
        "current_custodian_role": current_custodian_role,
        "current_custodian_name": current_custodian_name,
        "is_retailer_verified": is_retailer_verified,
        "pending_handover": pending_handover,
        "journey_checkpoints": checkpoints,
        "parent_lots": parent_lots,
        "child_packet_batches": child_packet_batches,
        "packet_weight_g": create_payload.get("packet_weight_g"),
        "packet_count": create_payload.get("packet_count"),
        "parent_lot_code": create_payload.get("parent_lot_code"),
        "on_hand_kg": qty_val,
        "net_qty_kg": qty_val,
        "unit": create_payload.get("unit", "Kg"),
        "packages_count": create_payload.get("packages_count", 1),
        "package_type": create_payload.get("package_type", "Plastic Crates"),
        "crop": crop_name,
        "variety": variety_name,
        "category": create_payload.get("category", cat_name),
        "harvest_date": create_payload.get("harvest_date") or lot.created_at.isoformat(),
        "sowing_date": create_payload.get("sowing_date", ""),
        "shelf_life_days": create_payload.get("shelf_life_days", 14),
        "origin_plot_id": str(lot.origin_plot_id) if lot.origin_plot_id else create_payload.get("plot_id", ""),
        "origin_plot_name": lot.origin_plot.plot_name if lot.origin_plot else create_payload.get("plot_name", ""),
        "plot_area_acres": float(lot.origin_plot.area_acres) if (lot.origin_plot and lot.origin_plot.area_acres) else create_payload.get("plot_area_acres"),
        "origin_lat": origin_lat,
        "origin_lng": origin_lng,
        "origin_location": origin_loc,
        "grade": create_payload.get("grade", "Grade A"),
        "farming_method": create_payload.get("farming_method", "Conventional"),
        "soil_type": create_payload.get("soil_type", ""),
        "irrigation_type": create_payload.get("irrigation_type", ""),
        "fertilizers": create_payload.get("fertilizers", ""),
        "last_spray_date": create_payload.get("last_spray_date", ""),
        "moisture_pct": create_payload.get("moisture_pct"),
        "cold_wash_applied": create_payload.get("cold_wash_applied", False),
        "harvest_photo_url": create_payload.get("harvest_photo_url", ""),
        "base_price_per_unit": create_payload.get("base_price_per_unit"),
        "estimated_value": create_payload.get("estimated_value"),
        "payment_status": create_payload.get("payment_status", "PENDING"),
        "intended_buyer": create_payload.get("intended_buyer", "APMC Mandi Aggregator"),
        "remarks": create_payload.get("remarks", ""),
        "is_editable": is_editable,
        "lot_seq": lot.head_seq,
        "created_at": lot.created_at.isoformat(),
    }


class LotListCreateView(APIView):
    """List or create crop/produce lots with rich agricultural and settlement fields."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request):
        user_org = request.user.org
        qs = Lot.objects.select_related(
            "product", "origin_plot", "custodian_org", "created_by_org", "pending_receiver_org"
        ).filter(
            models.Q(custodian_org=user_org)
            | models.Q(created_by_org=user_org)
            | models.Q(pending_receiver_org=user_org)
        )

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
        items = [_build_lot_item(lot) for lot in lots]

        return Response({"items": items, "next_cursor": None}, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        event_id_str = data.get("event_id")
        label_serial = data.get("label_serial")
        product_data = data.get("product")
        net_qty = data.get("net_qty_kg") if data.get("net_qty_kg") is not None else data.get("quantity_kg")
        event_time_str = data.get("event_time") or timezone.now().isoformat()

        if isinstance(product_data, str):
            product_data = {"name": product_data, "variety": data.get("variety", "")}
        elif not product_data and data.get("crop"):
            product_data = {"name": data.get("crop"), "variety": data.get("variety", "")}

        prod_name_hint = (product_data or {}).get("name", "") if isinstance(product_data, dict) else ""
        raw_cat = data.get("product_category_code") or data.get("crop_category") or data.get("category") or "VG"
        cat_code, cat_name = resolve_product_category(raw_cat, prod_name_hint)

        user_org = request.user.org

        if not label_serial:
            label_serial = generate_mentor_batch_id(request.user, cat_code, user_org)

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

        existing_event = TraceEvent.objects.filter(event_id=event_id).first()
        if existing_event:
            lot = existing_event.lot
            return Response(_build_lot_item(lot), status=status.HTTP_200_OK)

        with transaction.atomic():
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

            prod_name = product_data.get("name")
            prod_variety = product_data.get("variety")
            product, _ = Product.objects.get_or_create(
                name=prod_name,
                variety=prod_variety,
            )

            plot_obj = None
            plot_id_val = data.get("plot_id") or data.get("origin_plot_id")
            if plot_id_val:
                try:
                    from apps.organisations.models import Plot
                    plot_obj = Plot.objects.filter(plot_id=plot_id_val, org=user_org).first()
                except Exception:
                    pass

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

            qr_label.lot = lot
            qr_label.status = "BOUND"
            qr_label.bound_at = timezone.now()
            qr_label.save(update_fields=["lot", "status", "bound_at"])

            LotBalance.objects.create(
                lot=lot,
                qty_in_kg=net_qty,
            )

            prof = (
                EntityProfile.objects.filter(user_id=request.user.user_id, role="PRODUCER").first()
                or EntityProfile.objects.filter(user_id=request.user.user_id).first()
                or (EntityProfile.objects.filter(phone_e164=request.user.phone_e164).first() if request.user.phone_e164 else None)
            )
            farmer_uid = get_or_mint_farmer_uid(prof if prof else request.user)
            farmer_name = (f"{prof.first_name} {prof.last_name}".strip() or prof.organisation_name) if prof else user_org.name

            payload = {
                "label_serial": label_serial,
                "farmer_uid": farmer_uid,
                "farmer_name": farmer_name,
                "product_category_code": cat_code,
                "product_category_name": cat_name,
                "category": cat_name,
                "product": {"name": prod_name, "variety": prod_variety, "category": cat_name, "category_code": cat_code},
                "net_qty_kg": float(net_qty),
                "unit": data.get("unit", "Kg"),
                "packages_count": int(data.get("packages_count") or data.get("crate_count") or 1),
                "package_type": data.get("package_type", "Plastic Crates"),
                "harvest_date": data.get("harvest_date") or event_time_str,
                "sowing_date": data.get("sowing_date"),
                "shelf_life_days": int(data.get("shelf_life_days", 14)),
                "plot_id": str(plot_obj.plot_id) if plot_obj else (str(plot_id_val) if plot_id_val else None),
                "plot_name": plot_obj.plot_name if plot_obj else data.get("plot_name", ""),
                "plot_area_acres": float(plot_obj.area_acres) if (plot_obj and plot_obj.area_acres) else None,
                "origin_lat": float(data["origin_lat"]) if data.get("origin_lat") is not None else None,
                "origin_lng": float(data["origin_lng"]) if data.get("origin_lng") is not None else None,
                "origin_location": data.get("origin_location", ""),
                "grade": data.get("grade", "Grade A"),
                "farming_method": data.get("farming_method", "Conventional"),
                "soil_type": data.get("soil_type", ""),
                "irrigation_type": data.get("irrigation_type", ""),
                "fertilizers": data.get("fertilizers", ""),
                "last_spray_date": data.get("last_spray_date", ""),
                "moisture_pct": float(data["moisture_pct"]) if data.get("moisture_pct") is not None else None,
                "cold_wash_applied": bool(data.get("cold_wash_applied", False)),
                "harvest_photo_url": data.get("harvest_photo_url", ""),
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

        return Response(_build_lot_item(lot), status=status.HTTP_201_CREATED)


class LotDetailView(APIView):
    """Retrieve or update details for a specific lot by public code."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request, code):
        lot = Lot.objects.select_related(
            "custodian_org", "created_by_org", "pending_receiver_org", "product", "origin_plot"
        ).filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        if (
            lot.custodian_org_id != user_org.org_id
            and lot.created_by_org_id != user_org.org_id
            and lot.pending_receiver_org_id != user_org.org_id
        ):
            raise exceptions.PermissionDenied(
                {"detail": "You do not have permission to view lots belonging to another organisation.", "code": "CROSS_ORG_FORBIDDEN"}
            )

        return Response(_build_lot_item(lot), status=status.HTTP_200_OK)

    def put(self, request, code):
        """Update an editable harvest lot before next custody approval."""
        lot = Lot.objects.select_related("custodian_org", "created_by_org", "product").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        if lot.custodian_org_id != user_org.org_id and lot.created_by_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "You do not have permission to edit lots belonging to another organisation.", "code": "CROSS_ORG_FORBIDDEN"}
            )

        if (
            lot.state not in ("CREATED", "IN_CUSTODY")
            or lot.custodian_org_id != lot.created_by_org_id
            or lot.pending_receiver_org_id is not None
        ):
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

        net_qty = data.get("net_qty_kg") if data.get("net_qty_kg") is not None else data.get("quantity_kg")
        if net_qty is not None:
            try:
                net_qty = float(net_qty)
            except (ValueError, TypeError):
                net_qty = None

        with transaction.atomic():
            if prod_data.get("name") or data.get("variety") or data.get("crop"):
                cur_name = prod_data.get("name") or data.get("crop") or (lot.product.name if lot.product else "Produce")
                cur_variety = prod_data.get("variety") or data.get("variety") or (lot.product.variety if lot.product else "")
                product, _ = Product.objects.get_or_create(
                    name=cur_name,
                    variety=cur_variety,
                )
                lot.product = product
                lot.save(update_fields=["product"])

            plot_id_val = data.get("plot_id") or data.get("origin_plot_id")
            if plot_id_val:
                try:
                    from apps.organisations.models import Plot
                    plot_obj = Plot.objects.filter(plot_id=plot_id_val, org=user_org).first()
                    if plot_obj:
                        lot.origin_plot = plot_obj
                except Exception:
                    pass

            balance = LotBalance.objects.filter(lot=lot).first()
            if net_qty is not None and balance:
                balance.qty_in_kg = net_qty
                balance.save(update_fields=["qty_in_kg"])

            prev_create = TraceEvent.objects.filter(lot=lot, event_type__in=["HARVEST_CREATE", "LOT_UPDATE"]).order_by("-lot_seq").first()
            prev_payload = prev_create.payload if prev_create else {}
            raw_cat = data.get("product_category_code") or data.get("category") or prev_payload.get("product_category_code") or "VG"
            cat_code, cat_name = resolve_product_category(raw_cat, lot.product.name)

            lot.head_seq += 1
            payload = {
                "label_serial": lot.public_code,
                "farmer_uid": prev_payload.get("farmer_uid", ""),
                "farmer_name": prev_payload.get("farmer_name", user_org.name),
                "product_category_code": cat_code,
                "product_category_name": cat_name,
                "category": cat_name,
                "product": {"name": lot.product.name, "variety": lot.product.variety or "", "category": cat_name, "category_code": cat_code},
                "net_qty_kg": float(balance.qty_on_hand_kg if balance else (net_qty or 0.0)),
                "unit": data.get("unit", prev_payload.get("unit", "Kg")),
                "packages_count": int(data.get("packages_count", prev_payload.get("packages_count", 1))),
                "package_type": data.get("package_type", prev_payload.get("package_type", "Plastic Crates")),
                "harvest_date": data.get("harvest_date") or prev_payload.get("harvest_date"),
                "sowing_date": data.get("sowing_date") or prev_payload.get("sowing_date"),
                "shelf_life_days": int(data.get("shelf_life_days", prev_payload.get("shelf_life_days", 14))),
                "plot_id": str(lot.origin_plot_id) if lot.origin_plot_id else prev_payload.get("plot_id"),
                "plot_name": lot.origin_plot.plot_name if lot.origin_plot else data.get("plot_name", prev_payload.get("plot_name", "")),
                "origin_lat": float(data["origin_lat"]) if data.get("origin_lat") is not None else prev_payload.get("origin_lat"),
                "origin_lng": float(data["origin_lng"]) if data.get("origin_lng") is not None else prev_payload.get("origin_lng"),
                "origin_location": data.get("origin_location", prev_payload.get("origin_location", "")),
                "grade": data.get("grade", prev_payload.get("grade", "Grade A")),
                "farming_method": data.get("farming_method", prev_payload.get("farming_method", "Conventional")),
                "soil_type": data.get("soil_type", prev_payload.get("soil_type", "")),
                "irrigation_type": data.get("irrigation_type", prev_payload.get("irrigation_type", "")),
                "fertilizers": data.get("fertilizers", prev_payload.get("fertilizers", "")),
                "last_spray_date": data.get("last_spray_date", prev_payload.get("last_spray_date", "")),
                "moisture_pct": float(data["moisture_pct"]) if data.get("moisture_pct") is not None else prev_payload.get("moisture_pct"),
                "cold_wash_applied": bool(data.get("cold_wash_applied", prev_payload.get("cold_wash_applied", False))),
                "harvest_photo_url": data.get("harvest_photo_url", prev_payload.get("harvest_photo_url", "")),
                "base_price_per_unit": float(data["base_price_per_unit"]) if data.get("base_price_per_unit") is not None else prev_payload.get("base_price_per_unit"),
                "estimated_value": float(data["estimated_value"]) if data.get("estimated_value") is not None else prev_payload.get("estimated_value"),
                "payment_status": data.get("payment_status", prev_payload.get("payment_status", "PENDING")),
                "intended_buyer": data.get("intended_buyer", prev_payload.get("intended_buyer", "APMC Mandi Aggregator")),
                "remarks": data.get("remarks", prev_payload.get("remarks", "")),
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

        resp_item = _build_lot_item(lot)
        resp_item["message"] = "Harvest lot updated successfully."
        return Response(resp_item, status=status.HTTP_200_OK)


class LotEventsView(APIView):
    """Retrieve audit events for a lot."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request, code):
        lot = Lot.objects.filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        if (
            lot.custodian_org_id != user_org.org_id
            and lot.created_by_org_id != user_org.org_id
            and lot.pending_receiver_org_id != user_org.org_id
        ):
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


class LotHandoverRequestView(APIView):
    """POST /api/v1/lots/<str:code>/handover-request
    Initiate a secure 2-way custody handover request from the current custodian to the next party
    (AGGREGATOR, PROCESSOR, WHOLESALER, DISTRIBUTOR, or RETAILER) by Gmail, Role ID, or Mobile.
    """

    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        lot = Lot.objects.select_related("custodian_org", "created_by_org", "product").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        user_org = request.user.org
        if lot.custodian_org_id != user_org.org_id and lot.created_by_org_id != user_org.org_id:
            raise exceptions.PermissionDenied(
                {"detail": "Only the active custodian can initiate a custody handover request.", "code": "NOT_CUSTODIAN"}
            )

        if lot.state == "IN_TRANSIT":
            raise exceptions.ValidationError(
                {"detail": "A custody handover request is already pending for this batch.", "code": "ALREADY_IN_TRANSIT"}
            )

        data = request.data
        target_role = str(data.get("target_role") or data.get("to_role") or "AGGREGATOR").strip().upper()
        if target_role not in ("AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"):
            target_role = "AGGREGATOR"

        raw_phone = str(data.get("target_phone") or data.get("to_phone") or "").strip()
        target_phone = ""
        if raw_phone:
            digits = re.sub(r"\D", "", raw_phone)
            if len(digits) == 10:
                target_phone = f"+91{digits}"
            elif len(digits) >= 11:
                target_phone = f"+{digits}"

        target_email = str(data.get("target_email") or data.get("to_email") or "").strip().lower()
        target_role_id = str(data.get("target_role_id") or data.get("target_uid") or "").strip()

        target_name = str(data.get("target_name") or data.get("to_name") or f"Verified {target_role.title()}").strip()
        vehicle_no = str(data.get("vehicle_no") or "").strip().upper()
        location_name = str(data.get("location_name") or "").strip()
        remarks = str(data.get("remarks") or "").strip()

        balance = LotBalance.objects.filter(lot=lot).first()
        default_qty = float(balance.qty_on_hand_kg) if balance else 100.0
        try:
            declared_qty_kg = float(data.get("declared_qty_kg") or default_qty)
        except (ValueError, TypeError):
            declared_qty_kg = default_qty

        lat = None
        lng = None
        if data.get("lat") is not None and data.get("lng") is not None:
            try:
                lat = float(data["lat"])
                lng = float(data["lng"])
            except (ValueError, TypeError):
                pass

        # Resolve target Organisation by Gmail, Role ID, or Phone
        target_org = None
        if target_email:
            t_user = AppUser.objects.select_related("org").filter(email__iexact=target_email).first()
            if t_user and t_user.org:
                target_org = t_user.org
        if not target_org and target_role_id:
            t_prof = EntityProfile.objects.filter(entity_code=target_role_id).first()
            if t_prof:
                t_user = AppUser.objects.select_related("org").filter(user_id=t_prof.user_id).first()
                if t_user and t_user.org:
                    target_org = t_user.org
        if not target_org and target_phone:
            target_user = AppUser.objects.select_related("org").filter(phone_e164=target_phone).first()
            if target_user and target_user.org:
                target_org = target_user.org

        if not target_org or target_org.org_id == lot.custodian_org_id:
            org_type_map = {
                "AGGREGATOR": "AGGREGATOR",
                "PROCESSOR": "PROCESSOR",
                "WHOLESALER": "WHOLESALER",
                "DISTRIBUTOR": "DISTRIBUTOR",
                "RETAILER": "RETAILER",
            }
            target_org = Organisation.objects.create(
                name=target_name or f"{target_role.title()} ({target_email or target_phone[-4:] if target_phone else 'Partner'})",
                org_type=org_type_map.get(target_role, "AGGREGATOR"),
                verification="VERIFIED",
            )

        handover_pin = "".join(secrets.choice("0123456789") for _ in range(6))

        prof = EntityProfile.objects.filter(user_id=request.user.user_id).first()
        from_role = prof.role if prof else "PRODUCER"
        from_name = (prof.organisation_name or f"{prof.first_name} {prof.last_name}".strip()) if prof else user_org.name

        with transaction.atomic():
            Handover.objects.filter(lot=lot, state="PENDING").update(state="EXPIRED")

            handover = Handover.objects.create(
                handover_id=uuid.uuid4(),
                lot=lot,
                from_org=lot.custodian_org,
                to_org=target_org,
                declared_qty_kg=declared_qty_kg,
                state="PENDING",
                expires_at=timezone.now() + timezone.timedelta(hours=72),
            )

            lot.state = "IN_TRANSIT"
            lot.pending_receiver_org = target_org
            lot.head_seq += 1

            payload = {
                "handover_id": str(handover.handover_id),
                "from_role": from_role,
                "from_name": from_name,
                "target_role": target_role,
                "target_phone": target_phone,
                "target_email": target_email,
                "target_role_id": target_role_id,
                "target_name": target_name,
                "declared_qty_kg": declared_qty_kg,
                "vehicle_no": vehicle_no,
                "handover_pin": handover_pin,
                "location_name": location_name,
                "lat": lat,
                "lng": lng,
                "remarks": remarks,
            }
            event_hash = calculate_event_hash(bytes(lot.head_hash or b""), "HANDOVER_REQUEST", lot.head_seq, payload)
            TraceEvent.objects.create(
                event_id=uuid.uuid4(),
                lot=lot,
                lot_seq=lot.head_seq,
                event_type="HANDOVER_REQUEST",
                event_time=timezone.now().isoformat(),
                org=user_org,
                user=request.user,
                payload=payload,
                event_hash=event_hash,
            )
            lot.head_hash = event_hash
            lot.save(update_fields=["state", "pending_receiver_org", "head_seq", "head_hash"])

            from apps.publicview.services import refresh_public_view
            refresh_public_view(lot)

        item = _build_lot_item(lot)
        item["handover_id"] = str(handover.handover_id)
        item["handover_pin"] = handover_pin
        item["message"] = f"Custody handover request sent to {target_name} ({target_role}). Batch is now locked and IN_TRANSIT."
        return Response(item, status=status.HTTP_201_CREATED)


class IncomingHandoversView(APIView):
    """GET /api/v1/lots/handovers/incoming
    Return pending custody handover requests and active custody lots for downstream roles
    (Aggregator, Processor, Wholesaler, Distributor, Retailer).
    """

    permission_classes = [IsVerifiedOrg]

    def get(self, request):
        user_org = request.user.org
        prof = (
            EntityProfile.objects.filter(user_id=request.user.user_id).first()
            or (EntityProfile.objects.filter(phone_e164=request.user.phone_e164).first() if request.user.phone_e164 else None)
        )
        role_filter = str(request.query_params.get("role") or (prof.role if prof else "")).strip().upper()
        user_phone = getattr(request.user, "phone_e164", "") or ""
        user_email = (getattr(request.user, "email", "") or "").strip().lower()

        transit_lots = Lot.objects.select_related(
            "product", "origin_plot", "custodian_org", "created_by_org", "pending_receiver_org"
        ).filter(state="IN_TRANSIT").order_by("-created_at")[:100]

        pending_requests = []
        for lot in transit_lots:
            item = _build_lot_item(lot)
            ph = item.get("pending_handover") or {}
            is_match = (
                lot.pending_receiver_org_id == user_org.org_id
                or (user_phone and ph.get("target_phone") == user_phone)
                or (user_email and ph.get("target_email") == user_email)
                or (role_filter and ph.get("target_role") == role_filter)
                or not role_filter
                or role_filter == "PRODUCER"
            )
            if is_match:
                pending_requests.append(item)

        custody_qs = Lot.objects.select_related(
            "product", "origin_plot", "custodian_org", "created_by_org", "pending_receiver_org"
        ).filter(state__in=["IN_CUSTODY", "CREATED"]).order_by("-created_at")[:100]

        active_custody_lots = []
        for lot in custody_qs:
            item = _build_lot_item(lot)
            if (
                lot.custodian_org_id == user_org.org_id
                or (role_filter and item.get("current_custodian_role") == role_filter)
            ):
                active_custody_lots.append(item)

        return Response(
            {
                "pending_requests": pending_requests,
                "incoming_requests": pending_requests,
                "active_custody_lots": active_custody_lots,
            },
            status=status.HTTP_200_OK,
        )


class LotHandoverAcceptView(APIView):
    """POST /api/v1/lots/<str:code>/handover-accept
    Next party (Aggregator, Processor, Wholesaler, Distributor, or Retailer) confirms custody acceptance
    by scanning/verifying the lot QR code and logging current weight, condition, photo, and GPS.
    Permanently locks the Farmer's batch record.
    """

    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        lot = Lot.objects.select_related("custodian_org", "created_by_org", "pending_receiver_org", "product").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found for scanned QR code.", "code": "NOT_FOUND"})

        user_org = request.user.org
        prof = (
            EntityProfile.objects.filter(user_id=request.user.user_id).first()
            or (EntityProfile.objects.filter(phone_e164=request.user.phone_e164).first() if request.user.phone_e164 else None)
        )

        data = request.data
        last_req = TraceEvent.objects.filter(lot=lot, event_type="HANDOVER_REQUEST").order_by("-lot_seq").first()
        req_role = (last_req.payload or {}).get("target_role") if last_req else None

        actor_role = str(data.get("actor_role") or req_role or (prof.role if prof else "AGGREGATOR")).strip().upper()
        if actor_role not in ("AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"):
            actor_role = "AGGREGATOR"

        actor_name = str(
            data.get("actor_name")
            or ((last_req.payload or {}).get("target_name") if last_req else "")
            or (prof.organisation_name if prof and prof.organisation_name else "")
            or user_org.name
        ).strip()

        balance = LotBalance.objects.filter(lot=lot).first()
        default_qty = float(balance.qty_on_hand_kg) if balance else 100.0
        try:
            received_qty_kg = float(data.get("received_qty_kg") or data.get("current_weight_kg") or default_qty)
        except (ValueError, TypeError):
            received_qty_kg = default_qty

        condition = str(data.get("condition") or "Fresh & Verified Intact").strip()
        storage_temp = str(data.get("storage_temp") or "Ambient (24°C)").strip()
        photo_url = str(data.get("photo_url") or "").strip()
        location_name = str(
            data.get("location_name")
            or (f"{prof.village_town}, {prof.district}" if prof and prof.district else f"{actor_role.title()} Hub")
        ).strip()
        remarks = str(data.get("remarks") or f"Custody accepted by {actor_name} ({actor_role}).").strip()

        lat = None
        lng = None
        if data.get("lat") is not None and data.get("lng") is not None:
            try:
                lat = float(data["lat"])
                lng = float(data["lng"])
            except (ValueError, TypeError):
                pass

        with transaction.atomic():
            acceptor_org = lot.pending_receiver_org or user_org
            if acceptor_org.org_id == lot.created_by_org_id:
                org_type_map = {
                    "AGGREGATOR": "AGGREGATOR",
                    "PROCESSOR": "PROCESSOR",
                    "WHOLESALER": "WHOLESALER",
                    "DISTRIBUTOR": "DISTRIBUTOR",
                    "RETAILER": "RETAILER",
                }
                acceptor_org = Organisation.objects.create(
                    name=actor_name or f"Verified {actor_role.title()}",
                    org_type=org_type_map.get(actor_role, "AGGREGATOR"),
                    verification="VERIFIED",
                )

            open_ho = Handover.objects.filter(lot=lot, state="PENDING").order_by("-opened_at").first()
            if open_ho:
                diff = abs(float(open_ho.declared_qty_kg) - received_qty_kg)
                open_ho.received_qty_kg = received_qty_kg
                open_ho.state = "ACCEPTED_WITH_DISCREPANCY" if diff > 0.5 else "ACCEPTED"
                open_ho.closed_at = timezone.now()
                open_ho.save(update_fields=["received_qty_kg", "state", "closed_at"])
            else:
                Handover.objects.create(
                    handover_id=uuid.uuid4(),
                    lot=lot,
                    from_org=lot.custodian_org,
                    to_org=acceptor_org,
                    declared_qty_kg=received_qty_kg,
                    received_qty_kg=received_qty_kg,
                    state="ACCEPTED",
                    expires_at=timezone.now() + timezone.timedelta(hours=24),
                    closed_at=timezone.now(),
                )

            if balance:
                deductions = float(balance.qty_in_kg) - float(balance.qty_on_hand_kg)
                balance.qty_in_kg = received_qty_kg + deductions
                balance.save(update_fields=["qty_in_kg"])

            lot.custodian_org = acceptor_org
            lot.pending_receiver_org = None
            lot.state = "IN_CUSTODY"
            lot.head_seq += 1

            payload = {
                "actor_role": actor_role,
                "actor_name": actor_name,
                "received_qty_kg": received_qty_kg,
                "condition": condition,
                "storage_temp": storage_temp,
                "photo_url": photo_url,
                "location_name": location_name,
                "lat": lat,
                "lng": lng,
                "retail_ready": actor_role == "RETAILER",
                "remarks": remarks,
            }
            event_hash = calculate_event_hash(bytes(lot.head_hash or b""), "HANDOVER_ACCEPT", lot.head_seq, payload)
            TraceEvent.objects.create(
                event_id=uuid.uuid4(),
                lot=lot,
                lot_seq=lot.head_seq,
                event_type="HANDOVER_ACCEPT",
                event_time=timezone.now().isoformat(),
                org=acceptor_org,
                user=request.user,
                payload=payload,
                event_hash=event_hash,
            )
            lot.head_hash = event_hash
            lot.save(update_fields=["custodian_org", "pending_receiver_org", "state", "head_seq", "head_hash"])

            from apps.publicview.services import refresh_public_view
            refresh_public_view(lot)

        item = _build_lot_item(lot)
        item["message"] = f"Custody accepted by {actor_name} ({actor_role}). Previous custodian is permanently locked."
        return Response(item, status=status.HTTP_200_OK)


class LotAppendScanUpdateView(APIView):
    """POST /api/v1/lots/<str:code>/append-scan
    Downstream parties (Aggregator, Processor, Wholesaler, Distributor, Retailer) scan the lot QR code
    to append current weight, product condition, storage temperature, photo capture, and GPS location.
    Cannot overwrite original farmer harvest data.
    """

    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        lot = Lot.objects.select_related("custodian_org", "created_by_org", "product").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found for scanned QR code.", "code": "NOT_FOUND"})

        user_org = request.user.org
        prof = (
            EntityProfile.objects.filter(user_id=request.user.user_id).first()
            or (EntityProfile.objects.filter(phone_e164=request.user.phone_e164).first() if request.user.phone_e164 else None)
        )

        current_item = _build_lot_item(lot)
        data = request.data

        actor_role = str(
            data.get("actor_role")
            or (current_item.get("current_custodian_role") if current_item.get("current_custodian_role") != "PRODUCER" else "")
            or (prof.role if prof and prof.role != "PRODUCER" else "AGGREGATOR")
        ).strip().upper()

        if actor_role not in ("AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"):
            actor_role = "AGGREGATOR"

        actor_name = str(
            data.get("actor_name")
            or current_item.get("current_custodian_name")
            or (prof.organisation_name if prof and prof.organisation_name else user_org.name)
        ).strip()

        balance = LotBalance.objects.filter(lot=lot).first()
        default_qty = float(balance.qty_on_hand_kg) if balance else 100.0
        try:
            current_weight_kg = float(data.get("current_weight_kg") or data.get("weight_kg") or data.get("net_qty_kg") or default_qty)
        except (ValueError, TypeError):
            current_weight_kg = default_qty

        condition = str(data.get("condition") or "Good / Intact").strip()
        storage_temp = str(data.get("storage_temp") or "Ambient").strip()
        action_stage = str(data.get("action_stage") or f"{actor_role.title()} Scan Update").strip()
        photo_url = str(data.get("photo_url") or "").strip()
        location_name = str(data.get("location_name") or f"{actor_role.title()} Facility").strip()
        remarks = str(data.get("remarks") or "").strip()
        retail_ready = bool(data.get("retail_ready")) or (actor_role == "RETAILER")

        lat = None
        lng = None
        if data.get("lat") is not None and data.get("lng") is not None:
            try:
                lat = float(data["lat"])
                lng = float(data["lng"])
            except (ValueError, TypeError):
                pass

        with transaction.atomic():
            if balance and current_weight_kg > 0:
                deductions = float(balance.qty_in_kg) - float(balance.qty_on_hand_kg)
                balance.qty_in_kg = current_weight_kg + deductions
                balance.save(update_fields=["qty_in_kg"])

            lot.head_seq += 1
            payload = {
                "actor_role": actor_role,
                "actor_name": actor_name,
                "current_weight_kg": current_weight_kg,
                "condition": condition,
                "storage_temp": storage_temp,
                "action_stage": action_stage,
                "photo_url": photo_url,
                "location_name": location_name,
                "lat": lat,
                "lng": lng,
                "retail_ready": retail_ready,
                "remarks": remarks,
            }
            event_hash = calculate_event_hash(bytes(lot.head_hash or b""), "CUSTODY_APPEND", lot.head_seq, payload)
            TraceEvent.objects.create(
                event_id=uuid.uuid4(),
                lot=lot,
                lot_seq=lot.head_seq,
                event_type="CUSTODY_APPEND",
                event_time=timezone.now().isoformat(),
                org=lot.custodian_org,
                user=request.user,
                payload=payload,
                event_hash=event_hash,
            )
            lot.head_hash = event_hash
            lot.save(update_fields=["head_seq", "head_hash"])

            from apps.publicview.services import refresh_public_view
            refresh_public_view(lot)

        item = _build_lot_item(lot)
        item["message"] = f"Scan update appended to immutable ledger by {actor_name} ({actor_role})."
        return Response(item, status=status.HTTP_201_CREATED)


class LotPacketBatchesView(APIView):
    """POST /api/v1/lots/<str:code>/packet-batches
    Section 3.7 & Decision 34 (Small Packet Batches with Child Batch QR):
    Allows Aggregator, Processor, Wholesaler, Distributor, or Retailer to split/repack an accepted lot
    into small consumer packet batches (e.g., 500 g packets).
    Each packet batch is a child lot with its own 32-char Lot Code and one batch-level child QR
    printed across all packets of that batch, preserving full parent lineage and enforcing mass balance.
    """

    permission_classes = [IsVerifiedOrg]

    def post(self, request, code):
        parent_lot = Lot.objects.select_related("custodian_org", "created_by_org", "product", "origin_plot").filter(public_code=code).first()
        if not parent_lot:
            raise exceptions.NotFound({"detail": "Parent lot not found.", "code": "NOT_FOUND"})

        parent_item = _build_lot_item(parent_lot)
        data = request.data or {}

        prof = (
            EntityProfile.objects.filter(user_id=request.user.user_id).first()
            or (EntityProfile.objects.filter(phone_e164=request.user.phone_e164).first() if request.user.phone_e164 else None)
        )
        actor_role = str(
            data.get("actor_role")
            or (parent_item.get("current_custodian_role") if parent_item.get("current_custodian_role") != "PRODUCER" else "")
            or (prof.role if prof and prof.role != "PRODUCER" else "PROCESSOR")
        ).strip().upper()
        if actor_role not in ("AGGREGATOR", "PROCESSOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"):
            actor_role = "PROCESSOR"

        actor_name = str(
            data.get("actor_name")
            or parent_item.get("current_custodian_name")
            or (prof.organisation_name if prof and prof.organisation_name else request.user.org.name)
        ).strip()

        try:
            packet_weight_g = float(data.get("packet_weight_g") or 500.0)
            packet_count = int(data.get("packet_count") or 10)
        except (ValueError, TypeError):
            raise exceptions.ValidationError({"detail": "packet_weight_g and packet_count must be positive numbers.", "code": "INVALID_PACKETS"})

        if packet_weight_g <= 0 or packet_count <= 0:
            raise exceptions.ValidationError({"detail": "packet_weight_g and packet_count must be greater than zero.", "code": "INVALID_PACKETS"})

        batch_qty_kg = data.get("batch_qty_kg")
        if batch_qty_kg is not None:
            batch_qty_kg = float(batch_qty_kg)
        else:
            batch_qty_kg = round((packet_weight_g * packet_count) / 1000.0, 3)

        package_label = str(data.get("package_label") or f"{int(packet_weight_g)}g Consumer Packet").strip()
        location_name = str(data.get("location_name") or f"{actor_role.title()} Packhouse").strip()
        remarks = str(data.get("remarks") or f"Packed {packet_count} x {int(packet_weight_g)}g packets from parent lot {parent_lot.public_code}.").strip()

        with transaction.atomic():
            parent_balance = LotBalance.objects.select_for_update().filter(lot=parent_lot).first()
            available_kg = float(parent_balance.qty_on_hand_kg) if parent_balance else float(parent_item.get("on_hand_kg") or 0.0)

            if batch_qty_kg > available_kg + 0.001:
                raise exceptions.ValidationError({
                    "detail": f"Mass balance exceeded: requested packet batch weight ({batch_qty_kg} kg) exceeds available parent lot balance ({available_kg} kg).",
                    "code": "MASS_BALANCE_EXCEEDED",
                })

            cat_code = parent_item.get("product_category_code") or "VG"
            cat_name = parent_item.get("product_category_name") or "Vegetables"
            child_code = generate_mentor_batch_id(request.user, cat_code, parent_lot.custodian_org)

            block = QrBlock.objects.create(
                block_id=uuid.uuid4(),
                issued_to_org=parent_lot.custodian_org,
                issued_by=request.user,
                count=1,
            )
            child_lot = Lot.objects.create(
                lot_id=uuid.uuid4(),
                public_code=child_code,
                product=parent_lot.product,
                origin_plot=parent_lot.origin_plot,
                created_by_org=parent_lot.created_by_org,
                lot_kind="SPLIT_CHILD",
                state="IN_CUSTODY",
                custodian_org=parent_lot.custodian_org,
                head_seq=1,
            )
            QrLabel.objects.create(
                serial=child_code,
                block=block,
                issued_to_org=parent_lot.custodian_org,
                lot=child_lot,
                status="BOUND",
                bound_at=timezone.now(),
            )
            LotBalance.objects.create(
                lot=child_lot,
                qty_in_kg=Decimal(str(batch_qty_kg)),
            )

            if parent_balance:
                parent_balance.qty_split_out_kg = Decimal(str(float(parent_balance.qty_split_out_kg) + batch_qty_kg))
                parent_balance.save(update_fields=["qty_split_out_kg"])

            split_event_id = uuid.uuid4()
            LotEdge.objects.create(
                parent_lot=parent_lot,
                child_lot=child_lot,
                qty_kg=Decimal(str(batch_qty_kg)),
                event_id=split_event_id,
            )

            # Record TraceEvent on child packet batch preserving full upstream lineage
            child_payload = {
                "label_serial": child_code,
                "parent_lot_code": parent_lot.public_code,
                "farmer_uid": parent_item.get("farmer_uid", ""),
                "farmer_name": parent_item.get("journey_checkpoints", [{}])[0].get("actor_name", "Origin Producer"),
                "product_category_code": cat_code,
                "product_category_name": cat_name,
                "category": cat_name,
                "product": {
                    "name": parent_lot.product.name if parent_lot.product else parent_item.get("crop", ""),
                    "variety": parent_lot.product.variety if parent_lot.product else parent_item.get("variety", ""),
                    "category": cat_name,
                    "category_code": cat_code,
                },
                "net_qty_kg": batch_qty_kg,
                "unit": "Kg",
                "packages_count": packet_count,
                "package_type": package_label,
                "packet_weight_g": packet_weight_g,
                "packet_count": packet_count,
                "package_label": package_label,
                "harvest_date": parent_item.get("harvest_date"),
                "shelf_life_days": parent_item.get("shelf_life_days", 14),
                "origin_lat": parent_item.get("origin_lat"),
                "origin_lng": parent_item.get("origin_lng"),
                "origin_location": parent_item.get("origin_location"),
                "grade": parent_item.get("grade", "Grade A"),
                "farming_method": parent_item.get("farming_method", "Conventional"),
                "actor_role": actor_role,
                "actor_name": actor_name,
                "location_name": location_name,
                "action_stage": f"Packet Batch Created ({packet_count} x {int(packet_weight_g)}g)",
                "condition": f"{packet_count} packets ({int(packet_weight_g)}g each)",
                "retail_ready": actor_role == "RETAILER",
                "upstream_checkpoints": parent_item.get("journey_checkpoints", []),
                "remarks": remarks,
            }
            c_hash = calculate_event_hash(b"", "PACKET_BATCH_CREATED", 1, child_payload)
            TraceEvent.objects.create(
                event_id=split_event_id,
                lot=child_lot,
                lot_seq=1,
                event_type="PACKET_BATCH_CREATED",
                event_time=timezone.now().isoformat(),
                org=parent_lot.custodian_org,
                user=request.user,
                qty_kg=Decimal(str(batch_qty_kg)),
                payload=child_payload,
                event_hash=c_hash,
            )
            child_lot.head_hash = c_hash
            child_lot.save(update_fields=["head_hash"])

            # Also record a CUSTODY_APPEND note on parent lot so parent journey reflects the packet split
            parent_lot.head_seq += 1
            p_payload = {
                "actor_role": actor_role,
                "actor_name": actor_name,
                "current_weight_kg": max(0.0, round(available_kg - batch_qty_kg, 3)),
                "action_stage": f"Split Packet Batch {child_code} ({packet_count} x {int(packet_weight_g)}g = {batch_qty_kg} kg)",
                "condition": f"Packet Batch Minted ({child_code})",
                "location_name": location_name,
                "child_batch_code": child_code,
                "packet_weight_g": packet_weight_g,
                "packet_count": packet_count,
                "remarks": remarks,
            }
            p_hash = calculate_event_hash(bytes(parent_lot.head_hash or b""), "CUSTODY_APPEND", parent_lot.head_seq, p_payload)
            TraceEvent.objects.create(
                event_id=uuid.uuid4(),
                lot=parent_lot,
                lot_seq=parent_lot.head_seq,
                event_type="CUSTODY_APPEND",
                event_time=timezone.now().isoformat(),
                org=parent_lot.custodian_org,
                user=request.user,
                qty_kg=Decimal(str(batch_qty_kg)),
                payload=p_payload,
                event_hash=p_hash,
            )
            parent_lot.head_hash = p_hash
            parent_lot.save(update_fields=["head_seq", "head_hash"])

            from apps.publicview.services import refresh_public_view
            refresh_public_view(parent_lot)
            refresh_public_view(child_lot)

        child_item = _build_lot_item(child_lot)
        updated_parent = _build_lot_item(parent_lot)
        return Response({
            "status": "created",
            "message": f"Small packet batch {child_code} ({packet_count} x {int(packet_weight_g)}g = {batch_qty_kg} kg) created with child QR.",
            "packet_batch": child_item,
            "parent_lot": updated_parent,
        }, status=status.HTTP_201_CREATED)


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


class LotQrImageView(APIView):
    """Return crisp PNG image bytes of QR code pointing to public lot URL."""

    def get(self, request, code):
        from apps.identity.services.pdf_sheet import generate_qr_image_bytes
        from django.http import HttpResponse

        url = f"https://annasutra.in/l/{code}"
        buf = generate_qr_image_bytes(url)
        return HttpResponse(buf.getvalue(), content_type="image/png")


class LotStickerPdfView(APIView):
    """Return printable A4 sticker sheet PDF for a lot."""

    permission_classes = [IsVerifiedOrg]

    def get(self, request, code):
        from apps.identity.services.pdf_sheet import render_a4_sticker_sheet
        from django.http import HttpResponse

        lot = Lot.objects.select_related("created_by_org").filter(public_code=code).first()
        if not lot:
            raise exceptions.NotFound({"detail": "Lot not found.", "code": "NOT_FOUND"})

        org_name = lot.created_by_org.name if lot.created_by_org else "AnnaSutra"
        count = int(request.query_params.get("count", 24))
        count = max(1, min(count, 96))
        serials = [code] * count

        pdf_bytes = render_a4_sticker_sheet(
            serials=serials,
            entity_code=code,
            org_name=org_name,
        )
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="lot_stickers_{code}.pdf"'
        return response
