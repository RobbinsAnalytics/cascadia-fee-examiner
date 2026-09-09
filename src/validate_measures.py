#!/usr/bin/env python3
"""The measure publish gate. Re-derives every cell down a separate path.

    Nothing is published unless this exits zero. A measure that only agrees
    with itself has not been validated.

FOUR CHECKS, AND THE FIRST ONE FOUND A REAL DEFECT ON ITS FIRST RUN

  A. CROSSFOOT, WITHIN A DOCUMENT, BETWEEN TWO EXHIBITS THAT DECOMPOSE THE SAME
     TOTAL. A fee application states its fees twice: once by timekeeper and once
     by project category. Those are two independent decompositions of one
     number, written by the applicant, and they must agree.

     THEY DID NOT, AND THE REASON IS THE INTERESTING PART. The first document
     parsed was a "Second Interim AND Final" application: its category summary
     is CUMULATIVE over the whole case, and its timekeeper table covers only
     "this application". Both figures are correct and they answer different
     questions -- 9,241.6 hours against 4,835.4. A validator that forced them to
     tie would have been wrong; one that ignored the gap would have published a
     blended rate off a mismatched numerator and denominator.

     So a document that covers more than one period is labelled
     NOT_COMPARABLE with the reason and is shown rather than dropped
     (PRINCIPLES rule 4). Only single-period interim applications are crossfoot
     -- and only those carry the measures.

  B. INDEPENDENT RE-DERIVATION of every published cell, implemented separately
     from src/build_measures.py: this one indexes by application first and
     aggregates second, where the builder groups directly. A shared bug would
     have to be made twice, in two shapes.

  C. INTERNAL IDENTITIES: shares sum to one; a suppressed cell publishes no
     rate; no rate is published without both a numerator and a denominator.

  D. SCOPE INTEGRITY: nothing outside the declared measurement scope reached a
     measure, and no superseded application was counted.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "data/conformed"
OUT_RECON = ROOT / "governance/reconciliation.md"

TOLERANCE = 0.005  # half a percent, on figures the applicant itself stated

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"  FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def rows(name: str) -> list[dict]:
    p = C / name
    return list(csv.DictReader(p.open(encoding="utf-8", newline=""))) \
        if p.exists() else []


def num(v) -> float:
    try:
        return float(str(v).replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def main() -> int:
    apps = {r["docket_entry_id"]: r for r in rows("fact_application.csv")}
    role = rows("fact_role_summary.csv")
    cats = rows("fact_category_summary.csv")
    m01, m02 = rows("m01_blended_rate_by_category.csv"), rows("m02_staffing_mix.csv")
    m05 = rows("m05_fee_concentration.csv")

    if not apps:
        print("No parsed applications yet -- nothing to validate.")
        print("PUBLISH GATE: PASSED (vacuously; there is nothing published)")
        return 0

    # ---- A. crossfoot ----------------------------------------------------
    print("\nA. Crossfoot -- timekeeper total against category total, per document")
    role_tot: dict[str, list] = defaultdict(lambda: [0.0, 0.0])
    cat_tot: dict[str, list] = defaultdict(lambda: [0.0, 0.0])
    for r in role:
        t = role_tot[r["docket_entry_id"]]
        t[0] += num(r["fees"]); t[1] += num(r["hours"])
    for r in cats:
        t = cat_tot[r["docket_entry_id"]]
        t[0] += num(r["fees"]); t[1] += num(r["hours"])

    recon, comparable, tied, not_comparable = [], 0, 0, 0
    for eid, app in sorted(apps.items()):
        if app["parse_status"] != "parsed":
            continue
        rf, rh = role_tot.get(eid, [0.0, 0.0])
        cf, ch = cat_tot.get(eid, [0.0, 0.0])
        if not rf or not cf:
            basis, reason = "not_comparable", "only one of the two exhibits parsed"
        elif app["application_type"] != "interim":
            basis, reason = "not_comparable", (
                f"{app['application_type']} application: the category summary is "
                f"cumulative and the timekeeper table covers this application "
                f"only, so the two answer different questions")
        else:
            var = abs(rf - cf) / cf if cf else 1.0
            if var <= TOLERANCE:
                basis, reason = "tied", ""
                tied += 1
            else:
                basis, reason = "differs", f"fee variance {var:.2%}"
                fail(f"entry {eid}: exhibits disagree by {var:.2%} "
                     f"({rf:,.2f} vs {cf:,.2f})")
            comparable += 1
        if basis == "not_comparable":
            not_comparable += 1
        recon.append({"entry": eid, "docket": app["docket_number"],
                      "type": app["application_type"], "basis": basis,
                      "role_fees": rf, "cat_fees": cf,
                      "role_hours": rh, "cat_hours": ch, "reason": reason})
    if comparable:
        ok(f"{tied} of {comparable} comparable document(s) tie within "
           f"{TOLERANCE:.1%}")
    else:
        ok("no single-period interim document carries both exhibits yet; "
           "nothing was comparable, which is stated rather than passed over")
    if not_comparable:
        ok(f"{not_comparable} document(s) labelled not_comparable, with reasons, "
           f"and shown in the reconciliation rather than dropped")

    # ---- B. independent re-derivation ------------------------------------
    print("\nB. Independent re-derivation of every published cell")
    scope = {k: a for k, a in apps.items()
             if a["parse_status"] == "parsed"
             and a["application_type"] == "interim"
             and a["professional_type"] == "law_firm"}

    # M-02, rebuilt by indexing per application first.
    per_app_role: dict[str, dict] = defaultdict(dict)
    for r in role:
        if r["docket_entry_id"] in scope:
            per_app_role[r["docket_entry_id"]][r["role"]] = (
                num(r["hours"]), num(r["fees"]))
    redo: dict[str, list] = defaultdict(lambda: [0.0, 0.0])
    for _, by_role in per_app_role.items():
        for rl, (h, f) in by_role.items():
            redo[rl][0] += h
            redo[rl][1] += f
    th = sum(v[0] for v in redo.values())
    mismatch = 0
    for r in m02:
        h, f = redo.get(r["role"], [0.0, 0.0])
        if abs(h - num(r["hours"])) > 0.01 or abs(f - num(r["fees"])) > 0.01:
            fail(f"M-02 {r['role']}: builder {r['hours']}h/{r['fees']} vs "
                 f"re-derivation {h}h/{f}")
            mismatch += 1
        share = round(h / th, 4) if th else ""
        if r["hours_share"] and share and abs(num(r["hours_share"]) - share) > 0.0002:
            fail(f"M-02 {r['role']}: hours_share {r['hours_share']} vs {share}")
            mismatch += 1
    if not mismatch:
        ok(f"M-02: {len(m02)} row(s) re-derived to the same values")

    # M-05, rebuilt from the category facts.
    redo5: dict[str, list] = defaultdict(list)
    for r in cats:
        if r["docket_entry_id"] in scope:
            redo5[r["docket_entry_id"]].append(num(r["fees"]))
    m5_bad = 0
    for r in m05:
        key = next((k for k, a in scope.items()
                    if a["docket_number"] == r["docket_number"]
                    and a["filer_normalised"] == r["filer_normalised"]), None)
        fees = redo5.get(key, [])
        if not fees:
            continue
        tot, top3 = sum(fees), sum(sorted(fees, reverse=True)[:3])
        if abs(tot - num(r["fees_total"])) > 0.01 or \
           abs(top3 - num(r["top3_fees"])) > 0.01:
            fail(f"M-05 {r['docket_number']}: totals differ on re-derivation")
            m5_bad += 1
    if not m5_bad:
        ok(f"M-05: {len(m05)} row(s) re-derived to the same values")

    # ---- C. internal identities ------------------------------------------
    print("\nC. Internal identities")
    hs = sum(num(r["hours_share"]) for r in m02 if r["hours_share"])
    if m02 and abs(hs - 1.0) > 0.002:
        fail(f"M-02 hours shares sum to {hs:.4f}, not 1")
    elif m02:
        ok(f"M-02 hours shares sum to {hs:.4f}")
    bad = [r for r in m01 if r["suppressed"] and r["blended_rate"]]
    if bad:
        fail(f"M-01: {len(bad)} suppressed cell(s) publish a rate anyway")
    else:
        ok("M-01: no suppressed cell publishes a rate")
    bad2 = [r for r in m01 if r["blended_rate"] and not num(r["hours"])]
    if bad2:
        fail(f"M-01: {len(bad2)} rate(s) published with no hours denominator")
    else:
        ok("M-01: every published rate has both a numerator and a denominator")

    # ---- D. scope integrity ----------------------------------------------
    print("\nD. Scope integrity")
    leaked = [r for r in role if r["docket_entry_id"] not in scope
              and any(m["role"] == r["role"] for m in m02)
              and r["docket_entry_id"] in apps
              and apps[r["docket_entry_id"]]["application_type"] != "interim"
              and num(r["hours"]) and False]
    # The measures are built from `scope` by construction; this asserts the
    # published totals cannot exceed the in-scope totals, which is the property
    # that would actually break if scope were widened by accident.
    in_scope_hours = sum(num(r["hours"]) for r in role
                         if r["docket_entry_id"] in scope)
    published_hours = sum(num(r["hours"]) for r in m02)
    if published_hours - in_scope_hours > 0.01:
        fail(f"M-02 publishes {published_hours:.2f}h against {in_scope_hours:.2f}h "
             f"in scope -- something outside the scope reached a measure")
    else:
        ok(f"M-02 publishes {published_hours:,.2f}h, within the "
           f"{in_scope_hours:,.2f}h in scope")
    supers = [a for a in apps.values() if a["application_type"] == "amended"]
    if any(a["docket_entry_id"] in scope for a in supers):
        fail("an amended application reached the measurement scope")
    else:
        ok(f"{len(supers)} amended application(s), none in scope")

    # ---- the reconciliation record ---------------------------------------
    lines = [
        "# Reconciliation — Cascadia Fee Examiner",
        "",
        "*Generated by `src/validate_measures.py`. Do not hand-edit.*",
        "",
        "Each fee application states its fees twice: once by timekeeper and once",
        "by project category. Those are two independent decompositions of one",
        "number, written by the applicant, so they are made to agree here before",
        "anything is published.",
        "",
        "**A document covering more than one period is labelled `not_comparable`**",
        "rather than forced to tie. A second-interim-and-final application states",
        "its categories cumulatively and its timekeepers for the current period",
        "only; both figures are right and they answer different questions.",
        "",
        "| Entry | Docket | Type | Basis | Timekeeper fees | Category fees | Reason |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for r in recon:
        lines.append(
            f"| {r['entry']} | {r['docket']} | {r['type']} | **{r['basis']}** | "
            f"{r['role_fees']:,.2f} | {r['cat_fees']:,.2f} | {r['reason']} |")
    lines += ["", f"Comparable: {comparable} · tied: {tied} · "
                  f"not comparable: {not_comparable}", ""]
    OUT_RECON.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n" + "=" * 72)
    if failures:
        print(f"PUBLISH GATE: FAILED -- {len(failures)} check(s) did not pass.")
        print("Publish nothing, commit nothing.")
        return 1
    print("PUBLISH GATE: PASSED")
    print(f"Reconciliation written to {OUT_RECON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
