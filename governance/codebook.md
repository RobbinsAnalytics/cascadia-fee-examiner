# The task codebook

*Stage 2 artifact. Owner: Aaron Robbins. Established 2026-09-09.*

The conformed vocabulary every fee measure is grouped by. **Code meanings are
loaded from the published files at build time and are never written as a
`CASE WHEN` inside a query.** A codebook that lives in a query is a codebook
nobody can review, version or crosswalk.

Built by `src/build_codebook.py` from two frozen sources (S-02 and S-03 in the
source register) into `data/conformed/dim_task_code.csv`.

---

## Two vocabularies, not two versions of one

**The brief expected an annually revised code set and effective-dating across
years. That is false for this domain.** `utbms.com` publishes exactly one
bankruptcy workbook, dated 1997, with no change log and no superseding revision.
Revised sets exist for litigation (DRI, 2007) and for activity, expense and
project codes — but not for bankruptcy.

What actually varies is **whose vocabulary is in force**:

| Vocabulary | Author | Size | In force |
|---|---|---|---|
| `UTBMS-BK-1997` | American Bar Association | 21 task codes in 4 phases | 1997 onward, by industry convention |
| `USTP-APPB-2013` | Executive Office for U.S. Trustees | 22 project categories | Cases filed on or after 2013-10-01 |

So effective-dating in this module is **across vocabularies, keyed on the case's
filing date**, not across annual revisions of one list. A fee application in a
case filed in 2019 is read against the U.S. Trustee's categories; the ABA set is
what the firm's own billing system is likely to speak.

**Neither is what a firm actually files.** Appendix B ¶C.8.b says its list
"should be used to the extent applicable" and is "not exclusive", and firms
routinely file their own category names. That third layer is a per-firm mapping
built in stage 3b, and it is where the real conformance work is.

## The crosswalk, and what it found

`data/reference/crosswalk_task_codes.csv` maps each of the 22 Appendix B
categories to its UTBMS counterpart. It is **authored, versioned and
priority-ordered**, per PRINCIPLES rule 6, and it records what the two documents
say rather than what they ought to say.

| Match type | Count | Meaning |
|---|---|---|
| `exact` | 9 | Same name, same stated scope |
| `rename` | 8 | Same category, different punctuation or word order |
| `broader` | 2 | The Appendix B category covers more than the UTBMS code |
| `none` | 3 | No UTBMS counterpart exists |

**The three with no counterpart are Budgeting (Case), Reporting and Valuation.**
Budgeting is the guidelines' own instrument — Exhibit C-1 *is* a budget by
project category — so a category for the work of preparing it could not have
existed in a 1997 billing vocabulary.

**Two UTBMS codes have no Appendix B counterpart**: `B410` General Bankruptcy
Advice/Opinions and `B420` Restructurings. Both describe work done before a case
exists, which is not what a fee application in that case compensates.

## The notice's own claim, checked rather than repeated

The Federal Register notice states that the U.S. Trustee Program

> extracted and separately categorized certain tasks that are included in the
> broader Appendix A guidelines' project categories, all but one of which is
> included in the long-established Uniform Task Based Management System
> ("UTBMS") bankruptcy code set

and then names the seven: Assumption and Rejection of Leases and Contracts;
Avoidance Action Analysis; Corporate Governance and Board Matters; Litigation;
Non-Working Travel; Real Estate; and Reporting.

**`src/build_codebook.py` tests that sentence against the crosswalk on every
run.** Six of the seven map to a B-code. Exactly one does not, and it is
**Reporting**. The claim holds, and the module can now name the exception the
notice declined to name.

This is the module's thesis at its smallest scale — reconcile a number against
someone else's published assertion — and it arrives at stage 2 rather than
waiting for stage 5.

## Two independent readings of the same list

The 22 categories appear twice in the notice: as the prose list in ¶C.8.b, and
as the row labels of the Exhibit D-1 model form. **The build reads both and
compares them**, in order, and records whether they agree.

They agree. That check is not decorative: the first version of the prose parser
used an end anchor naming a paragraph that does not exist in this notice, so it
ran past the list and returned two **expense** categories as project categories.
The count came out at 24 and looked entirely plausible. The table read is what a
comparison would have caught immediately, which is why it is now part of the
build rather than something a session did once by eye.

## Limits

1. **`Litigation` is mapped `broader` and the mapping is the honest half of a
   real mismatch.** Appendix B's category reaches adversary proceedings; the
   UTBMS bankruptcy set sends those to a separate litigation code set entirely.
   A firm coding to UTBMS puts that time somewhere this crosswalk cannot see.
2. **`Case Administration` is defined residually** by the U.S. Trustee —
   "coordination and compliance activities not specifically covered by another
   category" — so it absorbs whatever the other 21 do not. Any measure that
   compares category shares must say so, because its size is partly an artifact
   of the vocabulary rather than of the work.
3. **The UTBMS name `Financing/Cash Collections` reads where Appendix B reads
   `Cash Collateral`.** Recorded, not corrected. A mapping file that silently
   repairs its own source is a mapping file nobody can audit.
