# Branch tracker

Updated 2026-11-24, after the 8.39.2 install-notice preview. Live site: runtheweights.vercel.app (master). Previews sit behind Vercel login.

| Branch | Commit | Build label | Cache | Status | Preview URL |
|---|---|---|---|---|---|
| master | 6611d66 | 8.40.1 | v125 | Live, matches origin. Fast forwarded from block-rollover | https://runtheweights.vercel.app |
| block-rollover | 6611d66 | 8.40.1 | v125 | Merged into master (fast forward). Has master 8.39, the 8.39.1 hotfix, and the block trigger on the date rule | https://runtheweights-85xj8am5b-billmalone123s-projects.vercel.app |
| install-notice | 5d3064e | 8.39.2 | v126 | Preview only, not merged. Cut from hotfix-today-state. iPhone browser tab gets Add to Home Screen first, Coming from Safari card on Today in an empty Home Screen app, Moving to the Home Screen in Settings | https://runtheweights-nb0e9sdw7-billmalone123s-projects.vercel.app |
| hotfix-today-state | 862fb0b | 8.39.1 | v124 | Merged into master through block-rollover. Today state by date, Current week, Do this workout today, Reset this week | https://runtheweights-4yx7dv6t4-billmalone123s-projects.vercel.app |
| run-base | 03404ba | 8.39 | v122 | Merged into master | https://runtheweights-asltsgv7s-billmalone123s-projects.vercel.app |
| setup-max-reps | 53dd18d | 8.37d | v120 | Merged into master | https://runtheweights-63rqawkv0-billmalone123s-projects.vercel.app |
| intro-story | ea65706 | 8.37c | v119 | Merged into master | https://runtheweights-dqrmj1x85-billmalone123s-projects.vercel.app |
| week-lookahead | 17c1431 | 8.37 | v118 | Merged into master | https://runtheweights-pxuhi540e-billmalone123s-projects.vercel.app |
| 8.35a-analytics | 29e39a9 | 8.34 era | | Pushed so it is not only local | https://runtheweights-hjoqbnwlf-billmalone123s-projects.vercel.app |
| phase3-today-options | bc8266b | Phase 3 preview | | Pushed so it is not only local | None. Vercel made no deployment for this commit |
| fix-daylog | 8bfde59 | 8.35b | | Already on origin | |
| branch-tracker | this commit | | | This file, pushed so it is on GitHub. Not a build | |

## Notes

- 8.40 block-rollover preview before the hotfix merge (4f90d53) was runtheweights-rlxb7s7yr.
- master went from 8.39 (03404ba) to 8.40.1 (6611d66) on 2026-11-24, by fast forward from block-rollover, at the owner's request.

- block-rollover now includes master 8.39. Its block done card follows the calendar week rule. The earlier 8.38 preview (c8b8ac3) was runtheweights-1brlg2tw8.
- Earlier previews: intro-story at 898b7e1 was runtheweights-ovstjcpdp, and 8.37b at 91ec51e was runtheweights-k28xxku8a.
