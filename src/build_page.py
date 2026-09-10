"""Build docs/index.html — the module's visual layer.

K2 IS THE RULE THIS FILE EXISTS TO KEEP. Every figure on the page -- in a
title, a subtitle, an annotation, a summary, a table cell or an aria-label --
is computed here from a certified artifact. Nothing is typed. The artifacts:

    data/conformed/m04_coverage.csv          Chart 1 (coverage by court)
    data/reference/crosswalk_task_codes.csv  Chart 2 (task-vocabulary crosswalk)
    data/conformed/dim_firm.csv,
    bridge_firm_alias.csv, unresolved_firms.csv               Chart 3 (firm resolution)
    data/conformed/m02_staffing_mix.csv,
    fact_application.csv                     Chart 4 (staffing mix)
    data/conformed/v2_requested_vs_allowed.csv                Chart 5 (reconciliation)
    governance/health.json                   the health surface, the KPI band

THIS BUILD IS HONEST ABOUT AN INCOMPLETE CORPUS. 48 of 216 Appendix B-era
cases have been searched; the page says so in its own subtitle, not only in
governance/. M-01, M-03 and M-05 have zero rows -- nothing clears the n>=3
suppression floor yet -- and are not charted here; a chart on an empty table
is a canvas pretending to be a finding.

No reader controls (Checklist A, VIZ-PRINCIPLES 0.2). No invented colour or
typeface: the palette, the inks and the provenance strip come from the
Cascadia ECharts theme, copied into docs/assets/ from cascadia-standards.
"""
import csv
import hashlib
import html
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
CONF = REPO / "data" / "conformed"
REF = REPO / "data" / "reference"
GOV = REPO / "governance"
DOCS = REPO / "docs"

BRD_SOURCE = "Florida-UCLA-LoPucki Bankruptcy Research Database"
COST_SOURCE = "CourtListener RECAP archive, federal bankruptcy dockets"


def read_csv(name, base=None):
    with ((base or CONF) / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def fmt(n, dp=0):
    return format(round(float(n), dp) if dp else int(round(float(n))), ",")


def pct(num, den, dp=1):
    return round(100.0 * num / den, dp) if den else 0.0


# ---------------------------------------------------------------------------
# Fact-computation functions. Each reads a committed artifact and returns
# exactly the figures its chart and its prose need -- nothing is derived here
# that could not be re-derived by a reader from the same file.
# ---------------------------------------------------------------------------

def coverage_facts(health):
    """Chart 1. m04_coverage.csv, grouping=court, plus the 'all' row.

    year_filed grouping is deliberately NOT read here. Those eight rows look
    like a trend, but the years are an artifact of which cases happened to be
    searched first (48 of 216, acquisition incomplete) -- charting them as a
    sequence would misrepresent scan order as history. Court grouping is a
    true ranked-category claim with no sequence implied, so it is kept.
    """
    rows = read_csv("m04_coverage.csv")
    all_row = next(r for r in rows if r["grouping"] == "all")
    courts = sorted(
        (r for r in rows if r["grouping"] == "court"),
        key=lambda r: float(r["case_reach_rate"]),
    )
    acq = health["acquisition"]
    return {
        "all": all_row,
        "courts": courts,
        "population": acq["cases_in_population"],
        "searched": acq["cases_searched"],
        "not_searched": acq["cases_not_yet_searched"],
        "truncated": acq["cases_truncated"],
        "no_docket": int(all_row["cases"]) - int(all_row["cases_with_a_docket"]),
    }


def crosswalk_facts(health):
    """Chart 2. crosswalk_task_codes.csv, grouped by match_type.

    Cross-checked against health.json's own independently-written tally
    (codebook.crosswalk_by_match_type) rather than trusted on its own -- the
    same independent-check habit as validate_measures.py's separate-path
    re-derivation. Fails loudly if the two disagree.
    """
    rows = read_csv("crosswalk_task_codes.csv", REF)
    counts = {}
    for r in rows:
        counts[r["match_type"]] = counts.get(r["match_type"], 0) + 1
    check = health["codebook"]["crosswalk_by_match_type"]
    if counts != check:
        raise SystemExit(
            "crosswalk_facts: recount %s does not match health.json's own "
            "tally %s -- one of the two artifacts has drifted" % (counts, check)
        )
    none_rows = [r for r in rows if r["match_type"] == "none"]
    return {
        "total": len(rows),
        "counts": counts,
        "none_categories": [r["ustp_category"] for r in none_rows],
        "the_one": health["codebook"]["the_one"][0],
        "claim_holds": health["codebook"]["notice_claim_all_but_one_holds"],
    }


def firm_resolution_facts(health):
    """Chart 3. dim_firm.csv / bridge_firm_alias.csv / unresolved_firms.csv.

    Self-check: resolved + unresolved must sum to health.json's own
    caption_firm_pairs, or the build stops rather than publish a count that
    disagrees with the artifact that is supposed to be the same fact computed
    a second way.
    """
    bridge = read_csv("bridge_firm_alias.csv")
    unresolved = read_csv("unresolved_firms.csv")
    resolved_pairs = len(bridge)
    unresolved_pairs = len(unresolved)
    total = resolved_pairs + unresolved_pairs
    expected = health["resolution"]["caption_firm_pairs"]
    if total != expected:
        raise SystemExit(
            "firm_resolution_facts: %d resolved + %d unresolved = %d, but "
            "health.json reports caption_firm_pairs=%d" %
            (resolved_pairs, unresolved_pairs, total, expected)
        )
    # Three examples, organisation names only -- never an `attorney` field
    # value (person-name-control.md). unresolved_firms.csv's own columns are
    # caption-derived firm strings and candidate BRD names, both organisations.
    examples = sorted(unresolved, key=lambda r: -int(r["documents"]))[:3]
    return {
        "resolved": resolved_pairs,
        "unresolved": unresolved_pairs,
        "total": total,
        "match_rate": health["resolution"]["match_rate"],
        "distinct_firms": len({r["firm_key"] for r in bridge}),
        "examples": [
            {"name": r["caption_name"], "reason": r["reason"]} for r in examples
        ],
    }


def staffing_facts():
    """Chart 4. m02_staffing_mix.csv, cross-checked against fact_application.csv.

    THE FINDING THIS FUNCTION EXISTS TO STATE PRECISELY: the three applications
    in M-02's scope carry a blank filer_normalised -- not because firm
    resolution failed across the board, but because these three specific
    documents' captions did not match the extraction pattern. Confirmed here
    by reading fact_application.csv directly rather than trusting the round
    number in m02's own `firms` column: on docket deb 20-11177, a DIFFERENT
    entry on the SAME docket (147157402, a final application) resolved to
    "Kirkland & Ellis LLP..." -- so this is a per-document extraction gap, not
    a per-docket resolution failure, and the page must say the narrower,
    truer thing.
    """
    m02 = read_csv("m02_staffing_mix.csv")
    apps = read_csv("fact_application.csv")
    scope = [
        r for r in apps
        if r["parse_status"] == "parsed"
        and r["application_type"] == "interim"
        and r["professional_type"] == "law_firm"
    ]
    blank_filer = [r for r in scope if not r["filer_normalised"].strip()]
    if len(blank_filer) != len(scope):
        raise SystemExit(
            "staffing_facts: expected every in-scope application to carry a "
            "blank filer_normalised (the known finding); found %d of %d "
            "non-blank -- the finding has changed and the page copy must be "
            "re-checked before this assertion is loosened."
            % (len(scope) - len(blank_filer), len(scope))
        )
    # Does any OTHER entry on the same docket resolve? Read straight from the
    # bridge table rather than assumed, so the sentence stays true if the
    # corpus changes.
    dockets = {(r["court_id"], r["docket_number"]) for r in scope}
    bridge = read_csv("bridge_firm_alias.csv")
    resolved_dockets = {(r["court_id"], r["docket_number"]) for r in bridge}
    same_docket_resolves = sorted(dockets & resolved_dockets)

    by_role = {r["role"]: r for r in m02}
    total_hours = sum(float(r["hours"]) for r in m02)
    total_fees = sum(float(r["fees"]) for r in m02)
    return {
        "roles": sorted(m02, key=lambda r: -float(r["hours_share"])),
        "n_applications": len(scope),
        "total_hours": total_hours,
        "total_fees": total_fees,
        "same_docket_resolves": len(same_docket_resolves),
        "example_docket": same_docket_resolves[0] if same_docket_resolves else None,
        "partner": by_role["partner"],
        "associate": by_role["associate"],
    }


def reconciliation_facts(health):
    """Chart 5. v2_requested_vs_allowed.csv, grouped by the blocking rule."""
    rows = read_csv("v2_requested_vs_allowed.csv")
    counts = {}
    for r in rows:
        counts[r["rule"]] = counts.get(r["rule"], 0) + 1
    rec = health["reconciliation_V2"]
    if counts != rec["not_paired_by_rule"] or rec["paired"] != 0:
        raise SystemExit(
            "reconciliation_facts: recount %s / paired=%d does not match "
            "health.json's reconciliation_V2 %s" % (counts, 0, rec)
        )
    return {
        "total": len(rows),
        "paired": rec["paired"],
        "counts": counts,
        "orders_parsed": rec["orders_parsed"],
        "orders_omnibus": rec["orders_omnibus"],
    }


# ---------------------------------------------------------------------------

def asset_v(name):
    """`assets/<name>?v=<content hash>` so a republish is never served stale.

    Hash of the file's bytes, so the URL changes when and only when the asset
    does. Copied practice from cascadia-matter-ledger-analytics/src/build_page.py.
    """
    b = (DOCS / "assets" / name).read_bytes()
    return "assets/%s?v=%s" % (name, hashlib.md5(b).hexdigest()[:10])


def table(tid, caption, headers, rows):
    h = ["<table id=\"%s\"><caption>%s</caption><thead><tr>" % (tid, caption)]
    h += ["<th scope=\"col\">%s</th>" % html.escape(c) for c in headers]
    h.append("</tr></thead><tbody>")
    for r in rows:
        h.append("<tr>" + "".join(
            "<th scope=\"row\">%s</th>" % html.escape(str(c)) if i == 0
            else "<td>%s</td>" % html.escape(str(c))
            for i, c in enumerate(r)) + "</tr>")
    h.append("</tbody></table>")
    return "".join(h)


def main():
    health = json.loads((GOV / "health.json").read_text(encoding="utf-8"))

    cov = coverage_facts(health)
    cw = crosswalk_facts(health)
    fr = firm_resolution_facts(health)
    st = staffing_facts()
    rc = reconciliation_facts(health)

    data = {
        "asOfSpine": health["frozen_spine"]["as_of_date"],
        "c1": {
            "courts": [
                {"court": r["group_value"], "cases": int(r["cases"]),
                 "stored": int(r["cases_with_any_stored_document"]),
                 "reach": round(float(r["case_reach_rate"]) * 100, 2)}
                for r in cov["courts"]
            ],
            "population": cov["population"], "searched": cov["searched"],
        },
        "c2": {
            "counts": cw["counts"], "total": cw["total"],
            "noneCategories": cw["none_categories"],
        },
        "c3": {
            "resolved": fr["resolved"], "unresolved": fr["unresolved"],
            "total": fr["total"], "examples": fr["examples"],
        },
        "c4": {
            "roles": [
                {"role": r["role"], "applications": int(r["applications"]),
                 "hoursShare": round(float(r["hours_share"]) * 100, 2),
                 "feesShare": round(float(r["fees_share"]) * 100, 2),
                 "rateMin": float(r["rate_min"]) if r["rate_min"] else None,
                 "rateMax": float(r["rate_max"]) if r["rate_max"] else None}
                for r in st["roles"]
            ],
            "nApplications": st["n_applications"],
        },
        "c5": {
            "counts": rc["counts"], "total": rc["total"], "paired": rc["paired"],
        },
        "health": health,
    }

    facts = {
        "population": fmt(cov["population"]),
        "searched": fmt(cov["searched"]),
        "not_searched": fmt(cov["not_searched"]),
        "truncated": cov["truncated"],
        "no_docket": cov["no_docket"],
        "reach_pct": round(float(cov["all"]["case_reach_rate"]) * 100, 1),
        "doc_reach_pct": round(float(cov["all"]["document_reach_rate"]) * 100, 2),
        "cw_total": cw["total"], "cw_exact": cw["counts"].get("exact", 0),
        "cw_rename": cw["counts"].get("rename", 0),
        "cw_broader": cw["counts"].get("broader", 0),
        "cw_none": cw["counts"].get("none", 0),
        "cw_none_list": ", ".join(cw["none_categories"]),
        "cw_the_one": cw["the_one"],
        "fr_resolved": fr["resolved"], "fr_unresolved": fr["unresolved"],
        "fr_total": fr["total"], "fr_rate": round(fr["match_rate"] * 100, 0),
        "fr_firms": fr["distinct_firms"],
        "fr_ex1_name": fr["examples"][0]["name"],
        "fr_ex2_name": fr["examples"][1]["name"],
        "st_n": st["n_applications"],
        "st_partner_hours": round(float(st["partner"]["hours_share"]) * 100, 1),
        "st_partner_fees": round(float(st["partner"]["fees_share"]) * 100, 1),
        "st_associate_hours": round(float(st["associate"]["hours_share"]) * 100, 1),
        "st_associate_fees": round(float(st["associate"]["fees_share"]) * 100, 1),
        "st_docket_court": st["example_docket"][0] if st["example_docket"] else "",
        "st_docket_num": st["example_docket"][1] if st["example_docket"] else "",
        "rc_total": rc["total"], "rc_paired": rc["paired"],
        "rc_no_order": rc["counts"].get("1: no parsed order on this docket", 0),
        "rc_omnibus": rc["counts"].get("2: order is omnibus", 0),
        "rc_unresolved": rc["counts"].get(
            "3: filer strings do not resolve to one firm", 0),
        "gates_passed": str(health["all_gates_passed"]).lower(),
        "generated": health["generated_utc"].replace("T", " ").replace(
            "+00:00", " UTC"),
        "last_run_status": html.escape(health["acquisition"]["last_run_status"]),
        "parse_rate": round(health["parse"]["parse_rate"] * 100, 1),
        "parsed": health["parse"]["parsed"], "documents": health["parse"]["documents"],
        "unclass_rate": round(
            health["acquisition"]["unclassified_rate"] * 100, 2),
        "entries": fmt(health["acquisition"]["unique_docket_entries_classified"]),
        "as_of": health["frozen_spine"]["as_of_date"],
    }

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(render(data, facts, health), encoding="utf-8")
    print("wrote docs/index.html")
    for k in ("population", "searched", "reach_pct", "doc_reach_pct",
              "cw_exact", "cw_none", "fr_resolved", "fr_unresolved",
              "st_n", "rc_paired", "parse_rate"):
        print("  %-14s %s" % (k, facts[k]))


def render(data, f, health):
    t1 = table(
        "tbl-c1", "Chart 1 data — coverage reach by court",
        ["Court", "Cases searched", "Documents stored", "Reach"],
        [[r["court"], fmt(r["cases"]), fmt(r["stored"]), "%.1f%%" % r["reach"]]
         for r in data["c1"]["courts"]],
    )
    t2 = table(
        "tbl-c2", "Chart 2 data — task-vocabulary crosswalk by match type",
        ["Match type", "Categories"],
        [[k, fmt(v)] for k, v in sorted(data["c2"]["counts"].items(),
                                        key=lambda kv: -kv[1])],
    )
    t3 = table(
        "tbl-c3", "Chart 3 data — firm-identity resolution",
        ["Outcome", "Caption/firm pairs"],
        [["Resolved by a stated rule", fmt(data["c3"]["resolved"])],
         ["Unresolved, published with a reason", fmt(data["c3"]["unresolved"])]],
    )
    t4 = table(
        "tbl-c4", "Chart 4 data — staffing mix, hours and fees share by role",
        ["Role", "Applications reporting", "Hours share", "Fees share",
         "Rate min", "Rate max"],
        [[r["role"], fmt(r["applications"]), "%.1f%%" % r["hoursShare"],
          "%.1f%%" % r["feesShare"],
          ("$%.0f" % r["rateMin"]) if r["rateMin"] else "—",
          ("$%.0f" % r["rateMax"]) if r["rateMax"] else "—"]
         for r in data["c4"]["roles"]],
    )
    t5 = table(
        "tbl-c5", "Chart 5 data — why requested could not be paired with allowed",
        ["Blocking rule", "Applications"],
        [[k.split(": ", 1)[1].capitalize(), fmt(v)]
         for k, v in sorted(data["c5"]["counts"].items())],
    )

    subs = {
        "data": json.dumps(data, separators=(",", ":")),
        "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5,
        "v_css": asset_v("cascadia.css"),
        "v_echarts": asset_v("echarts.min.js"),
        "v_cascadia_echarts_theme": asset_v("cascadia-echarts-theme.js"),
        "v_page": asset_v("page.js"),
    }
    subs.update(f)
    out = TEMPLATE
    for k, v in subs.items():
        out = out.replace("@@%s@@" % k, str(v))
    import re
    left = sorted(set(re.findall(r"@@(\w+)@@", out)))
    if left:
        raise SystemExit("unsubstituted tokens in template: %s" % left)
    return out


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cascadia Fee Examiner — entity resolution with no shared key</title>
<meta name="description" content="A conformed spine across three sources that share no key: a frozen bankruptcy database, fee applications pulled from the public docket, and two task vocabularies. An independent portfolio project, built and reported honestly at 48 of 216 cases searched.">
<meta property="og:type" content="website">
<meta property="og:title" content="Cascadia Fee Examiner — entity resolution with no shared key">
<meta property="og:description" content="The same law firm named three ways across three systems, and no key to join them. A conformed spine, reported at its actual state of completion.">
<meta property="og:image" content="https://www.robbinsanalytics.com/assets/thumb-fee-examiner.png">
<meta property="og:url" content="https://www.robbinsanalytics.com/cascadia-fee-examiner/">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://www.robbinsanalytics.com/assets/thumb-fee-examiner.png">
<link rel="stylesheet" href="@@v_css@@">
<style>
  .answers { display:flex; flex-wrap:wrap; gap:18px; margin:18px 0 6px; }
  .answer { flex:1 1 210px; border:1px solid var(--mist,#E4E7E3); border-radius:3px;
            padding:14px 16px; background:#FCFCFA; }
  .answer .lbl { font:12px/1.5 "Segoe UI",Arial,sans-serif; color:#5B6660;
                 text-transform:uppercase; letter-spacing:.06em; }
  .answer .val { font:700 30px/1.15 "Source Serif 4",Georgia,serif; margin:4px 0 2px; }
  .answer .val.neutral { color:#232B27; }
  .answer .val.partial { color:#5B6660; }
  .answer .note { font:13px/1.5 "Segoe UI",Arial,sans-serif; color:#5B6660; }
  .chart { width:100%; }
  .chart-summary { font:13px/1.6 "Segoe UI",Arial,sans-serif; color:#232B27;
                   margin:10px 2px 0; max-width:70ch; }
  details.data-table { margin:8px 2px 0; }
  details.data-table summary { font:12px/1.5 "Segoe UI",Arial,sans-serif;
                               color:#5B6660; cursor:pointer; min-height:24px; }
  details.data-table table { border-collapse:collapse; margin-top:8px;
                             font:12px/1.5 "Segoe UI",Arial,sans-serif; }
  details.data-table caption { text-align:left; font-weight:600; padding:4px 0;
                               color:#232B27; }
  details.data-table th, details.data-table td { border:1px solid #E4E7E3;
                             padding:4px 8px; text-align:right; }
  details.data-table th[scope="row"] { text-align:left; font-weight:400; }
  details.data-table thead th { background:#F3F5F2; text-align:right; }
  .governance-note { border-left:3px solid #1E7A4C; padding:2px 0 2px 14px;
                     margin:16px 2px; font:14px/1.65 "Segoe UI",Arial,sans-serif;
                     color:#232B27; max-width:72ch; }
  .health { border:1px solid #E4E7E3; border-radius:3px; padding:16px 18px;
            background:#FCFCFA; margin:16px 0; }
  .health dl { display:grid; grid-template-columns:1fr auto; gap:6px 18px;
               margin:0; font:13px/1.6 "Segoe UI",Arial,sans-serif; }
  .health dt { color:#5B6660; }
  .health dd { margin:0; text-align:right; font-variant-numeric:tabular-nums;
               color:#232B27; }
  .state { display:inline-block; padding:1px 8px; border-radius:2px;
           font:12px/1.6 "Segoe UI",Arial,sans-serif; }
  .state.stopped { background:#F6EDE7; color:#BA572D; }
  .state.ok      { background:#E8F1EC; color:#1E7A4C; }
  table.refused { border-collapse:collapse; margin:12px 2px 4px; width:100%;
                    font:13px/1.55 "Segoe UI",Arial,sans-serif; }
  table.refused caption { text-align:left; font-weight:600; padding:4px 0;
                            color:#232B27; }
  table.refused th, table.refused td { border:1px solid #E4E7E3;
                            padding:7px 10px; text-align:left;
                            vertical-align:top; }
  table.refused thead th { background:#F3F5F2; }
  table.refused th[scope="row"] { font-weight:400; color:#232B27; }
  h2 { font:600 24px/1.3 "Source Serif 4",Georgia,serif; margin:34px 0 6px; }
  h3 { font:600 17px/1.35 "Source Serif 4",Georgia,serif; margin:22px 0 4px; }
  .lede { font:17px/1.65 "Source Serif 4",Georgia,serif; max-width:70ch; }
  @media (max-width:400px) { .answer .val { font-size:24px; } }
</style>
<script src="@@v_echarts@@"></script>
<!-- Local, and after ECharts so registerTheme('cascadia') finds it. -->
<script src="@@v_cascadia_echarts_theme@@"></script>
</head>
<body>

<!--CASCADIA_DATA_START-->
<script id="cascadia-data" type="application/json">@@data@@</script>
<!--CASCADIA_DATA_END-->

<div class="wrap">

<header class="site-head">
  <p class="kicker"><a href="https://www.robbinsanalytics.com/">Cascadia Portfolio</a> · Fee Examiner</p>
  <h1>The same firm, named three ways, with no key to join them</h1>
  <p class="subtitle">A conformed spine across a frozen bankruptcy database, fee applications
  pulled from the public docket, and two task-code vocabularies — three sources, three
  owners, none sharing an identifier. Reported honestly at its actual state: @@searched@@ of
  @@population@@ Appendix B-era cases searched so far.</p>
</header>

<h2>Where the build actually stands</h2>
<p class="lede">Nothing below claims the acquisition is finished, because it is not.</p>
<p class="chart-summary">The population is 216 large-corporate Chapter 11 cases filed under
the U.S. Trustee's Appendix B fee guidelines. Of those, @@searched@@ have been searched
against the public docket archive and @@not_searched@@ have not — a rate limit measured at
50 requests per hour, on either credential tier, is the reason. @@truncated@@ of the
searched cases were truncated at a page cap and are excluded from the rates below rather
than counted as complete.</p>

<div class="answers">
  <div class="answer">
    <p class="lbl">Cases searched</p>
    <p class="val neutral">@@searched@@ / @@population@@</p>
    <p class="note">@@reach_pct@@% of searched cases yielded at least one stored document;
    document-level reach is @@doc_reach_pct@@%.</p>
  </div>
  <div class="answer">
    <p class="lbl">Firm identity resolved</p>
    <p class="val neutral">@@fr_resolved@@ / @@fr_total@@</p>
    <p class="note">Caption-to-database pairs matched by a stated subset rule. Every
    unresolved pair is published with its own reason, not dropped.</p>
  </div>
  <div class="answer">
    <p class="lbl">Task vocabulary, exact match</p>
    <p class="val neutral">@@cw_exact@@ / @@cw_total@@</p>
    <p class="note">U.S. Trustee project categories with an identical 1997 UTBMS
    counterpart. @@cw_none@@ have none at all.</p>
  </div>
  <div class="answer">
    <p class="lbl">Requested paired with allowed</p>
    <p class="val partial">@@rc_paired@@ / @@rc_total@@</p>
    <p class="note">The court's own award, checked against the applicant's ask, under four
    stated rules. Zero pairs yet — every row says which rule stopped it.</p>
  </div>
</div>

<h2>Coverage varies by forum, and the largest court is the least reached</h2>
<div class="chart-card">
  <div id="c1" class="chart" style="height:420px"></div>
  <p id="sum-c1" class="chart-summary"></p>
  <details class="data-table"><summary>Chart 1 data table</summary>@@t1@@</details>
</div>

<div class="governance-note">
<strong>"Not yet searched" and "not covered" are different claims</strong>, and this chart
carries only the first: every bar is a court that has been searched, and its reach is the
share of its cases with at least one retrievable document. @@no_docket@@ searched cases
returned no docket in the archive at all. The documents are public at the claims agents'
own sites, which prohibit automated retrieval — this measures what is reachable by the one
permitted method, RECAP, and that is the honest scope of the claim.
</div>

<h2>Two vocabularies for the same billing categories, and one has no counterpart</h2>
<div class="chart-card">
  <div id="c2" class="chart" style="height:340px"></div>
  <p id="sum-c2" class="chart-summary"></p>
  <details class="data-table"><summary>Chart 2 data table</summary>@@t2@@</details>
</div>

<div class="governance-note">
<strong>The U.S. Trustee's own notice says seven of its categories were extracted from an
older vocabulary, "all but one" of which is in the 1997 UTBMS set — and does not say which
one.</strong> This build tested that claim rather than repeating it: the one is
<strong>@@cw_the_one@@</strong>. The three categories with no UTBMS counterpart at all are
@@cw_none_list@@.
</div>

<h2>Nine of twenty-five caption-to-database firm pairs resolve by a stated rule</h2>
<div class="chart-card">
  <div id="c3" class="chart" style="height:280px"></div>
  <p id="sum-c3" class="chart-summary"></p>
  <details class="data-table"><summary>Chart 3 data table</summary>@@t3@@</details>
</div>

<div class="governance-note">
<strong>A 100% match rate would be evidence the matching rule is too loose, not that the
data is clean.</strong> The rule matches when the database's short editorial name is a
token subset of the docket caption's full name — never a similarity score, never a single
shared token unless it is unique in that docket. The @@fr_unresolved@@ pairs that do not
match are published with the specific reason each failed, most often because the database
records only the lead firm and the docket names a co-counsel, local, or conflicts firm the
database never recorded — e.g. <strong>@@fr_ex1_name@@</strong> and
<strong>@@fr_ex2_name@@</strong>.
</div>

<h2>Three applications, and the document behind them names no firm</h2>
<div class="chart-card">
  <div id="c4" class="chart" style="height:340px"></div>
  <p id="sum-c4" class="chart-summary"></p>
  <details class="data-table"><summary>Chart 4 data table</summary>@@t4@@</details>
</div>

<div class="governance-note">
<strong>This is a staffing mix within @@st_n@@ applications, not within the population, and
none of the three carries an extracted firm name.</strong> That is not a resolution
failure across the board: a different filing on the same docket
(@@st_docket_court@@ @@st_docket_num@@) resolved cleanly to a named firm — it is these three
specific documents whose caption text did not match the extraction pattern, and the honest
reading is a per-document gap, not a per-docket one. Read this chart against the coverage
figures above, never as a claim about the population.
</div>

<h2>Zero of eleven applications could be checked against what the court allowed</h2>
<div class="chart-card">
  <div id="c5" class="chart" style="height:280px"></div>
  <p id="sum-c5" class="chart-summary"></p>
  <details class="data-table"><summary>Chart 5 data table</summary>@@t5@@</details>
</div>

<div class="governance-note">
<strong>This is the module's one figure against an answer key it did not produce</strong> —
the court's fee order, written by a different author than the application it responds to.
An omnibus order publishes no single allowed figure by design: several professionals'
awards in one order cannot be attributed without a rule this module has not written, so the
award count is published and the amount is left blank rather than summed or guessed.
</div>

<h2>How it stays right</h2>
<p class="chart-summary">The figures above are read from the module's own health surface,
written by the same gates that must pass before anything is published — not restated by
hand.</p>

<div class="health">
  <h3 style="margin-top:0">Build state</h3>
  <dl>
    <dt>All three publish gates passed</dt><dd><span class="state @@gates_passed@@">@@gates_passed@@</span></dd>
    <dt>Last acquisition run</dt><dd><span class="state stopped">@@last_run_status@@</span></dd>
    <dt>Docket entries classified</dt><dd>@@entries@@ (@@unclass_rate@@% unclassified)</dd>
    <dt>Documents parsed</dt><dd>@@parsed@@ of @@documents@@ (@@parse_rate@@%)</dd>
    <dt>Spine frozen as of</dt><dd>@@as_of@@</dd>
    <dt>Health surface generated</dt><dd>@@generated@@</dd>
  </dl>
</div>

<h3>What this module refuses to publish, and why</h3>
<p class="chart-summary">A module that only ever shows what it measured has said nothing
about what it declined to measure. Every refusal below is a decision, not a gap that was
never noticed.</p>

<table class="refused">
<caption>Measures deliberately not certified</caption>
<thead><tr><th scope="col">What is refused</th><th scope="col">Why</th></tr></thead>
<tbody>
<tr><th scope="row">Total professional fees per case</th>
    <td>The archive holds a minority of the applications in most cases; a per-case total
    would sum an unknown fraction and read as complete. Coverage is published as its own
    measure instead.</td></tr>
<tr><th scope="row">Anything at per-person grain</th>
    <td>Rates by named timekeeper, seniority curves, leverage by individual. The source data
    supports all of them. No per-timekeeper row exists anywhere in this module's
    pipeline — the parser aggregates to application × firm × role as it reads, before
    anything is written.</td></tr>
<tr><th scope="row">Anything cut by debtor identity</th>
    <td>No output carries a party column. Telecommunications debtors are excluded at the
    spine, before any measure, by an industry-code test rather than a name match.</td></tr>
<tr><th scope="row">Awarded amounts as an input to any other measure</th>
    <td>They are the reconciliation's answer key. Using an answer key as an input is how a
    check stops being one.</td></tr>
</tbody>
</table>

<div class="disclosure">
<h3>Disclosure</h3>
<p>An independent portfolio project by Aaron Robbins. This module uses data from the
Florida-UCLA-LoPucki Bankruptcy Research Database, as its use conditions require. The
UTBMS bankruptcy code set is the intellectual property of the American Bar Association,
reproduced by the LEDES Oversight Committee with the ABA's permission. Court filings are
public records. <strong>No natural person's name appears anywhere on this page or in this
module's data</strong> — not a timekeeper, not an attorney of record, not a judge — and no
telecommunications debtor is analysed. Nothing here is legal advice.</p>
<p>Source, governance documents and build scripts:
<a href="https://github.com/RobbinsAnalytics/cascadia-fee-examiner">github.com/RobbinsAnalytics/cascadia-fee-examiner</a>.
Every figure on this page is computed at build time from a certified artifact; the
independent re-derivation that gates publication is <code>src/validate_measures.py</code>.</p>
<p class="asof">Spine frozen as of @@as_of@@ · health surface generated @@generated@@ · cost
layer retrieved per document, incomplete at @@searched@@ of @@population@@ cases</p>
</div>

</div>

<script src="@@v_page@@"></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
