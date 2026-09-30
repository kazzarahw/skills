# Design system

The look, and the constraints that keep it safe. Read before restyling, adding a panel type, or editing `assets/template.html`.

## Contents
- The look
- Tokens
- Type
- Encoding rules
- What to leave out
- Editing the template safely

## The look

A restrained research-lab aesthetic: a duotone of one saturated ink on off-white paper, flat fills, hairlines instead of boxes, sharp corners, tracked-caps micro-labels, very large thin numerals, and a dot texture in place of gradients. The template uses system font stacks that degrade to ordinary sans without looking broken.

The dashboard reads as a page, not an app: one column of panels divided by 1px rules, the title as a huge condensed headline, a sticky single-row toolbar.

## Tokens

All colours derive from two inputs, `--accent` (the ink) and `--paper`, using `color-mix`, so changing `--accent` restyles everything consistently.

| Token | Light | Dark |
|---|---|---|
| `--ink` | `--accent` (default `#0000f2`) | accent mixed 38% into white |
| `--paper` | `#f4f4f2` | accent mixed 14% into near-black |
| `--muted` | ink 66% on paper | same formula |
| `--rule` | ink 20% on paper (hairlines) | same |
| `--wash` | ink 6% on paper (hover, track) | same |
| `--c0…--c5` | ink at 100, 70, 46, 30, 19, 11% on paper (series ramp) | same |

Dark mode is chosen by `prefers-color-scheme`, the THEME button (remembered in `localStorage` when available), `theme.mode` in the config, or `#theme=dark`.

Pick an accent that keeps ≥ 4.5:1 against `#f4f4f2`; `build` refuses lighter ones (yellow-ish and pastel inks fail). Good alternatives to cobalt: deep teal `#00635d`, oxblood `#8a1c2b`, graphite `#1f2937`. Choose by data if it helps (a calm teal for compliance scans, cobalt by default), not for decoration.

## Type

- Display and numerals: condensed stack (`Bahnschrift`, `Arial Narrow`, `Roboto Condensed`, `Liberation Sans Narrow`, …), weight 300, tabular figures. Headline `clamp(44px, 8.2vw, 112px)`, uppercase, tight leading. KPI numerals up to 84px.
- Labels: 10.5px uppercase, `letter-spacing:.1em`, weight 500. Used for panel titles, column headers, legends, buttons, footers.
- Body: system sans at 14px. Addresses, ports and timestamps: monospace 12.5px.

## Encoding rules

- **Hero dimension = darkest ink.** The most important value in a chart (high severity, failures, the biggest byte source) gets `--c0`; the rest step down the ramp. Severity is lightness, never red/amber/green.
- **Series:** at most 5 named series plus "other". Order by importance (severity high→low, failure first) or by count. Colour follows the value's slot, and every series has a legend entry that also filters.
- **Redundancy:** colour is never the only carrier. Signals use a filled / half / hollow square plus the word HIGH / MED / INFO; ranks print the number; tooltips name the series.
- **Charts:** thin bars with a 1px gap, hairline grid at 0, 50%, 100% of a rounded-up maximum, no chart borders, axis labels in the caps style. Sparklines are a 1px line without fill.
- **Heat:** dot area encodes count (square-root scale so area is honest); empty hours are a tiny rule-coloured dot so the grid stays visible.
- **One screen first:** KPIs, signals and the timeline sit above the fold; detail (ranks, table, drawer) follows. Every number can be clicked through to events.

## What to leave out

A second accent hue, pie/donut charts, dual axes, gauges, gradients, shadows and rounded corners. If a chart needs a legend with more than six entries, the field has too many values: rank it instead.

## Editing the template safely

`assets/template.html` has a `<style id="soc-style">` block, a `<script id="soc-app">` block, and placeholders (`__CSP__`, `__TITLE__`, `<!--__CFG__-->`, `<!--__DATA__-->`) that `soc_dash.py build` fills. The build hashes the style and script blocks into the CSP, so edits inside them are fine; edits that add a new inline block or attribute are not.

- Render data only with `h()`/`sv()` (DOM builders that use `textContent`). Never `innerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, or string timers. Log text is hostile input.
- No inline `on*=` attributes (the helper ignores them) and no `style=` attributes or `setAttribute('style', …)`. Set styles with `el.style.prop = …` (allowed under the style hash) or classes. CSP drops the forbidden forms without an error.
- No network: no fonts, scripts, images, or `fetch`. `verify.py` fails when an external `src`, `href` or `url()` reference appears.
- A new panel type is a function returning `{el, update}` registered in `builders`; `update()` recomputes from the shared `fails` bitmask. A panel that shows alternatives to its own filter ignores that field's bit: `visible(i, ignoredBits)`.
- Keep per-event work in typed arrays. The template handles 300k+ events; per-event objects or DOM nodes per event do not.
- Re-run `verify.py` after any template edit; it exercises clicks, not just load.
