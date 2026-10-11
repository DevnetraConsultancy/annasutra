#!/usr/bin/env python3
"""Generates api/openapi.yaml. Edit OPS and SCHEMAS, rerun, validate with openapi-spec-validator."""
import os, yaml

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api", "openapi.yaml")

S = lambda n: {"$ref": f"#/components/schemas/{n}"}
obj = lambda props, req=None: {"type": "object", "properties": props, **({"required": req} if req else {})}
st = {"type": "string"}
uid = {"type": "string", "format": "uuid"}
num = {"type": "number"}
dt = {"type": "string", "format": "date-time"}

SCHEMAS = {
    "Problem": obj({"type": st, "title": st, "status": {"type": "integer"}, "detail": st, "code": st}, ["title", "status", "code"]),
    "OtpRequest": obj({"phone": st, "language": st}, ["phone"]),
    "OtpVerify": obj({"phone": st, "code": st, "device_public_key": st, "device_label": st}, ["phone", "code"]),
    "TokenPair": obj({"access_token": st, "refresh_token": st, "expires_in": {"type": "integer"}, "org_verification": st}, ["access_token", "refresh_token"]),
    "RefreshRequest": obj({"refresh_token": st}, ["refresh_token"]),
    "WebAuthnOptions": obj({"options": {"type": "object"}}),
    "WebAuthnResult": obj({"credential": {"type": "object"}}, ["credential"]),
    "DeviceRegister": obj({"public_key": st, "key_alg": st, "label": st}, ["public_key"]),
    "Device": obj({"device_id": uid, "label": st, "created_at": dt, "revoked_at": dt}),
    "OrgRegister": obj({"name": st, "org_type": {"type": "string", "enum": ["FARMER", "AGGREGATOR", "WHOLESALER", "DISTRIBUTOR", "RETAILER"]}, "fssai_no": st, "consent_notice_version": st, "consent_language": st}, ["name", "org_type", "consent_notice_version"]),
    "Org": obj({"org_id": uid, "name": st, "org_type": st, "verification": st}),
    "PartnerInvite": obj({"to_org_id": uid}, ["to_org_id"]),
    "Partner": obj({"org_id": uid, "name": st, "status": st}),
    "LabelBlockRequest": obj({"count": {"type": "integer", "minimum": 1, "maximum": 500}}, ["count"]),
    "LabelBlock": obj({"block_id": uid, "serials": {"type": "array", "items": st}}),
    "EventBase": obj({"event_id": uid, "event_time": dt, "facility_id": uid, "on_behalf_of_org_id": uid, "device_signature": st, "evidence_ids": {"type": "array", "items": uid}}, ["event_id", "event_time"]),
    "LotCreate": obj({"event_id": uid, "label_serial": st, "plot_id": uid, "product": obj({"name": st, "variety": st}, ["name"]), "harvest_date": {"type": "string", "format": "date"}, "net_qty_kg": num, "qty_basis": {"type": "string", "enum": ["MEASURED", "ESTIMATED", "DECLARED"]}, "gross_kg": num, "tare_kg": num, "crates": {"type": "integer"}, "event_time": dt, "device_signature": st}, ["event_id", "label_serial", "product", "net_qty_kg", "event_time"]),
    "Lot": obj({"lot_id": uid, "public_code": st, "state": st, "custodian_org": uid, "pending_receiver_org": uid, "on_hand_kg": num, "lot_seq": {"type": "integer"}}),
    "LotList": obj({"items": {"type": "array", "items": S("Lot")}, "next_cursor": st}),
    "Inspection": obj({"event_id": uid, "event_time": dt, "grade": st, "defect_pct": num, "temperature_c": num, "notes": st, "evidence_ids": {"type": "array", "items": uid}}, ["event_id", "event_time"]),
    "Dispatch": obj({"event_id": uid, "event_time": dt, "to_org_id": uid, "qty_kg": num, "vehicle_no": st, "destination": st, "crates": {"type": "integer"}, "device_signature": st}, ["event_id", "event_time", "to_org_id", "qty_kg", "device_signature"]),
    "Handover": obj({"handover_id": uid, "lot_code": st, "state": st, "declared_qty_kg": num, "received_qty_kg": num, "expires_at": dt}),
    "Receive": obj({"event_id": uid, "event_time": dt, "matches": {"type": "boolean"}, "received_qty_kg": num, "rejected_qty_kg": num, "gross_kg": num, "tare_kg": num, "condition": st, "crates_counted": {"type": "integer"}, "evidence_ids": {"type": "array", "items": uid}, "device_signature": st}, ["event_id", "event_time", "device_signature"]),
    "Dispute": obj({"event_id": uid, "event_time": dt, "reason": st, "claimed_qty_kg": num, "evidence_ids": {"type": "array", "items": uid}, "device_signature": st}, ["event_id", "event_time", "reason", "device_signature"]),
    "Resolve": obj({"event_id": uid, "event_time": dt, "agreed_qty_kg": num, "note": st, "device_signature": st}, ["event_id", "event_time", "agreed_qty_kg", "device_signature"]),
    "Split": obj({"event_id": uid, "event_time": dt, "children": {"type": "array", "minItems": 1, "items": obj({"label_serial": st, "qty_kg": num}, ["label_serial", "qty_kg"])}, "device_signature": st}, ["event_id", "event_time", "children"]),
    "Merge": obj({"event_id": uid, "event_time": dt, "input_lot_codes": {"type": "array", "minItems": 2, "items": st}, "label_serial": st, "device_signature": st}, ["event_id", "event_time", "input_lot_codes", "label_serial"]),
    "Sort": obj({"event_id": uid, "event_time": dt, "outputs": {"type": "array", "items": obj({"grade": st, "qty_kg": num, "label_serial": st}, ["grade", "qty_kg"])}, "rejected_kg": num, "waste_kg": num}, ["event_id", "event_time", "outputs"]),
    "Repack": obj({"event_id": uid, "event_time": dt, "crates": {"type": "integer"}, "note": st}, ["event_id", "event_time"]),
    "Waste": obj({"event_id": uid, "event_time": dt, "qty_kg": num, "reason_code": st, "evidence_ids": {"type": "array", "items": uid}}, ["event_id", "event_time", "qty_kg", "reason_code"]),
    "Sale": obj({"event_id": uid, "event_time": dt, "qty_kg": num}, ["event_id", "event_time", "qty_kg"]),
    "Correction": obj({"event_id": uid, "event_time": dt, "reason": st, "new_values": {"type": "object"}, "device_signature": st}, ["event_id", "event_time", "reason", "new_values", "device_signature"]),
    "LabelReissue": obj({"event_id": uid, "event_time": dt, "new_serial": st, "reason": st, "device_signature": st}, ["event_id", "event_time", "new_serial", "reason", "device_signature"]),
    "EventResult": obj({"event_id": uid, "status": {"type": "string", "enum": ["ACCEPTED", "REJECTED", "CONFLICT"]}, "lot_seq": {"type": "integer"}, "reason_code": st, "message": st}, ["event_id", "status"]),
    "SyncBatch": obj({"items": {"type": "array", "maxItems": 100, "items": obj({"path": st, "method": st, "body": {"type": "object"}}, ["path", "body"])}}, ["items"]),
    "SyncResult": obj({"results": {"type": "array", "items": S("EventResult")}}),
    "EventList": obj({"items": {"type": "array", "items": {"type": "object"}}, "next_cursor": st}),
    "EvidenceUploadRequest": obj({"kind": {"type": "string", "enum": ["PHOTO", "SCALE_PHOTO", "LAB_CERT", "DOC"]}, "sha256": st, "content_type": st, "size_bytes": {"type": "integer"}}, ["kind", "sha256", "content_type"]),
    "EvidenceUpload": obj({"evidence_id": uid, "upload_url": st, "expires_at": dt}),
    "PublicLot": obj({"code": st, "product": st, "harvest_date": {"type": "string", "format": "date"}, "region": st, "stages_confirmed": {"type": "integer"}, "quality_checks": {"type": "integer"}, "certificates": {"type": "array", "items": st}, "scan_count": {"type": "integer"}, "gaps_flagged": {"type": "boolean"}, "disclaimer": st}),
    "RecallOpen": obj({"lot_code": st, "reason": st}, ["lot_code", "reason"]),
    "Recall": obj({"recall_id": uid, "status": st, "root_lot": st}),
    "RecallTrace": obj({"items": {"type": "array", "items": obj({"lot_code": st, "custodian": st, "state": st, "on_hand_kg": num, "sold_kg": num})}}),
}

# (method, path, operationId, summary, request schema, response schema, status, auth, idempotent)
OPS = [
    ("post", "/v1/auth/otp/request", "requestOtp", "Send an SMS code", "OtpRequest", None, 202, False, False),
    ("post", "/v1/auth/otp/verify", "verifyOtp", "Verify code, register device key", "OtpVerify", "TokenPair", 200, False, False),
    ("post", "/v1/auth/refresh", "refreshToken", "Rotate tokens", "RefreshRequest", "TokenPair", 200, False, False),
    ("post", "/v1/auth/passkeys/register/options", "passkeyRegisterOptions", "Start passkey registration", None, "WebAuthnOptions", 200, True, False),
    ("post", "/v1/auth/passkeys/register/verify", "passkeyRegisterVerify", "Finish passkey registration", "WebAuthnResult", None, 204, True, False),
    ("post", "/v1/auth/passkeys/login/options", "passkeyLoginOptions", "Start passkey login", None, "WebAuthnOptions", 200, False, False),
    ("post", "/v1/auth/passkeys/login/verify", "passkeyLoginVerify", "Finish passkey login", "WebAuthnResult", "TokenPair", 200, False, False),
    ("post", "/v1/auth/devices", "registerDevice", "Register a device signing key", "DeviceRegister", "Device", 201, True, True),
    ("get", "/v1/auth/devices", "listDevices", "List my devices", None, "Device", 200, True, False),
    ("delete", "/v1/auth/devices/{device_id}", "revokeDevice", "Revoke a device", None, None, 204, True, False),
    ("post", "/v1/organisations", "registerOrganisation", "Register a business or farmer (assisted or self)", "OrgRegister", "Org", 201, True, True),
    ("get", "/v1/partners", "listPartners", "List trusted partners", None, "Partner", 200, True, False),
    ("post", "/v1/partners/invitations", "invitePartner", "Invite a verified business", "PartnerInvite", "Partner", 201, True, True),
    ("post", "/v1/partners/invitations/{org_id}/accept", "acceptPartner", "Accept a partner invitation", None, "Partner", 200, True, True),
    ("post", "/v1/labels/blocks", "requestLabelBlock", "Download a block of unused QR serials", "LabelBlockRequest", "LabelBlock", 201, True, True),
    ("post", "/v1/lots", "createLot", "Create a batch and bind a QR serial", "LotCreate", "Lot", 201, True, True),
    ("get", "/v1/lots", "listLots", "List lots my organisation holds or touched", None, "LotList", 200, True, False),
    ("get", "/v1/lots/{code}", "getLot", "Get a lot (scoped to caller)", None, "Lot", 200, True, False),
    ("get", "/v1/lots/{code}/events", "listLotEvents", "Event history for a lot", None, "EventList", 200, True, False),
    ("post", "/v1/lots/{code}/inspections", "addInspection", "Record an inspection", "Inspection", "EventResult", 201, True, True),
    ("post", "/v1/lots/{code}/dispatch", "dispatchLot", "Dispatch to the next receiver", "Dispatch", "Handover", 201, True, True),
    ("post", "/v1/handovers/{handover_id}/receive", "receiveHandover", "Receive (accept)", "Receive", "Handover", 200, True, True),
    ("post", "/v1/handovers/{handover_id}/dispute", "disputeHandover", "Dispute quantities", "Dispute", "Handover", 200, True, True),
    ("post", "/v1/handovers/{handover_id}/resolve", "resolveHandover", "Agree a final quantity", "Resolve", "Handover", 200, True, True),
    ("post", "/v1/lots/{code}/split", "splitLot", "Split into child lots", "Split", "LotList", 201, True, True),
    ("post", "/v1/lots/merge", "mergeLots", "Merge lots into a new lot", "Merge", "Lot", 201, True, True),
    ("post", "/v1/lots/{code}/sort", "sortLot", "Sort or grade into outputs", "Sort", "LotList", 201, True, True),
    ("post", "/v1/lots/{code}/repack", "repackLot", "Repack containers, same lot", "Repack", "EventResult", 201, True, True),
    ("post", "/v1/lots/{code}/waste", "recordWaste", "Record waste or spoilage", "Waste", "EventResult", 201, True, True),
    ("post", "/v1/lots/{code}/sales", "recordSale", "Record retail sales (kg)", "Sale", "EventResult", 201, True, True),
    ("post", "/v1/events/{event_id}/corrections", "correctEvent", "Append a correction event", "Correction", "EventResult", 201, True, True),
    ("post", "/v1/lots/{code}/label-reissue", "reissueLabel", "Void old serial, bind a new one", "LabelReissue", "EventResult", 201, True, True),
    ("post", "/v1/evidence/uploads", "requestEvidenceUpload", "Get a signed upload URL", "EvidenceUploadRequest", "EvidenceUpload", 201, True, True),
    ("post", "/v1/sync/events", "syncEvents", "Submit queued events in a batch", "SyncBatch", "SyncResult", 200, True, True),
    ("post", "/v1/recalls", "openRecall", "Open a recall", "RecallOpen", "Recall", 201, True, True),
    ("get", "/v1/recalls/{recall_id}/trace", "traceRecall", "Forward-trace report", None, "RecallTrace", 200, True, False),
    ("get", "/v1/public/lots/{code}", "getPublicLot", "Consumer-visible summary (no login)", None, "PublicLot", 200, False, False),
]

def build():
    paths = {}
    for m, p, oid, summ, req, resp, code, auth, idem in OPS:
        op = {"operationId": oid, "summary": summ, "tags": [p.split("/")[2]], "responses": {}}
        params = []
        for seg in p.split("/"):
            if seg.startswith("{"):
                params.append({"name": seg.strip("{}"), "in": "path", "required": True, "schema": st})
        if idem:
            params.append({"$ref": "#/components/parameters/IdempotencyKey"})
        if m == "get" and ("list" in oid or oid == "listLotEvents"):
            params += [{"$ref": "#/components/parameters/Limit"}, {"$ref": "#/components/parameters/Cursor"}]
        if params:
            op["parameters"] = params
        if req:
            op["requestBody"] = {"required": True, "content": {"application/json": {"schema": S(req)}}}
        r = {"description": "OK"}
        if resp:
            r["content"] = {"application/json": {"schema": S(resp)}}
        op["responses"][str(code)] = r
        for ec, d in (("400", "Validation error"), ("401", "Not authenticated"), ("403", "Not allowed"), ("409", "Conflict with current state"), ("429", "Rate limited")):
            op["responses"][ec] = {"description": d, "content": {"application/problem+json": {"schema": S("Problem")}}}
        op["security"] = [{"bearerAuth": []}] if auth else []
        paths.setdefault(p, {})[m] = op
    doc = {
        "openapi": "3.0.3",
        "info": {"title": "AnnaSutra API", "version": "1.0.0-draft",
                 "description": "Contract for the mobile app and public page. The server is the authority. Every write carries an Idempotency-Key and a client-made event_id. Do not add endpoints or fields without human approval."},
        "servers": [{"url": "https://api.example.in", "description": "Replace with the real domain"}],
        "paths": paths,
        "components": {
            "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
            "parameters": {
                "IdempotencyKey": {"name": "Idempotency-Key", "in": "header", "required": True, "schema": uid, "description": "Same key returns the same result; sending twice stores once."},
                "Limit": {"name": "limit", "in": "query", "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50}},
                "Cursor": {"name": "cursor", "in": "query", "schema": st},
            },
            "schemas": SCHEMAS,
        },
    }
    with open(OUT, "w") as f:
        yaml.safe_dump(doc, f, sort_keys=False, width=120)
    print("wrote", OUT, "paths:", len(paths))

if __name__ == "__main__":
    build()
