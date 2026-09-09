#!/usr/bin/env python3
"""Re-apply the classification vocabularies to the cached search results. Offline.

    WHY THIS EXISTS AS ITS OWN STEP

The keep/drop vocabulary is a mapping file, and a mapping file gets corrected --
PRINCIPLES rule 6 says an unrecognised value is appended and surfaced rather
than coerced, which means the file grows as the corpus teaches it. If
classification were only ever computed at fetch time, every correction would
require re-fetching 216 cases to take effect, and nobody would make the
correction.

So the cache is the evidence and the classification is derived from it. Fixing a
rule and re-running this costs seconds and no network traffic. The roster stays
what it is -- a record of which cases have been searched -- and stops being the
place tallies live.

    IT WROTE ITSELF INTO EXISTENCE. On the day this module was built, the rule
    set classed "Debtors' Motion for Entry of an Order Establishing Procedures
    for Interim Compensation" as an ORDER, downloaded it, and failed to parse
    it -- because a motion about compensation procedures contains no award and
    no timekeeper table. Adding one rule fixed it. Without this step, that
    correction would have been worth less than the cost of applying it.

PERSON-NAME CONTROL: this reads entry descriptions, which can name people, and
writes only COUNTS and the columns the manifest already carries. No description
reaches a committed file, and the classification tallies it emits go to
data/live/, which is gitignored working state.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data/live/cache"
ROSTER = ROOT / "data/live/roster.json"
SPINE = ROOT / "data/conformed/dim_case.csv"
MANIFEST = ROOT / "data/raw/recap/manifest.csv"
OUT = ROOT / "data/live/classification.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prune", action="store_true",
                    help="drop manifest rows, and delete the files, for "
                         "documents whose class is no longer a keeper")
    args = ap.parse_args()

    from pull_fee_applications import (  # noqa: E402
        CLASSIFIER, PROF_TYPES, KEEP_CLASSES, classify, load_rules,
        normalise_filer,
    )

    entry_rules = load_rules(CLASSIFIER)
    prof_rules = load_rules(PROF_TYPES)

    spine = {r["PrimaryKey"]: r for r in
             csv.DictReader(SPINE.open(encoding="utf-8", newline=""))
             if r["in_appendix_b_era"] == "true"}
    roster = json.loads(ROSTER.read_text(encoding="utf-8"))["searched"] \
        if ROSTER.exists() else {}

    # The cache key is an md5 of the query string, and the query is
    # deterministic in (court_id, CaseNum) -- so each case's cache file is
    # computed rather than searched for. An earlier version matched on the
    # court and docket number carried in the RESULTS, which found nothing: a
    # search returns entries from related dockets too, so results[0] is not
    # reliably the case that was asked about.
    import hashlib

    def cache_path_for(court: str, docket: str) -> Path:
        query = (f'court_id:{court} AND docketNumber:"{docket}" AND '
                 f'("application for compensation" OR "fee application")')
        return CACHE_DIR / (hashlib.md5(query.encode("utf-8")).hexdigest() + ".json")

    per_case: dict[str, dict] = defaultdict(
        lambda: {"classified": {}, "unique_entries": 0, "available_keepers": 0})
    total_entries = 0

    for pk, case in spine.items():
        cache_file = cache_path_for(case["court_id"], case["CaseNum"])
        if not cache_file.exists():
            continue
        payload = json.loads(cache_file.read_text(encoding="utf-8"))
        results = payload.get("results", [])
        seen, unique = set(), []
        for r in results:
            k = (r.get("docket_entry_id"), r.get("attachment_number"))
            if k in seen:
                continue
            seen.add(k)
            unique.append(r)
        bucket = per_case[pk]
        for r in unique:
            cls = classify(r.get("description", ""), entry_rules,
                           "entry_class") or "unclassified"
            bucket["classified"][cls] = bucket["classified"].get(cls, 0) + 1
            if cls in KEEP_CLASSES and r.get("is_available") and r.get("filepath_local"):
                bucket["available_keepers"] += 1
        bucket["unique_entries"] = len(unique)
        total_entries += len(unique)

    tally: dict[str, int] = defaultdict(int)
    for b in per_case.values():
        for cls, n in b["classified"].items():
            tally[cls] += n

    out = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cases": {pk: dict(b) for pk, b in per_case.items()},
        "totals": dict(sorted(tally.items(), key=lambda t: -t[1])),
        "unique_entries": total_entries,
        "unclassified_rate": (tally.get("unclassified", 0) / total_entries)
        if total_entries else None,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(f"Cases with cached results : {len(per_case)}")
    print(f"Unique docket entries     : {total_entries}")
    print("Classification:")
    for cls, n in out["totals"].items():
        print(f"  {cls:<22} {n:>6}   {n / max(1, total_entries):6.1%}")
    rate = out["unclassified_rate"]
    print(f"Unclassified rate         : "
          f"{rate:.2%}" if rate is not None else "n/a")

    if MANIFEST.exists():
        rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8", newline="")))
        changed = dropped = 0
        kept = []
        for r in rows:
            # The manifest carries no description, so reclassification here uses
            # the filer string it already holds only for professional type; the
            # entry class is refreshed from the cache by docket_entry_id.
            new_prof = classify(r.get("filer_normalised", ""), prof_rules,
                                "professional_type") or r["professional_type"]
            if new_prof != r["professional_type"]:
                r["professional_type"] = new_prof
                changed += 1
            kept.append(r)
        # Re-derive entry_class from the cache where we can see the entry.
        cache_class: dict[str, str] = {}
        for cache_file in CACHE_DIR.glob("*.json"):
            for res in json.loads(cache_file.read_text(encoding="utf-8")).get(
                    "results", []):
                cid = str(res.get("docket_entry_id"))
                if cid not in cache_class:
                    cache_class[cid] = classify(
                        res.get("description", ""), entry_rules,
                        "entry_class") or "unclassified"
        final = []
        for r in kept:
            new_cls = cache_class.get(str(r["docket_entry_id"]), r["entry_class"])
            if new_cls != r["entry_class"]:
                print(f"  reclassified entry {r['docket_entry_id']}: "
                      f"{r['entry_class']} -> {new_cls}")
                r["entry_class"] = new_cls
                changed += 1
            if args.prune and new_cls not in KEEP_CLASSES:
                p = ROOT / r["path"]
                if p.exists():
                    p.unlink()
                dropped += 1
                continue
            final.append(r)
        if changed or dropped:
            with MANIFEST.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()),
                                   lineterminator="\n")
                w.writeheader()
                w.writerows(final)
        print(f"Manifest: {changed} field(s) corrected, {dropped} row(s) pruned, "
              f"{len(final)} remain")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
