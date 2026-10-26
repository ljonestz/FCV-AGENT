"""FCV-route readout -> .docx.  render(data, meta, path) takes the dict produced by parse_fcv_docx.py."""
import json, sys
from fcv_docx_style import Report, CONTENT_W, BE_AWARE

SCALE6 = ["Extremely Low", "Very Low", "Low", "Adequate", "Well Embedded", "Very Well Embedded"]


def render(d, meta, path):
    R = Report("fcv", meta)
    R.banner()
    if meta.get("disclaimer"):
        R.status_line(meta["disclaimer"])
    R.be_aware(BE_AWARE)

    sens, resp = d["ratings"]["FCV Sensitivity"], d["ratings"]["FCV Responsiveness"]
    levels = [r[2] for r in d["priority_table"]]
    lines = [(f"{levels.count(k)} {k}", k) for k in ("High", "Medium", "Low") if levels.count(k)]
    R.scorecard([dict(label="FCV Sensitivity", value=sens["value"], n=6, idx=SCALE6.index(sens["value"]) + 1,
                      lo=SCALE6[0], hi=SCALE6[-1]),
                 dict(label="FCV Responsiveness", value=resp["value"], n=6, idx=SCALE6.index(resp["value"]) + 1,
                      lo=SCALE6[0], hi=SCALE6[-1])],
                {"label": "Priority actions", "number": len(d["priority_table"]), "lines": lines},
                note=d["rating_note"])

    R.h1("Executive Summary")
    R.info_box(d["exec"]["opening"], label="Opening assessment", bold=True)
    R.h2_caps("Strengths")
    for x in d["exec"]["strengths"]:
        R.body(x)
    R.h2_caps("Gaps")
    for x in d["exec"]["gaps"]:
        R.body(x)

    R.h1("FCV Risk Exposure")
    for k, paras in d["risk"].items():
        R.h2_caps(k)
        for x in paras:
            R.body(x)

    R.h1("FCV Sensitivity & Responsiveness")
    for i, (lab, r) in enumerate((("FCV Sensitivity", sens), ("FCV Responsiveness", resp))):
        R.rating_segment(lab, r["value"], why=r["text"], first=(i == 0))
    R.small(d["rating_note"])

    R.h1("Priority Actions for the Task Team")
    R.body(d["priority_intro"], keep=True)
    rows = [[r[0], (r[1], f"priority_{r[0]}"), r[2], r[3], r[4]] for r in d["priority_table"]]
    R.data_table(["#", "Priority Action", "Priority", "FCV Focus", "Timing"],
                 [0.35, 3.05, 0.8, 1.2, CONTENT_W - 5.4], rows, pill_cols=(2,), link_col=1)

    R.h1("Strategic Priorities")
    for p in d["priorities"]:
        R.priority_header(p["num"], p["title"], p["meta"], anchor=f"priority_{p['num']}",
                          widths=[1.35, 0.75, 1.1, 1.45, CONTENT_W - 4.65])
        R.label("The Gap")
        for x in p["gap"]:
            R.body(x)
        R.label("Why It Matters")
        for x in p["why"]:
            R.body(x)
        R.label("Essential Actions")
        for i, a in enumerate(p["actions"], start=1):
            if a["target"]:
                R.action_heading(f"{p['num']}.{i}", a["target"])
            for x in a["instr"]:
                R.body(x)
            for x in a["suggested"]:
                R.drafting_box(x, label="Suggested text")
        if p["notes"]:
            R.notes_grid(p["notes"])
        if p["who"]:
            R.who_strip(p["who"])

    R.h1("Watch List for Supervision")
    for i, w in enumerate(d["watch"]):
        R.diamond_item(f"{w['num']}. {w['title']}", w["flag"], " ".join(w["text"]), last=(i == len(d["watch"]) - 1))
    R.save(path)
    return path


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    meta = dict(
        title="FCV Recommendations Note",
        project_line="STAR  ·  Syria  ·  Project Appraisal Document (PAD)  ·  23 October 2026",
        running_label="STAR (Syria)",
        classification="Official Use Only",
        generator=data.get("generator_line", ""),
        disclaimer="Draft - human review required. Named approval of this version must be recorded separately before sharing. This app does not record human approval.",
        its_url="https://fcvriskdashboardqa.worldbank.org/project-screener",
    )
    print(render(data, meta, sys.argv[2]))
