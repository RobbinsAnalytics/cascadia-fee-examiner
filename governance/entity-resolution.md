# Entity resolution — the rules, written before any output

*Stage 4 artifact. Owner: Aaron Robbins. Established 2026-09-09.*

**These rules were written before a single resolved row was produced, and this
document was committed before `src/resolve_entities.py` was run.** That ordering
is the point of the stage. A resolution rule written after looking at its own
output is a rule fitted to the answer, and the match rate it reports is not
evidence of anything.

---

## What is actually hard here, and what is not

**Within one bankruptcy case the key is shared.** Everything hangs off the case
number, so joining a docket entry to its case is trivial. **This module does not
claim that join as a skill and neither should its page.** Getting that wrong
would be visible to anyone who has worked with court data.

The genuinely keyless problems are one level down, and they are keyless because
**each system's owner decided independently what to call the same thing**:

| # | Problem | Why no key exists |
|---|---|---|
| **R-1** | The same law firm across three systems | The database records a short editorial name; the docket records whatever the caption says; the caption itself varies between filings in one case |
| **R-3** | Debtor entities in a jointly administered case | One lead case number covers many affiliated filing entities, and which entity a document belongs to is written in prose |
| **R-4** | Database case ↔ archive docket ↔ SEC filer | Three identifier schemes, one of which is formatted differently by each court |

**R-2, counterparty identity across Schedule G, the claims register and cure
notices, is DEFERRED and not attempted.** The reason is evidentiary rather than
technical: the schedules are on the docket but were not retrievable at usable
volume in the archive this module is permitted to use, and the claims registers
live on claims-agent sites whose terms prohibit automated access. **A resolution
exercise on data this module cannot lawfully obtain would be a demonstration
with no subject.** Recorded here so it reads as a decision.

---

## R-1 · Firm identity across owners

### R-1a · The within-docket key, assigned at acquisition

The filing professional's name is read from the docket entry's own description,
between the application phrase and the role clause:

> "First Interim Fee Application **of Kirkland & Ellis LLP and Kirkland & Ellis
> International LLP**, Attorneys for the Debtors" → `Kirkland & Ellis LLP and
> Kirkland & Ellis International LLP`

**The last such phrase in the description is taken, not the first.** A caption
like "Notice Final Fee Application for Compensation for Services and
Reimbursement of Expenses of Jefferies LLC" contains three candidate
prepositions and only the last introduces the filer.

This yields a key that is stable **within one docket** and is used for the
measures. It is deliberately not matched to anything at acquisition time: a
resolution rule written inside an acquisition script is a rule nobody reviews.

### R-1b · The cross-source match

**Left side.** `dim_case.DipAtty` and `dim_case.CommCredAtty` — the database's
own short editorial forms, e.g. `Kirkland Ellis`, `Weil Gotshal`,
`Pachulski Stang`. They carry no punctuation, no entity suffix, and frequently
only two surnames of a four-surname firm.

**Right side.** `filer_normalised` from R-1a — the caption form, e.g.
`Kirkland & Ellis LLP and Kirkland & Ellis International LLP`.

**Normalisation, applied to both sides, in this order:**

1. Lowercase; strip accents.
2. Replace `&` with ` and `; strip all other punctuation to spaces.
3. Remove entity suffixes: `llp`, `llc`, `lp`, `pc`, `plc`, `pllc`, `ltd`,
   `inc`, `pa`, `chartered`, `international`.
4. Remove role words: `attorneys`, `attorney`, `counsel`, `for`, `the`,
   `debtors`, `debtor`, `committee`, `official`, `unsecured`, `creditors`.
5. Collapse whitespace; drop tokens shorter than three characters except where
   the whole name is shorter.

**The match rule.** A candidate pair matches when the database's token set is a
**subset** of the caption's token set. Subset, not equality and not a similarity
score, and the direction is deliberate: the database name is systematically
shorter, so `{kirkland, ellis} ⊆ {kirkland, ellis, and, kirkland, ellis}`
resolves while a fuzzy score would need a threshold nobody can justify.

**A single shared token is never a match.** `{jones} ⊆ {jones, day}` would
resolve `Jones` to `Jones Day`, so a subset match on one token is rejected
unless the database name is itself a single token AND that token is unique
across all candidate captions in the docket.

**Overrides.** `data/reference/firm_alias_overrides.csv` — hand-authored, one
row per pair, each with a reason. An override is used only where the rule above
fails, and the file is where a reader looks to see how much of the match rate is
rule and how much is hand.

### What failure looks like, named in advance

**A match rate near 100% would be evidence that the rule is too loose, not that
the data is clean.** The left side is an editorial abbreviation and the right
side is a caption; some of them genuinely do not correspond, because the
database records the *lead* firm and a fee application may be filed by
co-counsel, local counsel or conflicts counsel who never appear in the
database's field at all.

**So the unresolved rate is published with examples**, in
`data/conformed/unresolved_firms.csv`. A resolution process that reports no
failures is not a control.

**The examples committed there are caption-derived firm strings only.** The
archive's own `attorney` field names individual people and is never used as an
input to this rule — see `governance/person-name-control.md`.

---

## R-3 · Debtor entities under one lead case

**Not attempted in this build, and this is a scope decision rather than a
failure.** Fee applications are filed on the lead docket in a jointly
administered case, so every document this module retrieves already belongs to
the lead case, and resolving affiliate entities would change no measure.

Recorded because the problem is real and the data to attack it — the "et al."
caption, the affiliate list in every first footnote, the associated-docket
links — is in the corpus already. It is the obvious next build.

## R-4 · Database case ↔ archive docket ↔ SEC filer

**Partly solved and honestly so.** The database carries `CikBefore`, populated on
100% of the era population, so the database-to-SEC join **has a shared key** and
is not an entity-resolution problem at all. The correction matters: the build
brief listed this as one of four keyless problems and it is not one.

What is keyless is the **court forum**. The database writes `DE`, `TX SD`,
`NY SD`; the archive uses `deb`, `txsb`, `nysb`. The mapping is a stated rule —
lowercase state, district letter where one exists, then `b` — implemented in
`src/build_spine.py` and **exercised against the live archive** during
acquisition, so a forum this dataset has never shown us is reported rather than
silently mis-mapped.

---

## Assertions re-tested on every run

| # | Assertion | Evidence | On failure |
|---|---|---|---|
| ER-1 | The unresolved rate is published with examples | `unresolved_firms.csv` exists and is non-empty whenever the match rate is below 100% | Build fails |
| ER-2 | No override row lacks a reason | Column check on the overrides file | Build fails |
| ER-3 | No resolved row was produced by a single-token subset match | Re-checked in the resolver | Build fails |
| ER-4 | No input to R-1b came from a person-bearing field | The resolver reads only `DipAtty`, `CommCredAtty` and `filer_normalised` | Build fails |

ER-3 is deliberately redundant with the rule itself. A rule that is only ever
applied and never re-verified cannot tell you the day it stops working.
