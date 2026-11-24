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
| `t832_food_locked.py` | 8.32: Food locked. Only the hero and the coming soon message, Open Body, no food input reachable, data kept through reload, backup and restore, no Food tip, flag on brings Food back |
| `t834_0_units.py` | 8.34 Part 0: Settings Food targets and the setup calorie line hidden while Food is locked; the weight unit setting (lb or kg) apart from mi and km, the migration that changes no stored number, kg entry stored in lb, kg steppers, no lb text left in kg, backup and restore of the unit |
| `t834_12_plan_today.py` | 8.34 Parts 1 and 2: the Plan active exercise card (header, big weight, set tiles, steppers, keypad, LOG SET, links, delete and undo, other lifts as rows), Today (greeting, streak pill, week ring and strip, workout card, stat tiles with no fake numbers), the floating tab bar, weekly streak cases, reduced motion, kg |
| `t834_short_normal.py` | 8.34 fix: the Normal and Short switch on the Plan card and on Today, before and during a workout, with sets logged on a lift Short keeps and on one it drops. Checks that switching never changes logged data in memory or in storage, that hidden sets show again on Normal, that the choice survives a reload, and that Quick Log aims at a short day with logs |
| `t834_3_finish.py` | 8.34 Part 3: the finish card. PR rules from plain data (weight PR, rep PR at a weight, body weight reps, a run of weekly top weights, ranking and the cap of 3, no PR on a first log, quick logs count as history), session times range checks, the real flow from the last set to Finish workout, the summary and last week comparison, the 1080 x 1350 share image, Web Share and the download fallback, an edited set recomputing, the fallback line, kg |

`common.py` holds the shared helpers: the page setup, `check()` and `baseline()`. `gapfn.js` measures the gap under a hero.

## Food lock (8.32)

Food is locked by `FOOD_ENABLED = false` in index.html and in `api/_food.js`. The checks that cover the Food screen itself (8.30 items 3 and 5, and 8.31 item 3) turn Food on inside the page with `FOOD_ON` from `common.py`. That way the Food code stays tested for when it comes back. `node food.js` section 11 proves that with Food locked, `/api/meal` and `/api/barcode` answer "Not available", make no outside call and read no key.

## Plan card and Today (8.34)

Plan shows the next lift as a card and the other lifts as rows; the full row for the card's lift opens through Notes and details. `t825` and `t826` test the full rows, so they turn the card off with an init script (`PA_OFF` in `common.py` does the same inside a page). The 8.29 and 8.30 hero checks for Today and Plan are retired, since both screens now use the headers from the references. The header and tab bar baselines were re-recorded in 8.34 for the floating tab bar; only the tab bar values changed.

## Week strip and navigation (8.37)

`t837_a_strip.py` covers the shared week strip on Today and Lift for three plans at 390 and 320: past, today, future and rest days, previewing next week without saving it, Short and Change workout per day, and storage unchanged after a round trip. `t837_b_nav.py` covers the four or five tab bar, the gear, the logo going to Today, the Change workout sheet and the removal of every Quick Log label. `baselines/storage_keys_835b.json` lists the storage keys on master before 8.37, so a new key fails the check. 8.37 removed the logo menu and the Quick Log tab, so the older checks for them now test where those items moved. The header and tab bar baselines were re-recorded for the narrower logo and the four tab bar.

## Setup maxes (8.37b)

`t837b_setup_max.py` covers the setup step for the three maxes at 390 and 320, in lb and kg. Each lift can take a typed max, a weight and reps (1 to 10, estimated with the same `epleyEstimate` Settings uses, then editable), or Skip for now, which saves no max for that lift.

## End of block (8.38)

`t838_block.py` seeds a 10 week block with `block_seed.js` and covers, at 390 and 320: no dead week 11 button, the block card once and on later opens (never during a workout), the soft card, Not yet up to 3, the proposed maxes (gain, no data, never lower, 25 percent flag, kg), Edit maxes, START BLOCK 2 through the archive with week 1 at max times percentage, Undo, backup with and without `monk_block_history_v1`, and the share image (size, fonts, weights off, no gain lift left off, download fallback, from Settings).

## Running without a race and Today first (8.39)

`t839_run_base.py` covers, at 390 and 320 and in km:
- the setup questions (Do you run, days a week, race Skip, Not now);
- the Run tab and the Today tile with no race;
- logging a run from Today;
- Settings Running;
- the three existing user cases;
- a race set later;
- backup with and without `monk_run_base_v1`.

`t839b_today_first.py` covers:
- Today showing today's planned workout first;
- a day counting as done for today only with today's date;
- strip marks only from this week's dates;
- plan weeks following the calendar: a missed week, three weeks away, the last week, finishing early, and a new user.

## Baselines

Some checks used to compare against a copy of the previous build served on a second port. In the repo they compare against saved values in `tests/browser/baselines` instead:

- the header, Settings icon and tab bar (8.29)
- the Week review and The Edge headlines (8.30 item 1)
- the Food block order (8.30 item 3)
- the strip style (8.31 item 1)

These values were recorded from 8.31. The same checks had already passed against 8.30 on a second port before they moved here. `827-about-edge-before.html` keeps the About and The Edge text from before 8.27, so the merge check can prove no text was lost.

## Retired checks

In 8.31, twelve 8.29 checks were retired: "everything below the hero unchanged against 8.28", for each of six screens (Today, Plan, Quick Log, Progress, Run and Food) at 360 and 390 wide. They compared every block under the hero with the 8.28 build. 8.30 changed those blocks on purpose: titles were removed, Food was reordered and Recent workouts was added. 8.31 changed them again with the Body view. So these checks could only fail, and there is no 8.28 server in the repo to compare against. The hero checks themselves remain, and the header, Settings icon and tab bar check now uses a saved baseline.
