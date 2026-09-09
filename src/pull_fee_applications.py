#!/usr/bin/env python3
"""Stage 3a -- acquire fee applications from the RECAP archive. RESUMABLE.

    This is the only script here that touches the network after the freeze, and
    it acquires a corpus rather than refreshing one. Stopping it is safe: the
    roster records which spine cases have been searched and the manifest records
    which documents have been stored, both fsynced before the next request, so a
    resumed run asks nothing it already has an answer to.

WHY PER-CASE AND NOT A WATERMARK

The sibling Matter Ledger module pulls a live edge and advances a watermark,
because its source keeps growing. This one does not: the roster is the frozen
spine, 216 cases, fixed on the day the snapshot was taken. So the resumable unit
is a COMPLETION SET -- which case keys have been searched -- and there is no
top-up, no discovery and no id floor. A case is searched once and is then done
forever, unless someone deliberately clears its roster entry.

WHAT IT REFUSES TO DO

  - It does not scrape a claims agent. Kroll's and Epiq's terms permit reading
    and prohibit "any use of direct or indirect automated searches or data
    queries" without written consent, and their coverage would be better than
    RECAP's. That is a constraint accepted rather than routed around, and the
    coverage rate this script measures is the honest consequence.
  - It does not persist a person's name. The API returns docket-level attorney,
    party and judge fields; the cache is written STRIPPED, at write time, so the
    fields are never on disk to leak. See governance/person-name-control.md.
  - It does not download an entry it has not classified. The keep/drop
    vocabulary is data/reference/entry_classifier.csv, applied before any
    storage request, and the unclassified rate is published.

RATE, MEASURED -- AND THE FIRST MEASUREMENT WAS WRONG IN A WAY WORTH RECORDING

A short burst was measured clean at 3 seconds and the spacing was set to 4. That
was a claim about a BURST generalised to SUSTAINED use, and it was false: the run
stopped itself after 86 requests over 25 minutes on sustained rate limiting.
Verification strength is part of a claim, and "fourteen requests in forty-five
seconds" does not establish an hourly rate.

The server states its own limits in the body of the 429, which is better
evidence than any timing experiment:

    unauthenticated   "Rate limit exceeded: 50/hour"
    authenticated     "Rate limit exceeded: 5/min"

So authentication is worth six times the hourly throughput -- 300/hour against
50 -- and the documented 5/min, 50/hour, 125/day figures describe the
AUTHENTICATED tier, while unauthenticated use is capped an order of magnitude
lower per hour. Spacing is therefore derived from which credential is in use
rather than from a constant, and the token is read from the environment and
never from a file.

Downloads come from a different host (storage.courtlistener.com) and are not
throttled by the API limiter; they keep their own, gentler spacing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SPINE = ROOT / "data/conformed/dim_case.csv"
CLASSIFIER = ROOT / "data/reference/entry_classifier.csv"
PROF_TYPES = ROOT / "data/reference/professional_type.csv"
ROSTER = ROOT / "data/live/roster.json"
CACHE_DIR = ROOT / "data/live/cache"
PDF_DIR = ROOT / "data/raw/recap"
MANIFEST = PDF_DIR / "manifest.csv"
RUN_RECORD = ROOT / "governance/last_live_run.json"

API = "https://www.courtlistener.com/api/rest/v4/search/"
STORAGE = "https://storage.courtlistener.com/"
UA = "cascadia-fee-examiner/1.0 (portfolio research; ajayrobbins@hotmail.com)"

# 5/min authenticated, 50/hour unauthenticated, both quoted by the server.
# A little over the stated interval in each case, not exactly at it.
SEARCH_SPACING_AUTH = 12.5      # 4.8/min
SEARCH_SPACING_ANON = 74.0      # 48.6/hour
DOWNLOAD_SPACING = 2.0
MAX_BACKOFF = 300.0
PAGE_SIZE_GUESS = 20

# Classes whose PDF is worth storing. Everything else is classified, counted,
# and left on the server.
KEEP_CLASSES = {
    "application_interim", "application_final", "application_amended", "order",
}

MANIFEST_FIELDS = [
    "case_primary_key", "court_id", "docket_number", "docket_id",
    "docket_entry_id", "document_number", "attachment_number",
    "entry_class", "professional_type", "filer_normalised",
    "page_count", "bytes", "sha256", "path", "storage_url", "retrieved_utc",
]


def load_rules(path: Path, pattern_col: str = "pattern") -> list[tuple]:
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    rules = []
    for r in rows:
        rules.append((int(r["priority"]), r, re.compile(r[pattern_col])))
    rules.sort(key=lambda t: t[0])
    return rules


def classify(text: str, rules: list[tuple], value_col: str) -> str:
    for _, row, rx in rules:
        if rx.search(text or ""):
            return row[value_col]
    return ""


def normalise_filer(description: str) -> str:
    """The filing professional's name, as the docket entry states it.

    Reads the string between 'of' and a role clause: 'First Interim Fee
    Application of Kirkland & Ellis LLP and Kirkland & Ellis International LLP,
    Attorneys for the Debtors' -> 'Kirkland & Ellis LLP and Kirkland & Ellis
    International LLP'. This is a WITHIN-DOCKET key only. Matching it to the
    spine's own firm names is stage 4's job and is deliberately not attempted
    here: a resolution rule written inside an acquisition script is a resolution
    rule nobody reviews.
    """
    if not description:
        return ""
    anchor = re.compile(
        r"(?i)\b(?:fee application|application for compensation|fee statement|"
        r"compensation and reimbursement of expenses)\b[^.]{0,60}?\b(?:of|for)\s+",
    )
    hits = list(anchor.finditer(description))
    if not hits:
        return ""
    # The LAST anchor, not the first. A caption like "Notice Final Fee
    # Application for Compensation for Services and Reimbursement of Expenses of
    # Jefferies LLC" contains three candidate prepositions and only the last one
    # introduces the filer; taking the first returns "Expenses of Jefferies LLC".
    tail = description[hits[-1].end():]
    tail = re.split(
        r"(?i),?\s+(?:as\s+|attorneys?\s+for|counsel\s+(?:to|for)|"
        r"for\s+the\s+(?:period|debtors?|month)|covering|from\s+\w+\s+\d|"
        r"for\s+(?:the\s+)?allowance|for\s+services|for\s+compensation|"
        r"seeking|requesting|in\s+the\s+amount)\b", tail
    )[0]
    tail = re.split(r"\s*\[|\s*\(Related", tail)[0]
    candidate = " ".join(tail.split()).strip(" ,;.")
    return candidate if looks_like_organisation(candidate) else ""


# Docket text that means the extraction ran past the end of the firm name.
_NOISE = re.compile(
    r"(?i)\(Entered:|Hearing scheduled|Filed by|\bDoc\b|#\s*\d|"
    r"\bNotice\)|\bre:|\bDeadline|\bObjections? due|\d{1,2}/\d{1,2}/\d{2,4}"
)

# Cues that a string names an ORGANISATION. Nothing without one is kept.
_ORG_CUE = re.compile(
    r"(?i)\b(l\.?l\.?p|l\.?l\.?c|p\.?l\.?l\.?c|p\.?c|p\.?a|plc|ltd|inc|"
    r"incorporated|corp|corporation|company|co\.|chartered|group|partners|"
    r"associates|consulting|advisors|advisers|holdings|&)\b|&"
)


def looks_like_organisation(s: str) -> bool:
    """Refuse anything that is not recognisably a firm. FAIL CLOSED.

    THIS FUNCTION EXISTS BECAUSE THE EXTRACTOR LEAKED A PERSON'S NAME. On
    2026-09-09 a docket description ending "...Order # 3 Notice) (Keane, Peter)
    (Entered: 11/14/2023)" was captured whole as a filer name and reached two
    working tables. Nothing had been committed, so nothing escaped -- but the
    escape was prevented by the order the session happened to do things in, and
    that is not a control.

    The design layer of the person-name rule aggregates timekeepers before
    writing, so timekeeper names were never at risk. The FILER string was the
    unguarded path: it is copied from publisher text rather than derived, and a
    caption that runs on carries whatever follows it, including the filing
    attorney's name in the court's own parenthetical.

    So this refuses by default. A string is kept only if it carries an explicit
    organisational cue AND no docket-noise marker. The cost is a lower match
    rate, and that is the correct direction to be wrong in: an unresolved firm
    is published as unresolved, while a leaked name is a control failure.
    """
    if not s or len(s) < 4 or len(s) > 160:
        return False
    if _NOISE.search(s):
        return False
    # An organisational cue decides it. "Wellman, Inc." is shaped like
    # "Lastname, Firstname" and is a company; the cue test alone already
    # refuses "Keane, Peter", so a separate person-shape test only adds a
    # false refusal.
    return bool(_ORG_CUE.search(s))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    """Persist before advancing. A roster that records work not yet done is
    worse than one that repeats work already finished."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)


def strip_result(r: dict) -> dict:
    """Keep only what the classifier and the manifest need.

    Written stripped rather than filtered on read: a cache that holds the
    attorney, party and judge fields and merely promises not to use them is one
    careless dump away from being the leak.
    """
    return {
        "docket_id": r.get("docket_id"),
        "docket_entry_id": r.get("docket_entry_id"),
        "docketNumber": r.get("docketNumber"),
        "court_id": r.get("court_id"),
        "document_number": r.get("document_number"),
        "attachment_number": r.get("attachment_number"),
        "description": r.get("description") or r.get("short_description") or "",
        "is_available": r.get("is_available"),
        "page_count": r.get("page_count"),
        "filepath_local": r.get("filepath_local"),
        "entry_date_filed": r.get("entry_date_filed"),
        "dateFiled": r.get("dateFiled"),
    }


class Budget:
    def __init__(self, ceiling: int):
        self.ceiling, self.used, self.stopped = ceiling, 0, None

    def spend(self) -> bool:
        if self.used >= self.ceiling:
            self.stopped = f"per-run request ceiling of {self.ceiling} reached"
            return False
        self.used += 1
        return True


def get(session, url, params, budget, spacing) -> requests.Response | None:
    backoff = spacing
    while True:
        if not budget.spend():
            return None
        resp = session.get(url, params=params, timeout=120)
        if resp.status_code == 429:
            backoff = min(backoff * 2, MAX_BACKOFF)
            print(f"      429 -- backing off {backoff:.0f}s")
            time.sleep(backoff)
            if backoff >= MAX_BACKOFF:
                budget.stopped = "sustained rate limiting"
                return None
            continue
        time.sleep(spacing)
        return resp


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-requests", type=int, default=600,
                    help="hard per-run ceiling; the run stops rather than "
                         "hammering, and records that it stopped")
    ap.add_argument("--max-cases", type=int, default=0,
                    help="stop after this many newly searched cases (0 = all)")
    ap.add_argument("--no-download", action="store_true",
                    help="classify only; store no PDFs")
    ap.add_argument("--max-pages", type=int, default=10,
                    help="pages of search results to enumerate per case. A "
                         "case whose results exceed this is recorded as "
                         "TRUNCATED and is excluded from the coverage "
                         "denominator rather than counted as if complete.")
    args = ap.parse_args()

    started = datetime.now(timezone.utc)
    entry_rules = load_rules(CLASSIFIER)
    prof_rules = load_rules(PROF_TYPES)

    spine = [
        r for r in csv.DictReader(SPINE.open(encoding="utf-8", newline=""))
        if r["in_appendix_b_era"] == "true"
    ]
    roster = json.loads(ROSTER.read_text(encoding="utf-8")) if ROSTER.exists() else {
        "searched": {}, "started_utc": started.isoformat(timespec="seconds")
    }
    manifest_rows = (
        list(csv.DictReader(MANIFEST.open(encoding="utf-8", newline="")))
        if MANIFEST.exists() else []
    )
    have = {(r["docket_entry_id"], r["attachment_number"]) for r in manifest_rows}

    todo = [c for c in spine if c["PrimaryKey"] not in roster["searched"]]
    print(f"Spine (Appendix B era) : {len(spine)} cases")
    print(f"Already searched       : {len(spine) - len(todo)}")
    print(f"To search this run     : {len(todo)}")
    print(f"Request ceiling        : {args.max_requests}")
    print("")

    budget = Budget(args.max_requests)
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    token = (os.environ.get("COURTLISTENER_TOKEN") or "").strip()
    if token:
        session.headers["Authorization"] = f"Token {token}"
    spacing = SEARCH_SPACING_AUTH if token else SEARCH_SPACING_ANON
    print(f"Credential             : "
          f"{'token from COURTLISTENER_TOKEN' if token else 'none (anonymous)'}")
    print(f"Search spacing         : {spacing}s "
          f"({'5/min' if token else '50/hour'} as quoted by the server)")
    print("")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    new_cases = new_docs = 0
    for case in todo:
        if args.max_cases and new_cases >= args.max_cases:
            budget.stopped = budget.stopped or f"--max-cases {args.max_cases} reached"
            break
        if budget.stopped:
            break

        court, docket = case["court_id"], case["CaseNum"]
        if not court or not docket:
            roster["searched"][case["PrimaryKey"]] = {
                "court_id": court, "docket_number": docket, "hits": 0,
                "classified": {}, "note": "no court_id or case number in the spine",
            }
            continue

        query = (f'court_id:{court} AND docketNumber:"{docket}" AND '
                 f'("application for compensation" OR "fee application")')
        print(f"  {case['NameCorp'][:38]:<38} {court} {docket}")

        # PAGINATION IS BY CURSOR, AND A page= PARAMETER IS SILENTLY IGNORED.
        #
        # The first version of this loop passed page=1,2,3... The endpoint
        # accepted every request, returned HTTP 200 each time, and served the
        # SAME twenty results on all six pages. Nothing errored. It surfaced
        # only after deduplication, when a case reporting 131 hits resolved to
        # 20 unique rows across 120 fetched -- and the shape of the bug is that
        # it would have understated the coverage denominator on exactly the
        # large cases where deep paging matters, while costing six requests each
        # to do it. The response's own `next` URL carries the cursor; follow it.
        results, page, total, truncated = [], 1, None, False
        url, params = API, {"type": "rd", "q": query, "order_by": "score desc"}
        while True:
            resp = get(session, url, params, budget, spacing)
            if resp is None:
                break
            if resp.status_code >= 500:
                # A transient server error killed the rest of this case's pages
                # in the first version. One retry, then give up on the case and
                # record it -- a 502 observed during rate measurement on
                # 2026-09-09 is why this branch exists.
                print(f"      HTTP {resp.status_code} -- one retry")
                time.sleep(spacing * 2)
                resp = get(session, url, params, budget, spacing)
                if resp is None or resp.status_code != 200:
                    print(f"      still failing -- case recorded as incomplete")
                    truncated = True
                    break
            elif resp.status_code != 200:
                print(f"      HTTP {resp.status_code} -- recorded, not retried")
                truncated = True
                break
            payload = resp.json()
            total = payload.get("count") if total is None else total
            batch = payload.get("results", [])
            results.extend(strip_result(r) for r in batch)
            nxt = payload.get("next")
            if not nxt or not batch:
                break
            if page >= args.max_pages:
                truncated = True
                break
            url, params = nxt, None   # the cursor lives in the URL
            page += 1

        if budget.stopped and not results:
            break

        # DEDUPLICATE BEFORE COUNTING ANYTHING.
        #
        # The archive's paged search returns the same document on more than one
        # page: a case reporting 103 hits returned 120 rows, six of which were
        # byte-identical references to one entry. Counting the raw rows inflates
        # every classification tally and, worse, inflates the denominator of the
        # coverage measure -- which would make coverage look better on exactly
        # the large cases where paging goes deepest. The download step was
        # already idempotent, so the duplication was invisible in the stored
        # corpus and would have been invisible in the measure too.
        seen_keys: set[tuple] = set()
        unique: list[dict] = []
        for r in results:
            k = (r.get("docket_entry_id"), r.get("attachment_number"))
            if k in seen_keys:
                continue
            seen_keys.add(k)
            unique.append(r)
        duplicates = len(results) - len(unique)
        results = unique

        classified: dict[str, int] = {}
        keepers = []
        for r in results:
            cls = classify(r["description"], entry_rules, "entry_class") or "unclassified"
            r["entry_class"] = cls
            r["professional_type"] = classify(
                r["description"], prof_rules, "professional_type") or "unknown"
            r["filer_normalised"] = normalise_filer(r["description"])
            classified[cls] = classified.get(cls, 0) + 1
            if cls in KEEP_CLASSES and r.get("is_available") and r.get("filepath_local"):
                keepers.append(r)

        cache_key = hashlib.md5(query.encode("utf-8")).hexdigest()
        atomic_write(CACHE_DIR / f"{cache_key}.json",
                     json.dumps({"query": query, "count": total,
                                 "results": results}, indent=1))

        stored = 0
        if not args.no_download:
            for r in keepers:
                key = (str(r["docket_entry_id"]), str(r["attachment_number"] or ""))
                if key in have:
                    continue
                if budget.stopped:
                    break
                url = STORAGE + r["filepath_local"]
                resp = get(session, url, None, budget, DOWNLOAD_SPACING)
                if resp is None or resp.status_code != 200:
                    continue
                rel = Path("data/raw/recap") / court / str(r["docket_id"]) / (
                    f"{r['document_number']}.{r['attachment_number'] or 0}.pdf")
                dest = ROOT / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(resp.content)
                manifest_rows.append({
                    "case_primary_key": case["PrimaryKey"], "court_id": court,
                    "docket_number": docket, "docket_id": r["docket_id"],
                    "docket_entry_id": r["docket_entry_id"],
                    "document_number": r["document_number"],
                    "attachment_number": r["attachment_number"] or "",
                    "entry_class": r["entry_class"],
                    "professional_type": r["professional_type"],
                    "filer_normalised": r["filer_normalised"],
                    "page_count": r["page_count"] or "",
                    "bytes": len(resp.content), "sha256": sha256_of(dest),
                    "path": rel.as_posix(), "storage_url": url,
                    "retrieved_utc": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"),
                })
                have.add(key)
                stored += 1
                new_docs += 1
                # Persist the manifest before the next request, not at the end.
                buf = ["," .join(MANIFEST_FIELDS)]
                for row in manifest_rows:
                    buf.append(",".join(
                        '"' + str(row.get(f, "")).replace('"', '""') + '"'
                        for f in MANIFEST_FIELDS))
                atomic_write(MANIFEST, "\n".join(buf) + "\n")

        roster["searched"][case["PrimaryKey"]] = {
            "court_id": court, "docket_number": docket,
            "hits": total or 0, "returned": len(results),
            "pages_fetched": page, "truncated": truncated,
            "duplicate_rows_dropped": duplicates,
            "classified": classified, "available_keepers": len(keepers),
            "stored": stored,
            "searched_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        atomic_write(ROSTER, json.dumps(roster, indent=1))
        new_cases += 1
        flag = " TRUNCATED" if truncated else ""
        print(f"      {total or 0} hits, {len(results)} unique, "
              f"{len(keepers)} to keep, "
              f"{stored} stored{flag}   "
              f"[requests {budget.used}/{budget.ceiling}]")

    record = {
        "script": "src/pull_fee_applications.py",
        "started_utc": started.isoformat(timespec="seconds"),
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "requests_used": budget.used,
        "request_ceiling": budget.ceiling,
        "cases_searched_this_run": new_cases,
        "documents_stored_this_run": new_docs,
        "cases_searched_total": len(roster["searched"]),
        "cases_in_spine": len(spine),
        "status": "stopped: " + budget.stopped if budget.stopped else "ok",
    }
    atomic_write(RUN_RECORD, json.dumps(record, indent=2) + "\n")
    print("")
    print(f"Status: {record['status']}")
    print(f"Searched {len(roster['searched'])} of {len(spine)} cases; "
          f"{len(manifest_rows)} documents in the manifest.")
    if budget.stopped:
        print("A stop is not a failure. Re-run to continue from the roster.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
