-- AnnaSutra PostgreSQL schema (version 1 draft).
-- The agent must adapt this through Django migrations, keeping every constraint.
-- Quantities are kilograms. All timestamps are timestamptz (UTC).

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE organisation (
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

CREATE TABLE app_user (
  user_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id      UUID NOT NULL REFERENCES organisation(org_id),
  phone_e164  TEXT NOT NULL UNIQUE,            -- field-level encrypted in the app layer
  role        TEXT NOT NULL CHECK (role IN ('OWNER','STAFF','VIEWER','AGENT')),
  status      TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','LOCKED','DISABLED')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE device (
  device_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES app_user(user_id),
  public_key  BYTEA NOT NULL,                  -- from Android Keystore or iOS Secure Enclave
  key_alg     TEXT NOT NULL DEFAULT 'ES256',
  label       TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at  TIMESTAMPTZ
);

CREATE TABLE passkey_credential (
  credential_id BYTEA PRIMARY KEY,
  user_id       UUID NOT NULL REFERENCES app_user(user_id),
  public_key    BYTEA NOT NULL,
  sign_count    BIGINT NOT NULL DEFAULT 0,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at    TIMESTAMPTZ
);

CREATE TABLE facility (
  facility_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id        UUID NOT NULL REFERENCES organisation(org_id),
  name          TEXT NOT NULL,
  facility_type TEXT NOT NULL,
  district      TEXT,
  state         TEXT
);

CREATE TABLE farmer_profile (
  farmer_org_id UUID PRIMARY KEY REFERENCES organisation(org_id),
  registered_by_user UUID REFERENCES app_user(user_id)   -- assisted registration
);

CREATE TABLE consent_record (
  consent_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID NOT NULL REFERENCES app_user(user_id),
  notice_version TEXT NOT NULL,
  language       TEXT NOT NULL,
  method         TEXT NOT NULL CHECK (method IN ('SELF','ASSISTED')),
  given_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  withdrawn_at   TIMESTAMPTZ
);

CREATE TABLE plot (
  plot_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  farmer_org_id UUID NOT NULL REFERENCES farmer_profile(farmer_org_id),
  village     TEXT,
  district    TEXT,
  state       TEXT,
  area_ha     NUMERIC(8,3) CHECK (area_ha > 0),
  lat         NUMERIC(9,6),                    -- restricted, encrypted, never public
  lon         NUMERIC(9,6)
);

CREATE TABLE partner_link (
  org_a       UUID NOT NULL REFERENCES organisation(org_id),
  org_b       UUID NOT NULL REFERENCES organisation(org_id),
  status      TEXT NOT NULL CHECK (status IN ('INVITED','ACCEPTED','REVOKED')),
  invited_by  UUID REFERENCES app_user(user_id),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (org_a, org_b),
  CHECK (org_a <> org_b)
);

CREATE TABLE product (
  product_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  variety     TEXT,
  UNIQUE (name, variety)
);

CREATE TABLE lot (
  lot_id          UUID PRIMARY KEY,                     -- client-made UUIDv7 allowed
  public_code     TEXT NOT NULL UNIQUE,                 -- 12 base32 chars + check char
  product_id      UUID NOT NULL REFERENCES product(product_id),
  origin_plot_id  UUID REFERENCES plot(plot_id),        -- NULL for merged lots
  created_by_org  UUID NOT NULL REFERENCES organisation(org_id),
  lot_kind        TEXT NOT NULL CHECK (lot_kind IN ('HARVEST','SPLIT_CHILD','MERGED','SORTED')),
  state           TEXT NOT NULL CHECK (state IN
                  ('CREATED','IN_TRANSIT','IN_CUSTODY','DISPUTED','CLOSED','RECALLED')),
  custodian_org   UUID NOT NULL REFERENCES organisation(org_id),
  pending_receiver_org UUID REFERENCES organisation(org_id),
  version         BIGINT NOT NULL DEFAULT 0,            -- optimistic concurrency
  head_seq        BIGINT NOT NULL DEFAULT 0,
  head_hash       BYTEA,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK ((state = 'IN_TRANSIT') = (pending_receiver_org IS NOT NULL))
);

CREATE TABLE qr_block (
  block_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  issued_to_org UUID NOT NULL REFERENCES organisation(org_id),
  issued_by   UUID NOT NULL REFERENCES app_user(user_id),
  issued_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  count       INT NOT NULL CHECK (count > 0)
);

CREATE TABLE qr_label (
  serial      TEXT PRIMARY KEY,                         -- printed code, unguessable
  block_id    UUID NOT NULL REFERENCES qr_block(block_id),
  issued_to_org UUID NOT NULL REFERENCES organisation(org_id),
  lot_id      UUID REFERENCES lot(lot_id),
  status      TEXT NOT NULL CHECK (status IN ('ISSUED','BOUND','VOID')),
  bound_at    TIMESTAMPTZ,
  CHECK ((status = 'BOUND') = (lot_id IS NOT NULL) OR status = 'VOID')
);

CREATE TABLE lot_edge (                                 -- genealogy
  parent_lot  UUID NOT NULL REFERENCES lot(lot_id),
  child_lot   UUID NOT NULL REFERENCES lot(lot_id),
  qty_kg      NUMERIC(12,3) NOT NULL CHECK (qty_kg > 0),
  event_id    UUID NOT NULL,
  PRIMARY KEY (parent_lot, child_lot),
  CHECK (parent_lot <> child_lot)
);

CREATE TABLE lot_balance (
  lot_id                  UUID PRIMARY KEY REFERENCES lot(lot_id),
  qty_in_kg               NUMERIC(12,3) NOT NULL CHECK (qty_in_kg >= 0),
  qty_out_transferred_kg  NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_out_transferred_kg >= 0),
  qty_split_out_kg        NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_split_out_kg >= 0),
  qty_rejected_kg         NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_rejected_kg >= 0),
  qty_waste_kg            NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_waste_kg >= 0),
  qty_sold_kg             NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_sold_kg >= 0),
  qty_variance_kg         NUMERIC(12,3) NOT NULL DEFAULT 0 CHECK (qty_variance_kg >= 0),
  -- on-hand must never be negative (small tolerance for rounding)
  CONSTRAINT on_hand_nonnegative CHECK (
    qty_in_kg + 0.001 >= qty_out_transferred_kg + qty_split_out_kg + qty_rejected_kg
                        + qty_waste_kg + qty_sold_kg + qty_variance_kg)
);

CREATE TABLE trace_event (                              -- APPEND ONLY
  event_id        UUID PRIMARY KEY,                     -- client-made UUIDv7
  lot_id          UUID NOT NULL REFERENCES lot(lot_id),
  lot_seq         BIGINT NOT NULL,
  event_type      TEXT NOT NULL,
  event_time      TIMESTAMPTZ NOT NULL,                 -- device claim
  recorded_at     TIMESTAMPTZ NOT NULL DEFAULT now(),   -- server truth
  org_id          UUID NOT NULL REFERENCES organisation(org_id),
  user_id         UUID NOT NULL REFERENCES app_user(user_id),
  device_id       UUID REFERENCES device(device_id),
  on_behalf_of    UUID REFERENCES organisation(org_id), -- agent acting for a farmer
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

-- Make trace_event append-only. Run as the schema owner. The app role gets INSERT and SELECT only.
CREATE OR REPLACE FUNCTION forbid_change() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'trace_event is append-only';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trace_event_no_update BEFORE UPDATE OR DELETE ON trace_event
  FOR EACH ROW EXECUTE FUNCTION forbid_change();
CREATE TRIGGER trace_event_no_truncate BEFORE TRUNCATE ON trace_event
  FOR EACH STATEMENT EXECUTE FUNCTION forbid_change();

CREATE TABLE handover (
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
CREATE UNIQUE INDEX one_open_handover ON handover(lot_id) WHERE state = 'PENDING';

CREATE TABLE inspection (
  inspection_id UUID PRIMARY KEY,
  event_id      UUID NOT NULL REFERENCES trace_event(event_id),
  grade         TEXT,
  defect_pct    NUMERIC(5,2) CHECK (defect_pct BETWEEN 0 AND 100),
  temperature_c NUMERIC(4,1),
  notes         TEXT
);

CREATE TABLE evidence (
  evidence_id UUID PRIMARY KEY,
  event_id    UUID NOT NULL REFERENCES trace_event(event_id),
  kind        TEXT NOT NULL CHECK (kind IN ('PHOTO','SCALE_PHOTO','LAB_CERT','DOC')),
  object_key  TEXT NOT NULL,
  sha256      BYTEA NOT NULL
);

CREATE TABLE lab_certificate (
  cert_id        UUID PRIMARY KEY,
  lot_id         UUID NOT NULL REFERENCES lot(lot_id),
  lab_org        UUID NOT NULL REFERENCES organisation(org_id),
  lab_accreditation_no TEXT,
  certificate_no TEXT NOT NULL,
  UNIQUE (lab_org, certificate_no)
);

CREATE TABLE scan_log (
  scan_id     BIGSERIAL PRIMARY KEY,
  serial      TEXT NOT NULL,
  user_id     UUID,
  scanned_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  coarse_area TEXT,
  result      TEXT NOT NULL
);

CREATE TABLE alert (
  alert_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rule        TEXT NOT NULL,
  lot_id      UUID REFERENCES lot(lot_id),
  severity    TEXT NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH')),
  detail      JSONB NOT NULL,
  status      TEXT NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN','REVIEWING','CLOSED')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recall (
  recall_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiated_by_org UUID NOT NULL REFERENCES organisation(org_id),
  root_lot         UUID NOT NULL REFERENCES lot(lot_id),
  reason           TEXT NOT NULL,
  opened_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  status           TEXT NOT NULL CHECK (status IN ('OPEN','CLOSED'))
);

CREATE TABLE public_view (                              -- the ONLY table the public page can read
  lot_id       UUID PRIMARY KEY REFERENCES lot(lot_id),
  public_code  TEXT NOT NULL UNIQUE,
  payload      JSONB NOT NULL,
  refreshed_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE audit_access_log (
  id          BIGSERIAL PRIMARY KEY,
  user_id     UUID NOT NULL,
  resource    TEXT NOT NULL,
  resource_id TEXT,
  at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE hash_anchor (                              -- record of daily external anchoring
  anchor_date DATE PRIMARY KEY,
  root_hash   BYTEA NOT NULL,
  location    TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Row-level security example. Repeat for every table that holds organisation data.
-- The application sets:  SET LOCAL app.org_id = '<caller org uuid>'  at the start of each request.
ALTER TABLE lot ENABLE ROW LEVEL SECURITY;
CREATE POLICY lot_org_scope ON lot
  USING (custodian_org = current_setting('app.org_id', true)::uuid
      OR pending_receiver_org = current_setting('app.org_id', true)::uuid
      OR created_by_org = current_setting('app.org_id', true)::uuid);

-- Roles (create in migrations, never reuse the owner role for the app):
--   app_rw      : SELECT/INSERT on most tables, UPDATE only on lot, lot_balance, handover, qr_label, alert, organisation
--   public_ro   : SELECT on public_view ONLY
--   auditor_ro  : SELECT on events and logs, access logged
-- REVOKE UPDATE, DELETE, TRUNCATE ON trace_event FROM PUBLIC, app_rw;
