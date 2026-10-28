import uuid
from django.db import models
from django.utils import timezone


class Organisation(models.Model):
    ORG_TYPE_CHOICES = [
        ("FARMER", "Farmer"),
        ("AGGREGATOR", "Aggregator"),
        ("PROCESSOR", "Processor"),
        ("WHOLESALER", "Wholesaler"),
        ("DISTRIBUTOR", "Distributor"),
        ("RETAILER", "Retailer"),
        ("LAB", "Lab"),
        ("OPERATOR", "Operator"),
    ]
    VERIFICATION_CHOICES = [
        ("PENDING", "Pending"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
        ("SUSPENDED", "Suspended"),
    ]

    org_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    org_type = models.TextField(choices=ORG_TYPE_CHOICES)
    fssai_no = models.TextField(null=True, blank=True)
    verification = models.TextField(choices=VERIFICATION_CHOICES, default="PENDING")
    verified_by = models.UUIDField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "organisation"


class Facility(models.Model):
    facility_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="facilities", db_column="org_id")
    name = models.TextField()
    facility_type = models.TextField()
    district = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "facility"


class FarmerProfile(models.Model):
    farmer_org = models.OneToOneField(Organisation, primary_key=True, on_delete=models.CASCADE, related_name="farmer_profile", db_column="farmer_org_id")
    registered_by_user = models.ForeignKey("identity.AppUser", null=True, blank=True, on_delete=models.SET_NULL, related_name="registered_farmers", db_column="registered_by_user")

    class Meta:
        db_table = "farmer_profile"


class Plot(models.Model):
    plot_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer_org = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name="plots", db_column="farmer_org_id")
    village = models.TextField(null=True, blank=True)
    district = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    area_ha = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = "plot"


class PartnerLink(models.Model):
    STATUS_CHOICES = [
        ("INVITED", "Invited"),
        ("ACCEPTED", "Accepted"),
        ("REVOKED", "Revoked"),
    ]

    org_a = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="partner_links_a", db_column="org_a", primary_key=True)
    org_b = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="partner_links_b", db_column="org_b")
    status = models.TextField(choices=STATUS_CHOICES)
    invited_by = models.ForeignKey("identity.AppUser", null=True, blank=True, on_delete=models.SET_NULL, related_name="partner_invitations", db_column="invited_by")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "partner_link"
        unique_together = (("org_a", "org_b"),)
