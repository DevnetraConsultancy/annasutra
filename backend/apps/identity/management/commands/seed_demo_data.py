"""Management command to ensure administrative setup for AnnaSutra.

Configures:
1. Superuser: admin / admin123
2. Single Admin user: devnetraconsultancy@gmail.com
Zero preloaded sample lots or mock entities.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.identity.models import AppUser
from apps.organisations.models import Organisation


class Command(BaseCommand):
    help = "Ensures admin identity setup without any sample or mock data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Verifying AnnaSutra administrative configuration..."))

        # 1. Django Superuser
        User = get_user_model()
        admin_user, created = User.objects.get_or_create(username="admin", defaults={"email": "admin@annasutra.in"})
        if created or not admin_user.check_password("admin123"):
            admin_user.set_password("admin123")
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Superuser ready: admin / admin123"))
        else:
            self.stdout.write("[OK] Superuser ready: admin / admin123")

        # 2. Operator Org & Single Admin User (Decision 32)
        admin_org, _ = Organisation.objects.get_or_create(
            name="AnnaSutra Operations",
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
        self.stdout.write(self.style.SUCCESS("[OK] Pure production-ready environment initialized with ZERO sample data."))
