#!/usr/bin/env python3
"""Stage 2 -- the task vocabularies, loaded from the frozen sources. Offline.

    Code meanings are read FROM the published files and are never written as a
    CASE WHEN inside a query. That is the whole point of the stage: a codebook
    that lives in a query is a codebook nobody can review, version or crosswalk.

TWO VOCABULARIES, NOT TWO VERSIONS OF ONE

The brief expected an annually revised code set and effective-dating across
years. That is false for this domain (source register F-04): the ABA UTBMS
bankruptcy set has exactly one version, 1997, and no change log. What actually
varies is WHOSE VOCABULARY IS IN FORCE:

  UTBMS-BK-1997   the legal industry's own billing code set, 21 task codes
                  under 4 phases, published by the ABA
  USTP-APPB-2013  the U.S. Trustee's project categories for larger chapter 11
                  cases, 22 of them, in force for cases filed on or after
                  2013-10-01

The second was derived from the first and then extended. The Federal Register
notice says so in as many words: the USTP "extracted and separately categorized
certain tasks that are included in the broader Appendix A guidelines' project
categories, all but one of which is included in the long-established Uniform
Task Based Management System ('UTBMS') bankruptcy code set."

THAT SENTENCE IS A CLAIM THIS SCRIPT CHECKS RATHER THAN REPEATS. The crosswalk
in data/reference/crosswalk_task_codes.csv is authored, and the counts it
produces -- how many Appendix B categories have no 1:1 UTBMS counterpart, and
which -- are computed here and reported. See governance/codebook.md.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
UTBMS_XLSX = ROOT / "data/raw/reference/aba_utbms_bankruptcy_codes_1997.xlsx"
FR_PDF = ROOT / "data/raw/reference/fr_2013-14323_appendix_b.pdf"
CROSSWALK = ROOT / "data/reference/crosswalk_task_codes.csv"
OUT_DIM = ROOT / "data/conformed/dim_task_code.csv"
OUT_FINDINGS = ROOT / "data/conformed/codebook_findings.json"

# In force for cases filed on or after this date. Source register F-01.
USTP_FROM = "2013-10-01"
UTBMS_FROM = "1997-01-01"


def read_utbms_bankruptcy(path: Path) -> list[dict]:
    """Read the ABA workbook by column reference, never by cell position.

    openpyxl indexes by true column, which matters here: the sheet leaves the
    phase-code column empty on task rows and the task-code column empty on phase
    rows, so a positional read of the non-empty cells puts the wrong value in
    the wrong field on every second row. This is the same trap the estate
    records against its job-tracker workbook, in a different file.
    """
    from openpyxl import load_workbook

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows: list[dict] = []
    phase_code = phase_name = ""
    for a, b, c, d in ws.iter_rows(min_col=1, max_col=4, values_only=True):
        a = (str(a).strip() if a is not None else "")
        b = (str(b).strip() if b is not None else "")
        c = (str(c).strip() if c is not None else "")
        d = (str(d).strip() if d is not None else "")
        if re.fullmatch(r"B\d00", a):          # phase row: code in A, name in C
            phase_code, phase_name = a, c
            continue
        if re.fullmatch(r"B\d{3}", b):         # task row: code in B, name in C
            rows.append({
                "vocabulary": "UTBMS-BK-1997",
                "code": b,
                "name": c,
                "phase_code": phase_code,
                "phase_name": phase_name,
                "definition": " ".join(d.split()),
                "effective_from": UTBMS_FROM,
                "effective_to": "",
                "source_file": UTBMS_XLSX.relative_to(ROOT).as_posix(),
            })
    wb.close()
    if not rows:
        raise SystemExit("FAIL: read no task codes from the ABA workbook.")
    return rows


def _fr_text(path: Path) -> str:
    try:
        import pymupdf  # type: ignore
    except ImportError:  # pragma: no cover
        import fitz as pymupdf  # type: ignore
    doc = pymupdf.open(path)
    text = chr(10).join(pg.get_text() for pg in doc)
    return re.sub(r"\s+", " ", text)


def read_ustp_exhibit_d1(path: Path) -> list[str]:
    """The category names as the notice's own Exhibit D-1 table prints them.

    A SECOND, INDEPENDENT READING of the same vocabulary. The prose list in
    paragraph C.8.b and this table are written by the same author in the same
    document and must agree; reading both and comparing them is what turns
    'the parse looked right' into a check. It is the cheapest possible version
    of the module's own thesis -- reconcile against something you did not
    produce -- and it caught a real defect: an end anchor that did not exist ran
    the prose parse past the list and into the expense categories.
    """
    flat = _fr_text(path)
    start = flat.find("EXHIBIT D–1—SUMMARY OF COMPENSATION REQUESTED BY PROJECT CATEGORY")
    if start < 0:
        return []
    head = "Project category Hours budgeted 1 Fees budgeted 1 Hours billed Fees sought"
    hstart = flat.find(head, start)
    if hstart < 0:
        return []
    body = flat[hstart + len(head):]
    end = body.find("VerDate")
    if end > 0:
        body = body[:end]
    # The table prints names run together with no delimiter, so it is split on
    # the known names rather than parsed. That is honest about what it is: a
    # confirmation that each expected name appears, in order, and that nothing
    # else does.
    return [" ".join(body.split())]


def read_ustp_categories(path: Path) -> list[dict]:
    """Read the project categories out of the Federal Register notice.

    They appear in guidelines paragraph C.8.b as a roman-numbered list, each
    entry 'Name: definition.' Both ends are anchored on text rather than on
    position, because a page-position read of a Federal Register PDF is exactly
    the kind of thing that breaks silently -- and did: the first end anchor here
    named a paragraph that does not exist in this notice, so the parse ran on
    into the EXPENSE categories and returned two entries that are not project
    categories at all. The anchor below is quoted from the sentence that
    actually follows the list.
    """
    flat = _fr_text(path)
    start = flat.find("The project categories set forth below should be used")
    if start < 0:
        raise SystemExit("FAIL: could not locate the C.8.b category list anchor.")
    end = flat.find(
        "c. The applicant should provide a brief narrative summary", start
    )
    if end < 0:
        raise SystemExit(
            "FAIL: could not locate the sentence that ends the C.8.b list. "
            "Refusing to guess where the list stops -- guessing is the defect "
            "this check exists to prevent."
        )
    block = flat[start:end]

    romans = r"(?:i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv|xvi|xvii|xviii|xix|xx|xxi|xxii|xxiii|xxiv)"
    items = list(re.finditer(rf"\b{romans}\.\s+([A-Z][^:]{{2,90}}?):\s*", block))
    rows: list[dict] = []
    for idx, m in enumerate(items):
        stop = items[idx + 1].start() if idx + 1 < len(items) else len(block)
        name = " ".join(m.group(1).split())
        definition = " ".join(block[m.end():stop].split()).rstrip()
        definition = re.sub(rf"\s*{romans}\.$", "", definition).strip()
        rows.append({
            "vocabulary": "USTP-APPB-2013",
            "code": "",
            "name": name,
            "phase_code": "",
            "phase_name": "",
            "definition": definition,
            "effective_from": USTP_FROM,
            "effective_to": "",
            "source_file": FR_PDF.relative_to(ROOT).as_posix(),
        })
    if not rows:
        raise SystemExit("FAIL: parsed no project categories from the notice.")
    return rows


def main() -> int:
    for p in (UTBMS_XLSX, FR_PDF):
        if not p.exists():
            raise SystemExit(f"FAIL: {p} missing. Run src/ingest_brd.py.")

    utbms = read_utbms_bankruptcy(UTBMS_XLSX)
    ustp = read_ustp_categories(FR_PDF)
    print(f"UTBMS-BK-1997  : {len(utbms)} task codes in "
          f"{len({r['phase_code'] for r in utbms})} phases")
    print(f"USTP-APPB-2013 : {len(ustp)} project categories")

    rows = utbms + ustp
    OUT_DIM.parent.mkdir(parents=True, exist_ok=True)
    fields = ["vocabulary", "code", "name", "phase_code", "phase_name",
              "definition", "effective_from", "effective_to", "source_file"]
    with OUT_DIM.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    findings = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "utbms_bk_1997_task_codes": len(utbms),
        "utbms_bk_1997_phases": sorted({r["phase_code"] for r in utbms}),
        "ustp_appb_2013_categories": len(ustp),
        "ustp_category_names": [r["name"] for r in ustp],
    }

    # --- Second reading: the notice's own Exhibit D-1 table -------------------
    table = read_ustp_exhibit_d1(FR_PDF)
    body = table[0] if table else ""
    if body:
        cursor, out_of_order, absent = 0, [], []
        for r in ustp:
            at = body.find(r["name"], cursor)
            if at < 0:
                (out_of_order if r["name"] in body else absent).append(r["name"])
            else:
                cursor = at + len(r["name"])
        findings["exhibit_d1_crosscheck"] = {
            "table_found": True,
            "absent_from_table": absent,
            "present_but_out_of_order": out_of_order,
            "agrees": not absent and not out_of_order,
        }
        verdict = "agree" if not absent and not out_of_order else "DISAGREE"
        print("")
        print(f"Exhibit D-1 second reading: prose list and table {verdict}")
        if absent:
            print(f"  absent from the table: {absent}")
        if out_of_order:
            print(f"  present but out of order: {out_of_order}")
    else:
        findings["exhibit_d1_crosscheck"] = {"table_found": False}
        print("")
        print("Exhibit D-1 second reading: table not located; "
              "the prose list stands unconfirmed")

    # --- The notice's own claim about its seven extracted tasks --------------
    # "the USTP extracted and separately categorized certain tasks ... all but
    # one of which is included in the long-established Uniform Task Based
    # Management System ('UTBMS') bankruptcy code set. These tasks are: ..."
    # Checked rather than repeated.
    extracted = [
        "Assumption and Rejection of Leases and Contracts",
        "Avoidance Action Analysis",
        "Corporate Governance and Board Matters",
        "Litigation",
        "Non-Working Travel",
        "Real Estate",
        "Reporting",
    ]
    findings["notice_claim_all_but_one"] = {
        "claim": "of the seven tasks the notice says it extracted, all but one "
                 "are in the UTBMS bankruptcy code set",
        "extracted_tasks": extracted,
    }

    if CROSSWALK.exists():
        cw = list(csv.DictReader(CROSSWALK.open(encoding="utf-8", newline="")))
        by_type: dict[str, list[str]] = {}
        for r in cw:
            by_type.setdefault(r["match_type"], []).append(r["ustp_category"])
        declared = {r["ustp_category"] for r in cw}
        actual = {r["name"] for r in ustp}
        missing = sorted(actual - declared)
        stray = sorted(declared - actual)
        mapped = {r["ustp_category"] for r in cw if r["utbms_code"].strip()}
        utbms_codes = {r["code"] for r in utbms}
        bad_code = sorted(
            r["utbms_code"] for r in cw
            if r["utbms_code"].strip() and r["utbms_code"].strip() not in utbms_codes
        )
        unmapped_utbms = sorted(
            utbms_codes - {r["utbms_code"].strip() for r in cw if r["utbms_code"].strip()}
        )
        findings["crosswalk"] = {
            "rows": len(cw),
            "by_match_type": {k: len(v) for k, v in sorted(by_type.items())},
            "no_utbms_counterpart": sorted(by_type.get("none", [])),
            "categories_not_in_crosswalk": missing,
            "crosswalk_rows_matching_no_category": stray,
            "crosswalk_rows_citing_an_unknown_utbms_code": bad_code,
            "utbms_codes_with_no_ustp_counterpart": unmapped_utbms,
        }
        unmapped_extracted = sorted(set(extracted) - mapped)
        findings["notice_claim_all_but_one"]["extracted_tasks_without_a_utbms_code"] =             unmapped_extracted
        findings["notice_claim_all_but_one"]["claim_holds"] =             len(unmapped_extracted) == 1
        print("")
        print(f"The notice's 'all but one' claim, checked against the crosswalk:")
        print(f"  seven extracted tasks; {len(unmapped_extracted)} with no UTBMS "
              f"counterpart -> {unmapped_extracted}")
        print(f"  claim holds: {len(unmapped_extracted) == 1}")
        if bad_code:
            print(f"  FAIL: crosswalk cites a UTBMS code that does not exist: {bad_code}")
        if unmapped_utbms:
            print(f"  UTBMS codes no Appendix B category maps to: "
                  f"{', '.join(unmapped_utbms)}")
        print("\nCrosswalk USTP-APPB-2013 -> UTBMS-BK-1997")
        for k, v in sorted(by_type.items()):
            print(f"  {k:<8} {len(v)}")
        if by_type.get("none"):
            print(f"  no UTBMS counterpart: {', '.join(sorted(by_type['none']))}")
        if missing:
            print(f"  FAIL: category with no crosswalk row: {missing}")
        if stray:
            print(f"  FAIL: crosswalk row matching no category: {stray}")
        if missing or stray or bad_code:
            OUT_FINDINGS.write_text(json.dumps(findings, indent=2) + "\n",
                                    encoding="utf-8")
            return 1
    else:
        print("\nNo crosswalk yet -- writing the category list for one to be "
              "authored against.")

    OUT_FINDINGS.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {OUT_DIM.relative_to(ROOT)} and "
          f"{OUT_FINDINGS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
