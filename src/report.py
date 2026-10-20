"""Turn an agent result into something a researcher can read, download and act on.   Owner: Engineering, with Product.

Works on the plain dicts produced by `AgentReport.to_dict()` (kind "draft_check") and `DiscoveryReport.to_dict()`
(kind "discovery"), so it does not depend on the agent's classes and is easy to test.
"""
from __future__ import annotations

from collections import Counter

STATUS_TEXT = {
    "checked": "checked",
    "unresolved": "reference not found",
    "not_found": "paper not found",
    "no_abstract": "no abstract available",
    "error": "error",
}
OUTCOME = {  # what the researcher sees for each checked citation
    "SUPPORT": "Supported",
    "CONTRADICT": "Contradicted",
    "NEI": "Not enough evidence",
}


def outcome(c: dict) -> str:
    if c.get("status") != "checked" or not c.get("verdict"):
        return "Could not check"
    return OUTCOME[c["verdict"]["label"]]


def summarize(report: dict) -> dict:
    """Counts the researcher sees first.  'needs_attention' = contradicted + not enough evidence + could not check."""
    cits = report.get("citations") or []
    counts = Counter(outcome(c) for c in cits)
    return {
        "citations": len(cits),
        "supported": counts.get("Supported", 0),
        "contradicted": counts.get("Contradicted", 0),
        "not_enough_evidence": counts.get("Not enough evidence", 0),
        "could_not_check": counts.get("Could not check", 0),
        "needs_attention": len(cits) - counts.get("Supported", 0),
        "read_full_text": sum(1 for c in cits if c.get("read_full_text")),
        "with_suggestion": sum(1 for c in cits if c.get("suggestions")),
    }


def table_rows(report: dict) -> list:
    rows = []
    for c in report.get("citations") or []:
        v = c.get("verdict") or {}
        p = c.get("paper") or {}
        rows.append({
            "#": c.get("index"),
            "Citation": c.get("marker", ""),
            "Claim": c.get("claim", ""),
            "Cited paper": p.get("title") or c.get("reference_text", "")[:80],
            "Outcome": outcome(c),
            "Confidence": round(v["confidence"], 2) if v.get("confidence") is not None else None,
            "Read full text": "yes" if c.get("read_full_text") else "",
            "Suggestion": (c["suggestions"][0]["paper"].get("title") if c.get("suggestions") else ""),
            "Note": c.get("status_detail", "") if c.get("status") != "checked" else "",
        })
    return rows


def _md_escape(s) -> str:
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def draft_to_markdown(report: dict) -> str:
    s = summarize(report)
    out = ["# CiteCheck report", "",
           f"Checked {s['citations']} citation(s): {s['supported']} supported, {s['contradicted']} contradicted, "
           f"{s['not_enough_evidence']} not enough evidence, {s['could_not_check']} could not be checked. "
           f"The full text was read for {s['read_full_text']}; a replacement paper is suggested for {s['with_suggestion']}.", "",
           "> CiteCheck is a second pair of eyes, not proof. Read the evidence sentences before you rely on a verdict. "
           "Suggested papers are papers to read, not citations to paste.", ""]
    for w in report.get("warnings") or []:
        out.append(f"- Note: {w}")
    out += ["", "| # | Citation | Outcome | Confidence | Cited paper |", "|---|---|---|---|---|"]
    for r in table_rows(report):
        out.append(f"| {r['#']} | {_md_escape(r['Citation'])} | {r['Outcome']} | {r['Confidence'] if r['Confidence'] is not None else '-'} "
                   f"| {_md_escape(r['Cited paper'])} |")
    for c in report.get("citations") or []:
        v = c.get("verdict") or {}
        p = c.get("paper") or {}
        out += ["", f"## {c.get('index')}. {outcome(c)}", "", f"**Your sentence:** {c.get('sentence', '')}", "",
                f"**Reference:** {c.get('reference_text', '') or '(none found)'}"]
        if p:
            link = p.get("url") or (f"https://doi.org/{p['doi']}" if p.get("doi") else "")
            year = f" ({p['year']})" if p.get("year") else ""
            out.append(f"**Paper read:** {p.get('title', '')}{year} {link}".rstrip())
        if c.get("status") != "checked":
            out.append(f"**Why it could not be checked:** {c.get('status_detail') or STATUS_TEXT.get(c.get('status'), '')}")
        if v:
            out.append(f"**Verdict:** {v.get('display_label')} (confidence {v.get('confidence', 0):.2f})"
                       + (" after reading the open-access full text" if c.get("read_full_text") else " from the abstract"))
            ev = (v.get("evidence") or [])[:1]
            for e in ev:
                out.append("**Deciding sentences:**")
                out += [f"> {s}" for s in e.get("sentences") or []]
        for sg in c.get("suggestions") or []:
            sp = sg.get("paper") or {}
            out.append(f"**Suggested paper to read:** {sp.get('title', '')} {sp.get('url') or ''} "
                       f"(supports the claim with confidence {sg.get('confidence', 0):.2f})".rstrip())
            out += [f"> {s}" for s in sg.get("sentences") or []]
        steps = c.get("steps") or []
        if steps:
            out.append("<details><summary>How the agent decided</summary>\n")
            out += [f"- {st.get('action')}: {st.get('detail')}" for st in steps]
            out.append("\n</details>")
    b = report.get("backend") or {}
    out += ["", "---", f"Verifier `{b.get('verifier')}`, threshold {b.get('tau')}, strict threshold for suggestions "
            f"{report.get('tau_strict')}. Generated {report.get('created_at', '')}."]
    return "\n".join(out) + "\n"


def discovery_to_markdown(report: dict) -> str:
    out = ["# CiteCheck: papers for your research direction", "", f"**Direction:** {report.get('direction', '')}", "",
           f"Search query: `{report.get('query', '')}`. {report.get('note', '')}", ""]
    for src, msg in (report.get("errors") or {}).items():
        out.append(f"- Source `{src}` did not answer ({msg}); results come from the other sources.")
    for i, c in enumerate(report.get("results") or [], 1):
        p = c.get("paper") or {}
        meta = ", ".join(str(x) for x in (p.get("venue"), p.get("year")) if x)
        out += ["", f"{i}. **{p.get('title', '')}**" + (f" ({meta})" if meta else ""),
                f"   {c.get('band', '')}, score {c.get('score', 0):.2f}; found in {', '.join(c.get('sources') or [])}"
                + (f"; matched: {', '.join(c.get('matched_terms') or [])}" if c.get("matched_terms") else "")]
        if c.get("key_sentence"):
            out.append(f"   > {c['key_sentence']}")
        if p.get("url"):
            out.append(f"   {p['url']}")
    return "\n".join(out) + "\n"


def to_markdown(report: dict) -> str:
    kind = report.get("kind")
    if kind == "draft_check":
        return draft_to_markdown(report)
    if kind == "discovery":
        return discovery_to_markdown(report)
    raise ValueError(f"unknown report kind {kind!r}")
