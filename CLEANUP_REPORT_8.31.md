# Cleanup report, build 8.31

All four items were pushed. Live at runtheweights.vercel.app: Version 8.31, service worker cache `monk-mode-v109`. Origin matches local.

## Preflight

- The build was 8.30, and the tree was clean and pushed at 767654d.
- Tag `pre-8.31` was created on 767654d and pushed.

## Commits

| Item | Commit | SW cache | Result |
|---|---|---|---|
| 1. Progression leaves the top strip | 07f7889 | v107 | pushed |
| 2. Run note saves only with the run | 7f0ca27 | v108 | pushed |
| 3. Weight history on Body | e683409 | v109 | pushed |
| 4. Browser checks in the repo | 18ccdcb | none (tests only) | pushed |
| Report | this commit | none | |

Before each push I reran every earlier check: the 8.26 to 8.30 browser checks, each earlier 8.31 item, and the four unit suites. All passed each time.

## Item 1. Progression leaves the top strip

**Audit:**
- The old Progression screen held an intro paragraph on double progression and the lift progress cards (`#progressCards`).
- Since 8.24, both have moved at load into the Progress tab, under "See full calendar and every lift". The strip's Progression button opened an empty screen. Nothing on it was unique.

**Changes:**
- Removed the Progression button from the strip.
- `goSec('progression')`, the only old route, now opens the Progress tab.
- Progression was dropped from the list of info screens.
- The screen's markup and code are still in place, because they are what moves into Progress.
- No tip, menu row or More row pointed at it.

**Unreachable:** nothing. Home, The Edge and Week review are still reachable from the strip. Week review and The Edge are also on More, and the lift cards are on Progress.

**Checks** (18 of 18):
- The strip shows exactly Home, The Edge, Week review on each of its three screens, with the right one marked.
- The strip looks the same as 8.30.
- No Progression text in the strip, the menu, More or the tab bar.
- The old route lands on Progress, both with and without `goTab('info')` first.
- The lift cards and intro are reachable on Progress.
- More lists only Week review and The Edge, and the logo menu is unchanged.
- All three strip screens show content, with no page errors.

## Item 2. Run note saves only with the run

**Changes:**
- On a date with no saved run, typing, blur, closing the note row, Cancel and a tap outside the sheet no longer store the note. Save writes it once the run itself is saved.
- On a date that already has a run, the note still autosaves as in 8.30.
- The sheet now shows a note only when its date has a saved run.

**Notes with no run:**
- I cannot count these from here. They live in each phone's local storage, and this machine has none of Billy's data.
- The app now has `orphanRunNoteCount()` to count them. They are kept, never deleted, and never shown: not in run history, not in the sheet.

**Decision:** saving a new run with an empty note field leaves any older stored note for that date in storage. Typing a note and saving replaces it.

**Checks** (17 of 17):
- Typing, blur, closing the row, Cancel, a tap outside and a reload all store nothing.
- Save stores the note, and it shows in run history.
- A saved run reopens with its note. Editing autosaves, and closing keeps the edit.
- Two planted notes with no run are counted and hidden from history and the sheet. They stay stored, including after a run is saved on one of those dates with an empty field.
- No page errors.
- The 8.30 run note check that expected "autosaves while typing" on an unsaved run was changed to the new behavior, and a check that the note saves with the run was added. It passes 15 of 15.

## Item 3. Weight history on Progress, Body

**What was built:**
- **Add weight form** at the top of Body:
  - Date (defaults to today, past dates allowed, no future dates) and weight, with Save.
  - One weight per date. Picking a date that already has a weight puts that value in the field and says "This date has X lb. Save replaces it." before you save.
- **Weigh ins list**, newest first, as ruled rows: date, weight, Edit, Delete.
  - Edit puts the row back in the form.
  - Delete removes it at once with a 5 second Undo bar and no dialog. It reuses the existing toast.
- **Week to week line**: "This week averages X lb, down Y lb from last week." It compares this 7 day average with the 7 days before it.
- **Chart**: the existing Body chart over every entry, with the 7 day average. It uses the 8.30 label collision logic, since it already ran through `lineChartSVG`.
- **Range**: 50 to 700 lb, or 23 to 317 kg. Anything else gets "Enter a weight between 50 and 700 lb."
- **Shared data**: the same `monk_bodyweight_v1` store as Food and Today, so weights already saved stay and show. Food's weigh in still writes today only, and it shows on Body and the other way round.
- **Stat card**: "None yet / Add your weight to see this" is now a button that opens the form on Body.
- **Backup and restore**: already carried `bodyweight`. No storage format change, so no migration and no extra backup step was needed.
- **Tip**: "Log your weight here any day. Past days work too." It shows once, on the first visit to the Body view, above the form.

**Decision, units:** there is no weight unit setting in the app. The only unit setting is the mi and km toggle on Run. I used it: km shows and takes weight in kg, mi in lb. Weights are always stored in lb, so nothing already saved changes. Food's weigh in still says lbs.

**Decision, Add weight button:** the empty Body view's old Add weight button sent you to Today's weight field. Add weight now opens the form on Body.

**Checks** (52 of 52):
- The stat card is a button and opens the form with focus in the weight field.
- Form defaults, and every field and button is 44 px.
- Add today, add three weeks ago, edit and replace, then delete with Undo. A second delete expires after 5 seconds, and a late Undo does nothing.
- The chart summary and the week to week line update.
- A future date is blocked.
- 49, 701 and empty are rejected. 50 and 700 are accepted.
- In kg: the form and list show kg, 80 kg is stored as 176.4 lb, and 20 kg and 318 kg are rejected.
- A weight entered on Food shows on Body, and the reverse.
- Chart labels don't collide at 320, 360 and 390, with no sideways scroll.
- The older weight is kept.
- The backup carries every weight. A restore into a fresh install keeps them all, and they survive a reload.
- The tip shows once by the form, not on Lifts. It is under 15 words, never shows again after Got it, and is in the backup.
- No page errors.

## Item 4. Browser checks in the repo

**Added:** `tests/README.md` (how to run, what each file covers), `tests/browser/run_all.sh`, `common.py`, `seed.js`, `gapfn.js`, `baselines/` and 15 check files.

**Coverage, 8.21 to 8.30:**
- The scratch folder had pass or fail browser checks only for 8.25 to 8.30.
- For 8.21 to 8.24 it held measuring scripts that check nothing (screenshots, contrast and layout counts), so there was nothing to port for those builds.
- The 8.25 check moved in as `t825_plan_week.py`. Its menu step was updated for 8.30, which moved Week review into More.

**Retired, 12 checks:** "everything below the hero unchanged against 8.28" in 8.29, for Today, Plan, Quick Log, Progress, Run and Food at 360 and 390. 8.30 changed those blocks on purpose, and 8.31 changed them again. There is also no 8.28 server in the repo to compare against. The hero checks remain.

**Old-build comparisons moved to saved baselines:**
- the header, Settings icon and tab bar, per screen
- the Week review and The Edge headlines
- the Food block order
- the strip style

The values were recorded from 8.31, after the same checks had passed against 8.30 on a second port.

**Updated to match 8.30 and 8.31 behavior:**
- the 8.25 menu step
- the 8.30 item 3 order check: the compare build already had the weigh in, so it is no longer filtered from one side only
- the 8.30 item 4 run note check (see item 2)

The 8.27 and 8.28 checks were already updated in 8.30.

**Full set at 8.31:**

| File | Result |
|---|---|
| t825_plan_week | 54 of 54 |
| t826_lift_notes | 26 of 26 |
| t827_quicklog_menu_edge | 47 of 47 |
| t828_tips | 64 of 64 |
| t829_hero | 117 of 117 |
| t830_1_titles | 45 of 45 |
| t830_2_recent_workouts | 21 of 21 |
| t830_3_food_order | 30 of 30 |
| t830_4_run_note | 15 of 15 |
| t830_5_chart_labels | 32 of 32 |
| t830_6_menu_more | 20 of 20 |
| t831_1_strip | 18 of 18 |
| t831_2_run_note_with_run | 17 of 17 |
| t831_3_weight_history | 52 of 52 |

**Unit suites:** food 496 passed and 0 failed, onb 138 and 0, sets 272 and 0. compat 83 passed and 3 failed: the 3 known failures. All match baseline.

## Not touched

- The Edge content, the hero words, the Settings icon and the bottom tab bar
- Plan and Today logic
- Quick Log recents and the two hour session split

## Process notes

- While the item 2 checks were running, I started item 3 in the same file the test server serves. I stopped that run, set item 3 aside, rebuilt item 2 alone, reran the full set on it, and only then pushed item 2. Item 3 was tested on its own copy and then in the repo before its push.
- The local test server on port 8765 stopped once during item 4. I restarted it and reran.
- `build_state.md` is gitignored, so its 8.31 entry is local only.
- Skills used: none.
