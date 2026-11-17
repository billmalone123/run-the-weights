> **NOT RUN YET.** Replace this line with the completion summary when done.

## Sync first

```
rm -f .git/index.lock .git/ORIG_HEAD.lock
git fetch origin
git reset --hard origin/master
```

Confirm `git log --oneline -3` shows build 8.05 or later before starting. This file runs in five phases. Finish each phase, run its checks, commit it on its own and push before starting the next.

## Context

Run the Weights started as one lifter's app and it still carries his numbers and his voice. It now needs to work for anyone who opens it: women as much as men, and busy young professionals who want strength and wellness to fit around a working week. The owner still uses it every day and his setup must not move. Every change in this file applies to new installs only, or is a neutral fix that changes nothing for him.

What a new user should feel: the app asks a few questions they can answer, builds a week that fits their days and minutes, and then stays out of the way. Strength first, simple, guided, nothing written for one gender.

Decisions already made (edit before running if any of these change):
1. Positioning: lead with "a plan that fits your week", not a wellness hub. No new trackers beyond the Today check-in in Phase 5.
2. Training focus options: Balanced, Lower body and glutes, Upper body, General fitness.
3. Today check-in: yes, sleep and energy, two taps.
4. Food goal: asked in setup (lose, maintain, gain), no numbers shown until the user enters them.
5. Mode: new installs start in Simple. Anyone with logged sessions or a finished onboarding keeps Advanced, which is the current default.

Audit first and skip anything already done. These exist and must be reused, not rebuilt: the 110 exercise library with `muscle`, `pattern`, `kind`, `equip`; `buildSession()` with session size, time budget and owned equipment; the guided workout; Today; the bottom tab bar; Simple and Advanced modes; per movement weights (`movementPrevEntry`, `variantSeed`); the weekly gain band. Note what you found at the top of the completion summary.

Voice rule for every string you write: short, direct sentences, no hype, no emoji, no dashes, gender neutral, second person. Coaching cues must give a real training reason, in the register of the existing `repWhy` lines.

## Task

### Phase 1: Remove the owner's personal defaults

Found in the audit before this file was written (line numbers drift, search by text):

1. `var FOOD_START_WEIGHT = 185, FOOD_DEFAULT_GOAL = 200;` Start weight becomes the first bodyweight entry on record. Goal weight becomes unset until the user enters one. `foodGoalWeight()` returns null when unset, and every caller handles null without showing a number.
2. Food tab hero `EVERY MEAL.<br>TO <span class="accent-word">200</span>.` Build it from the user's goal: "Every meal. To 170." when a goal exists, "Every meal counts." when it does not.
3. `buildFoodPost()` "Day N. 185 to 200." uses the real start and goal, and drops the line when either is missing.
4. `goalMode = 'bulk'` and `_onbFlowGoalMode = 'bulk'` defaults. A new user has no goal mode until setup sets one. The owner's stored mode is untouched.
5. Settings placeholders `e.g. 3300`, `e.g. 200`, Goal lbs `200`. Use neutral placeholders that are not anyone's targets.
6. Confirm the owner keeps everything: with his stored data (bodyweight history, food targets, goal mode) the Food tab, the post and Today read exactly as before.

### Phase 2: Copy for everyone

Rewrite every gendered or single-race line in the voice rule. Keep the brand idea, strong and fast, lifting and running together, without assuming a man or a race. Found in the audit:

1. About: "Most men pick a lane." and "Most me…" in the same block.
2. The Edge: "The men who dominate in every area of life…", "Build the kind of body that commands attention…", "stronger and move better than 99% of men your age".
3. `WEEK_ARC`: "This is where most guys quit. You don't quit."
4. Any copy that assumes a race date or a half marathon outside the Run tab, which is now optional.
5. Grep for `men`, `guys`, `his`, `bro`, `alpha`, `attention` after rewriting and confirm nothing gendered is left in rendered text.

Use the `design:ux-copy` plugin for the rewrite and keep each replacement the same length or shorter than what it replaces.

### Phase 3: Setup that fits a working week

Rebuild the new user flow around four questions a busy person can answer. One question per screen, a back button on each, progress shown, every answer editable later in Settings.

1. Which days can you train? Seven weekday toggles, Monday to Sunday. Two to six days.
2. How long do you have? 30, 45, 60 or 75 minutes. Maps onto `sessionBudget` and a matching `sessionSize`.
3. What is your focus? Balanced, Lower body and glutes, Upper body, General fitness (Phase 4 adds the templates).
4. Where do you train? Full gym, home with dumbbells, bodyweight only. Maps onto `equipOwned`.
5. Then the food goal: lose, maintain or gain, current weight, optional goal weight. No calorie numbers are suggested. Targets stay the user's own.

Placing training days on chosen weekdays: today a split's `week` array is fixed Monday to Sunday. Keep the split templates as they are and add a mapping layer: the template's training days, in order, land on the chosen weekdays and every other day is rest. `activeSplit().week` returns the mapped array, so the calendar, the week row, Today and `findNextUnloggedDay()` all follow without changes of their own. With no chosen weekdays stored (the owner), the template's own order is used, unchanged.

The 1RM step leaves the default path. A new user is never asked for a max. The workout screen already says "Pick a weight you can lift N times with good form" when there is no weight to suggest, and the first logged set seeds everything after it. The maxes screen stays in Settings for anyone who wants it.

### Phase 4: Training focus templates

Each focus is a real program, built from library exercises that already exist. Do not add exercises unless a slot has fewer than four options for the chosen equipment.

1. Lower body and glutes: two lower days led by a hip hinge or hip thrust (glute focus) and a squat pattern (quad focus), plus upper body on the other days so nothing is skipped. Hip thrust, Romanian deadlift, Bulgarian split squat, step ups, glute bridge, cable or band work for the glutes.
2. Balanced: the current upper and lower or full body templates, picked by day count.
3. Upper body: the current push, pull and arms emphasis.
4. General fitness: full body strength days with one short conditioning finisher from the library (carries, sled, ski erg, med ball) when the equipment exists, bodyweight otherwise.

Every template works at 2 to 6 days and with each equipment level by leaning on like for like swaps. Session size and budget from Phase 3 apply through `buildSession()`, so every pick still shows its reason line. The owner's split and session settings are untouched.

### Phase 5: Today check-in

1. Two taps above Start workout: Sleep (rough, okay, good) and Energy (low, okay, high). Stored per day, private to the device, in the backup.
2. Rough sleep or low energy offers "Short version": today's session at the next smaller session size and budget, for today only, with a reason line on each pick naming the check-in. Starting the normal session stays one tap.
3. Nothing here diagnoses or prescribes. One plain line of why, for example "Short night. The short version keeps the habit without the fatigue."
4. A user who skips the check-in sees no prompt and loses nothing.

## Verify before pushing

1. Owner path: load the app with stored sessions, bodyweight history, food targets, goal mode and maxes. Today, Workout, Food, the post text, the hero and Settings read exactly as before this file. Advanced stays on.
2. New user path: clear storage, complete setup choosing Tuesday, Thursday and Saturday, 45 minutes, Lower body and glutes, home with dumbbells, gain. Confirm Simple mode is on, the week row shows training on exactly those three days, sessions fit 45 minutes, every exercise uses equipment the user has, every pick has a reason line, the Food hero shows no number until a goal weight is entered, and the user was never asked for a max.
3. Repeat the new user path for each focus at 2 and 6 days and each equipment level. No slot is empty, no exercise needs equipment the user lacks.
4. Grep rendered text for gendered words and for 185 and 200 outside the owner's own stored data. None.
5. Check-in: rough sleep offers the short version, picking it shrinks today only, tomorrow is normal, skipping it changes nothing.
6. Backup from the owner path restores cleanly, and a backup from before this file restores without errors.
7. Accessibility: run `design:accessibility-review` on the setup screens and the check-in in Light and Black. Every control is at least 44px with a visible focus state.
8. No console errors, all script blocks parse, all suites pass at their current counts (`compat.js` keeps its three known stub failures).

## Last steps

For each phase, bump the build stamp and the service worker cache version, then commit with a clear message. Before every commit confirm `sw.js` is not empty (`wc -c sw.js` should be about 1550 bytes). A blank `sw.js` shipped once in this repo. Confirm `git log --oneline --graph -5` is a clean line, push, and confirm with `git log --oneline origin/master -3` that the push landed. Do this after every phase, not only at the end.

Leave a short summary at the top of this file when done: what the audit found already existed and was skipped, every personal default removed and what replaced it, each gendered line and its rewrite, how weekdays map onto split templates, what each focus template contains, how the check-in changes a session, the owner path check result, and anything that still needs a real phone check.
