"""Render the page and every chart across the K6 width ladder.

CHART-REVIEW K6 is an INVARIANT: render at the narrowest supported width, the
design width, and the two viewports either side of every DECLARED
breakpoint's HOST-ELEMENT crossing -- not the window's. The ladder is
DERIVED from `window.CASCADIA_BREAKPOINTS`, declared once in
docs/assets/page.js, and this script fails closed if none are declared rather
than falling back to a typed pair.

320 px is Rule 5.3 / WCAG 1.4.10 reflow and what CASCADIA.minCanvasPx
hard-codes -- the floor the system claims to support, not a phone
approximation.

Also checked at every width:
  * horizontal overflow -- Rule 5.3's 1.4.10 clause, asserted rather than assumed
  * the rendered provenance strip's segment count (K5) -- this page has no
    interactive "view" state, so every chart must show exactly 3 segments at
    every width; a 4th would mean a stray separator inside a segment's own text
  * the real ECharts grid rect, printed alongside page.js's own estimate, so a
    silent geometry error stays visible rather than only ever wrong at runtime

Output: docs/renders/<chart>-<width>.png plus page-<width>.png
Exit non-zero if any width overflows horizontally, or if any chart's rendered
provenance strip does not carry exactly 3 segments.
"""
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "renders"
URL = "http://localhost:8732/"
DESIGN_WIDTH = 1040
NARROW_WIDTH = 320
SEARCH_MAX = 1600
CHARTS = ["c1", "c2", "c3", "c4", "c5"]


def k6_ladder(browser):
    """The K6 ladder, derived from what the page declares -- and translated
    from viewport width to the width at which each chart's HOST ELEMENT
    actually crosses each declared breakpoint. See module docstring.
    """
    page = browser.new_page(viewport={"width": DESIGN_WIDTH, "height": 900})
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(500)
    bps = page.evaluate("() => window.CASCADIA_BREAKPOINTS || null")
    if not bps:
        page.close()
        sys.exit("page.js declares no window.CASCADIA_BREAKPOINTS, so the K6 "
                 "ladder cannot be derived. Fail closed rather than fall back "
                 "to a typed pair -- a typed pair is what let K6 go unrun.")

    def host_width(viewport, cid):
        page.set_viewport_size({"width": viewport, "height": 900})
        page.wait_for_timeout(60)
        return page.evaluate("(id) => document.getElementById(id).clientWidth",
                             cid)

    widths = {NARROW_WIDTH, DESIGN_WIDTH}
    crossings = []
    for cid in CHARTS:
        for b in bps:
            lo, hi = NARROW_WIDTH, SEARCH_MAX
            if host_width(hi, cid) < b:
                continue
            if host_width(lo, cid) >= b:
                continue
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if host_width(mid, cid) >= b:
                    hi = mid
                else:
                    lo = mid
            crossings.append((cid, b, hi))
            widths.add(lo)
            widths.add(hi)
    page.close()
    return sorted(widths), list(bps), crossings


def main():
    argv = sys.argv[1:]
    out_dir = OUT
    if "--out" in argv:
        i = argv.index("--out")
        out_dir = pathlib.Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    widths = [int(a) for a in argv if a.isdigit()]
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright is required: pip install playwright && playwright install chromium")
    out_dir.mkdir(parents=True, exist_ok=True)

    overflow_failures = []
    segment_failures = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        if widths:
            print("explicit widths: %s" % ", ".join(str(w) for w in widths))
        else:
            widths, bps, crossings = k6_ladder(browser)
            print("K6 ladder derived from declared breakpoints %s"
                  % ", ".join(str(b) for b in bps))
            for cid, b, v in crossings:
                print("  %s crosses host %d px between viewport %d and %d"
                      % (cid, b, v - 1, v))
            print("  widths: %s" % ", ".join(str(w) for w in widths))
        for width in widths:
            page = browser.new_page(viewport={"width": width, "height": 1600},
                                    device_scale_factor=2)
            errors = []
            page.on("console", lambda m: errors.append(m.text)
                    if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(URL, wait_until="networkidle")
            page.wait_for_timeout(1200)

            if errors:
                print("  CONSOLE ERRORS at %dpx:" % width)
                for e in errors[:8]:
                    print("    " + e)

            page.screenshot(path=str(out_dir / ("page-%d.png" % width)),
                            full_page=True)
            for cid in CHARTS:
                card = page.locator("#%s" % cid).locator(
                    "xpath=ancestor::div[contains(@class,'chart-card')]")
                target = card if card.count() else page.locator("#%s" % cid)
                target.screenshot(path=str(out_dir / ("%s-%d.png" % (cid, width))))
                print("  %s-%d.png" % (cid, width))

            seg = page.evaluate(
                """() => Array.from(document.querySelectorAll('.cascadia-provenance'))
                        .map(n => n.textContent.split(' \\u00b7 ').length)"""
            )
            for cid, n in zip(CHARTS, seg):
                if n != 3:
                    segment_failures.append((width, cid, n))

            grid = page.evaluate(
                """() => Object.fromEntries(['c1','c2','c3','c4','c5'].map(id => {
                     try {
                       const ch = echarts.getInstanceByDom(
                         document.getElementById(id));
                       const g = ch.getModel().getComponent('grid')
                                  .coordinateSystem.getRect();
                       return [id, Math.round(g.width)];
                     } catch (e) { return [id, 'n/a']; }
                   }))"""
            )
            over = page.evaluate(
                """() => ({scroll: document.documentElement.scrollWidth,
                          client: document.documentElement.clientWidth})"""
            )
            print("  width %d: strip segments %s" % (width, seg))
            print("  width %d: grid px %s" % (width, grid))
            if over["scroll"] > over["client"] + 1:
                overflow_failures.append((width, over["scroll"], over["client"]))
                print("  width %d: HORIZONTAL OVERFLOW  scrollWidth %d > "
                      "clientWidth %d"
                      % (width, over["scroll"], over["client"]))
            page.close()
        browser.close()

    print("\nrenders in %s" % out_dir)
    failed = False
    if overflow_failures:
        failed = True
        print("\nRULE 5.3 / WCAG 1.4.10 FAILED -- the page scrolls sideways:")
        for w, sw, cw in overflow_failures:
            print("  at %d px the document is %d px wide (over by %d)"
                  % (w, sw, sw - cw))
    if segment_failures:
        failed = True
        print("\nK5 FAILED -- a provenance strip did not render 3 segments:")
        for w, cid, n in segment_failures:
            print("  %s at %d px: %d segments" % (cid, w, n))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
