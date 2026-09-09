#!/usr/bin/env python3
"""Stage 3b -- read the summary exhibits out of the stored corpus. Offline.

    TIER A ONLY, AND THAT IS THE DESIGN RATHER THAN A SHORTFALL.

Appendix B prescribes the SUMMARY forms -- a table of professionals with their
titles, rates and hours (Exhibit A/B), and a summary of compensation by project
category (Exhibit D). It does not prescribe the format of the underlying time
detail; paragraph C.10 says an applicant "may provide the electronic data in the
manner in which it maintains it". So the summaries are the conformed layer and
the line-item detail is the unconformed one, which is the opposite of the
intuitive expectation.

Every measure in the register is computable from the summaries. Parsing the
time detail would add per-entry dates and narratives, and the narratives are the
one thing this module refuses to persist, so the effort would buy a date axis at
the cost of the control that makes the module publishable.

THE PERSON-NAME CONTROL, IN THE ONE PLACE IT ACTUALLY BINDS

This parser reads names -- it must, because a name is how a table row announces
itself. IT NEVER WRITES ONE. A row is recognised, its title is conformed to a
role, and its hours and fees are added to a running total for
(application x firm x role). The name is a local variable that goes out of scope.
There is no per-person structure anywhere in this file, so there is nothing for a
later change to accidentally serialise.

LAYOUT FAMILIES
A firm's exhibit layout is its own. Each family is detected by a header
signature rather than by page position, recorded per document as
`layout_family`, and a document matching none of them is recorded `unparsed`
with the reason. The unparsed rate is published; a parser that silently returns
nothing for a third of the corpus is indistinguishable from one that works.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/raw/recap/manifest.csv"
ROLES = ROOT / "data/reference/title_to_role.csv"
OUT_ROLE = ROOT / "data/conformed/fact_role_summary.csv"
OUT_CATEGORY = ROOT / "data/conformed/fact_category_summary.csv"
OUT_APP = ROOT / "data/conformed/fact_application.csv"
OUT_STATUS = ROOT / "data/conformed/parse_status.csv"

MONEY = r"\$\s?([\d,]+(?:\.\d{2})?)"
NUMBER = r"([\d,]+\.\d{2}|[\d,]+\.\d{1}|[\d,]+)"

ROLE_FIELDS = ["docket_entry_id", "case_primary_key", "court_id",
               "docket_number", "filer_normalised", "role",
               "timekeepers", "hours", "fees", "rate_min", "rate_max",
               "layout_family"]
CATEGORY_FIELDS = ["docket_entry_id", "case_primary_key", "court_id",
                   "docket_number", "filer_normalised", "category_as_filed",
                   "matter_number", "hours", "fees", "layout_family"]
APP_FIELDS = ["docket_entry_id", "case_primary_key", "court_id",
              "docket_number", "document_number", "filer_normalised",
              "professional_type", "entry_class", "application_type",
              "period_start", "period_end", "page_count",
              "total_fees_stated", "total_hours_stated",
              "layout_family", "parse_status"]
STATUS_FIELDS = ["docket_entry_id", "path", "page_count", "layout_family",
                 "parse_status", "reason", "role_rows", "category_rows"]


def load_role_rules() -> list[tuple]:
    rows = list(csv.DictReader(ROLES.open(encoding="utf-8", newline="")))
    return sorted(
        ((int(r["priority"]), r["role"], re.compile(r["pattern"])) for r in rows),
        key=lambda t: t[0],
    )


def to_role(title: str, rules: list[tuple]) -> str:
    for _, role, rx in rules:
        if rx.search(title or ""):
            return role
    return "other"


def to_float(s: str | None) -> float | None:
    if not s:
        return None
    try:
        return float(str(s).replace(",", "").replace("$", "").strip())
    except ValueError:
        return None


def page_text(doc, i: int) -> str:
    return doc[i].get_text()


def detect_family(full: str) -> str:
    """Header signature, not page position.

    A page-position detector is the thing that breaks the first time a firm adds
    a cover page, and it breaks silently -- it finds A table and reads it as if
    it were THE table.
    """
    if re.search(r"(?i)attorney\s+name\s*\n\s*position", full) and \
       re.search(r"(?i)hourly\s+rate", full):
        return "exhibit_a_attorney_table"
    if re.search(r"(?i)\bname\s*\n\s*(title|position)\b", full) and \
       re.search(r"(?i)hourly\s+rate", full):
        return "generic_timekeeper_table"
    if re.search(r"(?i)\[\s*matter\s+no\.?\s*\d+\s*\]", full):
        return "matter_category_prose"
    return ""


def parse_attorney_table(lines: list[str], rules: list[tuple]) -> list[dict]:
    """Exhibit A / B layout: one field per extracted line, in column order.

    A row is: name, position, department, admission year, fees, hours, rate
    increases, rate... The parser anchors on the POSITION line -- the only field
    drawn from a small controlled vocabulary -- and reads outward from it. It
    then requires a plausible fees/hours pair before accepting the row, so a
    stray occurrence of the word "Partner" in prose cannot manufacture one.
    """
    out: list[dict] = []
    position_rx = re.compile(
        r"(?i)^\s*(partner|associate|of\s+counsel|senior\s+counsel|counsel|"
        r"paralegal|paraprofessional|legal assistant|law clerk|staff attorney|"
        r"director|principal|shareholder|member|summer associate|attorney)\b\s*$"
    )
    money_rx = re.compile(r"^\s*" + MONEY + r"\s*$")
    num_rx = re.compile(r"^\s*" + NUMBER + r"\s*$")

    for i, ln in enumerate(lines):
        if not position_rx.match(ln):
            continue
        window = lines[i + 1: i + 9]
        fees = hours = rate = None
        for j, w in enumerate(window):
            m = money_rx.match(w)
            if m and fees is None:
                fees = to_float(m.group(1))
                nxt = window[j + 1] if j + 1 < len(window) else ""
                hm = num_rx.match(nxt)
                if hm:
                    hours = to_float(hm.group(1))
                continue
            if fees is not None and rate is None:
                m2 = money_rx.match(w)
                if m2:
                    rate = to_float(m2.group(1))
        if fees is None or hours is None or not hours:
            continue
        if not (0.05 <= hours <= 20000) or not (0 < fees <= 50_000_000):
            continue
        implied = fees / hours if hours else None
        if implied is not None and not (50 <= implied <= 5000):
            continue
        out.append({
            "role": to_role(ln, rules),
            "hours": hours,
            "fees": fees,
            "rate": rate if rate and 50 <= rate <= 5000 else implied,
        })
    return out


def parse_matter_categories(full: str) -> list[dict]:
    """The inline project-category summary.

        (a) Case Administration [Matter No. 20]
        Total Fees:  $252,273.00
        Total Hours: 389.40

    The category name is the FIRM'S, not the U.S. Trustee's. Conforming it is a
    separate, reviewable step; capturing it verbatim here is what makes that
    step auditable.
    """
    out = []
    rx = re.compile(
        r"(?:\(\w{1,3}\)\s*)?([A-Z][^\[\n]{2,80}?)\s*\[\s*Matter\s+No\.?\s*(\d+)\s*\]"
        r"[\s\S]{0,200}?Total\s+Fees:\s*" + MONEY +
        r"[\s\S]{0,80}?Total\s+Hours:\s*" + NUMBER,
        re.I,
    )
    for m in rx.finditer(full):
        name = " ".join(m.group(1).split())
        out.append({
            "category_as_filed": name,
            "matter_number": m.group(2),
            "fees": to_float(m.group(3)),
            "hours": to_float(m.group(4)),
        })
    return out


def parse_period(full: str) -> tuple[str, str]:
    m = re.search(
        r"(?i)\bfor\s+the\s+period\s+(?:from\s+)?"
        r"([A-Z][a-z]+\s+\d{1,2},\s*\d{4})"
        r"\s*(?:through(?:\s+and\s+including)?|to|-|through)\s*"
        r"([A-Z][a-z]+\s+\d{1,2},\s*\d{4})", full)
    if not m:
        m = re.search(
            r"(?i)\bfrom\s+([A-Z][a-z]+\s+\d{1,2},\s*\d{4})"
            r"\s*(?:through(?:\s+and\s+including)?|to)\s*"
            r"([A-Z][a-z]+\s+\d{1,2},\s*\d{4})", full)
    if not m:
        return "", ""

    def iso(s: str) -> str:
        for fmt in ("%B %d, %Y", "%b %d, %Y"):
            try:
                return datetime.strptime(" ".join(s.split()), fmt).date().isoformat()
            except ValueError:
                continue
        return ""
    return iso(m.group(1)), iso(m.group(2))


def application_type(entry_class: str, full: str) -> str:
    if entry_class == "order":
        return "order"
    if entry_class == "application_amended":
        return "amended"
    if re.search(r"(?i)\bfinal\s+fee\s+application\b", full[:4000]):
        return "final"
    if entry_class == "application_final":
        return "final"
    return "interim"


def main() -> int:
    try:
        import pymupdf  # type: ignore
    except ImportError:  # pragma: no cover
        import fitz as pymupdf  # type: ignore

    if not MANIFEST.exists():
        raise SystemExit("FAIL: no corpus manifest. Run pull_fee_applications.py.")

    rules = load_role_rules()
    docs = list(csv.DictReader(MANIFEST.open(encoding="utf-8", newline="")))
    role_rows, cat_rows, app_rows, status_rows = [], [], [], []

    for d in docs:
        path = ROOT / d["path"]
        if not path.exists():
            status_rows.append({
                "docket_entry_id": d["docket_entry_id"], "path": d["path"],
                "page_count": d["page_count"], "layout_family": "",
                "parse_status": "absent",
                "reason": "file not on disk; gitignored corpus, re-fetch to parse",
                "role_rows": 0, "category_rows": 0})
            continue
        try:
            doc = pymupdf.open(path)
            full = "\n".join(page_text(doc, i) for i in range(len(doc)))
        except Exception as exc:
            status_rows.append({
                "docket_entry_id": d["docket_entry_id"], "path": d["path"],
                "page_count": d["page_count"], "layout_family": "",
                "parse_status": "unreadable", "reason": str(exc)[:120],
                "role_rows": 0, "category_rows": 0})
            continue

        if len(full.strip()) < 200 * max(1, len(doc)) // 10:
            status_rows.append({
                "docket_entry_id": d["docket_entry_id"], "path": d["path"],
                "page_count": len(doc), "layout_family": "",
                "parse_status": "image_only",
                "reason": "little or no extractable text; would need OCR",
                "role_rows": 0, "category_rows": 0})
            continue

        family = detect_family(full)
        lines = [ln.rstrip() for ln in full.split("\n")]
        roles = (parse_attorney_table(lines, rules)
                 if family in {"exhibit_a_attorney_table",
                               "generic_timekeeper_table"} else [])
        cats = parse_matter_categories(full)
        if cats and not family:
            family = "matter_category_prose"

        # AGGREGATE BEFORE WRITING. Nothing per-person is constructed.
        by_role: dict[str, dict] = defaultdict(
            lambda: {"timekeepers": 0, "hours": 0.0, "fees": 0.0,
                     "rate_min": None, "rate_max": None})
        for r in roles:
            b = by_role[r["role"]]
            b["timekeepers"] += 1
            b["hours"] += r["hours"]
            b["fees"] += r["fees"]
            rt = r.get("rate")
            if rt:
                b["rate_min"] = rt if b["rate_min"] is None else min(b["rate_min"], rt)
                b["rate_max"] = rt if b["rate_max"] is None else max(b["rate_max"], rt)

        common = {
            "docket_entry_id": d["docket_entry_id"],
            "case_primary_key": d["case_primary_key"],
            "court_id": d["court_id"], "docket_number": d["docket_number"],
            "filer_normalised": d["filer_normalised"],
        }
        for role, b in sorted(by_role.items()):
            role_rows.append({**common, "role": role,
                              "timekeepers": b["timekeepers"],
                              "hours": round(b["hours"], 2),
                              "fees": round(b["fees"], 2),
                              "rate_min": b["rate_min"] or "",
                              "rate_max": b["rate_max"] or "",
                              "layout_family": family})
        for c in cats:
            cat_rows.append({**common, **c, "layout_family": family})

        start, end = parse_period(full)
        status = ("parsed" if (by_role or cats) else "unparsed")
        reason = "" if status == "parsed" else (
            f"no known layout matched (detected family: {family or 'none'})")
        app_rows.append({
            **common,
            "document_number": d["document_number"],
            "professional_type": d["professional_type"],
            "entry_class": d["entry_class"],
            "application_type": application_type(d["entry_class"], full),
            "period_start": start, "period_end": end,
            "page_count": len(doc),
            "total_fees_stated": round(sum(b["fees"] for b in by_role.values()), 2)
            if by_role else "",
            "total_hours_stated": round(sum(b["hours"] for b in by_role.values()), 2)
            if by_role else "",
            "layout_family": family, "parse_status": status,
        })
        status_rows.append({
            "docket_entry_id": d["docket_entry_id"], "path": d["path"],
            "page_count": len(doc), "layout_family": family,
            "parse_status": status, "reason": reason,
            "role_rows": len(by_role), "category_rows": len(cats)})

    for path, fields, rows in (
        (OUT_ROLE, ROLE_FIELDS, role_rows),
        (OUT_CATEGORY, CATEGORY_FIELDS, cat_rows),
        (OUT_APP, APP_FIELDS, app_rows),
        (OUT_STATUS, STATUS_FIELDS, status_rows),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)

    tally: dict[str, int] = defaultdict(int)
    for s in status_rows:
        tally[s["parse_status"]] += 1
    fam: dict[str, int] = defaultdict(int)
    for s in status_rows:
        fam[s["layout_family"] or "none"] += 1

    print(f"Documents in corpus : {len(docs)}")
    for k, v in sorted(tally.items()):
        print(f"  {k:<12} {v:>4}   {v / max(1, len(docs)):.1%}")
    print("Layout families:")
    for k, v in sorted(fam.items(), key=lambda t: -t[1]):
        print(f"  {k:<28} {v:>4}")
    print(f"Role rows {len(role_rows)}, category rows {len(cat_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
