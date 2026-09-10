# Chart review — Cascadia Fee Examiner

*Opened 2026-09-09, empty by design. Owner: Aaron Robbins.*
*Binding standard: `cascadia-standards/design-system/CHART-REVIEW.md` v2.8 and
`VIZ-PRINCIPLES.md` v2.8, read from that repository at `main` `6634020`. Not the
copies attached to any project.*

**No charts exist yet and no panel has been run.** This file is opened now so
that the record has a home before there is anything to put in it, and so that
the transport certification below is a field the first panel has to fill rather
than a clause someone remembers to add.

---

## Transport certification — a field every panel record must carry

Rule 7.4 states blindness conditions on **what the author puts in a seat's
prompt**. A measured finding of 2026-08-28 established that this does not reach
what the **runtime injects beneath the prompt**: a probe subagent received a
skill description in full, and an attached-project block naming the module's
own documents, before any prompt was read. In a Code session the same class of
leak arrives through the estate's `CLAUDE.md` files. Two surfaces, one hole.

**So blindness is a property of the transport as well as of the prompt, and a
panel record states which transport it ran on and what that transport injects.**

Every panel record filed here carries this block, completed:

```
transport            <where the seats ran>
injects              <what reached a seat beneath the prompt: skill
                      descriptions, project blocks, CLAUDE.md files, none>
blind                certified | not certified
basis                <the measurement, or the reason none exists>
```

**A panel that cannot certify its transport records `blind: not certified`.** It
does not assert blindness and it does not omit the field. That is the same
posture the standard already takes with `N = not measured`, and the same posture
as its rule that no findings is never a pass.

**Extent of the leak, as measured, because overstating it would be its own
defect:** filenames and one-line descriptions travel; rule *content* does not. A
seat learns it is reading a Cascadia artifact under a review rule. It does not
learn the rules to grade against.

**This clause is proposed for `VIZ-PRINCIPLES.md` Rule 7.4 and is not applied
from here.** Amending the standard from a session rooted in a module repository
is a cross-repo commit this module forbids. The text to file is in the build
report.

## Why no panel was run in the session that built this module

**A Code session sitting inside `C:\Projects` is a contaminated transport by the
finding above**, because the estate's `CLAUDE.md` files reach a subagent beneath
any prompt. A panel run here could not certify its own blindness, so it would
have to record `not certified` — and a panel that starts from that position is
worth less than one run from a surface that can do better.

Rooting a session outside `C:\Projects` is **not** sufficient on its own: the
Cowork probe ran from a home directory with no `C:\Projects` in existence and
still received the skill description. Bare calls carrying neither skills nor
project context are the only route measured clean so far.

## What a panel will be given when there is something to review

Recorded now so the materials condition is not decided by whoever happens to
render the charts.

- **Static renders only**, at the widths `CHART-REVIEW.md` names, **including
  the narrowest supported width** (the v2.5 materials condition).
- Widths are a property of the **chart element**, not the window — the renders
  wanted are the viewports either side of the host's actual breakpoint crossing
  (the v2.8 K6 repair).
- **The panel reads static renders and therefore says nothing about
  interaction** (the v2.8 scope clause). The checklist is not blind to
  interaction; the panel is. Those are different instruments and a clean panel
  is not evidence about hover, tooltip or touch behaviour.
- No brief, no build notes, no intended finding. Images only.

## 0 · Reading panel (Rule 7.4) — RUN 2026-09-10, Cowork side

*Actually run, on the 20 renders this repo produced. Run from the Cascadia
Estate Cowork project, per `ESTATE-STATE.md` §3, against the
`cascadia-reading-panel` skill, against `cascadia-fee-examiner` branch
`build/fee-examiner-frontend` commit `f0f3c95`, `docs/renders/`. Filed at
`cascadia-estate/panels/2026-09-10_Panel_fee-examiner-reading-panel.md`
(337 lines) and relayed into this repo by
`cascadia-estate/briefs/2026-09-10_Brief_fee-examiner-panel-fixes.md`, whose
Block A1 receipt (`wc -l` against the filed record, taken directly from
Cowork's own session) is this session's basis for copying the record below
as verbatim rather than reconstructing it secondhand. This session has no
access to `cascadia-estate` (gated, no credentials held here) and did not
independently re-open the filed record — it is reproduced from the relay
brief's Appendix, which states it exists for exactly this reason: so the
copy-in step does not depend on `cascadia-estate` being attached.
`cascadia-standards` `HEAD` at panel run time: `main` `6634020`, checked
twice by the panel session (before and after it ran), unchanged both times;
this session separately confirmed `6634020` is still `HEAD` as of this edit
(2026-09-10).*

**Source of the renders, as the panel recorded it.**
`feeexaminerpanelhandoff.zip`, containing the 20 PNGs named in the kickoff
(`c1`–`c5` × `320`/`625`/`626`/`1040`) plus a copy of the kickoff document.
Claimed origin — this branch, commit `f0f3c95`, `docs/renders/` — was
**not independently verified by the panel** (it had no repo access). This
session, which does have repo access, confirms commit `f0f3c95` is real: it
is the tip of `build/fee-examiner-frontend` as merged into this working
tree's history, and is the commit this session started from before applying
the fixes below.

**Two open items on the estate's own state, noted by the panel, not
resolved here either.** `ESTATE-STATE.md` §5 (as of 2026-09-09) lists the
Fee Examiner build project as "Not started" and the copy-2 repoint brief as
"not issued," per the panel's own record. Per this brief's own Block B2,
correcting or even fully investigating that discrepancy is explicitly not
this session's job — `cascadia-estate` files (`ESTATE-STATE.md`,
`cascadia-parking-lot.md`) are Cowork's, and a Code session finding one
wrong reports it rather than editing it. Reported here, not resolved: this
module's own repo state (spine merged to `main` at `700bd0d`, frontend built
on `build/fee-examiner-frontend` at `f0f3c95`, both real and gated,
confirmed again by this session) is consistent with active build work
already having happened, which is some evidence against "not started" —
but this session cannot see the Cowork project state `ESTATE-STATE.md`
describes and is not the authority on whether that line is stale.

**Pre-panel notes: not obtained by the panel. `N = not measured`.** Recorded
by the panel per the skill's own rule that a missing number is stated, not
reconstructed after the fact. Separately, §2 of this file already carries
*this session's own* pre-panel notes from before the panel ran — five
defects found and fixed in this build's own review, which is a different
number and not a substitute for the panel's own N.

### Transport certification — measured, not asserted (the panel's own)

**`blind: not certified` — contamination measured directly, on the Cowork
transport, before the seats were spawned.**

A throwaway probe subagent, given only an instruction to report any context
it could see that was not in its literal prompt, returned — before any task
content —

- the opening lines of **both** connected projects' `CLAUDE.md` files
  (`cascadia-estate` and `cascadia-standards`);
- the full skills list, including the `cascadia-reading-panel` skill's own
  one-line description verbatim: *"Runs a Rule 7.4 reading panel — a blind,
  multi-seat adversarial read of charts before they ship … the roster,
  disposition and D/N/R metric blocks that `CHART-REVIEW.md` expects."*
- the deferred-tools list and a `userEmail` context block.

This matches the class of leak recorded in `cascadia-parking-lot.md` §3a
(found 2026-08-28, Reading Panel API build) — and the panel's own record
flags it as a new instance worth relaying back there: that finding described
the skill-description leak and the `CLAUDE.md` leak as "two different
surfaces, one hole" (Cowork vs. Code transport). In the panel's own run both
surfaces leaked at once, because its Cowork session carried both repos as
connected folders simultaneously. Extent is consistent with the earlier
finding and not worse in kind: filenames and one-line descriptions travel;
rule *content* (`VIZ-PRINCIPLES.md` / `CHART-REVIEW.md` text) did not appear
in the probe's report, and none of the four seat prompts contained rule
text, rule numbers, the kickoff document, source data, or another seat's
output.

Each of the four seats was spawned as a separate subagent, in a single
message, seeing only its seat prompt and the chart images it names. None was
told this was a Rule 7.4 review, what the suspected findings were, or what
any other seat said. What none of them could have avoided receiving, by the
same transport channel the probe measured: knowledge that *some*
chart-review process was in flight and that the project concerns Cascadia
visualization work. No seat's returned text referenced the design system,
rule numbers, or the panel process by name.

This repo's own transport certification (above, in the "Why no panel was
run" section) remains correct and unchanged by this: **this repo is a
contaminated transport for the same class of reason**, and no panel has ever
run from inside it. The panel whose record follows ran from Cowork, not from
here.

### Roster

```
READING PANEL — Cascadia Fee Examiner — 2026-09-10
Decision served (Rule 0.1): Whether a reader who has never seen this
  module's governance documents comes away believing its cross-source
  claims — coverage, the task-vocabulary crosswalk, firm-identity
  resolution, the staffing mix, the requested-vs-allowed reconciliation —
  are what the charts say they are, at the corpus's actual, partial size
  (48 of 216 cases searched per the kickoff; not independently verified
  by this panel, which saw only the charts).
Charts panelled: 5   States: default only (no interactive states supplied)
Nature: simulated (all four seats)

  Seat 1  Bankruptcy fee-application reviewer   — simulated — why this
          seat: the population, the vocabularies and the reconciliation
          are legal-operations concepts; this seat is the one likely to
          notice a claim that overstates what a partial docket search
          can support.
  Seat 2  Entity-resolution / data-matching engineer — simulated — why
          this seat: firm resolution (Chart 3) and staffing mix (Chart 4)
          both turn on a matching or classification rule's honest limits;
          cast to read those two adversarially.
  Seat 3  Legal-operations / fee-examiner practitioner — simulated — why
          this seat: reads the staffing-mix and reconciliation charts for
          whether "requested vs. allowed" and "per-role share" read as
          claims about the case or about the estate.
  Seat 4  Visualization reader — simulated — canvas only; tables and
          arithmetic excluded; cast identically for every artifact per the
          skill's own note.

Blindness asserted: design system ✓ (no rule text/numbers in any prompt) ·
                    review and build notes ✓ (kickoff doc withheld) ·
                    source data ✓ (no tables, no generator, no database) ·
                    intended finding from outside the artifact ✓ (no
                    finding stated in any seat prompt) ·
                    other seats' output ✓ (single joint spawn, no seat
                    saw another's return)
Run: parallel ✓ (one message, four independent subagent spawns)
Author's pre-panel notes recorded: ☐ NOT RECORDED — N = not measured
Transport: NOT CERTIFIED BLIND — see certification section above. The
  checkboxes above describe the prompt level only; the transport-level gap
  applies regardless of what any individual checkbox says.
```

Render allocation: seats 1–3 were given the design-width render only
(`c<n>-1040.png`) for all five charts. Seat 4 was given all 20 images (all
four widths of all five charts). A deliberate allocation choice made by the
panel session, not a skill requirement.

### Seat returns (verbatim, copied from the filed record)

#### Seat 1 — Bankruptcy fee-application reviewer

**Chart 1**
- SENTENCE: "This is telling me they searched 48 cases across eight courts and got wildly different hit rates depending on which court — but half those courts only contributed one or two cases, so the 100% and 0% bars are just single coin-flips dressed up as rates."
- NUMBER: "21.1% — that's the label on the end of the deb bar, which is also the court with the largest n (19 cases), so it's actually the most trustworthy number on the page even though the title frames it almost apologetically ('the largest, Delaware, sits at 21%')." — located at: data label on the bar.
- QUESTION: "Can you re-sort or re-color this so the n=1 and n=2 courts aren't visually competing on equal footing with deb and txsb — I want to know how you want me to weight a 100% bar built on one case."
- GAP: "I looked for the total size of the underlying docket universe — 48 searched, but searched out of how many total cases in existence? The subtitle tells me not-yet-searched cases are excluded, but not how big that excluded pile is."

**Chart 2**
- SENTENCE: "Of 22 U.S. Trustee project categories, 9 line up exactly with the old 1997 UTBMS codes, 8 are just renamed, 2 got broadened, and 3 have nothing to map to — a straightforward one-time classification, not a trend."
- NUMBER: "9 — the label at the end of the 'Exact match' bar." — located at: bar end label.
- QUESTION: "Who made the call on 'renamed only' versus 'broader in Appendix B,' and is there a write-up of that judgment anywhere, since those two buckets look like they could shift into each other depending on how strictly you define 'renamed.'"
- GAP: "I didn't see whether any UTBMS code maps to more than one U.S. Trustee category, or vice versa — the chart treats this as a clean one-to-one classification and I have no way to tell if it is."

**Chart 3**
- SENTENCE: "Out of 25 firm-name pairs pulled from case captions, only 9 — about a third — matched the database automatically, and the other 16 didn't get dropped, they got published with some kind of flagged reason."
- NUMBER: "36% — stated right in the title, and it checks out against the bars (9 of 25)." — located at: title text, cross-checked against the two bar labels.
- QUESTION: "What are the 16 reasons, actually — are they a handful of repeated failure modes (multiple firms in one caption, abbreviation not in the lookup) or 16 different one-off judgment calls, because that changes whether I trust the 'resolved' 9 as a clean rule or a rule that just happened to work on the easy cases."
- GAP: "I looked for a breakdown of the unresolved reasons on the chart itself and didn't find it — the caption says it's in the data table, which is a real answer, but the chart alone doesn't tell me what's driving the 64%."

**Chart 4**
- SENTENCE: "This chart says partners bill half the hours but take almost two-thirds of the fees — except when I look at the n's, 'partner' is n=1, 'associate' is n=1, 'of counsel' is n=1, so this isn't a role pattern across a population, it's one filing's billing mix wearing a role-based-chart costume."
- NUMBER: "62.5% — the blue 'fees share' label on the Partner bar — but I would say it with an asterisk out loud, not repeat it as a finding." — located at: bar label.
- QUESTION: "Since only one of the three applications reports a partner rate and only one reports an associate rate, is this chart actually just describing a single fee application, and if so why is it framed as 'partners bill X, associates bill Y' instead of naming that one application?"
- GAP: "I looked for which of the three applications contributed which role rows — is it the same one application driving both the partner and associate bars, or three different ones each contributing a single role? The chart doesn't say, and that matters a lot for how I read it."

**Chart 5**
- SENTENCE: "Of the 11 fee applications that at least had a docket to check, zero — not some, zero — could actually be matched up against what the court awarded, mostly because there was no parsed order sitting on the docket at all."
- NUMBER: "0 of 11 paired — stated in the source line at the bottom, and echoed in the title." — located at: provenance line and title.
- QUESTION: "For the 8 'no parsed order on the docket' — is that because the order genuinely doesn't exist yet (case still pending), or because your parser is missing orders that are actually there? Those are very different problems and I'd want to know which one before I trust the '0 of 11' as a finding about the courts rather than about the tool."
- GAP: "I looked for how these 11 relate to the 48 cases in Chart 1 or the 25 pairs in Chart 3 — whether this is a subset of one of those or an independent pull — and there's nothing on the chart tying the populations together."

#### Seat 2 — Entity-resolution / data-matching engineer

**Chart 1**
- SENTENCE: "This is telling me our document coverage is wildly uneven by court — we've got two courts at 100% but they're n=1 and n=2, while Delaware, which is the court that actually matters for this population, is sitting at 21%."
- NUMBER: "21.1% — that's the label printed at the end of the 'deb' bar, which the subtitle tells me is Delaware, n=19." — located at: bar end label.
- QUESTION: "Delaware is your biggest bucket of searched cases and your worst retrieval rate — is that a RECAP archive gap (nobody's uploaded those documents) or is it a search/parsing problem on our end, because those are two very different fixes."
- GAP: "I looked for the denominator behind '48 cases searched' against however many cases exist total — the title and footer both flag that 'not-yet-searched' cases are excluded, but there's no bar or number telling me how many cases that is, so I can't tell if 48 is 10% or 90% of the docket."

**Chart 2**
- SENTENCE: "This is a one-time crosswalk showing that fewer than half the Trustee's 22 project categories line up cleanly with the old 1997 UTBMS codes, so if we're planning to key off UTBMS task codes we should expect real gaps."
- NUMBER: "9 — the label at the end of the top 'Exact match' bar." — located at: bar end label.
- QUESTION: "For the 3 with 'no UTBMS counterpart' and the 2 that are 'broader in Appendix B,' what are we doing downstream — dropping those line items, forcing them into a closest-match bucket, or carrying them as unclassified? That's the part that actually affects our numbers."
- GAP: "I looked for the actual category names — which 9 are exact, which 3 have nothing — and it's not on the chart itself, just counts by bucket. I'd need the data table to know if the 'no counterpart' ones are trivial or something we bill a lot of hours under."

**Chart 3**
- SENTENCE: "Only 9 of 25 firm-name pairs from the case captions resolved to a database match automatically, and the chart's making a point of telling me the other 16 didn't get silently dropped, they got published with a reason attached."
- NUMBER: "9 of 25, 36% — that's the title's own framing, matching the 'Resolved by a stated rule' bar labeled 9 against the total of 25 stated in the subtitle/title." — located at: bar label and title/subtitle.
- QUESTION: "Can I see the distribution of those 16 'stated reasons' — is it mostly one predictable failure mode (like punctuation or 'LLP' vs 'LLP.' token mismatches) or sixteen different one-off reasons? That tells me whether the token-subset rule is under-tuned or whether these are genuinely hard cases."
- GAP: "I looked for any confidence tiering on the 'resolved' 9 — a token-subset match can still be a false positive — and there's nothing here distinguishing a clean 1-to-1 resolution from a resolution that happened to survive the rule by coincidence."

**Chart 4**
- SENTENCE: "This looks like the standard 'partners bill less time but take more of the fee dollar' story, but the subtitle is doing a lot of work admitting it's only 3 applications, so I wouldn't call this a finding about the case yet."
- NUMBER: "62.5% — the blue 'Fees share' label on the Partner bar." — located at: bar label.
- QUESTION: "The title says this is 'across just 3 applications whose filer never resolved to a named firm' — is that a coincidence of which 3 applications happened to have parseable timekeeper exhibits, or is there something about unresolved-filer applications specifically that made them the only ones with clean role data? I want to know if this 3 is a representative sample or a leftover pile."
- GAP: "I looked for what 'n' means across the whole chart and initially read it as a headcount of timekeepers before the subtitle corrected me — it's applications reporting that role, not people or dollars — and I didn't find anywhere on the chart itself (versus the subtitle) that restates that, so it's an easy number to misquote."

**Chart 5**
- SENTENCE: "Blunt one — of 11 fee applications where we had a docket to check, zero paired successfully to an order, so we currently have no verified 'what the court actually allowed' figure for any of them."
- NUMBER: "8 — the label on the 'No parsed order on the docket' bar, which is the majority of the 11." — located at: bar label.
- QUESTION: "For that 8-case 'no parsed order on the docket' bucket, is that because no order exists yet (timing), or because an order exists but our parser missed it? Those have completely different implications for whether '0 of 11 paired' is a temporary state or a parsing-coverage problem."
- GAP: "The subtitle says 'a looser pairing rule would pair more and claim less' — I looked for what that looser rule would actually produce, some kind of secondary bar or footnote showing the tradeoff, and it isn't here; it's stated as a design rationale but not shown."

#### Seat 3 — Legal-operations / fee-examiner practitioner

**Chart 1**
- SENTENCE: "This is telling me how complete our fee-application data actually is court by court — and it's wildly uneven, from zero coverage in a couple courts up to full coverage in a couple others, with Delaware — the court that matters most to us — only sitting at 21%."
- NUMBER: "Delaware (deb) is at 21.1%, from the bar labeled 'deb (n=19)' — that's the fifth bar down, and it's also called out in the title as '21%.'" — located at: bar label.
- QUESTION: "Before I use any number that includes or excludes Delaware, I want to know — is 21% coverage on Delaware good enough to draw conclusions from, or are we one FOIA request away from that number moving a lot?"
- GAP: "I looked for what 'not-yet-searched' means in scope — is there a denominator beyond these 48 cases, i.e., how many total Delaware cases exist that we haven't searched yet? The footnote mentions it's excluded but doesn't tell me the total universe size."

**Chart 2**
- SENTENCE: "This is just a one-time reference chart mapping our category names to the standard billing codes, so I know 9 of our categories line up exactly with UTBMS and 3 have no equivalent at all."
- NUMBER: "9 categories are an 'Exact match' — that's the bottom bar, labeled '9.'" — located at: bar label.
- QUESTION: "For the 3 categories with 'No UTBMS counterpart,' what are those categories, and how do we currently classify time billed to them when we're benchmarking against UTBMS norms?"
- GAP: "I looked for the actual category names on each bar or in a table — the chart tells me counts per bucket but not which specific project categories fall into 'renamed only' versus 'no counterpart,' and I'd need that to do anything with this."

**Chart 3**
- SENTENCE: "This one's telling me that when we try to automatically match the firm name on a docket caption to our firm database, only about a third resolve cleanly on a stated rule, and the rest get published anyway rather than dropped, which makes me want to know what's underneath that 'published with a reason' bucket before I trust downstream firm-level rollups."
- NUMBER: "9 pairs resolved by a stated rule — that's the bottom bar, and the subtitle repeats it as '9 pairs resolved (36%).'" — located at: bar label and subtitle.
- QUESTION: "What are the 'stated reasons' behind the 16 unresolved-but-published pairs — is that a human review, a fuzzy-match guess, or just a shrug and pass-through — because that affects whether I can trust any firm-level cut of this data?"
- GAP: "I looked for a breakdown of what the 16 unresolved reasons actually were and didn't find it on the chart itself — it just says each one 'carries its own stated reason in the data table.'"

**Chart 4**
- SENTENCE: "This is the one I'd actually flag in a meeting — it's presenting a partner-vs-associate hours/fees split as if it's a staffing-mix finding, but the title's own subtitle admits it's drawn from just 3 applications, and worse, those are 3 applications where the filer never even resolved to a named firm."
- NUMBER: "Partners take 62.5% of fees despite 49.7% of hours — that's the top blue bar, labeled '62.5%' — but I would not repeat this number without repeating the n=3 caveat in the same breath." — located at: bar label.
- QUESTION: "Which 3 applications is this built on, and why weren't they excluded given they're the same ones with the unresolved-filer problem I just saw flagged elsewhere — is this actually a representative sample of our caseload or is it 3 outlier matters?"
- GAP: "I looked for a total dollar or hours figure — how much money and time this 62.5%/49.7% split is actually built on — and didn't find it; everything here is a percentage of an unstated, and apparently very small, base."

**Chart 5**
- SENTENCE: "This one's a diagnostic on our own matching pipeline, not a finding about fees — it's telling me the docket-to-order pairing logic failed on all 11 candidate applications, mostly because there was no parsed order on the docket at all."
- NUMBER: "Zero of 11 applications were successfully paired — that's stated directly in the source line ('paired: 0 of 11') and repeated in the caption below the chart." — located at: provenance line and caption.
- QUESTION: "Given 0 of 11 paired, is any fee-versus-court-approved-amount comparison downstream of this actually running on real pairs, or is it running on none — and if it's the latter, what are we currently telling anyone about approved-versus-billed amounts?"
- GAP: "I looked for what happens next — is there a fallback or manual reconciliation path for these 11, or do they just drop out of the analysis silently — and the chart doesn't say."

#### Seat 4 — Visualization reader (all four widths per chart)

**Chart 1**
1. What is it about? Before reading the title: a ranked horizontal bar chart comparing a percentage ("reach"?) across eight court codes, each annotated with a sample size n. Title: "Among 48 cases searched, reach runs from 0% to 100% depending on the court, and the largest, Delaware, sits at 21%." Matches the drawn shape — but the chart never prints the word "Delaware," only "deb." The title's naming of Delaware is a translation the reader has to take on faith.
2. Does the picture support the title? "48 cases searched" sums correctly from the eight n's but 48 is never printed. "0% to 100%" is directly visible (moeb/cacb at 0.0%, txnb/njb at 100.0%). "The largest, Delaware, sits at 21%" checks out arithmetically (deb has the largest n, 19, and its label reads 21.1%) but two things are taken on faith: that deb=Delaware, and that "largest" means largest sample size rather than largest reach (deb is near the bottom of the ranking).
3. Right chart type? Yes — ranked bar chart is correct for "value varies by category, from a floor to a ceiling."
4. Hard to read? At 320px the x-axis ticks stop at 0/30/60/90 — the two 100% bars run past the last gridline with no "100" tick, though the printed labels cover for it. At 625px, 626px and 1040px a "100" tick is present and this disappears — a width-specific issue confined to the narrowest render.
5. Survives without colour? Yes — single series, differentiated by row label and printed value, not hue.
6. The number: deb (n=19): 21.1% — sixth bar from the top, y-axis label "deb (n=19)," value label printed at the bar's end, axis scaled 0–100 (0–90 at the narrowest width).

**Chart 2**
1. What is it about? A four-bucket classification count of how categories map onto a reference code list. Title: "9 of the 22 U.S. Trustee project categories match a 1997 UTBMS task code exactly; 3 have none at all." Matches the chart (Exact match=9, No counterpart=3).
2. Does the picture support the title? "9...match exactly" and "3 have none" are both directly visible. "22" total is the sum of all four bars and is not printed as a total — the reader must add. It does appear as an extra axis tick at 625px, 626px and 1040px, but that tick is dropped at 320px, exactly where a phone reader would look for it.
3. Right chart type? Yes.
4. Hard to read? Only the missing "22" tick at 320px; otherwise fully legible at every width.
5. Survives without colour? Mostly — "No UTBMS counterpart" is a muted grey-green against the other three bars' solid green, which could compress in true grayscale, but every bar carries its own printed count and row label, so no information is actually lost.
6. The number: Exact match: 9 — top bar, value label "9," axis scaled 0–20/22.

**Chart 3**
1. What is it about? A two-bar resolved/unresolved count out of a total. Title: "9 of 25 caption-to-database firm pairs resolve by a stated rule (36%); every one of the rest is published, not dropped." The chart shows the count split; the title adds a percentage and a disposition claim the bars alone don't carry.
2. Does the picture support the title? "9 of 25" is directly visible and correct (9 + 16 = 25, and 25 is the axis's labeled maximum at every width). "(36%)" is not printed anywhere as a percentage — both bars show only raw counts; 9/25 does equal 36% but the reader must compute it. "Every one of the rest is published, not dropped" is a disposition claim with no visual encoding at all — it rests entirely on subtitle/caption prose, not on anything drawn.
3. Right chart type? For the count comparison, yes. But the title leads with a rate and a disposition assurance that the chart itself does not show — the form and the headline pull in different directions.
4. Hard to read? No problems at any width.
5. Survives without colour? Yes — grey vs. green may compress, but each bar has its own row label and printed count.
6. The number: Resolved by a stated rule: 9 — bottom bar, axis scaled 0–25. (The 36% cannot be read off the plot itself — a finding, not a failure to look hard enough: no percentage appears anywhere in the image.)

**Chart 4**
1. What is it about? A paired-bar comparison of hours-share vs. fees-share across four staffing roles. Title: "Partners bill 49.7% of hours but take 62.5% of fees, across just 3 applications whose filer never resolved to a named firm." The first clause matches the chart's top pair exactly; the second is a scope/data-quality caveat the chart cannot show.
2. Does the picture support the title? "49.7% hours / 62.5% fees" for Partner are both directly visible and exact. "Across just 3 applications" is stated only in the caption/source line, not plotted. The Paraprofessional row is separately labeled "(n=3)" for an unrelated reason — three of three applications reported that role — and a fast reader could mistake that "n=3" for the "3 applications" the title refers to; same digit, two different meanings, one in text and one in a bar label. "Whose filer never resolved to a named firm" is entirely unverifiable from the plot — nothing about firm identity appears in the chart at all.
3. Right chart type? For the hours-vs-fees comparison, yes. But the back half of the title is a sample-composition caveat no bar chart form is built to carry, and it rides along as prose.
4. Hard to read? No cutoff or overlap at any width; the five-line title is tight but legible at 320px.
5. Survives without colour? This is the weakest of the five charts on this test: within each role, "Hours share" (green) and "Fees share" (blue) are told apart only by colour and the shared legend, with no per-bar text label. In grayscale, green and blue can render as similar mid-greys. The consistent bar ordering (hours always first, fees always second) partly rescues it for a reader who remembers the legend, but it is not self-evident from a single row in isolation.
6. The number: Partner — Fees share: 62.5% — top pair, second (blue) bar, row label "Partner (n=1)," legend "Fees share," axis scaled 0%–80%.

**Chart 5**
1. What is it about? A breakdown of reasons a matching/linking process failed, across three named blocking reasons. Title: "None of the 11 applications with a matching docket could be checked against what the court allowed." The chart shows only the three failure-reason bars (1, 2, 8); the "zero could be checked" headline claim is not itself a plotted bar — it is stated in the source line and body text, and is only inferable from the plot by noticing the three reasons exhaust all 11.
2. Does the picture support the title? "11 applications" sums correctly (1+2+8=11) and 11 is the axis's labeled maximum at every width. "With a matching docket" is a scope description taken on faith. "Could not be checked against what the court allowed" — nothing in the chart shows or references a court-allowed amount at all; the chart shows only reasons for the absence of a comparison, consistent with zero successful checks, but the "court allowed" concept itself has zero visual presence.
3. Right chart type? Yes — a simple bar chart is appropriate for enumerating exhaustive, mutually exclusive failure reasons that sum to the stated total.
4. Hard to read? No problems at any width; category labels wrap to two lines at 320px but stay legible.
5. Survives without colour? Yes, cleanly — all three bars are the identical green; categories are told apart purely by row label.
6. The number: No parsed order on the docket: 8 — bottom bar, axis scaled 0–11.

### Panel's own disposition table (§3 of the filed record — recommendations only)

*Recommended dispositions only, as filed by the panel. **Final disposition
is the author's** (this session's, below), per Rule 7.4. Two corrections
are already applied in the Rule column below, per Block A5/A6 of the relay
brief — they are not the panel's own original text at those two cells:
finding #10 is `5.4` alone (the panel's own citation read `2.3 / 5.4`; `2.3`
is color discipline generally and does not specifically require this,
`5.4` does); finding #5 is `uncited` (the panel's own citation read `6.4`,
which governs interactive titles that recompute under a reader control —
these are static charts with no such control, so `6.4` does not apply and
no other rule cleanly covers a static label reusing one digit for two
referents).*

| # | Finding, in the reviewers' words | Seats | n | Chart | Defect? | Novel? | Panel's recommended disposition | Rule |
|---|---|---|---|---|---|---|---|---|
| 1 | *"the denominator behind '48 cases searched' against however many cases exist total... there's no bar or number telling me how many cases that is"* (Seat 2); *"the total size of the underlying docket universe"* (Seat 1); *"how many total Delaware cases exist that we haven't searched yet"* (Seat 3); *"'48' is not printed anywhere on the chart; you must add it yourself"* (Seat 4) | 1,2,3,4 | **4** | 1 | yes | — | recommend revise — state the searched-vs-total population (or the 48 itself) on the chart | 4.2 / 4.3 |
| 2 | *"What are the 16 reasons, actually"* (Seat 1); *"Can I see the distribution of those 16 'stated reasons'"* (Seat 2); *"What are the 'stated reasons' behind the 16"* (Seat 3); *"'Every one of the rest is published, not dropped'... has no visual encoding at all"* (Seat 4) | 1,2,3,4 | **4** | 3 | yes | — | recommend revise — confirm the data table carries the reason breakdown; consider surfacing reason categories on the chart | 3.2 / 5.1 |
| 3 | *"it's one filing's billing mix wearing a role-based-chart costume"* (Seat 1); *"drawn from just 3 applications, so I wouldn't call this a finding about the case yet"* (Seat 2); *"presenting a... hours/fees split as if it's a staffing-mix finding"* (Seat 3); *"a fast reader could easily mistake the paraprofessional row's 'n=3' for the '3 applications'"* (Seat 4) | 1,2,3,4 | **4** | 4 | yes | — | recommend revise — highest-priority finding in the set; 4.5 may apply for the first time in this estate | 4.5 |
| 4 | *"is that because the order genuinely doesn't exist yet... or because your parser is missing orders"* (Seat 1); *"timing... or... our parser missed it"* (Seat 2); *"is any fee-versus-court-approved-amount comparison... running on real pairs, or... none"* (Seat 3) | 1,2,3 | **3** | 5 | yes | — | recommend revise — candidate open item, no existing rule cleanly covers it | none — candidate |
| 5 | *"initially read [n] as a headcount of timekeepers... it's an easy number to misquote"* (Seat 2); *"the same digit, two different meanings"* (Seat 4) | 2,4 | 2 | 4 | yes | — | recommend revise — rename the colliding digit | uncited — see Block A6 |
| 6 | *"I'd need the data table to know if the 'no counterpart' ones are trivial"* (Seat 2); *"I looked for the actual category names on each bar or in a table"* (Seat 3) | 2,3 | 2 | 2 | yes | — | accepted with reason — a category-count chart reasonably defers names to the data table | 5.1 |
| 7 | *"the title's naming of Delaware is a translation the reader has to take on faith"* | 4 | 1 | 1 | yes | — | recommend revise — spell out the court name on the chart itself | 3.2 |
| 8 | *"the axis undersells its own range only at the phone width"* | 4 | 1 | 1 | yes | — | accepted with reason — minor; printed value labels already carry it | 5.5 |
| 9 | *"the '22' tick... is dropped at 320px"* | 4 | 1 | 2 | yes | — | recommend revise — restore the max-value tick at narrow width | 5.5 |
| 10 | *"told apart only by colour and the shared legend... the weakest [chart] of the five"* | 4 | 1 | 4 | yes | — | recommend revise — add a direct label or pattern distinction | 5.4 — see Block A5 |
| 11 | *"nothing on the chart tying the populations together"* | 1 | 1 | 1, 3, 5 (cross-chart) | yes | — | recommend revise — worth a shared reference if meant to be read together | none — candidate |
| 12 | *"no confidence tiering on the resolved 9"* | 2 | 1 | 3 | yes | — | accepted with reason — a methodological question, not a misreading | 5.1 |
| 13 | *"the '(36%)'... cannot be read off the plot itself"* | 4 | 1 | 3 | no | — | rejected — 3.2's computed-aggregate exception covers it | — |
| 14 | *"'court allowed'... has zero visual presence"* | 4 | 1 | 5 | no | — | rejected — the title's actual claim is fully supported by the three reason-bars | — |
| 15 | *"those two buckets look like they could shift into each other"* | 1 | 1 | 2 | no | — | rejected — a follow-up question about method, not a misreading | — |

### Panel's own summary (§4 of the filed record)

```
PANEL: 4 seats, simulated · 5 charts · findings 15 · defects 12 · novel not measured
       recommend-revise 9 · accepted 3 · rejected 3 · multi-seat defects 6
       D = 2.40 defects/chart · N = not measured · R = 0.20 rejected share
```

Multi-seat defects (raised independently by two or more seats): #1 (4), #2
(4), #3 (4), #4 (3), #5 (2), #6 (2) — six of the twelve defects were found
by more than one blind seat. What three of five charts converged on
independently, unprompted: Charts 1, 3 and 4 each drew all four seats to the
same class of gap — a number or a disposition claim the chart asserts but
does not itself show enough to verify, at exactly the point where the
underlying population is small, partial, or undisclosed.

---

## 0b · Author's disposition — final, per Rule 7.4

*The panel's dispositions above are recommendations from a session with no
write access to this repo and no view of the chart-generation source or the
underlying data tables. This session has both, and Rule 7.4 places final
disposition with the build author. Each finding below states accept,
override, or change, with what checking the real data actually showed where
that mattered. Findings are fixed in `docs/assets/page.js` and
`src/build_page.py` and re-rendered at the full K6 ladder
(320/625/626/1040) unless noted otherwise; see the build report for the
render paths.*

| # | Chart | Author's disposition |
|---|---|---|
| 1 | 1 | **Accept, fixed.** Title now states "Among 48 of 216 Appendix B-era cases searched," the population figure confirmed against `governance/health.json`'s `frozen_spine.appendix_b_era_cases` (216) rather than printed on the panel's unverified say-so. |
| 2 | 3 | **Accept, changed.** Checked `unresolved_firms.csv` directly: all 16 unresolved rows carry the *identical* templated reason string — there are not 16 diagnoses, there is one stated mechanism applied 16 times. The fix is not "surface the 16 reasons" (there is nothing to surface) but to correct the chart's own summary, which previously overclaimed per-pair distinctiveness ("each pair carries its own stated reason") — that was this build's own error, worse than what the panel flagged. Now states the true shape and flags that per-pair causes are not yet classified (build-forward candidate). |
| 3 | 4 | **Accept, changed — see the editorial write-up below.** Highest-priority finding, all 4 seats. Option (a)+(b) chosen: retitled around the confirmed fact (one application's own split, docket vaeb 15-33896) and moved the filing-count disclosure onto every row label directly. |
| 4 | 5 | **Accept, changed.** Checked directly, not left as an open question: `order_gap_facts()` re-classified the underlying RECAP search results with this build's own classifier and found order-shaped docket entries correctly identified on 4 of the 5 dockets behind the 8 unpaired applications (77 entries total) — not a parser miss. Every one of those 77 entries is marked unavailable in RECAP (no PDF uploaded) — the same coverage gap Chart 1 measures, now confirmed for orders. This is a more specific answer than the panel's own timing-vs-parser framing offered, and is now in Chart 5's own accessible summary, computed at build time. |
| 5 | 4 | **Accept, fixed.** The panel's own citation (6.4) is wrong per Block A6 — 6.4 governs interactive titles under a reader control, and these are static charts. Treated as uncited. Fixed anyway: every row label now reads "(X of N filings)" instead of a bare "(n=X)," so no digit is reused across two referents. |
| 6 | 2 | **Override — revise, not accepted.** The panel's own recommendation ("accepted with reason — a category-count chart reasonably defers names to the data table") assumed the data table already carried the category names. Checked the table this build actually shipped: it carried only bucket counts, the same numbers already on the chart — the finding was correct about the shipped artifact. Fixed: the table now lists all 22 U.S. Trustee categories by name and match type, sourced from `crosswalk_task_codes.csv`; the three "no counterpart" categories are also now named directly in the chart's own accessible summary (Budgeting (Case), Reporting, Valuation). |
| 7 | 1 | **Accept, fixed.** "deb" row now labeled "deb — Delaware." |
| 8 | 1 | **Accept, as the panel recommended — no fix needed.** Minor, and the printed value labels already carry the information. Fixed incidentally anyway: the shared axis config now forces the max-value tick to render at every width (`showMaxLabel: true`), which also resolves #9 below. |
| 9 | 2 | **Accept, fixed.** Same shared-template fix as #8: the "22" tick (and Chart 1's "100" tick) now renders at 320px. |
| 10 | 4 | **Accept, fixed, with the citation corrected per Block A5** (5.4 alone, not "2.3 / 5.4"). Each bar's printed label now states its own series name ("Hours 49.7%" / "Fees 62.5%") rather than a bare percentage relying on color plus the legend — the chart is now legible in grayscale without the legend, which is what 5.4 asks for. |
| 11 | 1, 3, 5 | **Accept, fixed.** `funnel_facts()` added to `build_page.py`, computed from `governance/health.json` and cross-checked at every stage; a new governance-note ties 216 (population) → 48 (searched) → 63 (documents stored) → 25 (caption/firm pairs) → 11 (parsed applications considered for reconciliation) into one stated chain, so a reader moving between Charts 1, 3 and 5 does not have to infer whether the population sizes relate. |
| 12 | 3 | **Override — revise, not accepted.** Checked `bridge_firm_alias.csv` directly: `match_rule` is `token_subset` for all 9 resolved pairs — uniformly, the same shape as finding #2, so there is no tiering *in the data* to surface (inventing a confidence score the data doesn't support would be its own defect). What the shipped table did NOT carry, and now does, is the actual `matched_tokens` per pair — a new "Chart 3 detail" table lists the database firm, the docket caption string, and the specific tokens matched for all 9 resolved pairs, so a reader can audit each match on its own evidence instead of trusting an aggregate count. |
| 13 | 3 | **Accept, rejected — no change.** 9 and 25 are both printed; the 36% is a trivial derived figure squarely inside Rule 3.2's computed-aggregate exception (Block A3). |
| 14 | 5 | **Accept, rejected — no change.** The title's actual claim ("could not be checked") is fully supported by the three reason-bars summing to 11; the chart's job is to explain the absence of a comparison, not depict the missing comparison itself. |
| 15 | 2 | **Accept, rejected — no change.** A legitimate methodological follow-up, not a misreading of the chart as drawn. |

### Finding #3 (Chart 4) — the editorial decision, stated explicitly

The brief named four options and was explicit that leaving the chart as-is
(option d) must not be the default by omission. **Chosen: a combination of
(a) and (b).** Rejected: (c) and a bare (d).

- **(a) — retitled.** The canvas title's first clause now states the real
  scope directly: *"One application's own staffing split, not a caseload
  pattern"* — before it states any number. The old title led with the
  percentages and buried the scope caveat in a trailing clause ("across
  just 3 applications..."), which is exactly the structure all four seats
  independently read past.
- **(b) — n-disclosure moved onto the plot itself.** Every row's own
  category label now reads "(1 of 3 filings)" or "(3 of 3 filings)"
  instead of a bare "(n=X)." This was chosen *because* finding #5 is direct,
  measured evidence that subtitle-only disclosure already failed once, on a
  seat instructed to read carefully — repeating that same failure mode
  while calling it fixed would not be a real fix.
- **(c) — considered, rejected.** Suppressing the n=1 roles and keeping
  only paraprofessional would delete the chart's one real finding (one
  filing's own internal hours/fees split across roles) rather than frame it
  honestly. The panel's objection in all four seats was about framing, not
  about whether n=1 rows belong on the chart at all — nothing in any seat's
  language asked for the other three roles to be removed.
- **(d) — not chosen.** The subtitle-only disclosure is what was already
  in place, and finding #5 shows it did not work even once. Leaving the
  chart as-is and citing the subtitle would repeat a demonstrated failure.

**What checking the real data added that no seat had:** `fact_role_summary.csv`,
filtered to the chart's own in-scope document set, shows partner, associate
and of–counsel rows all come from the identical single docket entry
(12366662, docket vaeb 15-33896); paraprofessional alone is pooled, from
that same document plus two others (docket entry 141574549 on deb 20-11177,
and 370663496 on deb 22-10426) that report paraprofessional time only. Seat
1's own GAP question ("is it the same one application driving both the
partner and associate bars, or three different ones each contributing a
single role?") is answered precisely, not just acknowledged: it is the
former, confirmed, and now stated in both the subtitle and the accessible
summary.


## 1 · Checklist A, per chart

Five charts, built `src/build_page.py` / `docs/assets/page.js`, rendered
`src/render_charts.py` at the K6 ladder derived from
`window.CASCADIA_BREAKPOINTS = [560]`: **320, 625, 626, 1040** (the design
width and the narrowest supported width are both in that set; 625/626
bracket the one declared breakpoint's host-element crossing, confirmed
identical for every chart).

| Check | C1 coverage | C2 crosswalk | C3 firm resolution | C4 staffing mix | C5 reconciliation |
|---|---|---|---|---|---|
| 2.3.5 encoded categories | 1 hue, 8 ranked bars | 4 (1 hue + 1 neutral) | 2 (1 hue + 1 neutral) | 2 series | 1 hue, 3 ranked bars |
| 5.1 layer-3 keyboard nav | not required (ranked comparison) | not required | not required | not required | not required |
| 3.4 mark annotation | not applicable — claim carried by title + direct labels, no single highlighted point | same | same | same | same |
| K1 axis bounds data-derived | yes (100 is a rate ceiling, not a fit) | yes (`max: total`) | yes (`max: total`) | yes (`max` from actual max share + headroom — **fixed during this build; see note**) | yes (`max: total`) |
| K2 every figure computed | yes — `build_page.py`'s `SystemExit` guard on any unsubstituted `@@token@@`, plus three independent self-checks (crosswalk recount, firm-resolution sum, blank-filer assertion) that fail closed if a source artifact disagrees with `health.json` | yes | yes | yes | yes |
| K3 no annotation overlaps a mark | not applicable, no annotation | — | — | — | — |
| K5 provenance strip, 3 segments | rendered, confirmed at all 4 widths | confirmed | confirmed | confirmed | confirmed |
| K6 rendered at the full ladder | yes, 320/625/626/1040 | yes | yes | yes | yes |
| K7 assets are what shipped | content-hash query strings (`asset_v`) on all four shared assets | — | — | — | — |
| K8 OG / Twitter meta | present, one set for the page | — | — | — | — |

**Note on K1 / Chart 4's axis bound.** The first build typed `max: 70` on
Chart 4's percentage axis — a number that happened to clear this build's
actual maximum share and was wrong for the reason K1 exists: it was a guess
that would have clipped silently the moment a role's share crossed it, not a
bound derived from the data. It was found and replaced with a computed bound
(`max(hours, fees) * 1.15`, rounded) during this same session, before commit
— by looking at the render, not by a mechanical check, which none of K1's own
wording would have caught on its own.

**D / N / R**

```
D = 2.40 defects/chart (panel's own count, Cowork side) · N = not measured ·
R = 0.20 rejected share
findings: 15 filed by the panel (§0 above); dispositioned by the author in
          §0b — 8 accepted/fixed, 2 overridden to revise (#6, #12), 1
          accepted-and-changed beyond the panel's own ask (#2), 3 rejected
          as filed, 1 changed via a build-time check the panel could not
          run (#4). D/N/R are the panel's own figures, carried forward
          unchanged — this session did not re-run the panel and has no
          basis to recompute them.
```

## 2 · Findings from this build session's own review, before any panel

Not a panel — the author's own look at the renders, recorded because it
is the input a later N (novelty share) calculation will need, per the
`pre-panel-notes.md` convention Matter Ledger established.

| # | What was wrong | How it was found | Fixed |
|---|---|---|---|
| 1 | Chart 1's category labels (`court\n(n=X)`) overlapped their neighbours at every width — the per-row height added for a two-line label only fired when `L.narrow` was true, and 8 categories at design width had no such allowance | Looking at `c1-1040.png` directly; no mechanical check (K5, K6, overflow) caught it | Row height is now measured from the actual wrapped line count (`categoryLines()`), not guessed from a `showN`/narrow flag |
| 2 | Chart 3's plain-text labels ("Unresolved, published with a reason") wrapped to two lines from column width alone, with no embedded `\n` and no `showN` — the same defect as #1, different trigger | Looking at `c3-1040.png` | Same fix as #1; the measurement function does not care why a label wraps |
| 3 | Chart 1's accessible summary sentence read "Reach varies from 0% (undefined, n=NaN) to 100% (undefined, n=NaN)" — a property-name mismatch: the outer `rows` variable held the raw `{court, cases, reach}` objects, and the summary referenced `.label`/`.n`, which only exist on the array `barChart()` builds internally | Reading the rendered summary text under the chart, not from any console error (there was none — this failed silently in prose, not in a way K2's `SystemExit` guard could see) | Referenced the correct raw-object fields (`.court`, `.cases`) |
| 4 | Chart 4's x-axis `max: 70` was a typed literal — the K1 rule this build otherwise enforces mechanically nowhere caught its own author doing the thing it forbids | Same look at the render; a typed bound that happens to fit the current data is indistinguishable from a derived one until the data changes | Computed from the actual max share plus headroom |
| 5 | Chart 4's separate `%` axis-name element and its bottom-anchored legend both wanted the same vertical band below the ticks, and collided at every width once #4's fix moved the axis scale | Same render pass | Removed the axis-name element; each tick states its own unit via `axisLabel.formatter` instead |

None of these five were caught by K5, K6, K7, K8, the overflow check, or the
`SystemExit` unsubstituted-token guard — every one required looking at the
rendered image or the rendered text. Recorded as the concrete argument for
why a panel (even a simulated one) reads renders rather than trusting a
green mechanical checklist, and why this file says so before any panel has
run.

## Verdict

**A panel has run, from Cowork, on this build's 20 renders — not from this
repo, which remains a contaminated transport and has never run one itself.**
Its record is copied above, verbatim, with the two Block A5/A6 citation
corrections applied. All 15 findings are dispositioned by this session in
§0b: 9 fixed in the chart source (`docs/assets/page.js`, plus supporting
facts and tables in `src/build_page.py`), including the highest-priority
finding (#3, all four seats), 2 overridden from the panel's own
"accepted with reason" to a real revision after checking the actual shipped
table against what each seat asked for, 3 rejected as filed (the panel's own
rejections, confirmed), and 1 (#4) resolved beyond what either the panel or
the original build could say, using a direct re-classification check this
session ran against the live RECAP cache.

All five charts were rebuilt (`src/build_page.py`) and re-rendered at the
full K6 ladder (320/625/626/1040, all five charts) via `src/render_charts.py`
after the fixes; the render script's own mechanical checks (zero horizontal
overflow, a 3-segment provenance strip at every width) pass, and every
changed chart was additionally inspected by eye at multiple widths — the
step this build's own §2 findings, and the panel's, both depended on, since
neither K5/K6/K7/K8 nor the `SystemExit` unsubstituted-token guard would
have caught any of the specific defects fixed here either. `validate.py` and
`validate_freeze.py` both pass against the updated `docs/` tree.

**Not merged, not published, not deployed.** This file, and the fixes it
records, sit on `build/fee-examiner-frontend`, unmerged, pending Aaron's own
look at the rendering and his explicit instruction to go live.
