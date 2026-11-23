"""8.35b Part B: Short routes to the time picker, the check makes it the day's workout, Restore and Normal bring the plan back. Three plans, reloads."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
PLANS = [('upper and lower', ''), ('arnold', "setSplit('arnold')"), ('advanced runner', "setAdvanced(true);setRunning(true)")]
STORE = "JSON.stringify([localStorage.getItem('monk_sessions_v1'),localStorage.getItem('monk_day_added_v1')])"
CLOSE = "document.querySelectorAll('.settings-modal-overlay').forEach(m=>{if(m.id!=='dayTakeover')m.style.display='none'})"
def ids(pg, d): return pg.evaluate("paList('%s').map(e=>e.id)" % d)
def log_on(pg, ex, w, r):
    pg.evaluate("PA.ex='%s';PA.slot=null;PA.key=null;renderPlanActive()" % ex)
    pg.evaluate("PA.wLb=%s;PA.r=%s" % (w, r)); pg.click('#paLogBtn'); pg.wait_for_timeout(300)
    pg.evaluate("dismissTimer&&dismissTimer();document.querySelectorAll('.rest-modal-overlay').forEach(m=>m.classList.remove('visible'))")
def tab(pg): return pg.evaluate("document.body.dataset.tab")
def reload(pg):
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate(CLOSE); go(pg, 'today')
def fresh(b, setup):
    ctx, pg, errs = page(b, 390, 844)
    if setup: pg.evaluate(setup); pg.reload(); pg.wait_for_timeout(1500); pg.evaluate(CLOSE)
    go(pg, 'today'); return ctx, pg, errs, pg.evaluate("todayDayId()")
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, setup in PLANS:
        ctx, pg, errs, D = fresh(b, setup)
        before = pg.evaluate(STORE)
        pg.click('#tbAdj .day-adj-btn:has-text("Short")'); pg.wait_for_timeout(400)
        check(name + ': Short on Today opens the time picker', tab(pg) == 'quicklog' and pg.evaluate("quicklogSection.classList.contains('ql-short')"))
        check(name + ': the picker offers 20, 30, 45 and 60', pg.evaluate("[...qlTimes.querySelectorAll('button')].map(b=>b.textContent)") == ['20 min', '30 min', '45 min', '60 min'])
        check(name + ': opening the picker changes nothing', pg.evaluate(STORE) == before and not pg.evaluate("sessionIsShort('%s')" % D))
        own = pg.evaluate("programmedDayExercises('%s').map(e=>e.id)" % D)
        for m in [20, 30, 45, 60]:
            r = pg.evaluate("(()=>{var b=previewSession('%s','time',%d);return {n:b.list.length,hi:b.est.hi,ids:b.list.map(e=>e.id),first:b.list[0]&&b.list[0].kind}})()" % (D, m))
            check('%s: %d min fits' % (name, m), r['n'] > 0 and r['hi'] <= m, r)
            check('%s: %d min keeps the day\'s focus, main lift first' % (name, m), all(i in own for i in r['ids']) and r['first'] == 'compound', r)
        pg.click('#qlTimes button:has-text("30 min")'); pg.wait_for_timeout(300)
        prop = pg.evaluate("previewSession('%s','time',30).list.map(e=>e.id)" % D)
        check(name + ': the proposal shows the list and the time', pg.evaluate("qlToday.querySelectorAll('.session-list li').length") == len(prop) and 'About' in pg.evaluate("qlToday.innerText"))
        acts = pg.evaluate("[...qlToday.querySelectorAll('button')].map(b=>{var r=b.getBoundingClientRect();return [b.textContent,Math.round(r.height),Math.round(r.width)]})")
        check(name + ': check, Back and Different workout, 44 px', [a[0] for a in acts] == ['Use this workout', 'Back', 'Different workout'] and all(a[1] >= 44 and a[2] >= 44 for a in acts), acts)
        pg.click('#qlToday button:has-text("Different workout")'); pg.wait_for_timeout(300)
        check(name + ': Different workout shows the other workouts', pg.evaluate("getComputedStyle(qlOthers).display!=='none'&&qlOthers.children.length>0"))
        pg.click('#qlToday button:has-text("Back")'); pg.wait_for_timeout(400)
        check(name + ': Back returns to Today with nothing changed', tab(pg) == 'today' and pg.evaluate(STORE) == before and not pg.evaluate("sessionIsShort('%s')" % D))
        # Short from the Lift header, then the check.
        go(pg, 'training'); pg.evaluate("switchDay('%s');PA.day='%s';renderPlanActive()" % (D, D)); pg.wait_for_timeout(300)
        pg.click('#planActive .day-adj-btn:has-text("Short")'); pg.wait_for_timeout(400)
        check(name + ': Short in the Lift header opens the time picker', tab(pg) == 'quicklog' and pg.evaluate("quicklogSection.classList.contains('ql-short')"))
        pg.click('#qlTimes button:has-text("30 min")'); pg.wait_for_timeout(300)
        pg.click('#qlToday .ql-ok'); pg.wait_for_timeout(500)
        check(name + ': the check returns to Today', tab(pg) == 'today')
        check(name + ': Today shows the short workout', pg.evaluate("tbWork.querySelector('.tb-day').textContent").startswith('Short') and 'Planned workout:' in pg.evaluate("tbWork.innerText"))
        pg.click('.tb-start'); pg.wait_for_timeout(500)
        check(name + ': START opens Lift with that workout', tab(pg) == 'training' and ids(pg, D) == prop, [ids(pg, D), prop])
        log_on(pg, prop[0], 95, 8); s1 = pg.evaluate(STORE)
        reload(pg)
        check(name + ': Short holds after a reload', pg.evaluate("sessionIsShort('%s')" % D) and pg.evaluate("tbWork.querySelector('.restore-btn')") is not None)
        # Restore brings the plan back and keeps the set.
        pg.click('#tbWork .restore-btn'); pg.wait_for_timeout(400)
        check(name + ': Restore brings the planned workout back', not pg.evaluate("sessionIsShort('%s')" % D) and pg.evaluate(STORE) == s1)
        check(name + ': the logged set is still there', pg.evaluate("slotLogged(EX_BY_ID['%s'],'s1')" % prop[0]))
        reload(pg)
        check(name + ': Restore holds after a reload', not pg.evaluate("sessionIsShort('%s')" % D) and pg.evaluate(STORE) == s1)
        # 8.37: Normal is gone; Restore does it again after a takeover.
        pg.evaluate("openShortPicker('%s')" % D); pg.wait_for_timeout(300); pg.click('#qlToday .ql-ok'); pg.wait_for_timeout(500)
        check(name + ': a day with sets logged asks before Short', pg.evaluate("dayTakeover.style.display") == 'flex' and 'Your logged sets stay.' in pg.evaluate("dayTakeoverMsg.textContent"))
        pg.click('#dayTakeoverYes'); pg.wait_for_timeout(500)
        check(name + ': after Switch today is short, not the next day', pg.evaluate("sessionIsShort('%s')" % D) and pg.evaluate("todayDayId()") == D)
        reload(pg)
        check(name + ': the switch holds after a reload', pg.evaluate("sessionIsShort('%s')" % D))
        pg.click('#tbWork .restore-btn'); pg.wait_for_timeout(400)
        check(name + ': Restore after the takeover brings the plan back with no data changed', not pg.evaluate("sessionIsShort('%s')" % D) and pg.evaluate(STORE) == s1)
        reload(pg)
        check(name + ': that Restore holds after a reload', not pg.evaluate("sessionIsShort('%s')" % D))
        # Next week has no trace of it.
        pg.evaluate("openShortPicker('%s')" % D); pg.wait_for_timeout(300); pg.click('#qlToday .ql-ok'); pg.wait_for_timeout(500)
        nxt = pg.evaluate("(()=>{var w=currentTrainWeek+1;return [isShortDay('%s',w),!!quickFor('%s',w),boxChoice('%s',w)===undefined,buildSession('%s',w).list.length===programmedDayExercises('%s').length||buildSession('%s',w).list.length>=paList('%s').length]})()" % ((D,) * 7))
        check(name + ': next week the same day is the normal plan', nxt[:3] == [False, False, True], nxt)
        check(name + ': no page errors', not errs, errs); ctx.close()
    # Weights prefill from the last logged weight for that exercise, in any workout.
    ctx, pg, errs, D = fresh(b, '')
    other = pg.evaluate("splitDayIds().filter(d=>d!=='%s')[0]" % D)
    pg.evaluate("_qlDay='%s';startQuickNow('upper','%s')" % (other, other)); pg.wait_for_timeout(400)
    q = pg.evaluate("quickFor('%s',currentTrainWeek)" % other); ex = q['ids'][1]
    pg.evaluate("quickLogSet('%s',152.5,6,null,'')" % ex)
    pg.evaluate("goTab('training');switchDay('%s');PA.day='%s';PA.ex='%s';PA.slot=null;PA.key=null;renderPlanActive()" % (other, other, ex))
    check('weights prefill from the last logged weight in another workout', abs(pg.evaluate("PA.wLb") - 152.5) < 0.01, pg.evaluate("PA.wLb"))
    check('prefill: no page errors', not errs, errs); ctx.close()
sys.exit(1 if done() else 0)
