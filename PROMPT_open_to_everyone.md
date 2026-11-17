> **IN PROGRESS.** The completion summary replaces this line when all phases are pushed.
>
> **Decisions made at run time (owner, before Phase 0):** themes stay Light and Black only, which is live already, so Phase 5 is verified rather than rebuilt with a Dark default. Features already live that this file lists as out of scope (reason lines, week at a glance, PR badges, bodyweight chart) stay visible. New installs get the lean Lift screen; anyone with logged history keeps Advanced on.

## Sync first

```
rm -f .git/index.lock .git/ORIG_HEAD.lock
git fetch origin
git reset --hard origin/master
```

Confirm `git log --oneline -3` before starting. This file replaces `PROMPT_library_theme_visibility.md`. Do not run that one. Work in the phases below, in order. Finish each phase, run its checks, bump the build stamp and the service worker cache, commit, and push before starting the next.

## Context

Run the Weights is being opened up. It is for anyone, women and men, young people with busy lives who also want to go out, have a couple of drinks and enjoy themselves. The job of the app is to help people stay on their path when life gets in the way, not to shame them off it. If someone already dislikes lifting, any extra effort to understand the app is a reason to quit.

A review of the live app at a 390 by 844 phone viewport found these problems, all verified in a browser:

1. One Lift session (Full Body A, 8 exercises) is about 12,900 px tall, with 280 visible buttons and 96 inputs. The first exercise sits at the bottom edge of the first screen.
2. Developer text shows to users: the Run tab shows "Setup incomplete, see PROMPT_strava_sync.md" under a Connect Strava button.
3. Personal content shows to everyone: the Food tab says "Every meal. To 200.", goal weight defaults to 200, and "Copy today's post" writes "Day 3. 185 to 200."
4. A user who says no to cardio still gets a full race planner on the Run tab and Miles, Time, Avg HR and Feel fields on every calendar day, rest days included.
5. The voice is built for one reader: "Most men pick a lane" (twice, in About), "The men who dominate in every area of life", "stronger than 99% of men your age", "Cutting either short is for amateurs", "The weak skip it", "Become undeniable".
6. 94 font declarations use the display face, 10 are hardcoded inline, 8 use the mono face, 6 use the body face, and there are 37 distinct font sizes and 101 uppercase transforms. Nothing reads as one system.
7. The food math is `bodyweight x 15` for maintenance, with no height, age or sex. That was tuned for one person.
8. No handling of drinks, nights out, travel or missed days. There is also no streak shaming anywhere, which is good and must stay that way.
9. Jargon with no explanation: aim weight, top set, working sets, failure, Maintenance, 1RM, PPLUL, Arnold, DB Press, Bulk, Cut, Carb Load, Race Prep.

Do not rename storage keys (`monk_*`) or internal function names. That would break saved data. Only change what users see.

Voice rules for every string you write or rewrite: plain words, warm and direct, short sentences, gender neutral, no hype, no emoji, no dashes, no insults aimed at people who rest or miss a day. Address the reader as "you". Never imply that skipping a day makes someone weak.

Use a real browser for verification. Playwright with Chrome works. Check at 390 by 844 and at 360 by 740.

## Phase 0: Remove leaks and personal content

1. Hide the Strava row on the Run tab entirely until Strava is actually connectable. No "Setup incomplete" text and no dead button for any user.
2. Remove "To 200" and "185 to 200" from user facing copy. Goal weight must default to empty, and the Food headline must not contain a number.
3. Make "Copy today's post" invisible to normal users. Keep it behind a hidden toggle in Settings (a long press on the version label is fine) so it stays available for the owner.
4. If the user said they do not run or do cardio, hide the Run tab from the menu and hide the miles, time, avg HR and feel fields on every calendar day. Show them again the moment the user turns running on in Settings. Rest days never show run fields.
5. Check the "Storage: NOT persistent" message in Settings. Explain what it means in one plain sentence and only show it when storage is truly at risk. Say what to do about it in the same sentence.
6. Search the whole file for any other developer facing text: file names, "PROMPT", "TODO", build jargon. Report every hit and fix the user visible ones.

## Phase 1: Simplify the Lift screen

Goal: a stranger opens Lift and knows what to do without reading anything.

1. The first exercise card must start inside the first 844 px, so the first thing visible on open is today's first exercise. Shrink the "This is where you win" hero, move the week picker and rest timer into a single compact row, and hide the Maintenance toggle unless the user has a race.
2. Show one week by default (the current one) with a small way to change it, not all ten pills.
3. One row per set: weight, reps, and a done control. Prefill from last session or the aim weight. Remove the separate "top set aim weight/reps" stepper pair from the default view.
4. Collapse by default, each behind a single link or button: Swap (open a list only when tapped), Warm-up (one line with the suggested weights, plus a "Log warm-ups" link that reveals the six fields), and Failure (an advanced option, not visible by default).
5. Show a three step tip on a user's very first Lift visit: what a set is, tap the weight and reps, tap done. Dismissible, shown once.
6. Add a one line form cue under every exercise name, in plain words, for example "Feet shoulder width, chest up, sit back and down." Keep each cue under 14 words. Do not write cues that could cause injury if misread. Mark the file with a note that a certified trainer should review every cue before launch.
7. Targets to hit and report: session page height cut by at least half, visible buttons on first view under 40, and 3 taps or fewer from app open to the first logged set (count and report the before and after).

## Phase 2: One voice and one type system

1. Typography. Define one scale with tokens: use at most 7 font sizes (for example 12, 14, 16, 20, 28, 40, 56). Replace all 37 current sizes with the nearest token. Use two families only: the display face (Antonio) for large headings and the numbers in the progress ring, and the body face (DM Sans) for everything else, including buttons, labels and tabs. Remove the mono face unless it is used for the rest timer digits only, and report the 8 current uses before changing them. Replace every inline hardcoded `font-family:'Antonio'` with the token.
2. Reduce uppercase and wide letter spacing. Keep uppercase for one small label style only. Buttons, field labels, chips and helper text use sentence case. Keep contrast ratios at or above what they are today.
3. Copy. Rewrite every flagged line, and then scan the rest of the file for any other copy that talks only to men or sounds like a dare:
   * About: replace both "Most men pick a lane" lines with something about anyone who has to choose between getting stronger and keeping up their running, with no gender in it.
   * The Edge: replace "The men who dominate in every area of life..." and the "99% of men your age" line with benefits that anyone can claim, such as feeling strong, having more energy, and moving well in everyday life.
   * Footer: replace "Do the work. Become undeniable." with a calm line, for example "Show up when you can. Pick up where you left off."
   * The Code rules 03 and 04: "03 Rest fully between heavy sets and after hard runs. Recovery is part of the work." "04 Every fourth week, ease off, lifting and running both. Rest is how you keep going." Leave 01, 02, 05 and 06 alone unless they contain gendered or shaming language.
4. Jargon. Replace labels with plain words, and add a tiny "what's this" tooltip for any term that has to stay. Aim weight becomes "Target weight". Top set becomes "Heaviest set". Working sets becomes "Sets". Failure becomes "Went to failure" with a tooltip. Maintenance becomes "Easy week mode" with a tooltip. 1RM becomes "Your max" with a tooltip. In Settings, "DB Press" becomes "Shoulder press". Split names (Arnold, PPL, PPLUL) get a one line plain description each.
5. Use the same words for the same things everywhere. List the terms you standardized in the summary.

## Phase 3: Life happens

Keep this lean. These are small, optional, and never judgmental.

1. Missing a day. Audit what happens today when a day is missed. A missed session must never show a red, failed or "behind" state. Moving a session to another day should be a single tap and shift the week without penalty. After a missed session show one gentle line on the next open, for example "Welcome back. Pick up where you left off." Never add a streak counter.
2. Going out. Add a "Going out?" option on any day, in the day header menu. It offers two choices: "Move my session" (shift it to the nearest free day) or "Make it a short session" (see item 4). No lecture, no warning text.
3. Drinks. In the Food tab add a plain "Drinks" quick add with common sizes and rough calorie values, labeled as estimates: beer (12 oz), glass of wine (5 oz), cocktail, shot. Let the user edit the number. Show the total in the same calorie ring as food, with no judgmental copy and no colors that read as a warning.
4. Short session. A "Short on time" button on the Lift screen that shows only the main lifts for the day and hides accessories for that day only. It does not change the plan, and logging works the same. Count it as a completed day.
5. Rest and busy weeks. Rename any "skip" wording to "rest day" or "swap day". Make sure no screen uses the words "failed", "missed" or "behind" in user facing text.

## Phase 4: Onboarding for everyone

1. Welcome screen: say what the app does for the person, in one line, not a feature list. For example: "A simple plan to get stronger that works around your life." Keep Get Started and Skip.
2. Goal choices in plain words: Get stronger, Build muscle, Lose fat, Stay where I am, Train for a race (shown only if they run). Map these internally to the existing goal values so nothing in the food math breaks. Remove Carb Load from onboarding. Keep it in Settings under Advanced.
3. Add optional fields for height, age and sex with a "Prefer not to say" choice, and use them in the calorie math when provided (Mifflin St Jeor). If any are missing, keep the current bodyweight only estimate and say it is a rough starting point the user can edit. Never show a calorie target below a safe floor (use 1,200 as the floor for any user). Do not show a deficit above 25 percent of maintenance.
4. A lift days question that also says what each choice means in one line ("3 days, full body each time").
5. A new lifter must be able to finish onboarding without knowing any of their maxes. Confirm that still holds.

## Phase 5: Theme toggle, Dark and Black

Owner decision at run time: Light and Black only, already live. Verify items 4, 6 and 7 still hold; do not add Dark back.

1. Keep the current palette as Dark, the default.
2. Add Black as `html[data-theme="black"]` overriding only these tokens: `--bg #000000`, `--surface #0B0B0A`, `--surface-2 #151513`, `--border #22211E`, `--border-hi #2E2D29`, `--black #000000`, `--dark #050505`, `--card #0B0B0A`. Remove the body radial gradient in Black.
3. Replace every inline `style="background:#1A1A18"` (body and each `.tab-main`) with `style="background:var(--bg)"`. Leave `color:#1A1A18` on cream fills alone.
4. A small script in `<head>` right after the `theme-color` meta reads `localStorage` key `rtw_theme`, applies the attribute before first paint, and sets `theme-color` to `#000000` for Black.
5. Add a Theme row to the Settings modal using the existing `liftdays-wrap` / `liftdays-btn` pattern, with Dark and Black. `setTheme(t)` sets the attribute, updates the meta tag, stores the key in try/catch, and marks the active button. `openSettingsModal()` marks the active button too.
6. The brand PNGs have the old dark background baked in. Generate `assets/brand/rtw-square-a-black.png` and `assets/brand/rtw-wordmark-black.png` by a luminance remap between the old background and cream so the old background becomes pure black (keep alpha). In Black, swap them with `html[data-theme="black"] img[src$="rtw-square-a.png"] { content: url(...) }` and the same for the wordmark.
7. The theme is a device preference. Keep `rtw_theme` out of the backup payload and the versioned storage migration.

## Phase 6: Tagged library, behind Swap only

1. Add `muscle`, `pattern` and `equip` to every exercise, deriving `equip` from the rules already used for variant tags. Keep at most 5 tags per exercise.
2. Grow the library with the movements people actually do in a commercial gym and at home, so there are at least four real options per muscle and pattern. The library only appears inside Swap. It must not add anything to the default Lift screen, and the default number of exercises per session must not change.
3. The Swap list filters by muscle and pattern first, then shows equipment tags. Add Hide and Favorite. Hide removes it from swap suggestions only, never from history. Favorites sort to the top.
4. Existing ids must not change and old logged history must still resolve. Run the backward compat check from `PROMPT_backward_compat_audit.md`.

## Not in this prompt (on purpose)

More exercises per session by default, supersets, reason lines on every pick, week at a glance, PR badges, a Sunday HYROX template, and a bodyweight chart (the Food tab already has a weekly average). Each adds screen weight. Revisit after the new user test below.

Owner decision at run time: the ones already built stay visible. The HYROX template was already removed.

## Verify before pushing

1. Phase 0: search all visible text on every tab for "PROMPT_", "Setup incomplete", "To 200", "200". None may appear. Say no to cardio in onboarding and confirm the Run tab and run fields are gone, then turn running on in Settings and confirm they return.
2. Phase 1: at 390 by 844, report the Y position of the first exercise card on open, the session page height, the visible button count on first view, and the taps from app open to the first logged set, all before and after. Run it again at 360 by 740.
3. Phase 2: count distinct font sizes and families in the final CSS (target 7 sizes or fewer, 2 families). Search all visible text for " men ", "amateur", "the weak", "undeniable". None may appear. Confirm contrast on every changed element.
4. Phase 3: move a session, mark a day short, log two drinks, and confirm calories change and nothing uses failed, missed or behind wording. No streak counter anywhere.
5. Phase 4: finish onboarding as a new lifter with no maxes, as a runner, and as someone who skips optional fields. Check calorie targets for 120 lb, 150 lb, 200 lb and 250 lb users, with and without height, age and sex. No target below the floor.
6. Phase 5: toggle Dark and Black, reload, confirm no flash, no gray boxes around the logo or wordmark in Black, and the status bar color follows. A backup exported in one theme restores in the other and does not contain `rtw_theme`.
7. Phase 6: every pre existing exercise id resolves, history and progression still work for curated and custom variants, swapping shows only like for like options.
8. No console errors, all script blocks parse, all existing suites unaffected (Run tab worked example, stress permutations, calendar, week sync, chart, adaptive logging).
9. Take before and after screenshots of Welcome, onboarding, Lift, Run, Food, Calendar, More and Settings and save them in `/screens`. Do not commit them if the repo is not meant to hold images, just report where they are.

## Last steps

After every phase: bump the build stamp (and the service worker cache version), commit with a clear message, confirm `git log --oneline --graph -5` is a clean line, push, and confirm with `git log --oneline origin/master -3` that the push landed.

Leave a short summary at the top of this file when done: every leak found and fixed, the before and after numbers from the Lift screen checks, the final type scale and the terms you standardized, the exact rewrites of every flagged copy line, how Going out, Short on time and Drinks work, the calorie math changes and the floor, how the black theme and logo swap work, and anything that still needs a real phone check or a trainer review. Say plainly what was tested in a real browser and what was not.

When this is pushed, run one human test before building anything else: give the phone to three people who do not lift, say nothing, and time how long each takes to log a first set. Anything over 60 seconds means the Lift screen needs another pass.
