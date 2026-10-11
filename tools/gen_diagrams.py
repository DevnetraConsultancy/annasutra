#!/usr/bin/env python3
"""Generates every diagram in assets/diagrams as SVG + PNG.
Run:  pip install cairosvg  &&  python tools/gen_diagrams.py
Edit the diagram definitions at the bottom, rerun, and commit the outputs."""
import os
from xml.sax.saxutils import escape

try:
    import cairosvg
except ImportError:
    cairosvg = None

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "diagrams")
os.makedirs(OUT, exist_ok=True)

COL = {  # fill, stroke, title text, sub text
    "teal": ("#E1F5EE", "#0F6E56", "#085041", "#0F6E56"),
    "purple": ("#EEEDFE", "#534AB7", "#3C3489", "#534AB7"),
    "coral": ("#FAECE7", "#993C1D", "#712B13", "#993C1D"),
    "gray": ("#F1EFE8", "#5F5E5A", "#2C2C2A", "#5F5E5A"),
    "blue": ("#E6F1FB", "#185FA5", "#0C447C", "#185FA5"),
}
FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"
INK = "#444441"


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.title, self.parts = w, h, title, []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=12, anchor="middle", weight=400, fill=INK):
        self.add(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
                 f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{escape(s)}</text>')

    def heading(self, s):
        self.text(20, 26, s, size=15, anchor="start", weight=700, fill="#2C2C2A")

    def box(self, x, y, w, h, title, sub=None, color="teal", dashed=False):
        fill, stroke, tc, sc = COL[color]
        subs = [] if sub is None else ([sub] if isinstance(sub, str) else list(sub))
        if len(title) * 8.4 > w - 14:
            print(f"  WARN title may overflow: {title!r} in w={w}")
        for t in subs:
            if len(t) * 6.6 > w - 14:
                print(f"  WARN sub may overflow: {t!r} in w={w}")
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="1.2"{dash}/>')
        cx = x + w / 2
        if not subs:
            self.text(cx, y + h / 2 + 5, title, 13, weight=700, fill=tc)
        else:
            block = 16 + 16 * len(subs)
            ty = y + (h - block) / 2 + 13
            self.text(cx, ty, title, 13, weight=700, fill=tc)
            for i, t in enumerate(subs):
                self.text(cx, ty + 18 + 16 * i, t, 11, fill=sc)

    def diamond(self, cx, cy, w, h, label):
        pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
        self.add(f'<polygon points="{pts}" fill="#FFFFFF" stroke="#5F5E5A" stroke-width="1.2"/>')
        if len(label) * 8.4 > w * 0.78:
            print(f"  WARN diamond label may overflow: {label!r}")
        self.text(cx, cy + 5, label, 13, weight=700, fill="#2C2C2A")

    def arrow(self, pts, label=None, lx=None, ly=None, anchor="start"):
        d = "M" + " L".join(f"{x} {y}" for x, y in pts)
        self.add(f'<path d="{d}" fill="none" stroke="#5F5E5A" stroke-width="1.4" marker-end="url(#ah)"/>')
        if label:
            self.text(lx, ly, label, 11, anchor=anchor, fill="#5F5E5A")

    def line(self, x1, y1, x2, y2):
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#B4B2A9" '
                 f'stroke-width="1" stroke-dasharray="5 4"/>')

    def save(self, name):
        defs = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
                'markerHeight="7" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="#5F5E5A" '
                'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}" role="img"><title>{escape(self.title)}</title>{defs}'
               f'<rect width="100%" height="100%" fill="#FFFFFF"/>' + "".join(self.parts) + "</svg>")
        base = os.path.join(OUT, name)
        with open(base + ".svg", "w", encoding="utf-8") as f:
            f.write(svg)
        if cairosvg:
            cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=base + ".png", scale=2)
        print("wrote", name)


def vflow(name, title, steps, W=730, y0=60, main_w=300):
    """steps: ('box', title, sub, color) or ('dec', label, side) with side=(title, sub, color, merge)."""
    gap, cx = 32, W / 2
    items, y = [], y0
    for st in steps:
        if st[0] == "box":
            subs = [] if st[2] is None else ([st[2]] if isinstance(st[2], str) else st[2])
            h = 44 if not subs else 22 + 16 * len(subs) + 14
            items.append((st, y, h))
        else:
            h = 84
            items.append((st, y, h))
        y += h + gap
    s = Svg(W, y - gap + 36, title)
    s.heading(title)
    prev = None
    for i, (st, y, h) in enumerate(items):
        if prev is not None:
            s.arrow([(cx, prev[1] + prev[2]), (cx, y - 3)])
            pst = prev[0]
            if pst[0] == "dec":
                s.text(cx + 8, y - 12, "Yes", 11, anchor="start", fill="#5F5E5A")
        if st[0] == "box":
            s.box(cx - main_w / 2, y, main_w, h, st[1], st[2], st[3])
        else:
            dw = max(250, int(len(st[1]) * 8.4 / 0.74))
            s.diamond(cx, y + h / 2, dw, h, st[1])
            side = st[2]
            if side:
                sx, sw = cx + dw / 2 + 36, 160
                sh = 44 if not side[1] else 58
                s.arrow([(cx + dw / 2, y + h / 2), (sx - 3, y + h / 2)], "No", cx + dw / 2 + 18, y + h / 2 - 8, "middle")
                s.box(sx, y + h / 2 - sh / 2, sw, sh, side[0], side[1], side[2])
                if len(side) > 3 and side[3] and i + 1 < len(items):
                    nxt = items[i + 1]
                    ncy = nxt[1] + nxt[2] / 2
                    s.arrow([(sx + sw / 2, y + h / 2 + sh / 2), (sx + sw / 2, ncy), (cx + main_w / 2 + 3, ncy)])
        prev = (st, y, h)
    s.save(name)


# ---------------------------------------------------------------- diagrams
def d_overview():
    W, H = 1060, 250
    s = Svg(W, H, "AnnaSutra supply chain overview")
    s.heading("Supply chain: every holder approves the next one, every step is recorded forever")
    names = [("1 Farmer", ["Creates batch", "Makes the QR"], "teal"),
             ("2 Aggregator", ["Scan, weigh,", "check quality"], "teal"),
             ("3 Wholesaler", ["Grade, split to", "buyers"], "teal"),
             ("4 Distributor", ["Transport,", "split, deliver"], "teal"),
             ("5 Retailer", ["Shelf QR,", "sales, waste"], "teal"),
             ("6 Consumer", ["Scans shelf QR,", "reads summary"], "purple")]
    x, bw, gp = 20, 150, 20
    for i, (t, sub, c) in enumerate(names):
        s.box(x, 70, bw, 84, t, sub, c)
        if i < len(names) - 1:
            s.arrow([(x + bw + 2, 112), (x + bw + gp - 3, 112)])
        x += bw + gp
    s.text(W / 2, 190, "Each handover: sender approves the receiver, receiver confirms with biometric or PIN, custody moves.",
           12, fill="#5F5E5A")
    s.text(W / 2, 212, "The consumer can only read a short, safe summary. Nobody can edit old records.", 12, fill="#5F5E5A")
    s.save("01_supply_chain_overview")


def d_architecture():
    W, H = 760, 700
    s = Svg(W, H, "AnnaSutra system architecture")
    s.heading("System architecture")
    s.box(30, 50, 220, 56, "AnnaSutra team", "Verify, review alerts", "gray")
    s.box(270, 50, 220, 56, "Farmers, middlemen", "Flutter app: Android + iOS", "gray")
    s.box(510, 50, 220, 56, "Consumer", "Phone camera, browser", "purple")
    for cx in (140, 380, 620):
        s.arrow([(cx, 106), (cx, 136)])
    s.box(30, 140, 700, 56, "Cloudflare edge", "Bot check, firewall, rate limits, TLS", "coral")
    for cx in (140, 380, 620):
        s.arrow([(cx, 196), (cx, 226)])
    s.box(30, 230, 220, 56, "Admin site", "Extra login + hardware key", "teal")
    s.box(270, 230, 220, 56, "App API", "All rules, only writer", "teal")
    s.box(510, 230, 220, 56, "Public page", "Reads summary only", "purple")
    s.arrow([(250, 258), (266, 258)])
    s.box(30, 330, 220, 56, "File storage", "Photos, certificates", "teal")
    s.box(270, 330, 220, 56, "PostgreSQL", "History, never edited", "teal")
    s.arrow([(310, 286), (310, 308), (140, 308), (140, 326)])
    s.arrow([(380, 286), (380, 326)])
    s.arrow([(620, 286), (620, 358), (494, 358)])
    s.box(270, 430, 220, 56, "Background worker", "Alerts, checks, SMS", "teal")
    s.arrow([(380, 386), (380, 426)])
    s.add('<rect x="20" y="520" width="720" height="150" rx="12" fill="#FFFFFF" stroke="#B4B2A9" '
          'stroke-width="1.2" stroke-dasharray="6 4"/>')
    s.text(380, 546, "Safety nets", 13, weight=700, fill="#2C2C2A")
    s.arrow([(380, 486), (380, 516)])
    for i, (t, sub) in enumerate([("Backups", "Separate account"), ("Tamper check", "Daily external copy"),
                                  ("Logs in India", "Kept 180 days"), ("Monitoring", "Alerts to on-call")]):
        s.box(40 + i * 182, 572, 148, 60, t, sub, "coral")
    s.save("02_system_architecture")


def d_mobile():
    W, H = 680, 620
    s = Svg(W, H, "Mobile app layers")
    s.heading("Flutter app layers (Android and iOS)")
    s.box(190, 60, 300, 56, "Screens", "Farmer, receive, dispatch, history", "teal")
    s.box(520, 60, 140, 56, "QR scanner", "Camera", "gray")
    s.arrow([(520, 88), (494, 88)])
    s.arrow([(340, 116), (340, 144)])
    s.box(190, 148, 300, 56, "State and logic", "Riverpod providers + use cases", "teal")
    s.arrow([(340, 204), (340, 232)])
    s.box(190, 236, 300, 56, "Repositories", "One per feature, offline first", "teal")
    for cx in (135, 545):
        s.arrow([(340, 292), (340, 312), (cx, 312), (cx, 336)])
    s.arrow([(340, 292), (340, 336)])
    s.box(40, 340, 190, 64, "Encrypted local DB", ["Drift + SQLCipher", "events, outbox"], "teal")
    s.box(245, 340, 190, 64, "Sync worker", ["Sends outbox,", "retries safely"], "teal")
    s.box(450, 340, 190, 64, "Secure keys", ["Keystore / Keychain", "signing + DB key"], "coral")
    s.arrow([(340, 404), (340, 446)])
    s.box(245, 450, 190, 56, "API client", "HTTPS, idempotency key", "teal")
    s.arrow([(340, 506), (340, 540)])
    s.box(245, 544, 190, 56, "AnnaSutra API", "Server decides", "purple")
    s.save("03_mobile_app_layers")


def d_security():
    W = 680
    layers = [("1. Edge", "Cloudflare: bot checks, firewall, rate limits", "coral"),
              ("2. Identity", "SMS code, passkey or device key, no passwords", "teal"),
              ("3. Sessions and devices", "Short sessions, revoke a lost phone", "teal"),
              ("4. Access control", "Organisation-scoped checks + database row security", "teal"),
              ("5. Data protection", "Encrypted in transit and at rest, field-level keys", "teal"),
              ("6. Integrity", "Append-only events, hash chain, daily external copy", "coral"),
              ("7. Operations", "Logs in India 180 days, alerts, 6-hour incident clock", "coral"),
              ("8. People and process", "Two-party confirmation, audits, training", "gray")]
    s = Svg(W, 60 + len(layers) * 66 + 20, "Security layers")
    s.heading("Eight security layers: defence in depth")
    for i, (t, sub, c) in enumerate(layers):
        s.box(60, 50 + i * 66, 560, 52, t, sub, c)
    s.save("11_security_layers")


def d_state():
    W, H = 760, 470
    s = Svg(W, H, "Lot state machine")
    s.heading("Batch (lot) states")
    s.box(40, 70, 140, 50, "Created", None, "gray")
    s.box(270, 70, 140, 50, "In transit", None, "teal")
    s.box(500, 70, 140, 50, "In custody", None, "teal")
    s.arrow([(180, 95), (266, 95)], "dispatch", 223, 86, "middle")
    s.arrow([(410, 95), (496, 95)], "receive", 453, 86, "middle")
    s.arrow([(570, 70), (570, 44), (340, 44), (340, 66)], "dispatch onward", 455, 38, "middle")
    s.box(270, 210, 140, 50, "Disputed", None, "coral")
    s.arrow([(340, 120), (340, 206)], "numbers differ", 352, 168)
    s.arrow([(410, 235), (520, 235), (520, 124)], "resolved", 465, 227, "middle")
    s.box(500, 340, 140, 50, "Closed", None, "purple")
    s.arrow([(610, 120), (610, 336)], "split, sold, empty", 620, 230)
    s.box(40, 340, 400, 62, "In transit too long", ["Handover expires, gap flagged,", "last holder stays responsible"], "gray", dashed=True)
    s.box(40, 416, 400, 44, "Recalled", None, "gray", dashed=True)
    s.text(450, 443, "can be set on any state; holders notified; history kept", 11, anchor="start", fill="#5F5E5A")
    s.save("08_lot_state_machine")


def d_phases():
    W, H = 1060, 230
    s = Svg(W, H, "Delivery phases")
    s.heading("Delivery phases")
    ph = [("P0 Foundation", ["Repo, CI, API contract", "Backend skeleton", "Design system"]),
          ("P1 Identity + batch", ["Login, verification", "Create batch", "Bind QR sticker"]),
          ("P2 Handover chain", ["Dispatch, receive", "Disputes, gaps", "Offline sync"]),
          ("P3 Genealogy", ["Split, merge, sort", "Inspections, photos", "Recall, alerts"]),
          ("P4 Pilot ready", ["Penetration test", "Restore drill", "Store release"])]
    x = 20
    for i, (t, sub) in enumerate(ph):
        s.box(x, 60, 188, 104, t, sub, "teal" if i < 4 else "purple")
        if i < len(ph) - 1:
            s.arrow([(x + 190, 112), (x + 205, 112)])
        x += 208
    s.text(W / 2, 200, "Each phase ends with: tests pass, human review done, demo on a real low-cost phone.", 12, fill="#5F5E5A")
    s.save("12_delivery_phases")


def d_consumer_admin():
    W, H = 680, 740
    s = Svg(W, H, "Consumer and admin flows")
    s.heading("Consumer and admin flows")
    cx = 340
    s.box(190, 56, 300, 44, "Consumer scans shelf QR", None, "purple")
    s.arrow([(cx, 100), (cx, 130)])
    s.box(190, 134, 300, 44, "Public page checks the code", None, "purple")
    s.arrow([(cx, 178), (cx, 208)])
    s.diamond(cx, 250, 250, 84, "Code registered?")
    s.arrow([(465, 250), (501, 250)], "No", 483, 242, "middle")
    s.box(504, 228, 160, 44, "Generic not found", None, "gray")
    s.arrow([(cx, 292), (cx, 326)])
    s.text(cx + 8, 314, "Yes", 11, anchor="start", fill="#5F5E5A")
    s.box(190, 330, 300, 58, "Show short summary", "Stages, checks, region", "purple")
    s.line(40, 414, 640, 414)
    s.text(40, 408, "Admin team", 11, anchor="start", fill="#5F5E5A")
    s.box(190, 430, 300, 58, "Admin logs in", "Extra login + hardware key", "teal")
    s.arrow([(cx, 488), (cx, 512)])
    s.box(190, 516, 300, 44, "Pick a task from the queue", None, "teal")
    xs = [110, 263, 416, 569]
    for x in xs:
        s.arrow([(cx, 560), (cx, 576), (x, 576), (x, 592)])
    for x, t in zip(xs, ["Verify business", "Review alerts", "Issue QR blocks", "Open a recall"]):
        s.box(x - 70, 596, 140, 44, t, None, "teal")
        s.arrow([(x, 640), (x, 668)])
    s.box(40, 672, 600, 44, "Every admin action is logged; history cannot be edited", None, "gray")
    s.save("07_flow_consumer_admin")


def build():
    d_overview()
    d_architecture()
    d_mobile()
    vflow("04_flow_master", "Master flow: every user, every scan", [
        ("box", "Open AnnaSutra", None, "gray"),
        ("dec", "Logged in?", ("Join once", "SMS + secure login", "gray", False)),
        ("dec", "Business verified?", ("Wait", "Team checks you", "gray", False)),
        ("box", "Scan the batch QR", None, "teal"),
        ("dec", "Holder or named receiver?", ("Read only", "Scan is logged", "gray", False)),
        ("box", "Do the allowed action", "Receive, dispatch, inspect, sell", "teal"),
        ("box", "Saved forever, cannot be edited", None, "purple"),
    ])
    vflow("05_flow_farmer", "Farmer flow: create batch and hand over", [
        ("box", "Farmer opens Create batch", None, "gray"),
        ("box", "Enter crop and land details", None, "teal"),
        ("box", "Weigh and add photos", None, "teal"),
        ("box", "Scan a blank QR sticker", None, "teal"),
        ("dec", "Sticker unused?", ("Pick another", None, "gray", False)),
        ("box", "Batch created: ID + QR bound", None, "teal"),
        ("box", "Pick the next receiver", None, "teal"),
        ("box", "Approve with biometric or PIN", None, "teal"),
        ("dec", "Receiver confirms?", ("Gap flagged", "Sender responsible", "gray", False)),
        ("box", "Custody moves to receiver", None, "purple"),
    ])
    vflow("06_flow_middleman", "Middleman flow: receive, confirm, next step", [
        ("box", "Batch arrives: scan the QR", None, "gray"),
        ("dec", "Named receiver?", ("Blocked, logged", None, "gray", False)),
        ("box", "Weigh and inspect", None, "teal"),
        ("box", "Enter quantity received", None, "teal"),
        ("dec", "Within allowed difference?", ("Flag difference", "Both numbers saved", "gray", True)),
        ("box", "Confirm with biometric or PIN", None, "teal"),
        ("box", "Custody moves to you", None, "teal"),
        ("box", "Choose next step", ["Sort or grade, split, merge, store", "Waste or spoilage, retail sale"], "teal"),
        ("box", "Dispatch: next holder repeats this", None, "purple"),
    ])
    d_consumer_admin()
    d_state()
    vflow("09_qr_lifecycle", "QR label lifecycle", [
        ("box", "Admin issues serial block", "To a verified business", "coral"),
        ("box", "Serial status: ISSUED", None, "gray"),
        ("box", "User scans blank sticker", "and creates a batch", "teal"),
        ("dec", "Serial unused?", ("Reject", "Pick another", "gray", False)),
        ("box", "Serial BOUND to the batch", None, "teal"),
        ("box", "Same QR stays on the batch", "Dispatch, receive, store, repack", "teal"),
        ("dec", "Label intact?", ("Reissue", "Void old, bind new", "gray", False)),
        ("dec", "Lot kept whole?", ("New QR each lot", "Linked to parents", "gray", False)),
        ("box", "Shelf QR points to retail lot", "Public page shows summary", "purple"),
    ])
    vflow("10_offline_sync", "Offline-first sync", [
        ("box", "User does an action", None, "gray"),
        ("box", "Save event + outbox row", "One local transaction", "teal"),
        ("dec", "Online?", ("Wait, retry", "Backoff, no data loss", "gray", False)),
        ("box", "Send with event ID", "Resending is safe", "teal"),
        ("dec", "Server accepts?", ("Needs attention", "Shown to user", "gray", False)),
        ("box", "Mark synced", "Update local view", "purple"),
    ])
    d_security()
    d_phases()


if __name__ == "__main__":
    build()
