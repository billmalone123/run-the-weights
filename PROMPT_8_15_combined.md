> **DONE. Build 8.15 (SW v86).**
>
> **Open card.** The More toggle is gone. An open exercise shows, top to bottom: the target line, set rows, the rest chip, one action row (Add set and Remove last set on top; Swap, Warm up and Note below, each 44 px), the form cue with Watch how, and the PR or stall line only when one applies. Add set copies the weight above and shows its reps as the ghost value, so one tap on the check logs it. Remove last set asks "Remove set 3?" with Cancel only when that set has data. Advanced controls follow the existing Advanced rules. Stall copy is now "Same weight for 3 sessions. Try X lbs next time, then build back up."
>
> **How long do you have.** 20, 30, 45, 60 minutes or Full session, inline on Today and as a sheet from Short on time and from Going out (Make it a short session). The pick shows the exercises, sets and "About X min" before Start. Estimate: every working set is 40 seconds plus that exercise's own rest timer value, a drop set adds 40 seconds, and a rest range ("3 to 4 min") gives a range; a box only counts as met when the high end fits. Cut order: accessories that are not a muscle's first exercise, then extra sets down to 2, then other non-first exercises from the end, then first exercises (isolation first) from the end; quads and the hamstring and glute side rank as separate muscles. A trimmed or short day counts as the day's workout everywhere (Today progress, guided workout, the check on each card). Every displayed time now uses this formula, so full sessions read about 25 to 40 minutes instead of 65 to 90.
>
> **Short sessions.** Chest 2, back 2, shoulders 2, legs 2 (one quad, one hamstring or glute), biceps 1, triceps 1, only for muscles in that day, 2 to 3 sets. Drop sets: biceps and triceps on their one exercise, chest and back on the second exercise, machines, cables and dumbbells only, never anything with a barbell. On for people who answered Yes to "Have you lifted weights before?", or after 28 days of logging; otherwise the sheet says "Drop sets: added after your first month." A drop set is an extra row tagged Drop in the same card, stored in its own key.
>
> **Rest days.** Every non training day has a card: Easy walk 20 to 30 minutes, Stretch or mobility 10 minutes, Full rest (plus Easy run when running is on), rotated across the week. Mark done is optional. A day a session was moved off for Going out reads Recovery with full rest first. Today shows it on rest days, Plan shows it when a rest day in the week strip is tapped, and the week strip and first week preview name the suggestion.
>
> **Plan setup.** Onboarding and Change plan ask "How many days can you train?" with one row per option: a plain line read from the real template and an M T W T F S S strip. Onboarding now applies the template it describes (the onboarding default; before this, 6 days described PPL but set Arnold). New optional questions: lifting experience, and "How long do you usually have for a workout?" (30, 45, 60, 90), also in Settings as Usual workout length, with "You can change this any time in More." No weekday picker: the scheduler places days by a fixed template and only reorders one week at a time.
>
> **Measured at 390 by 844.** New 3, 4 and 6 day lifters and a 4 day runner: first card 254 px (Arnold 293), 34 to 36 buttons, 4 inputs, page 1,222 to 1,338 px, a set logged in 2 taps, zero console errors, DM Sans and Antonio only, 4 to 7 font sizes, no tap target under 44 px. All 12 time boxes on a chest day and a leg day fit. Tests: food 490, onb 138, sets 247, compat 83 with the 3 known failures.
>
> **Review fixes.** The code review found that the time box cap was also changing the saved set count, which could delete logged sets or overwrite a lifter's set count. Now the stored count is never touched by a cap: the card shows a separate count, a set already logged past the cap stays on screen, and Add set or Remove last set on a capped card changes this week only (`monk_session_sets_v1`). All four cases re-tested.
>
> **Security (A3).** The Anthropic key lives only in Vercel's environment and is read by api/meal.js on the server; the passcode is checked on the server in api/meal.js and api/barcode.js. Nothing secret ships to the browser. No change needed.

# Build 8.15: Open card actions, time boxed sessions, smart short workouts, rest day labels, clearer plan setup

Paste this into Claude Code in the RTW Developments folder. This is one build that replaces the separate 8.15 and 8.16 prompts.

## Sync first

1. `git checkout master && git pull origin master`
2. Confirm the build stamp reads 8.14. If it reads 8.13, the 8.14 commit (5578d93) was never pushed. Tell me and stop.
3. Run `git push origin master --dry-run`. If GitHub login fails, tell me right away and stop. Do not build on top of work that cannot go live.
4. Read the top of PROMPT_8_14_streamline.md for the house style.

## Context

This app is for anyone, including women and young people with busy lives who also go out. The tone is plain, short and never guilty.

8.14 made the Plan screen calm: one exercise opens at a time, closed cards are one line. That stays. Billy's feedback:

1. The More row hides Add set, Remove last set, Swap, Warm up and notes. They must be visible whenever an exercise is open. Opening an exercise is the only toggle.
2. The "Short on time" and "Going out?" sessions are only about 2 exercises total. Too thin to be useful.
3. Rest days (for example Thursday) show a blank screen. They should say what to do.
4. Sessions run 65 to 90 minutes. A person with an hour has no way to say so.
5. Plan setup must stay individual to each person, and the days per week choice must be clear about what each option means.

## Do not touch

- Light stays the default theme.
- The meal passcode behavior stays.
- The white wordmark box inside the logo pill stays.
- Never rename a `monk_*` storage key.
- Keep the 4 tabs (Today, Plan, Food, More), the accordion between exercises (one card open at a time, closed cards are one line with the fill in check, finishing the last set opens the next card), the single font setup, and the first week preview.

## Skills to use

First run `/plugin` and tell me which of these are installed. Invoke each installed one with the Skill tool. Do not just read about them. If one is missing, say so and do that check by hand.

- `design-skills:design-critique` on the open card, Today, the time picker and the rest day card, before and after.
- `design-skills:interaction-design` for the action row, the time picker, the drop set flow and the rest day card.
- `design-skills:ux-writing` for every label and message.
- `design-skills:journey-mapping` for the first week from onboarding to the first workout.
- `design-skills:accessibility-audit` for 44 px tap targets and contrast.
- `frontend-design:frontend-design` for hierarchy so the card feels calm, not crowded.
- `engineering:code-review` on your own diff before you commit.
- `engineering:testing-strategy` to decide the Playwright checks.
- `vercel:verification` and `vercel:deploy` after the push.
- The Security guidance plugin on your diff, if installed.

## Part A: Open card actions

### A1. Remove the More row

Delete the More toggle and its expand and collapse code on the exercise card. No second level of hiding inside an open card.

### A2. Show this on every open exercise card, top to bottom

1. Target line (as it is now).
2. Set rows with weight, reps and the check (as now).
3. Rest chip (as now).
4. One action row: **Add set**, **Remove last set**, **Swap**, **Warm up**, **Note**.
5. A small line for the form cue link, when the exercise has one.
6. The PR badge and stall note, only when they apply, one small line each.

Rules for the action row:

- Plain words, one line each. Secondary in weight so the set rows stay the main thing.
- All five fit in at most two rows at 390 px wide. Each tap target is 44 px or more.
- Remove last set: if the last set has weight or reps logged, ask once ("Remove set 3?") with a clear Cancel. If empty, remove with no prompt.
- Add set copies weight and reps from the set above so a lifter can tap the check right away.
- Warm up, Swap and Note reuse the existing features. Do not rebuild them. Only surface them.
- Keep the "Start with the empty bar, 45 lbs" line visible.
- Closed cards stay one line.

### A3. Security check (do once, report it)

The meal feature sits behind a passcode so strangers cannot run up the API bill. Find out where the API key lives.

1. Search index.html and every JS file for the key, the provider URL, and the passcode check.
2. Say plainly whether the key is in code the browser downloads, or only on a server.
3. If the key or the passcode is readable in the browser, tell me exactly where and how easy it is to extract. Do not change the passcode behavior. Only report, and suggest the smallest fix (for example a server side function that holds the key and checks the passcode) as a separate item for later.

## Part B: Time boxed and short sessions

### B1. "How long do you have?"

Add a time picker wherever a person starts a workout: on Today and inside Going out and Short on time.

- Choices: 20, 30, 45, 60 minutes, and Full session.
- Plain heading: "How long do you have?"
- After they pick, show the shortened workout and a time estimate ("About 38 min") before Start.
- Estimate from the plan's own rest timer values plus about 40 seconds per set. Show a range if rest times are mixed. Report the formula you used.
- Build the shortened session from the exercises already planned for today. Do not invent a new plan.
- Cut in this order until it fits: accessory exercises first, then extra sets down to 2 per exercise, then lowest priority exercises. Never cut a muscle group's first exercise before another group's second exercise.
- A shortened session counts as a completed workout day. No "partial" or "missed" wording anywhere.

### B2. Smart short session ("Going out" and "Short on time")

Replace the 2 exercise version with a recipe by muscle group, the minimum per muscle that still gives most of the benefit.

- Chest 2, Back 2, Shoulders 2, Legs 2 (one quad or hip dominant, one hamstring or glute), Biceps 1, Triceps 1.
- 2 to 3 sets per exercise.
- Only include the muscle groups that belong to today's planned workout. A leg day gets no chest.

Drop sets:

- Biceps and triceps (1 exercise each): the last set can be a drop set.
- Chest and back: the last set of the second exercise can be a drop set.
- One line in the app: "Drop set: when you are done, lower the weight by about a fifth and keep going."
- Only on machines, cables and dumbbells. Never on barbell squat, deadlift or bench. Barbell only exercises skip it.
- On for people who said they have lifted before. Off by default for new lifters, with the line "Added after your first month." Read the experience answer from onboarding.
- Log a drop set as extra rows inside the same card, tagged "Drop". It must not break the 2 tap logging flow.
- Wording stays honest: "Drop sets are a time saver." Never claim they are the only way to get a pump or growth.

Use the existing exercise data (muscle tags, equipment tags). If an exercise has no muscle tag, report it and do not guess.

### B3. Rest days are never blank

Every non training day shows a Rest day card that says what to do, based on their plan.

- Lifters: pick from "Easy walk, 20 to 30 minutes", "Stretch or mobility, 10 minutes", "Full rest. That counts too."
- If running is on: add "Easy run if you feel like it."
- Rotate suggestions across the week so rest days are not identical.
- One tap to mark done. Not required. No guilt or streak language.
- If the user marked Going out for a day, the card says "Recovery" with the gentlest option first.
- This also fills the week view and the first week preview so no day is blank anywhere.
- No medical advice. Say nothing about pain, injury or health conditions.

### B4. Make plan setup clear

In onboarding and in plan settings, the "How many days can you train?" step must show what each option means, using the real plan templates already in the code.

- Describe each option in one line (for example "3 days: full body each time", "4 days: upper body and lower body, twice each"). Read the real templates and describe exactly what exists. Do not invent plans.
- Show a small week strip (M T W T F S S) with the training days highlighted for each option.
- If onboarding already lets people pick weekdays, keep it. If it only picks a count and the scheduler already supports specific weekdays, add a weekday picker. If the scheduler does not support it, do NOT build it. Report that to me instead.
- Add one optional question: "How long do you usually have for a workout?" with 30, 45, 60, 90 minutes. Use the same time box logic from B1 to set the default session length. The first week preview must show these times.
- Add the line "You can change this any time in More."

## Verify before pushing

Use Playwright at 390x844 against a local server. Test a new 3 day lifter, a 4 day lifter, a 6 day lifter, and a person with running on. Report real numbers.

1. Zero console errors on every tab and in onboarding.
2. First card top under 300 px. With the first card open: visible buttons under 45, visible inputs under 16, page height under 1,600 px. Taps to log a set 2 or fewer.
3. In an open card, all five actions and the form cue are visible with no extra tap, and each works: Add set adds a row, Remove last set removes one (with the confirm when it has data), Swap opens the list, Warm up opens, Note opens.
4. Opening a second card closes the first, and the check still fills when every set is logged.
5. Time boxes: for 20, 30, 45 and 60 minutes, list the exercises, sets and estimate for one chest day and one leg day. Every estimate must be at or under the chosen time. List any that are not.
6. Short session recipe: 2 exercises each for chest, back, shoulders and legs, 1 each for biceps and triceps, only for the muscles in that day's workout.
7. Drop sets: only on allowed equipment and exercises, never on barbell lifts, default off for a new lifter.
8. Rest days: for each plan, list every day of the week. None blank in the week view, on Today, or in the first week preview.
9. Onboarding: screenshot the days per week step and confirm each option has a plain description and a week strip. Confirm the first week preview times follow the session length answer.
10. Tap targets under 44 px: list any (should be none). Fonts: DM Sans and Antonio only on every tab.
11. Existing tests: food, onb, sets, compat. Report pass counts. Compat has 3 known failures from before. Any new failure is a regression.
12. The security check report from A3.
13. Screenshots into `/tmp/shots/`: the open card on the 3 day and 6 day plans, Today with the time picker, a 30 minute session, a drop set row, and a rest day card.

If a number misses its target, say so and fix it. Do not claim a pass you did not measure.

## Last steps

1. Bump the build stamp to 8.15.
2. Bump the service worker cache by one.
3. Add a short summary of this change at the top of this file.
4. Commit with a plain message, then `git push origin master`.
5. If the push fails, stop and give me the exact error. Do not retry in loops.
6. After a successful push, check that the live site shows 8.15 and has no console errors. If it does not update within two minutes, say so.
7. Reply with: what changed, the measured numbers from Verify, anything you could not finish, and anything you skipped because the code did not support it.
8. End by listing every skill you invoked and one line on what it changed. List any named skill that was not installed.
