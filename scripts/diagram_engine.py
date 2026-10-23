"""Tiny swimlane / block-diagram renderer built on Pillow.

Why not matplotlib/graphviz: neither is installed in the project venv and the
documentation tooling must stay dependency-light. Pillow is already present.

Conventions
- Pure ASCII text only (no emoji, no special glyphs) so nothing renders as boxes.
- Supersampled x3 then downsampled for smooth edges.
- Node "rail" colours: G goods, M money, T trust/check, L ledger write, X neutral.
- Decisions are purple diamonds, start/end are dark-green pills.
"""

import os
from PIL import Image, ImageDraw, ImageFont

S = 3  # supersample factor
OUT_SCALE = 2  # final pixels per nominal pixel
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

RAIL = {
    "G": ("#0B3D2E", "#E8F5EE"),
    "M": ("#C2670A", "#FFF0D4"),
    "T": ("#1D4ED8", "#E6EEFF"),
    "L": ("#475569", "#E8EDF3"),
    "X": ("#64748B", "#FFFFFF"),
}
DEC = ("#6D28D9", "#F1EAFE")
TERM_FILL = "#0B3D2E"
LINE = "#334155"

LEGEND = [
    ("G", "Goods / custody event"),
    ("M", "Money event"),
    ("T", "Trust / evidence / check"),
    ("L", "Ledger / system write"),
    ("D", "Decision"),
]


def _font(path, size):
    return ImageFont.truetype(path, int(size * S))


class Diagram:
    def __init__(self, title, subtitle, lanes, ncols, cw=300, lane_h=235,
                 label_w=150, font=23, legend=True):
        self.title = title
        self.subtitle = subtitle
        self.lanes = lanes  # list of (name, hex fill)
        self.ncols = ncols
        self.cw = cw
        self.lane_h = lane_h
        self.label_w = label_w
        self.fs = font
        self.lh = int(font * 1.28)
        self.top = 118
        self.legend = legend
        self.W = int(label_w + ncols * cw + 30)
        self.H = int(self.top + len(lanes) * lane_h + (80 if legend else 25))
        self.nodes = {}
        self.edges = []
        self._m = ImageDraw.Draw(Image.new("RGB", (4, 4)))
        self.f_reg = _font(FONT_REG, font)
        self.f_bold = _font(FONT_BOLD, font)

    # ---------- geometry ----------
    def pt(self, col, lane, dx=0, dy=0):
        return (self.label_w + col * self.cw + self.cw / 2 + dx,
                self.top + lane * self.lane_h + self.lane_h / 2 + dy)

    def _wrap(self, text, maxw, font):
        lines = []
        for para in text.split("\n"):
            words = para.split()
            cur = ""
            for w in words:
                t = (cur + " " + w).strip()
                if self._m.textlength(t, font=font) / S <= maxw or not cur:
                    cur = t
                else:
                    lines.append(cur)
                    cur = w
            lines.append(cur)
        return lines

    def node(self, nid, col, lane, text, kind="proc", rail="X", w=None, h=None,
             dx=0, dy=0, bold_first=False):
        cx, cy = self.pt(col, lane, dx, dy)
        if kind == "dec":
            w = w or (self.cw - 60)
            lines = self._wrap(text, w * 0.56, self.f_reg)
            h = h or max(150, len(lines) * self.lh + 78)
        elif kind == "term":
            w = w or (self.cw - 40)
            lines = self._wrap(text, w - 80, self.f_bold)
            h = h or max(72, len(lines) * self.lh + 28)
        else:
            w = w or (self.cw - 70)
            lines = self._wrap(text, w - 30, self.f_reg)
            h = h or max(92, len(lines) * self.lh + 30)
        self.nodes[nid] = dict(cx=cx, cy=cy, w=w, h=h, kind=kind, rail=rail,
                               lines=lines, bold_first=bold_first)

    def edge(self, a, b, a_side="r", b_side="l", label=None, dash=False,
             via=None, a_dx=0, b_dx=0, lpt=None, color=None):
        self.edges.append(dict(a=a, b=b, a_side=a_side, b_side=b_side,
                               label=label, dash=dash, via=via, a_dx=a_dx,
                               b_dx=b_dx, lpt=lpt, color=color))

    def _anchor(self, nid, side, dx=0):
        n = self.nodes[nid]
        if side == "t":
            return (n["cx"] + dx, n["cy"] - n["h"] / 2)
        if side == "b":
            return (n["cx"] + dx, n["cy"] + n["h"] / 2)
        if side == "l":
            return (n["cx"] - n["w"] / 2, n["cy"] + dx)
        return (n["cx"] + n["w"] / 2, n["cy"] + dx)

    def _route(self, e):
        p0 = self._anchor(e["a"], e["a_side"], e["a_dx"])
        p1 = self._anchor(e["b"], e["b_side"], e["b_dx"])
        s0, s1 = e["a_side"], e["b_side"]
        if e["via"]:
            return [p0] + list(e["via"]) + [p1]
        V, H = ("t", "b"), ("l", "r")
        if s0 in V and s1 in V:
            if abs(p0[0] - p1[0]) < 1:
                return [p0, p1]
            ym = (p0[1] + p1[1]) / 2
            return [p0, (p0[0], ym), (p1[0], ym), p1]
        if s0 in H and s1 in H:
            if abs(p0[1] - p1[1]) < 1:
                return [p0, p1]
            xm = (p0[0] + p1[0]) / 2
            return [p0, (xm, p0[1]), (xm, p1[1]), p1]
        if s0 in V and s1 in H:
            return [p0, (p0[0], p1[1]), p1]
        return [p0, (p1[0], p0[1]), p1]

    # ---------- drawing ----------
    def _sc(self, p):
        return (p[0] * S, p[1] * S)

    def _dashed(self, d, p, q, color, width):
        import math
        x0, y0 = p
        x1, y1 = q
        L = math.hypot(x1 - x0, y1 - y0)
        if L == 0:
            return
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        pos, on = 0.0, True
        dash, gap = 16 * S, 10 * S
        while pos < L:
            seg = dash if on else gap
            end = min(pos + seg, L)
            if on:
                d.line([(x0 + ux * pos, y0 + uy * pos), (x0 + ux * end, y0 + uy * end)],
                       fill=color, width=width)
            pos = end
            on = not on

    def _arrow(self, d, pts, dash=False, color=None):
        import math
        color = color or LINE
        pts = [self._sc(p) for p in pts]
        width = 3 * S
        head = 17 * S
        x0, y0 = pts[-2]
        x1, y1 = pts[-1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        end = (x1 - ux * head * 0.8, y1 - uy * head * 0.8)
        line_pts = pts[:-1] + [end]
        for i in range(len(line_pts) - 1):
            if dash:
                self._dashed(d, line_pts[i], line_pts[i + 1], color, width)
            else:
                d.line([line_pts[i], line_pts[i + 1]], fill=color, width=width)
        # joints for solid lines
        if not dash:
            for p in line_pts[1:-1]:
                d.ellipse([p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2], fill=color)
        px, py = -uy, ux
        hw = 8.5 * S
        tip = (x1, y1)
        base = (x1 - ux * head, y1 - uy * head)
        d.polygon([tip, (base[0] + px * hw, base[1] + py * hw), (base[0] - px * hw, base[1] - py * hw)], fill=color)

    def _label(self, d, text, p):
        f = _font(FONT_BOLD, self.fs - 5)
        tw = self._m.textlength(text, font=f)
        th = (self.fs - 5) * S * 1.2
        x, y = p[0] * S, p[1] * S
        pad = 6 * S
        box = [x - tw / 2 - pad, y - th / 2 - pad / 2, x + tw / 2 + pad, y + th / 2 + pad / 2]
        d.rounded_rectangle(box, radius=8 * S, fill="#FFFFFF", outline="#CBD5E1", width=S)
        d.text((x, y), text, font=f, fill="#0F172A", anchor="mm")

    def _draw_node(self, d, n):
        cx, cy, w, h = n["cx"] * S, n["cy"] * S, n["w"] * S, n["h"] * S
        box = [cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]
        if n["kind"] == "dec":
            border, fill = DEC
            poly = [(cx, cy - h / 2), (cx + w / 2, cy), (cx, cy + h / 2), (cx - w / 2, cy)]
            d.polygon(poly, fill=fill)
            d.line(poly + [poly[0]], fill=border, width=3 * S, joint="curve")
            tcol, font = "#2E1065", self.f_reg
        elif n["kind"] == "term":
            d.rounded_rectangle(box, radius=min(h / 2, 38 * S), fill=TERM_FILL)
            tcol, font = "#FFFFFF", self.f_bold
        else:
            border, fill = RAIL[n["rail"]]
            d.rounded_rectangle(box, radius=14 * S, fill=fill, outline=border, width=3 * S)
            # left accent strip
            d.rounded_rectangle([box[0], box[1], box[0] + 9 * S, box[3]], radius=6 * S, fill=border)
            tcol, font = "#0F172A", self.f_reg
        lines = n["lines"]
        total = len(lines) * self.lh * S
        y = cy - total / 2 + self.lh * S / 2
        for i, ln in enumerate(lines):
            f = self.f_bold if (n["bold_first"] and i == 0) else font
            d.text((cx + (4 * S if n["kind"] == "proc" else 0), y), ln, font=f, fill=tcol, anchor="mm")
            y += self.lh * S

    def render(self, path):
        W, H = self.W * S, self.H * S
        img = Image.new("RGB", (W, H), "#FFFFFF")
        d = ImageDraw.Draw(img)

        # Title block
        d.text((24 * S, 24 * S), self.title, font=_font(FONT_BOLD, 34), fill="#0B3D2E")
        d.text((24 * S, 70 * S), self.subtitle, font=_font(FONT_REG, 21), fill="#64748B")
        d.line([(24 * S, 106 * S), ((self.W - 24) * S, 106 * S)], fill="#E2E8F0", width=2 * S)

        # Lanes
        for i, (name, fill) in enumerate(self.lanes):
            y0 = (self.top + i * self.lane_h) * S
            y1 = (self.top + (i + 1) * self.lane_h) * S
            d.rectangle([0, y0, W, y1], fill=fill)
            d.line([(0, y1), (W, y1)], fill="#CBD5E1", width=2 * S)
            if name:
                d.rectangle([0, y0, self.label_w * S, y1], fill="#0B3D2E")
                lf = _font(FONT_BOLD, self.fs - 4)
                lines = self._wrap(name, self.label_w - 22, lf)
                tot = len(lines) * self.lh * S
                yy = (y0 + y1) / 2 - tot / 2 + self.lh * S / 2
                for ln in lines:
                    d.text((self.label_w * S / 2, yy), ln, font=lf, fill="#FFFFFF", anchor="mm")
                    yy += self.lh * S

        # Edges (under nodes)
        routes = []
        for e in self.edges:
            pts = self._route(e)
            routes.append((e, pts))
            self._arrow(d, pts, dash=e["dash"], color=e["color"])

        for n in self.nodes.values():
            self._draw_node(d, n)

        for e, pts in routes:
            if not e["label"]:
                continue
            if e["lpt"]:
                p = e["lpt"]
            else:
                best, bl = 0, -1
                for i in range(len(pts) - 1):
                    L = abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1])
                    if L > bl:
                        best, bl = i, L
                p = ((pts[best][0] + pts[best + 1][0]) / 2, (pts[best][1] + pts[best + 1][1]) / 2)
                horiz = abs(pts[best + 1][1] - pts[best][1]) < 1
                lf = _font(FONT_BOLD, self.fs - 5)
                tw = self._m.textlength(e["label"], font=lf) / S + 16
                if horiz and bl < tw:
                    mh = max(self.nodes[e["a"]]["h"], self.nodes[e["b"]]["h"])
                    p = (p[0], p[1] - mh / 2 - 22)
            self._label(d, e["label"], p)

        # Legend
        if self.legend:
            y = (self.top + len(self.lanes) * self.lane_h + 40) * S
            x = 28 * S
            lf = _font(FONT_REG, 19)
            for key, text in LEGEND:
                if key == "D":
                    s = 11 * S
                    d.polygon([(x + s, y - s), (x + 2 * s, y), (x + s, y + s), (x, y)], fill=DEC[1], outline=DEC[0])
                else:
                    border, fill = RAIL[key]
                    d.rounded_rectangle([x, y - 11 * S, x + 26 * S, y + 11 * S], radius=5 * S, fill=fill, outline=border, width=2 * S)
                d.text((x + 36 * S, y), text, font=lf, fill="#334155", anchor="lm")
                x += (36 + 24) * S + self._m.textlength(text, font=lf)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        out = img.resize((self.W * OUT_SCALE, self.H * OUT_SCALE), Image.LANCZOS)
        out.save(path, optimize=True)
        return path
