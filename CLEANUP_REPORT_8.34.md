# Cleanup report, build 8.34

Pushed and live at runtheweights.vercel.app: Version 8.34. Tag `pre-8.34` is on 2ff0525.

| Part | Commit | Service worker cache |
|---|---|---|
| Part 0: Food settings hidden, weight unit | 063ed62 | `monk-mode-v111` |
| Parts 1 and 2: Plan card, Today, Short and Normal fix | b67bb0e | `monk-mode-v112` |
| Part 3: finish card | 469bfac | `monk-mode-v113` |
| Security hardening and this report | this commit | `monk-mode-v114` |

## Part 0

- **Food settings:** while `FOOD_ENABLED` is false, the Food targets section in Settings and the calorie line on the setup finish screen are hidden. Stored values are kept.
- **Weight unit:** a new lb or kg setting, `monk_weight_unit_v1`, separate from mi and km on Run. The default is lb.
  - Weights stay stored in lb and convert only on display, so no logged number changes.
  - The setting is in backups as `weightUnit`. A restore accepts only lb or kg.
  - Body weight now follows this setting instead of mi and km.

## Part 1: Plan

The user chose `references/plan_e_states.png` over `plan_b.png`, so the card follows that image where it differs from the spec.

- **Header:** ultramarine with a 32 px bottom radius.
  - Small caps row: "Week n of N" and "Exercise i of n".
  - The day title has a persimmon period, with Normal and Short at its right.
  - One line under it: minutes, lifts and moves, for example "46 min · 8 lifts · push and pull".
- **Current lift:**
  - Name in Antonio 30 px, with "Last time W x R · target a to b reps" under it.
  - Done sets are rows with an ultramarine check. Tap one to change it, which shows Save set n and Delete set n with Undo.
  - The current set sits in a white frame with a 3 px ultramarine border and a persimmon set number. Weight and reps boxes show Antonio 56 px numbers. Tap a number for the numeric keypad, or use the 48 px minus and plus buttons.
  - Upcoming sets are rows with an empty circle.
- **LOG SET:** persimmon with ink text, 56 px high, at the user's request. It has a press scale and a 280 ms pop, both off under reduced motion. It saves through `autoSaveExercise` and starts the rest timer.
- **Links:** Rest, Warm up, Add set and Swap, then Notes and details, which opens the full old row.
- **Finished lifts** sit above the card as one row each, for example "2 of 2 sets · 65 x 5, 65 x 6". Tap a row to reopen that lift. The lifts still to do stay as 56 px rows.
- **Tab bar:** floats on ink with a persimmon pill for the current tab. Run is a tab again for people who run, at the user's request. Everyone else sees Today, Plan, Food and Progress.

## Part 2: Today

- **Top:** the wordmark, and an ink pill showing the weekly streak, hidden at 0.
  - A week counts when its planned sessions are done. Rest days and moved sessions don't break it.
  - The current week counts once it is complete, and never breaks the run while it is still going.
- **Greeting:** "Ready to lift, name." The name is optional, set in Settings as Your name, stored in `monk_user_name_v1` and in backups as `userName`. It is cleaned and limited to 24 characters. With no name it reads "Ready to lift."
- **Week card:** a progress ring and a day strip showing done, rest (R), today and upcoming.
- **Workout card:** ultramarine, day name in Antonio 56 px, a meta line, Normal and Short, and a persimmon START WORKOUT button.
- **Stat tiles:** last week volume and next run. A tile is hidden when there is no data, and no numbers are made up.

## Fix: short session could not go back to normal

- **Cause:** Quick Log skipped a short day once it had a logged set, so "Use the full plan instead" never appeared.
- **Fix:** Quick Log now keeps that day. A Normal and Short switch on the Plan header and the Today card works both ways at any time.
- Switching changes only the session's shape (`shortDays`, `timeBoxes` and `quickSessions` for that week and day). Logged sets are never read or written, and a set hidden by Short shows again on Normal.

## Part 3: finish card

- **Trigger:** Finish workout appears once every set is in.
- **Summary:**
  - day name
  - duration, from the first to the last set, hidden when not known
  - sets
  - volume
  - the change against last week's same day, with an arrow, shown only when last week has a log
- **Highlights:** up to 3, one per lift, ranked weight PR, then rep PR at a weight (body weight lifts count reps), then a run of 2 or more weeks of rising top weight.
  - With none, the card reads "Showed up. Session n of the block."
  - A lift with no earlier log never gets a PR, and quick logs count as history.
  - Weights compare in lb and display in the chosen unit.
  - Everything is worked out when the card opens, so edited or deleted sets are reflected.
- **Share image:** a 1080 x 1350 PNG drawn on canvas: ultramarine, cream type, the Antonio day name, the top highlight large, two stats and the wordmark.
  - It is drawn when the card opens, so Share can hand the file to the Web Share API inside the tap.
  - Without Web Share it downloads, and the card says "Image saved to your downloads."
- **Buttons:** Share (persimmon) and Done. Escape closes the card, Tab stays inside it, and focus returns to where it was.
- **New key:** `monk_session_times_v1` holds the first and last set time per date and day. It is in backups as `sessionTimes`. Restore keeps only valid keys, timestamps and orders, up to 120 entries.

## Tests

| Test | Checks |
|---|---|
| `t834_0_units.py`: weight unit migration and display | 29 / 29 |
| `t834_12_plan_today.py`: Plan card, Today, tab bar, 8 streak cases | 75 / 75 |
| `t834_short_normal.py`: Short and Normal with sets logged | 24 / 24 |
| `t834_3_finish.py`: PR and progression rules, finish flow, share image, kg | 42 / 42 |
| All other browser tests, t825 to t832 | all pass |
| food, onb, sets | 507, 138, 272, no failures |
| compat | 83 pass, 3 known failures |

All checks ran at 390 x 844. Older tests were updated where 8.34 changed the screen:
- t825 and t826 test the full rows with the card turned off.
- The Today and Plan hero checks in t829 and t830 are retired.
- The tab bar baselines were re-recorded.

## Where the build differs from the spec

1. **Plan card layout:** it follows `plan_e_states.png`, as the user chose. There is no 96 px weight and no set tiles. The numbers sit in boxes inside the set frame, and the sets are rows.
2. **Run tab:** Run is a tab again, at the user's request.
3. **LOG SET size:** 56 px rather than 64 px, matching the image, in persimmon as the user asked.
4. **Copy:** the image's line about missed days was reworded to "A day you did not get to moves forward, it does not disappear.", because an 8.25 rule bans "missed" on Today.
5. **Plan toolbar:** the week toolbar and the day strip still sit between the card and the remaining lifts. The image shows the lifts directly under the card. Not changed yet.

## Security review

I read the full `pre-8.34..HEAD` diff myself. The `security-review` skill reviews uncommitted changes and there were none at that point, so it was not run.

- Every user-controlled string in new markup goes through `paEsc` or `textContent`: the name, day and lift names, and highlight text. The name is cleaned on save and on restore.
- Restored session times and weight units are range checked.
- **Hardened:** the new card put day and lift ids inside quoted JS strings in `onclick`. They now go through `paJs`, which escapes for JS and then HTML. A test proves an id containing quotes stays a plain string.
- **Older code, not changed:** a restored backup does not check custom exercise ids, and older rows use those ids the same way. The risk is low, because a person would have to import a hostile backup file. It is worth a pattern check on restore in a later build.
- The share image is made on the device and goes only where the person shares it.

## Skills used

- `anthropic-skills:token-smart-work`
- `design:design-critique`, against the reference images
- `design:accessibility-review`
  - Contrast was computed for each new color pair, and every text pair passes.
  - The day strip now uses hidden text instead of aria-label on list items.
- `design:ux-copy`: changed "Reps go from 1 to 100." to "Enter a number from 1 to 100."
- `design-skills:interaction-design`
  - Typed numbers now update in place, so the LOG SET tap after the keypad closes always lands.
  - The tile pop was shortened to 280 ms.
- `engineering:testing-strategy`: the streak case table and the PR rule tests
- `security-review` was not run, for the reason given above. The review was done by hand.
