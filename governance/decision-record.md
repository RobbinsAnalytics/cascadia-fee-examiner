# Decision record — Cascadia Fee Examiner

*Owner: Aaron Robbins. Opened 2026-09-09.*

Decisions that govern this module, with what they change and why. A decision
that never becomes an instruction is not adopted, so each one names the file or
mechanism that carries it.

---

## D-FE-01 · One name, both sides

**Decided 2026-08-31 by Aaron; this repository is the first under the rule.**

The local directory and the GitHub repository are both `cascadia-fee-examiner`.
The prior convention was `cascadia-<module>-analytics` locally and
`cascadia-<module>` remotely.

**It applies from this module forward and existing repositories are not
retrofitted** — not the local directory, not the remote, not the manifest key.
Control Tower, Deal Desk, Finance and Matter Ledger keep the split, and that
unevenness is a decision rather than drift, on the same footing as the estate's
standing position that dead work is not retrofitted.

**Adopting it was free because nothing constructs the name.** Verified in
`cascadia-standards` on 2026-08-31 across the starter kit, `hook_manifest.json`,
every `settings.json` and every `CLAUDE.md`: no code builds a path by appending
the suffix, and both estate checkers join the repository root to a manifest
**key** that is simply the directory name. That fact is the one to re-check
before any *further* naming decision, not to assume from this one.

**Carried by:** `REMOTE-CONVENTION.md` v1.0.0 in `cascadia-standards`, this
repository's `CLAUDE.md`, and `README.md`.

**Owed elsewhere:** an entry for this repository in
`cascadia-standards/governance/hook_manifest.json`, written from a session
rooted in that repository. Until it lands the estate drift check names this
repository as undeclared. That is the honest signal and is not to be worked
around from here.

## D-FE-02 · Cost comes from the filings, not from the spine

**Forced by evidence, 2026-09-09.**

The build brief assumed the Bankruptcy Research Database might carry
professional-fee figures across its whole panel. It does not: `ProfFees10k` is
populated on 151 of 1,218 cases and on **zero** of the 216 Appendix B-era cases,
because the publisher only records a total where the debtor kept filing 10-Ks
through final fee applications. The 102-case LoPucki-Doherty fee study is a
different artifact covering 1998 to 2007, and its own archive of applications
returns HTTP 404.

**So the cost layer is parsed from court filings**, and the external validation
in stage 5 reconciles against the **court's fee order** — a document written by
a different author than the application it responds to — rather than against a
BRD total that does not exist for this population.

**Carried by:** `governance/source-register.md` F-05; stages 3a and 3b.

## D-FE-03 · No retrieval script against a claims agent

**Decided 2026-09-09 on the terms as written.**

Kroll and Epiq both publish case dockets and filed papers for free reading, and
both prohibit "any use of direct or indirect automated searches or data queries"
without prior written consent. Their coverage of fee applications is materially
better than the volunteer-contributed archive this module uses.

**The module accepts the worse source rather than the prohibited method.** The
consequence is measured and published as M-04 rather than absorbed silently: a
coverage rate is what the constraint costs, stated as a number.

**Carried by:** `src/pull_fee_applications.py`, which has no claims-agent code
path; `governance/source-register.md` S-05.

## D-FE-04 · Person-level data is designed out, not pseudonymised

**Decided 2026-09-09, reversing an earlier design in the build plan.**

The plan called for a salted hash of each timekeeper's name as a surrogate key.
That was removed before implementation. No measure in this module needs a
per-person key; the hash would have been a pseudonymised individual record
serving nothing, weakly protective given the names sit in the same public PDFs,
and it would have broken independent re-derivation on any machine without the
salt.

**The parser aggregates to application × firm × role as it reads.** There is no
per-person row anywhere in the pipeline.

**Carried by:** `governance/person-name-control.md`; the writers in `src/`.

## D-FE-05 · The person-name gate is a publish gate, and that was forced

**Decided 2026-09-09 after two alternatives were examined and rejected.**

The control could not be a third git `pre-commit` gate: the canonical hook runs
exactly two, ends in `exec`, is marked "never edit", and is hashed estate-wide,
so chaining onto it would create drift in the one file whose purpose is to be
byte-identical everywhere. It could not be a `PreToolUse` hook either: that is
the exact shape the estate already recorded failing open, because such a hook
reads the index as it stood *before* the tool call.

**So it runs in `src/validate.py`, which exits non-zero.** The honest statement
of what that buys: it stops a bad artifact being published or relied on, and it
does not stop one being committed. The design layer is what makes that
acceptable.

**Reported, not applied:** the canonical `pre-commit` has no extension point. A
`.githooks/gates.d/` directory iterated in name order, credential gate first,
would let a module add a repo-specific gate without touching the shared file.
That is an amendment to `cascadia-standards` and belongs to a session rooted
there.

## D-FE-06 · The telecom exclusion is an industry test, not a name match

**Decided 2026-09-09; a deliberate divergence from the sibling module.**

Matter Ledger excludes by matching party names because its source records
parties only as free text. This source carries a publisher-assigned SIC code on
every row, so the exclusion tests a **structured field maintained by someone
else**. There is no misspelling problem, no `d/b/a` problem, and no
first-listed-party limitation.

SIC major group 48, Communications, is excluded at the spine: 95 cases of 1,218,
of which 8 are in the Appendix B era. What the test cannot do — it inherits the
publisher's classification, and it is a debtor test rather than a party test —
is stated in the rule rather than discovered later.

**Carried by:** `data/reference/excluded_sic.csv`, `src/build_spine.py`,
assertions SM-1 to SM-3 in `src/validate.py`.

## D-FE-07 · Truncated enumeration is excluded from rates, not counted as complete

**Decided 2026-09-09.**

The archive's search is enumerated per case up to a page cap. A case whose
results exceed the cap has an incomplete entry count, so it is excluded from
entry-level coverage rates and reported separately.

**The direction of the bias is why this matters.** Truncation happens on the
largest cases, and the largest cases are the best covered — so counting a
truncated case as if it were fully enumerated would push the published coverage
rate *upward*, in exactly the place a reader would be least able to check it.

**Carried by:** the `truncated` flag in the roster;
`src/build_coverage.py`'s complete-enumeration denominator.

## D-FE-08 · The scheduled lane ships as a definition and is not registered

**Decided 2026-09-09 by Aaron.**

The module carries `automation/coverage-recheck.md` as a named, inspectable
artifact so a future estate maintenance pass can reuse the lane. **It is not
registered in either scheduled-task store.** Nothing here runs unattended.

The job it describes is deliberately additive: it writes a new dated coverage
file and commits nothing. A scheduled job that re-pulled into the existing fact
tables would be a refresh in place, which the governing principles forbid.
