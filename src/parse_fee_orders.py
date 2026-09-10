#!/usr/bin/env python3
"""Stage 5 -- read what the COURT allowed out of each stored fee order. Offline.

    The order is the answer key. It is written by a different author than the
    application it responds to, and the difference between what was asked and
    what was allowed is the first defect rate in this portfolio measured against
    a key the module did not itself produce.

WHAT AN ORDER SAYS, AND HOW MUCH OF IT THIS READS

The operative language is regular across courts:

    "... allowed, on an interim basis, compensation in the amount of $608,524.00
     ... reimbursement of ... expenses ... in the amount of $1,547.19"

Every "in the amount of $X" clause is captured with the 160 characters before
it, and each is classed as fees, expenses, or a total from that context. The
basis (interim / final) is read from the same sentence where present.

OMNIBUS ORDERS. Many orders award several professionals at once, one paragraph
or one table row each. This parser records EVERY award it finds and flags the
order `omnibus` when more than one distinct fee award appears. Attributing each
award to its applicant is a resolution problem in its own right; here the
document-level facts are captured and the attribution is left explicit in
src/reconcile_orders.py, where a single-award order against a single filer is
the only pairing made without a rule to argue about.

PERSON-NAME CONTROL. Orders name the judge who signed them and the attorneys
who submitted them. Nothing from an order is written except amounts, a basis,
a count and the docket keys the manifest already carries.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data/raw/recap/manifest.csv"
OUT = ROOT / "data/conformed/fact_order.csv"

FIELDS = ["docket_entry_id", "case_primary_key", "court_id", "docket_number",
          "document_number", "filer_normalised", "professional_type",
          "basis", "fees_allowed", "expenses_allowed", "total_allowed",
          "fee_awards_found", "omnibus", "parse_status"]

AMOUNT = re.compile(r"in\s+the\s+(?:total\s+|aggregate\s+)?amount\s+of\s+\$\s?([\d,]+(?:\.\d{2})?)",
                    re.I)


def to_float(s: str) -> float:
    return float(s.replace(",", ""))


def classify_clause(ctx: str) -> str:
    c = ctx.lower()
    if re.search(r"expense|reimburse|disbursement", c) and not re.search(
            r"compensation|fees?\b", c[-90:]):
        return "expenses"
    if re.search(r"totaling|total\s+(?:of|amount)|aggregate", c[-60:]):
        return "total"
    if re.search(r"compensation|fees?\b|services", c):
        return "fees"
    return "unknown"


def main() -> int:
    try:
        import pymupdf  # type: ignore
    except ImportError:  # pragma: no cover
        import fitz as pymupdf  # type: ignore

    docs = [r for r in csv.DictReader(MANIFEST.open(encoding="utf-8", newline=""))
            if r["entry_class"] == "order"]
    rows = []
    for d in docs:
        path = ROOT / d["path"]
        base = {k: d.get(k, "") for k in FIELDS[:7]}
        if not path.exists():
            rows.append({**base, "basis": "", "fees_allowed": "",
                         "expenses_allowed": "", "total_allowed": "",
                         "fee_awards_found": 0, "omnibus": "",
                         "parse_status": "absent"})
            continue
        doc = pymupdf.open(path)
        flat = re.sub(r"\s+", " ", " ".join(p.get_text() for p in doc))
        if len(flat) < 200:
            rows.append({**base, "basis": "", "fees_allowed": "",
                         "expenses_allowed": "", "total_allowed": "",
                         "fee_awards_found": 0, "omnibus": "",
                         "parse_status": "image_only"})
            continue

        fees, expenses, totals = [], [], []
        for m in AMOUNT.finditer(flat):
            ctx = flat[max(0, m.start() - 160):m.start()]
            kind = classify_clause(ctx)
            amt = to_float(m.group(1))
            {"fees": fees, "expenses": expenses, "total": totals}.get(kind, []).append(amt)

        basis = ""
        b = re.search(r"(?i)allowed,?\s+on\s+an?\s+(interim|final)\s+basis", flat)
        if b:
            basis = b.group(1).lower()
        elif re.search(r"(?i)\bfinal\s+(?:fee\s+)?application|final\s+allowance", flat):
            basis = "final"
        elif re.search(r"(?i)\binterim\b", flat):
            basis = "interim"

        distinct_fees = sorted(set(fees))
        status = "parsed" if fees else "unparsed"
        rows.append({
            **base,
            "basis": basis,
            # One distinct award, one figure. More than one is left BLANK, not
            # summed: an omnibus order awards several professionals, and a
            # single-applicant final order restates each interim period's award
            # cumulatively -- a sum is wrong in both cases, and a blank says
            # "not attributable" rather than inventing a total.
            "fees_allowed": f"{distinct_fees[0]:.2f}" if len(distinct_fees) == 1 else "",
            "expenses_allowed": f"{sum(set(expenses)):.2f}" if expenses else "",
            "total_allowed": f"{max(totals):.2f}" if totals else "",
            "fee_awards_found": len(distinct_fees),
            "omnibus": "true" if len(distinct_fees) > 1 else "false",
            "parse_status": status,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    parsed = sum(1 for r in rows if r["parse_status"] == "parsed")
    omni = sum(1 for r in rows if r["omnibus"] == "true")
    print(f"Orders in corpus : {len(rows)}")
    print(f"  parsed         : {parsed}  (omnibus {omni}, single-award {parsed - omni})")
    print(f"  unparsed       : {sum(1 for r in rows if r['parse_status'] == 'unparsed')}")
    print(f"  absent         : {sum(1 for r in rows if r['parse_status'] == 'absent')}")
    for r in rows:
        if r["parse_status"] == "parsed":
            print(f"  {r['court_id']} {r['docket_number']} doc {r['document_number']:<6} "
                  f"{r['basis'] or '-':<8} fees ${float(r['fees_allowed'] or 0):>13,.2f}  "
                  f"awards {r['fee_awards_found']}  {r['filer_normalised'][:32]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
