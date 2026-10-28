"""Migration 0004: Add entity_deletion_request table and update status enums."""

from django.db import migrations

MYSQL_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS entity_deletion_request (
      request_id           CHAR(36) PRIMARY KEY,
      entity_id            CHAR(36) NOT NULL,
      requested_by_user_id CHAR(36) NOT NULL,
      reason               VARCHAR(40) NOT NULL,
      remarks              TEXT NULL,
      status               VARCHAR(20) NOT NULL DEFAULT 'PENDING',
      admin_remarks        TEXT NULL,
      reviewed_by          CHAR(36) NULL,
      reviewed_at          DATETIME NULL,
      created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      CONSTRAINT fk_del_req_entity FOREIGN KEY (entity_id) REFERENCES entity_profile(entity_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
]

SQLITE_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS entity_deletion_request (
      request_id           CHAR(36) PRIMARY KEY,
      entity_id            CHAR(36) NOT NULL,
      requested_by_user_id CHAR(36) NOT NULL,
      reason               VARCHAR(40) NOT NULL,
      remarks              TEXT NULL,
      status               VARCHAR(20) NOT NULL DEFAULT 'PENDING',
      admin_remarks        TEXT NULL,
      reviewed_by          CHAR(36) NULL,
      reviewed_at          TIMESTAMP NULL,
      created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (entity_id) REFERENCES entity_profile(entity_id) ON DELETE CASCADE
    );"""
]


def apply_deletion_request_schema(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor

    with connection.cursor() as cursor:
        if vendor == "mysql":
            for stmt in MYSQL_STATEMENTS:
                cursor.execute(stmt)
            cursor.execute(
                "ALTER TABLE entity_profile MODIFY COLUMN status "
                "ENUM('DRAFT','SUBMITTED','NEEDS_CHANGES','VERIFIED','REJECTED','SUSPENDED','TRASH','DELETION_REQUESTED','DEACTIVATED') "
                "NOT NULL DEFAULT 'DRAFT';"
            )
            cursor.execute(
                "ALTER TABLE verification_review MODIFY COLUMN decision "
                "ENUM('APPROVED','REJECTED','NEEDS_CHANGES','SUSPENDED','TRASH','RESTORED','DELETION_REQUESTED','DEACTIVATED') "
                "NOT NULL;"
            )
        else:
            for stmt in SQLITE_STATEMENTS:
                cursor.execute(stmt)


def reverse_deletion_request_schema(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS entity_deletion_request;")


class Migration(migrations.Migration):

    dependencies = [
        ("identity", "0003_add_trash_status"),
    ]

    operations = [
        migrations.RunPython(
            code=apply_deletion_request_schema,
            reverse_code=reverse_deletion_request_schema,
        ),
    ]
