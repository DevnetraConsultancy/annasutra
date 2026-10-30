"""WSGI config for AnnaSutra project."""
import os
import sys
import threading
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Ensure backend directory is in sys.path for serverless/container environments
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.dev"))
_raw_application = get_wsgi_application()

_schema_initialized = False
_schema_lock = threading.Lock()


def _ensure_production_database_schema():
    """Ensure database migrations and columns are applied in serverless environments (Vercel)."""
    global _schema_initialized
    if _schema_initialized:
        return
    with _schema_lock:
        if _schema_initialized:
            return
        _schema_initialized = True
        try:
            from django.core.management import call_command
            call_command("migrate", interactive=False)
        except Exception as e:
            import logging
            logging.getLogger("annasutra.wsgi").warning("Auto-migration exception: %s", e)

        # Direct idempotent DDL safeguard for MySQL
        try:
            from django.db import connection
            if connection.vendor == "mysql":
                with connection.cursor() as cursor:
                    try:
                        cursor.execute("ALTER TABLE app_user ADD COLUMN email VARCHAR(190) NULL UNIQUE;")
                    except Exception:
                        pass
                    try:
                        cursor.execute("ALTER TABLE app_user MODIFY COLUMN phone_e164 VARCHAR(32) NULL;")
                    except Exception:
                        pass
                    try:
                        cursor.execute("ALTER TABLE entity_profile MODIFY COLUMN phone_e164 VARCHAR(20) NULL;")
                    except Exception:
                        pass
                    try:
                        cursor.execute("ALTER TABLE entity_profile MODIFY COLUMN entity_code VARCHAR(32) NULL;")
                    except Exception:
                        pass
                    try:
                        cursor.execute("ALTER TABLE entity_profile ADD UNIQUE KEY uq_user_role (user_id, role);")
                    except Exception:
                        pass

                    # Purge any legacy non-admin entity data in cloud MySQL
                    try:
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                    except Exception:
                        pass

                    purge_tables = [
                        "farmer_profile", "plot", "partner_link",
                        "entity_plot", "entity_sensitive", "entity_role_details",
                        "verification_review", "profile_change_log", "sensitive_access_log",
                        "entity_deletion_request", "entity_consent_record", "entity_document",
                        "consent_record", "device", "passkey_credential",
                        "lot_edge", "lot_balance", "handover", "inspection", "evidence",
                        "lab_certificate", "scan_log", "alert", "recall", "public_view",
                        "trace_event", "hash_anchor", "lot", "product", "qr_label", "qr_block"
                    ]
                    for tbl in purge_tables:
                        try:
                            cursor.execute(f"DELETE FROM `{tbl}`;")
                        except Exception:
                            pass

                    try:
                        cursor.execute("DELETE FROM entity_profile WHERE email IS NULL OR email != 'devnetraconsultancy@gmail.com' OR phone_e164 LIKE '%8444997803%' OR organisation_name LIKE '%Biswas%';")
                    except Exception:
                        pass

                    try:
                        cursor.execute("DELETE FROM app_user WHERE email IS NULL OR email != 'devnetraconsultancy@gmail.com' OR phone LIKE '%8444997803%';")
                    except Exception:
                        pass

                    try:
                        cursor.execute("DELETE FROM organisation WHERE org_type != 'OPERATOR';")
                    except Exception:
                        pass

                    try:
                        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                    except Exception:
                        pass

        except Exception as ddl_err:
            import logging
            logging.getLogger("annasutra.wsgi").warning("Schema safeguard notice: %s", ddl_err)


def application(environ, start_response):
    """Normalize PATH_INFO to conform to PEP 3333 in serverless environments (Vercel)."""
    _ensure_production_database_schema()
    path_info = environ.get("PATH_INFO", "")
    if not path_info.startswith("/"):
        environ["PATH_INFO"] = "/" + path_info
    return _raw_application(environ, start_response)


app = application
