"""Public view projection service for AnnaSutra.

Generates and refreshes read-only public_view records strictly adhering to
the allow-list schema in api/openapi.yaml. Never leaks PII, farmer names,
phone numbers, coordinates, or financial transactions.
"""
from django.utils import timezone
from apps.publicview.models import PublicView
from apps.alerts.models import ScanLog
from apps.custody.models import Handover
from apps.ledger.models import TraceEvent


def refresh_public_view(lot) -> PublicView:
    """Builds or refreshes the public_view record for a lot."""
    # 1. Product name & variety
    prod = lot.product
    product_str = f"{prod.name} ({prod.variety})" if prod.variety else prod.name

    # 2. Harvest date from initial HARVEST_CREATE trace event or lot creation date
    harvest_event = TraceEvent.objects.filter(lot=lot, event_type="HARVEST_CREATE").first()
    if harvest_event and "harvest_date" in harvest_event.payload:
        harvest_date = harvest_event.payload["harvest_date"]
    elif harvest_event and harvest_event.event_time:
        harvest_date = harvest_event.event_time.date().isoformat()
    else:
        harvest_date = lot.created_at.date().isoformat()

    # 3. Coarse region (district and state only, never precise coordinates)
    region = "Purba Bardhaman, West Bengal"
    if lot.origin_plot and lot.origin_plot.facility:
        fac = lot.origin_plot.facility
        if fac.address:
            # Mask or extract coarse location
            region = fac.address.split(",")[-1].strip() or region

    # 4. Stages confirmed: count of accepted handovers
    stages_confirmed = Handover.objects.filter(
        lot=lot,
        state__in=["ACCEPTED", "ACCEPTED_WITH_DISCREPANCY"],
    ).count()

    # 5. Quality checks: count of inspection events
    quality_checks = TraceEvent.objects.filter(lot=lot, event_type="INSPECT").count()

    # 6. Certificates: list of lab certificates if any
    certificates = []
    # Can query lab_certificate table if available

    # 7. Scan count
    scan_count = ScanLog.objects.filter(serial=lot.public_code).count()

    # 8. Gaps flagged: whether any handover expired or unconfirmed
    gaps_flagged = Handover.objects.filter(lot=lot, state="EXPIRED").exists()

    # 9. Disclaimer mandated by docs/00_MASTER_BRIEF.md
    disclaimer = (
        "This record is based on information entered by supply-chain participants. "
        "It does not prove the contents of this package."
    )

    payload = {
        "code": lot.public_code,
        "product": product_str,
        "harvest_date": str(harvest_date),
        "region": region,
        "stages_confirmed": stages_confirmed,
        "quality_checks": quality_checks,
        "certificates": certificates,
        "scan_count": scan_count,
        "gaps_flagged": gaps_flagged,
        "disclaimer": disclaimer,
    }

    public_view, _ = PublicView.objects.update_or_create(
        lot=lot,
        defaults={
            "public_code": lot.public_code,
            "payload": payload,
            "refreshed_at": timezone.now(),
        },
    )
    return public_view
