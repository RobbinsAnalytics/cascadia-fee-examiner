# The person-name control

*Section 6 control. **Mandatory.** Owner: Aaron Robbins. Established 2026-09-09.*

---

## The control objective

> **No natural person's name is committed to this repository or published on any
> surface it produces.**

An eponymous firm name is not a person. "Kirkland & Ellis LLP" is a party to a
public filing; the associate whose hours appear beneath it is not.

## Why it is a control here and a precaution elsewhere

The estate's standing rule is that no real person is named or stored in any
repo. In every previous module that cost nothing, because the sources carried no
people. **This module's central source names a person on nearly every line it
has.** A fee application's time detail is, by construction, a list of what named
individuals did on named days, and the mandated summary exhibit is a table of
those individuals with their titles and their hourly rates.

So the rule stops being a thing to remember and becomes a thing to implement,
and its limits have to be stated rather than assumed.

## Four layers, weakest last

### Layer 0 — grain. *Structural. No exception possible.*

**No output of this module has a row per person.** The parser aggregates as it
reads: a fee application's timekeeper table is collapsed to
**(application × firm × conformed role)** — hours, fees, and the minimum, median
and maximum rate within that role — before anything is written. There is no
intermediate per-person table, no pseudonymous key, and no salted hash.

**A per-person surrogate key was designed and then removed, and the reasoning is
recorded because it is the more tempting option.** A salted hash of each
timekeeper's name would have been a pseudonymised individual record serving no
measure in the register: every measure is at firm-role grain already. It would
also have been weakly protective — a few hundred names appear in the same public
PDFs, so anyone holding the salt could invert it — and it would have broken
re-derivation, because a machine without the salt produces different keys and
the independent validator could no longer reach the same answer down a separate
path. **The control that costs nothing analytically is the one that holds.**

### Layer 1 — narratives are never persisted.

The narrative column of a time entry describes what a named person did, and
frequently names others: *"Confer with M. Whalen re investigation."* Redacting
names out of free prose is a heuristic and would be presented as a guarantee.
**So the narrative is never written to disk at all.** No measure needs it.

### Layer 2 — API responses are stripped at write time.

CourtListener's document search returns docket-level fields that name people:
`attorney`, `party`, `assignedTo` and `referredTo` (the judge). The response
cache under `data/live/cache/` exists so a resumed run does not re-ask questions
it already has answers to — and it is **written stripped**, retaining only
identifiers, docket and entry numbers, the entry description, availability, the
storage path and dates.

Stripping at write time rather than at read time is the load-bearing choice: a
cache that holds the fields and merely promises not to use them is one careless
`json.dump` away from being the leak.

**The entry description is retained and it is the one field that can name a
person**, in forms like *"Application for Compensation of [name], Fee
Examiner."* It is retained because the keep/drop classifier needs it. It is
**working state, not evidence**: `data/live/` is gitignored, descriptions are
never copied into a committed table, and no run record quotes one — a run record
that quotes a description in an error message is the leak path this sentence
exists to close.

### Layer 3 — schema conformance. *Checked, and its limits stated.*

`governance/schema_allowlist.json` declares the exact header of every committed
table. `src/validate.py` compares each one and **fails on an added column**, not
merely on a forbidden one, because the failure mode is a writer being changed
without the change being noticed. It also refuses any table whose header matches
a known person-bearing field name, and refuses the allow-list itself if any
column is ever declared class `person`.

The BRD's own person-bearing columns — judge at filing, at disposition and at
appointment, the CEO, the trustee, the examiner, the turnaround person — are
named in `src/build_spine.py` as `EXCLUDED_PERSON_COLUMNS` and are absent from
the spine's allow-list. The spine reads 217 fields and emits 47.

---

## Where this control lives, and why not in a git hook

**It is a publish gate in `src/validate.py`, not a third `pre-commit` gate, and
that was forced rather than preferred.**

The canonical `.githooks/pre-commit` runs exactly two gates and ends in `exec`.
It is marked *"Never edit"* in the starter kit, it is copied verbatim across the
estate, and its bytes are hashed by `check_hook_drift.py` — so chaining a third
gate into it here would produce drift in a file whose whole purpose is to be
identical everywhere.

**A `PreToolUse` hook was the obvious alternative and is the wrong shape.**
`SESSION-RULES` rule 3 and the starter kit both record what happened the last
time an index-inspecting check was written that way: a `PreToolUse` hook is
handed the index as it stood *before* the tool call, so staging and committing
inside a single call passes a gate that had already read the index. That is
exactly why the whitespace check was moved out of `PreToolUse` and into a git
hook. Rebuilding that shape here would produce a control that reports success
and enforces nothing, which is worse than no control.

So the enforcement sits where it can fail closed, and it is honest about being a
publish gate: **it stops a bad artifact from being published or relied on, and
it does not stop a bad artifact from being committed.** Layer 0 is what makes
that acceptable — the writers cannot produce the row in the first place.

**Recorded as a build-forward candidate for `cascadia-standards`:** the
canonical `pre-commit` has no extension point. A `.githooks/gates.d/` directory
iterated in name order, with the credential gate first, would let a module add a
repo-specific gate without touching a byte of the shared file. This is the third
instance of the estate's standing problem that the governance layer is not
maintainable by the machinery it governs.

---

## What this control does not do

Stated plainly, because a controls reader will ask.

1. **The retrieved PDFs on disk are full of names.** They are gitignored and
   never committed, but a copy of this repository's working directory is not the
   same thing as the repository. The corpus is evidence for a re-run, and its
   freeze is asserted by hash rather than by tracking the bytes, precisely so it
   never enters git history where it could not be removed.
2. **It does not de-identify the source.** These are public court filings and
   remain so. The control governs what this module reproduces, not what exists.
3. **A firm name can be a person's name.** The rule resolves that by class, not
   by string: a value in a column declared `organisation`, sourced from a
   filing's caption or signature block, is an organisation. A misclassified
   column would defeat this, which is why the class is declared per column and
   the header is checked rather than trusted.

## Assertions re-tested on every run

| # | Assertion | Evidence | On failure |
|---|---|---|---|
| PN-1 | No committed table declares a column of class `person` | The allow-list is read and checked | Gate exits non-zero |
| PN-2 | Every committed table's header exactly matches its declaration | Header comparison, added columns included | Gate exits non-zero |
| PN-3 | No committed header matches a known person-bearing field name | Set intersection with `_forbidden_source_columns` | Gate exits non-zero |
| PN-4 | No committed table under `data/` is undeclared | `git ls-files` against the allow-list | Gate exits non-zero |

PN-4 is deliberately redundant with PN-2: a table nobody declared would
otherwise pass by not being looked at.
