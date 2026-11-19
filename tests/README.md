# Tests

Two kinds: unit suites at the repo root, and browser checks in `tests/browser`.

## Unit suites

```
node food.js
node onb.js
node sets.js
node compat.js
```

Baseline: food, onb and sets pass with no failures. compat has 3 known failures.

## Browser checks

These need Python 3 with Playwright (`pip install playwright`, then `playwright install chromium`).

1. Serve the repo: `python3 -m http.server 8765` from the repo root.
2. Run everything: `tests/browser/run_all.sh`. It prints one line per file and then the unit suites. It exits non zero if any browser check fails.
3. Run one file: `python3 tests/browser/t831_3_weight_history.py`.

Settings, all optional:

- `RTW_URL` is the page to test. The default is `http://localhost:8765/index.html`.
- `RTW_SHOTS` is where screenshots go. The default is `tests/browser/out`, which is not committed. Logs from `run_all.sh` go there too.
- `RTW_UPDATE_BASELINES=1` rewrites the files in `tests/browser/baselines` from the build under test. Use it only after a change you meant to make.

Each check pins the clock to a fixed day in November 2026 and loads the same seed data from `seed.js`, so results do not depend on the day you run them.

## What each file covers

| File | Covers |
|---|---|
| `t825_plan_week.py` | 8.25: plan weeks after time away, deload weeks, freestyle, own plans, tab bar fit, logo menu, Week review wording |
| `t826_lift_notes.py` | 8.26: per lift notes, the Last time line, notes across swaps, Quick Log notes, backup and restore |
| `t827_quicklog_menu_edge.py` | 8.27: Quick Log Add exercise and search, new custom exercises, logo menu order, About merged into The Edge, rest timer over sheets |
| `t828_tips.py` | 8.28: one time tips shown once, never stacked, never over a tap target, Show tips again, backup and restore |
| `t829_hero.py` | 8.29: hero fit, font, square, spacing, Plan first card above the fold, lines from real data, offline font |
| `t830_1_titles.py` | 8.30 item 1: no repeated title under a hero, 24 px gap, Run unit toggle, Week review and The Edge headlines |
| `t830_2_recent_workouts.py` | 8.30 item 2: Quick Log recent workouts, the session list survives a reload |
| `t830_3_food_order.py` | 8.30 item 3: Food weigh in first, meal input above the totals |
| `t830_4_run_note.py` | 8.30 item 4, updated in 8.31: run note row, history line, length cap, backup and restore |
| `t830_5_chart_labels.py` | 8.30 item 5: chart date labels never collide at 320, 360 and 390 |
| `t830_6_menu_more.py` | 8.30 item 6: logo menu More row and More page, menu tip, taps outside the open menu |
| `t831_1_strip.py` | 8.31 item 1: top strip shows Home, The Edge and Week review; the old Progression route opens Progress |
| `t831_2_run_note_with_run.py` | 8.31 item 2: a run note saves only with its run; old notes with no run stay stored and hidden |
| `t831_3_weight_history.py` | 8.31 item 3: weight history on Body, units, the Food link, chart labels, backup and restore, the Body tip |

`common.py` holds the shared helpers: the page setup, `check()` and `baseline()`. `gapfn.js` measures the gap under a hero.

## Baselines

Some checks used to compare against a copy of the previous build served on a second port. In the repo they compare against saved values in `tests/browser/baselines` instead:

- the header, Settings icon and tab bar (8.29)
- the Week review and The Edge headlines (8.30 item 1)
- the Food block order (8.30 item 3)
- the strip style (8.31 item 1)

These values were recorded from 8.31. The same checks had already passed against 8.30 on a second port before they moved here. `827-about-edge-before.html` keeps the About and The Edge text from before 8.27, so the merge check can prove no text was lost.

## Retired checks

In 8.31, twelve 8.29 checks were retired: "everything below the hero unchanged against 8.28", for each of six screens (Today, Plan, Quick Log, Progress, Run and Food) at 360 and 390 wide. They compared every block under the hero with the 8.28 build. 8.30 changed those blocks on purpose: titles were removed, Food was reordered and Recent workouts was added. 8.31 changed them again with the Body view. So these checks could only fail, and there is no 8.28 server in the repo to compare against. The hero checks themselves remain, and the header, Settings icon and tab bar check now uses a saved baseline.
