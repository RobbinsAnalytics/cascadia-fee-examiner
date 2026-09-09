#!/usr/bin/env python3
"""The health surface. Offline; one JSON a frontend session can render.

governance/health.json is the machine-readable statement of how right this
module currently is: what is frozen and hashes to what, how much of the
population has been reached, how much of the corpus parsed, how much of the
resolution failed, and whether the gates passed on the last run. Every figure
in it is read from an artifact another script wrote -- nothing is computed here
that a certified artifact does not already carry.

    IT PUBLISHES THE BAD NUMBERS WITH THE GOOD ONES. A health surface that
    shows a coverage rate and hides the unclassified rate, or shows a match
    rate and hides the unresolved examples, is a brochure.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
G, C, L = ROOT / "governance", ROOT / "data/conformed", ROOT / "data/live"
OUT = G / "health.json"
HISTORY = G / "run_history.jsonl"


def jload(p: Path, default=None):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def rows(p: Path) -> list[dict]:
    return list(csv.DictReader(p.open(encoding="utf-8", newline=""))) \
        if p.exists() else []


def gate(cmd: list[str]) -> dict:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    tail = [ln for ln in r.stdout.strip().split("\n") if ln.strip()][-1:]
    return {"passed": r.returncode == 0, "exit_code": r.returncode,
            "last_line": tail[0] if tail else ""}


def main() -> int:
    spine_run = jload(G / "last_run.json", {})
    live_run = jload(G / "last_live_run.json", {})
    measures = jload(C / "measures_manifest.json", {"measures": {}})
    classification = jload(L / "classification.json", {})
    resolution = jload(C / "resolution_stats.json", {})
    codebook = jload(C / "codebook_findings.json", {})
    parse = rows(C / "parse_status.csv")
    coverage = rows(C / "coverage_by_case.csv")

    pop = spine_run.get("population", {})
    m04 = measures.get("measures", {}).get("M-04", {})
    scope = measures.get("measures", {}).get("_scope", {})

    parsed = sum(1 for r in parse if r["parse_status"] == "parsed")
    searched = sum(1 for r in coverage if r["docket_found"] != "")
    truncated = sum(1 for r in coverage if r["search_truncated"] == "true")

    print("Running the gates for the record...")
    gates = {
        "validate": gate([sys.executable, "-X", "utf8", "src/validate.py"]),
        "validate_freeze": gate([sys.executable, "-X", "utf8",
                                 "src/validate_freeze.py"]),
        "validate_measures": gate([sys.executable, "-X", "utf8",
                                   "src/validate_measures.py"]),
    }

    health = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "module": "cascadia-fee-examiner",
        "frozen_spine": {
            "as_of_date": spine_run.get("snapshot", {}).get("as_of_date"),
            "as_of_date_meaning": spine_run.get("snapshot", {}).get(
                "as_of_date_meaning"),
            "sha256": spine_run.get("snapshot", {}).get("sha256"),
            "cases_in_snapshot": pop.get("rows_in_snapshot"),
            "cases_after_subject_matter_filter": pop.get(
                "rows_after_subject_matter_filter"),
            "excluded_sic_48": pop.get("excluded_sic_48"),
            "appendix_b_era_cases": pop.get("appendix_b_era_cases"),
            "era_threshold_unknown": pop.get("era_threshold_unknown"),
        },
        "codebook": {
            "utbms_task_codes": codebook.get("utbms_bk_1997_task_codes"),
            "ustp_categories": codebook.get("ustp_appb_2013_categories"),
            "crosswalk_by_match_type": codebook.get("crosswalk", {}).get(
                "by_match_type"),
            "ustp_categories_without_utbms_counterpart": codebook.get(
                "crosswalk", {}).get("no_utbms_counterpart"),
            "notice_claim_all_but_one_holds": codebook.get(
                "notice_claim_all_but_one", {}).get("claim_holds"),
            "the_one": codebook.get("notice_claim_all_but_one", {}).get(
                "extracted_tasks_without_a_utbms_code"),
            "prose_and_exhibit_d1_agree": codebook.get(
                "exhibit_d1_crosscheck", {}).get("agrees"),
        },
        "acquisition": {
            "cases_in_population": m04.get("cases_in_population"),
            "cases_searched": searched,
            "cases_not_yet_searched": (m04.get("cases_in_population") or 0) - searched,
            "cases_truncated": truncated,
            "documents_stored": sum(int(r["documents_stored"] or 0)
                                    for r in coverage),
            "last_run_status": live_run.get("status"),
            "last_run_requests": live_run.get("requests_used"),
            "unique_docket_entries_classified": classification.get(
                "unique_entries"),
            "unclassified_rate": classification.get("unclassified_rate"),
            "classification": classification.get("totals"),
        },
        "coverage_M04": {
            "case_reach_rate": m04.get("case_reach_rate"),
            "document_reach_rate": m04.get("document_reach_rate"),
            "denominator_note": "rates are over SEARCHED cases; "
                                "not-yet-searched is reported separately, "
                                "not counted as uncovered",
        },
        "parse": {
            "documents": len(parse),
            "parsed": parsed,
            "parse_rate": round(parsed / len(parse), 4) if parse else None,
            "by_status": {s: sum(1 for r in parse if r["parse_status"] == s)
                          for s in sorted({r["parse_status"] for r in parse})},
            "layout_families": {f: sum(1 for r in parse
                                       if (r["layout_family"] or "none") == f)
                                for f in sorted({r["layout_family"] or "none"
                                                 for r in parse})},
        },
        "measurement_scope": scope,
        "resolution": {
            "caption_firm_pairs": resolution.get("caption_firm_pairs"),
            "match_rate": resolution.get("match_rate"),
            "unresolved_rate": resolution.get("unresolved_rate"),
            "by_rule": resolution.get("by_rule"),
            "single_token_matches_refused": resolution.get(
                "single_token_matches_refused"),
            "overrides_used": resolution.get("overrides_used"),
            "unresolved_examples_file": "data/conformed/unresolved_firms.csv",
        },
        "gates": gates,
        "all_gates_passed": all(g["passed"] for g in gates.values()),
    }
    OUT.write_text(json.dumps(health, indent=2) + "\n", encoding="utf-8")
    with HISTORY.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "utc": health["generated_utc"],
            "cases_searched": searched,
            "documents_stored": health["acquisition"]["documents_stored"],
            "parsed": parsed,
            "match_rate": resolution.get("match_rate"),
            "gates_passed": health["all_gates_passed"],
        }) + "\n")

    print(f"Spine        : {pop.get('appendix_b_era_cases')} era cases "
          f"(as of {health['frozen_spine']['as_of_date']})")
    print(f"Acquisition  : {searched} searched, {truncated} truncated, "
          f"{health['acquisition']['documents_stored']} documents stored")
    print(f"Coverage     : case reach {m04.get('case_reach_rate') or 'n/a'}, "
          f"document reach {m04.get('document_reach_rate') or 'n/a'}")
    print(f"Parse        : {parsed} of {len(parse)}")
    print(f"Resolution   : match {resolution.get('match_rate')}, "
          f"unresolved {resolution.get('unresolved_rate')}")
    print(f"Gates        : " + ", ".join(
        f"{k} {'PASS' if v['passed'] else 'FAIL'}" for k, v in gates.items()))
    print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0 if health["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
