# 05. Events, custody and quantity rules

Verified: the constraints in `db/schema.sql` were loaded and tested on PostgreSQL 16 (append-only blocking, gapless sequence, over-allocation, one open handover, in-transit consistency, self-parent edge).

## Event model

Business events are appended, never changed. The shape follows EPCIS ideas (what, when, where, why) but uses internal identifiers. Each event holds: event ID (client UUIDv7), type, lot, sequence number, device-claimed time, server-recorded time, organisation, user, device, on-behalf-of, facility, counterparty, quantity and basis, payload, `supersedes_event`, signature, previous hash, event hash, sync status.

**Time:** the device claims `event_time`. The server stamps `recorded_at` and flags events where the gap is large (start at 48 hours) or where the claimed time is before the previous event.

**Corrections:** a new event of type CORRECTION points to the event it replaces and carries a reason. Views show the latest effective value. Auditors see both. A quantity correction re-runs reconciliation and may raise an alert. Corrections beyond the author's window need a second approver.

## Event types and server-enforced preconditions

| Event | Preconditions | Effect |
|---|---|---|
| HARVEST_CREATE | Author is a farmer or agent acting for one; unbound serial issued to that org; qty > 0 | New lot CREATED, custodian = farmer, balance in = qty |
| INSPECT | Author is current custodian or pending receiver | Quality data; no quantity change |
| DISPATCH | Custodian only; state CREATED or IN_CUSTODY; no open handover; qty <= on-hand; receiver is a trusted partner | State IN_TRANSIT; handover PENDING |
| RECEIVE | Author is the named receiver; open handover | Computes difference; ACCEPTED or ACCEPTED_WITH_DISCREPANCY; custody moves |
| REJECT_AT_GATE | Pending receiver | Rejected quantity recorded against sender; rest accepted |
| SORT_GRADE | Custodian | Outputs (saleable + rejected + waste) must equal input |
| SPLIT | Custodian; children + remainder <= on-hand | New child lots with new QR; lot_edge rows |
| MERGE | Custodian of all inputs; same product | New lot with edges from all parents |
| REPACK | Custodian | Container change only, same lot |
| STORE | Custodian | Facility or cold-store note |
| WASTE / SPOIL | Custodian | waste += qty; reason mandatory; photo recommended |
| SELL_RETAIL | Retailer custodian | sold += qty (aggregate kg, no consumer identity) |
| CORRECTION | Same author org, or admin with second approver | New event; never mutates |
| LABEL_REISSUE | Custodian or admin | Void old serial, bind new serial to same lot (signed) |
| RECALL_OPEN / CLOSE | Admin, or any custodian in the lot's forward tree | State RECALLED; holders notified |

## Handover protocol (two parties)

1. Sender scans the batch, confirms quantity and condition, picks the receiver, taps Dispatch. State becomes IN_TRANSIT. The sender's event is signed with the device key.
2. Receiver scans the same QR, weighs, and taps **Matches** (one tap) or enters the actual quantity, rejected quantity and condition. Signed with the receiver's device key.
3. Within tolerance: ACCEPTED, variance recorded. Beyond tolerance: ACCEPTED_WITH_DISCREPANCY and the sender must agree or dispute within a window (start at 24 hours).
4. Custody moves to the receiver only when the receiver records receipt.

| Situation | Behaviour |
|---|---|
| Receiver refuses to confirm | Handover stays PENDING, then EXPIRED. Batch shows "custody unconfirmed". Sender remains responsible. Public view shows a gap |
| Receiver offline | Receiver scans and queues RECEIVE. Server validates on sync. Until then the batch is IN_TRANSIT |
| Quantities differ | Both numbers are stored and the difference flagged, never overwritten. A disputed batch cannot be re-dispatched until resolved or arbitrated |
| Non-custodian tries to record | Rejected (403) and logged as a security signal |
| Next participant never scans | Handover expires, batch flagged "orphan in transit", unaccounted quantity shown against the last custodian |
| Two receivers claim the same batch | Unique open-handover index plus row lock. First valid receipt wins, the second goes to a conflict queue |

**Signatures:** sign DISPATCH, RECEIVE, CORRECTION and LABEL_REISSUE with the device key (secure hardware, unlocked by biometric or PIN). Other events rely on the append-only chain. The weak point is false input, not forged storage.

## Quantity reconciliation (mass balance)

Worked example: farmer declares 500 kg. Aggregator accepts 480 kg, rejects 15 kg, documents 5 kg variance (1.0%). Wholesaler receives 475 kg (about 1.04% transit shrink). Sorting of 475 kg gives 450 saleable + 15 rejected + 10 waste = 475, so unexplained = 0.

Formula: `unexplained = qty_in - (transferred + split_out + rejected + waste + sold + documented_variance + on_hand)`.

**Tolerance [R]:** `max(2 x scale resolution, k x qty_in)`. Choose `k` per product and transit time from pilot data. Do not hard-code a number. Tomato shrink depends on heat, time and ripeness.

**Weights:** store gross, tare and net, plus basis (MEASURED, ESTIMATED, DECLARED). Estimates are allowed but weaker evidence. A scale-display photo is optional evidence.

### Invariants (enforced in the transaction and the database)

1. On-hand is never negative (CHECK constraint).
2. Sum of split children plus remainder <= parent on-hand.
3. A lot has one custodian and at most one open handover (partial unique index).
4. Events per lot have a gapless server-assigned sequence (UNIQUE).
5. Events are never updated or deleted (permissions + trigger).
6. Genealogy is acyclic.
7. A merge's inputs share the same custodian and product.
8. Quantity-changing events carry a reason code.

Legitimate loss is allowed if documented. Invariants flag **undocumented** gaps, they do not forbid loss.

## Forward and backward trace (recall)

```sql
-- Forward: every lot descended from the recalled lot, with current holders and stock
WITH RECURSIVE descendants AS (
  SELECT lot_id, 0 AS depth FROM lot WHERE public_code = :code
  UNION ALL
  SELECT e.child_lot, d.depth + 1
  FROM lot_edge e JOIN descendants d ON e.parent_lot = d.lot_id
)
SELECT l.public_code, o.name AS custodian, l.state,
       b.qty_in_kg - (b.qty_sold_kg + b.qty_waste_kg + b.qty_rejected_kg
         + b.qty_out_transferred_kg + b.qty_split_out_kg + b.qty_variance_kg) AS on_hand_kg,
       b.qty_sold_kg
FROM descendants d
JOIN lot l ON l.lot_id = d.lot_id
JOIN organisation o ON o.org_id = l.custodian_org
JOIN lot_balance b ON b.lot_id = l.lot_id;
-- Backward: same query with edge direction reversed (child to parent).
```

The result shows where unsold stock still is and how much was sold. It cannot identify consumers, so sold stock is handled through public notices.

## Sample event (tomato receipt)

```json
{
  "event_id": "0191f3c2-7a1e-7b2a-9d41-2c8e5a0b11f4",
  "event_type": "RECEIVE",
  "lot_public_code": "7K3Q9XMD4T2B",
  "lot_seq": 3,
  "event_time": "2026-10-07T09:12:40+05:30",
  "recorded_at": "2026-10-07T03:40:02Z",
  "org_id": "org-agg-bardhaman-01",
  "user_id": "usr-agg-001",
  "device_id": "dev-5f3a",
  "facility_id": "fac-collection-centre-bardhaman",
  "counterparty_org": "org-farmer-wb-000123",
  "qty_kg": 480.0,
  "qty_basis": "MEASURED",
  "payload": {
    "handover_id": "ho-0001",
    "declared_qty_kg": 500.0,
    "rejected_qty_kg": 15.0,
    "variance_kg": 5.0,
    "gross_kg": 512.0,
    "tare_kg": 32.0,
    "condition": "firm, 8% soft",
    "crates_declared": 20,
    "crates_counted": 20
  },
  "evidence": [{"kind": "SCALE_PHOTO", "sha256": "9c1f..."}],
  "sync_status": "ACCEPTED",
  "device_signature": "MEUCIQ...",
  "prev_hash": "b7a2...",
  "event_hash": "41de..."
}
```

## End-to-end tomato simulation (West Bengal)

Actors: Farmer Anita Mondal (F-WB-000123, Purba Bardhaman); Aggregator Bardhaman Agro Collect; Wholesaler Kolkata Fresh Traders; Distributor Metro Veg Dist; Retailer Gariahat Fresh.

| # | When | Actor | Event | Result |
|---|---|---|---|---|
| 1 | 6 Oct 16:30 | Farmer (assisted by agent) | HARVEST_CREATE 500 kg, 20 crates, sticker 7K3Q9XMD4T2B | Lot CREATED |
| 2 | 6 Oct 17:05 | Farmer | DISPATCH 500 kg to aggregator | IN_TRANSIT (signed) |
| 3 | 7 Oct 09:12 | Aggregator | RECEIVE gross 512, tare 32, accepts 480, reject 15, variance 5 | IN_CUSTODY |
| 4 | 7 Oct 11:00 | Aggregator | DISPATCH 480 kg to wholesaler | IN_TRANSIT |
| 5 | 7 Oct 17:40 | Wholesaler | RECEIVE 475 kg | IN_CUSTODY |
| 6 | 8 Oct 06:30 | Wholesaler | SORT_GRADE 450 + 15 + 10 = 475 | Unexplained 0 |
| 7 | 8 Oct 07:00 | Wholesaler | SPLIT 450 into 300 kg and 150 kg child lots, new QR each | Edges recorded |
| 8 | 8 Oct 12:00 | Distributor 1 | RECEIVE 300 kg | IN_CUSTODY |
| 9 | 9 Oct 07:15 | Retailer | RECEIVE 120 kg; creates shelf QR | IN_CUSTODY |
| 10 | 9-11 Oct | Retailer | SELL_RETAIL aggregates; 4 kg SPOIL | Balance tracked |

**Consumer sees:** "Tomato (hybrid). Harvested 6 Oct 2026, Purba Bardhaman, West Bengal. 5 stages, all confirmed. 3 quality checks recorded. Certificates: none attached. This record is based on information entered by supply-chain participants. It does not prove the contents of this package."

**Scenarios**

- **Recall:** lab fails lot 7K3Q... Admin opens recall, forward query finds 49 kg at the retailer and 71 kg already sold. Notifications go to every current holder. Sold stock is covered by a public notice.
- **Missing handover:** wholesaler dispatches 150 kg, nobody receives. After 24 hours it expires and is flagged "orphan in transit". Wholesaler stays responsible.
- **Disputed quantity:** distributor receives 288 kg of 300 declared (4%, above tolerance). ACCEPTED_WITH_DISCREPANCY. Sender notified to agree or dispute. Both numbers persist.
- **Cloned QR:** the same serial is scanned for RECEIVE in Kolkata while the lot is CLOSED and real stock is elsewhere. Alert fires (scan by non-custodian on closed lot). Admin reviews and may void the serial and reissue a new one for the real lot.

| Fact | Status |
|---|---|
| Who recorded an event and when (server) | Verified by the system |
| Quantity at each stage | Claimed, strengthened by cross-party agreement and scale photos |
| Origin plot and harvest date | Claimed |
| Quality grade | Observed by one party unless a third party inspects |
| Lab result | Verified only if the certificate checks out with the lab |
| Contents match the record | Not verifiable by software |
