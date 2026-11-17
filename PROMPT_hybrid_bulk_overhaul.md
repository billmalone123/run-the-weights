> **DONE. Five phases, builds 7.92 to 7.96 (SW v63 to v67), one commit and one push per phase.**
>
> **Audit, what already existed and was skipped.** Exercise variants and `EX_ALTS`, equipment tags on variant chips, the Custom variant, `findNextUnloggedDay()`, Quick Log bodyweight, the food log and the Settings modal were all present and reused, not rebuilt. Also already there and built on: estimate mode in the maxes modal (Epley with weight and reps fields), a Food tab weight block with weekly average and change, a `last-session-chip` status line, and an existing chart style (inline SVG, horizontal grid only) that the bodyweight chart copies. Two things the prompt assumed did not exist: there was **no ski erg no-repeat rule** anywhere in the repo, so the builder's weekly rotation is new, and there was **no per-set Done control**, since logging autosaves on blur, so one was added. Three suites (`compat.js`, `onb.js`, `sets.js`) only loaded the first two script blocks and had been failing since a third block was added in an earlier build; they now load every block. `onb.js` went from failing to 138 of 138. `compat.js` still has 3 failures (`switchDay() activates a day that exists` for the 3, 4 and 5 day splits). They fail identically on the untouched code and come from its DOM stub, not the app. Not fixed here.
>
> **Black theme and the brand swap.** Dark is unchanged and remains the default (no attribute). Black is `html[data-theme="black"]` overriding only `--bg --surface --surface-2 --border --border-hi --black --dark --card`; the body gradient is off. A tiny script right after the `theme-color` meta reads `rtw_theme` and sets the attribute and the status bar color before first paint. Verified: the attribute is present at the first `readystatechange`. The seven inline `background:#1A1A18` became `var(--bg)`, plus two `#1F1F1C` surfaces and seven hardcoded badge borders became tokens. The brand PNGs were remapped per pixel by luminance: `t = (L - L_bg) / (L_cream - L_bg)`, each channel `c - bg*(1 - t)`. The background reference is the 99th percentile of border pixels plus a small margin, because the old background has noise, so every edge pixel is exactly 0,0,0 and the cream is untouched. CSS `content: url(...)` swaps them in Black. `rtw_theme` is not in the backup payload (an explicit field list) or in the migration list. A Dark backup restores into Black and keeps Black. Contrast in Black: `--muted` 7.21:1 on bg and 6.76:1 on surface (Dark was 5.98 and 5.41), `--text` 18.17:1. Borders stay decorative, as in Dark. The nav pill still shows the wordmark as a dark chip inside the translucent pill; that is the existing design, and in Black it is pure black, not gray.
>
> **Library, before and after.** 43 exercises before, 110 after (67 new, all `day:"library"`, which matches no pool or split list). Every exercise has `muscle`, `pattern`, `kind` (compound or isolation, needed for like for like) and `equip`. Programmed exercises derive `equip` at load from the existing `EQUIP_RULES`, with one rule added for pull up bar. By muscle: chest 13, quads 14, full-body 12, lats 9, triceps 9, hamstrings 9, upper-back 7, core 7, biceps 6, delts 5, side-delts 5, rear-delts 5, glutes 5, calves 4. By pattern: push 32, pull 27, squat 18, hinge 14, conditioning 8, core 7, carry 4. Every muscle, pattern and kind slot holds at least 4. Every programmed exercise offers at least 4 like for like swaps. Swaps filter on that slot key: hand picked alts first, library extras behind More. Ten old alts that were never like for like (for example Lat Pulldown under Straight Arm Pulldown, Seated Leg Curl under RDL) drop out of suggestions, but a stored pick still resolves through `exVariants()`, so history stays. Hide removes a name from suggestions and the builder only, never the active pick and never history. The list is in backups, and Settings can show items again. Ids unchanged, and old sets still display and drive progression (checked with seeded old data).
>
> **How the builder picks, and where each reason comes from.** `buildSession(dayId, week)` is the one assembly point; `splitDayExercises()` and both render paths read it. Main compound is the first primary lift, else the first compound. Secondary is the next compound in the day's program. The finisher is an isolation for the main lift's muscle, else the day's last isolation. On Session size Default the list is the program exactly, in program order. With a size set: too many accessories are trimmed by a weekly rotation that names what sits out; too few are filled one at a time from the library. Fills go to the day's least covered muscle, isolation first across every muscle before any compound, owned equipment only, hidden names skipped, rotated by week. With a time budget set and the estimate over it, isolation accessories of different muscles pair into supersets. Each reason string is written by the branch that made the pick and names that rule and its inputs, for example "Accessory. Rear delts had no exercises so far today, the least of this day's muscles; rotated in for week 2." Checked on every split at sizes 4 and 10 over 6 weeks: exact counts, no duplicates, no week identical to the one before, a reason on every row.
>
> **Taps from open to first logged set.** Before: 3 (tap the Set 1 reps box, type one digit, tap away to commit; the weight box was already prefilled from the aim). After: 1 (Done, which fills an empty reps box from the aim reps, then last session, then the bottom of the range, and saves through the same path). It reads Logged only once the set is actually stored; with no weight available it focuses the weight box instead. If the app opens on Home, add 2 taps both before and after (menu, Lift).
>
> **Phase 4 and 5 notes.** Lift opens on `findNextUnloggedDay()` from every entry path. A mid workout restore still wins, and after the first pick of a day manual navigation is respected, both by design. Each set shows last session's numbers for that slot, matched on `activeVariant(ex)`; this was checked through a week advance for the default variant and a custom one. PR badge: this week's best Epley estimate beats every earlier week on the same exercise and variant. Week at a glance: Monday to Sunday, today outlined, logged days struck through, tap to open. Logging targets are all at least 44px. Bodyweight: the chart spans from the first weigh in (two weeks minimum, eight maximum), and a configurable band (default 0.5 to 1.0 lb a week) produces one line outside it with direction only. The existing goal mode calorie recommendation predates this and was left alone. Epley: one field per lift takes `235x4`, a single warns that it is noisy, more than 10 reps warns that it drifts, and Reset 1RMs now lands in estimate mode. The private Sunday template is titled **Engine** everywhere it renders; the word HYROX is in code comments only and appears nowhere in the DOM. It replaces only the Sunday slot when Settings turns it on, and its exercises are excluded from the food post, the only share surface. `liftDaysPerWeek` is untouched, so the run plan is byte-identical with Engine on or off and the hard lift and hard run rule holds. When the run plan puts a long or tempo run on that Sunday, the first station says so and tells you to keep it easy. Also fixed on the way: bodyweight, band, ski erg and rope work (Ab Wheel and Nordic Curl included) could never be logged without inventing a weight. They now log at weight 0, which progression and PR math skip.
>
> **Service worker incident.** The Phase 1 bump script truncated `sw.js` to zero bytes, and the empty file shipped with all five phase commits (dd095e9 through 1320c2f). An empty worker has no fetch or activate handler, so the app still loaded from the network but lost offline caching and old cache cleanup. Restored byte for byte from 35165c1 with the cache name at `monk-mode-v67`, and verified in Chromium that it activates and builds that cache. Phones that picked up the empty worker replace it on their next online load.
>
> **Still needs a real phone check.** Everything above was driven in headless Chromium at 390px, not on a device. On a real phone: (1) the no-flash load in Black and the iOS status bar color, since `black-translucent` status bars may ignore `theme-color`; (2) whether `img { content: url() }` swaps the brand PNGs on iOS Safari (Chromium only is verified; if Safari ignores it, the old gray-boxed PNG shows on true black); (3) `--muted` text and the very dark borders in Black under real screen brightness; (4) thumb reach for Weight, Reps and Done one handed; (5) the 9.5px week at a glance labels; (6) whether the Engine day should own Sunday at all when the long run is also on Sunday. Moving the long run to Saturday removes the overlap.

## Sync first

```
rm -f .git/index.lock .git/ORIG_HEAD.lock
git fetch origin
git reset --hard origin/master
```

Confirm `git log --oneline -3` before starting. This file runs in five phases. Finish each phase, run its checks, and commit it on its own before starting the next. Push once at the end of each phase.

## Context

The goal changed. The race is cancelled, the focus is a bulk from about 185 to 200 lb with heavy lifting, light cardio and a quiet technique first HYROX transition. The app needs to feel built for a hybrid athlete, not generated. Three problems to fix: the exercise library is too small to try things, the builder needs to show more of what it is doing and why, and the app should offer true black next to the current dark.

Before writing code, audit what already exists and skip anything already done. These exist today and must not be rebuilt: exercise variants and `EX_ALTS`, equipment tags on variant chips, the Custom variant option, `findNextUnloggedDay()` for the default day, the Quick Log bodyweight entry, the food log, the Settings modal. Note what you found at the top of your completion summary.

Voice rule for every string you write: short, direct sentences, no hype, no emoji, no dashes. Coaching cues must be grounded in a real training reason, in the same register as the existing `repWhy` lines and The Code.

## Task

### Phase 1: Theme toggle, Dark and Black

1. Keep the current palette as Dark, unchanged and still the default.
2. Add Black as `html[data-theme="black"]` overriding only the surface tokens: `--bg #000000`, `--surface #0B0B0A`, `--surface-2 #151513`, `--border #22211E`, `--border-hi #2E2D29`, `--black #000000`, `--dark #050505`, `--card #0B0B0A`. Accent, text, muted and dim stay as they are so existing contrast ratios hold. Remove the body radial gradient in Black.
3. Replace every inline `style="background:#1A1A18"` (the `body` and each `.tab-main`) with `style="background:var(--bg)"`. Leave `color:#1A1A18` on cream fills alone, that is label text, not a background.
4. A small script in `<head>` right after the `theme-color` meta reads `localStorage` key `rtw_theme` and applies the attribute before first paint, and sets the `theme-color` meta to `#000000` for Black. No flash on load.
5. Add a Theme row to the Settings modal using the existing `liftdays-wrap` / `liftdays-btn` pattern with Dark and Black buttons. `setTheme(t)` sets the attribute, updates the meta, stores the key in try/catch, and marks the active button. `openSettingsModal()` marks the active button too.
6. The brand PNGs have the old dark background baked in and would show as gray boxes on true black. Generate `assets/brand/rtw-square-a-black.png` and `assets/brand/rtw-wordmark-black.png` by remapping each pixel between the old background and cream so the old background becomes pure black (luminance remap, keep alpha). In Black, swap them with `html[data-theme="black"] img[src$="rtw-square-a.png"] { content: url(...) }` and the same for the wordmark.
7. Theme is a device preference. Keep `rtw_theme` out of the backup payload and the versioned storage migration.

### Phase 2: Tagged, larger exercise library

1. Audit `EXERCISES` and `EX_ALTS`. Add three fields to every exercise: `muscle` (primary muscle group), `pattern` (push, pull, squat, hinge, carry, core, conditioning) and `equip` (an array drawn from barbell, dumbbell, cable, machine, smith, band, bodyweight, pullup-bar, sled, tire, skierg, medball, rope). Derive `equip` for existing items from the rules already used for variant tags, do not hand tag from scratch.
2. Expand the library to roughly 100 exercises. Weight the additions toward the home gym: barbell, dumbbells up to 80 lb, cable stack, pull-up bar, tires, sled, ski erg, med ball, rope. Add enough per muscle and pattern that every slot has at least four real options. Do not invent exotic movements. Every new exercise needs the same fields as the existing ones: `repRange`, a `repWhy` in the app voice, `increment`, and the max linkage the existing ones use.
3. Existing ids must not change. Existing logged history must still resolve. Run the backward compat check described in `PROMPT_backward_compat_audit.md`.
4. The substitution picker should filter by `muscle` and `pattern` first, then show equipment tags, so a swap always offers a true like for like movement. Add a "Hide this exercise" option that stores a hidden list and removes it from swap suggestions only, never from history.

### Phase 3: Builder, more exercises per session and a reason for each pick

1. Make exercises per session a setting in Settings, with a sensible range, defaulting to the current count so nothing changes until the user changes it.
2. Build sessions from slots: main compound, secondary compound, accessories, finisher. Fill accessories and finisher from the library using equipment the user has, muscle coverage for that day, and recent history so the same structure is not repeated session to session (the same rule already applied to ski erg sessions).
3. Add superset support for accessories so a longer session does not run past the time budget. Show an estimated session time on the day header.
4. Next to each exercise show a one line reason it was chosen, for example "Cable fly. Chest finisher, pressing already covered." Generate these from the actual rule that picked the exercise, not from canned text. If a pick came from a rule, the reason names that rule.

### Phase 4: Visibility and ease of use

1. Confirm Lift opens to today's session with `findNextUnloggedDay()` and fix any path where it does not.
2. Show last session's weight and reps beside every set, so the target is visible without a lookup. Match on `activeVariant(ex)` the way `prevWeekEntry` does.
3. Add a week at a glance row: today highlighted, each day's focus, estimated time.
4. Audit tap targets on the logging screen. Weight, reps and the done control must sit in one thumb reach zone with at least 44px targets. Fix any that do not.
5. Add a PR badge when a set beats the best prior estimated 1RM for that exercise and variant.
6. Reduce taps from open to first logged set. Report the count before and after in the summary.

### Phase 5: Bulk and HYROX support

1. Bodyweight trend: a small chart from Quick Log bodyweight entries on the Food or Calendar surface, with the weekly change. If weekly change is outside a configurable band, show a one line prompt to adjust calories. No numeric diet prescriptions beyond the user's own target.
2. Epley reset flow that accepts multi rep sets (for example 235x4) and warns when a noisy single is being used.
3. A HYROX day template for the Sunday slot built from the new `sled`, `skierg`, `medball` and `rope` exercises, technique first and low intensity. It must be hidden from any public sharing or social surface for now, since HYROX is not being announced.
4. Keep the existing running hard day rule: a hard lift day and a hard run day never share a day.

## Verify before pushing

1. Theme: toggle Dark to Black and back, reload in each, confirm no flash, confirm the splash, nav pill, footer wordmark and Settings brand mark show no gray box in Black, confirm the status bar color follows. Check contrast of `--muted` text and borders in Black on a real phone screen.
2. A backup exported in Dark restores cleanly in Black and the reverse. `rtw_theme` is not in the backup.
3. Every exercise has `muscle`, `pattern` and `equip`. Print a table of counts per muscle and per pattern and confirm no slot has fewer than four options.
4. Every pre-existing exercise id still resolves and old logged sets still display and still drive progression.
5. Swap an exercise on three different muscle groups, confirm only like for like options appear and equipment tags are correct. Hide one, confirm it leaves swap suggestions but its history is intact.
6. Change exercises per session to the minimum and maximum, confirm the builder fills slots, never repeats the previous session's structure, and every pick shows a reason that names a real rule.
7. Log a set, advance a week, confirm last session numbers appear beside the set and progression still rolls correctly for curated and custom variants.
8. Confirm the HYROX template appears only on the Sunday slot and nowhere shareable.
9. No console errors, all script blocks parse, all existing suites unaffected (Run tab worked example, stress permutations, calendar, week sync, chart, adaptive logging).

## Last steps

For each phase, bump the build stamp (and the service worker cache version) and commit with a clear message. Confirm `git log --oneline --graph -5` is a clean line, push, and confirm with `git log --oneline origin/master -3` that the push landed. Do this after every phase, not only at the end.

Leave a short summary at the top of this file when done: what the audit found already existed and was skipped, how the black theme and brand image swap work, library counts before and after by muscle and pattern, how the slot builder picks and how each reason line is generated, the tap count before and after for opening to the first logged set, and anything that still needs a real browser or real phone check, since none of this has been checked in an actual browser this session.
