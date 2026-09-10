/**
 * Cascadia Fee Examiner — chart layer.
 *
 * Reads the build-time data block written by src/build_page.py. No figure is
 * computed here that is not already in that block (Rule K2); this file
 * decides geometry, not values.
 *
 * NONE OF THE FIVE CHARTS CALL cascadiaNavigator. Rule 5.1 layer-3 (keyboard
 * navigation) is required where a finding depends on shape, sequence or a
 * spatial relation the data table cannot express -- trend lines, slope
 * charts, small multiples. Every chart here is a ranked or paired category
 * comparison: coverage by court, crosswalk match type, resolved/unresolved,
 * role staffing mix, reconciliation blocking rule. None makes a shape or
 * sequence claim, so each carries an L3 shape clause in its own summary
 * sentence instead (VIZ-PRINCIPLES 5.1's closing clause) and none needs the
 * navigator. This is a real, checkable absence, not an oversight -- stated
 * once here rather than re-justified per chart.
 *
 * NONE CALLS cascadiaAnnotation either. The Matter Ledger reference module's
 * bar charts (its Charts 3, 4, 5, built from the same shared template this
 * file borrows) ship with no in-plot annotation -- the claim is carried by
 * the title and the direct bar labels, and 3.4's annotation-at-the-mark rule
 * applies to a chart whose claim is a single highlighted point, which none of
 * these five are. Only Matter Ledger's custom waterfall/line charts (not this
 * template) used it.
 */
(function () {
  'use strict';

  var D = JSON.parse(document.getElementById('cascadia-data').textContent);
  var C = CASCADIA.colors, INK = CASCADIA.textInk;
  var SANS = '"Segoe UI",-apple-system,"Helvetica Neue",Arial,sans-serif';

  function el(id) { return document.getElementById(id); }
  function nf(n) { return Number(n).toLocaleString('en-US'); }

  /**
   * How much vertical room the title block will actually take once wrapped.
   * Measured with a canvas text metric, not estimated from character counts
   * -- the serif title and the sans subtitle have different advance widths.
   */
  var _m = document.createElement('canvas').getContext('2d');
  function wrappedLines(text, px, font) {
    _m.font = font;
    var words = String(text).split(' '), lines = 1, cur = '';
    for (var i = 0; i < words.length; i++) {
      var test = cur ? cur + ' ' + words[i] : words[i];
      if (_m.measureText(test).width > px && cur) { lines++; cur = words[i]; }
      else { cur = test; }
    }
    return lines;
  }
  function titleTop(w, finding, subtitle) {
    var tl = wrappedLines(finding, w - 8,
      '600 20px "Source Serif 4", Georgia, serif');
    var sl = wrappedLines(subtitle, w - 8,
      '13px "Segoe UI", Arial, sans-serif');
    return Math.round(10 + tl * 26 + 8 + sl * 18 + 16);
  }

  /**
   * EVERY WIDTH AT WHICH THIS PAGE CHANGES ITS MIND, DECLARED IN ONE PLACE.
   *
   * CHART-REVIEW K6 is an INVARIANT: render at the narrowest width, the design
   * width, and the two viewports either side of every DECLARED breakpoint's
   * host-element crossing. A breakpoint that is used must be declared here,
   * or the render script has nothing to derive its ladder from and fails
   * closed rather than falling back to a typed pair.
   *
   * Only ONE breakpoint is declared: this page has no analog to Matter
   * Ledger's Chart 1 annotation-leaves-the-plot behaviour (no chart here
   * calls cascadiaAnnotation at all), so there is no "prose" threshold to
   * name. BP.narrow governs label-column width and axis tick density only.
   */
  var BP = { narrow: 560 };
  window.CASCADIA_BREAKPOINTS = [BP.narrow];

  /** Geometry that depends on how much room there actually is. */
  function layout(host) {
    var w = host.clientWidth || CASCADIA.minCanvasPx;
    var narrow = w < BP.narrow;
    return {
      w: w,
      narrow: narrow,
      labelWidth: Math.max(90, Math.min(190, Math.round(w * 0.28))),
      gridRight: narrow ? 44 : 84,
      tooltip: true,
      tapTip: !(window.matchMedia &&
                window.matchMedia('(hover: hover) and (pointer: fine)').matches)
    };
  }

  /**
   * Tooltip config, or `{show:false}` if the caller opts out.
   * Same capability-based touch handling as the Matter Ledger reference:
   * ask the pointer what it is, never the width. The readout anchors above
   * the tap point in VIEWPORT coordinates (not container coordinates), so it
   * stays visible once the container has been scrolled past the fold.
   */
  function tip(L, opts) {
    if (!L.tooltip) return { show: false };
    return {
      show: true,
      trigger: opts.trigger || 'item',
      confine: true,
      appendToBody: false,
      triggerOn: L.tapTip ? 'mousemove|click' : 'mousemove|mouseout',
      position: L.tapTip ? function (pt, params, dom, rect, size) {
        var cw = size.contentSize[0], chh = size.contentSize[1];
        var x = Math.round(pt[0] - cw / 2);
        x = Math.max(4, Math.min(x, size.viewSize[0] - cw - 4));
        var y = Math.round(pt[1] - chh - 18);
        var box = dom && dom.parentNode && dom.parentNode.getBoundingClientRect
                  ? dom.parentNode.getBoundingClientRect() : null;
        if (box) {
          var minY = Math.max(4, 8 - box.top);
          var maxY = Math.min(size.viewSize[1] - chh - 4,
                              window.innerHeight - 8 - chh - box.top);
          if (y < minY) y = Math.round(pt[1] + 26);
          if (y < minY) y = minY;
          if (maxY > minY && y > maxY) y = maxY;
        } else if (y < 4) {
          y = Math.round(pt[1] + 26);
        }
        return [x, y];
      } : undefined,
      formatter: opts.formatter
    };
  }

  /**
   * How many lines a category axis label will actually wrap to, measured
   * against the real label column width -- not guessed from a `showN` flag
   * or an embedded '\n'. That guess was wrong twice: Chart 1's "(n=X)" suffix
   * line was accounted for, but Chart 3's plain-text labels ("Unresolved,
   * published with a reason") wrap to two lines from width alone, with
   * neither a flag nor an embedded newline to detect it, and rendered
   * overlapping its neighbour at every width tested. Measuring is the only
   * version of this that cannot miss a case the boolean didn't anticipate.
   */
  function categoryLines(label, labelWidthPx) {
    _m.font = '12px ' + SANS;
    var words = String(label).replace(/\n/g, ' \n ').split(' ');
    var lines = 1, cur = '';
    for (var i = 0; i < words.length; i++) {
      if (words[i] === '\n') { lines++; cur = ''; continue; }
      var test = cur ? cur + ' ' + words[i] : words[i];
      if (_m.measureText(test).width > labelWidthPx - 10 && cur) {
        lines++; cur = words[i];
      } else {
        cur = test;
      }
    }
    return lines;
  }

  /** A horizontal bar chart, laid out for the width it actually has. */
  function barChart(id, opts) {
    var host = el(id), L = layout(host);
    var rows = opts.rows.slice();
    var top = titleTop(L.w, opts.finding, opts.subtitle) +
              (opts.showN && L.narrow ? 20 : 0);
    // Per-row height from the WORST-CASE wrap, not a boolean. A category
    // label needs roughly one 15px line-height per wrapped line, plus
    // padding so adjacent rows' labels do not touch.
    var maxLines = rows.reduce(function (m, r) {
      // Matches the yAxis data string built below EXACTLY -- same '\n'
      // placement -- or the measurement answers a question the render
      // does not ask.
      var text = opts.showN ? r.label + '\n(n=' + nf(r.n) + ')' : r.label;
      return Math.max(m, categoryLines(text, L.labelWidth));
    }, 1);
    var perRow = Math.max(30, maxLines * 16 + 8);
    host.style.height =
      (opts.baseHeight + rows.length * perRow + Math.max(0, top - 106)) + 'px';
    var ch = echarts.init(host, 'cascadia');
    ch.setOption({
      title: cascadiaTitle(opts.finding, opts.subtitle, { width: L.w - 14 }),
      grid: { left: 8, right: L.gridRight, bottom: 8, top: top,
              containLabel: true },
      xAxis: { type: 'value', name: opts.units, nameLocation: 'middle',
               nameGap: L.narrow ? 36 : 28, min: 0, max: opts.max,
               splitNumber: L.narrow ? 3 : 5,
               // K1: the axis must state its own bound. ECharts' automatic
               // 'nice' tick rounding drops the max as a labelled tick at
               // some widths (Chart 1 read "0/30/60/90" at 320px with no
               // "100", Chart 2 similarly lost its "22" -- both found by a
               // reading panel looking at the actual render, not by any
               // mechanical check). showMaxLabel forces the declared bound
               // to always render, regardless of what the rounding picks.
               axisLabel: { showMaxLabel: true, formatter: function (v) {
                 return opts.axisFormat ? opts.axisFormat(v) : nf(v);
               } } },
      yAxis: { type: 'category', inverse: !!opts.inverse,
               data: rows.map(function (r) {
                 return opts.showN ? r.label + '\n(n=' + nf(r.n) + ')' : r.label;
               }),
               axisLabel: { width: L.labelWidth, overflow: 'break',
                            lineHeight: 15, verticalAlign: 'middle',
                            interval: 0, margin: 10 } },
      tooltip: tip(L, {
        trigger: 'item',
        formatter: function (p) {
          var r = rows[p.dataIndex];
          return (opts.tooltip ? opts.tooltip(r) : r.label + ': ' + nf(r.value));
        }
      }),
      series: [{
        type: 'bar',
        data: rows.map(function (r) {
          if (!opts.colorFor) return r.value;
          var hue = opts.colorFor(r);
          return { value: r.value, itemStyle: { color: hue },
                   label: { color: CASCADIA.textInkFor(hue) } };
        }),
        itemStyle: { color: C.evergreen },
        label: { show: true, position: 'right', fontFamily: SANS,
                 fontSize: 12, color: INK.evergreen,
                 formatter: function (p) {
                   return opts.valueLabel(rows[p.dataIndex]);
                 } }
      }]
    });
    cascadiaResize(host, ch);
    cascadiaProvenance(host, opts.provenance);
    el('sum-' + id).textContent = opts.summary;
    cascadiaAccessible(host, { label: opts.ariaLabel, summaryId: 'sum-' + id,
                               tableId: 'tbl-' + id });
    return ch;
  }

  /**
   * A paired horizontal bar chart, two series per category. Used only by
   * Chart 4 (hours share vs. fees share, by role). Not folded into barChart()
   * because the two-series legend and per-series colour are structurally
   * different from every other chart's single evergreen series.
   */
  function pairedBarChart(id, opts) {
    var host = el(id), L = layout(host);
    var rows = opts.rows.slice();
    var top = titleTop(L.w, opts.finding, opts.subtitle) + (L.narrow ? 22 : 0);
    // Same measured-not-guessed row height as barChart() -- every category
    // here carries an explicit '\n(n=X)' line, same as Chart 1's, and the
    // same overlap defect would recur here without it.
    // READING-PANEL FINDING #5, 2 seats: the row label's bare "(n=X)" reused
    // the same digit the title uses for "3 applications", with two different
    // referents. Disambiguated below to "(X of N filings)"; measured here
    // against that same string so row height never drifts from what's drawn.
    var maxLines = rows.reduce(function (m, r) {
      return Math.max(m, categoryLines(
        r.label + '\n(' + nf(r.n) + ' of ' + nf(opts.nApplications) + ' filings)',
        L.labelWidth));
    }, 1);
    var perRow = Math.max(34, maxLines * 16 + 10);
    host.style.height =
      (opts.baseHeight + rows.length * perRow + Math.max(0, top - 106)) + 'px';
    // Rule 2.1 / K1: axis bounds derived from the plotted series, never
    // typed. A literal 70 happened to fit this build's numbers and would
    // silently clip the moment a role's share crossed it -- and at narrow
    // width it also placed the '%' unit name directly on top of the tick
    // that landed exactly at the typed bound, which is how the collision
    // was actually noticed.
    var maxVal = rows.reduce(function (m, r) {
      return Math.max(m, r.hours, r.fees);
    }, 0);
    var xMax = Math.ceil((maxVal * 1.15) / 10) * 10;
    var ch = echarts.init(host, 'cascadia');
    ch.setOption({
      title: cascadiaTitle(opts.finding, opts.subtitle, { width: L.w - 14 }),
      grid: { left: 8, right: L.gridRight, bottom: 34, top: top,
              containLabel: true },
      legend: { show: true, bottom: 0, left: 'center', itemWidth: 14,
                itemHeight: 10, textStyle: { fontFamily: SANS, fontSize: 12,
                                             color: C.basalt } },
      // No separate axis-name element: a '%' name at nameLocation:'middle'
      // and the legend both want the band directly below the ticks, and at
      // narrow widths they collided. Each tick states its own unit instead,
      // which needs no reserved vertical band at all.
      xAxis: { type: 'value', min: 0, max: xMax,
               splitNumber: L.narrow ? 3 : 5,
               axisLabel: { formatter: function (v) { return v + '%'; } } },
      yAxis: { type: 'category', inverse: true,
               data: rows.map(function (r) {
                 return r.label + '\n(' + nf(r.n) + ' of ' +
                        nf(opts.nApplications) + ' filings)';
               }),
               axisLabel: { width: L.labelWidth, overflow: 'break',
                            lineHeight: 15, verticalAlign: 'middle',
                            interval: 0, margin: 10 } },
      tooltip: tip(L, {
        trigger: 'item',
        formatter: function (p) {
          var r = rows[p.dataIndex];
          return r.label + '<br>' + p.seriesName + ': ' +
                 (p.seriesIndex === 0 ? r.hours : r.fees).toFixed(1) + '%';
        }
      }),
      series: [
        { name: 'Hours share', type: 'bar', itemStyle: { color: C.evergreen },
          data: rows.map(function (r) { return r.hours; }),
          label: { show: true, position: 'right', fontFamily: SANS,
                   fontSize: 12, color: INK.evergreen,
                   formatter: function (p) { return 'Hours ' + p.value.toFixed(1) + '%'; } } },
        { name: 'Fees share', type: 'bar', itemStyle: { color: C.glacier },
          data: rows.map(function (r) { return r.fees; }),
          label: { show: true, position: 'right', fontFamily: SANS,
                   fontSize: 12, color: INK.glacier,
                   formatter: function (p) { return 'Fees ' + p.value.toFixed(1) + '%'; } } }
      ]
    });
    cascadiaResize(host, ch);
    cascadiaProvenance(host, opts.provenance);
    el('sum-' + id).textContent = opts.summary;
    cascadiaAccessible(host, { label: opts.ariaLabel, summaryId: 'sum-' + id,
                               tableId: 'tbl-' + id });
    return ch;
  }

  /* ---------------- Chart 1 · coverage by court ---------------- */
  (function () {
    var d = D.c1, rows = d.courts.slice();
    var deb = rows.filter(function (r) { return r.court === 'deb'; })[0];
    var best = rows.slice().sort(function (a, b) { return b.reach - a.reach; })[0];
    // READING-PANEL FINDING #1, 2026-09-10 (4 seats, unprompted): "48" never
    // appeared against its own denominator anywhere the panel could see --
    // every seat asked how many total cases exist. Stated in the title now,
    // not only in page prose a chart-card crop would not include.
    var finding = 'Among ' + nf(d.searched) + ' of ' + nf(d.population) +
      ' Appendix B-era cases searched so far, reach runs from ' +
      Math.round(rows[0].reach) + '% to ' + Math.round(best.reach) +
      '% depending on the court' + (deb ? ', and the largest, Delaware, sits at ' +
      Math.round(deb.reach) + '%' : '');
    var subtitle = 'Share of searched cases with at least one retrievable ' +
      'fee application or order, by court. Every bar states how many cases ' +
      'that court contributed.';
    barChart('c1', {
      // FINDING #7, one seat: "deb" never gets spelled out as Delaware
      // anywhere the panel could see, only in the title's own prose -- the
      // court code itself is what appears on the axis in the same crop.
      // Named directly on the one row a reader is most likely to look up.
      rows: rows.map(function (r) {
        return { label: r.court === 'deb' ? 'deb — Delaware' : r.court,
                 n: r.cases, value: r.reach };
      }),
      // 100 is a true mathematical ceiling on a reach RATE (it cannot exceed
      // 100% by construction), not a guess at where this build's numbers
      // happen to top out -- unlike Chart 4's max, which was.
      showN: true, baseHeight: 200, units: '% reach', max: 100,
      finding: finding, subtitle: subtitle,
      valueLabel: function (r) { return r.value.toFixed(1) + '%'; },
      tooltip: function (r) {
        return r.label + '<br>' + nf(r.n) + ' cases searched · ' +
               r.value.toFixed(1) + '% reach';
      },
      provenance: { source: 'CourtListener RECAP archive', asOf: 'retrieved per document',
                    flags: 'rates over searched cases only; not-yet-searched excluded' },
      // rows here is the RAW d.courts array (sorted ascending by reach in
      // Python), whose fields are .court/.cases/.reach -- not the .label/.n
      // shape barChart's own `rows` parameter uses internally. Referencing
      // .label/.n on this array is exactly the property-name mismatch that
      // rendered as "undefined, n=NaN" until the render step surfaced it.
      summary: 'Ranked bar chart, one bar per court searched so far. Reach varies ' +
        'from ' + Math.round(rows[0].reach) + '% (' + rows[0].court + ', n=' +
        nf(rows[0].cases) + ') to ' + Math.round(rows[rows.length - 1].reach) +
        '% (' + rows[rows.length - 1].court + ', n=' +
        nf(rows[rows.length - 1].cases) +
        '). No trend or sequence is implied — courts are ranked by reach, not by size or date.',
      ariaLabel: 'Ranked bar chart: coverage reach rate by court, cases searched so far.'
    });
  })();

  /* ---------------- Chart 2 · task-vocabulary crosswalk ---------------- */
  (function () {
    var d = D.c2;
    var order = ['exact', 'rename', 'broader', 'none'];
    var labels = { exact: 'Exact match', rename: 'Renamed only',
                   broader: 'Broader in Appendix B', none: 'No UTBMS counterpart' };
    var rows = order.filter(function (k) { return d.counts[k]; }).map(function (k) {
      return { label: labels[k], key: k, n: d.counts[k], value: d.counts[k] };
    });
    barChart('c2', {
      rows: rows, baseHeight: 170, units: 'categories', max: d.total,
      finding: d.counts.exact + ' of the 22 U.S. Trustee project categories match ' +
        'a 1997 UTBMS task code exactly; ' + d.counts.none + ' have none at all',
      subtitle: 'Every Appendix B project category, classed by how it maps to the ' +
        'ABA UTBMS bankruptcy code set of 1997 — the only version of that set ' +
        'that exists.',
      colorFor: function (r) {
        return r.key === 'none' ? C.rain : C.evergreen;
      },
      valueLabel: function (r) { return nf(r.value); },
      tooltip: function (r) { return r.label + ': ' + nf(r.n) + ' of ' + d.total; },
      provenance: { source: 'ABA UTBMS 1997; U.S. Trustee Appendix B (78 FR 36248)',
                    asOf: 'both vocabularies fixed by publication', flags: 'no adjustments' },
      // READING-PANEL FINDING #6, two seats: "I looked for the actual
      // category names... and it's not on the chart itself." The names for
      // the 'none' bucket were already in the surrounding page prose, but
      // that prose sits outside the chart-card crop a reader (or a panel
      // seat) may see in isolation. Named here too, in the one place
      // guaranteed to travel with the chart.
      summary: 'Bar chart, four categories: exact match, renamed only, broader in ' +
        'Appendix B, and no UTBMS counterpart. ' + rows.map(function (r) {
          return r.n + ' ' + r.label.toLowerCase();
        }).join('; ') + '. The ' + d.counts.none + ' with no counterpart are ' +
        d.noneCategories.join(', ') + '. No trend is implied — this is a ' +
        'one-time classification of a fixed vocabulary, not a series over time.',
      ariaLabel: 'Bar chart: task-vocabulary crosswalk by match type, four categories.'
    });
  })();

  /* ---------------- Chart 3 · firm-identity resolution ---------------- */
  (function () {
    var d = D.c3;
    var rows = [
      { label: 'Resolved by a stated rule', key: 'resolved', value: d.resolved },
      { label: 'Unresolved, published with a reason', key: 'unresolved', value: d.unresolved }
    ];
    var pct = Math.round(1000 * d.resolved / d.total) / 10;
    barChart('c3', {
      rows: rows, baseHeight: 150, units: 'caption/firm pairs', max: d.total,
      finding: d.resolved + ' of ' + d.total + ' caption-to-database firm pairs ' +
        'resolve by a stated rule (' + pct + '%); every one of the rest is published, not dropped',
      subtitle: 'Every caption-derived firm string seen in a stored document, ' +
        'matched against the database’s own short firm names by a token-subset rule.',
      colorFor: function (r) { return r.key === 'resolved' ? C.evergreen : C.rain; },
      valueLabel: function (r) { return nf(r.value); },
      tooltip: function (r) { return r.label + ': ' + nf(r.value) + ' of ' + d.total; },
      provenance: { source: 'Bankruptcy Research Database; RECAP docket captions',
                    asOf: 'as resolved in this build', flags: 'no adjustments' },
      // READING-PANEL FINDING #2, 4 seats, all independently asked "what are
      // the 16 reasons." Checked against the data: they are not 16 reasons.
      // Every unresolved pair carries the IDENTICAL templated sentence -- one
      // shared stated mechanism, not a per-case diagnosis. The previous
      // summary here claimed each pair "carries its own stated reason",
      // which overclaimed a distinctiveness the data does not have; this is
      // a correctness fix to this chart's own copy, not only a response to
      // the panel's question. d.reasonsUniform is computed at build time so
      // this sentence cannot drift from the underlying data again.
      summary: 'Bar chart, two categories. ' + d.resolved + ' pairs resolved (' + pct +
        '%), ' + d.unresolved + ' unresolved. ' + (d.reasonsUniform
          ? 'Every unresolved pair is published against the SAME stated ' +
            'mechanism -- the subset rule did not match -- not a distinct ' +
            'diagnosis per pair; which specific token mismatch caused each ' +
            'one is not yet classified.'
          : 'Each unresolved pair carries its own stated reason in the ' +
            'data table.'),
      ariaLabel: 'Bar chart: firm-identity resolution outcome, resolved versus unresolved.'
    });
  })();

  /* ---------------- Chart 4 · staffing mix ---------------- */
  (function () {
    var d = D.c4;
    var partner = d.roles.filter(function (r) { return r.role === 'partner'; })[0];
    var assoc = d.roles.filter(function (r) { return r.role === 'associate'; })[0];
    var roleLabel = { partner: 'Partner', associate: 'Associate',
                       of_counsel: 'Of counsel', paraprofessional: 'Paraprofessional' };
    var rows = d.roles.map(function (r) {
      return { label: roleLabel[r.role] || r.role, n: r.applications,
               hours: r.hoursShare, fees: r.feesShare };
    });
    pairedBarChart('c4', {
      rows: rows, baseHeight: 210, nApplications: d.nApplications,
      finding: 'One application\u2019s own staffing split, not a caseload pattern: ' +
        'its partners bill ' + partner.hoursShare.toFixed(1) + '% of hours but take ' +
        partner.feesShare.toFixed(1) + '% of fees',
      subtitle: 'Share of in-scope hours and fees by conformed timekeeper role. One ' +
        'application (docket vaeb 15-33896) reports its own partner, associate and ' +
        'of-counsel split; it and two smaller filings each add paraprofessional time ' +
        'only — the filing count on every bar states which.',
      summary: 'Paired bar chart, four roles, two series each: hours share and fees ' +
        'share. One application, docket vaeb 15-33896, carries the partner, associate ' +
        'and of-counsel rows: partner holds ' + partner.hoursShare.toFixed(1) +
        '% of hours and ' + partner.feesShare.toFixed(1) + '% of fees; associate holds ' +
        assoc.hoursShare.toFixed(1) + '% and ' + assoc.feesShare.toFixed(1) +
        '%. Two smaller filings add only paraprofessional time, pooled into that row. ' +
        'This is one filing\u2019s own internal split, not a sampled pattern across cases.',
      provenance: { source: 'Fee-application timekeeper summary exhibits',
                    asOf: 'as parsed in this build', flags: 'n=' + d.nApplications +
                    ' applications; not a population figure' },
      ariaLabel: 'Paired bar chart: one application\u2019s staffing split, hours share ' +
        'and fees share by role.'
    });
  })();

  /* ---------------- Chart 5 · requested vs. allowed reconciliation ---------------- */
  (function () {
    var d = D.c5;
    var labels = {
      '1: no parsed order on this docket': 'No parsed order on the docket',
      '2: order is omnibus': 'Order is omnibus (multiple awards)',
      '3: filer strings do not resolve to one firm': 'Filer did not resolve to one firm'
    };
    var order = ['1: no parsed order on this docket', '2: order is omnibus',
                 '3: filer strings do not resolve to one firm'];
    var rows = order.filter(function (k) { return d.counts[k]; }).map(function (k) {
      return { label: labels[k] || k, n: d.counts[k], value: d.counts[k] };
    });
    barChart('c5', {
      rows: rows, baseHeight: 160, units: 'applications', max: d.total,
      finding: 'None of the ' + d.total + ' applications with a matching docket could ' +
        'be checked against what the court allowed',
      subtitle: 'Every parsed application, and the rule that stopped it from being ' +
        'paired with an order. A looser pairing rule would pair more and claim less.',
      valueLabel: function (r) { return nf(r.value); },
      tooltip: function (r) { return r.label + ': ' + nf(r.value) + ' of ' + d.total; },
      provenance: { source: 'Fee applications and fee orders, RECAP archive',
                    asOf: 'as reconciled in this build',
                    flags: 'paired: ' + d.paired + ' of ' + d.total },
      summary: 'Bar chart, three reasons no pairing was made: ' + rows.map(function (r) {
        return nf(r.n) + ' — ' + r.label.toLowerCase();
      }).join('; ') + '. Zero of ' + d.total + ' applications were successfully paired. ' +
        'For the ' + nf(d.orderGap.applications) + ' with no parsed order: order-shaped ' +
        'docket entries were found and correctly classified on ' +
        nf(d.orderGap.docketsWithOrderSeen) + ' of the underlying ' +
        nf(d.orderGap.dockets) + ' dockets (' + nf(d.orderGap.orderEntriesSeen) +
        ' entries seen in total) — so this is not a parser miss. Every one of those ' +
        'entries is marked unavailable in RECAP: no PDF has been uploaded, the same ' +
        'coverage gap Chart 1 measures directly.',
      ariaLabel: 'Bar chart: applications not paired with an order, by blocking rule.'
    });
  })();

})();
