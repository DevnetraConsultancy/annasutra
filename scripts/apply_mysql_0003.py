import os
import pymysql
from urllib.parse import urlparse

# Read DATABASE_URL from .env.prod
db_url = None
if os.path.exists(".env.prod"):
    with open(".env.prod", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                db_url = line.strip().split("=", 1)[1].strip("'\"")
                break

if not db_url:
    print("No DATABASE_URL found in .env.prod")
    exit(1)

parsed = urlparse(db_url)
conn = pymysql.connect(
    host=parsed.hostname,
    port=parsed.port or 3306,
    user=parsed.username,
    password=parsed.password,
    database=parsed.path.lstrip("/"),
    ssl={"check_hostname": False},
)

with conn.cursor() as cur:
    print("Modifying entity_profile status ENUM...")
    cur.execute(
        "ALTER TABLE entity_profile MODIFY COLUMN status "
        "ENUM('DRAFT','SUBMITTED','NEEDS_CHANGES','VERIFIED','REJECTED','SUSPENDED','TRASH') "
        "NOT NULL DEFAULT 'DRAFT';"
    )
    print("Modifying verification_review decision ENUM...")
    cur.execute(
        "ALTER TABLE verification_review MODIFY COLUMN decision "
        "ENUM('APPROVED','REJECTED','NEEDS_CHANGES','SUSPENDED','TRASH','RESTORED') "
        "NOT NULL;"
    )
    print("Recording migration in django_migrations...")
    cur.execute(
        "INSERT IGNORE INTO django_migrations (app, name, applied) "
        "VALUES ('identity', '0003_add_trash_status', NOW());"
    )
    conn.commit()

conn.close()
print("Aiven MySQL migration 0003 applied successfully!")
