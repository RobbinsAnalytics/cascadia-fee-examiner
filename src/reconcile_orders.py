#!/usr/bin/env python3
"""Stage 5, V-2 -- what was requested against what the court allowed. Offline.

    Nothing in the portfolio currently states a variance rate against an answer
    key it did not itself produce. This does, and it is honest about how few
    pairs it can make and why.

THE PAIRING RULE, STATED SO IT CAN BE ARGUED WITH

An application and an order are paired when, and only when:

  1. they sit on the same docket (court_id + docket_number);
  2. the order names exactly ONE fee award (not omnibus);
  3. the order's filer string resolves to the same firm key as the
     application's, OR both filer strings are non-empty and identical after
     the resolver's own normalisation;
  4. the order's basis matches the application's type (interim to interim,
     final to final), or the order states no basis.

Anything that fails a rule is written out as `not_paired` with the rule number,
so the pairing rate is published beside the variance rate. A pairing made by a
looser rule would produce a better-looking table and a worse claim.

THE REQUESTED FIGURE is the application's own timekeeper total where its
exhibit parsed. It is fees only, never fees and expenses, because the order
states those separately and this compares like with like.
"""

from __future__ import annotations

import csv
import sys
import unicodedata
import re
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "data/conformed"
OUT = C / "v2_requested_vs_allowed.csv"
RECON = ROOT / "governance/reconciliation.md"

FIELDS = ["court_id", "docket_number", "application_entry_id", "order_entry_id",
          "filer_normalised", "application_type", "order_basis",
          "fees_requested", "fees_allowed", "cut_absolute", "cut_pct",
          "status", "rule"]

SUFFIXES = {"llp", "llc", "lp", "pc", "plc", "pllc", "ltd", "inc", "pa",
            "chartered", "international", "co", "corp"}


def rows(name: str) -> list[dict]:
    p = C / name
    return list(csv.DictReader(p.open(encoding="utf-8", newline=""))) \
        if p.exists() else []


def key(name: str) -> str:
    s = unicodedata.normalize("NFKD", name or "").lower().replace("&", " and ")
    toks = [t for t in re.sub(r"[^a-z0-9]+", " ", s).split()
            if t not in SUFFIXES and len(t) >= 3]
    return " ".join(toks)


def num(v) -> float | None:
    try:
        return float(str(v).replace(",", "")) if str(v).strip() else None
    except ValueError:
        return None


def main() -> int:
    apps = [a for a in rows("fact_application.csv")
            if a["parse_status"] == "parsed" and a["entry_class"] != "order"]
    orders = [o for o in rows("fact_order.csv") if o["parse_status"] == "parsed"]

    by_docket_orders: dict[tuple, list] = defaultdict(list)
    for o in orders:
        by_docket_orders[(o["court_id"], o["docket_number"])].append(o)

    out, paired = [], 0
    for a in apps:
        cands = by_docket_orders.get((a["court_id"], a["docket_number"]), [])
        if not cands:
            out.append({**base(a), "status": "not_paired",
                        "rule": "1: no parsed order on this docket"})
            continue
        chosen, why = None, ""
        for o in cands:
            if o["omnibus"] == "true":
                why = "2: order is omnibus"
                continue
            if not (a["filer_normalised"] and o["filer_normalised"]
                    and key(a["filer_normalised"]) == key(o["filer_normalised"])):
                why = "3: filer strings do not resolve to one firm"
                continue
            if o["basis"] and o["basis"] != a["application_type"]:
                why = "4: order basis differs from application type"
                continue
            chosen = o
            break
        if not chosen:
            out.append({**base(a), "status": "not_paired", "rule": why or "1"})
            continue
        req, allowed = num(a["total_fees_stated"]), num(chosen["fees_allowed"])
        if req is None or allowed is None:
            out.append({**base(a, chosen), "status": "not_comparable",
                        "rule": "requested or allowed figure did not parse"})
            continue
        cut = req - allowed
        out.append({**base(a, chosen),
                    "fees_requested": f"{req:.2f}", "fees_allowed": f"{allowed:.2f}",
                    "cut_absolute": f"{cut:.2f}",
                    "cut_pct": f"{cut / req:.4f}" if req else "",
                    "status": "paired", "rule": "1-4"})
        paired += 1

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in out:
            w.writerow({f: r.get(f, "") for f in FIELDS})

    reasons = defaultdict(int)
    for r in out:
        if r["status"] != "paired":
            reasons[r["rule"]] += 1

    lines = ["", "## V-2 · Requested against allowed", "",
             "*The court's order is the answer key: a different author than the "
             "application it responds to.*", "",
             f"Parsed applications: {len(apps)} · parsed orders: {len(orders)} · "
             f"**paired: {paired}**", ""]
    if reasons:
        lines += ["| Why not paired | Applications |", "|---|---:|"]
        lines += [f"| {k} | {v} |" for k, v in sorted(reasons.items())]
        lines.append("")
    if paired:
        lines += ["| Docket | Filer | Type | Requested | Allowed | Cut |",
                  "|---|---|---|---:|---:|---:|"]
        for r in out:
            if r["status"] == "paired":
                lines.append(f"| {r['docket_number']} | {r['filer_normalised'][:40]} | "
                             f"{r['application_type']} | {float(r['fees_requested']):,.2f} | "
                             f"{float(r['fees_allowed']):,.2f} | {float(r['cut_pct']):.2%} |")
    text = RECON.read_text(encoding="utf-8") if RECON.exists() else ""
    text = text.split("\n## V-2 ")[0].rstrip("\n") + "\n" + "\n".join(lines) + "\n"
    RECON.write_text(text, encoding="utf-8")

    print(f"Applications : {len(apps)}   orders parsed: {len(orders)}")
    print(f"Paired       : {paired}")
    for k, v in sorted(reasons.items()):
        print(f"  not paired, rule {k}: {v}")
    for r in out:
        if r["status"] == "paired":
            print(f"  {r['docket_number']} {r['filer_normalised'][:30]:<30} requested "
                  f"{float(r['fees_requested']):>13,.2f} allowed {float(r['fees_allowed']):>13,.2f} "
                  f"cut {float(r['cut_pct']):.2%}")
    return 0


def base(a: dict, o: dict | None = None) -> dict:
    return {"court_id": a["court_id"], "docket_number": a["docket_number"],
            "application_entry_id": a["docket_entry_id"],
            "order_entry_id": o["docket_entry_id"] if o else "",
            "filer_normalised": a["filer_normalised"],
            "application_type": a["application_type"],
            "order_basis": o["basis"] if o else ""}


if __name__ == "__main__":
    raise SystemExit(main())
