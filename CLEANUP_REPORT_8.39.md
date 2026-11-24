# 8.39 Running without a race

Branch `run-base`, cut from master 53dd18d (8.37d), not from block-rollover. Build label 8.39, cache `monk-mode-v122`. Pushed for a preview only. Not merged.

## Skills used

anthropic-skills:token-smart-work, design:ux-copy, design:accessibility-review, design-skills:interaction-design, design:design-critique, engineering:testing-strategy, security-review on the final diff. design-elevation and superdesign were not used.

## Step 0 audit (read only, before any change)

- **Run tab with no race.** With running off, it shows "Running is off." and a Turn on running button. With running on, it shows a big Log a run, a strip of this week's runs, an 8 week distance chart, the last five runs, and a "Race plan and full schedule" button that opens the race setup.
- **Run logging.** The Log a run sheet (`openRunLog`, `saveQuickRun`) takes distance, time, type, feel and a note. Runs are stored by date in `monk_run_logs_v1` as `{miles, secs, hr, feel, type, source}`. Strava sync writes to the same place.
- **Running setting.** `monk_running_v1` ('1' or '0'), set through `setRunning`. Settings has a Running On/Off row, and the welcome flow's cardio question sets it. The setup wizard asks "Do you run?" Yes/No, then mileage, then race (No/Yes and a date), then distance. It writes `runPlan.runner`, but it never turned the running switch on.
- **Today and runs.** A Run tile shows only when a race plan gives a run within 6 days (`nextPlannedRun`). With no race, Today showed nothing about running.
- **Race plan.** `generateRunPlan` needs a race date. With one, it builds calendar weeks back from race day with easy, long and tempo runs, mileage ramps, cutback weeks and a taper. Without one, it returns null, so there is no plan.

Nothing conflicted with the brief, so the build went ahead.

## What changed

- **Setup.** "Do you run?" now offers Yes, regularly / A little / Not now. Yes or A little asks "How many days a week?" (1 to 5, 3 chosen) on the same step. The race question is Skip (chosen) or "Yes, add a race date", and Yes runs the existing date and distance flow. Not now turns running off and says it stays one tap away on the Run tab, which still offers Turn on running. The wizard's steps are unchanged, so onb.js passes as before.
- **Run tab, no race ahead.** A top card shows "Runs this week, 2 of 3", the distance this week in mi or km, and an optional target progress line. Log a run stays the main button, and recent runs come from the logs. "Race plan and full schedule" becomes a quiet "Add a race for a plan" link that opens the race date field. There is no schedule, pace or generated plan.
- **Today.** A "Runs this week, 1 of 3" tile with a Log a run button. It shows only when running is on, no race is ahead and there is a goal. Saving a run updates Today and Run.
- **Settings, Running.** Below On/Off: runs a week (1 to 5), an optional weekly distance target in the run unit (stored in miles), the race date, and a button to add or change the race.
- **Existing users.** With a race ahead, nothing changes. With logged runs, no race and no answer, the goal is 3. With no runs, no race and no answer, the card shows "No runs yet. Log one and it shows here." and Log a run, with no goal and no Today tile.
- **Storage.** One key, `monk_run_base_v1`, holding `{on, perWeek, weeklyTarget}`. It is in backup and restore and is cleaned on restore. A backup without it loads as before. Runs and races are stored as before.

## Added mid build at your request: Today first

- On the day it is, Today shows that day's planned workout first, even when earlier days this week are open.
- A day counts as done for today only when its sets carry today's date. If today's workout was logged on an earlier date this week, Today says "Logged on Tuesday, November 17. It counts for that day, not today." and offers Open in Lift. It doesn't offer Start workout, because a second session would overwrite that week's sets.
- Strip marks: a check needs sets dated inside that week's dates, and today's check needs today's date. Logs from earlier dates no longer mark this week's days.
- **Plan weeks follow the calendar, for every user (your choice).**
  - A plan week starts on the Monday of its first logged set, and the weeks after it start 7 days apart.
  - On open, each calendar week that has passed moves the plan one week on. A missed day or a whole missed week never holds anyone back, and being away three weeks moves three weeks on.
  - Missed days stay missed. No set is moved or changed, and today's workout never writes over last week's sets (each lift keeps one entry per plan week).
  - It stays put when a set has been logged in the plan week since this Monday, or when the user finished a week early and the next week's Monday is still ahead.
  - It never moves past the last week (8.38's block card covers week 10), and a new user with no logs stays on week 1.
  - Nothing is hardcoded and no key is added. The anchor comes from the dates already on the logs.
  - This fixes the Nov 23 screenshot. It runs on open only, so an app left open across Sunday night moves on the next open.
- `findNextUnloggedDay`, the week ring and the advance to next week still count any log in the plan week. Only today's card and the strip marks read dates.
- The 8.39 brief said the strip and lift flow do not change. Your later message overrides that for these three rules. It is a separate commit, so it can move to another branch.

## Older checks updated for the new rules

- `t825_plan_week.py`: "after 16 days away, plan week unchanged" (the 8.25 rule) is now "the plan moves two weeks on".
- `t834_short_normal.py`, `t835b_a_daylog.py`, `t835b_b_short.py`, `t835b_cd_nav.py`: their clock is now Monday. They test Short on Upper A. Thursday's Today now correctly opens Upper B, and Short does not shorten Upper B.
- `todayDayId()` (Change workout and Quick Log target) now falls back to the same today first day that Today shows.

## Not changed, reported

- Short does not shorten Upper B on the Upper/Lower plan: 7 lifts either way. This is already true on master.
- The legacy Today card (free style) has no runs tile.
- A race date in the past counts as no race, so the base view comes back after race day.

## Tests

- `t839_run_base.py`: 77 checks at 390 and 320.
- `t839b_today_first.py`: 20 checks at 390 and 320.
- onb.js: 138 passed.
- Full suite: 28 browser files, 0 failures. food, onb and sets pass. compat.js has the 3 known failures ("N-day split: switchDay() activates a day that exists" for the 3, 4 and 5 day splits).
- Screenshots: `tests/browser/out/839-*`.
