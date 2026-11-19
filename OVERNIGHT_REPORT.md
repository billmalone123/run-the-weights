# Overnight report (8.26 to 8.29)

## Summary
| Build | Result | Commit | SW cache | Checks |
|---|---|---|---|---|
| 8.26 Per lift notes | Pushed, live | 60997cb | monk-mode-v97 | 26 of 26 |
| 8.27 Quick Log, menu, The Edge, rest timer | Pushed, live | a7fbc2a | monk-mode-v98 | 47 of 47 |
| 8.28 One time tips | Pushed, live | a70c1eb | monk-mode-v99 | 64 of 64 |
| 8.29 Hero top section | Pushed, live | bc5b6d1 | monk-mode-v100 | 129 of 129 |

No build failed a check at commit time, so nothing was reverted. Problems found while building were fixed before commit and are listed under each build. Every build also reran the earlier suites and the unit tests (food, onb, sets at 0 failures; compat at its 3 known failures).
Rollback point: tag pre-overnight on a24b0cf (8.25).
This report is not committed.

## Step 0. Preflight
- Build at start: 8.25, SW cache monk-mode-v96. Working tree clean, HEAD a24b0cf equals origin/master. PASS.
- Tag pre-overnight created on a24b0cf and pushed.
- Backups, same as the existing process: a copy of index.html, sw.js and food.js before each build in the session scratchpad, git history plus the pre-overnight tag, and in app data backups taken before any first save under a new storage rule.

## Build 1. 8.26 Per lift notes: PUSHED, commit 60997cb, SW monk-mode-v97, live confirmed

Checks at 360 wide (26 of 26 passed):
- PASS: Note button is a 44 px target
- PASS: tapping Note shows a multiline note field
- PASS: autosaves on blur, keyed by exercise and date
- PASS: autosaves on close without blur
- PASS: closed card shows the ruled Note marker
- PASS: cards without a note show no marker
- PASS: reopen: note still there
- PASS: note survives reload
- PASS: note capped at 500
- PASS: note survives logging, removing a set and clearing the day
- PASS: after Swap, note stays attached to the exercise
- PASS: note shows in the lift history, escaped
- PASS: next week the same lift shows Last time with its date
- PASS: next week the field starts empty
- PASS: Last time is one line
- PASS: Quick Log lift has the Note row
- PASS: Quick Log note saved by exercise and date
- PASS: Quick Log entry still a new Quick Log entry
- PASS: custom exercises get notes the same way
- PASS: workout level note unchanged
- PASS: backup includes liftNotes
- PASS: wiped notes gone
- PASS: restore brings lift notes back
- PASS: restored notes survive reload
- PASS: older backup without notes restores and keeps notes
- PASS: no page errors
- PASS: unit tests food 496/0, onb 138/0, sets 272/0, compat 83/3 (the 3 known split failures)
- PASS: workout note check (first card unchanged 508/764, save, reload, calendar, restore, clear)
- PASS: upgrade from the 8.21 export loses no keys; restore keeps 174 entries

Decisions made without asking:
- The card already had a "Note" button that opened a detail panel (rep reasons, targets) with no user text. The note field now sits at the top of that panel, so tapping Note opens it. The detail stays under it.
- New key monk_lift_notes_v1, shape { exerciseId: { date: text } }. Keyed by the exercise id, so a swap keeps the note on the same card. Mirrored to IndexedDB, in backup and restore, range checked (500 chars, date keys only).
- The marker on a closed card shows when today's note exists.
- "Last time" shows the latest earlier note for that exercise with its date, cut to one line with an ellipsis.
- Quick Log keeps its existing short "Notes" field on each set entry and adds the same lift Note row below it.
- Notes are not removed when an entry is deleted in Progress.
- Lift history (Progress, Lifts) lists notes under the table, newest first, five shown until See all.

Left alone: the existing Quick Log per set notes field, the workout note, every other card panel.

## Build 2. 8.27 Quick Log, menu, The Edge: PUSHED, commit a7fbc2a, SW monk-mode-v98, live confirmed

Audit, Part A (two lines):
- Quick Log picked a lift from four fixed main lift buttons (bench, squat, deadlift, OHP) into a one set form; each save is one Quick Log entry { d, ts, week, weight, reps, quickLog: true }, always appended. Since 8.25, Log as I go also had search and recents into that form.
- The library is the EXERCISES array in index.html (indexed by EX_BY_ID); custom exercises live in monk_custom_ex_v1 grouped by plan day, with an "any" group and a muscle field since 8.25. No change to how Quick Log entries are recorded was needed, so Part A was built.

Checks at 360 wide (47 of 47 passed):
- PASS: short on time path and time choices unchanged
- PASS: Add exercise opens a sheet with recents first
- PASS: last numbers prefilled for the recent lift
- PASS: recent lift reaches its first logged set in 3 taps
- PASS: search covers the library, rows are ruled
- PASS: searched exercise added second, in order
- PASS: no exact match: first row offers to add the typed text
- PASS: asks one tap for the primary muscle
- PASS: new exercise saved as custom, any day group, muscle core
- PASS: focus goes to the first empty field
- PASS: exact match shows no add row
- PASS: new exercise shows up in search
- PASS: new exercise shows up in an own plan search and adds
- PASS: session kept across tab switches
- PASS: Add set adds a row with the last values
- PASS: sets logged in all three exercises
- PASS: each set is a new Quick Log entry
- PASS: new session starts empty
- PASS: two Quick Log sessions on one day stay separate entries
- PASS: remove from session keeps logged sets
- PASS: old 4 lift limit removed
- PASS: Choose a lift opens the sheet and fills the form
- PASS: Choose a different lift opens the same sheet
- PASS: sheet and session tap targets at least 44 px
- PASS: menu order: Quick Log under Plan, no About row
- PASS: with running on every other item keeps its order
- PASS: old About link lands on The Edge: goTab('info');goSec('about')
- PASS: old About link lands on The Edge: goTab('about')
- PASS: old About link lands on The Edge: onbFlowExploreAbout()
- PASS: every About and Edge line kept, About first
- PASS: subnav has no separate About
- PASS: first run intro shows once only, with the About facts
- PASS: rest timer running
- PASS: rest timer on: every button tappable in settingsModal
- PASS: rest timer on: every button tappable in changePlanModal
- PASS: rest timer on: every button tappable in maxesModal
- PASS: rest timer on: every button tappable in goingOutSheet
- PASS: rest timer on: every button tappable in swapSheet
- PASS: rest timer on: every button tappable in exSheet
- PASS: rest timer on: every button tappable in ownPlanModal
- PASS: rest timer on: every button tappable in aboutIntro
- PASS: rest timer on: every button tappable in runSetupModal
- PASS: rest timer on: every button tappable in runLogSheet
- PASS: rest timer on: every button tappable in onbWizard
- PASS: wiped custom exercises
- PASS: restore keeps the new custom exercises
- PASS: no page errors
- PASS: 8.26 suite 26 of 26, 8.25 suite 54 of 54, workout note check, upgrade and restore check
- PASS: unit tests food 495/0, onb 138/0, sets 272/0, compat 83/3 (known)

Decisions made without asking:
- The session list (which exercises are in the current Quick Log session) is kept in memory, not stored, so no new key was needed. Every logged set is stored at once as its own Quick Log entry. A reload starts an empty list; logged sets are all kept. "Start a new session" begins a fresh list.
- Adding an exercise that is already in the session scrolls to it instead of adding a duplicate block.
- Removing an exercise from the session (plain confirm) does not delete sets already logged; it only takes it off the list.
- Weight 0 is accepted for bodyweight lifts; reps must be 1 or more.
- Each session exercise also gets the 8.26 lift Note row.
- In Log as I go, search and recents on the freestyle home now add to the same session list instead of the one set form.
- The old one set form stays (RPE and per set note); its four lift buttons became one "Choose a lift" button, and "Choose a different lift" opens the same sheet.
- The empty Week review/More tab list (no longer reachable since 8.25) dropped its About row; Week review, The Edge and Home remain.
- About text moved word for word to the top of The Edge, inside the same element id "about", so the one time intro still copies it. Nothing was found to be a true duplicate between About and The Edge, so nothing was removed. The info subnav lost its separate About button. goSec('about') and goTab('about') redirect to The Edge. The onboarding teaser now reads "Explore what's possible → The Edge". The intro dialog label reads "The Edge". The existing monk_about_seen_v1 flag still decides the once only intro, so anyone who saw About does not see it again.
- Rest timer fix: every modal and sheet overlay sits above the timer bar (z-index 340 over 300). The timer keeps running underneath and shows again when the modal closes.
- Tests updated because the spec changed them: food.js About teaser text, About landing, logo menu (no About), More rows; my 8.25 suite's freestyle prefill and menu checks.

Left alone: the short on time path and time choices, the rest timer's own modal (restModal), Week review.

## Build 3. 8.28 One time tips: PUSHED, commit a70c1eb, SW monk-mode-v99, live confirmed

Checks at 360 wide (64 of 64 passed):
- PASS: no tip while onboarding is on screen
- PASS: fresh install starts with no tips seen
- PASS: fresh install shows every tip once
- PASS: tips appear in place, Today first
- PASS: never again after Got it, also after reload
- PASS: tip today: under 15 words, no dashes, no exclamation
- PASS: tip today covers no tap target and Got it is tappable
- PASS: tip today: Got it at least 44 px, text contrast 4.5:1
- PASS: tip today: one on screen
- PASS: tip plan: under 15 words, no dashes, no exclamation
- PASS: tip plan covers no tap target and Got it is tappable
- PASS: tip plan: Got it at least 44 px, text contrast 4.5:1
- PASS: tip plan: one on screen
- PASS: tip quicklog: under 15 words, no dashes, no exclamation
- PASS: tip quicklog covers no tap target and Got it is tappable
- PASS: tip quicklog: Got it at least 44 px, text contrast 4.5:1
- PASS: tip quicklog: one on screen
- PASS: tip progress: under 15 words, no dashes, no exclamation
- PASS: tip progress covers no tap target and Got it is tappable
- PASS: tip progress: Got it at least 44 px, text contrast 4.5:1
- PASS: tip progress: one on screen
- PASS: tip food: under 15 words, no dashes, no exclamation
- PASS: tip food covers no tap target and Got it is tappable
- PASS: tip food: Got it at least 44 px, text contrast 4.5:1
- PASS: tip food: one on screen
- PASS: tip run: under 15 words, no dashes, no exclamation
- PASS: tip run covers no tap target and Got it is tappable
- PASS: tip run: Got it at least 44 px, text contrast 4.5:1
- PASS: tip run: one on screen
- PASS: tip style: under 15 words, no dashes, no exclamation
- PASS: tip style covers no tap target and Got it is tappable
- PASS: tip style: Got it at least 44 px, text contrast 4.5:1
- PASS: tip style: one on screen
- PASS: tip menu: under 15 words, no dashes, no exclamation
- PASS: tip menu covers no tap target and Got it is tappable
- PASS: tip menu: Got it at least 44 px, text contrast 4.5:1
- PASS: tip menu: one on screen
- PASS: tip lnote: under 15 words, no dashes, no exclamation
- PASS: tip lnote covers no tap target and Got it is tappable
- PASS: tip lnote: Got it at least 44 px, text contrast 4.5:1
- PASS: tip lnote: one on screen
- PASS: tip wnote: under 15 words, no dashes, no exclamation
- PASS: tip wnote covers no tap target and Got it is tappable
- PASS: tip wnote: Got it at least 44 px, text contrast 4.5:1
- PASS: tip wnote: one on screen
- PASS: tapping anywhere else dismisses and marks seen
- PASS: switching tabs fast never stacks two tips
- PASS: Settings has Show tips again, 44 px, and it resets them
- PASS: reset confirms in plain words
- PASS: backup includes seen tips
- PASS: restore keeps seen tips
- PASS: restored seen tips survive reload
- PASS: older backup restored: only new feature tips remain
- PASS: no page errors (fresh)
- PASS: existing user starts with old tips marked seen
- PASS: existing user sees only the new feature tips, each once
- PASS: existing user tip menu covers no tap target
- PASS: existing user tip lnote covers no tap target
- PASS: existing user tip quicklog covers no tap target
- PASS: existing user tip progress covers no tap target
- PASS: existing user tip style covers no tap target
- PASS: existing user tip wnote covers no tap target
- PASS: no page errors (existing user)
- PASS: reduced motion: tip has no animation
- PASS: 8.27 suite 47 of 47, 8.26 suite 26 of 26, 8.25 suite 54 of 54, upgrade and restore check
- PASS: workout note check with tips already seen (first card 508/764 unchanged). With a tip showing on Plan the card moves down by the tip's height, which is how the tips are meant to work.
- PASS: unit tests food 495/0, onb 138/0, sets 272/0, compat 83/3 (known)
- Two problems found and fixed during the build, before commit: the lift note tip could sit below the screen under a tall open card, and the scroll check never ran during a long scroll.

Tips as shipped, each checked against the screen:
- Today: "Start here. This screen shows what is next today." (Draft said it opens your next workout; on a rest day it does not, so rewritten.)
- Plan: "Log each set here. Tap a lift to see Swap and Add set." (Note moved to its own tip.)
- Lift notes: "Tap a lift, then Note. Your last note for it shows there."
- Workout notes: "Write how it felt. It saves by date in the full calendar." (Draft said you will see it next time; the app shows past workout notes in the calendar, not on the next session, so rewritten.)
- Quick Log: "Pick any lift or type your own. Log as you go." (true as drafted, anchored on Add exercise)
- Progress: "Your lifts by date. Pick an exercise to see its history." (Draft promised weight going up; rewritten to say what the screen does.)
- Run: "Your running plan lives here. Log each run when you finish it." (Draft said it is separate from lifting; Today also shows runs, so rewritten.)
- Food: "Log meals here. Your totals for the day show at the top."
- Logo menu: "Tap the logo for every screen, plus Week review and The Edge."
- Training style: "Follow a plan or train your own way. Switch under Set your maxes."

Decisions made without asking:
- Tips sit in the page flow next to what they explain (with a small pointer), so they push content down and can never cover a button. No overlay, no dimming, a 160 ms fade that is off under reduced motion.
- At most one tip per screen visit. The next one waits for the next visit, so it never runs like a tour. A tip only appears when its spot is on screen; tips lower on a page appear when you scroll to them.
- Tapping anywhere else, Escape, or Got it all mark the tip seen. Leaving a screen by code (not a tap) hides it without marking it.
- No tips while onboarding, the logo menu, or any modal other than Settings is open.
- Settings has no training style control. The choice lives under Settings, Set your maxes, Change Training Plan. The style tip sits under Set your maxes in Settings and says where to find it.
- New key monk_tips_seen_v1 { v: 1, seen: { id: 1 } }. On first run of 8.28 a person with any logs, food, or the About seen flag counts as existing and gets only the six new feature tips. Kept in backups. Restoring a backup from before 8.28 adds the four old tips to seen and keeps whatever was already seen, so only new feature tips can show.
- "Show tips again" sits in Settings under Backup and Restore, with a plain confirmation line.

Left alone: the one time About (now The Edge) intro, onboarding, every screen's content.

## Build 4. 8.29 Hero top section: PUSHED, commit bc5b6d1, SW monk-mode-v100, live confirmed (font file served live: 200, font/woff2, 11056 bytes)

references/today-direction-d.png was missing (there is no references folder in the repo), so the build follows the written spec only.

Words and lines at 360 wide with the test data (Thursday, week 7):
- Today: UPPER A, "Week 7 of 10. 8 lifts. About 42 to 46 minutes." (98 px)
- Plan: PLAN, "Week 7 of 10. Session 1 of 4." (34 px at 360x700, so the first card shows above the tab bar; 96 px max on taller screens)
- Quick Log: QUICK LOG, "Log anything. Last numbers fill in." (79 px, one line)
- Progress: PROGRESS, "Your lifts by date." (80 px)
- Run: RUN, line from the real plan, for example "Easy 3 mi today." (168 px)
- Food: FOOD, "Today." (149 px)

Checks at 360 and 390 wide (129 of 129 passed):
- PASS: 360 today: UPPER A, no clipping, inside 24 px gutters
- PASS: 360 today: size within max 168 and min
- PASS: 360 today: fills the width (largest size that fits) unless at max
- PASS: 360 today: one line
- PASS: 360 today: hero font is the bundled Antonio 700, line in body font
- PASS: 360 today: square 18% of size, persimmon, word in ink
- PASS: 360 today: 16 px under the header, not sticky
- PASS: 360 today: everything below the hero unchanged against 8.28
- PASS: 360 today: header, Settings icon and tab bar unchanged against 8.28
- PASS: 360 training: PLAN, no clipping, inside 24 px gutters
- PASS: 360 training: size within max 96
- PASS: 360 training: fills the width (largest size that fits) unless at max
- PASS: 360 training: one line
- PASS: 360 training: hero font is the bundled Antonio 700, line in body font
- PASS: 360 training: square 18% of size, persimmon, word in ink
- PASS: 360 training: 16 px under the header, not sticky
- PASS: 360 training: everything below the hero unchanged against 8.28
- PASS: 360 training: header, Settings icon and tab bar unchanged against 8.28
- PASS: 360x700 Plan: first exercise card starts above the fold (44 px of it shows above the tab bar)
- PASS: 360 quicklog: QUICK LOG, no clipping, inside 24 px gutters
- PASS: 360 quicklog: size within max 168
- PASS: 360 quicklog: fills the width (largest size that fits) unless at max
- PASS: 360 quicklog: one line
- PASS: 360 quicklog: hero font is the bundled Antonio 700, line in body font
- PASS: 360 quicklog: square 18% of size, persimmon, word in ink
- PASS: 360 quicklog: 16 px under the header, not sticky
- PASS: 360 quicklog: everything below the hero unchanged against 8.28
- PASS: 360 quicklog: header, Settings icon and tab bar unchanged against 8.28
- PASS: 360 calendar: PROGRESS, no clipping, inside 24 px gutters
- PASS: 360 calendar: size within max 96 and min
- PASS: 360 calendar: fills the width (largest size that fits) unless at max
- PASS: 360 calendar: one line
- PASS: 360 calendar: hero font is the bundled Antonio 700, line in body font
- PASS: 360 calendar: square 18% of size, persimmon, word in ink
- PASS: 360 calendar: 16 px under the header, not sticky
- PASS: 360 calendar: everything below the hero unchanged against 8.28
- PASS: 360 calendar: header, Settings icon and tab bar unchanged against 8.28
- PASS: 360 running: RUN, no clipping, inside 24 px gutters
- PASS: 360 running: size within max 168 and min
- PASS: 360 running: fills the width (largest size that fits) unless at max
- PASS: 360 running: one line
- PASS: 360 running: hero font is the bundled Antonio 700, line in body font
- PASS: 360 running: square 18% of size, persimmon, word in ink
- PASS: 360 running: 16 px under the header, not sticky
- PASS: 360 running: everything below the hero unchanged against 8.28
- PASS: 360 running: header, Settings icon and tab bar unchanged against 8.28
- PASS: 360 food: FOOD, no clipping, inside 24 px gutters
- PASS: 360 food: size within max 168 and min
- PASS: 360 food: fills the width (largest size that fits) unless at max
- PASS: 360 food: one line
- PASS: 360 food: hero font is the bundled Antonio 700, line in body font
- PASS: 360 food: square 18% of size, persimmon, word in ink
- PASS: 360 food: 16 px under the header, not sticky
- PASS: 360 food: everything below the hero unchanged against 8.28
- PASS: 360 food: header, Settings icon and tab bar unchanged against 8.28
- PASS: 360 Today: session name and line from real data
- PASS: 360 no page errors
- PASS: 390 today: UPPER A, no clipping, inside 24 px gutters
- PASS: 390 today: size within max 168 and min
- PASS: 390 today: fills the width (largest size that fits) unless at max
- PASS: 390 today: one line
- PASS: 390 today: hero font is the bundled Antonio 700, line in body font
- PASS: 390 today: square 18% of size, persimmon, word in ink
- PASS: 390 today: 16 px under the header, not sticky
- PASS: 390 today: everything below the hero unchanged against 8.28
- PASS: 390 today: header, Settings icon and tab bar unchanged against 8.28
- PASS: 390 training: PLAN, no clipping, inside 24 px gutters
- PASS: 390 training: size within max 96
- PASS: 390 training: fills the width (largest size that fits) unless at max
- PASS: 390 training: one line
- PASS: 390 training: hero font is the bundled Antonio 700, line in body font
- PASS: 390 training: square 18% of size, persimmon, word in ink
- PASS: 390 training: 16 px under the header, not sticky
- PASS: 390 training: everything below the hero unchanged against 8.28
- PASS: 390 training: header, Settings icon and tab bar unchanged against 8.28
- PASS: 390x700 Plan: first exercise card starts above the fold (44 px of it shows above the tab bar)
- PASS: 390 quicklog: QUICK LOG, no clipping, inside 24 px gutters
- PASS: 390 quicklog: size within max 168
- PASS: 390 quicklog: fills the width (largest size that fits) unless at max
- PASS: 390 quicklog: one line
- PASS: 390 quicklog: hero font is the bundled Antonio 700, line in body font
- PASS: 390 quicklog: square 18% of size, persimmon, word in ink
- PASS: 390 quicklog: 16 px under the header, not sticky
- PASS: 390 quicklog: everything below the hero unchanged against 8.28
- PASS: 390 quicklog: header, Settings icon and tab bar unchanged against 8.28
- PASS: 390 calendar: PROGRESS, no clipping, inside 24 px gutters
- PASS: 390 calendar: size within max 96 and min
- PASS: 390 calendar: fills the width (largest size that fits) unless at max
- PASS: 390 calendar: one line
- PASS: 390 calendar: hero font is the bundled Antonio 700, line in body font
- PASS: 390 calendar: square 18% of size, persimmon, word in ink
- PASS: 390 calendar: 16 px under the header, not sticky
- PASS: 390 calendar: everything below the hero unchanged against 8.28
- PASS: 390 calendar: header, Settings icon and tab bar unchanged against 8.28
- PASS: 390 running: RUN, no clipping, inside 24 px gutters
- PASS: 390 running: size within max 168 and min
- PASS: 390 running: fills the width (largest size that fits) unless at max
- PASS: 390 running: one line
- PASS: 390 running: hero font is the bundled Antonio 700, line in body font
- PASS: 390 running: square 18% of size, persimmon, word in ink
- PASS: 390 running: 16 px under the header, not sticky
- PASS: 390 running: everything below the hero unchanged against 8.28
- PASS: 390 running: header, Settings icon and tab bar unchanged against 8.28
- PASS: 390 food: FOOD, no clipping, inside 24 px gutters
- PASS: 390 food: size within max 168 and min
- PASS: 390 food: fills the width (largest size that fits) unless at max
- PASS: 390 food: one line
- PASS: 390 food: hero font is the bundled Antonio 700, line in body font
- PASS: 390 food: square 18% of size, persimmon, word in ink
- PASS: 390 food: 16 px under the header, not sticky
- PASS: 390 food: everything below the hero unchanged against 8.28
- PASS: 390 food: header, Settings icon and tab bar unchanged against 8.28
- PASS: 390 Today: session name and line from real data
- PASS: 390 no page errors
- PASS: 360 FULL BODY session fits cleanly
- PASS: 360 very long own day name wraps at the min (56 px, two or more lines), never clips
- PASS: 360 own plan Today line leaves out the plan week
- PASS: 360 freestyle Today shows only what exists
- PASS: 360 QUICK LOG on one line with the square after LOG
- PASS: 390 FULL BODY session fits cleanly
- PASS: 390 very long own day name wraps at the min (56 px, two or more lines), never clips
- PASS: 390 own plan Today line leaves out the plan week
- PASS: 390 freestyle Today shows only what exists
- PASS: 390 QUICK LOG on one line with the square after LOG
- PASS: rest day: Today keeps its current content, no hero
- PASS: Run line comes from the real plan (week left out while the plan is in its lead in week 0)
- PASS: Run line names the run planned today
- PASS: hero font comes from this site only, no third party font request for it
- PASS: offline load shows the hero in the bundled font
- PASS: 8.28 suite 64 of 64, 8.27 suite 47 of 47, 8.26 suite 26 of 26, 8.25 suite 54 of 54, upgrade and restore check
- PASS: unit tests food 495/0, onb 138/0, sets 272/0, compat 83/3 (known)
- Screenshots at 360: screenshots/829-today-360.png, 829-training-360.png, 829-quicklog-360.png, 829-calendar-360.png, 829-running-360.png, 829-food-360.png, plus 829-running-plan-360.png with a run plan set.

Problems found and fixed during the build, before commit:
- The existing home page already used a class named hero (flex layout), which broke the first version. The new classes are named rtwh.
- A very long own plan day name shrank to about 25 px on one line instead of wrapping at the 56 px min. The word block is now capped at the fit width, and the check requires the min and two or more lines.
- At 360x700 the first Plan card started at 645 px, behind the fixed tab bar (top at 639). The fold is now the top of the tab bar, and the Plan word shrinks until 44 px of the card shows.
- Test fixes, not app changes: the 8.27 suite closed the logo menu by tapping at y 700, which now lands on Start workout, so it uses Escape. The 8.28 overlap check now only counts buttons in the open modal when a tip sits inside Settings. The workout note layout check sees the first Plan card lower by the hero's height (508 to 647), which is the intended push down. The card's own height is unchanged (764).

Decisions made without asking:
- The bundled face is registered as its own family, "RTW Hero", from assets/fonts/antonio-latin-700-normal.woff2 (@fontsource/antonio 5.3.0, latin, 700, licence in assets/fonts/OFL-Antonio.txt), preloaded, and used only by the hero word. The existing Google Fonts link for Antonio, DM Sans and Space Mono stays as it was, so every other piece of text keeps its current font. Removing it would have changed other text. The hero itself makes no third party request.
- Offline: the service worker already caches every file it fetches, so the font is cached on the first online visit. Tested by loading online, going offline, reloading: the hero renders in the bundled font. The service worker logic is unchanged apart from the version.
- Sizing: the word fits the screen width minus 48 px (the square is inside the measured box). The block lines up with the 20 px page edge used below it. Max and min: 168 and 56 px on Today, Quick Log, Run, Food; 96 and 40 px on Plan and Progress. Quick Log never wraps and may go under 56 px to stay on one line. On Plan the word may go under 40 px to keep the first card visible.
- The 16 px is measured from the header's bottom edge to the top of the word.
- Today hides the hero on a rest day and when the week is done (rest day and empty states keep their current content). Freestyle shows TODAY with no line. An own plan shows the day name, lifts and minutes, without the plan week.
- Plan's session count uses the next workout not yet logged this week, or "All 4 sessions done." when the week is done.
- Run leaves the week out while the run plan is in its lead in week (numbered 0), shows "Week N. No run planned today." on a day without a run, the race detail on race day, and no line when no run plan is set.
- Food keeps "Today." as the spec gives it, even after stepping to another day with the arrows.
- The existing screen titles under the hero (THURSDAY block, PLAN label, LOG WHAT YOU EAT, the PROGRESS and RUN blocks) were left in place, because nothing below the hero was to change. This repeats some words; worth a look in daylight.
- Screenshots are committed in screenshots/ so they are kept.

Left alone: everything below the hero, the header, the Settings icon, the tab bar, all logic and storage.
Seen but not changed: a tap outside the open logo menu can also press the button underneath it (found while running the 8.27 suite). This behaviour is older than this build.
