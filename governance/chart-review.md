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

## 0 · Reading panel (Rule 7.4) — PROPOSED, NOT RUN

*Written 2026-09-10, the same session that built the five charts below. The
transport certification and "why no panel was run" sections above still
govern: this section proposes a roster for a later Estate-rooted session to
cast, and casts none itself.*

**The decision the panel would be reading for (Rule 0.1):** whether a reader
who has never seen this module's governance documents comes away believing
its cross-source claims — coverage, the crosswalk, firm resolution, the
staffing mix, the reconciliation — are what the charts say they are, at the
corpus's actual, partial size.

**Proposed roster**, named by role only, each *not cast*:

| Seat | Reason |
|---|---|
| Bankruptcy fee-application reviewer (domain) | The population, the vocabularies and the reconciliation are legal-operations concepts; a domain reader is the one who would notice a claim that overstates what a partial docket search can support. |
| Entity-resolution / data-matching engineer (domain) | Chart 3 and Chart 4's finding are both about a matching rule's honest limits; this seat is cast to read those two charts adversarially. |
| Legal-operations or fee-examiner practitioner (domain) | Reads the staffing-mix and reconciliation charts for whether "requested vs. allowed" and "per-role share" read as claims about the case or about the estate — the distinction the governance notes insist on. |
| Visualisation specialist (canvas-only, no tables, no numbers, no finding stated) | The dedicated seat Rule 7.4 requires — reads canvas alone, blind to every other seat's brief. |

`Nature: simulated (proposed)` — no seat has been spawned.

```
transport            not applicable -- no panel has run
injects              not applicable -- no panel has run
blind                not certified
basis                see "Why no panel was run", above: a Code session
                     rooted in C:\Projects is a contaminated transport by
                     the 2026-08-28 finding, and a panel run from here could
                     not certify its own blindness
```

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
D = -- · N = -- · R = --
findings: not yet run (no panel has been cast)
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

**No panel has run.** Five charts exist, are built from certified artifacts
with three independent self-checks, and are rendered clean across the full
K6 ladder with no horizontal overflow and a correct 3-segment provenance
strip at every width. That is a checklist passing, not a naive read — the
distinction this file exists to keep. The roster above is ready to be cast
from an Estate-rooted session; this one could not certify its own blindness
and did not try.
