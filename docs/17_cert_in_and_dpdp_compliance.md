# 17. CERT-In Directions and DPDP Act 2023 Compliance Guide

This document defines AnnaSutra's operational policies and architecture for statutory compliance under Indian cyber and data protection laws:
1. **CERT-In Cyber Incident Reporting Directions (2022)**
2. **Digital Personal Data Protection (DPDP) Act 2023 & DPDP Rules 2025**

---

## 1. CERT-In Directions (Cyber Security Directions, 2022)

### 1.1 Mandatory 6-Hour Reporting Window
Under Rule 20 of CERT-In Cyber Security Directions (2022), all cyber incidents falling into the specified types (including unauthorized access to systems, data breaches, ransomware, identity theft, and fake application/portal activity) must be reported to the Indian Computer Emergency Response Team (CERT-In) within **6 hours** of noticing or being brought to notice.

- **Designated Filing Channel:** Email to `incident@cert-in.org.in` or portal at `https://www.cert-in.org.in`.
- **Clock Start:** The 6-hour countdown begins the moment an anomaly is confirmed as an active security incident by system logs or operator triage.
- **Incident Lead:** Platform Security Officer / Chief Technology Officer.
- **Reporting Format:**
  1. Incident details (Date, Time, Timezone).
  2. Affected systems (IP addresses, domain names, cloud regions).
  3. Nature of breach / unauthorized access.
  4. Immediate containment actions taken.
  5. Contact point for forensic investigation.

### 1.2 180-Day ICT System Log Retention Within India
- All system logs, authentication events, API access records, and audit trails must be retained for at least **180 days** within Indian territorial jurisdiction.
- **Log Security:**
  - Audit logs are written to append-only storage (`logs/audit.log`).
  - No plaintext OTPs, auth tokens, device signatures, or unmasked phone numbers are logged.
  - Timestamps are strictly synchronized via Indian Standard Time (IST) / UTC with NTP.

---

## 2. Digital Personal Data Protection (DPDP) Act 2023 & DPDP Rules 2025

### 2.1 Core Principles Implemented
1. **Notice & Consent:** A clear, itemized notice is provided to farmers, traders, and staff in **English, Hindi, and Bengali** prior to collecting personal data (mobile number and device identifiers).
2. **Purpose Limitation:** Data is processed solely for verifying agricultural custody handovers, lot identity, and fraud prevention in food supply chains.
3. **Storage Limitation & Erasure:** Inactive user credentials and device bindings are wiped on logout or upon validated account termination request, subject to statutory tax/traceability retention rules.
4. **Data Principal Rights:**
   - **Right to Access:** Users can view their registered profile, verified organisation, and active devices.
   - **Right to Correction:** Users can request correction of inaccurate profile data.
   - **Right to Grievance Redressal:** A named Grievance Redressal Officer is published on the portal and mobile app with a guaranteed 7-day resolution timeline.

### 2.2 Grievance Redressal Officer Contact
- **Name:** Data Protection & Grievance Officer, AnnaSutra Agri-Traceability
- **Email:** grievance@annasutra.in
- **Location:** Kolkata, West Bengal, India
- **Response SLA:** Acknowledgment within 24 hours, resolution within 7 calendar days.

---

## 3. Data Protection Invariants in AnnaSutra Architecture

| Artifact | Data Protection Implementation |
|---|---|
| Consumer Public Page | Reads exclusively from `public_view` projection. Zero personal data (phone numbers, farmer names, exact GPS coordinates) exposed. |
| Ledger Trace Events | Append-only in PostgreSQL. Signed with device keys. Protected by DB triggers forbidding UPDATE and DELETE. |
| Database Encryption | Field-level encryption for sensitive attributes, SQLCipher on Android, TLS 1.3 in transit, AES-256 at rest. |
| External Anchoring | Daily cryptographic Merkle root anchored externally to provide mathematical proof of non-tampering without publishing raw records. |
