# The subject-matter exclusion rule

*Section 6 control. **Mandatory.** Owner: Aaron Robbins. Established 2026-09-09.*

---

## The control objective

> **No telecommunications debtor is the subject of analysis in this module, and
> nothing it produces may read as an assessment of any identified party's
> professional-fee exposure — carrier or otherwise.**

This is a hard constraint on the artifact, not a stylistic preference. The
measures here are about how legal work is billed and staffed, not about who was
billed, so satisfying it costs no analytical content.

The rule is stated and enforced **at sector level**. An exclusion aimed at a
single company would be weaker as well as narrower: it would miss that company's
predecessors, its operating entities, and every competitor whose inclusion would
raise the same objection.

## Why an industry code and not a name list

The sibling Matter Ledger module excludes by matching party names, because its
source records parties as free text and nothing else. **This source is
different, and the difference makes the control stronger.**

The Bankruptcy Research Database classifies every debtor with a Standard
Industrial Classification code assigned by the publisher, and populates it on
100% of rows. So the exclusion can be a test on a **structured field maintained
by someone else** rather than a heuristic over spelling. There is no
`CONTI CABELISION ON N E` problem here: no misspelling, no `d/b/a` form, no
subsidiary sharing no token with its parent, and no first-listed-party
limitation.

**SIC major group 48, Communications**, is the excluded class. It covers
telephone communications, radiotelephone, telegraph, radio and television
broadcasting, cable, and communication services not elsewhere classified — which
is to say it is broader than "carrier", deliberately.

## Three layers, in order of strength

### Layer 0 — design. *Structural. No exception possible.*

**No measure in this module is cut by debtor identity, and nothing is published
at debtor grain.** Every figure is an aggregate over fee applications by
professional role, project category, court and year.

There is no output shape in which one company's professional-fee exposure could
be read, because no output has a company in it. This is the layer that satisfies
the objective, and it is what makes the layers below a belt rather than the
trousers.

### Layer 1 — the spine filter. *Structural. Auditable by code list.*

`src/build_spine.py` drops every row whose `SICMajGroup` begins with a code in
`data/reference/excluded_sic.csv` **before any downstream artifact sees it**.
The excluded rows never reach `dim_case.csv`, so they are never in the roster
that stage 3a acquires documents for, and no telecom debtor's fee application is
ever retrieved.

**Measured on the 2026-09-09 build: 1,218 cases read, 95 excluded, 1,123
retained.** Of the 224 Chapter 11 cases filed on or after 1 October 2013, **8
were excluded** and 216 remain.

**Every run publishes the drop count** into `governance/last_run.json`. A filter
whose catch count is never reported is a filter nobody has checked.

### Layer 2 — re-assertion against the output. *The one that catches a regression.*

`src/validate.py` re-reads the built `dim_case.csv` and asserts that no surviving
row carries an excluded code, reading the vocabulary from
`data/reference/excluded_sic.csv` rather than from the constant in the builder.
Two independent readings of the same rule.

This is deliberately redundant with layer 1. **A control that is only ever
applied and never re-verified cannot tell you the day it stops working.**

---

## What this cannot do

1. **It inherits the publisher's classification.** A debtor whose primary SIC
   code is not 48 but whose business is substantially communications is retained.
   The publisher assigns one primary code per debtor; a conglomerate gets the
   code of its principal activity. This is a property of the source and cannot
   be engineered around from inside it.
2. **It is a debtor test, not a party test.** A telecom company appearing in
   someone else's bankruptcy — as a creditor, a counterparty, a contract
   assignee — is invisible to it. **Layer 0 is what makes that acceptable:**
   no output carries a party at all, so there is nothing for such an appearance
   to be read out of.
3. **SIC codes are a 1987 vocabulary applied to a 2026 industry.** Firms whose
   business did not exist when the scheme was written land in
   `Communication Services, Not Elsewhere Classified` or in a non-48 group
   entirely. The exclusion is as good as the classification, and the
   classification is stated rather than claimed to be exhaustive.

## Assertions re-tested on every run

| # | Assertion | Evidence | On failure |
|---|---|---|---|
| SM-1 | No output carries a column at debtor-identity grain that a measure is cut by | Schema allow-list; no measure declares a debtor dimension | Gate exits non-zero |
| SM-2 | No row in `dim_case.csv` carries an excluded SIC major group | Re-read of the built artifact against the committed vocabulary | Gate exits non-zero |
| SM-3 | The exclusion count is published | Present in `governance/last_run.json` | Run marked incomplete |
