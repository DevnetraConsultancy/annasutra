"""Migration 0003: Add TRASH status to entity_profile and verification_review.

Allows soft-deletion to Admin Trash and restoration of entity profiles.
"""

from django.db import migrations


def alter_mysql_enums(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor == "mysql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                "ALTER TABLE entity_profile MODIFY COLUMN status "
                "ENUM('DRAFT','SUBMITTED','NEEDS_CHANGES','VERIFIED','REJECTED','SUSPENDED','TRASH') "
                "NOT NULL DEFAULT 'DRAFT';"
            )
            cursor.execute(
                "ALTER TABLE verification_review MODIFY COLUMN decision "
                "ENUM('APPROVED','REJECTED','NEEDS_CHANGES','SUSPENDED','TRASH','RESTORED') "
                "NOT NULL;"
            )


def reverse_mysql_enums(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("identity", "0002_registration_schema"),
    ]

    operations = [
        migrations.RunPython(alter_mysql_enums, reverse_mysql_enums),
    ]
