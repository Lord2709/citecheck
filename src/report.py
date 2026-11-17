"""Turn an agent result into something a researcher can read, download and act on.   Owner: Engineering, with Product.

Works on the plain dicts produced by `AgentReport.to_dict()` (kind "draft_check") and `DiscoveryReport.to_dict()`
(kind "discovery"), so it does not depend on the agent's classes and is easy to test.
"""
from __future__ import annotations

import re
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


CONF_NOTE = ("Confidences are the model's scores and are not calibrated yet: \"≥ 0.99\" means the model is very sure, "
             "not that it is right.")


def fmt_conf(c) -> str:
    """Display a model confidence.  The uncalibrated model often outputs 0.999…; "1.00" would overstate certainty."""
    if c is None:
        return "-"
    c = float(c)
    return "≥ 0.99" if c >= 0.995 else f"{c:.2f}"


NUMBER = re.compile(r"\d")
ABSTRACT_ONLY_NOTE = ("Only the abstract could be read: no free full text of this paper was found. Numbers, methods "
                      "and detailed results are usually only in the full paper, so this does not mean your sentence "
                      "is wrong.")
ABSTRACT_ONLY_BLOCKED_NOTE = ("Only the abstract could be read: a free copy of this paper exists, but its website "
                              "refused our download. Open it ({url}) and paste the passage that backs your sentence.")
ABSTRACT_ONLY_OFF_NOTE = ("Only the abstract was read, because full-text reading was switched off for this check. "
                          "Numbers, methods and detailed results are usually only in the full paper.")
NUMBER_NOTE = "Your sentence cites a number; abstracts rarely include them."


def outcome(c: dict) -> str:
    if c.get("status") != "checked" or not c.get("verdict"):
        return "Could not check"
    return OUTCOME[c["verdict"]["label"]]


def full_text_status(read_full_text: bool, steps) -> str:
    """What happened to the full text of the cited paper: read | not_found (looked, no free copy) | blocked (a free
    copy exists, but its site refused our download) | not_needed (the abstract was decisive) | off (full-text reading
    switched off) | "" (none of these).  Taken from the steps the
    agent records (objects or dicts), so reports saved before this field existed get it too."""
    if read_full_text:
        return "read"
    found = ""
    for s in steps or []:
        action = s.get("action", "") if isinstance(s, dict) else getattr(s, "action", "")
        detail = s.get("detail", "") if isinstance(s, dict) else getattr(s, "detail", "")
        if action == "find open-access full text":
            found = "not_found"
        elif action == "free copy":
            found = "blocked"             # a free copy exists, but its site refused our download
        elif action == "read full text?" and not found:
            found = "not_needed" if detail.startswith("not needed") else "off" if "off" in detail else found
    return found


def free_copy_url(c: dict) -> str:
    return next((s.get("detail", "") for s in c.get("steps") or [] if s.get("action") == "free copy"), "")


def ft_status(c: dict) -> str:
    """full_text_status of a citation dict, also for reports saved before the field existed."""
    if c.get("full_text_status"):
        return c["full_text_status"]
    return full_text_status(bool(c.get("read_full_text")), c.get("steps") or []) if c.get("verdict") else ""


def abstract_only(c: dict) -> bool:
    """A verdict that rests on the abstract alone (not on the full text, nor on text the researcher pasted)."""
    return bool(c.get("verdict")) and c.get("status") == "checked" and not c.get("read_full_text") \
        and not c.get("abstract_pasted")


def display_outcome(c: dict) -> str:
    """'Not in the abstract' says more than 'Not enough evidence' when only the abstract could be read."""
    o = outcome(c)
    if o == "Not enough evidence" and abstract_only(c) and ft_status(c) in ("not_found", "blocked", "off"):
        return "Not in the abstract"
    return o


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
        "abstract_only": sum(1 for c in cits if abstract_only(c)),
        "no_free_full_text": sum(1 for c in cits if abstract_only(c) and ft_status(c) == "not_found"),
        "free_copy_refused": sum(1 for c in cits if abstract_only(c) and ft_status(c) == "blocked"),
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
            "Outcome": display_outcome(c),
            "Confidence": fmt_conf(v["confidence"]) if v.get("confidence") is not None else None,
            "Read full text": "yes" if c.get("read_full_text") else "",
            "Suggestion": (c["suggestions"][0]["paper"].get("title") if c.get("suggestions") else ""),
            "Note": c.get("status_detail", "") if c.get("status") != "checked" else "",
        })
    return rows


def _md_escape(s) -> str:
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


def abstract_only_lines(s: dict) -> list:
    """The summary's warning when verdicts rest on abstracts only (empty when none do)."""
    if not s.get("abstract_only"):
        return []
    judged = s["citations"] - s["could_not_check"]
    tail = f", and for {s['no_free_full_text']} of them no free full text exists" if s.get("no_free_full_text") else ""
    noun = "verdict" if judged == 1 else "verdicts"
    verb = "rests" if s["abstract_only"] == 1 else "rest"
    return ["", f"**{s['abstract_only']} of {judged} {noun} {verb} on the abstract alone{tail}.** Numbers and "
                "detailed results are usually only in the full paper."]


def draft_to_markdown(report: dict) -> str:
    s = summarize(report)
    out = ["# CiteCheck report", "",
           f"Checked {s['citations']} citation(s): {s['supported']} supported, {s['contradicted']} contradicted, "
           f"{s['not_enough_evidence']} not enough evidence, {s['could_not_check']} could not be checked. "
           f"The full text was read for {s['read_full_text']}; "
           f"a replacement paper is suggested for {s['with_suggestion']}.",
           *abstract_only_lines(s),
           "",
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
        block = [f"## {c.get('index')}. {display_outcome(c)}", f"**Your sentence:** {c.get('sentence', '')}",
                 f"**Reference:** {c.get('reference_text', '') or '(none found)'}"]
        if p:
            link = p.get("url") or (f"https://doi.org/{p['doi']}" if p.get("doi") else "")
            year = f" ({p['year']})" if p.get("year") else ""
            kind = c.get("pasted_kind") or "abstract"
            pasted = f" ({kind} pasted by the researcher)" if c.get("abstract_pasted") else ""
            block.append(f"**Paper read:** {p.get('title', '')}{year} {link}".rstrip() + pasted)
        if c.get("status") != "checked":
            block.append(f"**Why it could not be checked:** {c.get('status_detail') or STATUS_TEXT.get(c.get('status'), '')}")
        if v:
            source = (" after reading the open-access full text" if c.get("read_full_text")
                      else f" from the {c.get('pasted_kind') or 'abstract'} you pasted" if c.get("abstract_pasted")
                      else " from the abstract")
            block.append(f"**Verdict:** {v.get('display_label')} (confidence {fmt_conf(v.get('confidence'))}){source}")
            if display_outcome(c) == "Not in the abstract":
                st = ft_status(c)
                note = (ABSTRACT_ONLY_OFF_NOTE if st == "off"
                        else ABSTRACT_ONLY_BLOCKED_NOTE.format(url=free_copy_url(c)) if st == "blocked"
                        else ABSTRACT_ONLY_NOTE)
                block.append(f"> {note}" + (f" {NUMBER_NOTE}" if NUMBER.search(c.get("claim", "")) else ""))
            for e in (v.get("evidence") or [])[:1]:
                block.append("**Deciding sentences:**\n\n" + "\n".join(f"> {s}" for s in e.get("sentences") or []))
        for sg in c.get("suggestions") or []:
            sp = sg.get("paper") or {}
            block.append(f"**Suggested paper to read:** {sp.get('title', '')} {sp.get('url') or ''} "
                         f"(supports the claim with confidence {fmt_conf(sg.get('confidence'))})".rstrip()
                         + "\n\n" + "\n".join(f"> {s}" for s in sg.get("sentences") or []))
        steps = c.get("steps") or []
        if steps:
            block.append("<details><summary>How the agent decided</summary>\n\n"
                         + "\n".join(f"- {st.get('action')}: {st.get('detail')}" for st in steps) + "\n\n</details>")
        out += [""] + "\n\n".join(b.rstrip() for b in block).split("\n")   # a blank line between fields: no run-on lines
    b = report.get("backend") or {}
    out += ["", "---", f"Verifier `{b.get('verifier')}`, threshold {b.get('tau')}, strict threshold for suggestions "
            f"{report.get('tau_strict')}. Generated {report.get('created_at', '')}.", "",
            CONF_NOTE]
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
