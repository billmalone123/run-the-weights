> **DONE. Build 8.16 (SW v87). Four commits: Part A, Part B (with A's review fixes), Part C, then C's review fixes with the version bump.**
>
> **Part A, Quick Log.** Today's time chips, Short on time (Today and each day header) and Going out all open Quick Log with the time and the day carried over; the logo menu still reaches it. It shows today's plan trimmed to the time, then five fixed quick workouts (Upper body, Legs, Push, Pull, Full body) built only from the exercise data and the person's equipment. Legs get 2, 3, 4 and 5 exercises at 20, 30, 45 and 60 minutes (quad, hinge, glute, calves, single leg by name; the data has no inner or outer thigh exercises). A started quick workout keeps its exercise list, stands in for one unlogged day, skips lifts already logged that week, and counts as that day everywhere. Drop sets only on the last set of the last exercise, never on a barbell, never for a new lifter. The old one set log is behind "Log a workout I already did". Estimates add 45 seconds per exercise for setup (no warm up switch exists, so none is added): full chest day 32 to 34 min became 38 to 40, full leg day 31 to 33 became 36 to 38.
>
> **Part B, rest and Swap.** The rest chip opens 30s, 60s, 90s, 2 min, 3 min, a 15 second stepper, and This exercise or All exercises; "Tap to change" shows once. Settings has Rest between sets (Short 0.75x, Normal, Long 1.25x, rounded to 15 s); a card choice wins. Every estimate reads the same rest values. The live timer has minus 15, plus 15 and Skip, and sits above the tab bar. Swap exercise is a full width button on every open card, with "Machine busy? No equipment? Swap it." on the first card of a first workout, and a 44 px icon on closed cards. The sheet shows three like for like options for the person's equipment with a reason line, then Just today (this week only) or Keep it, with Undo; everything else is under See all options. Logged sets stay with the exercise they were done on.
>
> **Part C.** Progress is one screen: workouts this month, best lift gain and bodyweight change; a Lifts, Body, Week switch; one small SVG chart with a text summary; a five row table with See all. The full calendar and lift cards sit behind one link, and no runs show there. Height for an 8 week user: 24,830 px before, 1,012 px after. About is Billy's note and fits one screen; no contact link exists in the code, so none was added. Runners get a Run tab between Plan and Food (5 tabs at 76 by 52 px; non runners keep 4): today's planned run or Log a run, the week, weekly distance, the last five runs, mi or km. The quick log takes distance, time (27:30 or minutes and seconds) and type, shows pace live, and saves in 3 taps. More lost Run and Quick Log and has 6 rows: Progress, Settings, About, Week Overview (kept, it shows the 10 week arc the Plan strip does not), The Edge, Home.
>
> **Not done or not possible.** Inner and outer thigh slot (no data). Warm up time in estimates (no warm up switch). A third set at 45 and 60 minutes when the stored count is 2 (that would change saved sets). More has 6 rows, not 5, until Billy decides on The Edge and Home. Named plugin skills other than dataviz, code-review and security-review are not installed.

# Combined build: Quick Log and legs, easier rest time and Swap, Progress redesign, short About, and a Run tab

Paste this into Claude Code in the RTW Developments folder. This one file replaces these three prompts: PROMPT_quick_session_legs.md, PROMPT_8_16_rest_and_swap.md and PROMPT_progress_about_run.md.

## Sync first

1. `git checkout master && git pull origin master`
2. Run `git status`. If there are uncommitted changes, stop and tell me.
3. Note the current build stamp. At the end you will bump it by one.
4. Run `git push origin master --dry-run`. If GitHub login fails, tell me right away and stop. Do not build on work that cannot go live.
5. Read the top of the newest PROMPT_*.md for the house style.

## How to run this big build safely

This is three parts. Work in this order: Part A (Quick Log, legs, honest time estimates), Part B (rest time and Swap), Part C (Progress, About, Run tab).

1. Do all the audits listed in Parts A and C first, before building anything, and put the short tables in your report.
2. After each part: run the tests, then make a local commit with a plain message. Three commits total.
3. Bump the build stamp and service worker cache once, at the end.
4. If you run low on room or a part is blocked, stop after the last finished part, push what is done, and tell me exactly what is left. Do not push half finished work.
5. Use `/compact` between parts if the session gets long.

## Context

This app is for anyone, including women and young people with busy lives who also go out. The tone is plain, short and never guilty. A shortened session counts as a full day. No "missed", "partial", "behind" or streak shaming anywhere.

Billy's feedback, all in one list:

1. Quick Log is where people land when they are short on time. They say how long they have and get predetermined workouts for that time.
2. Leg day has too few exercises. Two is too little.
3. Rest time is hard to change. Make it easy.
4. Swap exercise is not obvious enough.
5. Progress needs a better design with a graph or table and far less scrolling.
6. About should only say what this plan is and how Billy built it.
7. Run gets its own tab, separate from the lifting side, and an easier log.

## Do not touch

- Light stays the default theme.
- The meal passcode behavior stays.
- The white wordmark box inside the logo pill stays.
- Never rename or remove an existing `monk_*` storage key. New keys must start with `monk_` and be included in backups. Values restored from a backup must be checked against allowed ranges before use. Existing logged data must keep working with no migration that could lose anything.
- Bottom tabs: non runners keep exactly 4 (Today, Plan, Food, More). Only when running is on, add one Run tab (Part C). Do not add or move any other tab.
- Keep the accordion between exercises (one card open at a time), the open card action row, rest day cards, the single font setup, the first week preview, and the hidden "Copy today's post" behind a long press on the version label.
- Keep the hidden Strava dev note hidden.

## Skills to use

Run `/plugin` yourself if you can, otherwise say you could not. Tell me which of these are installed. Invoke each installed one with the Skill tool. If one is missing, say so and do that check by hand.

- `token-smart-work` first: search before reading, never read index.html whole, quiet test output, short report.
- `dataviz` before writing any chart code (Part C).
- `design-skills:interaction-design` and `design-skills:design-critique` on every new or changed screen, before and after.
- `design-skills:ux-writing` for every label and for the About copy.
- `design-skills:journey-mapping` for the rushed day path (Part A) and a new runner's first run (Part C).
- `design-skills:accessibility-audit` for 44 px tap targets, contrast, and chart text alternatives.
- `frontend-design:frontend-design` for hierarchy.
- `engineering:code-review` and the Security guidance plugin on your diff, once per part.
- `engineering:testing-strategy` to decide the Playwright checks.
- `vercel:verification` and `vercel:deploy` after the push.

## Part A: Quick Log is the short on time home, legs get a real session, honest estimates

### A1. Audit first (report before building)

Before changing anything, list in a short table:

- What Quick Log does today, where it lives, how it is reached, and what storage it uses.
- Every place a person can say they are short on time today: the "How long do you have?" picker on Today, Short on time, Going out, and anything else. For each, where it leads.
- The current leg day recipe and the full list of leg exercises in the exercise data, with their muscle and equipment tags.

If Quick Log today is a different feature (for example logging a workout you already did), keep that working as a small link inside the new screen called "Log a workout I already did". Do not delete it.

### A2. Quick Log is the one place for short on time

Make Quick Log the single destination for every short on time path:

- The Today time picker, Short on time, and Going out all open Quick Log, with the time already chosen if they picked one.
- Quick Log is also reachable from More, as now.
- Remove duplicate screens and sheets that did the same job. Keep one flow. Do not delete data.

**The Quick Log screen:**

1. Heading: "How long do you have?" with chips for 20, 30, 45, 60 minutes. Remember the last choice.
2. Under it, the first card is **Today's plan, trimmed to your time**, labeled clearly. It shows the exercises, sets, and "About X min". One big Start button.
3. Below that, **Other quick workouts** for that time, as simple cards: Upper body, Legs, Push, Pull, Full body. Each card shows the name, "About X min", and a one line preview of the exercises. Tap to see the full list, then Start.
4. If a person is on a rest day, the first card says so kindly and offers the quick workouts as an extra. Never push.
5. A small link at the bottom: "Log a workout I already did" (the old Quick Log job, if it had one).

"Predetermined" means the workouts are fixed recipes, not random. Build them deterministically from the existing exercise data and the recipe in step 3. Same time and same equipment gives the same workout every time. Do not invent new exercises or tags. Filter by the equipment the person said they have. If a slot has no matching exercise, report it and fill it with the closest match from the same muscle, never leave a gap or duplicate an exercise.

Starting a quick workout opens the normal workout screen with the normal card behavior, so logging, rest controls and Swap all work. It counts as a completed day.

### A3. Better recipes, and legs get a real session

Keep the recipe for upper body muscles from before (chest 2, back 2, shoulders 2, biceps 1, triceps 1, 2 to 3 sets each) and add time scaling.

**Legs scale with time:**

| Time | Leg exercises |
|---|---|
| 20 min | 2: one quad or knee dominant, one hamstring or hip hinge |
| 30 min | 3: quad, hamstring or hinge, glute |
| 45 min | 4: quad, hinge, glute, calves |
| 60 min | 5: add one single leg or inner or outer thigh exercise |

- 2 to 3 sets per exercise.
- Choose by the movement and muscle tags in the data. Put the biggest compound first.
- No drop sets on barbell squat, deadlift or other barbell lifts. A drop set is allowed only on a machine, cable or dumbbell exercise, only on the last set of the last exercise, and only if drop sets are on for that person. Keep the existing 28 day rule for new lifters.
- Report any time slot where the data does not have enough exercises.

**Other days scale with time too:** at 20 minutes use the minimum recipe. At 45 and 60 minutes, upper days may add a third set or one extra accessory per muscle if it still fits the time. Do not go over the chosen time.

### A4. Honest time estimates

Billy's sessions run longer than the app's estimate. Fix the formula so the promise "About X min" holds:

- Keep each set at about 40 seconds plus that exercise's rest time.
- Add about 45 seconds per exercise for setting up and moving between stations.
- Add the warm up time if a warm up is on.
- Use this one formula everywhere: Quick Log, the time picker, the first week preview, the plan estimates. The app must never show two different estimates for the same workout.
- Report the estimate for one full chest day and one full leg day before and after the change.
- Every quick workout must come in at or under the time chosen, using the new formula.

## Part B: Easy rest time and an obvious Swap

### B1. Easy rest time

Today the rest chip is hard to change. Make adjusting it a one or two tap job in three places.

**On the open card.** The rest chip shows the current rest ("Rest 2:00"). Tapping it opens a small picker with:

- Quick choices: 30s, 60s, 90s, 2 min, 3 min.
- A minus and plus stepper in 15 second steps for anything in between.
- Two choices for where it applies: "This exercise" (default) and "All exercises".
- A plain close. No save button needed: changes apply right away.

Show a small hint on the chip the first time only ("Tap to change"), then never again.

**During the live rest timer.** While the countdown is running, show minus 15 and plus 15 buttons right on the timer. These only change the current countdown, not the saved rest time. Add a Skip button if one is not already there. All three must be 44 px tap targets.

**Defaults and setting.** Keep the app's existing default rest values per exercise type. Add one setting in More, under Settings, called "Rest between sets" with three choices: Short, Normal, Long. These scale all defaults (for example about 0.75x, 1x, 1.25x, rounded to 15 seconds). A per exercise or all exercise choice from the card overrides this.

Rules:

- Rest time changes must flow into the time estimates ("About X min") from the time picker, the short sessions, and the first week preview. One source of truth. The app must never show two different estimates.
- Store changes in new `monk_*` keys. Include them in backups. Check values restored from a backup against allowed ranges (15 seconds to 10 minutes) before using them.
- Do not change the saved sets or reps on any card.
- Plain words. No jargon.

### B2. Make Swap obvious

- On every open exercise card, make Swap a clearly visible button with an icon and the label "Swap exercise", not a small secondary chip. It should be the most noticeable button in the action row after the set check, without taking over from the set rows.
- Add one short helper line under it, shown only on the first open card of the first workout: "Machine busy? No equipment? Swap it."
- On closed cards, add a small swap icon at the far right that opens the same swap sheet without having to open the card first. It must be 44 px tall.

**The swap sheet.** Rebuild it so a person can pick in one tap:

- Title: "Swap this exercise".
- Show the top 3 like for like options first, as large tappable rows. Each row shows the exercise name, the equipment it needs, and one plain line on why it fits ("Same muscle, uses dumbbells").
- Choose options by the same muscle and similar movement, filtered by the equipment the user said they have. Use the existing exercise data and variants (`EXERCISES`, `EX_ALTS`, equipment tags, `exVariants()`, `activeVariant()`). Do not invent new exercises or new tags. If fewer than 3 match, show what matches.
- Under the top 3, a "See all options" row for the full existing list. Keep every existing swap behavior.
- After tapping an option, ask nothing complicated. Show two buttons: "Just today" and "Keep it". Just today is the default and swaps for this workout only. Keep it swaps from now on. A one line Undo appears for a few seconds after swapping.
- Swapping must keep any sets the user already logged for that exercise today, and tell them in one line if weights will be blank because the new exercise is different.
- Time estimates update after a swap.

## Part C: Progress redesign, short About, and a Run tab

### C1. Audit first (report before building)

Before changing anything, list in a short table:

- Everything Progress shows today, in order, with its height in px at 390x844, for an empty user and for a user with 8 weeks of logs.
- Where running lives today: every screen, row, field and storage key related to runs, and what hides it for non runners.
- Everything About shows today.

Keep this table short. It goes into your final report.

### C2. Progress redesign

Goal: a person sees how they are doing in one screen, with no hunting.

Layout, top to bottom:

1. **Summary strip** with three tiles: workouts this month, best lift gain (or "Log a lift to see this"), and bodyweight change (or a blank state). Pick tiles from data the app already stores. Do not invent metrics.
2. **A segmented control** with 3 views: Lifts, Body, Week. Runs do not appear in Progress. Runs have their own tab.
3. **One compact chart** for the selected view, with a small table under it.
4. Nothing else on the first screen. Everything else is behind "See all".

The views:

- **Lifts:** a picker for the exercise (only exercises that have logs, default the most recently logged). Line chart of the top set weight over time. Under it a table of the last 5 sessions: date, top set, total sets. A "See all" row expands the full history.
- **Body:** line chart of bodyweight with a 7 day average line. Table of the last 5 entries. "Add weight" button.
- **Week:** a 7 day strip. Each day shows one of: done, shortened (counts as done), rest, upcoming. No "missed" state. Under it, a plain line like "3 workouts this week."

Rules:

- Build charts as small inline SVG. No chart library, no new dependency, no network. Use the CSS tokens for colors and the existing fonts only.
- Every chart has a text alternative (a visually hidden summary like "Bench press top set rose from 135 to 165 lbs over 8 weeks") and the table acts as the accessible data view.
- Handle 0, 1, 2 and 50 data points cleanly. No NaN, no empty axes. One point shows a single dot with its value. Zero points shows a friendly empty state with one button that goes to where they log it.
- Axis labels: at most 4 on each axis. Text no smaller than the app's smallest existing size.
- First screen of Progress must show the summary strip and the chart without scrolling at 390x844. Total page height for a user with 8 weeks of data under 1,200 px with the table limited to 5 rows.
- Chart and table must update right after a new log.
- Keep font sizes within the existing 7 size cap.

### C3. About: short and only about the plan

Replace the About screen content with only this. Billy writes in short, direct sentences. No dashes.

> **About Run the Weights**
>
> I'm Billy. I built this plan myself.
>
> I've lifted and run for years, and I captained Division 1 cross country in college. I put this plan together from what I learned doing that, plus research with online tools.
>
> I tested it on myself first. It's built for real schedules. Short on time? Going out tonight? The plan bends. You don't fall behind.
>
> This is not medical advice. If something hurts, stop and check with a doctor.

Rules:

- If the app already has a way to reach Billy (an Instagram handle or contact link), add it as one line at the end. Find it in the code. Do not invent a handle or link. If none exists, leave the line out and tell me.
- About must fit on one screen at 390x844 with no scrolling.
- Everything else that About showed before is removed from About. Do not delete any feature. If something useful was there (the version number, Copy today's post, the privacy or storage note, the rules text), move it somewhere sensible, such as a small footer on the More screen, and list what you moved.

### C4. Run is its own tab

Run gets its own bottom tab, fully separate from the lifting screens. It only exists when running is on.

- Non runners keep the 4 tabs: Today, Plan, Food, More.
- Runners get 5: Today, Plan, Run, Food, More. Billy chose this on purpose. Keep labels short so all 5 fit at 390 px wide with 44 px tap targets.
- Turning running on or off in Settings updates the tab bar right away, with no reload.
- `goTab('run')` must work, and any old run entry point must land in the Run tab.
- Remove run content from the lifting side: the Plan screen and the Progress screen show lifting only. Remove the Run row from More, since the tab replaces it. Today may show one small card for a planned run, because Today is the home for the whole day.

**What the Run tab shows, top to bottom:**

1. If a run is planned for today, a card: "Run: Easy 3 mi" with a "Log it" button. If the app has no run plan, show a big "Log a run" button. Do not invent a run plan.
2. This week's runs as a small 7 day strip with a run marker on the days that have one.
3. A weekly distance chart (small inline SVG, text alternative included).
4. A table of the last 5 runs with date, distance, time, pace and type. "See all" expands the rest.
5. Units (mi or km) as a small toggle inside the tab.

**Quick run log** (one screen or sheet, at most 3 inputs):

1. Distance with a numeric keypad. Miles by default, with a small mi and km toggle that sticks.
2. Time as minutes and seconds (and hours if needed) with a numeric keypad. Accept "27:30" typed in, and also separate fields. No free text parsing surprises.
3. Type: Easy, Long, Fast, Intervals, as 4 large buttons. Default to the type planned for today, or the last type used.
4. Pace is calculated and shown live, not typed. Format like 8:52 per mi.
5. Optional: "How did it feel?" as three words or icons, collapsed so it does not slow people down.
6. One big Save button. After saving, return to the Run tab with a one line confirmation. Logging a run takes 3 taps or fewer when the type is prefilled.

Rules:

- Reuse the existing run storage and data. Existing runs must still show correctly.
- The "Easy run if you feel like it" option on rest day cards opens the quick run log.
- Do not touch the hidden Strava dev note. Keep it hidden.
- Handle bad input kindly: zero distance, zero time, or absurd values (over 100 mi or over 24 hours) get a plain message, never a crash or NaN.
- Running off means the tab, the Today card, the rest day option and every run field are gone everywhere.

### C5. Trim More (keep the 5 tab bar clean)

Billy wants the Run tab as a fifth tab for runners. The 4 other tabs stay. To keep the app light, trim the inside of More instead of removing a tab.

1. Audit every row in More today. List each row, what it opens, and whether another screen already does the same job.
2. Remove the entry point (not the feature, not the data) for rows that are now duplicated:
   - Run, because the Run tab replaces it.
   - Quick Log, because it is now reached from Today, Short on time and Going out. Keep the "Log a workout I already did" link inside the Quick Log screen.
   - Week Overview, if the Plan screen's week strip already shows the same thing. If it shows more, report what is extra and leave the row.
3. Keep Progress, Settings and About.
4. For The Edge, Home, and any other row you do not recognize as a core action, report what it is and give a one line keep, merge or cut recommendation. Do not remove these yet. I will decide.
5. Goal: More has 5 rows or fewer, each with a plain one line description, and fits one screen at 390x844 with no scrolling.
6. Nothing that is removed from More may become unreachable if it holds data a person needs. List where each removed entry point is now reached.

## Verify before pushing

Use Playwright at 390x844 against a local server. Seed localStorage with realistic data in the app's real formats, read from the code. Test a new 3 day lifter, a 4 day lifter, a 6 day lifter, a lifter with limited equipment (dumbbells only), a runner with 8 weeks of runs and lifts, and a user with no data. Report real numbers. Verify each part after it is built.

### Checks for every part

1. Zero console errors on every tab and in onboarding, for every seeded user.
2. Tab bar: exactly 4 tabs for a non runner and exactly 5 for a runner, all labels fit at 390 px.
3. Tap targets under 44 px: list any (should be none). Fonts: DM Sans and Antonio only. Font sizes per tab 7 or fewer.
4. Existing tests: food, onb, sets, compat. Report pass counts. Compat has 3 known failures from before. Any new failure is a regression.
5. Taps to log a set stays 2 or fewer. First exercise card top under 300 px.

### Part A checks
1. Zero console errors on every tab and in onboarding, for every seeded user.
2. The audit table from step 1.
3. Every short on time entry point opens Quick Log (Today picker, Short on time, Going out, More). Chosen time carries over.
4. Taps from opening the app on Today to the first logged set on a quick workout: report the count (target 4 or fewer).
5. For 20, 30, 45 and 60 minutes, list every quick workout (today's plan, Upper, Legs, Push, Pull, Full body) with exercises, sets and the estimate. Every estimate at or under the chosen time. List any that are not.
6. Legs have exactly 2, 3, 4 and 5 exercises at 20, 30, 45 and 60 minutes. No duplicates, no gaps. List the exercises chosen for each.
7. The same inputs give the same workout twice (deterministic). Dumbbell only user sees only dumbbell options.
8. Drop sets: none on barbell exercises, none for a new lifter, only on the last set of the last exercise when on.
9. Estimates: one formula everywhere. Show before and after for a full chest day and leg day.
10. Starting a quick workout: open card actions, rest controls and Swap all work, and the day counts as completed in the week view and in Progress.
11. The old Quick Log function (if any) still works from its link, and old data still shows.
12. Bottom bar tab count unchanged (4, or 5 with Run for runners). Tap targets under 44 px: list any (should be none). Fonts: DM Sans and Antonio only.
13. Existing tests: food, onb, sets, compat. Report pass counts. Compat has 3 known failures from before. Any new failure is a regression.
14. Screenshots into `/tmp/shots/`: Quick Log at 20 and 45 minutes, a Legs quick workout open, and Today with the entry point.


### Part B checks
1. Zero console errors on every tab and in onboarding.
2. Rest picker: opens from the chip in one tap. Each quick choice sets the rest correctly. Stepper moves in 15 second steps. "This exercise" changes only that exercise. "All exercises" changes every exercise. Values survive a page reload.
3. Live timer: plus 15 and minus 15 change the running countdown only, not the saved rest time. Skip works.
4. Setting: Short, Normal and Long change defaults as described and the time estimates update. List the estimate for one chest day under each.
5. Restore from a backup with an out of range rest value: confirm it is rejected or clamped, not used.
6. Swap: button visible on every open card with no extra tap. The icon on a closed card opens the sheet. The top 3 match the muscle and the user's equipment. Just today and Keep it behave differently. Undo works. Logged sets survive the swap. Time estimates update.
7. First card top under 300 px. Page height with the first card open under 1,700 px. Taps to log a set still 2 or fewer.
8. Tap targets under 44 px: list any (should be none). Fonts: DM Sans and Antonio only.
9. Existing tests: food, onb, sets, compat. Report pass counts. Compat has 3 known failures from before. Any new failure is a regression.
10. Screenshots into `/tmp/shots/`: the open card with the rest picker open, the live timer with the plus and minus controls, the open card showing the Swap button, and the swap sheet.


### Part C checks
1. Zero console errors on every tab and in onboarding, for every seeded user.
2. The audit table from step 1, with before and after heights for Progress.
3. Progress first screen shows the summary strip and a chart with no scrolling. Page height for the 8 week user under 1,200 px. Report the actual number.
4. Charts render correctly for 0, 1, 2 and 50 points. No NaN anywhere. Text alternatives are present.
5. Each Progress view updates right after a new log.
6. About fits one screen with no scroll. List everything moved out of About and where it went.
7. Run flow: count taps to log a run with a prefilled type. Check pace math for these cases: 3.1 mi in 27:30 is about 8:52 per mi, 5 km in 25:00 is 5:00 per km, 6.2 mi in 55:00 is about 8:52 per mi. Check the mi and km toggle, bad input messages, and that old runs still display.
8. Run tab: exists only when running is on, between Plan and Food. Turning running on or off updates the bar with no reload. Plan and Progress show no run content. The rest day easy run option opens the log. Today shows the planned run card only when one exists.
9. Tab bar: exactly 4 tabs for a non runner and exactly 5 for a runner. All 5 labels fit at 390 px with tap targets of 44 px or more.
10. Tap targets under 44 px: list any (should be none). Fonts: DM Sans and Antonio only. Font sizes per tab 7 or fewer.
11. Backup and restore: new keys are in the backup, and a restored value that is out of range is rejected or clamped.
12. Existing tests: food, onb, sets, compat. Report pass counts. Compat has 3 known failures from before. Any new failure is a regression.
13. Screenshots into `/tmp/shots/`: Progress (each view), About, the Run tab, the quick run log, and Today with a run card.



### More checks

1. More lists 5 rows or fewer and fits one screen with no scrolling. Report the final list.
2. Every removed entry point is still reachable from the place the report names.
3. Report your keep, merge or cut recommendation for The Edge, Home and any other unfamiliar row.

If a number misses its target, say so and fix it. Do not claim a pass you did not measure.

## Last steps

1. Bump the build stamp by one and bump the service worker cache by one.
2. Add a short summary of this change at the top of this file.
3. Commit any remaining changes, then `git push origin master`.
4. If the push fails, stop and give me the exact error. Do not retry in loops.
5. After a successful push, check that the live site shows the new build and has no console errors. If it does not update within two minutes, say so.
6. Reply with: what changed per part, the measured numbers from Verify, anything you could not finish, and anything you skipped because the code did not support it.
7. End by listing every skill you invoked and one line on what it changed. List any named skill that was not installed.
