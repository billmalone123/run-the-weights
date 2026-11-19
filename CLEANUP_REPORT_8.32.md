# Cleanup report, build 8.32

Pushed. Commit 76d4cfe. Live at runtheweights.vercel.app: Version 8.32, service worker cache `monk-mode-v110`. Origin matches local.

## Preflight

- The build was 8.31, and the tree was clean and pushed at 0387af5.
- Tag `pre-8.32` was created on 0387af5 and pushed.

## What changed

**Food tab:**
- The FOOD hero and its persimmon square stay, with the hero line "Today.".
- Under them: "Food tracking is coming soon." and "Log your weight on Progress, then Body.", with an Open Body button. The button opens Progress on the Body view.
- Every Food input, total and control is hidden with `display: none`, including the weigh in. None of them can be reached by tap or keyboard.

**Flag:**
- `var FOOD_ENABLED = false;` is in the first script in the page body.
- It adds the class `food-off` to the page, and CSS hides everything Food related from that one class.
- All the Food code stays in place.

**Food pointers removed while the flag is off:**
- the Food tip
- the Food today card on Today, with its "Log a meal" link (the Bodyweight card now spans the row)
- the "Log a meal" button on the setup finish screen ("Start lifting" stays)

**Data:**
- No stored data, storage key, backup field or restore step changed.
- Food logs, food targets, goal mode and weights stay as they were. Weights saved from Food show on Body.

**Kept:** the Food icon in the bottom tab bar and the Food row in the logo menu. Both open the coming soon screen.

## API endpoints

What each endpoint did before 8.32:

**`api/meal.js`:**
- POST only.
- Checked the `x-rtw-pass` header against `MEAL_PASSCODE`.
- Took a photo and/or a note.
- Called the Anthropic Messages API with `ANTHROPIC_API_KEY` (model from `MEAL_MODEL`) and returned the estimated items.

**`api/barcode.js`:**
- POST only, with the same passcode check.
- Validated the barcode.
- Called Open Food Facts, which needs no key. If that had nothing, it called USDA FoodData Central with a hardcoded `DEMO_KEY`.
- Returned nutrition per 100 g.

**Now:**
- The new `api/_food.js` holds the server flag, `FOOD_ENABLED: false`. Vercel does not route files that start with an underscore.
- While it is false, both endpoints answer 503 `{"error":"Not available"}` as their first step. That happens before the method check, the passcode, the body, any key or any fetch.
- The passcode check and everything after it are unchanged, for when Food comes back.
- Live check after deploy: both endpoints answered `{"error":"Not available"}` with status 503.

## Turning Food back on

Two changes: `FOOD_ENABLED = true` in index.html and `FOOD_ENABLED: true` in `api/_food.js`. The server functions can't read a value from index.html, so a single shared flag was not possible without a build step. `node food.js` checks that both ship as false.

## Checks

**8.32 browser check, `t832_food_locked.py`** (28 of 28):
- **Food tab:** shows only the hero and the coming soon block, with the hero word FOOD and the persimmon square.
  - The message and line are exact, with no dashes or exclamation marks.
  - The message sits about 24 px under the hero, with no sideways scroll at 360.
  - The only control on the tab is the 44 px Open Body button. 40 presses of Tab never reach a food input.
  - The food inputs still exist behind the flag.
- **Open Body:** opens Progress on Body, and weights saved from Food show there.
- **Food stays reachable:** it is still in the tab bar and the logo menu.
- **Today:** no food card and nothing pointing to logging food. The bodyweight card stays.
- **Setup finish:** no Log a meal button, and Start lifting stays.
- **Data:**
  - Planted food logs, targets, goal mode and weights are unchanged after a reload.
  - The backup carries them.
  - A restore into a fresh install brings them back unchanged, and Food still shows the coming soon state.
- **Food tip:** never shows on a fresh install.
- **Flag on:** turning the flag on in the page brings Food back with its 24 px gap and no coming soon block.
- No page errors.

**`food.js` section 11, new, 11 checks.** With Food locked, each endpoint gets a valid passcode and a valid body:
- **Response:** each answers 503 Not available.
- **No outside call:** `fetch` is called 0 times. That covers Anthropic, Open Food Facts and USDA.
- **No key read:** no key or passcode is read from the environment. A control check shows the same probe does see the passcode read when Food is on.
- **Passcode kept:** with Food on again, both endpoints still return 401 for a wrong passcode.
- **Shipped flags:** both ship false.

Sections 9 and 10 still test the full endpoints with Food on.

**Earlier browser checks, updated for 8.32:**
- **`t828_tips`:** a fresh install now expects every tip except Food. The "tap anywhere else" check now uses the Run screen, since Food has no tip. It runs 60 checks, down from 64, because the four per tip checks no longer run for Food.
- **Turn Food on in the page first,** so the Food code stays tested for when it returns: `t830_3_food_order`, `t830_5_chart_labels` (the Food bodyweight chart) and `t831_3_weight_history` (the Food to Body link).
- **`gapfn.js`:** it now measures to the first visible block under the hero. On Food, that is the coming soon block.

**Full set at 8.32:**

| File | Result |
|---|---|
| t825_plan_week | 54 of 54 |
| t826_lift_notes | 26 of 26 |
| t827_quicklog_menu_edge | 47 of 47 |
| t828_tips | 60 of 60 |
| t829_hero | 117 of 117 |
| t830_1_titles | 45 of 45 |
| t830_2_recent_workouts | 21 of 21 |
| t830_3_food_order | 30 of 30 |
| t830_4_run_note | 15 of 15 |
| t830_5_chart_labels | 32 of 32 |
| t830_6_menu_more | 20 of 20 |
| t831_1_strip | 18 of 18 |
| t831_2_run_note_with_run | 17 of 17 |
| t831_3_weight_history | 52 of 52 |
| t832_food_locked | 28 of 28 |

**Unit suites:**
- food: 507 passed, 0 failed (496 before, plus 11 new)
- onb: 138 passed, 0 failed
- sets: 272 passed, 0 failed
- compat: 83 passed, 3 failed (the 3 known failures)

## Decisions

- **Button label:** "Open Body".
- **Coming soon block placement:** it sits after the hidden Food section, not right under the hero. The 8.30 rule that puts 24 px under a hero targets the section right after it. If the coming soon block sat there, the Food section would have lost its gap when Food comes back. The coming soon block gets its own 24 px.
- **Flag location:** the page flag is in the first script in the body, not in the head. The unit test harness loads the page's scripts by position, and a new head script shifted them. The flag still runs before any Food markup is drawn.
- **Left alone, since you said not to touch anything else:**
  - the Food targets section in Settings (calories, protein, carbs, fat, goal weight, and the owner only meal passcode)
  - the setup finish line that shows a daily calorie target when one exists

  Neither points to logging food. Say if you want them hidden too.

## Process notes

- `build_state.md` is gitignored, so its 8.32 entry is local only.
- Skills used: none.
