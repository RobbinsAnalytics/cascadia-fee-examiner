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

## Verdict

**None. No charts, no panel, no checklist run.** This module's stages 1 to 3
produce data and governance artifacts; the visual layer is a later session's
work, and this file is where its record lands.
