> **DONE. Build 8.14 (SW v85).**
>
> **Four tabs.** Today, Plan, Food, More. Plan is the old Workout tab (still `data-tab="training"`). More lists Progress, Settings and About with one line each, then Quick Log, Week Overview, The Edge, Home, and Run when running is on. `goTab()` takes every old id plus `workout`, `plan`, `progress`, `settings` and `about`; Progress, Settings, About, Quick Log, info and Run all light More.
>
> **Calm Plan screen.** One card open at a time. Closed cards are one line: name, sets x reps, a check that fills when every set is in. The open card shows the target line, set rows, a Rest chip (starts that lift's rest) and More. Behind More: form cue, this week's status, Add set and Remove last set, Sets pills, Log as planned, Went to failure, Swap, Warm-up, Notes, How to. Nothing removed. The first card with work left opens on its own; finishing a card's last set opens the next. The tag and time badges above the cards are hidden outside Advanced (the week strip already shows the time), and the six day plan's Warm-up button sits in the Short on time / Going out? row. At 390 by 844, new 3 day lifter, tip dismissed: first card 331 to 254 px, page 2,973 to 1,025 px, buttons 73 to 30, inputs 24 to 4, taps to log a set from Today: 2 (Plan, check). 4 day: card at 293, 1,180 px. 6 day: card at 293 (was 369 mid-build), 1,198 px.
>
> **One font.** `button, input, select, textarea { font-family: inherit; }` removed every Arial (14 on Plan, 2 each on Food and Progress). Chart SVG labels now use `var(--font-body)`. No other hard coded stacks existed. Every tab measures DM Sans and Antonio only, 4 to 7 font sizes.
>
> **The 2,000 px value.** No fixed height anywhere. Settings is a modal capped at 90 percent of the screen (760 px) that scrolls inside; Progress is its natural height (2,064 px empty, 2,748 px with a logged set); More is 718 px. 2,000 px is the cap image viewers use when they shrink a tall full page screenshot, so the outside check was most likely reading screenshot sizes.
>
> **First week preview.** You're ready lists the next seven days from today, read from the split the answers set up and each session's own time estimate, in plain words (Full body, Upper body, Chest and back, Rest or walk). Then "Miss a day? No problem. We shift it." and, when a weight was given, "Daily food target: about X calories. You can change it any time." Fits 390 by 844 with no scroll (content ends at 625 px).
>
> **Tap targets.** 44 px minimum on day pills, Today links, goal and setting pills, week buttons, arrows, Apply, Backup, the logo pill and text links. None under 44 measured on any tab.
>
> **Not done or not possible.** The named plugin skills (design-skills, frontend-design, engineering, vercel:*) are not installed here; the built in code-review skill ran on the diff. Plan sessions estimate 65 to 90 minutes, longer than the 40 in the example; the preview reports the plan's real numbers and does not change plan logic. Not tested on a real phone.

# Build 8.14: Streamline the app (tabs, Workout screen, fonts, first week preview)

Paste this whole file into Claude Code in the monk-mode repo.

## Sync first

1. `git checkout master && git pull origin master`
2. Confirm the build stamp reads 8.13. If not, stop and tell me.
3. Read the top of the newest PROMPT_*.md so you know the house style.

## Context

Billy owns this app. It is for anyone, including women and young people with busy lives who also go out and drink. Voice is plain, short, no jargon, no guilt.

An outside check of 8.13 found these problems:

- The Workout screen is 3,794 px tall with 94 visible buttons and 32 inputs. 27 buttons show on the first screen. Too dense for a new lifter.
- The bottom bar has 5 tabs (Today, Workout, Food, Progress, Settings). That is too many.
- Some text falls back to Arial (buttons and inputs not inheriting the font) on Workout, Food, Progress, Settings.
- Progress and Settings measure exactly 2,000 px tall. That looks like a fixed height or a capture artifact. Check it.
- The "You're ready" screen ends onboarding with no preview of what the first week looks like.

## Do not touch (Billy decided these)

- Light stays the default theme.
- The meal passcode stays. It protects the API key from strangers running up usage.
- The white wordmark box inside the logo pill in Light theme stays.
- Never rename any `monk_*` storage key.

## Plugins to use

Load these skills and use them as you go, not at the end:

- `design-skills:design-critique` for the Workout and Today screens.
- `design-skills:ux-writing` for every string you add or change.
- `design-skills:accessibility-audit` for tap target size (44 px minimum) and contrast.
- `frontend-design:frontend-design` for spacing and hierarchy choices.
- `engineering:code-review` on your own diff before you commit.
- `engineering:testing-strategy` to decide what the Playwright checks in Verify should cover.
- `vercel:verification` and `vercel:deploy` to confirm the live site after the push.

Invoke each one with the Skill tool. Do not just read about them.

## Task

### 1. Four tabs, not five

Bottom bar becomes: **Today, Plan, Food, More**.

- Plan is the current Workout tab (rename the label only, keep `data-tab` values working so nothing else breaks).
- More holds Progress, Settings, and About as simple rows on one screen. Each row opens the existing screen.
- Keep `goTab()` working for every old tab id. Anything that calls `goTab('progress')` or `goTab('settings')` must still land in the right place and highlight More.

### 2. Calm Workout screen

Goal: a new lifter opens Plan and sees one clear next move.

- With the first visit tip dismissed, the first exercise card must start under 300 px from the top.
- Show one exercise card expanded at a time. Others are collapsed to a single line (name, sets x reps, a small check).
- Inside an expanded card show only: set rows (weight, reps, check), a rest timer chip, and a "More" row.
- Move Swap, Warm up, Failure, Form cue link, notes, and variants behind the "More" row.
- Logging a first set takes 3 taps or fewer from opening Plan.
- Target: fewer than 40 visible buttons and 16 visible inputs on first load, and the page under 2,200 px tall with the first card open.
- Keep every existing feature. This is hiding and ordering, not deleting.

### 3. One font everywhere

- Add a global rule so `button, input, select, textarea` use `font-family: inherit`.
- Find any hard coded `Arial`, `sans-serif` only, or system font stacks in index.html and the JS built strings, and point them at `var(--font-body)` or `var(--font-display)`.
- Verify by loading each tab and listing computed font families of all visible leaf elements. Only DM Sans and Antonio may appear (Space Mono only where numbers need it already).

### 4. Fix the 2,000 px mystery

Open More, Progress, and Settings at 390x844. If a container has a fixed `height: 2000px` or similar, replace it with natural height. Report what you found.

### 5. First week preview on "You're ready"

Billy asked what this is. It means: at the end of onboarding, before the user taps Start, show a short list of their next 7 days based on their answers. Like:

- Mon: Full body, about 40 min
- Tue: Rest or walk
- Wed: Full body, about 40 min
- and so on

Plus one line under it: "Miss a day? No problem. We shift it."

Rules:

- Build it from the plan the app already generated from their goal, days per week, and equipment. Do not invent new plan logic.
- Plain words. No "split", "hypertrophy", "RPE".
- If calories were set, one line: "Daily food target: about X calories. You can change it any time."
- Keep it on one screen with no scrolling at 390x844.

## Verify before pushing

Run Playwright against a local server (`python3 -m http.server 8123`) at 390x844 and report real numbers:

1. Console errors: zero on every tab.
2. Tab bar: exactly 4 buttons. Old `goTab` ids all still work.
3. Plan screen: first card top (px), visible buttons, visible inputs, page height, taps to log one set.
4. Fonts: distinct families per tab. No Arial.
5. Font sizes: 7 or fewer distinct sizes per tab.
6. More, Progress, Settings heights, and the cause of the 2,000 px value.
7. Onboarding: run the whole flow and screenshot the first week preview.
8. Tap targets under 44 px: list any.
9. Screenshots of Today, Plan (card open), Food, More into `/tmp/shots/`.

If a number misses its target, say so and fix it. Do not claim a pass you did not measure.

## Last steps

1. Bump the build stamp to 8.14.
2. Bump the service worker cache (`CACHE = 'monk-mode-vNN'`) by one.
3. Add a short summary of this change at the top of this prompt file.
4. Commit with a plain message, then `git push origin master`.
5. After the push, check that the live site shows build 8.14 and has no console errors.
6. Reply with: what changed, the measured numbers from Verify, and anything you could not finish.
7. End the reply by listing every skill you invoked and one line on what it changed. If a skill named above was not used, say so and why.
