#!/usr/bin/env python3
"""Stage 3b -- the certified measures. Offline; reads the conformed facts.

Every figure this module publishes is computed here from a committed artifact.
Nothing downstream types a number. Definitions, owners, lineage and limits are
in governance/metric_register.md; a figure that appears in an output and is not
defined there is not certified and must not be published.

    M-01  Blended hourly rate by conformed project category
    M-02  Staffing mix -- share of hours by conformed role
    M-03  Rate progression across successive applications by one filer
    M-05  Fee concentration -- share of fees in the top three categories

M-04, public-record coverage, is built by src/build_coverage.py because it is
computable before a single PDF is parsed and is the measure the others must be
read against.

    SUPPRESSION IS A RULE HERE, NOT A JUDGMENT CALL. Coverage is bimodal, so a
    year or a court can easily resolve to one case and one firm. Every cell
    carries its own n, and a cell below MIN_APPLICATIONS is written with its
    counts and a blank rate rather than dropped -- a dropped cell reads as
    "nothing here" and an empty rate reads as "not enough to say", which are
    different claims (PRINCIPLES rule 3).
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
ROLE = ROOT / "data/conformed/fact_role_summary.csv"
CATEGORY = ROOT / "data/conformed/fact_category_summary.csv"
APP = ROOT / "data/conformed/fact_application.csv"
FIRM_MAP = ROOT / "data/reference/firm_category_to_ustp.csv"
CROSSWALK = ROOT / "data/reference/crosswalk_task_codes.csv"
MEASURES_MANIFEST = ROOT / "data/conformed/measures_manifest.json"

OUT_M01 = ROOT / "data/conformed/m01_blended_rate_by_category.csv"
OUT_M02 = ROOT / "data/conformed/m02_staffing_mix.csv"
OUT_M03 = ROOT / "data/conformed/m03_rate_progression.csv"
OUT_M05 = ROOT / "data/conformed/m05_fee_concentration.csv"
OUT_UNMAPPED = ROOT / "data/conformed/unmapped_categories.csv"

MIN_APPLICATIONS = 3

M01_FIELDS = ["ustp_category", "applications", "firms", "hours", "fees",
              "blended_rate", "suppressed"]
M02_FIELDS = ["role", "applications", "firms", "timekeepers", "hours", "fees",
              "hours_share", "fees_share", "rate_min", "rate_max"]
M03_FIELDS = ["court_id", "docket_number", "filer_normalised", "role",
              "applications", "first_rate_max", "last_rate_max",
              "change_absolute", "change_pct"]
M05_FIELDS = ["court_id", "docket_number", "filer_normalised", "categories",
              "fees_total", "top3_fees", "top3_share"]
UNMAPPED_FIELDS = ["category_as_filed", "occurrences", "hours", "fees",
                   "reason"]


def rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return list(csv.DictReader(path.open(encoding="utf-8", newline="")))


def num(v) -> float:
    try:
        return float(str(v).replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def load_firm_map() -> list[tuple]:
    out = []
    for r in rows(FIRM_MAP):
        out.append((re.compile(r["firm_pattern"]),
                    r["category_as_filed"].strip().lower(),
                    r["ustp_category"], r["match_type"]))
    return out


def conform_category(firm: str, category: str, mapping: list[tuple]) -> tuple:
    key = (category or "").strip().lower()
    for firm_rx, cat, ustp, mtype in mapping:
        if cat == key and firm_rx.search(firm or ""):
            return ustp, mtype
    return "", ""


def write(path: Path, fields: list[str], data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(data)


def main() -> int:
    role_rows = rows(ROLE)
    cat_rows = rows(CATEGORY)
    app_rows = rows(APP)
    mapping = load_firm_map()

    # ---- Applications in scope for measurement --------------------------
    # An amended application supersedes the one it amends, and a final
    # application re-presents every interim period it covers. Summing them
    # double-counts, so only non-superseded INTERIM applications carry the
    # measures, and the register says so.
    parsed_apps = {r["docket_entry_id"]: r for r in app_rows
                   if r["parse_status"] == "parsed"}
    # INTERIM ONLY. A final application re-presents every interim period it
    # covers, and a second-interim-and-final application states its categories
    # cumulatively while its timekeeper table covers the current period only --
    # so including finals both double-counts and mismatches a numerator to a
    # denominator. An amended application supersedes the one it amends. Both are
    # excluded here and both are counted in the manifest, because "excluded" and
    # "not present" are different claims.
    scope = {k: r for k, r in parsed_apps.items()
             if r["application_type"] == "interim"
             and r["professional_type"] == "law_firm"}
    excluded = {t: sum(1 for r in parsed_apps.values()
                       if r["application_type"] == t)
                for t in ("final", "amended", "order")}
    print(f"Applications parsed        : {len(parsed_apps)}")
    print(f"  in measurement scope     : {len(scope)} "
          f"(law firms; single-period interim only)")
    print(f"  excluded by type         : "
          + ", ".join(f"{k} {v}" for k, v in excluded.items()))

    # ---- M-01 blended rate by conformed category ------------------------
    by_cat: dict[str, dict] = defaultdict(
        lambda: {"apps": set(), "firms": set(), "hours": 0.0, "fees": 0.0})
    unmapped: dict[str, dict] = defaultdict(
        lambda: {"occurrences": 0, "hours": 0.0, "fees": 0.0})
    for r in cat_rows:
        if r["docket_entry_id"] not in scope:
            continue
        ustp, _ = conform_category(r["filer_normalised"],
                                   r["category_as_filed"], mapping)
        if not ustp:
            u = unmapped[r["category_as_filed"]]
            u["occurrences"] += 1
            u["hours"] += num(r["hours"])
            u["fees"] += num(r["fees"])
            continue
        b = by_cat[ustp]
        b["apps"].add(r["docket_entry_id"])
        b["firms"].add(r["filer_normalised"])
        b["hours"] += num(r["hours"])
        b["fees"] += num(r["fees"])

    m01 = []
    for ustp, b in sorted(by_cat.items()):
        enough = len(b["apps"]) >= MIN_APPLICATIONS
        m01.append({
            "ustp_category": ustp,
            "applications": len(b["apps"]), "firms": len(b["firms"]),
            "hours": round(b["hours"], 2), "fees": round(b["fees"], 2),
            "blended_rate": (round(b["fees"] / b["hours"], 2)
                             if enough and b["hours"] else ""),
            "suppressed": "" if enough else
            f"fewer than {MIN_APPLICATIONS} applications",
        })
    write(OUT_M01, M01_FIELDS, m01)
    write(OUT_UNMAPPED, UNMAPPED_FIELDS,
          [{"category_as_filed": k, "occurrences": v["occurrences"],
            "hours": round(v["hours"], 2), "fees": round(v["fees"], 2),
            "reason": "no row in data/reference/firm_category_to_ustp.csv"}
           for k, v in sorted(unmapped.items(), key=lambda t: -t[1]["fees"])])

    # ---- M-02 staffing mix ----------------------------------------------
    by_role: dict[str, dict] = defaultdict(
        lambda: {"apps": set(), "firms": set(), "tk": 0, "hours": 0.0,
                 "fees": 0.0, "rmin": None, "rmax": None})
    for r in role_rows:
        if r["docket_entry_id"] not in scope:
            continue
        b = by_role[r["role"]]
        b["apps"].add(r["docket_entry_id"])
        b["firms"].add(r["filer_normalised"])
        b["tk"] += int(num(r["timekeepers"]))
        b["hours"] += num(r["hours"])
        b["fees"] += num(r["fees"])
        for key, col in (("rmin", "rate_min"), ("rmax", "rate_max")):
            v = num(r[col])
            if v:
                b[key] = v if b[key] is None else (
                    min(b[key], v) if key == "rmin" else max(b[key], v))
    total_hours = sum(b["hours"] for b in by_role.values())
    total_fees = sum(b["fees"] for b in by_role.values())
    m02 = [{
        "role": role, "applications": len(b["apps"]), "firms": len(b["firms"]),
        "timekeepers": b["tk"], "hours": round(b["hours"], 2),
        "fees": round(b["fees"], 2),
        "hours_share": round(b["hours"] / total_hours, 4) if total_hours else "",
        "fees_share": round(b["fees"] / total_fees, 4) if total_fees else "",
        "rate_min": b["rmin"] or "", "rate_max": b["rmax"] or "",
    } for role, b in sorted(by_role.items())]
    write(OUT_M02, M02_FIELDS, m02)

    # ---- M-03 rate progression ------------------------------------------
    # Within one docket and one filer, across successive non-superseded
    # applications, at role grain. Ordered by the application's period start --
    # never by docket number, which is the order of filing rather than of work.
    series: dict[tuple, list] = defaultdict(list)
    for r in role_rows:
        app = scope.get(r["docket_entry_id"])
        if not app or not app["period_start"]:
            continue
        series[(app["court_id"], app["docket_number"],
                app["filer_normalised"], r["role"])].append(
            (app["period_start"], num(r["rate_max"])))
    m03 = []
    for (court, docket, filer, role), points in sorted(series.items()):
        pts = sorted((p for p in points if p[1]), key=lambda t: t[0])
        if len(pts) < 2:
            continue
        first, last = pts[0][1], pts[-1][1]
        m03.append({
            "court_id": court, "docket_number": docket,
            "filer_normalised": filer, "role": role,
            "applications": len(pts),
            "first_rate_max": first, "last_rate_max": last,
            "change_absolute": round(last - first, 2),
            "change_pct": round((last - first) / first, 4) if first else "",
        })
    write(OUT_M03, M03_FIELDS, m03)

    # ---- M-05 fee concentration -----------------------------------------
    per_app: dict[str, list] = defaultdict(list)
    for r in cat_rows:
        if r["docket_entry_id"] in scope:
            per_app[r["docket_entry_id"]].append(num(r["fees"]))
    m05 = []
    for eid, fees in sorted(per_app.items()):
        if len(fees) < 3:
            continue
        app = scope[eid]
        tot = sum(fees)
        top3 = sum(sorted(fees, reverse=True)[:3])
        m05.append({
            "court_id": app["court_id"], "docket_number": app["docket_number"],
            "filer_normalised": app["filer_normalised"],
            "categories": len(fees), "fees_total": round(tot, 2),
            "top3_fees": round(top3, 2),
            "top3_share": round(top3 / tot, 4) if tot else "",
        })
    write(OUT_M05, M05_FIELDS, m05)

    manifest = json.loads(MEASURES_MANIFEST.read_text(encoding="utf-8")) \
        if MEASURES_MANIFEST.exists() else {"measures": {}}
    manifest["built_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest["measures"].update({
        "_scope": {"rule": "law-firm, single-period interim applications",
                   "in_scope": len(scope), "excluded_by_type": excluded},
        "M-01": {"rows": len(m01), "columns": M01_FIELDS,
                 "applications_in_scope": len(scope),
                 "categories_unmapped": len(unmapped),
                 "min_applications_per_cell": MIN_APPLICATIONS},
        "M-02": {"rows": len(m02), "columns": M02_FIELDS,
                 "total_hours": round(total_hours, 2),
                 "total_fees": round(total_fees, 2)},
        "M-03": {"rows": len(m03), "columns": M03_FIELDS},
        "M-05": {"rows": len(m05), "columns": M05_FIELDS},
    })
    MEASURES_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n",
                                 encoding="utf-8")

    print(f"M-01 categories            : {len(m01)}  "
          f"(unmapped firm categories: {len(unmapped)})")
    print(f"M-02 roles                 : {len(m02)}")
    print(f"M-03 progression series    : {len(m03)}")
    print(f"M-05 applications          : {len(m05)}")
    if by_role:
        print("")
        print("Staffing mix:")
        for r in m02:
            print(f"  {r['role']:<18} {r['hours']:>10,.1f} h  "
                  f"{r['hours_share'] or 0:>6.1%}  "
                  f"rate {r['rate_min'] or '-'}-{r['rate_max'] or '-'}")
    if unmapped:
        print("")
        print("Firm categories with no mapping (surfaced, never coerced):")
        for k, v in sorted(unmapped.items(), key=lambda t: -t[1]["fees"])[:10]:
            print(f"  {k[:52]:<52} ${v['fees']:>12,.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
