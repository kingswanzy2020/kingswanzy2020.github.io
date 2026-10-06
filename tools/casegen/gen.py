"""Generate case-study pages in the same template as eks/index.html.

Each content module defines PAGE (a dict). Diagrams are drawn with the same
vocabulary as the hand-built pages: coloured node cards with an icon tile,
dashed containers, numbered arrows, a wiring table and a legend.
"""
import html, importlib.util, os, re, sys, glob, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, "..", ".."))
# Images extracted from the NextWork PDFs (pdfimages -png); only needed the first time,
# since the resized copies are committed under <slug>/img/.
PDFIMG = os.environ.get("PDFIMG", os.path.join(HERE, "pdfimg"))
RAW = "https://raw.githubusercontent.com/kingswanzy2020/Projects/main/"

HEAD_LINKS = """<meta name="theme-color" content="#0b1220">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@500;600&display=swap">
<link rel="stylesheet" href="../assets/site.css">"""

BAR = """<div class="bar">
  <div class="wrap">
    <a class="brand" href="../"><span class="avatar sm" aria-hidden="true">AT</span><b>Ahmed Tetteh</b><small>DevOps &middot; Platform &middot; SRE</small></a>
    <nav>
      <a class="back" href="../#work">&larr; All case studies</a>
      <a href="https://github.com/kingswanzy2020">GitHub</a>
      <a href="https://www.linkedin.com/in/ahmed-tetteh-76a538126/">LinkedIn</a>
      <a href="mailto:kingsleyswanzy@gmail.com">Email</a>
    </nav>
  </div>
</div>
"""

MONO = "IBM Plex Mono, ui-monospace, monospace"
SANS = "IBM Plex Sans, system-ui, sans-serif"

NUMW = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]


def esc(s):
    return html.escape(s, quote=False)


# ---------------------------------------------------------------- glyphs
def _st(k):
    return f'fill="none" stroke="var(--c-{k})" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"'


def glyph(name, x, y, k):
    """Draw a small line icon inside the 30x30 tile whose top-left is (x, y)."""
    s = _st(k)
    cx, cy = x + 15, y + 15
    f = f'fill="var(--c-{k})"'
    g = {
        "browser": f'<rect x="{x+6}" y="{y+8}" width="18" height="14" rx="2" {s}/><line x1="{x+6}" y1="{y+12.5}" x2="{x+24}" y2="{y+12.5}" {s}/><circle cx="{x+9}" cy="{y+10.3}" r="0.9" {f}/>',
        "globe": f'<circle cx="{cx}" cy="{cy}" r="8.5" {s}/><ellipse cx="{cx}" cy="{cy}" rx="3.6" ry="8.5" {s}/><line x1="{cx-8.5}" y1="{cy}" x2="{cx+8.5}" y2="{cy}" {s}/>',
        "lb": f'<line x1="{x+7}" y1="{cy}" x2="{x+14}" y2="{cy}" {s}/><line x1="{x+14}" y1="{cy}" x2="{x+18}" y2="{cy-6}" {s}/><circle cx="{x+21}" cy="{cy-6}" r="2.4" {s}/><line x1="{x+14}" y1="{cy}" x2="{x+18}" y2="{cy}" {s}/><circle cx="{x+21}" cy="{cy}" r="2.4" {s}/><line x1="{x+14}" y1="{cy}" x2="{x+18}" y2="{cy+6}" {s}/><circle cx="{x+21}" cy="{cy+6}" r="2.4" {s}/>',
        "ctl": f'<circle cx="{cx}" cy="{cy}" r="4" {s}/><circle cx="{cx}" cy="{cy}" r="8" {s} stroke-dasharray="2.6 2.6"/>',
        "lock": f'<rect x="{x+8.5}" y="{y+14}" width="13" height="9.5" rx="1.8" {s}/><path d="M{x+11.2},{y+14} v-3.2 a3.8,3.8 0 0 1 7.6,0 v3.2" {s}/>',
        "server": f'<rect x="{x+7}" y="{y+7}" width="16" height="7" rx="1.5" {s}/><rect x="{x+7}" y="{y+17}" width="16" height="7" rx="1.5" {s}/><circle cx="{x+10.5}" cy="{y+10.5}" r="0.9" {f}/><circle cx="{x+10.5}" cy="{y+20.5}" r="0.9" {f}/>',
        "code": f'<polyline points="{x+12},{y+9} {x+7},{y+15} {x+12},{y+21}" {s}/><polyline points="{x+18},{y+9} {x+23},{y+15} {x+18},{y+21}" {s}/><line x1="{x+16}" y1="{y+8}" x2="{x+14}" y2="{y+22}" {s}/>',
        "db": f'<ellipse cx="{cx}" cy="{y+10}" rx="7.5" ry="3" {s}/><path d="M{cx-7.5},{y+10} v10 a7.5,3 0 0 0 15,0 v-10" {s}/><path d="M{cx-7.5},{y+15} a7.5,3 0 0 0 15,0" {s}/>',
        "disk": f'<rect x="{x+7}" y="{y+8}" width="16" height="14" rx="2" {s}/><circle cx="{cx}" cy="{cy}" r="3.4" {s}/><circle cx="{cx}" cy="{cy}" r="0.9" {f}/>',
        "bars": f'<line x1="{x+9}" y1="{y+22}" x2="{x+9}" y2="{y+17}" {s}/><line x1="{x+14}" y1="{y+22}" x2="{x+14}" y2="{y+13}" {s}/><line x1="{x+19}" y1="{y+22}" x2="{x+19}" y2="{y+9}" {s}/><line x1="{x+6}" y1="{y+23.5}" x2="{x+24}" y2="{y+23.5}" {s}/>',
        "scale": f'<line x1="{x+10}" y1="{y+22}" x2="{x+10}" y2="{y+8}" {s}/><polyline points="{x+7},{y+11} {x+10},{y+7.5} {x+13},{y+11}" {s}/><line x1="{x+20}" y1="{y+8}" x2="{x+20}" y2="{y+22}" {s}/><polyline points="{x+17},{y+19} {x+20},{y+22.5} {x+23},{y+19}" {s}/>',
        "trend": f'<polyline points="{x+7},{y+20} {x+12},{y+13} {x+16},{y+17} {x+23},{y+9}" {s}/><line x1="{x+6.5}" y1="{y+23}" x2="{x+23.5}" y2="{y+23}" {s}/>',
        "user": f'<circle cx="{cx}" cy="{y+11}" r="3.6" {s}/><path d="M{x+7.5},{y+23} a7.5,6.5 0 0 1 15,0" {s}/>',
        "git": f'<circle cx="{x+10}" cy="{y+8.5}" r="2.3" {s}/><circle cx="{x+10}" cy="{y+21.5}" r="2.3" {s}/><circle cx="{x+20}" cy="{y+12}" r="2.3" {s}/><line x1="{x+10}" y1="{y+10.8}" x2="{x+10}" y2="{y+19.2}" {s}/><path d="M{x+20},{y+14.3} c0,4 -10,3 -10,5" {s}/>',
        "gear": f'<circle cx="{cx}" cy="{cy}" r="4.5" {s}/><line x1="{cx}" y1="{cy-9}" x2="{cx}" y2="{cy-6}" {s}/><line x1="{cx}" y1="{cy+6}" x2="{cx}" y2="{cy+9}" {s}/><line x1="{cx-9}" y1="{cy}" x2="{cx-6}" y2="{cy}" {s}/><line x1="{cx+6}" y1="{cy}" x2="{cx+9}" y2="{cy}" {s}/><line x1="{cx-6.4}" y1="{cy-6.4}" x2="{cx-4.2}" y2="{cy-4.2}" {s}/><line x1="{cx+4.2}" y1="{cy+4.2}" x2="{cx+6.4}" y2="{cy+6.4}" {s}/><line x1="{cx+6.4}" y1="{cy-6.4}" x2="{cx+4.2}" y2="{cy-4.2}" {s}/><line x1="{cx-4.2}" y1="{cy+4.2}" x2="{cx-6.4}" y2="{cy+6.4}" {s}/>',
        "doc": f'<path d="M{x+9},{y+7} h8 l5,5 v11 h-13 z" {s}/><polyline points="{x+17},{y+7} {x+17},{y+12} {x+22},{y+12}" {s}/><line x1="{x+12}" y1="{y+16}" x2="{x+19}" y2="{y+16}" {s}/><line x1="{x+12}" y1="{y+19.5}" x2="{x+19}" y2="{y+19.5}" {s}/>',
        "bolt": f'<polyline points="{x+17},{y+6} {x+10},{y+16} {x+15},{y+16} {x+13},{y+24} {x+20},{y+13} {x+15},{y+13} {x+17},{y+6}" {s}/>',
        "shield": f'<path d="M{cx},{y+6.5} l7,3 v5 c0,5 -3.5,8 -7,9.5 c-3.5,-1.5 -7,-4.5 -7,-9.5 v-5 z" {s}/><polyline points="{cx-3},{cy+0.5} {cx-0.5},{cy+3} {cx+3.5},{cy-2}" {s}/>',
        "box": f'<path d="M{cx},{y+6.5} l8,4 v9 l-8,4 l-8,-4 v-9 z" {s}/><polyline points="{cx-8},{y+10.5} {cx},{y+14.5} {cx+8},{y+10.5}" {s}/><line x1="{cx}" y1="{y+14.5}" x2="{cx}" y2="{y+23.5}" {s}/>',
        "key": f'<circle cx="{x+11}" cy="{cy}" r="4" {s}/><line x1="{x+15}" y1="{cy}" x2="{x+24}" y2="{cy}" {s}/><line x1="{x+21}" y1="{cy}" x2="{x+21}" y2="{cy+3.5}" {s}/><line x1="{x+24}" y1="{cy}" x2="{x+24}" y2="{cy+3}" {s}/>',
        "gate": f'<path d="M{cx},{y+6.5} l8.5,8.5 l-8.5,8.5 l-8.5,-8.5 z" {s}/><polyline points="{cx-3.2},{cy} {cx-0.8},{cy+2.6} {cx+3.6},{cy-2.6}" {s}/>',
        "bell": f'<path d="M{x+9},{y+20} h12 c-1.5,-1.5 -2,-3 -2,-6 a4,4 0 0 0 -8,0 c0,3 -0.5,4.5 -2,6 z" {s}/><path d="M{x+13.5},{y+22.5} a1.6,1.6 0 0 0 3,0" {s}/>',
        "filter": f'<path d="M{x+7},{y+8} h16 l-6,7.5 v7 l-4,-2 v-5 z" {s}/>',
        "cloud": f'<path d="M{x+10},{y+21} a4.5,4.5 0 0 1 -0.5,-9 a6,6 0 0 1 11.5,1.5 a3.8,3.8 0 0 1 0,7.5 z" {s}/>',
        "chat": f'<path d="M{x+7},{y+9} h16 v10 h-9 l-4,3.5 v-3.5 h-3 z" {s}/><line x1="{x+11}" y1="{y+13}" x2="{x+19}" y2="{y+13}" {s}/><line x1="{x+11}" y1="{y+16}" x2="{x+16}" y2="{y+16}" {s}/>',
        "terminal": f'<rect x="{x+6}" y="{y+8}" width="18" height="14" rx="2" {s}/><polyline points="{x+9.5},{y+12.5} {x+12.5},{y+15} {x+9.5},{y+17.5}" {s}/><line x1="{x+14.5}" y1="{y+18}" x2="{x+19.5}" y2="{y+18}" {s}/>',
        "cache": f'<rect x="{x+7}" y="{y+7}" width="16" height="5" rx="1.5" {s}/><rect x="{x+7}" y="{y+12.5}" width="16" height="5" rx="1.5" {s}/><rect x="{x+7}" y="{y+18}" width="16" height="5" rx="1.5" {s}/>',
        "mail": f'<rect x="{x+6}" y="{y+9}" width="18" height="12" rx="1.5" {s}/><polyline points="{x+6.5},{y+9.5} {cx},{y+16} {x+23.5},{y+9.5}" {s}/>',
        "cycle": f'<path d="M{x+22},{y+12} a7.5,7.5 0 0 0 -13.5,-1" {s}/><polyline points="{x+8},{y+7} {x+8.3},{y+11.2} {x+12.5},{y+11}" {s}/><path d="M{x+8},{y+18} a7.5,7.5 0 0 0 13.5,1" {s}/><polyline points="{x+22},{y+23} {x+21.7},{y+18.8} {x+17.5},{y+19}" {s}/>',
        "x": f'<circle cx="{cx}" cy="{cy}" r="8.5" {s}/><line x1="{cx-3.5}" y1="{cy-3.5}" x2="{cx+3.5}" y2="{cy+3.5}" {s}/><line x1="{cx+3.5}" y1="{cy-3.5}" x2="{cx-3.5}" y2="{cy+3.5}" {s}/>',
        "ai": f'<rect x="{x+8}" y="{y+8}" width="14" height="14" rx="2.5" {s}/><circle cx="{cx}" cy="{cy}" r="2.6" {s}/><line x1="{x+12}" y1="{y+5.5}" x2="{x+12}" y2="{y+8}" {s}/><line x1="{x+18}" y1="{y+5.5}" x2="{x+18}" y2="{y+8}" {s}/><line x1="{x+12}" y1="{y+22}" x2="{x+12}" y2="{y+24.5}" {s}/><line x1="{x+18}" y1="{y+22}" x2="{x+18}" y2="{y+24.5}" {s}/>',
        "pod": f'<rect x="{x+7}" y="{y+7}" width="16" height="16" rx="3" {s}/><rect x="{x+11}" y="{y+11}" width="8" height="8" rx="1.5" {s}/>',
        "signal": f'<line x1="{cx}" y1="{y+24}" x2="{cx}" y2="{y+14}" {s}/><path d="M{cx-4},{y+11} a5.5,5.5 0 0 1 8,0" {s}/><path d="M{cx-7},{y+8} a9.5,9.5 0 0 1 14,0" {s}/><circle cx="{cx}" cy="{y+14}" r="1.2" {f}/>',
    }
    return g[name]


# ---------------------------------------------------------------- diagram
class Diagram:
    def __init__(self, d):
        self.d = d
        self.nodes = {}
        for n in d["nodes"]:
            n = dict(n)
            n.setdefault("w", 160)
            n["h"] = n.get("h") or (88 if n.get("tag") else 72)
            self.nodes[n["id"]] = n

    # anchor on a side of a node, with an optional offset along that side
    def anchor(self, n, side, off=0):
        x, y, w, h = n["x"], n["y"], n["w"], n["h"]
        return {"r": (x + w, y + h / 2 + off), "l": (x, y + h / 2 + off),
                "t": (x + w / 2 + off, y), "b": (x + w / 2 + off, y + h)}[side]

    def route(self, e):
        a, b = self.nodes[e["from"]], self.nodes[e["to"]]
        if "pts" in e:
            return e["pts"]
        ss, ts = e.get("ss"), e.get("ts")
        so, to = e.get("so", 0), e.get("to_off", 0)
        acx, acy = a["x"] + a["w"] / 2, a["y"] + a["h"] / 2
        bcx, bcy = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
        if not ss:
            if b["x"] >= a["x"] + a["w"] - 4:
                ss, ts = "r", ts or "l"
            elif b["x"] + b["w"] <= a["x"] + 4:
                ss, ts = "l", ts or "r"
            elif bcy > acy:
                ss, ts = "b", ts or "t"
            else:
                ss, ts = "t", ts or "b"
        ts = ts or {"r": "l", "l": "r", "b": "t", "t": "b"}[ss]
        p1 = self.anchor(a, ss, so)
        p2 = self.anchor(b, ts, to)
        gap = 4
        # pull the end point back so the arrowhead sits just outside the box
        dx = {"l": -gap, "r": gap, "t": 0, "b": 0}[ts]
        dy = {"t": -gap, "b": gap, "l": 0, "r": 0}[ts]
        p2 = (p2[0] + dx, p2[1] + dy)
        if ss in "lr" and ts in "lr":
            if abs(p1[1] - p2[1]) < 1:
                return [p1, p2]
            mx = e.get("mx", (p1[0] + p2[0]) / 2)
            return [p1, (mx, p1[1]), (mx, p2[1]), p2]
        if ss in "tb" and ts in "tb":
            if abs(p1[0] - p2[0]) < 1:
                return [p1, p2]
            my = e.get("my", (p1[1] + p2[1]) / 2)
            return [p1, (p1[0], my), (p2[0], my), p2]
        if ss in "lr":  # horizontal then vertical
            return [p1, (p2[0], p1[1]), p2]
        return [p1, (p1[0], p2[1]), p2]

    def render(self):
        d = self.d
        W, H = 1244, d["h"]
        out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(d["aria"])}">']
        out.append("<defs>")
        for k, col in [("req", "var(--c-app)"), ("data", "var(--dg-line)"), ("ctl", "var(--c-ctl)"),
                       ("obs", "var(--c-obs)"), ("aws", "var(--c-aws)"), ("neu", "var(--c-neu)")]:
            out.append(f'<marker id="m{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><polygon points="0,0 10,5 0,10" fill="{col}"/></marker>')
        out.append("</defs>")
        for c in d.get("boxes", []):
            k = c["k"]
            dash = c.get("dash", "6 5")
            sw = c.get("sw", 1.2)
            out.append(f'<rect x="{c["x"]}" y="{c["y"]}" width="{c["w"]}" height="{c["h"]}" rx="{c.get("rx", 8)}" fill="none" stroke="var(--c-{k})" stroke-width="{sw}" stroke-dasharray="{dash}" opacity=".8"/>')
            out.append(f'<text x="{c["x"] + 18}" y="{c["y"] - 7}" font-family="{MONO}" font-size="{c.get("fs", 10.5)}" letter-spacing="1.3" fill="var(--c-{k})">{esc(c["label"])}</text>')
        for n in self.nodes.values():
            out.append(self.node(n))
        badges = []
        for i, e in enumerate(d["edges"], 1):
            pts = self.route(e)
            kind = e.get("k", "req")
            kind = {"app": "req"}.get(kind, kind)
            col = {"req": "var(--c-app)", "data": "var(--dg-line)", "ctl": "var(--c-ctl)", "obs": "var(--c-obs)",
                   "aws": "var(--c-aws)", "neu": "var(--c-neu)"}[kind]
            sw = 1.6 if kind in ("req", "data") else 1.4
            dash = ' stroke-dasharray="5 4"' if e.get("dash") else ""
            if len(pts) == 2:
                out.append(f'<line x1="{pts[0][0]:g}" y1="{pts[0][1]:g}" x2="{pts[1][0]:g}" y2="{pts[1][1]:g}" stroke="{col}" stroke-width="{sw}"{dash} marker-end="url(#m{kind})" fill="none"/>')
            else:
                ps = " ".join(f"{p[0]:g},{p[1]:g}" for p in pts)
                out.append(f'<polyline points="{ps}" stroke="{col}" stroke-width="{sw}"{dash} marker-end="url(#m{kind})" fill="none"/>')
            if "badge" in e:
                bx, by = e["badge"]
            else:
                segs = list(zip(pts, pts[1:]))
                seg = max(segs, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
                bx, by = (seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2
            badges.append((i, bx, by))
        for i, bx, by in badges:
            out.append(f'<circle cx="{bx:g}" cy="{by:g}" r="9" fill="var(--dg-box)" stroke="var(--dg-line)" stroke-width="1"/><text x="{bx:g}" y="{by + 3.4:g}" font-family="{MONO}" font-size="9.5" font-weight="500" text-anchor="middle" fill="var(--ink-2)">{i}</text>')
        out.append("</svg>")
        return "".join(out)

    def node(self, n):
        x, y, w, h, k = n["x"], n["y"], n["w"], n["h"], n["k"]
        icon = n.get("icon", "server")
        slot = n.get("slot", icon)
        o = [f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="var(--dg-box)" stroke="var(--c-{k})" stroke-width="1.3"/>',
             f'<path d="M{x + 5},{y + .65:g} h{w - 10} a4.4,4.4 0 0 1 4.4,4.4 v0 h-{w - 1.2:g} v0 a4.4,4.4 0 0 1 4.4,-4.4 z" fill="var(--c-{k})"/>',
             f'<rect x="{x + 13}" y="{y + 13}" width="30" height="30" rx="6" fill="var(--c-{k}-s)"/>',
             glyph(icon, x + 13, y + 13, k),
             f'<!--ICON:{slot}--><!--<image href="../assets/icons/{slot}.svg" x="{x + 15}" y="{y + 15}" width="26" height="26" preserveAspectRatio="xMidYMid meet"/>-->',
             f'<text x="{x + 51}" y="{y + 33}" font-family="{SANS}" font-size="12.5" font-weight="600" fill="var(--ink)">{esc(n["t"])}</text>']
        if n.get("s"):
            o.append(f'<text x="{x + 13}" y="{y + 59}" font-family="{MONO}" font-size="9.6" fill="var(--muted)">{esc(n["s"])}</text>')
        if n.get("tag"):
            tw = round(len(n["tag"]) * 5.75 + 12)
            o.append(f'<rect x="{x + 13}" y="{y + 67}" width="{tw}" height="15" rx="3" fill="var(--c-{k}-s)"/><text x="{x + 19}" y="{y + 77.5}" font-family="{MONO}" font-size="9.3" fill="var(--c-{k})">{esc(n["tag"])}</text>')
        o.append("</g>")
        return "".join(o)


# ---------------------------------------------------------------- page
def nameof(diagram, nid):
    for n in diagram["nodes"]:
        if n["id"] == nid:
            return n.get("name", n["t"])
    raise KeyError(nid)


def img_src(P, s):
    """Resolve a proof image to a URL, copying PDF-extracted images into the site."""
    if "raw" in s:
        return RAW + urllib.parse.quote(s["raw"])
    if "url" in s:
        return s["url"]
    if "pdf" in s:
        src = os.path.join(PDFIMG, s["pdf"])
        dst_dir = os.path.join(SITE, P["slug"], "img")
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, s["name"])
        if os.path.exists(dst):
            return "img/" + s["name"]
        from PIL import Image
        im = Image.open(src).convert("RGB")
        if s.get("crop"):
            im = im.crop(s["crop"])
        if im.width > 1400:
            im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        return "img/" + s["name"]
    raise ValueError(s)


def ledger_legend(rows):
    m = sum(r[0] == "measured" for r in rows)
    o = sum(r[0] == "observed" for r in rows)
    d = sum(r[0] == "design" for r in rows)
    n = len(rows)
    parts = []
    if m:
        parts.append(f"{NUMW[m].lower()} measured")
    if o:
        parts.append(f"{NUMW[o].lower()} observed")
    head = f"{NUMW[n]} claims." if n != 1 else "One claim."
    s = head + " " + ", ".join(parts)
    if d:
        noun = "a design property" if d == 1 else "design properties"
        s += f", {NUMW[d].lower()} stated as {noun} rather than dressed up as {'a result' if d == 1 else 'results'}."
    else:
        s += "."
    s = s.replace(". zero", ". Zero")
    return s[0].upper() + s[1:]


def page(P):
    D = P["diagram"]
    svg = Diagram(D).render()
    spec = "\n".join(f"      <div><dt>{esc(a)}</dt><dd>{b}</dd></div>" for a, b in P["spec"])
    how = "\n".join(f"      <p><strong>{q}</strong> {a}</p>" for q, a in P["how"])
    rows = []
    for i, e in enumerate(D["edges"], 1):
        ft = e.get("ft") or f'{nameof(D, e["from"])} &rarr; {nameof(D, e["to"])}'
        rows.append(f'          <tr><td>{i}</td><td class="ft">{ft}</td><td class="mech">{e["mech"]}</td><td>{e["what"]}</td></tr>')
    legend = []
    for kind, a, b in P["legend"]:
        if kind.startswith("line"):
            _, col, *st = kind.split(":")
            style = f"border-color:var(--{col})" + ("; border-top-style:dashed" if st else "")
            legend.append(f'            <div><u style="{style}"></u><span><b>{a}</b>{b}</span></div>')
        else:
            legend.append(f'            <div><i style="background:var(--{kind})"></i><span><b>{a}</b>{b}</span></div>')
    reach = "<br>\n          ".join(f"<b>{a} &mdash;</b> {b}" for a, b in P["reach"])
    led = []
    for tag, h3, p, method in P["ledger"]:
        label = {"measured": "Measured", "observed": "Observed", "design": "By design"}[tag]
        led.append(f"""      <div class="v-row {tag}">
        <div class="v-tag">{label}</div>
        <div>
          <h3>{h3}</h3>
          <p>{p}</p>
          <p class="v-method"><b>Method</b> {method}</p>
        </div>
      </div>""")
    proof = ""
    if P.get("shots"):
        figs = []
        for s in P["shots"]:
            figs.append(f"""      <figure>
        <img loading="lazy" alt="{html.escape(s['alt'])}" src="{img_src(P, s)}">
        <figcaption>{s['cap']}</figcaption>
      </figure>""")
        proof = f"""
  <section>
    <div class="col">
      <h2>Proof</h2>
      <p class="h2note">{P.get('proof_note', 'Captured during the build')}</p>
    </div>
    <div class="shots">
{chr(10).join(figs)}
    </div>
  </section>
"""
    broke = ""
    if P.get("broke"):
        n = len(P["broke"])
        note = P.get("broke_note") or (f"{NUMW[n]} failure{'s' if n > 1 else ''} worth keeping")
        arts = "\n".join(f"""        <article>
          <h3>{h}</h3>
          <p>{t}</p>
        </article>""" for h, t in P["broke"])
        broke = f"""
  <section>
    <div class="col">
      <h2>What actually broke</h2>
      <p class="h2note">{note}</p>
      <div class="broke">
{arts}
      </div>
    </div>
  </section>
"""
    ledger_intro = P.get("ledger_intro_obs", "the running system")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(P['meta'])}">
<title>{esc(P['title_tag'])}</title>
{HEAD_LINKS}
</head>
<body class="case">
{BAR}
<div class="wrap">

  <header class="mast">
    <div class="col">
      <p class="eyebrow">Case study &mdash; {P['eyebrow']}</p>
      <h1>{P['h1']}</h1>
      <p class="standfirst">{P['standfirst']}</p>

      <div class="status">
        <span class="chip">{P['chip']}</span>
        <p>{P['status']}</p>
      </div>
    </div>

    <dl class="spec">
{spec}
    </dl>
  </header>

  <section>
    <div class="col">
      <h2>What it does</h2>
      <p class="h2note">Summary</p>
      <p>{P['summary']}</p>
    </div>
  </section>

  <section>
    <div class="col">
      <h2>How it is wired</h2>
      <p class="h2note">The mechanism</p>
{how}
    </div>

    <figure class="fig">
      <div class="fig-scroll">
{svg}
      </div>
      <figcaption>{P['figcaption']}</figcaption>
    </figure>

    <div class="wiring">
      <div class="panel">
        <h4>How the components communicate</h4>
        <table class="wire">
          <thead><tr><th>No</th><th>From &rarr; to</th><th>Mechanism</th><th>What happens</th></tr></thead>
          <tbody>
{chr(10).join(rows)}
          </tbody>
        </table>
      </div>
      <div>
        <div class="panel">
          <h4>Legend</h4>
          <div class="key">
{chr(10).join(legend)}
          </div>
        </div>
        <div class="panel">
          <h4>{P.get('reach_title', 'What was reachable')}</h4>
          <p class="surface">{reach}</p>
        </div>
      </div>
    </div>
  </section>

  <section>
    <div class="col">
      <h2>What I verified, and how</h2>
      <p class="h2note">Evidence, separated from design intent</p>
      <p>Building something and being able to prove it works are different claims, so I've kept them separate below. <strong>Measured</strong> means I created the condition myself and recorded what happened. <strong>Observed</strong> means I looked at {ledger_intro} and saw the state it was already in. <strong>By design</strong> means the configuration guarantees it, but I didn't run a test against it &mdash; better to say that plainly than dress it up as a result.</p>
    </div>

    <div class="ledger">

{chr(10).join(led)}

    </div>
    <p class="legend">{P.get('ledger_legend') or ledger_legend(P['ledger'])}</p>
  </section>
{proof}{broke}
  <section>
    <div class="col">
      <h2>Source</h2>
      <p class="h2note">Everything on this page came from here</p>
      <div class="src">
        <p>{P['source']}</p>
        <pre>{P['clone']}</pre>
      </div>
      <p class="stack"><b>Stack</b><br>{P['stack']}</p>
    </div>
  </section>

{P.get('_next', '')}
  <footer class="col">
    Ahmed Tetteh &middot; <a href="mailto:kingsleyswanzy@gmail.com">kingsleyswanzy@gmail.com</a> &middot; <a href="https://github.com/kingswanzy2020">github.com/kingswanzy2020</a> &middot; <a href="https://www.linkedin.com/in/ahmed-tetteh-76a538126/">LinkedIn</a><br>
    {P.get('footer', 'Static HTML and CSS. No JavaScript, no framework, no build step for the page itself.')}
  </footer>

</div>
</body>
</html>
"""


def load_pages():
    pages = []
    for f in sorted(glob.glob(os.path.join(HERE, "content", "*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        pages.extend(m.PAGES)
    return pages


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for P in load_pages():
        if only and P["slug"] not in only:
            continue
        os.makedirs(os.path.join(SITE, P["slug"]), exist_ok=True)
        with open(os.path.join(SITE, P["slug"], "index.html"), "w") as fh:
            fh.write(page(P))
        print("wrote", P["slug"])
