"""8.37b setup maxes: per lift, I know my max, I know a weight and reps (Settings estimate, 1 to 10 reps), or Skip for now. lb and kg, 390 and 320."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
FRESH = "localStorage.setItem('monk_onboarded_v1','1');" + SEEN
MAXES = "JSON.parse(localStorage.getItem('monk_mode_maxes_v1')||'{}')"
def wizard(b, W, kg=False):
    ctx, pg, errs = page(b, W, 844, seed=False, init=FRESH + ("localStorage.setItem('monk_weight_unit_v1','kg');" if kg else ''))
    pg.evaluate("onb={};onbSaveDraft();openOnboardingWizard();onbPick('days',4);onbNext()"); pg.wait_for_timeout(300)
    return ctx, pg, errs
def mode(pg, k, label):
    pg.click('#onbBody .onb-lift:nth-of-type(%d) .onb-mode:has-text("%s")' % (['squat', 'bench', 'ohp'].index(k) + 1, label)); pg.wait_for_timeout(200)
def nxt(pg): return pg.evaluate("!onbNextBtn.disabled")
with sync_playwright() as p:
    b = p.chromium.launch()
    for W in [390, 320]:
        ctx, pg, errs = wizard(b, W)
        check('%d: the maxes step is open' % W, pg.evaluate("onb.step") == 'maxes' and pg.evaluate("onbWizard.style.display") == 'flex')
        modes = pg.evaluate("[...document.querySelectorAll('#onbBody .onb-lift')].map(f=>[...f.querySelectorAll('.onb-mode')].map(b=>b.textContent+':'+b.getAttribute('aria-pressed')).join('|'))")
        check('%d: each lift offers the two ways and Skip, I know my max first' % W, modes == ['I know my max:true|I know a weight and reps:false|Skip for now:false'] * 3, modes)
        # Typed max path, unchanged.
        pg.fill('#onb-max-squat', '315'); pg.wait_for_timeout(100)
        check('%d: a typed max is kept as typed' % W, pg.evaluate("onb.squat") == '315' and not nxt(pg))
        # Weight and reps.
        mode(pg, 'bench', 'I know a weight and reps')
        check('%d: weight and reps shows weight, reps and Estimated max' % W, pg.evaluate("[!!document.getElementById('onb-w-bench'),!!document.getElementById('onb-r-bench'),/Estimated max/.test(document.querySelector('#onbBody .onb-lift:nth-of-type(2)').innerText)]") == [True, True, True])
        check('%d: focus moves to the weight field' % W, pg.evaluate("document.activeElement.id") == 'onb-w-bench')
        pg.fill('#onb-w-bench', '185'); pg.fill('#onb-r-bench', '5'); pg.wait_for_timeout(100)
        est = pg.evaluate("document.getElementById('onb-max-bench').value")
        check('%d: 185 for 5 estimates the same as the Settings function' % W, float(est) == pg.evaluate("epleyEstimate(185,5)") == 215, [est, pg.evaluate("epleyEstimate(185,5)")])
        pg.fill('#onb-r-bench', '11'); pg.wait_for_timeout(100)
        msg = pg.evaluate("document.getElementById('onb-msg-bench').textContent")
        check('%d: 11 reps is refused with a plain message' % W, 'Use a set of 1 to 10 reps' in msg and pg.evaluate("document.getElementById('onb-max-bench').value") == '' and not nxt(pg), msg)
        check('%d: the message has no dashes or exclamation marks' % W, not any(c in msg for c in '-–—!'), msg)
        pg.fill('#onb-r-bench', '5'); pg.fill('#onb-max-bench', '220'); pg.wait_for_timeout(100)
        check('%d: the estimate can be edited before going on' % W, pg.evaluate("onb.bench") == '220')
        # Skip.
        mode(pg, 'ohp', 'Skip for now')
        check('%d: a skipped lift lets Next go on' % W, nxt(pg) and 'Skipped' in pg.evaluate("document.querySelector('#onbBody .onb-lift:nth-of-type(3)').innerText"))
        small = pg.evaluate("[...document.querySelectorAll('#onbBody button, #onbBody input')].filter(e=>e.offsetParent).map(e=>{var r=e.getBoundingClientRect();return [e.id||e.textContent,Math.round(r.width),Math.round(r.height)]}).filter(x=>x[1]<44||x[2]<44)")
        check('%d: every control is 44 px or larger' % W, not small, small)
        fit = pg.evaluate("(()=>{var c=document.getElementById('onbWizardCard');return [document.documentElement.scrollWidth<=innerWidth,c.scrollWidth<=c.clientWidth+1,[...document.querySelectorAll('#onbBody .onb-mode')].every(b=>b.scrollWidth<=b.clientWidth+1)]})()")
        check('%d: fits with no sideways scroll or cut labels' % W, all(fit), fit)
        pg.evaluate("document.querySelector('#onbBody .onb-lift:nth-of-type(2)').scrollIntoView({block:'center'})")
        pg.screenshot(path=shot('837b-setup-max-%d.png' % W))
        # Back and forth keeps the choices.
        pg.evaluate("onbNext()"); pg.wait_for_timeout(200); pg.evaluate("onbBack()"); pg.wait_for_timeout(200)
        check('%d: Back keeps the mode, the set and the edited estimate' % W, pg.evaluate("[document.getElementById('onb-w-bench').value,document.getElementById('onb-r-bench').value,document.getElementById('onb-max-bench').value,!!document.getElementById('onb-max-ohp')]") == ['185', '5', '220', False])
        pg.evaluate("onbNext();onbPick('runs',false);onbNext()"); pg.wait_for_timeout(300)
        summ = pg.evaluate("onbBody.innerText")
        check('%d: the summary names the skipped lift' % W, 'Squat 315 lbs' in summ and 'Bench 220 lbs' in summ and 'Shoulder Press skipped' in summ, summ[:200])
        pg.evaluate("onbNext()"); pg.wait_for_timeout(600)
        mx = pg.evaluate(MAXES)
        check('%d: saved maxes: 315, 220, and no key for the skipped lift' % W, mx == {'squat': 315, 'bench': 220}, mx)
        check('%d: no page errors' % W, not errs, errs); ctx.close()
    # The typed path with all three, as before.
    ctx, pg, errs = wizard(b, 390)
    for k, v in [('squat', '405'), ('bench', '315'), ('ohp', '90')]: pg.fill('#onb-max-' + k, v)
    pg.evaluate("onbNext();onbPick('runs',false);onbNext();onbNext()"); pg.wait_for_timeout(600)
    check('typed maxes for all three save exactly as before', pg.evaluate(MAXES) == {'squat': 405, 'bench': 315, 'ohp': 90}, pg.evaluate(MAXES))
    # Settings Edit your maxes still estimates the same way.
    pg.evaluate("openMaxesModal();setMaxesMode('reps')"); pg.wait_for_timeout(200)
    pg.fill('#reps-weight-bench', '185'); pg.fill('#reps-count-bench', '5'); pg.wait_for_timeout(200)
    check('Settings estimate gives the same number for the same set', pg.evaluate("document.getElementById('max-bench').value") == '215', pg.evaluate("document.getElementById('max-bench').value"))
    check('typed path: no page errors', not errs, errs); ctx.close()
    # kg.
    for W in [390, 320]:
        ctx, pg, errs = wizard(b, W, kg=True)
        mode(pg, 'squat', 'I know a weight and reps')
        lab = pg.evaluate("document.querySelector('#onbBody .onb-lift').innerText")
        check('%d kg: labels say kg' % W, 'Weight, kg' in lab and 'Estimated max, kg' in lab, lab)
        pg.fill('#onb-w-squat', '100'); pg.fill('#onb-r-squat', '5'); pg.wait_for_timeout(100)
        shown = pg.evaluate("document.getElementById('onb-max-squat').getAttribute('data-wu-shown')")
        lb = pg.evaluate("epleyEstimate(100*WU_LB_PER_KG,5)")
        want = round(round(lb / 2.20462262 * 10) / 10 / 2.5) * 2.5
        check('%d kg: 100 kg for 5 shows the Settings estimate on the 2.5 kg step' % W, shown is not None and abs(float(shown) - want) < 0.01 and abs(float(shown) / 2.5 - round(float(shown) / 2.5)) < 1e-9, [shown, want, lb])
        pg.screenshot(path=shot('837b-setup-max-kg-%d.png' % W))
        pg.fill('#onb-max-bench', '100'); mode(pg, 'ohp', 'Skip for now')
        pg.evaluate("onbNext();onbPick('runs',false);onbNext();onbNext()"); pg.wait_for_timeout(600)
        mx = pg.evaluate(MAXES)
        check('%d kg: maxes are stored in lb as before' % W, abs(mx.get('squat', 0) - want * 2.20462262) < 0.05 and abs(mx.get('bench', 0) - 220.46) < 0.05 and 'ohp' not in mx, mx)
        check('%d kg: no page errors' % W, not errs, errs); ctx.close()
    b.close()
sys.exit(1 if done() else 0)
