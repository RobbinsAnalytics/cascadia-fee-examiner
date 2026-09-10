#!/usr/bin/env python3
"""Stage 4 -- firm identity across sources that share no key. Offline.

    THE RULES ARE IN governance/entity-resolution.md AND WERE COMMITTED BEFORE
    THIS SCRIPT RAN. This file implements them; it does not decide them. If a
    rule here differs from that document, the document is right and this is the
    defect.

WHAT IS BEING RESOLVED

  left   dim_case.DipAtty / CommCredAtty -- the database's short editorial form
         ("Kirkland Ellis", "Weil Gotshal", "Pachulski Stang"): no punctuation,
         no entity suffix, often two surnames of a four-surname firm.

  right  filer_normalised -- the docket caption's form ("Kirkland & Ellis LLP
         and Kirkland & Ellis International LLP").

Two systems, two owners, no shared identifier, and neither side is wrong.

WHY SUBSET AND NOT A SIMILARITY SCORE

The database name is systematically SHORTER than the caption, so containment is
the actual relationship and a threshold would be a number nobody could justify.
{kirkland, ellis} is a subset of {kirkland, ellis, and, kirkland, ellis}. A
score would need to explain why 0.82 resolves and 0.79 does not.

THE GUARD THAT MATTERS: a subset match on a SINGLE token would resolve "Jones"
to "Jones Day" -- and to "Jones Walker" in the same docket. Single-token matches
are refused unless the token is unique across every caption in that docket.

PERSON-NAME CONTROL: the archive's `attorney` field names individual people and
is never read here. The only inputs are two organisation columns from the spine
and a caption-derived firm string.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SPINE = ROOT / "data/conformed/dim_case.csv"
MANIFEST = ROOT / "data/raw/recap/manifest.csv"
OVERRIDES = ROOT / "data/reference/firm_alias_overrides.csv"
OUT_FIRM = ROOT / "data/conformed/dim_firm.csv"
OUT_BRIDGE = ROOT / "data/conformed/bridge_firm_alias.csv"
OUT_UNRESOLVED = ROOT / "data/conformed/unresolved_firms.csv"
OUT_STATS = ROOT / "data/conformed/resolution_stats.json"

SUFFIXES = {"llp", "llc", "lp", "pc", "plc", "pllc", "ltd", "inc", "pa",
            "chartered", "international", "co", "corp"}
ROLE_WORDS = {"attorneys", "attorney", "counsel", "for", "the", "debtors",
              "debtor", "committee", "official", "unsecured", "creditors",
              "creditor", "possession", "and", "of", "to", "as", "special",
              "local", "conflicts", "co"}

FIRM_FIELDS = ["firm_key", "canonical_name", "source", "dockets", "applications"]
BRIDGE_FIELDS = ["firm_key", "brd_name", "caption_name", "court_id",
                 "docket_number", "match_rule", "matched_tokens"]
UNRESOLVED_FIELDS = ["caption_name", "court_id", "docket_number",
                     "documents", "candidate_brd_names", "reason"]


def normalise(name: str) -> list[str]:
    """Steps 1 to 5 of R-1b, in the order the rule states them."""
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", " ", s)
    tokens = [t for t in s.split() if t]
    tokens = [t for t in tokens if t not in SUFFIXES]
    tokens = [t for t in tokens if t not in ROLE_WORDS]
    tokens = [t for t in tokens if len(t) >= 3]
    return tokens


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit("FAIL: no corpus manifest. Run pull_fee_applications.py.")

    spine = {r["PrimaryKey"]: r for r in
             csv.DictReader(SPINE.open(encoding="utf-8", newline=""))}
    docs = list(csv.DictReader(MANIFEST.open(encoding="utf-8", newline="")))
    overrides = {}
    if OVERRIDES.exists():
        for r in csv.DictReader(OVERRIDES.open(encoding="utf-8", newline="")):
            if not r.get("reason", "").strip():
                raise SystemExit(
                    f"FAIL (ER-2): override {r} has no reason. "
                    f"An override without a stated reason is indistinguishable "
                    f"from a fudge.")
            overrides[(r["brd_name"].strip(), r["caption_name"].strip())] = r["reason"]

    # Captions per docket, so single-token uniqueness can be tested per docket.
    captions_by_docket: dict[tuple, set] = defaultdict(set)
    docs_by_caption: dict[tuple, int] = defaultdict(int)
    for d in docs:
        if not d["filer_normalised"].strip():
            continue
        key = (d["court_id"], d["docket_number"])
        captions_by_docket[key].add(d["filer_normalised"].strip())
        docs_by_caption[(key, d["filer_normalised"].strip())] += 1

    bridge, unresolved = [], []
    firms: dict[str, dict] = {}
    single_token_rejects = 0

    for (court, docket), captions in sorted(captions_by_docket.items()):
        case = next((c for c in spine.values()
                     if c["court_id"] == court and c["CaseNum"] == docket), None)
        brd_names = []
        if case:
            for col in ("DipAtty", "CommCredAtty"):
                v = (case.get(col) or "").strip()
                if v:
                    brd_names.append(v)

        # Token frequency across this docket's captions, for the R-1b guard.
        token_dockets: dict[str, int] = defaultdict(int)
        for cap in captions:
            for t in set(normalise(cap)):
                token_dockets[t] += 1

        for cap in sorted(captions):
            cap_tokens = normalise(cap)
            cap_set = set(cap_tokens)
            matched = None
            for brd in brd_names:
                if (brd, cap) in overrides:
                    matched = (brd, "override", sorted(cap_set))
                    break
                brd_tokens = set(normalise(brd))
                if not brd_tokens or not brd_tokens <= cap_set:
                    continue
                if len(brd_tokens) == 1:
                    tok = next(iter(brd_tokens))
                    if token_dockets.get(tok, 0) > 1:
                        # ER-3: refuse. "Jones" would take Jones Day and
                        # Jones Walker in the same docket.
                        single_token_rejects += 1
                        continue
                    matched = (brd, "single_token_unique_in_docket",
                               sorted(brd_tokens))
                    break
                matched = (brd, "token_subset", sorted(brd_tokens))
                break

            if matched:
                brd, rule, toks = matched
                firm_key = "-".join(normalise(brd)) or "unknown"
                firms.setdefault(firm_key, {
                    "firm_key": firm_key, "canonical_name": brd,
                    "source": "brd", "dockets": set(), "applications": 0})
                firms[firm_key]["dockets"].add((court, docket))
                firms[firm_key]["applications"] += docs_by_caption[
                    ((court, docket), cap)]
                bridge.append({
                    "firm_key": firm_key, "brd_name": brd, "caption_name": cap,
                    "court_id": court, "docket_number": docket,
                    "match_rule": rule, "matched_tokens": " ".join(toks)})
            else:
                unresolved.append({
                    "caption_name": cap, "court_id": court,
                    "docket_number": docket,
                    "documents": docs_by_caption[((court, docket), cap)],
                    "candidate_brd_names": " | ".join(brd_names) or "(none)",
                    "reason": ("no database firm name for this case"
                               if not brd_names else
                               "no database name's tokens are a subset of the "
                               "caption -- most often a co-counsel, local or "
                               "conflicts firm the database never recorded"),
                })

    for path, fields, data in (
        (OUT_BRIDGE, BRIDGE_FIELDS, sorted(bridge, key=lambda r: r["firm_key"])),
        (OUT_UNRESOLVED, UNRESOLVED_FIELDS,
         sorted(unresolved, key=lambda r: -r["documents"])),
        (OUT_FIRM, FIRM_FIELDS,
         [{"firm_key": v["firm_key"], "canonical_name": v["canonical_name"],
           "source": v["source"], "dockets": len(v["dockets"]),
           "applications": v["applications"]}
          for v in sorted(firms.values(), key=lambda x: x["firm_key"])]),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(data)

    total = len(bridge) + len(unresolved)
    stats = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "caption_firm_pairs": total,
        "resolved": len(bridge),
        "unresolved": len(unresolved),
        "match_rate": round(len(bridge) / total, 4) if total else None,
        "unresolved_rate": round(len(unresolved) / total, 4) if total else None,
        "by_rule": {r: sum(1 for b in bridge if b["match_rule"] == r)
                    for r in sorted({b["match_rule"] for b in bridge})},
        "single_token_matches_refused": single_token_rejects,
        "overrides_used": sum(1 for b in bridge if b["match_rule"] == "override"),
        "distinct_firms": len(firms),
    }
    OUT_STATS.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    # ER-1: the unresolved rate is published with examples, or the build fails.
    if total and len(unresolved) == 0:
        print("\nNOTE: every caption resolved. That is a finding about the RULE, "
              "not a certificate about the data -- see entity-resolution.md, "
              "'what failure looks like'. Check the rule before believing it.")
    if total and len(bridge) and not OUT_UNRESOLVED.exists():
        raise SystemExit("FAIL (ER-1): no unresolved file was written")

    print(f"Caption/firm pairs      : {total}")
    print(f"  resolved              : {len(bridge)}  "
          f"({stats['match_rate'] or 0:.1%})")
    print(f"  unresolved            : {len(unresolved)}  "
          f"({stats['unresolved_rate'] or 0:.1%})")
    print(f"  single-token refused  : {single_token_rejects}")
    print(f"Distinct firms resolved : {len(firms)}")
    if stats["by_rule"]:
        print("By rule:")
        for k, v in stats["by_rule"].items():
            print(f"  {k:<32} {v}")
    if unresolved:
        print("\nUnresolved, most documents first:")
        for u in unresolved[:8]:
            print(f"  {u['caption_name'][:56]:<56} {u['documents']:>2} doc(s)")
            print(f"      candidates: {u['candidate_brd_names'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
