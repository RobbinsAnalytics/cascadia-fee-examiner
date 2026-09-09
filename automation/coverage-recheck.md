---
name: cascadia-fee-examiner-coverage-recheck
description: Re-measure how much of this module's professional-fee record has become reachable in the RECAP archive since the last check, writing a new dated coverage file and committing nothing.
---

# Coverage re-check — a named artifact, not a registered job

**Status: DEFINED, NOT SCHEDULED.** Aaron's decision, 2026-09-09. This file
exists so the lane is inspectable and reusable; nothing here runs unattended,
and it is registered in **neither** scheduled-task store.

> **Two stores exist and neither tool indicates the other does.** Code reads
> `C:\Users\Ajayr\.claude\scheduled-tasks\`; Cowork reads
> `C:\Users\Ajayr\Claude\Scheduled\`. If this is ever registered, the store must
> be named in the same sentence. A definition that says "the scheduled tasks"
> has already cost this estate a session.

---

## What it would do, and the one thing it must never do

The RECAP archive grows when someone buys a document from PACER and contributes
it. So this module's coverage is not fixed: a case with no available fee
application today may have one next quarter, and **that change is itself the
finding** — it measures how a public record becomes publicly reachable over
time.

**It is an additive extension and never a refresh in place** (PRINCIPLES rule 2).

| Step | What it does |
|---|---|
| 1 | `python src/pull_fee_applications.py --max-requests <n>` against a **copy of the roster with the search flags cleared**, so cases are re-enumerated |
| 2 | `python src/reclassify.py` — offline, no network |
| 3 | `python src/build_coverage.py --as-of <date>` writing **`data/conformed/coverage_<date>.csv`**, a new file |
| 4 | Report the delta against the previous dated file in three lines |

**It must not** rewrite `coverage_by_case.csv`, `m04_coverage.csv`, or any
`fact_` table; re-run the freeze-protected spine build; or commit or push
anything. The earlier figures have to still exist, exactly as published, for a
then-versus-now comparison to be computable at all — which is the entire reason
rule 2 exists.

## Why it commits nothing

A scheduled run cannot be supervised, and this repository's publish gates are
the supervision. The sibling Matter Ledger module carries a repo-local
`PreToolUse` hook that fails a push closed during a scheduled run; **this module
does not carry one, because it has no scheduled run to guard.** If this job is
ever registered, that hook is copied in first and this paragraph is what says
so.

## Suggested cadence, if it is ever wanted

**Quarterly.** The archive's own bulk data regenerates quarterly, contribution
is driven by litigation activity rather than by a clock, and a monthly re-check
of a frozen 216-case population would mostly re-measure noise.

## Rate

**50 requests per hour on either tier**, quoted by the server itself, so 74-second
spacing, the server's `Retry-After` honoured on a 429, and a hard per-run
request ceiling — the measured basis is in `src/pull_fee_applications.py`'s
header. A scheduled run inherits those and must not be given a larger ceiling
than an attended one.
