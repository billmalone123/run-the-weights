"""8.37 Part A: the week strip on Today, shared with Lift. Seven days, today picked on open, states, a day ahead, a day gone by,
a rest day, next week, back in one tap, reload lands on today. Three plans at 390 and 320. Nothing new is stored."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
PLANS = [('upper and lower', ''), ('arnold', "setSplit('arnold')"), ('advanced runner', "setAdvanced(true);setRunning(true)")]
CLOSE = "document.querySelectorAll('.settings-modal-overlay').forEach(m=>{if(m.id!=='dayTakeover')m.style.display='none'})"
KEYS = json.load(open(os.path.join(HERE, 'baselines', 'storage_keys_835b.json')))
DATA = "JSON.stringify(['monk_sessions_v1','monk_day_added_v1','monk_quick_sessions_v1','monk_week_moves_v1','monk_short_days_v1','monk_mode_train_week_v1'].map(k=>localStorage.getItem(k)))"
CELLS = """(h)=>[...document.querySelectorAll(h+' .wg-day')].map(b=>{var r=b.getBoundingClientRect(),t=b.querySelector('.wg-title');
  return {c:b.className,p:b.getAttribute('aria-pressed'),a:b.getAttribute('aria-label'),w:r.width,h:r.height,cut:!t.classList.contains('wg-cut')&&t.scrollWidth>t.clientWidth+1,vis:!!b.offsetParent}})"""
def tab(pg): return pg.evaluate("document.body.dataset.tab")
def cells(pg, h='#tbStrip'): return pg.evaluate(CELLS, h)
def tap(pg, i, h='#tbStrip'): pg.click('%s .wg-day >> nth=%d' % (h, i)); pg.wait_for_timeout(300)
def reload(pg): pg.reload(); pg.wait_for_timeout(1500); pg.evaluate(CLOSE); go(pg, 'today')
def log_on(pg, ex, w, r):
    pg.evaluate("PA.ex='%s';PA.slot=null;PA.key=null;renderPlanActive()" % ex)
    pg.evaluate("PA.wLb=%s;PA.r=%s" % (w, r)); pg.click('#paLogBtn'); pg.wait_for_timeout(300)
    pg.evaluate("dismissTimer&&dismissTimer();document.querySelectorAll('.rest-modal-overlay').forEach(m=>m.classList.remove('visible'))")
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, setup in PLANS:
        for W in [390, 320]:
            n = '%s %d' % (name, W)
            ctx, pg, errs = page(b, W, 844)
            if setup: pg.evaluate(setup); pg.reload(); pg.wait_for_timeout(1500); pg.evaluate(CLOSE)
            go(pg, 'today')
            week, ti, wk = pg.evaluate("splitWeekOf(currentTrainWeek)"), pg.evaluate("wsToday()"), pg.evaluate("currentTrainWeek")
            fut = [i for i in range(ti + 1, 7) if week[i] != 'rest']
            rest = [i for i in range(ti + 1, 7) if week[i] == 'rest'] or [i for i in range(7) if week[i] == 'rest' and i != ti]
            past = [i for i in range(ti) if week[i] != 'rest']
            c = cells(pg)
            check(n + ': seven days, today picked on open', len(c) == 7 and [x['p'] for x in c].index('true') == ti and 'today' in c[ti]['c'], [x['p'] for x in c])
            check(n + ': every day is a 44 px target, no cut text', all(x['w'] >= 44 and x['h'] >= 44 and not x['cut'] for x in c), [(round(x['w']), round(x['h']), x['cut']) for x in c])
            check(n + ': day letter and date on each day', all(len(x['a'].split(', ')) >= 3 for x in c) and pg.evaluate("[...tbStrip.querySelectorAll('.wg-date')].every(e=>/^\\d+$/.test(e.textContent))"))
            check(n + ': rest days read as rest', all(('rest' in c[i]['c']) == (week[i] == 'rest') for i in range(7)))
            check(n + ': days ahead read as upcoming', all('upcoming' in c[i]['a'] and 'open' in c[i]['c'] for i in fut), [c[i]['a'] for i in fut])
            sel_ok = pg.evaluate("(()=>{var b=tbStrip.querySelector('.wg-day.picked .wg-in'),o=tbStrip.querySelector('.wg-day:not(.picked) .wg-in'),cs=getComputedStyle(b),co=getComputedStyle(o);return cs.backgroundColor!==co.backgroundColor&&cs.borderTopColor!==co.borderTopColor})()")
            check(n + ': the picked day changes shape, not only color, and says pressed', sel_ok and c[ti]['p'] == 'true')
            ow = pg.evaluate("document.documentElement.scrollWidth-innerWidth")
            check(n + ': no sideways overflow', ow <= 0, ow)
            # A day gone by with nothing logged.
            if past:
                pi = past[0]; tap(pg, pi)
                t = pg.evaluate("tbWork.innerText")
                check(n + ': a past day shows Nothing logged and Log for this day', 'Nothing logged.' in t and 'Log for this day' in t and not pg.evaluate("!!tbWork.querySelector('.tb-start')"), t[:120])
                pg.click('#tbWork .tb-logfor'); pg.wait_for_timeout(600)
                check(n + ': Log for this day opens Lift on that day', tab(pg) == 'training' and pg.evaluate("localStorage.getItem('monk_mode_last_day_v1')||PA.day") == week[pi] and pg.evaluate("PA.day") == week[pi], [tab(pg), pg.evaluate("PA.day"), week[pi]])
                check(n + ': Lift shows the same day picked', [x['p'] for x in cells(pg, '#weekGlance')].index('true') == pi)
                ex = pg.evaluate("paList('%s')[0].id" % week[pi]); log_on(pg, ex, 50, 8)
                go(pg, 'today')
                c = cells(pg)
                check(n + ': a day with one set logged reads as partly logged (8.39.1: done at 70 percent)', 'part' in c[pi]['c'] and 'partly logged' in c[pi]['a'], c[pi])
                check(n + ': the selection stays on that day on Today', c[pi]['p'] == 'true')
                t = pg.evaluate("tbWork.innerText")
                check(n + ': the past day lists what was logged', 'Open in Lift' in t and '1 set' in t, t[:160])
            # A day ahead.
            if fut:
                fi = fut[0]; D = week[fi]; tap(pg, fi)
                t = pg.evaluate("tbWork.innerText"); dow = pg.evaluate("PA_DOWS[%d]" % fi)
                check(n + ': a day ahead shows its plan with no START WORKOUT', not pg.evaluate("!!tbWork.querySelector('.tb-start')") and ('Planned for ' + dow) in t and pg.evaluate("tbWork.querySelectorAll('.tb-list li').length") > 0, t[:200])
                adj = pg.evaluate("[...tbAdj.querySelectorAll('button')].map(b=>{var r=b.getBoundingClientRect(),cs=getComputedStyle(b);return [b.textContent,Math.round(r.height),cs.borderTopColor,cs.backgroundColor]})")
                check(n + ': Short and Change workout under it, 44 px, ink outline, not persimmon', [a[0] for a in adj] in (['Short', 'Change workout', 'Do this workout today'], ['Short', 'Change workout']) and all(a[1] >= 44 and a[2] == 'rgb(20, 20, 20)' and 'rgb(242, 85, 44)' not in a[3] for a in adj), adj)
                before = pg.evaluate(DATA)
                pg.click('#tbAdj .day-adj-btn:has-text("Short")'); pg.wait_for_timeout(400)
                check(n + ': Short on a day ahead opens the time picker for that day', tab(pg) == 'quicklog' and pg.evaluate("quickTargetDay()") == D)
                pg.click('#qlToday button:has-text("Back")'); pg.wait_for_timeout(400)
                check(n + ': Back changes nothing', pg.evaluate(DATA) == before and tab(pg) == 'today')
                pg.click('#tbAdj .day-adj-btn:has-text("Short")'); pg.wait_for_timeout(400)
                pg.click('#qlTimes button:has-text("30 min")'); pg.wait_for_timeout(200)
                pg.click('#qlToday .ql-ok'); pg.wait_for_timeout(600)
                k = '%d|%s' % (wk, D)
                check(n + ': the change is stored under that day', pg.evaluate("timeBoxes['%s']" % k) == 30 and pg.evaluate("sessionIsShort('%s')" % D), k)
                check(n + ': today keeps its own workout', not pg.evaluate("sessionIsShort(todayDayId())") or pg.evaluate("todayDayId()") == D)
                c = cells(pg)
                check(n + ': the day reads as shortened and stays picked', 'short' in c[fi]['c'] and 'shortened' in c[fi]['a'] and c[fi]['p'] == 'true', c[fi])
                check(n + ': its card shows the short workout and Restore', pg.evaluate("[...document.querySelectorAll('#tbAdj .day-adj-btn')].some(b=>b.innerText.trim()==='Full workout')") and pg.evaluate("tbWork.querySelector('.tb-day').textContent").startswith('Short'))
                reload(pg)
                c = cells(pg)
                check(n + ': reopening lands on today', [x['p'] for x in c].index('true') == ti)
                check(n + ': the short day survives a reload', 'short' in c[fi]['c'] and pg.evaluate("sessionIsShort('%s')" % D))
                tap(pg, fi); pg.click('#tbAdj .day-adj-btn:has-text("Full workout")'); pg.wait_for_timeout(400)
                check(n + ': Restore brings the plan back for that day', not pg.evaluate("sessionIsShort('%s')" % D) and 'short' not in cells(pg)[fi]['c'])
            # Today on Today selects on Lift too, and back.
            sl = fut[0] if fut else (rest[0] if rest else 0)
            tap(pg, sl); go(pg, 'training')
            check(n + ': picking a day on Today picks it on Lift', [x['p'] for x in cells(pg, '#weekGlance')].index('true') == sl)
            tap(pg, ti, '#weekGlance'); go(pg, 'today')
            check(n + ': picking on Lift picks it on Today', [x['p'] for x in cells(pg)].index('true') == ti)
            # Next week, back in one tap, reload.
            pg.click('#tbStrip .ws-arr[aria-label="Next week"]'); pg.wait_for_timeout(400)
            check(n + ': next week shows', pg.evaluate("currentTrainWeek") == wk + 1 and ('Week %d' % (wk + 2)) in pg.evaluate("tbStrip.querySelector('.ws-wk').innerText"))
            check(n + ': previewing a week does not save it', pg.evaluate("localStorage.getItem('monk_mode_train_week_v1')") == str(wk))
            nf = [i for i in range(7) if week[i] != 'rest'][0]
            ND = pg.evaluate("splitWeekOf(currentTrainWeek)[%d]" % nf)
            tap(pg, nf)
            check(n + ': a day next week previews with no START', not pg.evaluate("!!tbWork.querySelector('.tb-start')") and 'Planned for' in pg.evaluate("tbWork.innerText"))
            pg.click('#tbAdj .day-adj-btn:has-text("Short")'); pg.wait_for_timeout(400)
            pg.click('#qlTimes button:has-text("20 min")'); pg.wait_for_timeout(200)
            pg.click('#qlToday .ql-ok'); pg.wait_for_timeout(600)
            check(n + ': a day next week is adjusted under next week\'s key', pg.evaluate("timeBoxes['%d|%s']" % (wk + 1, ND)) == 20 and pg.evaluate("timeBoxes['%d|%s']" % (wk, ND)) in (None, 'full'))
            check(n + ': and shows on that day', 'short' in cells(pg)[nf]['c'] and pg.evaluate("currentTrainWeek") == wk + 1)
            homes = pg.evaluate("[...tbStrip.querySelectorAll('.ws-home')].map(b=>Math.round(b.getBoundingClientRect().height))")
            check(n + ': This week is one 44 px button', len(homes) == 1 and homes[0] >= 44, homes)
            pg.click('#tbStrip .ws-home'); pg.wait_for_timeout(400)
            check(n + ': one tap goes back to this week and today', pg.evaluate("currentTrainWeek") == wk and [x['p'] for x in cells(pg)].index('true') == ti)
            pg.click('#tbStrip .ws-arr[aria-label="Next week"]'); pg.wait_for_timeout(300)
            reload(pg)
            check(n + ': reopening after a preview lands on this week and today', pg.evaluate("currentTrainWeek") == wk and [x['p'] for x in cells(pg)].index('true') == ti)
            pg.evaluate("_selSlot=null;viewWeek(%d)" % (wk + 1)); pg.wait_for_timeout(200)
            check(n + ': next week\'s short day is still there', pg.evaluate("sessionIsShort('%s')" % ND))
            pg.evaluate("wsHome()"); pg.wait_for_timeout(200)
            # A rest day gets a workout.
            ri = rest[0] if rest else None
            if ri is not None: tap(pg, ri)
            if ri is not None: check(n + ': a rest day shows rest and Change workout, no START', pg.evaluate("tbWork.querySelector('.tb-day').textContent") == 'Rest' and not pg.evaluate("!!tbWork.querySelector('.tb-start')") and (ri < ti or pg.evaluate("[...tbAdj.querySelectorAll('button')].map(b=>b.textContent)") == ['Change workout']))
            if ri is not None and ri > ti:
                pg.click('#tbAdj .day-adj-btn'); pg.wait_for_timeout(300)
                move = pg.evaluate("_cw.day")
                check(n + ': the sheet says which workout moves to the rest day', move and pg.evaluate("SPLIT_DAYS['%s'].title" % move).rstrip('.') in pg.evaluate("cwSub.textContent"), pg.evaluate("cwSub.textContent"))
                pg.click('#cwSheet .cw-opt:has-text("Pick another workout")'); pg.wait_for_timeout(500)
                pg.evaluate("_qlOpen='push';renderQuickLog()"); pg.click('#qlOthers .today-start'); pg.wait_for_timeout(600)
                c = cells(pg)
                check(n + ': the rest day now holds a workout', 'rest' not in c[ri]['c'] and pg.evaluate("splitWeekOf(currentTrainWeek)[%d]" % ri) == move and pg.evaluate("!!quickFor('%s', currentTrainWeek)" % move), c[ri]['c'])
                check(n + ': the rest day is still picked and shows it', c[ri]['p'] == 'true' and 'Push' in pg.evaluate("tbWork.innerText"))
            keys = pg.evaluate("Object.keys(localStorage)")
            check(n + ': no new storage key', all(k in KEYS for k in keys), [k for k in keys if k not in KEYS])
            if W == 390 or name == 'upper and lower':
                pg.evaluate("_selSlot=null;wsAfter()"); go(pg, 'today')
                pg.screenshot(path=shot('837-today-strip-%s-%d.png' % (name.split()[0], W)), full_page=False)
            check(n + ': no page errors', not errs, errs); ctx.close()
    # Screenshots on the default plan: a day ahead, a day gone by.
    for W in [390, 320]:
        ctx, pg, errs = page(b, W, 844); go(pg, 'today')
        ti = pg.evaluate("wsToday()"); tap(pg, ti + 1)
        pg.screenshot(path=shot('837-future-day-%d.png' % W))
        tap(pg, 1); pg.screenshot(path=shot('837-past-day-%d.png' % W))
        ctx.close()
    sys.exit(1 if done() else 0)
