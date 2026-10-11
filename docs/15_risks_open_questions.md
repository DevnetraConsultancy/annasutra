# 15. Risks, open questions and sources

## Residual risks (cannot be solved by software)

1. **Physical truth.** Two parties can agree on a false number or fake a photo. Needs audits, lab tests, trusted weighing and incentives.
2. **Endpoint compromise.** Malware on an unlocked phone can approve actions. Secure-hardware keys help but not completely.
3. **Human factors.** Weak recovery processes and social engineering are the most common real breaches.
4. **Insider and collusion risk** at the platform operator.
5. **Zero-day flaws** in dependencies, plugins or vendors.
6. **Adoption.** Users tapping "matches" without weighing, or traders with no reason to take part.

## Open questions for the human owner

1. Who operates the platform, and who holds the external anchor account? (governance)
2. Which cloud and which Indian region? Does any rule require data to stay in India?
3. Which SMS provider, and what sender registration is needed?
4. Does AnnaSutra count as a CERT-In covered entity, and what exactly must be reported?
5. DPDP: exact commencement dates, classification, consent wording, retention periods. (counsel)
6. Do FSSAI or state mandi rules require record formats or retention periods for tomato traders?
7. Do any government systems offer permitted data exchange? Do not promise integrations until confirmed.
8. Tolerance values per product and season. Start with pilot data.
9. Are tamper-evident labels worth the cost for any lots?
10. Who prints and distributes QR sticker books, and who pays?
11. Passkey behaviour and device-key signing on the real target phones. Prototype early.
12. Does the team have a Mac (or a macOS CI runner) for iOS builds?

## Things that change quickly: check before relying on them [verify]

Cloudflare plan features and limits; Flutter plugin versions and maintenance (passkeys, SQLCipher with Drift, scanner); minimum OS versions for passkeys; Play Integrity and App Attest requirements; Google Play and Apple store requirements; SMS sender registration rules; Antigravity menu names and features (version 2.0 was announced at Google I/O 2026).

## Sources used while preparing this package (accessed 11 October 2026)

- DPDP Rules 2025 timeline: https://www.jsalaw.com/?p=55573 and https://www.taxmann.com/post/blog/analysis-indias-dpdp-act-and-rules/
- CERT-In directions (6-hour reporting, 180-day logs in India): https://khaitanco.com/thought-leaderships/Indian-Computer-Emergency-Response-Team-Direction-Paradigm-Shift-in-Cyber-Incident-Reporting and https://mondaq.co.uk/india/it-and-internet/1270332/6-hours-to-report-cyber-incidents-to-cert-in
- OWASP ASVS: https://owasp.org/www-project-ASVS/ (5.0.0 released May 2025)
- ISO 22005 announcement: https://www.iso.org/news/2007/07/Ref1063.html (no newer edition found)
- Flutter passkeys and platform minimums: https://mojoauth.com/blog/add-passkeys-to-flutter-in-30-minutes (secondary source; read the plugin's own docs) and https://pub.dev/documentation/flutter_passkey_service
- Antigravity getting started: https://codelabs.developers.google.com/getting-started-google-antigravity ; documentation: https://antigravity.google/docs
- Google I/O 2026 developer keynote (Android CLI and skills): https://developers.googleblog.com/all-the-news-from-the-google-io-2026-developer-keynote/

**Not researched in this package:** GS1 EPCIS and Digital Link current text, FSSAI recall and licensing text, APEDA and e-NAM interfaces, INATrace internals. Do not rely on statements about them without checking the official sources (gs1.org, fssai.gov.in, apeda.gov.in, enam.gov.in).
