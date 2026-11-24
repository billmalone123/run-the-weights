# 8.38 End of block

Branch `block-rollover`, cut from master 53dd18d (8.37d). Built as 8.38 (cache v121). Then master (8.39) was merged in and it was relabelled **8.40**, cache `monk-mode-v123`, so the label is past the live build. Pushed for a preview only. Not merged.

## Skills used

anthropic-skills:token-smart-work, design:ux-copy, design:accessibility-review, design-skills:interaction-design, design:design-critique, engineering:testing-strategy, security-review on the final diff (no findings). design-elevation and superdesign were not used.

## What changed

- **No dead end.** At the end of week 10 every "Start week 11" path now opens the block card: the Today card, the legacy Today card, the Lift "Week done" banner (now labeled "Start a new block") and `advanceToNextWeek()` itself.
- **Block card on Today.** It shows once when the last day of week 10 is logged, and again on each open after. It never shows while a workout is active. It shows weeks trained (n of 10), sessions logged, and the three maxes old to proposed with the biggest gain marked. Buttons: START BLOCK 2 (persimmon, 56 px), Edit maxes and Share (ink outlines, 44 px), and a Not yet link.
- **Not yet** is counted per block. After 3, the card shows only from Settings and Today reads "Block done" with no button.
- **Soft version.** Under 6 of 10 weeks with logged sets, the heading is "Start a new block?" and there is no Share.
- **Block number** is the count of archived cycles in `monk_split_history_v1`, plus 1.
- **START BLOCK 2** runs in this order: save the block record holding both sets of maxes, run the Start New Cycle archive (now `archiveCycle()`, with no confirm and no modal), write the new maxes, snapshot the cycle start maxes, then week 1. If the app stops between the archive and the maxes write, `blockRecover()` restores the maxes from the record on the next open.
- **Settings.** "Start New Cycle" became "Start new block" and opens the same card, with the proposal and its confirm. A Block row reads "Block N, week W of 10", with "Share block N" and "Undo last block start" for 14 days.
- **Undo** is built. It shows only while nothing has been logged in the new block. It restores the archived sets, the old maxes, the week and the cycle start snapshot, and removes the record.
- **New key** `monk_block_history_v1`, holding `[{n, endedAt, oldMaxes, newMaxes}]`. It is in backup and restore and is validated on restore. A backup without it loads as block 1 plus its archive count. Deviation to note: the open block's snooze count lives in the same array as `{n, snoozes}` until START replaces it, so it adds no second key.
- **Share.** A preview of a 1080x1350 image with a Show weights switch, on by default. Sharing uses the Web Share API with the file, and downloads the image if that isn't available. 8.36's share code became one `shareImage()` helper that both cards use. Fonts load through the existing `finFonts()` before drawing.

## Block done on the calendar week rule (after the 8.39 merge)

The block ends like every other week: when the last week is fully logged, or when its calendar week is over, logged or not. Plan weeks stop at the last week, so a missed day there never holds a block open. Someone away for weeks lands on week 10, and the card shows once that week's calendar week has passed. With fewer than 6 weeks logged, they get the soft version. After Not yet, Today shows Block done with no button, even if week 10 days are still open. Today's order: block card, then the "logged on an earlier date" card from 8.39, then Block done, then Week done.

## Formula

For each max (squat, bench, ohp), every exercise tied to it with `maxKey` and `maxPct`, using its main variant only:

1. Take the heaviest set in the last three weeks (weeks 8 to 10) with reps at or above the plan's target (`repRange[0]`).
2. Implied max = `e1rm(w, r) / e1rm(1, target) / maxPct`. A set at exactly the target reps implies `w / maxPct`, and extra reps count through the app's Epley estimate.
3. Use the main lift's implied max (bb-squat, flat-bb-bench, seated-ohp). If it has none, use the median across the tied lifts.
4. Proposed = implied x `START_FRACTION` (0.92), rounded to 5 lb, or to 2.5 kg in kg mode.
5. Never below the old max. With no qualifying set, the old max is kept.
6. If the proposal is more than 25% above the old max, the card shows "Check this weight", holds the old max, and offers a one-tap "Use N" to confirm.

Week 1 of block 2 = new max x percentage, with no +3% carry, because the archive clears the logs the carry reads.

## Ramp table (10 week test fixture, 4 day plan, lb)

| Lift | Old max | Best set wk 8 to 10 | Proposed max | Block 2 week 1 |
|---|---|---|---|---|
| Squat | 300 | 295 x 5 (week 10) | 340 | 270 |
| Bench | 225 | 220 x 5 (week 10) | 255 | 205 |
| Shoulder press | 60 | 60 x 5 (week 9) | 70 | 55 |

Each week 1 weight sits about 8% under the week 10 weight it follows.

## Where archived cycles can be seen

Nowhere directly. `monk_split_history_v1` is read only by Progress (`earliestArchivedWeights`, the start weight on each lift card), by the backup, and now by the block count and Undo. No viewer was added.

## Dead buttons found

- "Start week 11" on Today, on the legacy Today card and on the Lift banner did nothing at week 10. Fixed.
- **Already on master:** Settings > "Set your maxes" opened the maxes sheet behind Settings, so the tap seemed to do nothing. Fixed by closing Settings first, because Start new block lives in that sheet.

## Out of scope, reported only

- After a restart, Progress still labels weeks W1 to W10 per block, and the cards mix archived start weights with new block logs.
- The hardcoded "Training Week n of 10" labels are unchanged.
- **Known bug:** Change Training Plan resets to week 1 without archiving, so new week 1 logs collide with the old week 1 entries.
- `weekAnchor` holds for the session. `totalTrainWeeks()` can shrink as a race date nears, which moves "the last week".

## Tests

- `t838_block.py`: 76 checks at 390 and 320 on a 10 week fixture (`block_seed.js`).
- Full suite after the 8.39 merge: 29 browser files, 0 failures. food, onb and sets pass. compat.js has the 3 known failures ("N-day split: switchDay() activates a day that exists" for the 3, 4 and 5 day splits).
- Screenshots are in `tests/browser/out/838-*`.
