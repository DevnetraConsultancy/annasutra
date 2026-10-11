# 01. Product and scope

## Users and roles

Every person belongs to exactly one **organisation** (a farmer is an organisation of one). Inside an organisation a person is Owner, Staff or Viewer.

| Who | Can do | Cannot do |
|---|---|---|
| Farmer | Create a batch, bind a QR sticker, weigh, add photos, approve the first receiver | Change anything after handing over |
| Cooperative agent | Register farmers and enter data on their behalf (stamped "recorded on behalf of") | Act without the farmer's recorded consent |
| Aggregator | Receive, inspect, sort, store, dispatch onward | Edit earlier records |
| Wholesaler | Receive, inspect, grade, split, merge, store, dispatch | Edit earlier records |
| Distributor | Receive, inspect, store, dispatch, split | Edit earlier records |
| Retailer | Receive, store, record sales and waste, create the shelf QR | Send stock to businesses that are not trusted partners |
| Consumer | Scan and read a short summary on the public page (no login) | See names, prices, quantities, farm location |
| Platform verifier (admin) | Verify businesses, issue QR blocks, review alerts, open recalls | Edit or delete any record |
| Auditor | Read-only access to evidence and logs, access is logged | Change anything |
| Security officer | Incidents, key rotation | Be the same person as the verifier |

## Scope

**In scope for version 1:** Flutter app (Android and iOS), backend API, hardened admin, public consumer page, QR labels, offline sync, hash-chain audit with external anchor, Cloudflare protection, logging for Indian rules.

**Out of scope for version 1:** payments, blockchain, IoT or GPS trackers, RFID, government portal integrations (no documented public interfaces confirmed), a custom web dashboard, GS1 membership.

**Future (do not build now):** EPCIS 2.0 export adapter, certificate checks with laboratories, BLE scale integration, tamper-evident labels for high-value lots, analytics.

## The approval chain (the key business rule)

1. A business joins once and is verified by the platform team.
2. The current holder of a batch picks the next receiver from their **trusted partners** (verified businesses that accepted a partner invitation).
3. The farmer approves only the first hop. After that, whoever holds the batch approves the next hop.
4. The receiver confirms receipt with biometric or PIN. Custody moves only then.
5. If the receiver never confirms, the handover expires. The batch is flagged and the last confirmed holder stays responsible.

**Ownership, custody and responsibility are different.** Version 1 enforces custody. Ownership is a recorded claim only.

## Success measures for the pilot

Share of batches with a complete chain; handover confirmation rate; unexplained quantity difference rate; time to record a handover (target under 60 seconds); duplicate-QR alert rate; recall trace time; offline sync failure rate; cost per traceable kilogram.

## Pilot shape (from the earlier plan)

About 40 farmers, 3 aggregators, 1 mandi with 4 or 5 wholesalers, 3 distributors, 10 to 15 retailers, 8 to 12 weeks. Field agent per cluster, local-language training, incentives such as faster payment confirmation and a digital record usable for credit conversations.
