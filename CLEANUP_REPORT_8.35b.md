# Cleanup report, build 8.35b

Local branch `fix-daylog` only. Not pushed, not merged. Master has not moved: it is still 29e39a9, the base of this branch.

| Part | Commit | Service worker cache |
|---|---|---|
| Part A: one day, one log | 836bed7 | none |
| Part B: Short and Quick Log flow | 1ec25fb | none |
| Parts C and D: bottom bar, Lift rename, navigation rule | 1c39987 | `monk-mode-v116` |
| This report | next commit | `monk-mode-v116` |

## Part A: data layer

- **New key `monk_day_added_v1`.** It records which lifts were added to a day, as `{'week|dayId': [exercise ids]}`.
  - It is in backups as `dayAdded` and is range checked on restore: week up to 200, day ids are letters, digits, `_` and `-`, at most 20 ids per day and 400 days.
  - An old backup without the key loads and leaves the key as it was.
- **Day label on new entries only.** A new set entry gets `day`, the day it was logged on. Old entries are never changed.
  - A restore drops a bad label and keeps a good one.
  - Finding the day of an entry, in this order: its label, then the exercise's only programmed day, then a lift added to that day, then the finish time for that date, then the weekday's slot.
- **Fixed cases.**
  - A: a logged lift that Short drops stays on the day, marked "Added to this day".
  - B and D: a Quick Log set on a planned lift shows on that day's card and counts for the day, also after a reload.
  - E: picking another workout on a day with sets logged asks "Switch today to X? Your logged sets stay." and then takes over today, not the next day.
  - C already worked and is covered by a test.
- **Old Quick Log entries** give the same totals as master: volume 96350, streak 6, sessions 6 and 2, 4 entries.
- **`test_backup` was absent**, so the real backup check was skipped. Old, new and out of range backups are tested with built files.

## Part B: Short and Quick Log

- Short on Today and in the Lift header opens the time picker: 20, 30, 45 and 60 minutes.
- The proposal shows "Shorter Upper A, 30 minutes", the lift list, the time, and "Use this workout", Back and Different workout. All are 44 px.
- "Use this workout" returns to Today. Today and Lift show "Short Upper A" and the line "Planned workout: Upper A. Restore".
- Restore and Normal bring the plan back. Logged sets are kept, storage is the same before and after.
- Next week the same day is the normal plan.
- **Fixed on the way:**
  - The time preview ignored the picked time. It now fits: Upper and Lower 20 min gives 2 lifts in 13 to 15 min, 30 gives 4 in 24 to 28, 45 gives 7 in 38 to 42, 60 gives 8 in 42 to 46. Arnold fits too.
  - Weights now prefill from the last logged weight for that lift in any workout, before the box and the target.

## Part C: bottom bar and Lift

- **Bar while Food is locked:** Today, Lift, Run, Quick Log, Progress. With Food on, Food takes the Quick Log slot.
- **Run is always shown.** With running off, Run shows "Running is off." and a "Turn on running" button.
- **No label is cut at 390 or 320.** Each tab is 66 px wide at 390 and 53 px at 320. "Quick Log" wraps to two lines at 320. All are at least 44 px.
- **Every tab clears the floating bar** at both widths. Tested on Today, Lift, Run, Quick Log and Progress.
- **Today:** a "Quick Log" button with "Log a lift without a plan" under START WORKOUT. Ink outline, 44 px, never persimmon.
- **Lift toolbar:** a "Quick Log" link next to Rest timer. They stay side by side at 390 and 320.
- **Rename:** the tab, hero word, section label and every "Plan screen" phrase now say Lift.
- **Where "Plan" still shows, and why:**
  - "Change Training Plan" in Settings, because it is the program, not the screen.
  - "Planned workout: X. Restore", as the spec asks.
  - The lower case "plan" in plan setup, the plan builder and tips, because those are the program.

## Part D: navigation rule

### Inventory before the change

Taps are counted from Today.

| Control | Where | What is in it | Taps |
|---|---|---|---|
| Logo menu | Header, every screen but Today | Today, Plan, Quick Log, Food, Run if on, Progress, More | 1 to open |
| More page | Logo menu, More | Week review, The Edge | 2 |
| Rest timer | Lift toolbar | Rest presets | 2 |
| Warm up | Lift card | Warm up sets | 2 |
| Notes and details | Lift card | Notes, RPE, failure | 2 |
| Add exercise | Lift, under the list | Exercise picker | 2 |
| Row heads | Lift, full list | Sets for that lift | 2 |
| See all options | Swap sheet | More swaps | 3 |
| Race plan | Run | Race plan | 2 |
| See full calendar | Progress | Full calendar | 2 |
| Log a workout I already did | Quick Log | Past workout form | 2 |
| How | Lift plan notice | Explainer | 2 |
| Run note | Run | Note field | 2 |

The Today links "Short on time" and "Going out?" are visible buttons, not a dropdown, so they stay.

### After

- **The logo menu holds Quick Log, Week review, The Edge and Settings.** Today, Lift, Run and Progress left it because they are in the bar.
- **Quick Log stays in the menu as the one exception.** The spec lists the menu as one of the four Quick Log entry points.
- **Food is not in the menu while locked.** It returns to the bar when the flag is on.
- **The More page has no entry point now.** Its two rows, Week review and The Edge, are in the menu itself. The page is kept, so old links still work.
- **The workout title on Lift is a plain heading**, not tappable. Days switch with the day strip.
- **Every daily action is on screen:** Normal, Short, START, Quick Log on Today and in the toolbar. The expanders above are details of one lift, not a daily action.
- **The menu tip now reads** "Week review, The Edge and Settings live here."

## Tests

- New tests:
  - `t835b_a_daylog.py`: 75 checks.
  - `t835b_b_short.py`: 92 checks.
  - `t835b_cd_nav.py`: 66 checks. It covers both Food states, the 390 and 320 widths, the four Quick Log entry points and the way back, the menu, the title and the confirmation.
- Three plans: Upper and Lower, Arnold, and Advanced with running on. Each case is followed by a reload.
- Updated tests for the new bar and menu: t825, t827, t828, t830_6, t831_1, t832, t834_12, t834_short_normal and `food.js`. The t829 header baselines were saved again for the tab bar only; the header and gear are unchanged.
- **Full suite:** 952 browser checks over 22 files, 0 failed. food.js 511 passed, onb.js 138, sets.js 272, 0 failed. compat.js has its 3 known failures.
- Screenshots in `tests/browser/out/`, at 390 and 320:
  - `835b-today`
  - `835b-time-picker`
  - `835b-proposed`
  - `835b-lift-short`
  - `835b-confirm`
  - `835b-bar`

## Kept or not done

- **The `short` field on quick sessions was not used.** In the final flow, Normal and Restore remove the short overlay, and logged lifts stay as added. Part A item 4 suggested the field, but this flow needs no new stored field.
- **Known limit:** for entries made before the label, one exercise programmed on two days and logged on two days on the same date can still be read as either day. None of the preset plans programs a lift on two days.
- **Known limit:** an own plan with the same exercise twice in one day still shares one row id.
- **Security review of the branch diff:** no findings. Every name typed by the user goes through `paEsc` or `paJs`, the menu labels are fixed text, and the backup values are range checked.

## Skills used

- `anthropic-skills:token-smart-work`
- `design:accessibility-review`
- `design:ux-copy`
- `design-skills:interaction-design`
- `engineering:testing-strategy`
- `security-review`
