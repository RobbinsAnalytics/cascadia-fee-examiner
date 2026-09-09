#!/usr/bin/env python3
"""The module's domain publish gate. Exits non-zero and stops the build.

    Nothing under data/conformed/ is committed and nothing is published unless
    this script and src/validate_freeze.py both exit zero (PRINCIPLES rule 8).

WHAT IT CHECKS, AND WHY EACH ONE IS HERE

  A. SNAPSHOT INTEGRITY -- every raw file's sha256 still matches its committed
     sidecar. This is the freeze over the sources, and for the RECAP corpus it
     is the ONLY freeze: those PDFs are gitignored (they name a timekeeper on
     nearly every page), so git cannot compare them and the manifest is what
     stands in for that. A gitignored path inside freeze.toml would FAIL OPEN --
     git reports no change on a file it does not track -- which is why the
     corpus is hashed here instead of declared there.

  B. PROTECTED PATHS ARE TRACKED. Reuses validate_freeze.load_protected() and
     asserts every path the freeze gate believes it is protecting is actually in
     git's index. This is the fail-open trap the freeze template documents,
     turned into a check: Path.glob matches the filesystem, not the index.

  C. SCHEMA CONFORMANCE against governance/schema_allowlist.json -- exact header
     match, so an ADDED column fails. See that file for why this is a publish
     gate rather than a third git hook.

  D. THE SUBJECT-MATTER EXCLUSION, re-asserted against the output rather than
     trusted from the run that produced it. A control that is only ever applied
     and never re-verified cannot tell you the day it stops working.

Every check reports state or content it can actually see. Where a check inspects
STATE rather than BEHAVIOUR the message says so (SESSION-RULES trap 6.4).
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST = ROOT / "governance/schema_allowlist.json"
RECAP_MANIFEST = ROOT / "data/raw/recap/manifest.csv"

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sidecars() -> None:
    print("\nA. Snapshot integrity -- raw files against their committed sidecars")
    sidecars = sorted(ROOT.glob("data/raw/**/*.sha256"))
    if not sidecars:
        fail("no .sha256 sidecars found under data/raw/ -- nothing is frozen")
        return
    for side in sidecars:
        target = side.with_suffix("")
        if side.name.endswith(".sha256"):
            target = side.parent / side.name[: -len(".sha256")]
        if not target.exists():
            fail(f"{target.relative_to(ROOT).as_posix()} is missing but its "
                 f"sidecar is committed -- the freeze cannot be asserted")
            continue
        expected = side.read_text(encoding="utf-8").split()[0]
        actual = sha256_of(target)
        rel = target.relative_to(ROOT).as_posix()
        if expected != actual:
            fail(f"{rel} MOVED: sidecar {expected[:16]}... actual {actual[:16]}...")
        else:
            ok(f"{rel}  {actual[:16]}...")


def check_recap_corpus() -> None:
    print("\nA2. RECAP corpus -- the hash-asserted half of the freeze")
    if not RECAP_MANIFEST.exists():
        notes.append("no RECAP corpus yet (stage 3a has not run); nothing to hash")
        print("  --    no manifest yet; stage 3a has not run")
        return
    rows = list(csv.DictReader(RECAP_MANIFEST.open(encoding="utf-8")))
    missing = mismatched = 0
    for r in rows:
        p = ROOT / r["path"]
        if not p.exists():
            missing += 1
            continue
        if sha256_of(p) != r["sha256"]:
            mismatched += 1
    if mismatched:
        fail(f"{mismatched} of {len(rows)} corpus files do not match the manifest")
    if missing:
        # Absence is not corruption: the PDFs are gitignored, so a fresh clone
        # legitimately has none. Say which situation this is rather than guessing.
        print(f"  --    {missing} of {len(rows)} corpus files absent "
              f"(expected in a fresh clone; re-fetch with pull_fee_applications.py)")
    if rows and not mismatched and not missing:
        ok(f"all {len(rows)} corpus files match the manifest")


def check_protected_paths_tracked() -> None:
    print("\nB. Freeze gate integrity -- every protected path is git-tracked")
    cfg = ROOT / "governance/freeze.toml"
    if not cfg.exists():
        fail("governance/freeze.toml is missing")
        return
    try:
        from validate_freeze import load_protected  # type: ignore
    except Exception as exc:  # pragma: no cover
        fail(f"could not import load_protected from validate_freeze: {exc}")
        return
    try:
        # Returns (paths, baseline). Unpacked rather than indexed so that a
        # template change to this signature fails loudly here.
        protected, baseline = load_protected(ROOT, str(cfg))
    except Exception as exc:
        fail(f"load_protected raised: {exc}")
        return
    if not protected:
        fail("freeze.toml protects nothing")
        return
    untracked = []
    for rel in sorted({str(p) for p in protected}):
        r = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--error-unmatch", "--", rel],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            untracked.append(rel)
    if untracked:
        fail("protected but NOT tracked by git -- the freeze gate would pass "
             f"these without comparing anything: {untracked}")
    else:
        ok(f"{len(protected)} protected path(s), all tracked against "
           f"baseline '{baseline}' (state: git's index, not a diff)")


def check_schemas() -> None:
    print("\nC. Schema conformance -- committed tables against the allow-list")
    spec = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    forbidden = {c.lower() for c in spec["_forbidden_source_columns"]}

    for rel, table in spec["tables"].items():
        path = ROOT / rel
        declared = list(table["columns"].keys())
        if any(cls == "person" for cls in table["columns"].values()):
            fail(f"{rel} declares a column of class 'person' -- forbidden by "
                 f"construction")
        if not path.exists():
            print(f"  --    {rel} not built yet")
            continue
        with path.open(encoding="utf-8", newline="") as fh:
            header = next(csv.reader(fh), [])
        if header != declared:
            added = [c for c in header if c not in declared]
            removed = [c for c in declared if c not in header]
            fail(f"{rel} header differs from its declaration "
                 f"(added={added or 'none'}, removed={removed or 'none'})")
            continue
        hits = [c for c in header if c.lower() in forbidden]
        if hits:
            fail(f"{rel} carries a forbidden column: {hits}")
        else:
            ok(f"{rel}  {len(header)} columns, header matches its declaration")

    # Anything committed under data/ that nobody declared at all.
    r = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "data/"],
        capture_output=True, text=True,
    )
    tracked_tables = [
        p for p in r.stdout.split()
        if p.endswith(".csv") and p != "data/raw/recap/manifest.csv"
    ]
    undeclared = [p for p in tracked_tables if p not in spec["tables"]]
    if undeclared:
        fail(f"committed table(s) with no entry in the allow-list: {undeclared}")
    elif tracked_tables:
        ok(f"{len(tracked_tables)} committed table(s), all declared")


def check_subject_matter() -> None:
    print("\nD. Subject-matter exclusion, re-asserted against the output")
    path = ROOT / "data/conformed/dim_case.csv"
    if not path.exists():
        print("  --    dim_case.csv not built yet")
        return
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    # SM-1: no column names a party at person grain -- covered by C.
    # SM-2: no excluded industry survives.
    excluded = ROOT / "data/reference/excluded_sic.csv"
    if not excluded.exists():
        fail("data/reference/excluded_sic.csv is missing -- the rule has no "
             "declared vocabulary")
        return
    codes = {
        r["sic_major_code"].strip()
        for r in csv.DictReader(excluded.open(encoding="utf-8", newline=""))
    }
    survivors = [r["NameCorp"] for r in rows if r["sic_major_code"].strip() in codes]
    if survivors:
        fail(f"SM-2: {len(survivors)} excluded-industry row(s) survived the "
             f"filter, e.g. {survivors[:3]}")
    else:
        ok(f"SM-2: no row in {len(rows):,} carries an excluded SIC major group "
           f"({sorted(codes)})")
    # SM-3: the drop count is published rather than silent.
    run = ROOT / "governance/last_run.json"
    if run.exists():
        rec = json.loads(run.read_text(encoding="utf-8"))
        n = rec.get("population", {}).get("excluded_sic_48")
        if n is None:
            fail("SM-3: the run record does not publish the exclusion count")
        else:
            ok(f"SM-3: the run record publishes the exclusion count ({n})")


def check_no_stray_control_bytes() -> None:
    """No tracked text file carries a control byte that is not tab or newline.

    THIS CHECK IS HERE BECAUSE THE FAILURE IT CATCHES ALREADY HAPPENED, in this
    repository, on 2026-09-09. A tool layer between an authoring session and
    disk interpreted the two-character sequence backslash-b inside a regular
    expression and wrote a single 0x08 byte instead. The file still parsed, the
    module still imported, and every rule in the affected pattern silently
    stopped matching anything -- because the pattern now required a literal
    backspace character that no docket description contains.

    That is the exact shape this estate cares about: a guard that is present,
    tracked, syntactically valid, and unable to fire. It cost four rules in the
    entry classifier and was found by testing the classifier against real
    descriptions rather than by reading it. A regex is not reviewable by eye at
    the byte level, so the check is a mechanism instead.
    """
    print("\nE. Source integrity -- no stray control bytes in tracked text")
    r = subprocess.run(["git", "-C", str(ROOT), "ls-files"],
                       capture_output=True, text=True)
    text_suffixes = {".py", ".csv", ".json", ".md", ".toml", ".txt", ".sha256"}
    allowed = {9, 10, 13}  # tab, newline, carriage return
    offenders = []
    for rel in r.stdout.split("\n"):
        rel = rel.strip()
        if not rel or Path(rel).suffix not in text_suffixes:
            continue
        p = ROOT / rel
        if not p.exists():
            continue
        data = p.read_bytes()
        hits = [(i, b) for i, b in enumerate(data) if b < 32 and b not in allowed]
        if hits:
            i, b = hits[0]
            ctx = data[max(0, i - 40):i + 20].decode("utf-8", "replace")
            offenders.append(f"{rel}: {len(hits)} byte(s), first 0x{b:02x} "
                             f"near ...{ctx.strip()}...")
    if offenders:
        for o in offenders:
            fail(o)
    else:
        ok("no control bytes outside tab, newline and carriage return")


def main() -> int:
    print("Cascadia Fee Examiner -- domain publish gate")
    check_sidecars()
    check_recap_corpus()
    check_protected_paths_tracked()
    check_schemas()
    check_subject_matter()
    check_no_stray_control_bytes()

    print("\n" + "=" * 72)
    if failures:
        print(f"PUBLISH GATE: FAILED -- {len(failures)} check(s) did not pass.")
        print("Publish nothing, commit nothing.")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PUBLISH GATE: PASSED")
    for n in notes:
        print(f"  note: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
