# Branch tracker

Updated 2026-11-23. Live site: runtheweights.vercel.app (master). Previews sit behind Vercel login.

| Branch | Commit | Build label | Cache | Status | Preview URL |
|---|---|---|---|---|---|
| master | 53dd18d | 8.37d | v120 | Live, matches origin | https://runtheweights.vercel.app |
| block-rollover | c8b8ac3 | 8.38 | v121 | Preview only, not merged | https://runtheweights-1brlg2tw8-billmalone123s-projects.vercel.app |
| run-base | 03404ba | 8.39 | v122 | Preview only, not merged | https://runtheweights-asltsgv7s-billmalone123s-projects.vercel.app |
| setup-max-reps | 53dd18d | 8.37d | v120 | Merged into master | https://runtheweights-63rqawkv0-billmalone123s-projects.vercel.app |
| intro-story | ea65706 | 8.37c | v119 | Merged into master | https://runtheweights-dqrmj1x85-billmalone123s-projects.vercel.app |
| week-lookahead | 17c1431 | 8.37 | v118 | Merged into master | https://runtheweights-pxuhi540e-billmalone123s-projects.vercel.app |
| 8.35a-analytics | 29e39a9 | 8.34 era | | Pushed so it is not only local | https://runtheweights-hjoqbnwlf-billmalone123s-projects.vercel.app |
| phase3-today-options | bc8266b | Phase 3 preview | | Pushed so it is not only local | None. Vercel made no deployment for this commit |
| fix-daylog | 8bfde59 | 8.35b | | Already on origin | |
| branch-tracker | local | | | This file. Committed locally, not pushed | |

## Notes

- block-rollover and run-base were each cut from master 53dd18d. Neither includes the other.
- run-base carries the general calendar week rule (plan weeks follow the calendar for every user) and Today first. block-rollover was built before that rule. Whichever merges second needs the other's changes merged in, plus a fresh test run.
- Earlier previews: intro-story at 898b7e1 was runtheweights-ovstjcpdp, and 8.37b at 91ec51e was runtheweights-k28xxku8a.
