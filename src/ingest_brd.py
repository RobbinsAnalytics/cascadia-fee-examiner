#!/usr/bin/env python3
"""Stage 1 -- acquire the frozen source snapshots. THIS SCRIPT RE-PULLS.

    Running this overwrites the freeze. It is the one deliberate act
    PRINCIPLES rule 1 reserves; no other script in this repo touches the
    network for the BRD, and nothing rebuilds by re-downloading.

WHAT IT FETCHES

  1. The Florida-UCLA-LoPucki Bankruptcy Research Database Cases table, as the
     publisher's own zip. It is 2.9 MB and is committed outright -- this module
     does NOT take the sibling Matter Ledger's hash-only departure, because at
     this size there is no reason to.

  2. The reference documents the conformed vocabularies are built FROM: the
     Federal Register notice carrying the U.S. Trustee's Appendix B project
     categories, and the ABA UTBMS bankruptcy code set. Code meanings are loaded
     from these files at build time and are never written as a CASE WHEN inside
     a query.

WHY THE PUBLISHER'S DATE IS THE AS-OF DATE

The BRD was frozen by its authors after the December 2022 update; the zip is
named for its release, 2023-01-12, and the download link is stated to remain
active indefinitely. So the as-of date is a property of the source, not of our
retrieval -- which is why the retrieval date is recorded separately and both
appear in governance/source-register.md. Documents acquired later from
CourtListener carry their own retrieval dates for the same reason.

Every file gets a sha256 sidecar. src/validate.py recomputes them on every run.
"""

from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
UA = "cascadia-fee-examiner/1.0 (portfolio research; ajayrobbins@hotmail.com)"
TIMEOUT = 180

# (destination, url, note). The BRD download endpoint 302s to a filename that
# carries the publisher's release date; we keep our own stable name so nothing
# downstream depends on a redirect target we do not control.
SOURCES = [
    (
        "data/raw/brd/brd_cases_table.zip",
        "https://lopucki.law.ufl.edu/download_cases_table.php",
        "BRD Cases table, csv + xlsx + Protocols + User's Manual + Stata do files",
    ),
    (
        "data/raw/reference/fr_2013-14323_appendix_b.pdf",
        "https://www.govinfo.gov/content/pkg/FR-2013-06-17/pdf/2013-14323.pdf",
        "78 FR 36248 -- USTP Appendix B fee guidelines, incl. the C.8 project categories",
    ),
    (
        "data/raw/reference/aba_utbms_bankruptcy_codes_1997.xlsx",
        "https://utbms.com/wp-content/uploads/2023/11/ABA-UTBMS-Bankruptcy-Codes-1997.xlsx",
        "ABA UTBMS bankruptcy task codes; ABA intellectual property, hosted by the LOC",
    ),
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(dest: Path, url: str) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    digest = sha256_of(dest)
    (dest.parent / (dest.name + ".sha256")).write_text(
        f"{digest}  {dest.name}\n", encoding="utf-8"
    )
    return {
        "path": dest.relative_to(ROOT).as_posix(),
        "url": url,
        "effective_url": resp.url,
        "bytes": len(resp.content),
        "sha256": digest,
        "last_modified": resp.headers.get("Last-Modified", ""),
        "content_type": resp.headers.get("Content-Type", ""),
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main() -> int:
    print("Cascadia Fee Examiner -- source acquisition")
    print("THIS OVERWRITES THE FREEZE. Nothing else in this repo re-downloads.\n")
    records = []
    for rel, url, note in SOURCES:
        dest = ROOT / rel
        print(f"  {urlparse(url).netloc} -> {rel}")
        rec = fetch(dest, url)
        rec["note"] = note
        records.append(rec)
        print(f"      {rec['bytes']:,} bytes   sha256 {rec['sha256'][:16]}...")
        if rec["effective_url"] != url:
            print(f"      redirected to: {rec['effective_url']}")

    print("\nRecord these in governance/source-register.md if they have moved:")
    for r in records:
        print(f"  {r['path']}")
        print(f"      sha256 {r['sha256']}")
        print(f"      bytes  {r['bytes']:,}   retrieved {r['retrieved_utc']}")
    print("\nDone. Run src/build_spine.py next; it reads only what is on disk.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
