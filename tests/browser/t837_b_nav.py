"""8.37 Part B: no Quick Log tab, the bar is Today, Lift, Run, Progress (Food fifth when on), gear on four tabs, logo goes to Today,
no dropdown anywhere, Week review in Progress, The Edge and Why I built this in Settings, Short and Change workout on Today and Lift,
the Change workout sheet, no Quick Log words left, and a round trip that leaves storage as it was."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
CLOSE = "document.querySelectorAll('.settings-modal-overlay').forEach(m=>{if(m.id!=='dayTakeover')m.style.display='none'})"
BAR = "[...document.querySelectorAll('#tabbar .tabbar-btn')].filter(b=>b.offsetParent).map(b=>{var s=b.querySelector('span'),r=b.getBoundingClientRect();return {t:b.dataset.tab,l:s.innerText.replace(/\\n/g,' '),w:Math.round(r.width),h:Math.round(r.height),cut:s.scrollWidth>s.clientWidth+1||s.scrollHeight>s.clientHeight+1}})"
HEAD = """()=>{var g=e=>{var x=document.getElementById(e);if(!x||!x.offsetParent)return null;var r=x.getBoundingClientRect();return [r.left,r.right,r.top,r.bottom,r.width,r.height]};
  return {logo:g('navLogo'),streak:g('navStreak'),gear:g('navGear'),vw:innerWidth}}"""
NAVKEYS = ['monk_mode_last_tab_v1', 'monk_mode_last_day_v1', 'monk_autopick_date_v1', 'monk_tips_seen_v1']
ALL = "JSON.stringify(Object.keys(localStorage).sort().filter(k=>%s.indexOf(k)===-1).map(k=>[k,localStorage.getItem(k)]))" % json.dumps(NAVKEYS)
TABS = ['today', 'training', 'running', 'calendar']
def tab(pg): return pg.evaluate("document.body.dataset.tab")
def over(a, b): return a and b and a[0] < b[1] - 0.5 and b[0] < a[1] - 0.5
with sync_playwright() as p:
    b = p.chromium.launch()
    for W in [390, 320]:
        ctx, pg, errs = page(b, W, 844); go(pg, 'today')
        bar = pg.evaluate(BAR)
        check('%d: bar while Food is locked is Today, Lift, Run, Progress' % W, [x['l'] for x in bar] == ['Today', 'Lift', 'Run', 'Progress'], bar)
        check('%d: four tabs, no label cut, 44 px' % W, all(not x['cut'] and x['w'] >= 44 and x['h'] >= 44 for x in bar), bar)
        check('%d: no Quick Log tab' % W, pg.evaluate("!document.querySelector('#tabbar [data-tab=quicklog]')"))
        pg.screenshot(path=shot('837-bar-%d.png' % W), clip={'x': 0, 'y': 844 - 90, 'width': W, 'height': 90})
        pg.evaluate(FOOD_ON); go(pg, 'today')
        bar2 = pg.evaluate(BAR)
        check('%d: with Food on the bar is Today, Lift, Run, Food, Progress' % W, [x['l'] for x in bar2] == ['Today', 'Lift', 'Run', 'Food', 'Progress'] and all(not x['cut'] and x['w'] >= 44 and x['h'] >= 44 for x in bar2), bar2)
        pg.screenshot(path=shot('837-bar-food-%d.png' % W), clip={'x': 0, 'y': 844 - 90, 'width': W, 'height': 90})
        pg.evaluate("FOOD_ENABLED=false;document.documentElement.classList.add('food-off')"); go(pg, 'today')
        for t in TABS:
            go(pg, t)
            h = pg.evaluate(HEAD)
            g = h['gear']
            check('%d %s: gear in the top right, 44 px, labelled Settings' % (W, t), g and g[4] >= 44 and g[5] >= 44 and g[1] <= h['vw'] and g[1] >= h['vw'] - 24 and pg.evaluate("navGear.getAttribute('aria-label')") == 'Settings', g)
            check('%d %s: gear is ink' % (W, t), pg.evaluate("getComputedStyle(navGear).color") == 'rgb(20, 20, 20)', pg.evaluate("getComputedStyle(navGear).color"))
            ok = h['logo'] and h['logo'][0] >= 0 and not over(h['logo'], h['streak']) and not over(h['logo'], h['gear']) and not over(h['streak'], h['gear'])
            check('%d %s: header fits with no overlap' % (W, t), ok, h)
            pg.click('#navGear'); pg.wait_for_timeout(300)
            check('%d %s: the gear opens Settings in one tap' % (W, t), pg.evaluate("settingsModal.style.display") == 'flex')
            pg.click('#settingsModal .settings-cancel-btn'); pg.wait_for_timeout(300)
            check('%d %s: closing Settings returns to the same tab' % (W, t), tab(pg) == t and pg.evaluate("settingsModal.style.display") == 'none', tab(pg))
            ow = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
            check('%d %s: no sideways overflow' % (W, t), ow <= 0, ow)
        go(pg, 'calendar'); pg.click('#navLogo'); pg.wait_for_timeout(400)
        check('%d: the logo goes to Today and opens no menu' % W, tab(pg) == 'today' and pg.evaluate("!document.querySelector('.navmenu.on,#navMenu,[role=menu],[aria-haspopup=menu],[aria-haspopup=listbox]')"))
        check('%d: the logo is not a menu button' % W, pg.evaluate("navLogo.getAttribute('aria-haspopup')") is None and 'Today' in pg.evaluate("navLogo.getAttribute('aria-label')"))
        pg.screenshot(path=shot('837-header-%d.png' % W), clip={'x': 0, 'y': 0, 'width': W, 'height': 60})
        # Week review from Progress.
        go(pg, 'calendar')
        wr = pg.evaluate("(()=>{var b=document.querySelector('#progressHome .prog-review'),r=b.getBoundingClientRect();return [b.innerText.split('\\n')[0],Math.round(r.height),Math.round(r.top),innerHeight]})()")
        check('%d: Week review is a visible button near the top of Progress' % W, wr[0] == 'Week review' and wr[1] >= 44 and wr[2] < wr[3] * 0.4, wr)
        pg.click('#progressHome .prog-review'); pg.wait_for_timeout(400)
        check('%d: Week review opens' % W, tab(pg) == 'info' and pg.evaluate("document.getElementById('sec-overview').style.display") == 'block')
        # The Edge and Why I built this in Settings, near the top.
        go(pg, 'today'); pg.click('#navGear'); pg.wait_for_timeout(300)
        s = pg.evaluate("(()=>{var a=[...document.querySelectorAll('#settingsModal .settings-about button')],m=document.getElementById('maxesDisplay').getBoundingClientRect().top;return a.map(b=>{var r=b.getBoundingClientRect();return [b.textContent,Math.round(r.height),r.top<m]})})()")
        check('%d: Settings starts with The Edge and Why I built this' % W, [x[0] for x in s] == ['The Edge', 'Why I built this'] and all(x[1] >= 44 and x[2] for x in s), s)
        pg.click('#settingsModal .settings-about button:has-text("The Edge")'); pg.wait_for_timeout(400)
        check('%d: The Edge opens from Settings' % W, tab(pg) == 'info' and pg.evaluate("document.getElementById('sec-edge').style.display") == 'block' and pg.evaluate("settingsModal.style.display") == 'none')
        go(pg, 'today'); pg.click('#navGear'); pg.wait_for_timeout(300)
        pg.click('#settingsModal .settings-about button:has-text("Why I built this")'); pg.wait_for_timeout(400)
        check('%d: Why I built this opens its page' % W, pg.evaluate("(()=>{var e=document.getElementById('sec-why'),r=e.getBoundingClientRect();return e.style.display==='block'&&r.top<innerHeight&&r.bottom>0})()"))
        # Short and Change workout, visible, on Today and Lift.
        for t, host in [('today', '#tbAdj'), ('training', '#planActive')]:
            go(pg, t)
            a = pg.evaluate("[...document.querySelectorAll('%s .day-adj button')].map(b=>{var r=b.getBoundingClientRect(),cs=getComputedStyle(b);return [b.textContent,Math.round(r.height),!!b.offsetParent,cs.borderTopColor,cs.backgroundColor]})" % host)
            check('%d %s: Short and Change workout are visible 44 px buttons' % (W, t), [x[0] for x in a] == ['Short', 'Change workout'] and all(x[1] >= 44 and x[2] and x[3] == 'rgb(20, 20, 20)' and x[4] != 'rgb(242, 85, 44)' for x in a), a)
        go(pg, 'training'); pg.click('#toolRestBtn'); pg.wait_for_timeout(200)
        check('%d: Rest timer opens in place, not as a dropdown' % W, pg.evaluate("getComputedStyle(restPresets).position") == 'static' and pg.evaluate("restPresets.classList.contains('open')"))
        pg.click('#toolRestBtn')
        # The sheet.
        go(pg, 'today'); pg.click('#tbAdj .day-adj-btn:has-text("Change workout")'); pg.wait_for_timeout(300)
        opts = pg.evaluate("[...cwSheet.querySelectorAll('.cw-opt')].map(b=>{var r=b.getBoundingClientRect();return [b.querySelector('b').textContent,Math.round(r.height)]})")
        check('%d: the sheet has the three options, 44 px' % W, [o[0] for o in opts] == ['Pick another workout', 'Add an exercise', 'Build my own'] and all(o[1] >= 44 for o in opts), opts)
        check('%d: the sheet takes focus and says which day' % W, pg.evaluate("document.activeElement===cwSheet.querySelector('.cw-opt')") and pg.evaluate("cwSub.textContent").startswith('For today'), pg.evaluate("cwSub.textContent"))
        pg.screenshot(path=shot('837-change-sheet-%d.png' % W))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        check('%d: Escape closes the sheet and focus goes back' % W, pg.evaluate("cwSheet.style.display") == 'none' and pg.evaluate("document.activeElement.textContent") == 'Change workout')
        check('%d: no page errors' % W, not errs, errs); ctx.close()
    # The three options, on the default plan.
    ctx, pg, errs = page(b, 390, 844); go(pg, 'today')
    D = pg.evaluate("todayDayId()")
    pg.click('#tbAdj .day-adj-btn:has-text("Change workout")'); pg.click('#cwSheet .cw-opt:has-text("Pick another workout")'); pg.wait_for_timeout(500)
    check('Pick another workout shows saved and recent workouts', tab(pg) == 'quicklog' and pg.evaluate("qlOthers.children.length") > 0 and pg.evaluate("quickTargetDay()") == D)
    pg.click('#qlToday .ql-back'); pg.wait_for_timeout(400)
    check('Back from it returns to Today, Today lit in the bar', tab(pg) == 'today' and pg.evaluate("document.querySelector('.tabbar-btn.current').dataset.tab") == 'today')
    pg.click('#tbAdj .day-adj-btn:has-text("Change workout")'); pg.click('#cwSheet .cw-opt:has-text("Add an exercise")'); pg.wait_for_timeout(300)
    check('Add an exercise opens the search with muscle picks for new ones', pg.evaluate("exSheet.style.display") == 'flex' and pg.evaluate("_sheetMode") == 'day')
    pg.fill('#exSheetQ', 'hip thrust'); pg.wait_for_timeout(300)
    ex = pg.evaluate("exSheetList.querySelector('.ex-row[data-id]').dataset.id")
    pg.click('#exSheetList .ex-row[data-id="%s"]' % ex); pg.wait_for_timeout(400)
    check('the lift joins the day, marked as added', pg.evaluate("(buildSession('%s',currentTrainWeek).added||{})['%s']" % (D, ex)) == True and ex in (pg.evaluate("dayAdded[currentTrainWeek+'|%s']" % D) or []))
    pg.click('#tbAdj .day-adj-btn:has-text("Change workout")'); pg.click('#cwSheet .cw-opt:has-text("Build my own")'); pg.wait_for_timeout(400)
    check('Build my own opens the session list with the search', tab(pg) == 'quicklog' and pg.evaluate("exSheet.style.display") == 'flex' and pg.evaluate("_sheetMode") == 'session')
    pg.evaluate("closeExSheet()")
    # No Quick Log words anywhere on screen.
    left = []
    for t in ['today', 'training', 'running', 'calendar', 'quicklog']:
        go(pg, t)
        if 'Quick Log' in pg.evaluate("document.body.innerText"): left.append(t)
    pg.click('#navGear'); pg.wait_for_timeout(200)
    if 'Quick Log' in pg.evaluate("settingsModal.innerText"): left.append('settings')
    check('no Quick Log words on any screen, Settings or tips', not left and all('Quick Log' not in t for t in pg.evaluate("TIP_DEFS.map(d=>d.t)")), left)
    check('the gear tip names the gear', 'gear' in pg.evaluate("TIP_DEFS.filter(d=>d.id==='menu')[0].t"))
    ctx.close()
    # Round trip: looking around stores nothing.
    ctx, pg, errs = page(b, 390, 844); go(pg, 'today')
    before = pg.evaluate(ALL)
    pg.click('#tbStrip .ws-arr[aria-label="Next week"]'); pg.wait_for_timeout(300)
    pg.click('#tbStrip .wg-day >> nth=2'); pg.click('#tbStrip .ws-home'); pg.wait_for_timeout(300)
    pg.click('#tbStrip .wg-day >> nth=5'); pg.click('#tbStrip .wg-day >> nth=1'); pg.wait_for_timeout(200)
    go(pg, 'training'); pg.click('#weekGlance .wg-day >> nth=4'); go(pg, 'today')
    pg.click('#tbStrip .wg-day >> nth=%d' % pg.evaluate("wsToday()"))
    pg.click('#tbAdj .day-adj-btn:has-text("Change workout")'); pg.click('#cwSheet .settings-cancel-btn')
    pg.click('#tbAdj .day-adj-btn:has-text("Short")'); pg.wait_for_timeout(300)
    #  8.39.1: Upper B cannot be shortened, so Short says so in place.
    if pg.evaluate("document.body.dataset.tab") == 'quicklog': pg.click('#qlToday button:has-text("Back")'); pg.wait_for_timeout(300)
    else: check('Short on a day it cannot shorten says Already about', pg.evaluate("(document.querySelector('#tbAdj .adj-note')||{}).innerText||''").startswith('Already about '))
    for t in TABS: go(pg, t); pg.click('#navGear'); pg.click('#settingsModal .settings-cancel-btn')
    pg.click('#navLogo'); pg.wait_for_timeout(300)
    after = pg.evaluate(ALL)
    diff = [x for x in json.loads(after) if x not in json.loads(before)] + [x for x in json.loads(before) if x not in json.loads(after)]
    check('a round trip of looking, previewing and cancelling leaves storage as it was', after == before, diff)
    pg.reload(); pg.wait_for_timeout(1500)
    check('and the reload lands on today', pg.evaluate("selSlot()") == pg.evaluate("wsToday()") and pg.evaluate("currentTrainWeek") == pg.evaluate("homeWeek()"))
    check('no page errors', not errs, errs); ctx.close()
    sys.exit(1 if done() else 0)
