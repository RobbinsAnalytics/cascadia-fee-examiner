#!/usr/bin/env python3
"""Stage 1 -- build the case spine from the frozen BRD snapshot. Offline.

Reads the publisher's zip directly. There is deliberately no extracted copy of
the csv on disk: an extracted file is a second copy that nothing keeps true, and
the zip is what the sha256 in the source register covers.

THREE THINGS THIS FILE IMPLEMENTS RATHER THAN INTENDS

1 -- THE COLUMN ALLOW-LIST. The Cases table carries 217 fields and several of
     them are the names of natural persons: the judge at filing, at disposition
     and at appointment; the CEO; the trustee; the examiner; the turnaround
     person. `KEEP` below is an allow-list, not a deny-list, because a deny-list
     silently admits every field the publisher adds later. Organisations are
     kept -- a debtor, a law firm and a claims agent are parties to a public
     filing, not people.

2 -- THE SUBJECT-MATTER EXCLUSION. SIC major group 48 (Communications) is
     dropped before anything downstream sees it, and the drop count is written
     into the run record. A filter whose catch count is never reported is a
     filter nobody has checked. See governance/subject-matter-filter.md.

3 -- MISSING IS FLAGGED, NEVER FILLED (PRINCIPLES rule 3). AssetsPetition and
     LiabPetition are null on 45 of the 224 Appendix B-era cases, so
     `meets_threshold` is a three-state field -- true, false, or unknown -- and
     the unknowns are counted on the page rather than assumed either way.

THE ENCODING TRAP: the csv is Latin-1, not UTF-8, and a UTF-8 read raises
partway through. The publisher documents no encoding.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ZIP_PATH = ROOT / "data/raw/brd/brd_cases_table.zip"
OUT_CASE = ROOT / "data/conformed/dim_case.csv"
OUT_COURT = ROOT / "data/reference/dim_court.csv"
RUN_RECORD = ROOT / "governance/last_run.json"

# The U.S. Trustee's Appendix B guidelines apply to cases FILED ON OR AFTER this
# date (78 FR 36248, A.3). The guidelines' own effective date is 2013-11-01 and
# is a different thing: it is when the USTP began applying them. The population
# boundary is the filing date.
APPENDIX_B_FROM = date(2013, 10, 1)

# Petition thresholds, in millions of dollars, matching the BRD's units.
THRESHOLD_ASSETS_M = 50.0
THRESHOLD_LIAB_M = 50.0

EXCLUDED_SIC_MAJOR = {"48"}  # Communications. See governance/subject-matter-filter.md

# --- The allow-list. Every column that reaches dim_case is named here. --------
KEEP = [
    # identity and keys
    "PrimaryKey", "CaseNum", "NameCorp", "CommonName", "CikBefore",
    # timing
    "DateFiled", "YearFiled", "DateConfirmed", "YearConfirmed",
    "DateDisposed", "YearDisposed", "DaysIn",
    # forum
    "DistFiled", "CityFiled",
    # case shape
    "Chapter", "Voluntary", "Prepackaged", "Disposition", "Emerge", "Shop",
    # size at petition and before
    "AssetsPetition", "LiabPetition", "AssetsBefore", "LiabBefore",
    "SalesBefore", "EmplBefore",
    # industry
    "SICPrimary", "SICDescription", "SICIndustryGroup", "SICMajGroup", "SICDivision",
    # organisations retained for entity resolution (firms, not people)
    "DipAtty", "CommCredAtty", "ClaimsAgent", "ClaimsAgentFirm",
    # the publisher's own fee-related fields, kept so their emptiness is visible
    "ProfFees10k", "DateFeeRev", "FeeReviewer",
    # the publisher's statement about what is on PACER at all
    "DktOnPacer", "DocsOnPacer", "DocsPublic",
]

# Named so a reader can see the control was applied rather than forgotten.
EXCLUDED_PERSON_COLUMNS = [
    "JudgeFiling", "JudgeDisposition", "JudgeApptDist", "DateJudgeAppt",
    "CeoFiling", "CeoNotes", "CeoReplaced", "DateCeoBegin", "DateCeoEnd",
    "TrusteeName", "ExaminerName", "TurnPerson", "CommRetireesName",
]

DERIVED = [
    "court_id", "filed_iso", "in_appendix_b_era", "meets_threshold",
    "threshold_basis", "sic_major_code",
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def court_id_from_dist(dist: str) -> str:
    """BRD forum string -> CourtListener bankruptcy court id.

    The BRD writes the forum as a state abbreviation optionally followed by a
    district letter and 'D': 'DE', 'TX SD', 'NY SD'. CourtListener ids for the
    bankruptcy courts are the lowercased state, the lowercased district letter
    where one exists, then 'b'. So DE -> deb, TX SD -> txsb, NJ -> njb.

    This is a rule, not a lookup table, and a rule can be wrong for a forum this
    dataset has not shown us. Every id produced here is exercised against the
    live archive in src/pull_fee_applications.py, and one that returns no docket
    for any case is reported rather than silently accepted.
    """
    dist = (dist or "").strip()
    if not dist:
        return ""
    m = re.fullmatch(r"([A-Z]{2})(?:\s+([A-Z])D)?", dist)
    if not m:
        return ""
    state, letter = m.group(1).lower(), (m.group(2) or "").lower()
    return f"{state}{letter}b"


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_millions(value: str) -> float | None:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def read_cases(zip_path: Path) -> tuple[list[dict], str]:
    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if len(members) != 1:
            raise SystemExit(
                f"FAIL: expected exactly one csv in the snapshot, found {members}"
            )
        member = members[0]
        raw = zf.read(member)
    # Latin-1, documented nowhere by the publisher and established by failure.
    text = raw.decode("latin-1")
    rows = list(csv.DictReader(io.StringIO(text)))
    return rows, member


def main() -> int:
    if not ZIP_PATH.exists():
        raise SystemExit(f"FAIL: no snapshot at {ZIP_PATH}. Run src/ingest_brd.py.")

    started = datetime.now(timezone.utc)
    rows, member = read_cases(ZIP_PATH)
    checks: list[dict] = []

    def check(name, value, expectation, passed):
        checks.append({"check": name, "value": value,
                       "expectation": expectation, "passed": bool(passed)})

    print(f"Snapshot member : {member}")
    print(f"Rows read       : {len(rows):,}")

    header = set(rows[0].keys()) if rows else set()
    missing = [c for c in KEEP if c not in header]
    check("allow-listed columns present", len(missing), "0", not missing)
    if missing:
        raise SystemExit(f"FAIL: allow-listed columns absent from source: {missing}")

    leaked = [c for c in EXCLUDED_PERSON_COLUMNS if c in KEEP]
    check("no person column in the allow-list", len(leaked), "0", not leaked)
    if leaked:
        raise SystemExit(f"FAIL: person-name column in the allow-list: {leaked}")

    out_rows, excluded_telecom, courts = [], [], {}
    for r in rows:
        sic_major = (r.get("SICMajGroup") or "").strip()
        sic_code = sic_major.split(" ", 1)[0] if sic_major else ""
        if sic_code in EXCLUDED_SIC_MAJOR:
            excluded_telecom.append(
                {"NameCorp": r.get("NameCorp", ""), "YearFiled": r.get("YearFiled", ""),
                 "SICPrimary": r.get("SICPrimary", "")}
            )
            continue

        rec = {c: (r.get(c) or "").strip() for c in KEEP}
        filed = parse_date(r.get("DateFiled", ""))
        chapter = (r.get("Chapter") or "").strip()
        assets = parse_millions(r.get("AssetsPetition", ""))
        liab = parse_millions(r.get("LiabPetition", ""))

        rec["court_id"] = court_id_from_dist(r.get("DistFiled", ""))
        rec["filed_iso"] = filed.isoformat() if filed else ""
        rec["sic_major_code"] = sic_code
        rec["in_appendix_b_era"] = str(
            bool(filed and filed >= APPENDIX_B_FROM and chapter == "11")
        ).lower()

        if assets is None or liab is None:
            rec["meets_threshold"] = "unknown"
            rec["threshold_basis"] = (
                "petition figure missing: "
                + ", ".join(
                    n for n, v in (("AssetsPetition", assets), ("LiabPetition", liab))
                    if v is None
                )
            )
        else:
            meets = assets >= THRESHOLD_ASSETS_M and liab >= THRESHOLD_LIAB_M
            rec["meets_threshold"] = str(meets).lower()
            rec["threshold_basis"] = f"AssetsPetition={assets:g}M; LiabPetition={liab:g}M"

        if rec["court_id"]:
            courts.setdefault(
                rec["court_id"], {"court_id": rec["court_id"],
                                  "brd_dist_filed": rec["DistFiled"], "cases": 0}
            )["cases"] += 1
        out_rows.append(rec)

    era = [r for r in out_rows if r["in_appendix_b_era"] == "true"]
    unknown_threshold = sum(1 for r in era if r["meets_threshold"] == "unknown")
    meets = sum(1 for r in era if r["meets_threshold"] == "true")
    no_court = sum(1 for r in out_rows if not r["court_id"])

    check("telecom (SIC 48) rows excluded", len(excluded_telecom), ">0", excluded_telecom)
    check("no SIC 48 row survives", sum(1 for r in out_rows
                                        if r["sic_major_code"] in EXCLUDED_SIC_MAJOR),
          "0", not any(r["sic_major_code"] in EXCLUDED_SIC_MAJOR for r in out_rows))
    check("every row has a court_id", no_court, "0", no_court == 0)
    check("Appendix B-era cases present", len(era), ">0", era)

    fieldnames = KEEP + DERIVED
    OUT_CASE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CASE.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    OUT_COURT.parent.mkdir(parents=True, exist_ok=True)
    with OUT_COURT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["court_id", "brd_dist_filed", "cases"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(courts.values(), key=lambda c: c["court_id"]))

    record = {
        "script": "src/build_spine.py",
        "started_utc": started.isoformat(timespec="seconds"),
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "snapshot": {
            "path": ZIP_PATH.relative_to(ROOT).as_posix(),
            "member": member,
            "sha256": sha256_of(ZIP_PATH),
            "as_of_date": "2023-01-12",
            "as_of_date_meaning": "publisher's release date for the frozen snapshot",
        },
        "population": {
            "rows_in_snapshot": len(rows),
            "rows_after_subject_matter_filter": len(out_rows),
            "excluded_sic_48": len(excluded_telecom),
            "appendix_b_era_cases": len(era),
            "era_meets_threshold": meets,
            "era_threshold_unknown": unknown_threshold,
            "courts": len(courts),
        },
        "checks": checks,
        "passed": all(c["passed"] for c in checks),
    }
    RUN_RECORD.parent.mkdir(parents=True, exist_ok=True)
    RUN_RECORD.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"Excluded SIC 48 : {len(excluded_telecom)}")
    print(f"Spine rows      : {len(out_rows):,}")
    print(f"Appendix B era  : {len(era)}  "
          f"(threshold met {meets}, unknown {unknown_threshold})")
    print(f"Courts          : {len(courts)} -> "
          f"{', '.join(sorted(courts)[:12])}{' ...' if len(courts) > 12 else ''}")
    print(f"\nWrote {OUT_CASE.relative_to(ROOT)} and {OUT_COURT.relative_to(ROOT)}")
    if not record["passed"]:
        print("\nFAIL: a build check did not pass. Commit nothing.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
