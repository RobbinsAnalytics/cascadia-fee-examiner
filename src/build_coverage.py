#!/usr/bin/env python3
"""Stage 3a -- the coverage measure. Offline; reads the roster and manifest.

    M-04 is a control measure, not an apology. It states what share of the
    professional-fee record in this population is reachable free, and it is the
    figure every other measure in this module has to be read against.

WHY IT IS A CERTIFIED MEASURE AND NOT A CAVEAT

The documents are public. Reading them costs nothing at a claims agent's site,
and those sites prohibit automated retrieval, so the only lawful bulk path is a
volunteer-contributed archive that holds a minority of them. That gap is not a
defect in this build -- it is a property of how public court records are
actually published, and it is more interesting than most of what a fee analysis
could say. A single estate-wide percentage would hide its shape, so this reports
by court and by year with the denominator on every cell.

THREE DENOMINATORS, DELIBERATELY

  cases            every Appendix B-era case in the spine
  entries          docket entries classified as an application or an order
  applications     entries classified as an application only

A case whose search was TRUNCATED at the page cap has an incomplete entry count,
so it is excluded from entry-level rates and counted separately. Counting a
truncated case as if it were complete is the failure this exclusion prevents:
truncation happens on the largest cases, which are also the best covered, so
including them would bias coverage upward.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SPINE = ROOT / "data/conformed/dim_case.csv"
ROSTER = ROOT / "data/live/roster.json"
CLASSIFICATION = ROOT / "data/live/classification.json"
MANIFEST = ROOT / "data/raw/recap/manifest.csv"
OUT_COVERAGE = ROOT / "data/conformed/coverage_by_case.csv"
OUT_M04 = ROOT / "data/conformed/m04_coverage.csv"
OUT_MANIFEST = ROOT / "data/conformed/measures_manifest.json"

APPLICATION_CLASSES = {"application_interim", "application_final",
                       "application_amended"}
KEEP_CLASSES = APPLICATION_CLASSES | {"order"}

COVERAGE_FIELDS = [
    "case_primary_key", "court_id", "docket_number", "year_filed",
    "meets_threshold", "docket_found", "search_truncated",
    "entries_classified", "entries_unclassified",
    "applications_listed", "orders_listed",
    "documents_available", "documents_stored",
]

M04_FIELDS = [
    "grouping", "group_value", "cases", "cases_with_a_docket",
    "cases_with_any_stored_document", "cases_complete_enumeration",
    "applications_listed", "documents_stored",
    "case_reach_rate", "document_reach_rate",
]


def pct(num: int, den: int) -> str:
    """A rate, or an explicit blank. Never a zero standing in for 'no data'."""
    return "" if not den else f"{num / den:.4f}"


def main() -> int:
    if not ROSTER.exists():
        raise SystemExit("FAIL: no roster. Run src/pull_fee_applications.py.")

    roster = json.loads(ROSTER.read_text(encoding="utf-8"))["searched"]
    # Classification is DERIVED from the cache by src/reclassify.py, not taken
    # from the roster's fetch-time tallies. A correction to the keep/drop
    # vocabulary must be able to reach the published coverage figure without a
    # re-fetch, or nobody makes the correction. The roster is fallback only, and
    # says so, for the case where reclassify has not been run.
    reclassified = {}
    if CLASSIFICATION.exists():
        reclassified = json.loads(
            CLASSIFICATION.read_text(encoding="utf-8")).get("cases", {})
    else:
        print("NOTE: no data/live/classification.json -- falling back to the "
              "roster's fetch-time tallies. Run src/reclassify.py first for "
              "figures that reflect the current vocabulary.")
    spine = [r for r in csv.DictReader(SPINE.open(encoding="utf-8", newline=""))
             if r["in_appendix_b_era"] == "true"]
    stored = defaultdict(int)
    if MANIFEST.exists():
        for r in csv.DictReader(MANIFEST.open(encoding="utf-8", newline="")):
            stored[r["case_primary_key"]] += 1

    unsearched = [c for c in spine if c["PrimaryKey"] not in roster]
    if unsearched:
        print(f"NOTE: {len(unsearched)} of {len(spine)} cases are not yet "
              f"searched. They are reported as such rather than counted as "
              f"having no coverage -- those are different claims.")

    rows = []
    for c in spine:
        k = c["PrimaryKey"]
        r = roster.get(k)
        rc = reclassified.get(k)
        classified = (rc or r or {}).get("classified", {}) or {}
        apps = sum(v for cls, v in classified.items()
                   if cls in APPLICATION_CLASSES)
        orders = classified.get("order", 0)
        rows.append({
            "case_primary_key": k,
            "court_id": c["court_id"],
            "docket_number": c["CaseNum"],
            "year_filed": c["YearFiled"],
            "meets_threshold": c["meets_threshold"],
            "docket_found": "" if r is None else str((r.get("hits") or 0) > 0).lower(),
            "search_truncated": "" if r is None else str(r.get("truncated", False)).lower(),
            "entries_classified": "" if r is None else sum(
                v for cls, v in classified.items() if cls != "unclassified"),
            "entries_unclassified": "" if r is None else classified.get("unclassified", 0),
            "applications_listed": "" if r is None else apps,
            "orders_listed": "" if r is None else orders,
            "documents_available": "" if r is None else (
                (rc or r).get("available_keepers", 0)),
            "documents_stored": stored.get(k, 0),
        })

    OUT_COVERAGE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_COVERAGE.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COVERAGE_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    searched = [r for r in rows if r["docket_found"] != ""]
    complete = [r for r in searched if r["search_truncated"] == "false"]

    def summarise(grouping: str, key) -> list[dict]:
        buckets = defaultdict(list)
        for r in searched:
            buckets[key(r)].append(r)
        out = []
        for value, rs in sorted(buckets.items()):
            comp = [r for r in rs if r["search_truncated"] == "false"]
            out.append({
                "grouping": grouping,
                "group_value": value,
                "cases": len(rs),
                "cases_with_a_docket": sum(1 for r in rs if r["docket_found"] == "true"),
                "cases_with_any_stored_document": sum(
                    1 for r in rs if r["documents_stored"] > 0),
                "cases_complete_enumeration": len(comp),
                "applications_listed": sum(int(r["applications_listed"] or 0)
                                           for r in comp),
                "documents_stored": sum(r["documents_stored"] for r in comp),
                "case_reach_rate": pct(
                    sum(1 for r in rs if r["documents_stored"] > 0), len(rs)),
                "document_reach_rate": pct(
                    sum(r["documents_stored"] for r in comp),
                    sum(int(r["applications_listed"] or 0) + int(r["orders_listed"] or 0)
                        for r in comp)),
            })
        return out

    m04 = (summarise("all", lambda r: "all")
           + summarise("court", lambda r: r["court_id"])
           + summarise("year_filed", lambda r: r["year_filed"]))

    with OUT_M04.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=M04_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(m04)

    overall = m04[0]
    manifest = {
        "built_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "spine_as_of_date": "2023-01-12",
        "corpus_retrieved": "per document; see data/raw/recap/manifest.csv",
        "measures": {
            "M-04": {
                "rows": len(m04),
                "columns": M04_FIELDS,
                "cases_in_population": len(spine),
                "cases_searched": len(searched),
                "cases_complete_enumeration": len(complete),
                "cases_truncated": len(searched) - len(complete),
                "cases_with_any_stored_document": overall["cases_with_any_stored_document"],
                "case_reach_rate": overall["case_reach_rate"],
                "document_reach_rate": overall["document_reach_rate"],
            }
        },
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Population        : {len(spine)} Appendix B-era cases")
    print(f"Searched          : {len(searched)}")
    print(f"  complete        : {len(complete)}")
    print(f"  truncated       : {len(searched) - len(complete)}")
    print(f"Cases reached     : {overall['cases_with_any_stored_document']}"
          f"  ({overall['case_reach_rate'] or 'n/a'})")
    print(f"Documents stored  : {sum(r['documents_stored'] for r in rows)}")
    print(f"Document reach    : {overall['document_reach_rate'] or 'n/a'} "
          f"(over completely enumerated cases only)")
    print("")
    print("By court, where at least one case was searched:")
    for r in m04:
        if r["grouping"] != "court" or r["cases"] < 3:
            continue
        print(f"  {r['group_value']:<6} {r['cases']:>3} cases  "
              f"reach {r['case_reach_rate'] or 'n/a':>6}  "
              f"{r['applications_listed']:>5} applications listed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
