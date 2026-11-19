# Cleanup report, build 8.30

Run on Nov 19, 2026. All six items are pushed and live. No check failed at push time, so nothing was reverted.

## Preflight

- The working tree was clean and pushed at 8.29, apart from `OVERNIGHT_REPORT.md`. The prompt asked for that file to be committed first.
- Committed it as "Add overnight report" (d5bc716) and pushed.
- Tagged that commit `pre-cleanup` and pushed the tag. To roll back the whole cleanup, use that tag.

## Summary

| Item | What | Commit | SW cache | Pushed | Browser checks |
|---|---|---|---|---|---|
| 1 | Repeated titles under the hero | 9a7954f | v101 | yes | 45 of 45 |
| 2 | Quick Log recent workouts, list survives a reload | 15ca54a | v102 | yes | 21 of 21 |
| 3 | Food: weigh in first, meal input above totals | 6aae938 | v103 | yes | 30 of 30 |
| 4 | Run note | 0f8f1a6 | v104 | yes | 14 of 14 |
| 5 | Chart date labels | 9e39d02 | v105 | yes | 32 of 32 |
| 6 | Logo menu More, outside tap fix | 8886839 | v106 | yes | 20 of 20 |

The build number is 8.30 throughout. Each commit bumped the service worker cache, so every push reaches installed apps.

Live check: runtheweights.vercel.app serves `monk-mode-v106` and "Version 8.30". The four new features are in the live page: run notes, the menu layer, the saved Quick Log list and the label picker.

Unit suites were run after every item:

| Suite | Baseline | Result |
|---|---|---|
| food | 495 pass | 496 pass, 0 fail |
| onb | 138 pass | 138 pass, 0 fail |
| sets | 272 pass | 272 pass, 0 fail |
| compat | 83 pass, 3 known failures | 83 pass, the same 3 failures |

Food gained one test (menu order). See item 6.

The earlier browser checks were also rerun after every item:
- 8.26: 26 of 26.
- 8.27: 47 of 47. Its two menu order checks now expect the 8.30 menu (item 6).
- 8.28: 64 of 64. One step tapped the Food heading that item 1 hides; it now taps the date line.
- 8.29: 117 pass. 12 checks compare everything below the hero against the previous build. They now differ because items 1 to 3 change exactly that. All hero fit checks, the Settings icon and tab bar checks, and Plan's first card above the fold still pass.

## 1. Repeated titles under the hero

Pushed, 9a7954f.

Changes:
- Today: the THURSDAY band is now a small line ("Thursday"), so the day stays.
- Plan: the PLAN eyebrow is gone.
- Progress: the PROGRESS band is gone. The three stat cards, the Lifts / Body / Week switch and everything below them are unchanged.
- Run: the RUN band is gone. The mi / km toggle sits under the hero, right aligned. Log a run is unchanged.
- Food: the "Food" label and LOG WHAT YOU EAT are gone.
- Quick Log: nothing repeated the hero, so nothing was removed.

Checks, at 360 and 390:
- No heading under any hero repeats the hero word.
- The gap from the hero to the first element is 24 px, 28 px on Progress (the cards' own margin).
- The mi / km buttons are 44 px, and the toggle still switches units.
- Week review and The Edge headlines match the pre-cleanup build.
- On a rest day the Today hero is hidden and the big day band still shows.
- No page errors.

Decisions:
- Every rule applies only while the hero shows. A screen whose hero is hidden (a rest day on Today) keeps its old heading.
- The 24 px gap is applied to all six hero screens, not only Run and Progress, as "fix it the same way".
- Kept, because they are cards or controls: Today's "Next workout Upper A" card, the Plan day band (UPPER A), Food's date control ("Today"), and Quick Log's HOW LONG DO YOU HAVE? (it doesn't repeat the hero).

### Legacy top strip audit (not removed)

- What it is: `#info-subnav`, a row of four buttons: Home, The Edge, Week review, Progression. The prompt calls the last one Progress, but it is the old Progression section, not the Progress tab.
- What it does: each button calls `goSec()`.
- Where it shows: on every screen of the `info` tab, so Home, The Edge, Week review and Progression. Nowhere else.
- What removing it would affect:
  - The old Home welcome screen and the old Progression section would have no way in. Since 8.30 the strip is their only entry point (see item 6).
  - The Edge and Week review would still open from the More page.
  - The `sb-*` button ids are also set by `goSec()`, which handles a missing button safely.

## 2. Quick Log recent workouts and a saved session list

Pushed, 15ca54a.

What changed:
- **Recent workouts** sits at the top of Quick Log, above HOW LONG DO YOU HAVE? and the Add exercise button.
  - It lists the last 5 sessions, plan or Quick Log. Each is a ruled row with the date and the lift names.
  - Long lists of names cut off after two lines.
  - Tapping a row loads those lifts into the session with last numbers filled in. Nothing is logged until a set is ticked.
  - The section is hidden when there are no logs.
- **The session list survives a reload.** It is saved in `monk_ql_session_v1` `{ v: 1, day, start, items }`, including numbers typed but not yet logged.
  - It is cleared when the day changes or Start a new session is tapped.
  - Values are range checked on load (unknown exercise, weight 0 to 2000, reps 1 to 200, at most 40 lifts and 30 sets each).
  - It is in backups as `quickLogSession` and comes back on restore only on the same day.

Checks at 360:
- 5 rows, newest first, above Add exercise.
- Rows are ruled and at least 44 px tall.
- Two Quick Log sessions on one day show as two rows.
- Row text contrast is 5.35:1 for the lifts and 15.9:1 for the date.
- Loading a row:
  - lifts load in order with last numbers filled
  - nothing is logged
  - focus moves to the first set
- From opening Quick Log, a recent lift reaches its first logged set in 2 taps, and it saves as a new Quick Log entry.
- Reload mid workout keeps the list, the ticked sets and typed numbers.
- The backup includes the list, and a same day restore brings it back.
- Start a new session clears it.
- Out of range values are dropped on load.
- The next day the list is cleared.
- Empty state is hidden.
- No page errors.

Decisions:
- **What counts as a session:**
  - Plan sets are one session per date.
  - Quick Log sets on one date split into separate sessions when more than two hours pass between sets. Entries only carry a timestamp, so this is the closest true rule.
- **Placement:** "At the top of Quick Log" was read as above the time choice, which keeps its own place and behaviour.

Missed, then fixed:
- Item 2 pushed with a 44 px gap above Recent workouts. Its label's top margin pushed the block down.
- The item 1 checks weren't rerun before that push. They caught it during item 4.
- The fix (one CSS line) went out with item 4 in 0f8f1a6.

## 3. Food

Pushed, 6aae938.

What changed:
- The weigh in is the first thing under the Food hero.
  - One field for today's weight, saved to the same `monk_bodyweight_v1` data that Today uses.
  - The last earlier weigh in shows small under it, for example "Last weigh in: 184 lb, Nov 17."
  - If today is already logged, the field shows it and it can be edited.
- The add a meal block now sits above the totals (Snap meal, Scan barcode, Choose photo, Or describe your meal, Estimate), with its review draft right under it.
- Order now: weigh in, day control, meal input, totals and goal, drinks, meals, repeat a meal, bodyweight.

Checks at 360 and 390:
- The weigh in comes first, 24 px under the hero.
- The field is 44 px tall.
- The meal input is above the totals.
- Every other block keeps its order.
- The last weigh in line is 14 px or smaller, with contrast of at least 4.5:1.
- Only one weigh in field is on the screen.
- A typed weight saves for today and shows on Today. It shows after a reload and can be edited.
- The Bodyweight block keeps its weekly average, chart and notes.
- Stepping to another day keeps the field on today.
- The fresh install Food tip sits under the weigh in and is under 15 words.
- No page errors.

Decisions:
- The weigh in input moved out of the Bodyweight block, which keeps everything else.
- The old input followed whichever day Food was showing. The new one is always today, as asked. Past days can no longer be typed into on Food, and weights already saved for past days are kept.
- The goal choice stays attached to the totals, under the meal input.
- The Food tip said "Your totals for the day show at the top", which is no longer true. It now reads "Weigh in here. Add meals below and your totals show under them." and sits under the weigh in.

## 4. Run note

Pushed, 0f8f1a6.

What changed:
- Log a run has a small ruled "Add a note" line under the easy / okay / hard choice.
- It is closed by default. When a note exists the line reads "Note".
- It opens to a plain text field, 500 characters at most, with a count shown in the last 50.
- The note saves 400 ms after typing stops, on blur, on Save and on Cancel.
- Storage is `monk_run_notes_v1` `{ v: 1, notes: { date: text } }`, kept apart from the run logs.
- Recent runs shows a "Note" line under that run, escaped as plain text.
- It is in backups as `runNotes` and range checked on restore and load: real dates only, strings only, cut to 500 characters, blank notes dropped.

Checks at 360:
- The row sits under the feel choice, closed, ruled, 44 px tall.
- Tapping it opens the field with focus.
- The note autosaves to the versioned key.
- Run history shows it as plain text; markup typed into the note is not rendered.
- The saved run itself is unchanged.
- Reopening shows it closed, labelled Note, with the text kept.
- 600 typed characters save as 500.
- It saves on blur, and it survives a reload.
- It is in the backup and restores into a fresh install.
- Bad stored values are dropped, including an impossible date.
- No page errors.

Decisions:
- The note autosaves even when the sheet is cancelled. It shows in history only on a date that has a run.

## 5. Chart date labels

Pushed, 9e39d02.

What changed:
- **The rule:** one label picker for every dated axis.
  - It measures each label and always keeps the first and last.
  - A middle label stays only with at least 8 screen px of clear space from every label already kept.
  - Labels never rotate and are clamped inside the chart.
- **Where it applies:**
  - Progress Lifts and Body (line charts)
  - Run weekly distance (bars)
  - The race plan's week labels, which keep their 520 px minimum width
- **Measuring:** label widths are measured with the page font plus 10 percent, in case the web font arrives late.

Checks at 320, 360 and 390:
- **Progress Lifts:**
  - With the known case (Sep 28, Oct 5, Nov 16, Nov 18) only Sep 28 and Nov 18 print, with clear space.
  - The pre-cleanup build printed Sep 28 at 53 to 85 px and Oct 5 at 72 to 98 px, overlapping.
  - With 12 dates: Sep 28, Oct 19, Nov 2, Nov 18.
- **Progress Body:** first and last kept.
- **Progress Week:** a day strip, not a chart; the day labels don't overlap.
- **Run weekly distance and the race plan:** no overlap.
- **Food bodyweight chart:** its two labels ("2 wk ago", "Today") don't overlap.
- On every chart: at least 7.5 px between labels (8 px required, with half a pixel for rounding), none past the edge, none rotated.
- **Unit checks on the picker:** one label stays centred, two are both kept, a dense set keeps first and last and thins the middle.
- No page errors.

Left alone:
- The Food bodyweight chart only ever has those two edge labels, so it didn't need the picker. It is checked anyway.
- The race plan's planned and logged mile values above each bar are values, not dates. They have their own lift rule and weren't changed.
- The Week view is a strip of days, not a chart.

## 6. Logo menu More

Pushed, 8886839.

What changed:
- **Menu:** Today, Plan, Quick Log, Food, Run (when running is on), Progress, More.
- **More page:** the existing More page now has two ruled rows, Week review and The Edge, each opening the same screen as before.
- **Tick:** the menu ticks More on the More page, on Week review and on The Edge.
- **Logo menu tip:** now reads "More lives here now: Week review and The Edge."
- **Outside tap fix:** while the menu is open, a clear layer covers the page under it.
  - A tap outside only closes the menu. After a touch the layer stays up to 700 ms to absorb the click the browser sends after it.
  - Escape and menu items work as before.

Checks at 360 with touch and 390 with a mouse:
- **Menu:**
  - The order is exact, with no Week review, The Edge or About rows.
  - Rows are at least 44 px tall.
  - A menu item still navigates.
- **Outside taps:**
  - Touching Start workout under the open menu only closes the menu; Start workout is not pressed.
  - Touching the Food tab with the menu open only closes it.
  - The next tap after that works normally.
  - A mouse click outside the menu only closes it.
- **More page:**
  - It has two ruled rows of at least 44 px.
  - Week review and The Edge each open the same screen, with the same content, as the old route.
  - The tick shows More on all three screens.
- **Routes and tip:**
  - Escape closes the menu and returns focus to the logo.
  - The old About route still lands on The Edge.
  - The new tip text shows for an existing user who hasn't dismissed it.
- No page errors.

Decisions:
- **Home row:** the More page had a third row, Home (the old welcome screen). It was removed so More has exactly the two rows asked for. Home is still reachable from the top strip on Week review and The Edge.
- **Links to the two screens:**
  - All of them (Settings, onboarding, the About redirect, the strip) still open the same screens.
  - Only the menu needed to change.
  - The "Explore" path in setup still lands on The Edge.
- **The logo menu tip** keeps its id, so anyone who already dismissed it won't see the new words.
- **Tests:** the food.js menu tests now expect More in place of Week review and The Edge, plus a menu order check. The More page test expects two rows. This is why food has 496 passing tests.

## Not touched

As instructed, these were left alone:
- The Edge content
- The hero words
- The Settings icon
- The bottom tab bar
- Today and Plan logic

## Notes for review

- **8.29 screenshots:** the 8.29 check script overwrote the committed `screenshots/829-*.png` while it ran. They were restored from git, and the final run saved its screenshots in the session scratchpad instead.
- **Test scripts:** the 8.30 check scripts (`v1.py` to `v6.py`, `v827c.py`, `v828c.py`, `v829c.py`) are in the session scratchpad `c830/` folder. They aren't in the repo.
