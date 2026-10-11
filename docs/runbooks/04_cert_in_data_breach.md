# Runbook 04: Data Breach & CERT-In Mandatory Escalation

## Severity: CRITICAL
## Statutory Requirement
Under CERT-In Directions 2022 (Rule 20), cyber security incidents must be reported to `incident@cert-in.org.in` within **6 hours** of discovery.

## 6-Hour Timeline & Action Checklist

| Time Elapsed | Target Action | Responsible Party |
|---|---|---|
| **T + 0 min** | Breach detected (DB intrusion, credential dumping, API exfiltration). | Incident Commander |
| **T + 30 min** | Containment: isolate affected instances, block attacker IPs, rotate root keys. | DevSecOps Lead |
| **T + 90 min** | Preliminary impact assessment: estimate data scope (principals affected, lots impacted). | Security Officer & Legal |
| **T + 180 min** | Draft CERT-In Incident Report Form with system logs, IOCs, and remediation steps. | Security Officer |
| **T + 300 min** | Executive sign-off and dispatch report to `incident@cert-in.org.in`. | CTO / CEO |
| **T + 360 min** | **Hard Deadline:** Formal confirmation and receipt of CERT-In incident tracking ID. | Legal Counsel |

## CERT-In Incident Filing Template
```text
To: incident@cert-in.org.in
Subject: Cyber Incident Report - AnnaSutra Agri-Traceability Platform

1. Name of Organisation: AnnaSutra Agri-Traceability
2. Date and Time of Incident (IST): [YYYY-MM-DD HH:MM:SS]
3. Time Incident was Noticed: [YYYY-MM-DD HH:MM:SS]
4. Nature / Type of Incident: [Unauthorized Access / Data Exfiltration / Ransomware]
5. Affected Systems / IPs: [List public endpoints, cloud region, IP ranges]
6. Point of Contact: Data Protection & Security Officer (security@annasutra.in, +91-XXXXXXXXXX)
7. Containment Measures Taken:
   - Suspended compromised user sessions and revoked API tokens.
   - Isolated compromised database instances and rotated cryptographic keys.
   - Exported forensic audit logs from 180-day audit store.
```
