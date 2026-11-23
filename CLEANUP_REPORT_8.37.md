# Cleanup report, build 8.37

Local branch `week-lookahead` only. Not pushed, not merged. It was cut from master at 48906f8 (8.35b1).

| Part | Commit | Service worker cache |
|---|---|---|
| Code: week strip, Quick Log merged into Today and Lift, gear, no menus | see `git log` | `monk-mode-v118` |
| Tests | see `git log` | `monk-mode-v118` |
| This report | see `git log` | `monk-mode-v118` |

Build label: Version 8.37.

## Skills used

- anthropic-skills:token-smart-work
- design-skills:interaction-design, for the strip and the Change workout sheet
- engineering:testing-strategy
- design:ux-copy
- design:accessibility-review
- design:design-critique, against references/today_b.png
- security-review, on the final diff: no findings

## Part A: week strip

- **One shared strip on Today and Lift.** It runs Monday to Sunday and shows the day letter, the date, the short workout name and a mark: a check for done, a half circle for shortened, a ring for upcoming, nothing for rest. Today's date sits in a persimmon circle with an ink ring.
- **Selection.**
  - The selected day is an ink pill with cream text, so it is shown by shape as well as color.
  - Every cell has `aria-pressed` and a full label, for example "Friday, November 20, Lower B, upcoming".
  - Choosing a day is announced.
- **Day previews.**
  - **Future day:** no START, a "Planned for Friday" line, the list of lifts, and the Short and Change workout buttons. A choice made there is stored under that day's existing `week|day` key.
  - **Past day:** the logged lifts with their set counts, or "Nothing logged." and "Log for this day", which opens Lift on that day.
  - **Rest day:** shows rest. Change workout moves the next unlogged workout onto it, using the existing week moves.
- **Changing week.**
  - The arrows or a swipe change week, and next week can be previewed and adjusted.
  - A preview is never saved as the current week, so a reload always lands on today.
  - "This week" is a single 44px tap back.
- **Fit.** It fits at 390 and 320 with every day a 44px target. The strip runs full width, and each cell is about 45 by 80 px at 320.

## Part B: Quick Log merged into Today and Lift

- **Tab bar.** It is Today, Lift, Run and Progress, with Food fifth when Food is on.
- **Short and Change workout** sit under the card on Today and under the header on Lift. They are 48px with an ink outline and never use persimmon. The sheet offers Pick another workout, Add an exercise and Build my own, reusing the Quick Log logic.
- **8.35b behaviors kept:** the Restore line, the takeover confirmation, added lifts, Short per date and weight prefill.
- **Menus.**
  - The logo dropdown is gone, and the logo goes to Today.
  - The gear is at the top right on every tab. It is 44px with the label "Settings", and returns you to the same tab.
  - Week review is a button in Progress.
  - The Edge and Why I built this are near the top of Settings.
- **Tips, onboarding and older tests were updated.** The menu tip now reads "The gear at the top opens Settings, The Edge and Why I built this."

## Where "Quick Log" is still left, and why

- **Code names only:** `tab-quicklog`, `openQuickLog`, the `quicklog` tip id, `QUICK_*` constants, CSS classes and comments.
  - The Quick Log screen still exists as an internal screen that Change workout opens. Its hero word is now WORKOUT.
  - Stored data uses `quickLog` on entries, which is unchanged.
  - No visible text says Quick Log. t837_b checks every screen, Settings and every tip.
- **Comments mentioning the old logo menu** remain in two code comments only. There is no menu code or markup left.

## Notes

- **Some form fields still use `<select>`:** the run fields, the Progress exercise picker and profile sex. These are form fields, not menus, so they were kept.
- **There is no Replay intro control in Settings,** on master or here. Nothing was invented. Say if you want one.
- **Behavior change:** a Short or other choice stored on a day dated today or later now counts until that date, so a choice made for Friday holds on Friday. Days in the past are unchanged.
- **Storage:** there is no new or changed key. The only key that is no longer written is `monk_nav_hint_v1`, which belonged to the removed menu. Storage is identical after a round trip.
- **The real backup test was skipped,** because `~/RTW Developments/test_backup/` does not exist. No backup was committed.
- **Design critique fixes:**
  - "Change workout" no longer wraps at 320.
  - "Week 7 of 10" stays on one line.
- **Accessibility fixes:**
  - Today's persimmon date has an ink ring. It was 2.97:1 against cream, and the ring brings it above 3:1.
  - Changing the selected day is announced.
- **Known bug found while auditing 8.38 (not fixed here):** Change Training Plan puts the week back to 1 but keeps the logged sets, so the new week 1 reads the old week 1 sets.

## Tests

- New tests: t837_a_strip (238 checks) and t837_b_nav (94 checks). They cover Upper and Lower, Arnold, and Advanced with running on, at 390 and 320.
- Updated tests: food.js, t825, t826 (a rest day fix), t827, t828, t829 (baselines re-recorded for the four tab bar and the narrower logo only), t830_6, t831_1, t832, t834_12, t834_short_normal, t835b_a, t835b_b and t835b_cd.
- Screenshots in tests/browser/out/: 837-today-strip, 837-future-day, 837-past-day, 837-change-sheet, 837-bar, 837-bar-food and 837-header, each at 390 and 320.
- **Full suite:** every browser test passes, and food.js (492), onb.js (138) and sets.js (272) pass. compat.js has 83 passed and 3 failed: these are the 3 known failures, "switchDay() activates a day that exists" for the 3, 4 and 5 day splits, the same as on master.
- **Rerun note:** the full run spanned a machine sleep, and seven files crashed in the middle of it (t830_2 to t831_2). Run again on their own, all seven pass.
