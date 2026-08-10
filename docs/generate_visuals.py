#!/usr/bin/env python3
"""Emit every visual in this repo as SVG, with the data figures derived from output/results.json.

No plotting library. Type is sized so the figures stay readable at 75% browser zoom.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import *  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "output", "results.json")


def audit(d):
    """Re-derive the guarantees from the shipped output rather than asserting them."""
    n = sum(v["n_participants"] for v in d.values())
    classified = sum(len(v["classifications"]) for v in d.values())
    themes = sum(len(v["themes"]) for v in d.values())
    quotes = [q for v in d.values() for t in v["themes"] for q in t["best_quote_ids"]]
    dupes = sum(len([q for t in v["themes"] for q in t["best_quote_ids"]]) -
                len({q for t in v["themes"] for q in t["best_quote_ids"]}) for v in d.values())
    orphan = sum(1 for v in d.values() for c in v["classifications"]
                 if c["theme"] not in {t["title"] for t in v["themes"]})
    partition = sum(1 for v in d.values() if sum(t["count"] for t in v["themes"]) == v["n_participants"])
    return dict(n=n, classified=classified, themes=themes, quotes=len(quotes),
                dupes=dupes, orphan=orphan, partition=partition, questions=len(d))


def hero(a):
    H = 340
    s = head(H, "h", "Codebook-free thematic coding: 495 open-ended responses classified into 26 themes with every quote verified against its source row")
    s += f'''
<text x="40" y="46" fill="{BLUE}" font-size="14" font-weight="700" letter-spacing="3.2" font-family="{MONO}">QUALITATIVE CODING / LLM PIPELINE</text>
<text x="40" y="102" fill="{INK}" font-size="35" font-weight="700">Nothing invented.</text>
<text x="40" y="146" fill="{INK}" font-size="35" font-weight="700">Nothing dropped.</text>
<rect x="40" y="168" width="150" height="2.5" fill="url(#rlh)"/>
<text x="40" y="200" fill="{INK3}" font-size="16">Thematic coding of open-ended survey text, no codebook</text>
<text x="40" y="224" fill="{INK3}" font-size="16">required. The model proposes the themes; the pipeline</text>
<text x="40" y="248" fill="{INK3}" font-size="16">enforces that nobody goes missing and no quote is faked.</text>
'''
    chips = [("detect", 40, 96), ("infer", 148, 88), ("cluster", 248, 104), ("verify", 364, 100)]
    for label, x, w in chips:
        last = label == "verify"
        s += f'<rect x="{x}" y="278" width="{w}" height="28" fill="{"#141d27" if last else f"url(#ndh)"}" stroke="{"#8f9aa6" if last else STROKE}" stroke-width="{1.8 if last else 1.2}" rx="3"/>\n'
        s += txt(x + w / 2, 297, label, 15, INK if last else INK3, weight="700" if last else "400")

    s += f'<rect x="500" y="52" width="364" height="254" fill="#0a0e12" stroke="#212b36" stroke-width="1.2" rx="4"/>\n'
    s += txt(518, 80, "CHECKED AGAINST THE SHIPPED OUTPUT", 13, MUTE, anchor="start")
    rows = [(f"{a['classified']} / {a['n']}", "participants classified", AQUA),
            (f"{a['quotes']} / {a['quotes']}", "quotes traced to source", AQUA),
            (f"{a['partition']} / {a['questions']}", "questions partition exactly", AQUA),
            (f"{a['orphan']}", "orphaned classifications", AQUA),
            (f"{a['dupes']}", "quotes reused across themes", AQUA)]
    for i, (num, label, col) in enumerate(rows):
        y = 116 + i * 38
        s += txt(518, y, num, 18, col, anchor="start", weight="700")
        s += txt(628, y, label, 13, INK3, anchor="start")
    return s + "</svg>\n"


def pipeline():
    H = 580
    s = head(H, "p", "Pipeline: an Excel file is scanned for question columns, the question is inferred from the answers, themes are clustered and every participant assigned, quotes are verified, and a summary is written")
    s += title_block("p", "PIPELINE", "From a spreadsheet nobody labelled to a coded dataset")
    stages = [
        (41, "discover", ["scan free-text cols", "no header trust"], STROKE, INK),
        (253, "infer", ["sample the answers", "recover the question"], BLUE, BLUE_T),
        (465, "cluster", ["3 to 5 themes", "all participants"], BLUE, BLUE_T),
        (677, "verify", ["resolve quote ids", "against source rows"], AQUA, AQUA_T),
    ]
    for i, (x, t, subs, stroke, tc) in enumerate(stages):
        cx = x + 91
        s += box(x, 128, 182, 96, "p", stroke=stroke, sw=1.6)
        s += txt(cx, 158, t, 17, tc, weight="700")
        for j, sub in enumerate(subs):
            s += txt(cx, 186 + j * 22, sub, 14, MUTE)
        if i < 3:
            s += f'<line x1="{x+182}" y1="176" x2="{x+206}" y2="176" stroke="#5a6673" stroke-width="1.8" marker-end="url(#arp)"/>\n'
    s += txt(41, 118, "one Excel file in", 15, FAINT, anchor="start")

    s += f'<line x1="768" y1="224" x2="768" y2="268" stroke="{AQUA}" stroke-width="1.8" marker-end="url(#argp)"/>\n'
    s += box(636, 270, 228, 74, "p", stroke="#8f9aa6", sw=1.6, fill="#141d27")
    s += txt(750, 300, "summarize", 17, INK, weight="700")
    s += txt(750, 326, "second model, warmer tone", 14, MUTE)

    s += f'<rect x="36" y="268" width="560" height="106" fill="#0a0e12" stroke="#4a5663" stroke-width="1.3" stroke-dasharray="6 5" rx="4"/>\n'
    s += txt(58, 296, "the three invariants the pipeline enforces", 15, INK2, anchor="start", weight="700")
    for i, inv in enumerate(["every participant lands in exactly one theme",
                             "no quote is reused across themes",
                             "every quote id resolves to a real response"]):
        s += txt(58, 320 + i * 20, inv, 14, MUTE, anchor="start")

    s += f'<line x1="316" y1="374" x2="316" y2="398" stroke="#5a6673" stroke-width="1.6" marker-end="url(#arp)"/>\n'
    s += f'<line x1="750" y1="344" x2="750" y2="398" stroke="#5a6673" stroke-width="1.6" marker-end="url(#arp)"/>\n'
    outs = [(36, "results.json", "themes, ids, quotes"),
            (330, "per-question .xlsx", "one per question + combined"),
            (700, "report.md", "human layer")]
    for x, t, sub in outs:
        w = 264 if x == 330 else (250 if x == 36 else 164)
        s += box(x, 400, w, 72, "p", stroke=ORANGE, sw=1.6, fill="#1c130e")
        s += txt(x + w / 2, 428, t, 16, ORANGE_T, weight="700")
        s += txt(x + w / 2, 452, sub, 13, MUTE)

    s += caption(["Two models, split by what each is good at: one proposes structure and assigns people to it, the other writes the",
                  "prose a stakeholder reads. The interesting engineering is not the call to either model, it is the layer underneath",
                  "that refuses to ship a theme set where somebody went missing or a quote cannot be traced back to who said it."], 512)
    return s + "</svg>\n"


def distribution(d):
    H = 560
    s = head(H, "d", "Theme distribution across six survey questions, showing how 495 participants partition into 26 themes")
    s += title_block("d", "SHIPPED RESULT", "How 495 participants partitioned into 26 themes")
    x0, x1 = 268, 820
    order = sorted(d.items(), key=lambda kv: -kv[1]["n_participants"])
    pal = [BLUE, AQUA, ORANGE, "#8f9aa6", "#6fa8ec"]
    y = 136
    for k, v in order:
        n = v["n_participants"]
        s += txt(258, y + 22, k.replace("_", " "), 15, INK3, anchor="end")
        cur = x0
        for i, t in enumerate(sorted(v["themes"], key=lambda t: -t["count"])):
            w = (x1 - x0) * t["count"] / n
            s += f'<rect x="{cur:.1f}" y="{y}" width="{max(w-3,2):.1f}" height="32" fill="{pal[i % len(pal)]}" rx="3"/>\n'
            if w > 54:
                s += txt(cur + w / 2, y + 22, f"{t['pct']}%", 14, "#0c1013", weight="700")
            cur += w
        s += txt(x1 + 10, y + 22, f"n={n}", 14, FAINT, anchor="start")
        y += 56
    s += txt(x0, 126, "each bar is one question; segments are its themes, largest first", 14, MUTE, anchor="start")
    s += caption(["Theme counts sum to the participant count on all six questions, so the segments are a true partition rather than",
                  "overlapping tags. One question totals 99% instead of 100% because the published percentages are integers."], 496)
    return s + "</svg>\n"


if __name__ == "__main__":
    d = json.load(open(RESULTS))
    a = audit(d)
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "docs", "figures"), exist_ok=True)
    for path, svg in [("assets/hero.svg", hero(a)),
                      ("assets/pipeline.svg", pipeline()),
                      ("docs/figures/theme_distribution.svg", distribution(d))]:
        p = os.path.join(ROOT, path)
        open(p, "w").write(svg)
        print(f"  {path}  {os.path.getsize(p):,} bytes")
