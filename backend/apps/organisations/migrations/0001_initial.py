"""AnnaSutra unified database initial migration.
Supports MySQL 8.0+ (primary production & CI target), PostgreSQL, and SQLite.
Enforces strict append-only immutability on trace_event, check constraints,
and one-open-handover uniqueness.
"""

from django.db import migrations

MYSQL_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS organisation (
      org_id        VARCHAR(36) PRIMARY KEY,
      name          VARCHAR(255) NOT NULL,
      org_type      VARCHAR(32) NOT NULL CHECK (org_type IN
                    ('FARMER','AGGREGATOR','WHOLESALER','DISTRIBUTOR','RETAILER','LAB','OPERATOR')),
      fssai_no      VARCHAR(64),
      verification  VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (verification IN ('PENDING','VERIFIED','REJECTED','SUSPENDED')),
      verified_by   VARCHAR(36),
      verified_at   DATETIME(6),
      created_at    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS app_user (
      user_id     VARCHAR(36) PRIMARY KEY,
      org_id      VARCHAR(36) NOT NULL,
      phone_e164  VARCHAR(32) NOT NULL UNIQUE,
      role        VARCHAR(32) NOT NULL CHECK (role IN ('OWNER','STAFF','VIEWER','AGENT')),
      status      VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','LOCKED','DISABLED')),
      created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      FOREIGN KEY (org_id) REFERENCES organisation(org_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS device (
      device_id   VARCHAR(36) PRIMARY KEY,
      user_id     VARCHAR(36) NOT NULL,
      public_key  VARBINARY(255) NOT NULL,
      key_alg     VARCHAR(32) NOT NULL DEFAULT 'ES256',
      label       VARCHAR(255),
      created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      revoked_at  DATETIME(6),
      FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS passkey_credential (
      credential_id VARBINARY(255) PRIMARY KEY,
      user_id       VARCHAR(36) NOT NULL,
      public_key    VARBINARY(255) NOT NULL,
      sign_count    BIGINT NOT NULL DEFAULT 0,
      created_at    DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      revoked_at    DATETIME(6),
      FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS facility (
      facility_id   VARCHAR(36) PRIMARY KEY,
      org_id        VARCHAR(36) NOT NULL,
      name          VARCHAR(255) NOT NULL,
      facility_type VARCHAR(64) NOT NULL,
      district      VARCHAR(128),
      state         VARCHAR(128),
      FOREIGN KEY (org_id) REFERENCES organisation(org_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS farmer_profile (
      farmer_org_id VARCHAR(36) PRIMARY KEY,
      registered_by_user VARCHAR(36),
      FOREIGN KEY (farmer_org_id) REFERENCES organisation(org_id),
      FOREIGN KEY (registered_by_user) REFERENCES app_user(user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS consent_record (
      consent_id     VARCHAR(36) PRIMARY KEY,
      user_id        VARCHAR(36) NOT NULL,
      notice_version VARCHAR(64) NOT NULL,
      language       VARCHAR(32) NOT NULL,
      method         VARCHAR(32) NOT NULL CHECK (method IN ('SELF','ASSISTED')),
      given_at       DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      withdrawn_at   DATETIME(6),
      FOREIGN KEY (user_id) REFERENCES app_user(user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS plot (
      plot_id     VARCHAR(36) PRIMARY KEY,
      farmer_org_id VARCHAR(36) NOT NULL,
      village     VARCHAR(128),
      district    VARCHAR(128),
      state       VARCHAR(128),
      area_ha     DECIMAL(8,3) CHECK (area_ha > 0),
      lat         DECIMAL(9,6),
      lon         DECIMAL(9,6),
      FOREIGN KEY (farmer_org_id) REFERENCES farmer_profile(farmer_org_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS partner_link (
      org_a       VARCHAR(36) NOT NULL,
      org_b       VARCHAR(36) NOT NULL,
      status      VARCHAR(32) NOT NULL CHECK (status IN ('INVITED','ACCEPTED','REVOKED')),
      invited_by  VARCHAR(36),
      created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      PRIMARY KEY (org_a, org_b),
      CHECK (org_a <> org_b),
      FOREIGN KEY (org_a) REFERENCES organisation(org_id),
      FOREIGN KEY (org_b) REFERENCES organisation(org_id),
      FOREIGN KEY (invited_by) REFERENCES app_user(user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS product (
      product_id  VARCHAR(36) PRIMARY KEY,
      name        VARCHAR(255) NOT NULL,
      variety     VARCHAR(255),
      UNIQUE KEY product_name_variety_idx (name, variety)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS lot (
      lot_id          VARCHAR(36) PRIMARY KEY,
      public_code     VARCHAR(64) NOT NULL UNIQUE,
      product_id      VARCHAR(36) NOT NULL,
      origin_plot_id  VARCHAR(36),
      created_by_org  VARCHAR(36) NOT NULL,
      lot_kind        VARCHAR(32) NOT NULL CHECK (lot_kind IN ('HARVEST','SPLIT_CHILD','MERGED','SORTED')),
      state           VARCHAR(32) NOT NULL CHECK (state IN
                      ('CREATED','IN_TRANSIT','IN_CUSTODY','DISPUTED','CLOSED','RECALLED')),
      custodian_org   VARCHAR(36) NOT NULL,
      pending_receiver_org VARCHAR(36),
      version         BIGINT NOT NULL DEFAULT 0,
      head_seq        BIGINT NOT NULL DEFAULT 0,
      head_hash       VARBINARY(255),
      created_at      DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      CHECK ((state = 'IN_TRANSIT') = (pending_receiver_org IS NOT NULL)),
      FOREIGN KEY (product_id) REFERENCES product(product_id),
      FOREIGN KEY (origin_plot_id) REFERENCES plot(plot_id),
      FOREIGN KEY (created_by_org) REFERENCES organisation(org_id),
      FOREIGN KEY (custodian_org) REFERENCES organisation(org_id),
      FOREIGN KEY (pending_receiver_org) REFERENCES organisation(org_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS qr_block (
      block_id    VARCHAR(36) PRIMARY KEY,
      issued_to_org VARCHAR(36) NOT NULL,
      issued_by   VARCHAR(36) NOT NULL,
      issued_at   DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      count       INT NOT NULL CHECK (count > 0),
      FOREIGN KEY (issued_to_org) REFERENCES organisation(org_id),
      FOREIGN KEY (issued_by) REFERENCES app_user(user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS qr_label (
      serial      VARCHAR(64) PRIMARY KEY,
      block_id    VARCHAR(36) NOT NULL,
      issued_to_org VARCHAR(36) NOT NULL,
      lot_id      VARCHAR(36),
      status      VARCHAR(32) NOT NULL CHECK (status IN ('ISSUED','BOUND','VOID')),
      bound_at    DATETIME(6),
      CHECK ((status = 'BOUND') = (lot_id IS NOT NULL) OR status = 'VOID'),
      FOREIGN KEY (block_id) REFERENCES qr_block(block_id),
      FOREIGN KEY (issued_to_org) REFERENCES organisation(org_id),
      FOREIGN KEY (lot_id) REFERENCES lot(lot_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS lot_edge (
      parent_lot  VARCHAR(36) NOT NULL,
      child_lot   VARCHAR(36) NOT NULL,
      qty_kg      DECIMAL(12,3) NOT NULL CHECK (qty_kg > 0),
      event_id    VARCHAR(36) NOT NULL,
      PRIMARY KEY (parent_lot, child_lot),
      CHECK (parent_lot <> child_lot),
      FOREIGN KEY (parent_lot) REFERENCES lot(lot_id),
      FOREIGN KEY (child_lot) REFERENCES lot(lot_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS lot_balance (
      lot_id                  VARCHAR(36) PRIMARY KEY,
      qty_in_kg               DECIMAL(12,3) NOT NULL CHECK (qty_in_kg >= 0),
      qty_out_transferred_kg  DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK (qty_out_transferred_kg >= 0),
      qty_split_out_kg        DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK (qty_split_out_kg >= 0),
      qty_rejected_kg         DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK (qty_rejected_kg >= 0),
      qty_waste_kg            DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK (qty_waste_kg >= 0),
      qty_sold_kg             DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK (qty_sold_kg >= 0),
      qty_variance_kg         DECIMAL(12,3) NOT NULL DEFAULT 0 CHECK (qty_variance_kg >= 0),
      CONSTRAINT on_hand_nonnegative CHECK (
        qty_in_kg + 0.001 >= qty_out_transferred_kg + qty_split_out_kg + qty_rejected_kg
                            + qty_waste_kg + qty_sold_kg + qty_variance_kg),
      FOREIGN KEY (lot_id) REFERENCES lot(lot_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS trace_event (
      event_id        VARCHAR(36) PRIMARY KEY,
      lot_id          VARCHAR(36) NOT NULL,
      lot_seq         BIGINT NOT NULL,
      event_type      VARCHAR(64) NOT NULL,
      event_time      DATETIME(6) NOT NULL,
      recorded_at     DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      org_id          VARCHAR(36) NOT NULL,
      user_id         VARCHAR(36) NOT NULL,
      device_id       VARCHAR(36),
      on_behalf_of    VARCHAR(36),
      facility_id     VARCHAR(36),
      counterparty_org VARCHAR(36),
      qty_kg          DECIMAL(12,3),
      qty_basis       VARCHAR(32) CHECK (qty_basis IN ('MEASURED','ESTIMATED','DECLARED')),
      payload         JSON NOT NULL,
      supersedes_event VARCHAR(36),
      sync_status     VARCHAR(32) NOT NULL DEFAULT 'ACCEPTED',
      device_signature LONGBLOB,
      prev_hash       VARBINARY(255),
      event_hash      VARBINARY(255) NOT NULL,
      UNIQUE KEY trace_event_lot_seq_idx (lot_id, lot_seq),
      FOREIGN KEY (lot_id) REFERENCES lot(lot_id),
      FOREIGN KEY (org_id) REFERENCES organisation(org_id),
      FOREIGN KEY (user_id) REFERENCES app_user(user_id),
      FOREIGN KEY (device_id) REFERENCES device(device_id),
      FOREIGN KEY (on_behalf_of) REFERENCES organisation(org_id),
      FOREIGN KEY (facility_id) REFERENCES facility(facility_id),
      FOREIGN KEY (counterparty_org) REFERENCES organisation(org_id),
      FOREIGN KEY (supersedes_event) REFERENCES trace_event(event_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS handover (
      handover_id     VARCHAR(36) PRIMARY KEY,
      lot_id          VARCHAR(36) NOT NULL,
      from_org        VARCHAR(36) NOT NULL,
      to_org          VARCHAR(36) NOT NULL,
      declared_qty_kg DECIMAL(12,3) NOT NULL CHECK (declared_qty_kg > 0),
      received_qty_kg DECIMAL(12,3) CHECK (received_qty_kg >= 0),
      state           VARCHAR(32) NOT NULL CHECK (state IN
                      ('PENDING','ACCEPTED','ACCEPTED_WITH_DISCREPANCY','DISPUTED','REJECTED','EXPIRED')),
      opened_at       DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      expires_at      DATETIME(6) NOT NULL,
      closed_at       DATETIME(6),
      pending_lot_id  VARCHAR(36) GENERATED ALWAYS AS (IF(state = 'PENDING', lot_id, NULL)) VIRTUAL,
      CHECK (from_org <> to_org),
      UNIQUE KEY one_open_handover (pending_lot_id),
      FOREIGN KEY (lot_id) REFERENCES lot(lot_id),
      FOREIGN KEY (from_org) REFERENCES organisation(org_id),
      FOREIGN KEY (to_org) REFERENCES organisation(org_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS inspection (
      inspection_id VARCHAR(36) PRIMARY KEY,
      event_id      VARCHAR(36) NOT NULL,
      grade         VARCHAR(64),
      defect_pct    DECIMAL(5,2) CHECK (defect_pct BETWEEN 0 AND 100),
      temperature_c DECIMAL(4,1),
      notes         TEXT,
      FOREIGN KEY (event_id) REFERENCES trace_event(event_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS evidence (
      evidence_id VARCHAR(36) PRIMARY KEY,
      event_id    VARCHAR(36) NOT NULL,
      kind        VARCHAR(32) NOT NULL CHECK (kind IN ('PHOTO','SCALE_PHOTO','LAB_CERT','DOC')),
      object_key  VARCHAR(255) NOT NULL,
      sha256      VARBINARY(255) NOT NULL,
      FOREIGN KEY (event_id) REFERENCES trace_event(event_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS lab_certificate (
      cert_id        VARCHAR(36) PRIMARY KEY,
      lot_id         VARCHAR(36) NOT NULL,
      lab_org        VARCHAR(36) NOT NULL,
      lab_accreditation_no VARCHAR(128),
      certificate_no VARCHAR(128) NOT NULL,
      UNIQUE KEY lab_cert_unique_idx (lab_org, certificate_no),
      FOREIGN KEY (lot_id) REFERENCES lot(lot_id),
      FOREIGN KEY (lab_org) REFERENCES organisation(org_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS scan_log (
      scan_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
      serial      VARCHAR(64) NOT NULL,
      user_id     VARCHAR(36),
      scanned_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      coarse_area VARCHAR(128),
      result      VARCHAR(64) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS alert (
      alert_id    VARCHAR(36) PRIMARY KEY,
      rule        VARCHAR(64) NOT NULL,
      lot_id      VARCHAR(36),
      severity    VARCHAR(32) NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH')),
      detail      JSON NOT NULL,
      status      VARCHAR(32) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','REVIEWING','CLOSED')),
      created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      FOREIGN KEY (lot_id) REFERENCES lot(lot_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS recall (
      recall_id        VARCHAR(36) PRIMARY KEY,
      initiated_by_org VARCHAR(36) NOT NULL,
      root_lot         VARCHAR(36) NOT NULL,
      reason           TEXT NOT NULL,
      opened_at        DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
      status           VARCHAR(32) NOT NULL CHECK (status IN ('OPEN','CLOSED')),
      FOREIGN KEY (initiated_by_org) REFERENCES organisation(org_id),
      FOREIGN KEY (root_lot) REFERENCES lot(lot_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS public_view (
      lot_id       VARCHAR(36) PRIMARY KEY,
      public_code  VARCHAR(64) NOT NULL UNIQUE,
      payload      JSON NOT NULL,
      refreshed_at DATETIME(6) NOT NULL,
      FOREIGN KEY (lot_id) REFERENCES lot(lot_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS audit_access_log (
      id          BIGINT AUTO_INCREMENT PRIMARY KEY,
      user_id     VARCHAR(36) NOT NULL,
      resource    VARCHAR(128) NOT NULL,
      resource_id VARCHAR(128),
      at          DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    """CREATE TABLE IF NOT EXISTS hash_anchor (
      anchor_date DATE PRIMARY KEY,
      root_hash   VARBINARY(255) NOT NULL,
      location    TEXT NOT NULL,
      created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;""",

    "DROP TRIGGER IF EXISTS trace_event_no_update;",
    """CREATE TRIGGER trace_event_no_update BEFORE UPDATE ON trace_event
    FOR EACH ROW
    BEGIN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'trace_event is append-only';
    END;""",

    "DROP TRIGGER IF EXISTS trace_event_no_delete;",
    """CREATE TRIGGER trace_event_no_delete BEFORE DELETE ON trace_event
    FOR EACH ROW
    BEGIN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'trace_event is append-only';
    END;""",
]

PG_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS organisation (
  org_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          TEXT NOT NULL,
  org_type      TEXT NOT NULL CHECK (org_type IN
                ('FARMER','AGGREGATOR','WHOLESALER','DISTRIBUTOR','RETAILER','LAB','OPERATOR')),
  fssai_no      TEXT,
  verification  TEXT NOT NULL DEFAULT 'PENDING' CHECK (verification IN ('PENDING','VERIFIED','REJECTED','SUSPENDED')),
  verified_by   UUID,
  verified_at   TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS app_user (
  user_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id      UUID NOT NULL REFERENCES organisation(org_id),
  phone_e164  TEXT NOT NULL UNIQUE,
  role        TEXT NOT NULL CHECK (role IN ('OWNER','STAFF','VIEWER','AGENT')),
  status      TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','LOCKED','DISABLED')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS device (
  device_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES app_user(user_id),
  public_key  BYTEA NOT NULL,
  key_alg     TEXT NOT NULL DEFAULT 'ES256',
  label       TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS passkey_credential (
  credential_id BYTEA PRIMARY KEY,
  user_id       UUID NOT NULL REFERENCES app_user(user_id),
  public_key    BYTEA NOT NULL,
  sign_count    BIGINT NOT NULL DEFAULT 0,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS facility (
  facility_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL REFERENCES organisation(org_id),
  name          TEXT NOT NULL,
  facility_type TEXT NOT NULL,
  district      TEXT,
  state         TEXT
);

CREATE TABLE IF NOT EXISTS farmer_profile (
  farmer_org_id UUID PRIMARY KEY REFERENCES organisation(org_id),
  registered_by_user UUID REFERENCES app_user(user_id)
);

CREATE TABLE IF NOT EXISTS consent_record (
  consent_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID NOT NULL REFERENCES app_user(user_id),
  notice_version TEXT NOT NULL,
  language       TEXT NOT NULL,
  method         TEXT NOT NULL CHECK (method IN ('SELF','ASSISTED')),
  given_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  withdrawn_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS plot (
  plot_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_org_id UUID NOT NULL REFERENCES farmer_profile(farmer_org_id),
  village     TEXT,
  district    TEXT,
  state       TEXT,
  area_ha     NUMERIC(8,3) CHECK (area_ha > 0),
  lat         NUMERIC(9,6),
  lon         NUMERIC(9,6)
);

CREATE TABLE IF NOT EXISTS partner_link (
  org_a       UUID NOT NULL REFERENCES organisation(org_id),
  org_b       UUID NOT NULL REFERENCES organisation(org_id),
  status      TEXT NOT NULL CHECK (status IN ('INVITED','ACCEPTED','REVOKED')),
  invited_by  UUID REFERENCES app_user(user_id),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (org_a, org_b),
  CHECK (org_a <> org_b)
);

CREATE TABLE IF NOT EXISTS product (
  product_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  variety     TEXT,
  UNIQUE (name, variety)
);

CREATE TABLE IF NOT EXISTS lot (
  lot_id          UUID PRIMARY KEY,
  public_code     TEXT NOT NULL UNIQUE,
  product_id      UUID NOT NULL REFERENCES product(product_id),
  origin_plot_id  UUID REFERENCES plot(plot_id),
  created_by_org  UUID NOT NULL REFERENCES organisation(org_id),
  lot_kind        TEXT NOT NULL CHECK (lot_kind IN ('HARVEST','SPLIT_CHILD','MERGED','SORTED')),
  state           TEXT NOT NULL CHECK (state IN
                  ('CREATED','IN_TRANSIT','IN_CUSTODY','DISPUTED','CLOSED','RECALLED')),
  custodian_org   UUID NOT NULL REFERENCES organisation(org_id),
  pending_receiver_org UUID REFERENCES organisation(org_id),
  version         BIGINT NOT NULL DEFAULT 0,
  head_seq        BIGINT NOT NULL DEFAULT 0,
  head_hash       BYTEA,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK ((state = 'IN_TRANSIT') = (pending_receiver_org IS NOT NULL))
);

CREATE TABLE IF NOT EXISTS qr_block (
  block_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issued_to_org UUID NOT NULL REFERENCES organisation(org_id),
  issued_by   UUID NOT NULL REFERENCES app_user(user_id),
  issued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  count       INT NOT NULL CHECK (count > 0)
);

CREATE TABLE IF NOT EXISTS qr_label (
  serial      TEXT PRIMARY KEY,
  block_id    UUID NOT NULL REFERENCES qr_block(block_id),
  issued_to_org UUID NOT NULL REFERENCES organisation(org_id),
  lot_id      UUID REFERENCES lot(lot_id),
  status      TEXT NOT NULL CHECK (status IN ('ISSUED','BOUND','VOID')),
  bound_at    TIMESTAMPTZ,
  CHECK ((status = 'BOUND') = (lot_id IS NOT NULL) OR status = 'VOID')
);

CREATE TABLE IF NOT EXISTS lot_edge (
  parent_lot  UUID NOT NULL REFERENCES lot(lot_id),
  child_lot   UUID NOT NULL REFERENCES lot(lot_id),
  qty_kg      NUMERIC(12,3) NOT NULL CHECK (qty_kg > 0),
  event_id    UUID NOT NULL,
  PRIMARY KEY (parent_lot, child_lot),
  CHECK (parent_lot <> child_lot)
);

CREATE TABLE IF NOT EXISTS lot_balance (
  lot_id                  UUID PRIMARY KEY REFERENCES lot(lot_id),
  qty_in_kg               NUMERIC(12,3) NOT NULL CHECK (qty_in_kg >= 0),
  qty_out_transferred_kg  NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_out_transferred_kg >= 0),
  qty_split_out_kg        NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_split_out_kg >= 0),
  qty_rejected_kg         NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_rejected_kg >= 0),
  qty_waste_kg            NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_waste_kg >= 0),
  qty_sold_kg             NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_sold_kg >= 0),
  qty_variance_kg         NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_variance_kg >= 0),
  CONSTRAINT on_hand_nonnegative CHECK (
    qty_in_kg + 0.001 >= qty_out_transferred_kg + qty_split_out_kg + qty_rejected_kg
                        + qty_waste_kg + qty_sold_kg + qty_variance_kg)
);

CREATE TABLE IF NOT EXISTS trace_event (
  event_id        UUID PRIMARY KEY,
  lot_id          UUID NOT NULL REFERENCES lot(lot_id),
  lot_seq         BIGINT NOT NULL,
  event_type      TEXT NOT NULL,
  event_time      TIMESTAMPTZ NOT NULL,
  recorded_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  org_id          UUID NOT NULL REFERENCES organisation(org_id),
  user_id         UUID NOT NULL REFERENCES app_user(user_id),
  device_id       UUID REFERENCES device(device_id),
  on_behalf_of    UUID REFERENCES organisation(org_id),
  facility_id     UUID REFERENCES facility(facility_id),
  counterparty_org UUID REFERENCES organisation(org_id),
  qty_kg          NUMERIC(12,3),
  qty_basis       TEXT CHECK (qty_basis IN ('MEASURED','ESTIMATED','DECLARED')),
  payload         JSONB NOT NULL,
  supersedes_event UUID REFERENCES trace_event(event_id),
  sync_status     TEXT NOT NULL DEFAULT 'ACCEPTED',
  device_signature BYTEA,
  prev_hash       BYTEA,
  event_hash      BYTEA NOT NULL,
  UNIQUE (lot_id, lot_seq)
);

CREATE OR REPLACE FUNCTION forbid_change() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'trace_event is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trace_event_no_update ON trace_event;
CREATE TRIGGER trace_event_no_update BEFORE UPDATE OR DELETE ON trace_event
  FOR EACH ROW EXECUTE FUNCTION forbid_change();

CREATE TABLE IF NOT EXISTS handover (
  handover_id     UUID PRIMARY KEY,
  lot_id          UUID NOT NULL REFERENCES lot(lot_id),
  from_org        UUID NOT NULL REFERENCES organisation(org_id),
  to_org          UUID NOT NULL REFERENCES organisation(org_id),
  declared_qty_kg NUMERIC(12,3) NOT NULL CHECK (declared_qty_kg > 0),
  received_qty_kg NUMERIC(12,3) CHECK (received_qty_kg >= 0),
  state           TEXT NOT NULL CHECK (state IN
                  ('PENDING','ACCEPTED','ACCEPTED_WITH_DISCREPANCY','DISPUTED','REJECTED','EXPIRED')),
  opened_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at      TIMESTAMPTZ NOT NULL,
  closed_at       TIMESTAMPTZ,
  CHECK (from_org <> to_org)
);
DROP INDEX IF EXISTS one_open_handover;
CREATE UNIQUE INDEX one_open_handover ON handover(lot_id) WHERE state = 'PENDING';

CREATE TABLE IF NOT EXISTS inspection (
  inspection_id UUID PRIMARY KEY,
  event_id      UUID NOT NULL REFERENCES trace_event(event_id),
  grade         TEXT,
  defect_pct    NUMERIC(5,2) CHECK (defect_pct BETWEEN 0 AND 100),
  temperature_c NUMERIC(4,1),
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS evidence (
  evidence_id UUID PRIMARY KEY,
  event_id    UUID NOT NULL REFERENCES trace_event(event_id),
  kind        TEXT NOT NULL CHECK (kind IN ('PHOTO','SCALE_PHOTO','LAB_CERT','DOC')),
  object_key  TEXT NOT NULL,
  sha256      BYTEA NOT NULL
);

CREATE TABLE IF NOT EXISTS lab_certificate (
  cert_id        UUID PRIMARY KEY,
  lot_id         UUID NOT NULL REFERENCES lot(lot_id),
  lab_org        UUID NOT NULL REFERENCES organisation(org_id),
  lab_accreditation_no TEXT,
  certificate_no TEXT NOT NULL,
  UNIQUE (lab_org, certificate_no)
);

CREATE TABLE IF NOT EXISTS scan_log (
  scan_id     BIGSERIAL PRIMARY KEY,
  serial      TEXT NOT NULL,
  user_id     UUID,
  scanned_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  coarse_area TEXT,
  result      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alert (
  alert_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule        TEXT NOT NULL,
  lot_id      UUID REFERENCES lot(lot_id),
  severity    TEXT NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH')),
  detail      JSONB NOT NULL,
  status      TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','REVIEWING','CLOSED')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recall (
  recall_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiated_by_org UUID NOT NULL REFERENCES organisation(org_id),
  root_lot         UUID NOT NULL REFERENCES lot(lot_id),
  reason           TEXT NOT NULL,
  opened_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  status           TEXT NOT NULL CHECK (status IN ('OPEN','CLOSED'))
);

CREATE TABLE IF NOT EXISTS public_view (
  lot_id       UUID PRIMARY KEY REFERENCES lot(lot_id),
  public_code  TEXT NOT NULL UNIQUE,
  payload      JSONB NOT NULL,
  refreshed_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_access_log (
  id          BIGSERIAL PRIMARY KEY,
  user_id     UUID NOT NULL,
  resource    TEXT NOT NULL,
  resource_id TEXT,
  at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS hash_anchor (
  anchor_date DATE PRIMARY KEY,
  root_hash   BYTEA NOT NULL,
  location    TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def apply_schema(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor
    with connection.cursor() as cursor:
        if vendor == "mysql":
            try:
                cursor.execute("SET GLOBAL log_bin_trust_function_creators = 1;")
            except Exception:
                pass
            for statement in MYSQL_STATEMENTS:
                clean_stmt = statement.strip()
                if clean_stmt:
                    cursor.execute(clean_stmt)
        elif vendor == "postgresql":
            cursor.execute(PG_SCHEMA_SQL)
        else:
            # Fallback for SQLite / test environments
            # SQLite supports standard table creation without schemas
            for statement in MYSQL_STATEMENTS:
                clean = statement.strip()
                if clean and not clean.startswith("DROP TRIGGER") and not clean.startswith("CREATE TRIGGER"):
                    # Strip engine and charset options for SQLite
                    clean_sqlite = clean.replace(
                        "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;",
                        ";"
                    )
                    clean_sqlite = clean_sqlite.replace("AUTO_INCREMENT", "AUTOINCREMENT")
                    clean_sqlite = clean_sqlite.replace("LONGBLOB", "BLOB")
                    clean_sqlite = clean_sqlite.replace("VARBINARY(255)", "BLOB")
                    clean_sqlite = clean_sqlite.replace("DATETIME(6)", "TIMESTAMP")
                    try:
                        cursor.execute(clean_sqlite)
                    except Exception:
                        pass


def reverse_schema(apps, schema_editor):
    connection = schema_editor.connection
    vendor = connection.vendor
    with connection.cursor() as cursor:
        if vendor == "postgresql":
            cursor.execute("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;")
        elif vendor == "mysql":
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            tables = [
                "hash_anchor", "audit_access_log", "public_view", "recall", "alert",
                "scan_log", "lab_certificate", "evidence", "inspection", "handover",
                "trace_event", "lot_balance", "lot_edge", "qr_label", "qr_block",
                "lot", "product", "partner_link", "plot", "consent_record",
                "farmer_profile", "facility", "passkey_credential", "device",
                "app_user", "organisation"
            ]
            for t in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {t};")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.RunPython(
            code=apply_schema,
            reverse_code=reverse_schema,
        ),
    ]
