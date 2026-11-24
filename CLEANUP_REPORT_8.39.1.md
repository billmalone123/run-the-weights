# 8.39.1 hotfix: Today state

Branch `hotfix-today-state`, cut from master 8.39 (03404ba). Not merged. Cache monk-mode-v124 (block-rollover already had v123).

## Rule
A date's view is built from three things only: the plan's workout for that weekday in full, the choices saved for that date, and the sets logged on that date. Only weights carry over.

## Reproduction (fixture, no real backup)
`tests/browser/hotfix_seed.js` builds the state from the owner's description: Arnold plan, plan week 6, Monday Nov 23 9:48 pm. Chest + Back part logged Fri Nov 20 with Short, Tue Arms and Fri Chest part logged, Sat Arms full, nothing today.

| Build | Today on Mon Nov 23 |
|---|---|
| 8.37d (live when the bug was seen) | Week 6, IN PROGRESS, SHORT CHEST + BACK, Continue workout, stale marks on Mon, Tue, Fri, Sat |
| 8.39 (master) | Week 7, TODAY, Chest + Back, 7 lifts, Start workout. The calendar week rule already fixed this case |
| 8.39.1 | Same as 8.39. It also holds when week 6 is picked by hand, after Start fresh, Do this workout today and Reset |

Run `RTW_OLD=<8.37d url> python3 t8391_today_state.py` to see the failing result again.

## Storage (approved before coding)
- No date: legacy set entries without `d`, `shortDays`, `timeBoxes`, `quickSessions`, `dayAdded`, `weekMoves`, `goingOutDays` (all keyed `week|day`). Undated entries count in history and Progress, never in a date's view. The `week|day` choices are cleared when a week is picked or reset. Sets are never touched.
- Added: `closed: true` on set entries (Start fresh). `f` and `t` flags in `monk_session_times_v1` (Finish for today, Do this workout today). New key `monk_week_anchor_v1 {week, monday}` (Current week), included in backups.
- No second session slot existed. Since 8.25 there is one entry per lift per date, so a second session on the same date uses the closed flag.
- 8.39 backups load in 8.39.1, and 8.39.1 backups load in 8.39 with every set (tested).

## What changed
1. A part logged workout leads Today only when it was logged today and its last set was within RECENT_HOURS (3). It shows Continue workout plus Finish for today and Start fresh. Otherwise Today shows the planned full workout with Start workout. An older one from today gets "Earlier today: Chest + Back, 4 of 7 lifts. Continue." DONE_FRACTION (0.7) of planned lifts counts as done. A part logged day gets its own strip mark.
2. Start fresh closes today's entries for that workout and starts new ones. Nothing is overwritten.
3. Short applies to its date. A visible Full workout button replaces the small Restore link.
4. Short that would not shorten says "Already about N min. Short would keep the same lifts." and labels nothing. Affected days: PPL + Upper Lower: Upper. Upper Lower: Upper B. Full Body: C. It also applies once enough lifts are logged that Short keeps them all.
5. The week anchor is a picked week if there is one, else the 8.39 calendar rule. A one time line: "This week is week N. Wrong? Change week."
6. Settings has a Training section with Current week (1 to 10) and "Pick the week you are training this week." Today has a Change week button. The confirm reads "This week will be week N. Your logged sets stay." It says plainly when the week is earlier than the last logged week, and where targets come from.
7. Do this workout today shows on any other day of this week. Sets log under today's date and that day's workout. That day shows done and today stays as planned. "Back to <planned workout>" restores.
8. Reset this week is in Settings and on Today. It clears moves, Short, time choices, added lifts and open workouts, and keeps every set.
9. Carryover is unchanged and tested: latest logged top set, partial or not, plus progression, falling back to an earlier week, then the max.

## Tests
- `t8391_today_state.py`: 99 checks, 0 failed. Covers the fixture at 390 and 320, partials, 70 percent, Finish, Start fresh, Short, anchors, the picker (weeks 4, 6, 7 and 9), Do this workout today (3 cases), Reset, carryover in lb and kg, and backups both ways.
- Older checks updated to the new design: t825 (today's rows show today's sets), t834 and t835b_b (Full workout button), t837_a (one set reads partly logged; next week keeps Short), t837_b (Upper B cannot shorten).
- Full suite: see the commit message. The 3 known compat.js failures (switchDay on the 3, 4 and 5 day splits) are unchanged.

## Screenshots (tests/browser/out/, not committed)
Before: `8391-before-390.png`. After: `8391-after-mon-390.png`, `8391-after-mon-320.png`, `8391-after-fri-preview-390.png`, `8391-after-fri-preview-320.png`, `8391-inprogress-390.png`, `8391-earlier-today-390.png`, `8391-short-390.png`, `8391-week-picker-390.png`, `8391-tuesday-390.png`, `8391-friday-390.png`.

## Skills
anthropic-skills:token-smart-work, design:ux-copy, design:accessibility-review, design-skills:interaction-design, engineering:testing-strategy, security-review (inline pass on the diff: every new HTML value is a number or a fixed string, names go through paEsc/paJs, and imported anchors and keys are validated. No findings). Not design-elevation or superdesign.

## Still not matching, or not verified
- Not verified without your real data: your real dates, any undated or odd entries, whether your phone sits on week 6 or 7 after the update, and how your Short and time choices from earlier weeks behave.
- Start fresh only shows with a recent part logged workout. On a fresh Monday there is nothing to restart.
- Secondary buttons on the ultramarine card use a cream outline, not ink. Ink on ultramarine fails contrast.
- On Lift, a past day's rows show sets dated in this calendar week. A day done early with Do this workout today shows on its own day's preview on Today.
- The week line shows once, on the open where the week moved.
