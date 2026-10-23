"""Builds every diagram used by the AnnaSutra 2.0 Farmer-First architecture proposal.

Run:  backend/venv/Scripts/python.exe scripts/arch_proposal_diagrams.py
Output: docs/diagrams/proposal/*.png
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from diagram_engine import Diagram  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "diagrams", "proposal"))

L0, L1, L2 = "#F7FAF8", "#EAF0F6", "#FBF4E8"


def lanes3(a, b, c):
    return [(a, L0), (b, L1), (c, L2)]


def p(name):
    return os.path.join(OUT, name)


# ---------------------------------------------------------------- core concept
def d_four_rails():
    d = Diagram("Core concept: four rails on one ledger",
                "Goods move, money settles, trust is earned, and the farmer gains from every closed trade.",
                [("GOODS rail\nwhat moves", L0), ("MONEY rail\nwho gets paid", "#FBF4E8"),
                 ("TRUST rail\nwho to believe", L1), ("INSIGHT rail\nwhat the farmer gains", "#F1EDF8")],
                5, cw=330, lane_h=200)
    rows = [
        (0, "G", ["Lot + QR with origin claims", "Open handshake, offline token", "Dual weigh slip (both sides)",
                  "Split / merge / sort genealogy", "Consumer QR provenance page"]),
        (1, "M", ["Trade: price + payment terms", "Risk-based credit rule", "Split-pay: undisputed value now",
                  "UPI or cash proof, farmer confirms", "Settled: receivable cleared"]),
        (2, "T", ["Tiered verification T0 to T3", "Evidence: photo, geo, lab", "Dispute ladder with SLAs",
                  "Trust band + buyer Pay-Score", "Hash-chained audit ledger"]),
        (3, "L", ["Mandi price band at listing", "Buyer Pay-Score shown before dispatch",
                  "Farmer-share view", "Credit passport (with consent)", "Insurance + loan eligibility"]),
    ]
    for lane, rail, items in rows:
        for c, t in enumerate(items):
            d.node(f"r{lane}{c}", c, lane, t, rail=rail)
            if c:
                d.edge(f"r{lane}{c-1}", f"r{lane}{c}")
    d.edge("r00", "r10", "b", "t", dash=True, label="lot becomes tradeable")
    d.edge("r02", "r12", "b", "t", dash=True, label="weight sets value")
    d.edge("r13", "r23", "b", "t", dash=True, label="behaviour feeds scores")
    d.edge("r23", "r33", "b", "t", dash=True, label="scores unlock credit")
    return d.render(p("01_four_rails.png"))


def d_layers():
    lanes = [("Clients", L0), ("Edge + API", L1), ("Domain services", "#FBF4E8"),
             ("Data stores", "#F1EDF8"), ("Integrations", L1)]
    d = Diagram("System layers", "Boring, proven building blocks; guarantees come from the domain services and the ledger.",
                lanes, 6, cw=300, lane_h=170, font=22)
    cl = ["Farmer app (offline PWA / Android)", "IVR + WhatsApp + SMS", "Agent / FPO console",
          "Trader + retailer web", "Consumer QR page", "Verifier / mediator desk"]
    ed = ["API gateway: auth, rate limit, audit", "OTP + passkey identity", "Sync gateway (idempotent events)",
          "Notification: SMS, WhatsApp, push", "Signed-token service", "Policy + consent engine"]
    dom = ["Lot + genealogy", "Trade + terms", "Custody + title", "Payment + settlement",
           "Dispute + mediation", "Trust + scores"]
    da = ["Hash-chained event ledger", "Relational store", "Evidence vault (EXIF stripped)",
          "Encrypted PII vault", "Public read models", "Daily Merkle anchor"]
    ig = ["UPI / PSP payments", "Agmarknet / eNAM prices", "Account Aggregator", "Weighbridge + IoT sensors",
          "e-way bill / GST", "DigiLocker / KYC"]
    for lane, rail, items in [(0, "G", cl), (1, "X", ed), (2, "M", dom), (3, "L", da), (4, "T", ig)]:
        for c, t in enumerate(items):
            d.node(f"l{lane}{c}", c, lane, t, rail=rail)
    return d.render(p("02_system_layers.png"))


def d_trade_states():
    d = Diagram("Trade state machine",
                "A trade is a contract. Delivery, payment and disputes are all states of the same object. Numbers refer to the transition table.",
                [("Happy path", L0), ("Exceptions", L2)], 7, lane_h=215)
    d.node("draft", 0, 0, "DRAFT", rail="X", bold_first=True)
    d.node("offered", 1, 0, "OFFERED", rail="M", bold_first=True)
    d.node("agreed", 2, 0, "AGREED", rail="M", bold_first=True)
    d.node("disp", 3, 0, "DISPATCHED", rail="G", bold_first=True)
    d.node("deliv", 4, 0, "DELIVERED", rail="G", bold_first=True)
    d.node("due", 5, 0, "PAYMENT_DUE", rail="M", bold_first=True)
    d.node("settled", 6, 0, "SETTLED", kind="term")
    d.node("cancel", 1, 1, "CANCELLED", rail="X", bold_first=True)
    d.node("expired", 2, 1, "EXPIRED", rail="X", bold_first=True)
    d.node("disputed", 4, 1, "DISPUTED", rail="T", bold_first=True)
    d.node("overdue", 6, 1, "OVERDUE", rail="T", bold_first=True)
    d.edge("draft", "offered", label="1")
    d.edge("offered", "agreed", label="2")
    d.edge("agreed", "disp", label="3")
    d.edge("disp", "deliv", label="4")
    d.edge("deliv", "due", label="5")
    d.edge("due", "settled", label="6")
    d.edge("offered", "cancel", "b", "t", label="7")
    d.edge("agreed", "expired", "b", "t", label="8")
    d.edge("deliv", "disputed", "b", "t", label="9")
    d.edge("disputed", "due", "r", "b", b_dx=-50, label="10")
    d.edge("due", "overdue", "b", "l", a_dx=50, label="11")
    d.edge("overdue", "settled", "t", "b", label="12")
    return d.render(p("03_trade_states.png"))


def d_handshake():
    d = Diagram("Universal handshake: open, offline-safe, two-signature delivery",
                "Used by every entity. No pre-linking; both devices only need to be physically together.",
                lanes3("Seller (any entity)", "Platform", "Buyer (any entity)"), 7)
    d.node("s1", 0, 0, "Create trade on the lot: qty, price, delivery and payment terms", rail="M")
    d.node("p1", 0, 1, "Check tiers; show buyer Pay-Score and mandi reference price", rail="T")
    d.node("s2", 1, 0, "Scan buyer ID QR (names the buyer, no pre-link)", rail="G")
    d.node("s3", 2, 0, "Sign Handover Token (offline OK): lot, qty, price, buyer, expiry", rail="L")
    d.node("b1", 3, 2, "Scan token; verify signature offline", rail="G")
    d.node("b2", 4, 2, "Countersign slip: accepted, rejected + reason + photo", rail="T")
    d.node("p2", 5, 1, "Sync: verify 2 signatures, nonce, custody chain; write ledger", rail="L")
    d.node("d2", 6, 1, "Within tolerance and evidence OK?", kind="dec")
    d.node("n1", 6, 0, "Yes: title moves; pay now by UPI link or cash proof", rail="M")
    d.node("n2", 6, 2, "No: undisputed part paid now; rest opens a case", rail="M")
    d.edge("s1", "p1", "b", "t", label="validate")
    d.edge("p1", "s2", "r", "b")
    d.edge("s2", "s3")
    d.edge("s3", "b1", "b", "t", label="goods + token")
    d.edge("b1", "b2")
    d.edge("b2", "p2", "r", "b", label="sync when online")
    d.edge("p2", "d2")
    d.edge("d2", "n1", "t", "b", label="Yes")
    d.edge("d2", "n2", "b", "t", label="No")
    return d.render(p("04_handshake.png"))


# ---------------------------------------------------------------- entities
def d_producer():
    d = Diagram("Entity 1: Producer (farmer) algorithm",
                "From harvest to paid-and-confirmed, with the farmer in control of price, terms and proof.",
                lanes3("Farmer (app / agent / voice)", "Platform", "Counterparty (buyer, FPO, verifier)"), 7)
    d.node("a", 0, 0, "Harvest ready", kind="term")
    d.node("b", 1, 0, "Declare harvest: crop, qty, plot, date, photo", rail="G")
    d.node("c", 1, 1, "Tier and yield plausibility OK?", kind="dec")
    d.node("x", 1, 2, "FPO or verifier vouches (assisted tier-up)", rail="T")
    d.node("dd", 2, 1, "Create lot + QR; attach origin claims; show mandi price band", rail="L")
    d.node("e", 2, 0, "Choose route (direct, FPO, mandi); set price and terms", rail="M")
    d.node("g", 3, 1, "Show buyer Pay-Score; credit terms only for proven buyers", rail="T")
    d.node("h", 4, 0, "Handshake: scan buyer, sign token, hand over goods", rail="G")
    d.node("i", 4, 2, "Buyer weighs, inspects and countersigns the slip", rail="G")
    d.node("j", 5, 1, "Verify, write ledger, split-pay the undisputed value", rail="L")
    d.node("k", 6, 2, "Buyer pays by UPI or marks cash paid", rail="M")
    d.node("l", 6, 0, "Farmer confirms payment (tap / OTP / voice)", rail="M")
    d.node("z", 5, 0, "Settled: scores and credit passport updated", kind="term")
    d.edge("a", "b")
    d.edge("b", "c", "b", "t")
    d.edge("c", "x", "b", "t", label="No")
    d.edge("c", "dd", "r", "l", label="Yes")
    d.edge("x", "dd", "r", "b", dash=True, label="after vouch")
    d.edge("dd", "e", "t", "b", label="lot ready")
    d.edge("e", "g", "r", "t")
    d.edge("g", "h", "r", "b", b_dx=-50)
    d.edge("h", "i", "b", "t", a_dx=50, b_dx=50, label="goods + token")
    d.edge("i", "j", "r", "b")
    d.edge("j", "k", "r", "l", label="payment request")
    d.edge("k", "l", "t", "b", label="proof")
    d.edge("l", "z", "l", "r")
    return d.render(p("05_producer.png"))


def d_aggregator():
    d = Diagram("Entity 2: Aggregator / FPO collection centre algorithm",
                "Pays farmers the same day, pools lots without losing who grew what, and shares upside fairly.",
                lanes3("Farmers", "Aggregator / FPO centre", "Platform and buyers"), 7)
    d.node("n1", 0, 1, "Publish today's rate card by grade; farmers see it before they arrive", rail="M")
    d.node("n2", 1, 0, "Farmer arrives with lot (QR or phone)", rail="G")
    d.node("n3", 1, 1, "Weigh in front of farmer; photo; quality check", rail="G")
    d.node("n4", 2, 1, "Grade meets rate card?", kind="dec")
    d.node("n4b", 2, 2, "Re-grade with evidence; farmer accepts, withdraws or asks mediation", rail="T")
    d.node("n5", 3, 1, "Trade created: net qty x rate; same-day payment", rail="M")
    d.node("n6", 3, 0, "Farmer confirms payment (tap / OTP)", rail="M")
    d.node("n7", 4, 1, "At cut-off: merge lots, keep each farmer's share in genealogy", rail="L")
    d.node("n8", 5, 1, "Sort into grade lots A / B / C; print QR labels", rail="G")
    d.node("n9", 5, 2, "Sell to any verified buyer (standard sell flow)", rail="M")
    d.node("n10", 6, 1, "Excess over rate paid + margin cap shared pro-rata", rail="M")
    d.node("n11", 6, 0, "Farmers see their share in the app", kind="term")
    d.edge("n1", "n3", "r", "l")
    d.edge("n2", "n3", "b", "t")
    d.edge("n3", "n4")
    d.edge("n4", "n5", label="Yes")
    d.edge("n4", "n4b", "b", "t", label="No")
    d.edge("n4b", "n5", "r", "b", dash=True, label="agreed after review")
    d.edge("n5", "n6", "t", "b", label="paid")
    d.edge("n5", "n7")
    d.edge("n7", "n8")
    d.edge("n8", "n9", "b", "t")
    d.edge("n9", "n10", "r", "b", label="sale proceeds")
    d.edge("n10", "n11", "t", "b")
    return d.render(p("06_aggregator.png"))


def d_wholesaler():
    d = Diagram("Entity 3: Wholesaler / commission agent algorithm",
                "Mandi sales become auditable: every bid logged, every deduction scheduled, statement shown before payout.",
                lanes3("Seller (farmer or aggregator)", "Wholesaler / commission agent", "Retailers and carriers"), 7)
    d.node("w1", 0, 0, "Consign lot: handshake + weigh slip", rail="G")
    d.node("w2", 0, 1, "Receive: weigh, temperature, quality check", rail="G")
    d.node("w3", 1, 1, "Principal or commission mode?", kind="dec")
    d.node("w5", 2, 1, "Commission: open auction log, every bid timed", rail="T")
    d.node("w4", 2, 2, "Principal: buy at agreed price, pay per terms, take title", rail="M")
    d.node("w6", 3, 1, "Split into sale lots; sort; new QR labels", rail="G")
    d.node("w7", 4, 2, "Retailers accept splits; weigh at pickup (handshake)", rail="G")
    d.node("w9", 5, 1, "Account-sale: gross minus itemised, scheduled deductions only", rail="M")
    d.node("w10", 5, 0, "Seller sees statement BEFORE payout; can query any line", rail="T")
    d.node("w11", 6, 1, "Net payout within SLA; each deduction has a receipt", rail="M")
    d.node("w12", 6, 2, "Seller confirms; deduction analytics per mandi", kind="term")
    d.edge("w1", "w2", "b", "t")
    d.edge("w2", "w3")
    d.edge("w3", "w5", label="Commission")
    d.edge("w3", "w4", "b", "l", label="Principal")
    d.edge("w5", "w6")
    d.edge("w4", "w6", "r", "b")
    d.edge("w6", "w7", "r", "l", label="one trade per split")
    d.edge("w7", "w9", "r", "b", label="sale proceeds")
    d.edge("w9", "w10", "t", "b", label="statement")
    d.edge("w10", "w11", "r", "t", label="approve / query")
    d.edge("w11", "w12", "b", "t")
    return d.render(p("07_wholesaler.png"))


def d_carrier():
    d = Diagram("Entity 4: Distributor / carrier algorithm",
                "Carriers hold custody, not title. Transit loss is attributed by delivery terms, never silently to the farmer.",
                lanes3("Dispatcher (owner)", "Carrier (custody only)", "Receiver"), 7)
    d.node("c1", 0, 0, "Dispatch: handshake names the carrier; title stays with owner", rail="G")
    d.node("c2", 1, 1, "Pickup: count crates, photo, temperature; custody moves", rail="G")
    d.node("c3", 2, 1, "In transit: GPS, temperature, door-open logs (offline buffer)", rail="L")
    d.node("c4", 3, 1, "Temp, route or delay breach?", kind="dec")
    d.node("c5", 3, 0, "Alert owner + receiver; adjust shelf life; keep evidence", rail="T")
    d.node("c6", 4, 2, "Arrive: receiver recounts and weighs (handshake)", rail="G")
    d.node("c7", 5, 2, "Transit loss within tolerance?", kind="dec")
    d.node("c8", 6, 2, "Yes: close leg; freight invoice linked to trade", rail="M")
    d.node("c9", 6, 1, "No: loss attributed by delivery terms; carrier claim opened", rail="T")
    d.edge("c1", "c2", "r", "t")
    d.edge("c2", "c3")
    d.edge("c3", "c4")
    d.edge("c4", "c5", "t", "b", label="Yes")
    d.edge("c4", "c6", "r", "t", label="No")
    d.edge("c5", "c6", "r", "t", dash=True, label="continues")
    d.edge("c6", "c7")
    d.edge("c7", "c8", label="Yes")
    d.edge("c7", "c9", "t", "l", label="No")
    return d.render(p("08_carrier.png"))


def d_retailer():
    d = Diagram("Entity 5: Retailer algorithm",
                "Buys from anyone verified (including farmers directly), sells with a consumer QR, and closes the loop on waste and recalls.",
                lanes3("Supplier (farmer, FPO, wholesaler)", "Retailer", "Evidence, platform, consumers"), 7)
    d.node("r1", 0, 0, "Supplier dispatches via handshake (direct farmer purchase allowed)", rail="G")
    d.node("r2", 1, 1, "Receive: weigh, temperature, quality; min shelf-life check", rail="G")
    d.node("r3", 2, 1, "Accept?", kind="dec")
    d.node("r4", 2, 2, "Reject with reason code + photo; rejected qty stays with supplier", rail="T")
    d.node("r5", 3, 1, "Pay per terms (UPI / cash proof); supplier sees SLA clock", rail="M")
    d.node("r7", 3, 0, "Optional verified-origin premium credited to supplier", rail="M")
    d.node("r6", 4, 1, "Split to shelf batches; print consumer QR with best-before", rail="G")
    d.node("r8", 5, 1, "Sell at POS; mark down on low shelf-life; log waste reason", rail="G")
    d.node("r9", 5, 2, "Consumer scans QR: provenance, freshness rating, issue report", rail="T")
    d.node("r10", 6, 1, "Safety issue or recall?", kind="dec")
    d.node("r11", 6, 0, "Recall: quarantine batches, block POS, notify upstream", rail="T")
    d.edge("r1", "r2", "r", "t")
    d.edge("r2", "r3")
    d.edge("r3", "r4", "b", "t", label="No")
    d.edge("r3", "r5", label="Yes")
    d.edge("r5", "r7", "t", "b", label="premium")
    d.edge("r5", "r6")
    d.edge("r6", "r8")
    d.edge("r8", "r9", "b", "t")
    d.edge("r8", "r10")
    d.edge("r9", "r10", "r", "b")
    d.edge("r10", "r11", "t", "b", label="Yes")
    return d.render(p("09_retailer.png"))


def d_consumer():
    d = Diagram("Entity 6: Consumer algorithm",
                "Zero-PII provenance, a visible farmer share, and a feedback loop that rewards good farms.",
                lanes3("Consumer", "Platform", "Chain (farmer, retailer, verifier)"), 7)
    d.node("q1", 0, 0, "Scan QR on pack", kind="term")
    d.node("q2", 1, 1, "Public view: consented fields only; no prices, no PII", rail="L")
    d.node("q3", 2, 1, "Show origin district, harvest date, journey, evidence level per claim", rail="T")
    d.node("q4", 3, 1, "Farmer-share indicator (aggregated, k-anonymous)", rail="T")
    d.node("q5", 3, 0, "Optional: rate freshness, thank farmer (UPI tip), report issue", rail="G")
    d.node("q6", 4, 0, "Safety or quality issue?", kind="dec")
    d.node("q7", 5, 1, "Open signal; cluster reports by lot; threshold triggers review", rail="L")
    d.node("q8", 5, 2, "Aggregated feedback reaches farmer and retailer", rail="T")
    d.node("q9", 6, 1, "Verifier reviews cluster; may open recall", rail="T")
    d.edge("q1", "q2", "r", "t")
    d.edge("q2", "q3")
    d.edge("q3", "q4")
    d.edge("q4", "q5", "t", "b")
    d.edge("q5", "q6")
    d.edge("q6", "q7", "r", "t", label="Yes: safety")
    d.edge("q6", "q8", "b", "l", label="No: quality note")
    d.edge("q7", "q9")
    return d.render(p("10_consumer.png"))


def d_verifier():
    d = Diagram("Entity 7: Verifier / mediator onboarding algorithm",
                "Progressive trust: start with a phone number, earn higher tiers with evidence. Fraud rules run before humans.",
                lanes3("Applicant", "Verifier / mediator", "Platform rules engine"), 7)
    d.node("v1", 0, 0, "Registration submitted (self or via agent with consent)", kind="term", w=240)
    d.node("v2", 1, 2, "Auto checks: duplicate ID or plot, geo mismatch, qty > area x max yield", rail="T")
    d.node("v3", 2, 2, "Risk flag?", kind="dec")
    d.node("v4", 2, 1, "Human review queue (SLA by tier); sample re-verification", rail="T")
    d.node("v5", 3, 2, "Clear: auto-approve tier; caps applied", rail="L")
    d.node("v6", 3, 1, "Decision?", kind="dec")
    d.node("v8", 3, 0, "More info: reason in local language; applicant resubmits", rail="X")
    d.node("v7", 4, 1, "Approve: issue QR + entity code", rail="G")
    d.node("v9", 5, 1, "Active entity: tier, caps, reputation start", kind="term")
    d.edge("v1", "v2", "b", "l", label="submit")
    d.edge("v2", "v3")
    d.edge("v3", "v4", "t", "b", label="Flag")
    d.edge("v3", "v5", label="Clear")
    d.edge("v4", "v6")
    d.edge("v6", "v8", "t", "b", label="More info")
    d.edge("v6", "v7", label="Approve")
    d.edge("v5", "v9", "r", "b")
    d.edge("v7", "v9")
    return d.render(p("11_verifier.png"))


# ---------------------------------------------------------------- special flows
def d_direct_sale():
    d = Diagram("Special flow: farmer sells directly to a retailer",
                "The case the current build makes awkward: no pre-linking, same-day money, full evidence.",
                lanes3("Farmer", "Platform", "Retailer"), 7)
    d.node("f1", 0, 0, "Lot ready; farmer opens SELL and picks Direct", rail="G")
    d.node("f3", 1, 0, "Scan retailer QR; terms prefilled from mandi band + risk rule", rail="G")
    d.node("f4", 1, 1, "Unknown retailer: provisional T0 account by OTP; cash/UPI on delivery enforced", rail="T")
    d.node("f5", 2, 0, "Sign token (offline OK)", rail="L")
    d.node("f6", 3, 2, "Retailer scans, weighs, inspects, countersigns", rail="G")
    d.node("f7", 4, 1, "Split-pay: UPI link for full value now; dispute only the rejected part", rail="M")
    d.node("f8", 4, 2, "Retailer pays by UPI or cash; farmer confirms", rail="M")
    d.node("f9", 5, 0, "Title moves on payment; retailer gets consumer QR labels", rail="L")
    d.node("f10", 6, 0, "Farmer paid same day; score + credit passport updated", kind="term")
    d.edge("f1", "f3")
    d.edge("f3", "f4", "b", "t", label="if new")
    d.edge("f4", "f5", "r", "b", b_dx=-45)
    d.edge("f5", "f6", "b", "t", a_dx=45, label="goods + token")
    d.edge("f6", "f7", "r", "l", label="sync")
    d.edge("f7", "f8", "b", "t")
    d.edge("f8", "f9", "r", "b")
    d.edge("f9", "f10")
    return d.render(p("12_direct_sale.png"))


def d_overdue():
    d = Diagram("Special flow: payment overdue escalation ladder",
                "Pressure rises automatically; the farmer never has to chase alone.",
                lanes3("Buyer", "Platform", "Seller (farmer)"), 7, lane_h=240)
    items = [
        "Due date D fixed at trade (cash, UPI, T+1, T+3 or credit)",
        "D-1: reminder to buyer",
        "D+0: overdue flag; farmer notified",
        "D+2: mediation case opens automatically",
        "D+7: buyer limited to cash terms; warning shown to farmers",
        "D+15: formal notice pack (ledger extract + acknowledgement of debt)",
        "D+30: network default flag (buyer can contest)",
    ]
    rails = ["L", "M", "T", "T", "T", "L", "T"]
    for i, t in enumerate(items):
        d.node(f"t{i}", i, 1, t, rail=rails[i])
        if i:
            d.edge(f"t{i-1}", f"t{i}")
    d.node("b0", 1, 0, "Buyer pays at any point: ladder stops, score updates", rail="M")
    d.edge("b0", "t1", "b", "t", dash=True, label="paid")
    d.node("s0", 2, 2, "One tap: confirm payment or raise issue", rail="X")
    d.node("s1", 3, 2, "Mediator contacts both parties (48 h SLA)", rail="T")
    d.node("s2", 5, 2, "Seller may use pack for APMC / legal / ODR", rail="X")
    d.edge("t2", "s0", "b", "t", label="notify")
    d.edge("t3", "s1", "b", "t")
    d.edge("t5", "s2", "b", "t")
    return d.render(p("13_overdue_ladder.png"))


def d_dispute():
    d = Diagram("Special flow: dispute resolution ladder",
                "Cheapest, fastest fix first; every level has a clock and writes an outcome to the ledger.",
                lanes3("Parties", "Platform", "Mediator / authority"), 7)
    d.node("d1", 0, 0, "Rejection or shortfall recorded with evidence", rail="T")
    d.node("d2", 1, 1, "Level 0 rules: tolerance, split-pay, rejection-anomaly check", rail="L")
    d.node("d3", 2, 1, "Accept computed result?", kind="dec")
    d.node("e1", 2, 2, "Closed: ledger event + scores", kind="term")
    d.node("d4", 2, 0, "Level 1: in-app counter-offer (24 h): re-price, return or split", rail="T")
    d.node("d5", 3, 0, "Agreed?", kind="dec")
    d.node("e2", 4, 0, "Closed: ledger event + scores", kind="term")
    d.node("d6", 3, 1, "Evidence pack auto-built: slips, photos, geo, timeline", rail="L")
    d.node("d7", 4, 2, "Level 2: FPO / mandi mediator proposes (48 h SLA)", rail="T")
    d.node("d8", 5, 2, "Parties accept?", kind="dec")
    d.node("d9", 5, 1, "Level 3: APMC grievance cell / ODR partner; pack exported", rail="T")
    d.node("d10", 6, 1, "Closed: ledger event + scores", kind="term")
    d.edge("d1", "d2", "r", "t")
    d.edge("d2", "d3")
    d.edge("d3", "e1", "b", "t", label="Yes")
    d.edge("d3", "d4", "t", "b", label="No")
    d.edge("d4", "d5")
    d.edge("d5", "e2", label="Yes")
    d.edge("d5", "d6", "b", "t", label="No")
    d.edge("d6", "d7", "r", "t")
    d.edge("d7", "d8")
    d.edge("d8", "d9", "t", "b", label="No")
    d.edge("d9", "d10")
    d.edge("d8", "d10", "r", "b", label="Yes")
    return d.render(p("14_dispute_ladder.png"))


def d_data_model():
    d = Diagram("Data model: what is new and how it connects",
                "Existing tables stay; the new objects wrap them so money and evidence sit next to goods.",
                [("Identity", L0), ("Goods", "#E9F4EE"), ("Money", "#FBF4E8"), ("Trust", L1)], 4, cw=330, lane_h=190)
    d.node("e1", 0, 0, "Entity (role, tier, consent)", rail="X")
    d.node("e2", 1, 0, "Delegate grant (agent acts for farmer)", rail="X")
    d.node("e3", 2, 0, "Device key (signs offline tokens)", rail="X")
    d.node("g1", 0, 1, "Lot (owner, custodian, origin claims)", rail="G")
    d.node("g2", 1, 1, "Lot edge (split, merge, sort)", rail="G")
    d.node("g3", 2, 1, "Trace event (hash chained, append-only)", rail="L")
    d.node("g4", 3, 1, "Handover token (one-time nonce)", rail="G")
    d.node("m1", 0, 2, "Trade (price, terms, state)", rail="M")
    d.node("m2", 1, 2, "Trade line items (base, premium, deductions)", rail="M")
    d.node("m3", 2, 2, "Payment (amount, method, UTR, proof)", rail="M")
    d.node("m4", 3, 2, "Account-sale statement", rail="M")
    d.node("t1", 0, 3, "Weigh slip (both sides)", rail="T")
    d.node("t2", 1, 3, "Evidence (photo, geo, lab)", rail="T")
    d.node("t3", 2, 3, "Case (level, SLA, outcome)", rail="T")
    d.node("t4", 3, 3, "Score snapshot (trust, pay, quality)", rail="T")
    d.edge("e2", "e1", "l", "r", label="acts for")
    d.edge("e1", "g1", "b", "t", label="owns / holds")
    d.edge("g1", "g2")
    d.edge("g2", "g3")
    d.edge("e3", "g4", "b", "t", label="signs")
    d.edge("g1", "m1", "b", "t", a_dx=40, b_dx=40, label="sold via")
    d.edge("m1", "m2")
    d.edge("m2", "m3")
    d.edge("m3", "m4")
    d.edge("m1", "t1", "b", "t", label="delivered with")
    d.edge("t1", "t2")
    d.edge("t2", "t3")
    d.edge("t3", "t4")
    return d.render(p("15_data_model.png"))


def d_roadmap():
    d = Diagram("Roadmap: four phases, each shippable on its own",
                "Durations are indicative and must be re-estimated after the pilot design review.",
                [("Phase 0\nBuilt", "#EEF2F6"), ("Phase 1\nMoney rail\n6-8 weeks", "#FBF4E8"),
                 ("Phase 2\nField rail\n8-10 weeks", "#E9F4EE"), ("Phase 3\nValue rail\n10-12 weeks", "#EAF0F6")],
                6, cw=300, lane_h=185, font=22)
    data = [
        ("L", ["Hash-chained ledger + daily anchor", "Lots, split / merge / sort", "5 roles, 11 languages",
               "OTP + passkey, encrypted PII", "Handover, tolerance, alerts", "Public QR page"]),
        ("M", ["Trade object + payment terms", "Title vs custody split", "UPI link + UTR + cash OTP receipt",
               "Split-pay + dual weigh slips", "Open handshake, no pre-link", "Pay-Score v0 + overdue ladder"]),
        ("G", ["Offline signed tokens", "Assisted entry + delegates", "IVR / WhatsApp / voice",
               "Account-sale for mandis", "Dispute ladder + mediators", "Carrier telemetry + loss rules"]),
        ("T", ["PSP auto-reconcile", "Credit passport (Account Aggregator)", "Insurance evidence pack",
               "Price board + offers", "ONDC / eNAM adapters", "Verified-origin premium"]),
    ]
    for lane, (rail, items) in enumerate(data):
        for c, t in enumerate(items):
            d.node(f"p{lane}{c}", c, lane, t, rail=rail)
    for lane in range(3):
        d.edge(f"p{lane}0", f"p{lane+1}0", "b", "t", dash=True)
    return d.render(p("16_roadmap.png"))


def build_all():
    fns = [d_four_rails, d_layers, d_trade_states, d_handshake, d_producer, d_aggregator, d_wholesaler,
           d_carrier, d_retailer, d_consumer, d_verifier, d_direct_sale, d_overdue, d_dispute, d_data_model, d_roadmap]
    for fn in fns:
        print("rendered", fn())


if __name__ == "__main__":
    build_all()
