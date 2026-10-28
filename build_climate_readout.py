"""Climate-lens readout -> .docx.  render(data, meta, path) takes the dict produced by parse_climate_html.py."""
import json, re, sys
from fcv_docx_style import Report, CONTENT_W, BE_AWARE
from fcv_presentation import priority_advisory_text



def scale_ends(scale_note, fallback=("Very limited", "Very strong")):
    m = re.match(r"Scale:\s*(.*?)\.", scale_note or "")
    if not m:
        return fallback
    parts = [x.strip() for x in m.group(1).split("/")]
    return parts[0], parts[-1]


def render(d, meta, path):
    R = Report("climate", meta)
    R.banner()
    R.be_aware(BE_AWARE)

    # ---- 01 overview
    R.h1("Overview")
    for para in d["overview"]:
        R.body(para)

    # ---- status notices
    for n in d["notices"]:
        R.caution(n["title"], n["body"])

    # ---- 02 assessment findings
    R.h1("Assessment findings")
    for f in d["findings"]:
        R.h2_question(f["question"])
        for para in f["paras"]:
            R.body(para)
        if f["related"]:
            R.related_line("Related operational priorities:",
                           [(t, "priority_" + t.split()[-1]) for t in f["related"]])

    # ---- 03 ratings after the assessment findings
    R.h1("Climate & FCV Sensitivity & Responsiveness")
    # ---- at a glance
    tiles = []
    for r in d["ratings"]:
        lo, hi = scale_ends(r.get("scale_note"))
        tiles.append(dict(label=r["dimension"], value=r["value"], n=r["valuemax"] or 5, idx=r["valuenow"] or 0, lo=lo, hi=hi))
    n_checks = sum(len(g["items"]) for g in d["checks"]["groups"])
    R.scorecard(tiles, {"label": "Operational priorities", "number": len(d["priorities"]),
                        "lines": [(f"+ {n_checks} points to check", None)]},
                note=d["ratings_disclaimer"])

    for i, r in enumerate(d["ratings"]):
        R.rating_segment(r["dimension"], r["value"], meaning=r["meaning"], why=r["why"], notes=r["notes"],
                         question=r["question"], scale=r["scale_note"], first=(i == 0))
    R.small(d["ratings_disclaimer"])

    # ---- 04 priorities
    R.h1("Ranked operational priorities")
    priority_intro = str(d["priority_intro"] or "")
    advisory = priority_advisory_text("climate")
    if d["priorities"] and advisory not in priority_intro:
        priority_intro = "\n\n".join(part for part in (priority_intro, advisory) if part)
    R.info_box(priority_intro, size=9.5, keep=True)
    rows = [[p["rank"], (p["title"], f"priority_{p['rank']}"), p["drafting_for"], p["lead"], p["confidence"]]
            for p in d["priorities"]]
    R.data_table(["#", "Operational priority", "Drafting target", "Suggested lead", "Confidence"],
                 [0.35, 2.65, 1.15, 1.7, CONTENT_W - 5.85], rows, center=(0, 4), pill_cols=(4,), link_col=1)
    for p in d["priorities"]:
        R.priority_header(p["rank"], p["title"],
                          [("Drafting target", p["drafting_for"]), ("Suggested lead", p["lead"]),
                           ("Confidence", p["confidence"])],
                          anchor=f"priority_{p['rank']}", widths=[1.45, CONTENT_W - 2.4, 0.95])
        R.label("Why this matters")
        for x in p["why"]:
            R.body(x)
        R.label("What the team could do")
        for x in p["act"]:
            R.body(x)
        prac = list(p["practical"])
        if p.get("followup"):
            prac.append(("Optional further work:", p["followup"]))
        if prac:
            R.grey_box("Practical considerations and Suggested Text", prac)
        if p.get("drafting"):
            R.drafting_box(p["drafting"], p["drafting_for"], label=p.get("drafting_title") or "Suggested drafting")

    # ---- 04 points to check
    c = d["checks"]
    R.h1(c["heading"])
    R.body(c["description"], keep=True)
    if c.get("band_title"):
        R.info_box(c["band_text"], label=c["band_title"], size=9.5, keep=True)
    if c.get("intro"):
        R.body(c["intro"], size=9, color="5F6B7A", italic=True)
    for g in c["groups"]:
        R.h2_caps(g["title"])
        if g.get("intro"):
            R.body(g["intro"], size=9, color="5F6B7A", italic=True, keep=True)
        R.numbered_items(g["items"])

    # ---- 05 guidance
    g = d["guidance"]
    R.h1(g["heading"])
    R.body(g["description"], keep=True)
    if g.get("intro"):
        R.body(g["intro"], size=9, color="5F6B7A", italic=True, keep=True)
    R.link_items(g["items"])

    # ---- 06 limitations
    R.h1("Limitations")
    for x in d["limitations"]:
        R.body(x)
    if d.get("closing"):
        R.closing(d["closing"])
    R.save(path)
    return path


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    meta = dict(
        title="FCV Recommendations Note",
        project_line="Somalia  ·  Project Information Document (PID), concept stage  ·  18 October 2026",
        running_label="Somalia",
        classification="Official Use Only",
        generator="",
        its_url="https://fcvriskdashboardqa.worldbank.org/project-screener",
    )
    print(render(data, meta, sys.argv[2]))
