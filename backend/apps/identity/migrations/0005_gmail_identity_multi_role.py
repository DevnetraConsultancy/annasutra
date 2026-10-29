"""Migration 0005: Gmail Primary Identity, Optional Mobile & Multi-Role Registrations per Gmail.

Implements Decisions 29, 30, 31, 32, 35:
- app_user.email (unique, nullable for legacy fixtures, mandatory for Google Sign-In)
- app_user.phone_e164 (nullable, unique when present)
- entity_profile: unique on (user_id, role), phone_e164 nullable & non-unique across roles
"""

from django.db import migrations


def apply_gmail_multi_role_schema(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor

    with connection.cursor() as cursor:
        if vendor == "mysql":
            # 1. Add email column to app_user if not exists, make phone_e164 nullable
            try:
                cursor.execute("ALTER TABLE app_user ADD COLUMN email VARCHAR(190) NULL UNIQUE;")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE app_user MODIFY COLUMN phone_e164 VARCHAR(32) NULL;")
            except Exception:
                pass

            # 2. Update entity_profile: make phone_e164 nullable, entity_code VARCHAR(32), drop single-user unique
            try:
                cursor.execute("ALTER TABLE entity_profile MODIFY COLUMN phone_e164 VARCHAR(20) NULL;")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE entity_profile MODIFY COLUMN entity_code VARCHAR(32) NULL;")
            except Exception:
                pass

            # Drop legacy single-column UNIQUE indexes on entity_profile(user_id) and entity_profile(phone_e164)
            for idx_col in ("user_id", "phone_e164"):
                try:
                    cursor.execute(f"ALTER TABLE entity_profile DROP INDEX {idx_col};")
                except Exception:
                    pass

            # Add composite unique index (user_id, role)
            try:
                cursor.execute("ALTER TABLE entity_profile ADD UNIQUE KEY uq_user_role (user_id, role);")
            except Exception:
                pass
        else:
            # SQLite (test runner): recreate app_user and entity_profile cleanly with new constraints
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_user_new (
                  user_id     VARCHAR(36) PRIMARY KEY,
                  org_id      VARCHAR(36) NOT NULL,
                  email       VARCHAR(190) NULL UNIQUE,
                  phone_e164  VARCHAR(32) NULL UNIQUE,
                  role        VARCHAR(32) NOT NULL CHECK (role IN ('OWNER','STAFF','VIEWER','AGENT')),
                  status      VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','LOCKED','DISABLED')),
                  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (org_id) REFERENCES organisation(org_id)
                );
            """)
            try:
                cursor.execute("""
                    INSERT INTO app_user_new (user_id, org_id, phone_e164, role, status, created_at)
                    SELECT user_id, org_id, phone_e164, role, status, created_at FROM app_user;
                """)
            except Exception:
                pass
            cursor.execute("DROP TABLE IF EXISTS app_user;")
            cursor.execute("ALTER TABLE app_user_new RENAME TO app_user;")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entity_profile_new (
                  entity_id         CHAR(36) PRIMARY KEY,
                  user_id           CHAR(36) NOT NULL,
                  role              TEXT NOT NULL,
                  entity_code       VARCHAR(32) NULL UNIQUE,
                  first_name        VARCHAR(80) NOT NULL,
                  last_name         VARCHAR(80) NOT NULL,
                  organisation_name VARCHAR(160) NOT NULL,
                  gender            TEXT NOT NULL DEFAULT 'UNSPECIFIED',
                  phone_e164        VARCHAR(20) NULL,
                  email             VARCHAR(190) NULL,
                  total_land_acres  DECIMAL(10,3) NULL,
                  address_line1     VARCHAR(200) NOT NULL,
                  address_line2     VARCHAR(200) NULL,
                  village_town      VARCHAR(100) NOT NULL,
                  district          VARCHAR(100) NOT NULL,
                  state             VARCHAR(100) NOT NULL,
                  pincode           CHAR(6) NOT NULL,
                  photo_object_key  VARCHAR(255) NOT NULL,
                  status            TEXT NOT NULL DEFAULT 'DRAFT',
                  version           INT NOT NULL DEFAULT 1,
                  submitted_at      TIMESTAMP NULL,
                  verified_at       TIMESTAMP NULL,
                  verified_by       CHAR(36) NULL,
                  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  UNIQUE (user_id, role),
                  CONSTRAINT chk_land CHECK (total_land_acres IS NULL OR total_land_acres > 0),
                  CONSTRAINT chk_verified CHECK (status <> 'VERIFIED' OR entity_code IS NOT NULL)
                );
            """)
            try:
                cursor.execute("""
                    INSERT INTO entity_profile_new
                    SELECT * FROM entity_profile;
                """)
            except Exception:
                pass
            cursor.execute("DROP TABLE IF EXISTS entity_profile;")
            cursor.execute("ALTER TABLE entity_profile_new RENAME TO entity_profile;")
            cursor.execute("PRAGMA foreign_keys = ON;")


def reverse_gmail_multi_role_schema(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("identity", "0004_entity_deletion_request"),
    ]

    operations = [
        migrations.RunPython(
            code=apply_gmail_multi_role_schema,
            reverse_code=reverse_gmail_multi_role_schema,
        ),
    ]
