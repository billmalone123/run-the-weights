"""8.35b Parts C and D, updated for 8.37: bottom bar for both Food flag states, Lift rename, Change workout entry points, no menu, title not interactive, fit at 390 and 320, screenshots."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
#  8.39: Today opens today's planned workout. These checks need a day Short
#  shortens (Upper A); Upper B is not shortened, so the clock sits on Monday.
import common, datetime; common.T0 = datetime.datetime(2026, 11, 16, 10, 0, 0)
from playwright.sync_api import sync_playwright
CLOSE = "document.querySelectorAll('.settings-modal-overlay').forEach(m=>{if(m.id!=='dayTakeover')m.style.display='none'})"
BAR = "[...document.querySelectorAll('#tabbar .tabbar-btn')].filter(b=>b.offsetParent).map(b=>{var s=b.querySelector('span'),r=b.getBoundingClientRect();return {t:b.dataset.tab,l:s.innerText.replace(/\\n/g,' '),w:Math.round(r.width),h:Math.round(r.height),cut:s.scrollWidth>s.clientWidth+1||s.scrollHeight>s.clientHeight+1||r.right>innerWidth}})"
CLEAR = """(id)=>{var t=document.getElementById('tab-'+id);scrollTo({top:document.documentElement.scrollHeight,behavior:'instant'});
  var bar=document.getElementById('tabbar').getBoundingClientRect().top, max=0;
  t.querySelectorAll('*').forEach(e=>{if(!e.offsetParent||e.children.length)return;var r=e.getBoundingClientRect();if(r.height&&r.bottom>max)max=r.bottom});
  return [Math.round(max),Math.round(bar)]}"""
def tab(pg): return pg.evaluate("document.body.dataset.tab")
with sync_playwright() as p:
    b = p.chromium.launch()
    for W in [390, 320]:
        ctx, pg, errs = page(b, W, 844); go(pg, 'today')
        bar = pg.evaluate(BAR)
        check('%d: bar while Food is locked is Today, Lift, Run, Progress' % W, [x['l'] for x in bar] == ['Today', 'Lift', 'Run', 'Progress'], bar)
        check('%d: no label cut, 44 px targets' % W, all(not x['cut'] and x['w'] >= 44 and x['h'] >= 44 for x in bar), bar)
        pg.screenshot(path=shot('835b-bar-%d.png' % W), clip={'x': 0, 'y': 844 - 90, 'width': W, 'height': 90})
        pg.evaluate("setRunning(false)"); go(pg, 'today')
        check('%d: Run is shown with running off' % W, 'running' in [x['t'] for x in pg.evaluate(BAR)])
        pg.click('#tabbar [data-tab=running]'); pg.wait_for_timeout(400)
        off = pg.evaluate("(()=>{var b=runOff.querySelector('button').getBoundingClientRect();return [getComputedStyle(runOff).display,Math.round(b.height),runHome.offsetParent===null]})()")
        check('%d: Run with running off says how to turn it on' % W, off[0] == 'block' and off[1] >= 44 and off[2], off)
        pg.click('#runOff button'); pg.wait_for_timeout(400)
        check('%d: Turn on running shows the Run page' % W, pg.evaluate("runningEnabled&&tab_running_ok()" if False else "runningEnabled&&getComputedStyle(runOff).display==='none'&&!!runHome.offsetParent"))
        pg.evaluate(FOOD_ON + ";document.querySelectorAll('.tabbar-btn').forEach(b=>b.style.display='')"); go(pg, 'today')
        bar2 = pg.evaluate(BAR)
        check('%d: bar with Food on is Today, Lift, Run, Food, Progress' % W, [x['l'] for x in bar2] == ['Today', 'Lift', 'Run', 'Food', 'Progress'] and all(not x['cut'] and x['h'] >= 44 for x in bar2), bar2)
        pg.evaluate("FOOD_ENABLED=false;document.documentElement.classList.add('food-off')"); go(pg, 'today')
        # Fit and clearance on every tab.
        for t in ['today', 'training', 'running', 'quicklog', 'calendar']:
            go(pg, t)
            ow = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
            check('%d %s: no sideways overflow' % (W, t), ow <= 0, ow)
            c = pg.evaluate(CLEAR, t)
            check('%d %s: content clears the floating bar' % (W, t), c[0] <= c[1], c)
        go(pg, 'today')
        # 8.37: Short and Change workout replace the Quick Log button under the card.
        q = pg.evaluate("[...document.querySelectorAll('#tbAdj .day-adj-btn')].map(e=>{var cs=getComputedStyle(e),r=e.getBoundingClientRect();return {txt:e.innerText,h:Math.round(r.height),border:cs.borderTopColor,bg:cs.backgroundColor,below:r.top>=tbWork.getBoundingClientRect().bottom}})")
        check('%d: Today has Short and Change workout under the card' % W, [x['txt'] for x in q] == ['Short', 'Change workout'] and all(x['below'] for x in q), q)
        check('%d: they are ink outlines, 44 px, never persimmon' % W, all(x['h'] >= 44 and x['border'] == 'rgb(20, 20, 20)' and x['bg'] in ('rgba(0, 0, 0, 0)', 'transparent') for x in q), q)
        pg.evaluate("document.querySelector('#tbAdj .day-adj-btn').focus()"); pg.wait_for_timeout(200)
        cov = pg.evaluate("[Math.round(document.querySelector('#tbAdj .day-adj').getBoundingClientRect().bottom),Math.round(tabbar.getBoundingClientRect().top)]")
        check('%d: the bar does not cover the buttons once they are in view' % W, cov[0] <= cov[1], cov)
        pg.screenshot(path=shot('835b-today-%d.png' % W), full_page=True)
        check('%d: no page errors' % W, not errs, errs); ctx.close()
    # Quick Log entry points and the way back.
    ctx, pg, errs = page(b, 390, 844)
    # 8.37: the old Quick Log ways in are one Change workout sheet on Today and Lift.
    for name, start, sel in [('Today', 'today', '#tbAdj .day-adj-btn:has-text("Change workout")'),
                             ('Lift', 'training', '#planActive .day-adj-btn:has-text("Change workout")')]:
        go(pg, start); pg.click(sel); pg.wait_for_timeout(300)
        pg.click('#cwSheet .cw-opt >> nth=0'); pg.wait_for_timeout(500)
        check('%s: Change workout, Pick another workout opens the workout screen' % name, tab(pg) == 'quicklog' and pg.evaluate("document.getElementById('tab-quicklog').style.display") == 'block')
        lit = pg.evaluate("(document.querySelector('.tabbar-btn.current')||{}).dataset")
        check('%s: the tab it came from stays lit' % name, lit and lit.get('tab') == start, lit)
        pg.click('#qlToday .ql-back'); pg.wait_for_timeout(400)
        check('%s: Back returns to %s' % (name, start), tab(pg) == start, tab(pg))
    go(pg, 'today'); pg.click('#tbAdj .day-adj-btn:has-text("Change workout")'); pg.wait_for_timeout(300); pg.click('#cwSheet .cw-opt >> nth=0'); pg.wait_for_timeout(400)
    pg.evaluate("_qlOpen='push';renderQuickLog()"); pg.click('#qlOthers .today-start'); pg.wait_for_timeout(500)
    check('picking a workout lands on Today showing it', tab(pg) == 'today' and pg.evaluate("tbWork.querySelector('.tb-day').textContent") == 'Push')
    check('no logo menu anywhere', pg.evaluate("!document.querySelector('#navMenu,[role=menu],[aria-haspopup=menu]')"))
    daily = pg.evaluate("['#tbAdj .day-adj-btn','#tbWork .tb-start','#navGear'].map(s=>!!(document.querySelector(s)||{}).offsetParent)")
    check('daily actions are on screen, not in a dropdown', all(daily), daily)
    go(pg, 'training'); pg.evaluate("renderPlanActive()")
    ti = pg.evaluate("(()=>{var t=document.querySelector('.pa-title');return [t.tagName,t.closest('button,a,[onclick],[role=button]')===null,t.getAttribute('onclick'),getComputedStyle(t).cursor,t.tabIndex]})()")
    check('the workout title on Lift is a plain label', ti[0] == 'H2' and ti[1] and ti[2] is None and ti[3] != 'pointer' and ti[4] < 0, ti)
    check('Lift shows the day strip to switch days', pg.evaluate("document.querySelectorAll('#weekGlance .wg-day').length") == 7)
    hero = pg.evaluate("heroFor ? (heroFor('training')||{}).w : null") if pg.evaluate("typeof heroFor==='function'") else 'Lift'
    words = pg.evaluate("document.body.innerText")
    check('no Plan tab or Plan screen wording on screen', not any(x in words for x in ['Plan tab', 'Plan screen', 'Back to Plan', 'Go to Plan']))
    check('nav: no page errors', not errs, errs); ctx.close()
    # Screenshots of the flow at 390 and 320.
    for W in [390, 320]:
        ctx, pg, errs = page(b, W, 844); go(pg, 'today'); D = pg.evaluate("todayDayId()")
        pg.evaluate("openShortPicker('%s')" % D); pg.wait_for_timeout(400)
        pg.screenshot(path=shot('835b-time-picker-%d.png' % W))
        pg.click('#qlTimes button:has-text("30 min")'); pg.wait_for_timeout(300)
        pg.evaluate("qlToday.scrollIntoView({block:'start'})"); pg.wait_for_timeout(200)
        pg.screenshot(path=shot('835b-proposed-%d.png' % W))
        pg.click('#qlToday .ql-ok'); pg.wait_for_timeout(500); pg.click('.tb-start'); pg.wait_for_timeout(500)
        pg.evaluate("scrollTo(0,0)"); pg.screenshot(path=shot('835b-lift-short-%d.png' % W))
        ex = pg.evaluate("paList('%s')[0].id" % D)
        pg.evaluate("PA.ex='%s';PA.slot=null;PA.key=null;renderPlanActive();PA.wLb=100;PA.r=8" % ex); pg.click('#paLogBtn'); pg.wait_for_timeout(300)
        pg.evaluate("dismissTimer&&dismissTimer();document.querySelectorAll('.rest-modal-overlay').forEach(m=>m.classList.remove('visible'))")
        pg.evaluate("setSessionLength('%s','full')" % D)
        pg.evaluate("openQuickLog(null,'%s');_qlOpen='full';renderQuickLog()" % D); pg.click('#qlOthers .today-start'); pg.wait_for_timeout(400)
        m = pg.evaluate("[dayTakeover.style.display,Math.round(dayTakeoverYes.getBoundingClientRect().height),Math.round(dayTakeover.querySelector('.settings-cancel-btn').getBoundingClientRect().height),document.activeElement.id]")
        check('%d: the confirmation shows with 44 px buttons and focus on Switch' % W, m[0] == 'flex' and m[1] >= 44 and m[2] >= 44 and m[3] == 'dayTakeoverYes', m)
        pg.screenshot(path=shot('835b-confirm-%d.png' % W))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        check('%d: Escape keeps the planned workout' % W, pg.evaluate("dayTakeover.style.display") == 'none' and not pg.evaluate("quickFor('%s',currentTrainWeek)" % D))
        check('%d shots: no page errors' % W, not errs, errs); ctx.close()
sys.exit(1 if done() else 0)
