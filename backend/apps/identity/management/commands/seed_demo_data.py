"""Management command to seed initial local development and demo data.

Creates:
1. Superuser: admin / admin123
2. Single Admin user: devnetraconsultancy@gmail.com
3. Sample Verified Producer: Bengal Organic Farmers Collective (farmer.bengal@gmail.com)
4. Sample Heritage Crop: Govindobhog Rice
5. Sample Traceable Lot: DEMO-LOT-001 with public provenance payload
"""

import hashlib
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.identity.models import AppUser, EntityProfile
from apps.organisations.models import Organisation
from apps.lots.models import Lot, Product
from apps.inventory.models import LotBalance
from apps.labels.models import QrBlock, QrLabel
from apps.publicview.models import PublicView


class Command(BaseCommand):
    help = "Seeds initial demo data for local development"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding AnnaSutra local development data..."))

        # 1. Django Superuser
        User = get_user_model()
        admin_user, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@annasutra.in"})
        if created or not admin_user.check_password("admin123"):
            admin_user.set_password("admin123")
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Superuser created/updated: admin / admin123"))
        else:
            self.stdout.write("[OK] Superuser already exists: admin / admin123")

        # 2. Operator Org & Single Admin User (Decision 32)
        admin_org, _ = Organisation.objects.get_or_create(
            name="AnnaSutra National Operations",
            defaults={
                "org_type": "OPERATOR",
                "verification": "VERIFIED",
                "fssai_no": "FSSAI-OPERATOR-001",
            },
        )
        admin_app_user, _ = AppUser.objects.get_or_create(
            email="devnetraconsultancy@gmail.com",
            defaults={
                "org": admin_org,
                "phone_e164": "+919999900000",
                "role": "OWNER",
                "status": "ACTIVE",
            },
        )
        self.stdout.write(self.style.SUCCESS("[OK] Admin Identity ready: devnetraconsultancy@gmail.com"))

        # 3. Verified Producer (Farmer) Organisation
        producer_org, _ = Organisation.objects.get_or_create(
            name="Bengal Organic Farmers Collective",
            defaults={
                "org_type": "FARMER",
                "verification": "VERIFIED",
                "fssai_no": "FSSAI-12824999000123",
            },
        )
        producer_user, _ = AppUser.objects.get_or_create(
            email="farmer.bengal@gmail.com",
            defaults={
                "org": producer_org,
                "phone_e164": "+919876543210",
                "role": "OWNER",
                "status": "ACTIVE",
            },
        )
        EntityProfile.objects.get_or_create(
            user_id=producer_user.user_id,
            role="PRODUCER",
            defaults={
                "entity_code": "PROD-WB-001",
                "first_name": "Debabrata",
                "last_name": "Mukherjee",
                "organisation_name": "Bengal Organic Farmers Collective",
                "gender": "MALE",
                "phone_e164": "+919876543210",
                "email": "farmer.bengal@gmail.com",
                "total_land_acres": 12.5,
                "address_line1": "Village Rayan, Post Galsi",
                "village_town": "Bardhaman",
                "district": "Purba Bardhaman",
                "state": "West Bengal",
                "pincode": "713101",
                "photo_object_key": "photos/producer_debabrata.jpg",
                "status": "VERIFIED",
                "submitted_at": timezone.now(),
                "verified_at": timezone.now(),
            },
        )
        self.stdout.write(self.style.SUCCESS("[OK] Verified Producer ready: Bengal Organic Farmers Collective (PROD-WB-001)"))

        # 4. Product: Govindobhog Heritage Rice
        product, _ = Product.objects.get_or_create(
            name="Heritage Govindobhog Rice",
            variety="Aromatic Heritage Grain",
        )

        # 5. Lot: DEMO-LOT-001
        dummy_hash = hashlib.sha256(b"genesis-lot-demo-001").digest()
        lot, _ = Lot.objects.get_or_create(
            public_code="DEMO-LOT-001",
            defaults={
                "product": product,
                "created_by_org": producer_org,
                "custodian_org": producer_org,
                "lot_kind": "HARVEST",
                "state": "IN_CUSTODY",
                "head_seq": 1,
                "head_hash": dummy_hash,
            },
        )

        # 6. QR Block & Label (Bound to Lot)
        qr_block, _ = QrBlock.objects.get_or_create(
            issued_to_org=producer_org,
            issued_by=admin_app_user,
            defaults={
                "count": 100,
            },
        )
        qr_label, _ = QrLabel.objects.get_or_create(
            serial="DEMO-LOT-001",
            defaults={
                "block": qr_block,
                "issued_to_org": producer_org,
                "lot": lot,
                "status": "BOUND",
                "bound_at": timezone.now(),
            },
        )

        # 7. Mass Balance
        LotBalance.objects.get_or_create(
            lot=lot,
            defaults={
                "qty_in_kg": 1000.0,
                "qty_out_transferred_kg": 0.0,
                "qty_split_out_kg": 0.0,
                "qty_rejected_kg": 0.0,
                "qty_waste_kg": 0.0,
                "qty_sold_kg": 0.0,
                "qty_variance_kg": 0.0,
            },
        )

        # 8. Public Provenance View
        public_payload = {
            "code": "DEMO-LOT-001",
            "batch_id": "DEMO-LOT-001",
            "product_name": "Heritage Govindobhog Rice",
            "variety": "Aromatic Heritage Grain (GI-Tagged)",
            "net_qty_kg": 1000.0,
            "harvest_date": "2026-10-15",
            "farmer_name_masked": "Debabrata M***",
            "farmer_uid_masked": "PROD-WB-001",
            "farm_location": "Bardhaman, West Bengal",
            "fssai_license": "12824999000123",
            "quality_grade": "Grade A Export Quality",
            "pesticide_status": "Zero Chemical Residue Verified",
            "timeline": [
                {
                    "stage": "Harvest & Sowing Record",
                    "date": "2026-10-15",
                    "actor": "Bengal Organic Farmers Collective",
                    "status": "COMPLETED",
                    "location": "Bardhaman, West Bengal",
                },
                {
                    "stage": "Quality & Moisture Assay",
                    "date": "2026-10-18",
                    "actor": "AgriQ Labs Kolkata (NABL Accredited)",
                    "status": "PASSED",
                    "detail": "Moisture: 12.1%, Purity: 99.4%",
                },
                {
                    "stage": "Storage & Custody",
                    "date": "2026-10-22",
                    "actor": "Bengal Organic Farmers Collective",
                    "status": "SECURED",
                    "detail": "Hermetic grain silo storage",
                },
            ],
        }

        PublicView.objects.update_or_create(
            lot=lot,
            defaults={
                "public_code": "DEMO-LOT-001",
                "payload": public_payload,
                "refreshed_at": timezone.now(),
            },
        )

        self.stdout.write(self.style.SUCCESS("[OK] Traceable Lot ready: DEMO-LOT-001 (View at /q/DEMO-LOT-001)"))
        self.stdout.write(self.style.SUCCESS("[OK] Demo data seed complete!"))
