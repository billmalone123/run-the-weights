"""Shared helpers for the browser checks. See tests/README.md.

RTW_URL   page to test (default http://localhost:8765/index.html)
RTW_SHOTS folder for screenshots (default tests/browser/out, not committed)
RTW_UPDATE_BASELINES=1 rewrites the files in baselines/ from the build under test.
"""
import json, datetime, os
HERE = os.path.dirname(os.path.abspath(__file__))
URL = os.environ.get('RTW_URL', 'http://localhost:8765/index.html')
ORIGIN = URL.split('/index.html')[0] + '/'
SHOTS = os.environ.get('RTW_SHOTS', os.path.join(HERE, 'out'))
os.makedirs(SHOTS, exist_ok=True)
def shot(name): return os.path.join(SHOTS, name)
SEED = '\n'.join(l for l in open(os.path.join(HERE, 'seed.js')).read().splitlines() if not l.startswith('//'))
GAPFN = open(os.path.join(HERE, 'gapfn.js')).read()
T0 = datetime.datetime(2026, 11, 19, 10, 0, 0)
RES = []
def check(n, ok, d=''):
    RES.append((n, bool(ok), str(d)[:220])); print(('PASS ' if ok else 'FAIL ') + n + ('  [' + str(d)[:220] + ']' if d != '' else ''))
def baseline(name, value):
    """Compare a value with the copy saved in baselines/<name>.json. The
    first run, or RTW_UPDATE_BASELINES=1, saves it instead."""
    p = os.path.join(HERE, 'baselines', name + '.json')
    if os.environ.get('RTW_UPDATE_BASELINES') == '1' or not os.path.exists(p):
        json.dump(value, open(p, 'w'), indent=1); return value
    return json.load(open(p))
def done():
    n = sum(1 for r in RES if not r[1]); print('\n%d checks, %d failed' % (len(RES), n)); return n
SEEN = "localStorage.setItem('monk_tips_seen_v1',JSON.stringify({v:1,seen:{today:1,plan:1,lnote:1,wnote:1,quicklog:1,progress:1,run:1,food:1,style:1,menu:1,body:1}}));"
INIT = "localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');" + SEEN
def page(b, w=360, h=700, seed=True, init=INIT, url=URL, clock=True):
    ctx = b.new_context(viewport={'width': w, 'height': h}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    if clock: pg.clock.install(time=T0)
    pg.add_init_script(init)
    pg.goto(url); pg.wait_for_timeout(900)
    if seed: pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    return ctx, pg, errs
def go(pg, t): pg.evaluate("goTab('%s');scrollTo(0,0)" % t); pg.wait_for_timeout(550)
