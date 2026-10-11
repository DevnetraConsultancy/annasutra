# 16. Platform targets: Android and Web from one Flutter codebase

**Decision (owner request):** build one Flutter codebase that runs as an **Android app** and as a **web app** (installable PWA). iOS can be added later from the same code. Backend, API, data model and rules do not change.

## Who uses which

| Platform | Main users | Why |
|---|---|---|
| Android app | Farmers, agents, aggregators, mandi staff, retailers | Camera, offline work, hardware-backed keys, background sync |
| Web app | Wholesalers, distributors, retail managers, office staff, anyone who cannot install the app | Works on a laptop or any phone browser. No install |
| Public consumer page | Shoppers | **Stays a separate tiny server-rendered page**, not Flutter web. A Flutter web app has a heavy first download, which is wrong for a shopper on a slow network |
| Admin | AnnaSutra team | Hardened Django admin behind Cloudflare Access |

## What is different on web (the agent must design for this, not hide it)

Everything below is a recommendation [R] or needs checking [verify] against current Flutter, browser and plugin documentation.

| Topic | Android | Web | Rule |
|---|---|---|---|
| Event signing key | Key in Android Keystore (secure hardware), unlocked by biometric or PIN | Browsers have no Keystore. Use a **WebAuthn passkey assertion** over the hash of the event | Sensitive actions (dispatch, receive, dispute, resolve, correct, label reissue) on web **require WebAuthn**. If the browser or device cannot do it, that user can view and record non-signed events but cannot hand over |
| Login | Passkey where supported, device key fallback | Passkey first. SMS code for enrolment and recovery | Needs your domain for passkey association |
| Local database | Drift + SQLCipher, key in Keystore | Drift on web storage (IndexedDB or similar) with **field-level encryption** using a non-extractable WebCrypto key [verify support]. SQLCipher is not available | Web local data is weaker protection. Store the minimum, wipe on logout, short expiry |
| Background sync | WorkManager | No reliable background work. Sync while the app is open and when the connection returns | Show an unsynced counter. Warn before closing with unsynced items |
| Storage eviction | Not an issue | Browsers can clear site data under pressure | Ask for persistent storage, sync often, warn the user |
| Session | Tokens in secure storage | Prefer HttpOnly, Secure, SameSite=Strict cookies. **Never** tokens in localStorage | Strict Content Security Policy [verify Flutter web CSP needs] |
| QR scanning | Camera plugin | Browser camera, needs HTTPS [verify plugin web support] | Always offer manual short-code entry |
| Photos | Camera, compress, hash | File picker or camera, compress, hash | Strip location data |
| Performance | Good on low-end phones | Larger first download. Test on cheap phones | Set a size budget in CI [R] |
| Accessibility | Screen reader works | Flutter web accessibility needs care [verify] | Test with a screen reader and keyboard |

## Required code structure (Phase 0)

Define interfaces in the domain layer and give each platform its own implementation. Business rules and screens must not know which platform they run on.

- `Signer`: Android Keystore implementation, Web WebAuthn implementation.
- `SecureStore`: secure storage on Android, encrypted storage on web.
- `LocalDatabase`: SQLCipher on Android, encrypted-field web storage on web.
- `SyncScheduler`: WorkManager plus foreground on Android, foreground only on web.
- `QrScanner`: native camera on Android, browser camera on web.

## Security consequences

Web has a larger attack surface for stolen sessions (XSS). So: strict CSP, no inline scripts, no third-party scripts, cookies not tokens, short sessions, re-authenticate for sensitive actions, and the earlier web hardening list in `docs/07` applies to the web target. Use OWASP ASVS 5.0 for the web target and MASVS for the Android target.

## Test matrix

Android 8 and above on a low-cost phone; Chrome, Edge and Firefox on desktop; Chrome on Android; Safari if iOS or macOS users are expected. Test each sensitive action with and without WebAuthn support, and offline then online.

## What to tell the human if something does not work

If WebAuthn, hardware keys or encrypted local storage behave differently than expected on a platform, stop and report. Do not weaken signing or storage rules to make the web build "work".
