# Cascadia Fee Examiner — what an agent needs to know

A governed conformed spine across **three sources that do not share a key**: the
Florida-UCLA-LoPucki Bankruptcy Research Database, the fee applications filed in
those cases, and the published UTBMS and U.S. Trustee task vocabularies. The
remote is `RobbinsAnalytics/cascadia-fee-examiner`.

**The estate's session rules — surfaces, guards, and the traps that have each
cost a session — are at
`C:\Projects\cascadia-standards\governance\SESSION-RULES.md`.** Read §1–§7 and
stop at the line. What gets published is governed by `PRINCIPLES.md` in the same
directory. This file carries only what is true of this repo.

## Two hard constraints, before anything else

**1 · No natural person's name is committed or published.** Fee applications
name timekeepers on nearly every line, so this is an implemented control and not
an intention. The rule and its mechanisms are in
`governance/person-name-control.md`. The one-line version: the parser aggregates
to **application × firm × role** as it reads and never writes a per-person row;
narratives are never persisted; API responses are stripped of `attorney`,
`party`, `assignedTo` and `referredTo` **at write time**; `dim_case` is built
from a column allow-list; and section C of `src/validate.py` refuses any
committed table whose header is not declared in
`governance/schema_allowlist.json` — a publish gate, not a third git hook. **An eponymous firm name is not a
person** — "Kirkland & Ellis LLP" is a party to the filing, not a timekeeper.

**2 · No telecommunications debtor is analysed.** SIC major group 48 is dropped
at the spine, before any measure. The rule, its owner and its measured drop
count are in `governance/subject-matter-filter.md`. Do not add a measure cut by
debtor identity.

## The naming convention changed at this repo

**This is the first repository under `REMOTE-CONVENTION.md` v1.0.0: one name,
both sides.** Local directory and GitHub repository are both
`cascadia-fee-examiner`. The older split — `cascadia-<m>-analytics` locally,
`cascadia-<m>` remotely — still stands in controltower, dealdesk, finance and
matter-ledger, and **those are not retrofitted.** That unevenness is a decision,
recorded in `governance/decision-record.md`, and is never to be read as drift.

## The freeze carries two dates, and they are different claims

`governance/freeze.toml`'s `as_of_date` is the **publisher's** date for the BRD
snapshot, 2023-01-12 — the database was frozen by its authors after the December
2022 update and the download link is stated to be permanent. Every row acquired
from CourtListener carries its **own** retrieval date, because that pull is a
genuinely later act against a live archive. Do not collapse the two.

`src/ingest_brd.py` re-pulls the source and overwrites the freeze. Only run it to
deliberately refresh. Everything else rebuilds from the committed snapshot,
offline.

**Both gates must pass before anything is committed under `data/conformed/`**:
`python src/validate.py` and `python src/validate_freeze.py`. Either exiting
non-zero means publish nothing, commit nothing.

## Four properties of the sources that will break a build

1. **The BRD csv is not UTF-8.** It is Latin-1. A UTF-8 read raises partway
   through. `src/build_spine.py` reads it with `encoding='latin-1'` and says so.
2. **BRD fee fields do not cover the modern panel.** `ProfFees10k` is populated
   on 151 of 1,218 cases and on **zero** cases filed in the Appendix B era, and
   `FeeReviewer` reads `pending` for every one of them. Cost comes from the
   filings, never from the BRD. The 102-case LoPucki-Doherty fee study is a
   different artifact covering 1998–2007, and its own applications archive 404s.
3. **RECAP holds a minority of fee applications and the shortfall is bimodal.**
   A mega-case may carry hundreds of available documents while a mid-size case
   beside it carries none. **Coverage is a published measure, not a caveat** — a
   coverage figure quoted as one estate-wide percentage hides the shape that
   matters.
4. **A "fee application" search hit is usually not a fee application.** The same
   query returns monthly fee statements, objections, certificates of no
   objection, fee examiner reports, orders, and financial-advisor applications
   whose flat monthly fee has no hourly rate in it. The keep/drop vocabulary is
   `data/reference/entry_classifier.csv` and its unclassified rate is published.
   Never filter these inline in a script.

## Never run `reclassify.py` while `pull_fee_applications.py` is running

The puller loads the corpus manifest into memory at start and rewrites the
whole file after every stored document. `reclassify.py` corrects the same
file in place. Run concurrently, the puller's stale in-memory copy overwrites
every correction within minutes, silently — this happened on 2026-09-09 and
put a refused filer string back into a working table three times. Stop the
puller, then reclassify. The acquisition is resumable, so stopping it costs
nothing.

## The docket's classification of a document is not the document's

A docket entry described as an interim application was, on its own first page,
a "FIRST AND FINAL FEE APPLICATION". The parser trusts the docket's class
except where the document's upper-case caption says it is also final, and
that override is deliberate: a final application re-presents every interim
period, so mistyping one as interim double-counts. Five of the first eight
parsed applications were finals.

## Claims-agent sites are open to a reader and closed to us

Kroll's and Epiq's terms of use both make filed papers "open to examination …
without charge" **and** prohibit "any use of direct or indirect automated
searches or data queries" without written consent. **Do not write a retrieval
script against any claims agent**, however public the documents are. RECAP is
the retrieval path, and that is a constraint on the build rather than a
preference. The quoted clauses are in `governance/source-register.md`.

## Committing

**Stage by name — never the two blanket forms.** They are denied in
`.claude/settings.json`, and that block does **not** bind under
`bypassPermissions`. What binds is
`.claude/hooks/no_blanket_add_or_force_push.py`, a `PreToolUse` hook.

**Line-ending churn on frozen data is not cosmetic** — it makes "the snapshot is
untouched" unassertable. `.gitattributes` prevents it and landed before the
first commit; the git `pre-commit` gate catches what gets through and fails
closed. **It is inert until `git config core.hooksPath .githooks` has been run
in this clone**, and on POSIX it is also inert unless `.githooks/pre-commit` is
tracked `100755`. Both were done at initialisation. Run
`python .claude/hooks/hook_test_matrix.py` to confirm the guards behave.

**This repo is declared in `cascadia-standards/governance/hook_manifest.json`**
(2026-09-14: `lifecycle: active`, all four guard files `required`). That entry
is authored and maintained from a session rooted in `cascadia-standards`,
never from here; `check_hook_drift.py` is the authority on the current state
of this repo's guards, not this file.

## Generated, not authored

`data/reference/dim_court.csv`, `data/conformed/*.csv`,
`data/conformed/measures_manifest.json`, `governance/health.json`,
`governance/last_run.json`, `governance/run_history.jsonl` and
`governance/reconciliation.md` are all build outputs. Regenerate them with the
scripts in `src/`. Hand-editing any of them is a recurring failure mode.

The **mapping files** under `data/reference/` are the opposite: they are
authored, versioned and priority-ordered, and an unrecognised value is
**appended to the mapping and surfaced in the report**, never coerced into the
nearest match (PRINCIPLES rule 6).
