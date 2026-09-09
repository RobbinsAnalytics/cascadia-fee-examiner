# Certified measure register

*Stage 3 artifact. Owner of every measure below: **Aaron Robbins**.*
*Spine as-of 2023-01-12 (the publisher's freeze). Cost layer retrieved from the
RECAP archive from 2026-09-09, per document.*

Every measure carries a written definition, a named owner, lineage to source
fields, and a stated limit. **A figure that appears in any rendered output and
is not defined here is not certified and must not be published.**

**Independent validation.** `src/validate_measures.py` re-derives every
published cell down a separately written path — it indexes by application first
and aggregates second, where the builder groups directly — and crossfoots each
application's two exhibits against each other. **Nothing is published unless
that script exits zero.** A measure that only agrees with itself has not been
validated.

---

## The population, and why it is smaller than it looks

| | |
|---|---|
| **Spine** | 1,218 large public-company bankruptcies, 1980–2022, less 95 excluded by industry, less everything outside the Appendix B era |
| **Cost-layer population** | **216 cases** — Chapter 11, filed on or after 2013-10-01, after the subject-matter exclusion |
| **Measurement scope** | Law-firm applications only, **single-period interim only** |

**Three exclusions, each for a stated reason rather than convenience.**

**Financial advisers, bankers and claims agents are excluded from every
rate measure.** Most bill a flat monthly fee plus a transaction fee, so they
have no hourly rate at all, and a blended rate computed over a population
containing them is not a rate of anything. They are classified, counted, and
kept out — `data/reference/professional_type.csv` is the vocabulary.

**Final applications are excluded**, because a final application re-presents
every interim period it covers. Summing a final with its own interims
double-counts the same hours.

**Amended applications are excluded**, because an amended application supersedes
the one it amends.

**Excluded is not the same claim as absent**, so the counts of each are
published in `data/conformed/measures_manifest.json` rather than left implicit.

## The two words that do the work

**"Requested", never "awarded."** Every figure below is what the professional
*asked for*. What the court *allowed* is a different number written by a
different author, and it is the answer key for the reconciliation rather than an
input to a measure.

**"Fees", never "fees and expenses."** Expenses are reimbursements at cost and
have no hours behind them, so including them would put a numerator over an
unrelated denominator.

---

## M-01 · Blended hourly rate by project category

> **Definition.** For a conformed project category, total fees requested divided
> by total hours billed, across all in-scope interim applications that report
> that category. Reported with the number of applications and the number of
> distinct filing firms behind each cell.

| | |
|---|---|
| **Owner** | Aaron Robbins |
| **Output** | `data/conformed/m01_blended_rate_by_category.csv` |
| **Lineage** | `fact_category_summary.csv` (fees, hours, category as filed) → `data/reference/firm_category_to_ustp.csv` → `dim_task_code.csv` (`USTP-APPB-2013`) |
| **Population** | In-scope applications whose category summary parsed |
| **Statistic** | A ratio of sums, not a mean of ratios. A mean of per-application rates would weight a small application equally with a large one. |

**Limits.**
- **The category is the firm's, conformed by a mapping this module wrote.** No
  firm observed so far files under the U.S. Trustee's own category names. The
  mapping is in `data/reference/firm_category_to_ustp.csv` with a `match_type`
  per row, and the weakest rows say so in their own note.
- **`Case Administration` is defined residually by the U.S. Trustee** —
  "coordination and compliance activities not specifically covered by another
  category" — so it absorbs whatever the vocabulary does not name. Four firm
  categories observed so far map to it for exactly that reason. Its size is
  partly an artifact of the vocabulary and must never be read as a finding about
  how much administration a case needed.
- **A cell below three applications publishes its counts and no rate**, marked
  `suppressed`. It is written rather than dropped: an empty rate says "not
  enough to say" and a missing row says "nothing here", and those are different
  claims.
- Unmapped firm categories are **surfaced in
  `data/conformed/unmapped_categories.csv`, never coerced** into the nearest
  match (PRINCIPLES rule 6).

## M-02 · Staffing mix

> **Definition.** For a conformed timekeeper role, the share of total in-scope
> hours and of total in-scope fees attributable to that role, with the observed
> minimum and maximum hourly rate.

| | |
|---|---|
| **Owner** | Aaron Robbins |
| **Output** | `data/conformed/m02_staffing_mix.csv` |
| **Lineage** | The applicant's own timekeeper summary exhibit → `data/reference/title_to_role.csv` → `fact_role_summary.csv` |
| **Population** | In-scope applications whose timekeeper exhibit parsed |

**Limits.**
- **Roles are conformed from firm-authored titles** and firms do not agree on
  what they mean. A non-equity partner is conformed with partners; "Director" is
  a partner-equivalent at some firms and a non-attorney grade at others. The
  weakest row in the mapping is the one that sends a bare "Attorney" to
  `associate`, and it says so in its own note.
- **This is a mix within the applications that parsed**, not within the
  population. Read it against M-04.
- Rate minimum and maximum are the extremes of the **role**, not of any person.
  No per-person figure exists anywhere in this module.

## M-03 · Rate progression within a matter

> **Definition.** For one docket, one filing firm and one role, the change in
> the maximum rate observed between the earliest and the latest in-scope
> interim application, ordered by the application's **period start date**.

| | |
|---|---|
| **Owner** | Aaron Robbins |
| **Output** | `data/conformed/m03_rate_progression.csv` |
| **Lineage** | `fact_role_summary.rate_max` joined to `fact_application.period_start` |
| **Population** | Series with at least two in-scope applications carrying a parsed period and a rate |

**Limits.**
- **Ordered by period start, never by docket number.** A docket number is the
  order of filing, and a later-filed application can cover an earlier period.
- **The maximum rate in a role is not one person's rate.** A rise can mean a
  rate increase, or a more senior person joining the matter. This measure cannot
  distinguish those, and saying which it is would require the per-person record
  this module refuses to keep. Stated here rather than discovered by a reader.
- Appendix B distinguishes a "step increase" for seniority from a true rate
  increase. This measure sees neither label; it sees only the number.

## M-04 · Public-record coverage

> **Definition.** The share of the cost-layer population reachable free. Reported
> three ways: cases with any retrievable application or order; documents
> retrieved against documents listed; and both by court and by filing year.

| | |
|---|---|
| **Owner** | Aaron Robbins |
| **Output** | `data/conformed/m04_coverage.csv`, `coverage_by_case.csv` |
| **Lineage** | `dim_case.csv` → the acquisition roster → `data/reference/entry_classifier.csv` → `data/raw/recap/manifest.csv` |
| **Population** | All 216 cases; searched cases for rates |

**This is the measure the others are read against**, and it is a control rather
than a caveat: it states what a constraint costs, as a number.

**Limits.**
- **A case whose enumeration was truncated is excluded from entry-level rates**
  and counted separately. Truncation happens on the largest cases and the
  largest cases are the best covered, so counting them would push the rate
  upward exactly where a reader could least check it.
- **"Not yet searched" and "not covered" are different**, and the coverage file
  distinguishes them on every row.
- Coverage measures **one archive**. The same documents are readable free at the
  claims agents' own sites, which prohibit automated retrieval. This measures
  what is reachable by a permitted method, and that is the honest scope of the
  claim.

## M-05 · Fee concentration

> **Definition.** For one in-scope application, the share of its total requested
> fees falling in its three largest project categories, as the applicant itself
> reported them.

| | |
|---|---|
| **Owner** | Aaron Robbins |
| **Output** | `data/conformed/m05_fee_concentration.csv` |
| **Lineage** | `fact_category_summary.csv` |
| **Population** | In-scope applications reporting at least three categories |

**Limits.**
- Computed on the firm's **own** categories, before conformance, so it is
  label-invariant — a firm that uses twelve categories and one that uses
  twenty-five are not made comparable by this measure and it does not claim to.
- A firm using few categories will show high concentration by construction. The
  category count is published beside the share for that reason.

---

## Measures deliberately not certified

**Total professional fees per case.** The archive holds a minority of the
applications in most cases, so a per-case total would be a sum over an unknown
fraction and would read as a complete figure. M-04 exists instead.

**Anything at per-person grain.** Rates by named timekeeper, seniority curves,
leverage by individual. The data supports all of them and the module refuses
them; see `governance/person-name-control.md`.

**Anything cut by debtor identity.** See `governance/subject-matter-filter.md`.

**Awarded amounts as a measure.** They are the reconciliation's answer key, and
using an answer key as an input is how a check stops being one.
