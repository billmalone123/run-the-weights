#!/bin/sh
# Runs every browser check, then the unit suites. One summary line per file.
# Needs the app served at RTW_URL (default http://localhost:8765/index.html).
cd "$(dirname "$0")"
mkdir -p out
status=0
for f in t8*.py; do
  if python3 "$f" > "out/$f.log" 2>&1; then r=ok; else r=FAILED; status=1; fi
  echo "$f: $(grep -E '[0-9]+ checks, [0-9]+ failed' "out/$f.log" | tail -1) $r"
done
cd ../..
for u in food onb sets compat; do echo "$u.js: $(node $u.js 2>&1 | grep -E '[0-9]+ passed' | tail -1)"; done
exit $status
