# Cleanup report, build 8.35c

Local branch `intro-story`, cut from the tip of `fix-daylog` (8bfde59). Not pushed, not merged. `8.35a-analytics` untouched.

| Stage | Commit | Service worker cache |
|---|---|---|
| Intro story, Replay intro, Why I built this | 323f957 | `monk-mode-v117` |
| No tips over the intro, test updates | c4a54e0 | `monk-mode-v117` |
| This report | next commit | `monk-mode-v117` |

## What changed

- **Three story screens** before the existing first open setup, with your words exactly as written.
  - Each screen has an ultramarine card with the Antonio headline and the persimmon square, the DM Sans body on cream, progress dots, and Next.
  - Skip is an ink pill on every screen, matching the streak pill in `today_b.png`.
  - Swipe left goes forward and swipe right goes back. Escape skips. Focus moves to each headline, and Tab stays inside the story.
  - "Set up my week" opens the existing setup. The setup itself is unchanged.
  - "Read the privacy page" shows only on screen 3.
- **Who sees it.** Only a fresh install with no saved data. It uses the same existing-user check as the setup screens, including the IndexedDB cross check.
  - Anyone with data, or with the setup flag already set, never sees it. This includes you.
- **One new flag, `monk_intro_seen_v1`.** It is set by Skip, Escape or the last button.
  - It is in backups as `introSeen`. A restore accepts only true or false.
  - No other saved data changes.
- **Replay intro** is a button in Settings. It ends where you were and does not open setup.
- **Why I built this** is a link on The Edge. It shows the three screens on one page, built from the same words, so they live in one place.
- **Tips wait** while the story is open.
- **Photo slot.**
  - It loads `references/photo_billy_1.jpg` to `_3.jpg` if they are present. If a file is missing, there is no frame and no broken image.
  - Photos are decorative, so they have empty alt text.
  - On screens 700 px tall or less, the photo steps aside so the whole story and Next fit with no scrolling.

## Please decide

- **No privacy page exists yet.** The link goes to `privacy.html`, which does not exist, so it leads to a missing page until that page ships. This should be fixed before merging.
- **The photo files are not here yet,** and `references/` is not tracked in git. When you add the photos, keep each under 150 KB and commit them, or Vercel will not serve them. The test checks the size of any `photo_billy_*.jpg` it finds.
- **Copy:** "went through the ringer" is usually spelled "wringer". I left it as written.
- **"Your training data stays on your phone."** This is true on this branch, because there is no analytics code and Strava is opt-in and only pulls runs in. If 8.35a analytics merges, the privacy page must keep this line true.

## D1 and captain mentions, not changed

- The Edge intro says "I'm Billy. I captained Division 1 cross country in college, and I've lifted and run for years."
- The same text appears once in the About popup after setup. A new user now sees the story, then setup, then that popup.

## Kept as is

- **The existing setup still asks for body weight, height, age and sex.** The story adds no questions. The setup was not rebuilt, as asked.
- **Analytics:** there is no analytics module on this branch, so no onboarding_step or intro_skipped events were added. No tracking code was added.

## Tests

- **New test `t835c_intro.py`, 84 checks:**
  - A fresh install sees screen 1. A seeded user and a user with data but no flags never see it.
  - The flag stops a second showing.
  - Next goes forward through the exact words, and the last button opens setup.
  - Swipe, Escape, and Skip on each screen all count as seen.
  - Replay intro changes no saved data.
  - Why I built this matches the story.
  - Backup and restore of the flag work.
  - With no photo there is no image and no frame. A test photo of 93 KB loads.
  - At 390 and 320 there is no sideways scroll and no cut text, targets are 44 px, Next is on screen, and the whole story text shows above the footer.
- **Screenshots** in `tests/browser/out/`: `835c-intro-{1,2,3}-{390,320}.png` and the same names with `-photo`.
- **Updated tests:**
  - `food.js`: the setup blocks stub the intro check.
  - `t828`: it now checks that no tip appears over the intro, and scrolls instantly. This fixed a flake under the taller 8.35b tab bar, where a tip could be placed during a smooth scroll.
- **Full suite:** 1037 browser checks over 23 files, 0 failed. food.js 511, onb.js 138, sets.js 272, 0 failed. compat.js has its 3 known failures.
- **Security review of the diff:** no findings. The story text is set with `textContent`, the photo paths and the link are fixed, the link has `rel=noopener`, and the flag is accepted only as a boolean.

## Skills used

- `anthropic-skills:token-smart-work`
- `design:ux-copy`
- `design:accessibility-review`
- `design-skills:interaction-design`
- `design:design-critique` against `references/today_b.png`. This led to the inset card and the ink Skip pill.
- `engineering:testing-strategy`
- `security-review`
