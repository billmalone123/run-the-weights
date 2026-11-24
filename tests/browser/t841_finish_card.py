"""8.41 finish card: DONE on the workout screen, one true message by priority (weight PR, rep PR, volume, weeks in a row, done this week, fallback), stats row, Share with Show weights off, Today after DONE, edge cases. 390 and 320."""
import sys, os, json, datetime, base64; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
PERS = 'rgb(242, 85, 44)'; INK = 'rgb(20, 20, 20)'; ULTRA = 'rgb(28, 47, 181)'; CREAM = 'rgb(242, 238, 228)'
#  Thursday Nov 19 2026 is upper-b in the upper-lower plan. Monday of this week is Nov 16.
FX = r"""(o)=>{
  setSplit('upper-lower');
  const W=o.week, dk=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
  const day=(w,i)=>dk(new Date(2026,10,16+7*(w-W)+i)), s={};
  const add=(dd,idx,wk,date,sets)=>{const ex=splitDayExercises(dd)[idx];if(!ex)return;
    const e={d:date,week:wk,day:dd,variant:activeVariant(ex),failure:null,weight:sets[0][0],reps:sets[0][1]};
    sets.forEach((x,i)=>e['s'+(i+1)]={w:x[0],r:x[1]});(s[ex.id]=s[ex.id]||[]).push(e)};
  const DOW={'upper-a':0,'lower-a':1,'upper-b':3,'lower-b':4};
  (o.full||[]).forEach(wk=>Object.keys(DOW).forEach(dd=>splitDayExercises(dd).forEach((ex,i)=>add(dd,i,wk,day(wk,DOW[dd]),[[50,8],[50,8]]))));
  (o.days||[]).forEach(dd=>splitDayExercises(dd).forEach((ex,i)=>add(dd,i,W,day(W,Math.min(DOW[dd],2)),[[50,8],[50,8]])));
  (o.ub||[]).forEach(x=>add('upper-b',x[0],x[1],day(x[1],3),x[2]));
  (o.today||[]).forEach(x=>add('upper-b',x[0],W,x[2]||'2026-11-19',x[1]));
  localStorage.setItem('monk_sessions_v1',JSON.stringify(s));
  localStorage.setItem('monk_mode_train_week_v1',String(W));
  localStorage.setItem('monk_week_anchor_v1',JSON.stringify({week:W,monday:'2026-11-16'}));
  localStorage.setItem('monk_session_times_v1',JSON.stringify(o.times||{'2026-11-19|upper-b':{s:Date.now()-40*60000,l:Date.now()-60000}}));
  if(o.kg) localStorage.setItem('monk_weight_unit_v1','kg');
  return Object.keys(s).length}"""
def ub_all(sets, n=6, start=0): return [[i, sets] for i in range(start, n)]
def setup(b, o, w=390, h=844, clock=T0):
    ctx = b.new_context(viewport={'width': w, 'height': h}, service_workers='block'); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.clock.install(time=clock); pg.add_init_script(INIT)
    pg.goto(URL); pg.wait_for_timeout(900)
    pg.evaluate(FX, o); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    return ctx, pg, errs
def open_lift(pg):
    pg.evaluate("tbStart('upper-b')"); pg.wait_for_timeout(500)
def tap_done(pg):
    open_lift(pg)
    sel = '#paDoneBtn' if pg.evaluate("!!document.getElementById('paDoneBtn')") else '#paFinishBtn'
    pg.click(sel); pg.wait_for_timeout(500)
    return pg.evaluate("FIN.sum&&FIN.sum.msg")
def full(m): return (m['head'] + ' ' + m['sub']).strip() if m else None
def name(pg, i): return pg.evaluate("activeVariant(splitDayExercises('upper-b')[%d])" % i)
def nlifts(pg): return pg.evaluate("splitDayExercises('upper-b').length")
with sync_playwright() as p:
    b = p.chromium.launch()
    # ---------- a. weight PR, with the card checked at 390 and 320 ----------
    for W in [390, 320]:
        o = {'week': 5, 'full': [3, 4], 'ub': [[0, 4, [[100, 8], [100, 8]]]], 'today': [[0, [[105, 6], [100, 8], [100, 8]]]] + ub_all([[50, 8], [50, 8]], 6, 1)}
        ctx, pg, errs = setup(b, o, w=W)
        check('%d setup: plan week 6, Thursday is upper-b' % W, pg.evaluate("[currentTrainWeek,todayKey()]") == [5, '2026-11-19'], pg.evaluate("[currentTrainWeek,todayKey()]"))
        before = pg.evaluate("localStorage.getItem('monk_sessions_v1')")
        open_lift(pg)
        db = pg.evaluate("(()=>{const e=document.getElementById('paDoneBtn')||document.getElementById('paFinishBtn');if(!e)return null;const r=e.getBoundingClientRect();return [e.textContent,Math.round(r.height),Math.round(r.width)]})()")
        check('%d workout screen: DONE shows once a set is logged, 44 px or more' % W, db and db[0] == 'Done' and db[1] >= 44 and db[2] >= 44, db)
        check('%d no card before the tap' % W, pg.evaluate("!document.getElementById('finSheet')||finSheet.hidden"))
        m = tap_done(pg)
        n0 = name(pg, 0)
        check('%d a: weight PR reads Name 105 for 6. Your best yet.' % W, full(m) == n0 + ' 105 for 6. Your best yet.', [full(m), n0])
        st = pg.evaluate("(()=>{const f=finSheet;return [!f.hidden,f.getAttribute('role'),f.getAttribute('aria-modal'),document.activeElement.id]})()")
        check('%d card opens as a dialog, focus on the headline' % W, st == [True, 'dialog', 'true', 'finTitle'], st)
        stats = pg.evaluate("[...document.querySelectorAll('.fin-stats li')].map(l=>l.innerText.replace(/\\s+/g,' '))")
        nsets = 3 + 2 * 5; vol = 105 * 6 + 1600 + 800 * 5
        check('%d stats: sets, volume in lb, minutes since the first set' % W, stats == ['%d Sets' % nsets, '{:,} Volume, lb'.format(vol), '40 Minutes'], [stats, nsets, vol])
        sty = pg.evaluate("(()=>{const c=document.querySelector('.fin-card'),t=finTitle,s=document.querySelector('.fin-sub');return [getComputedStyle(c).backgroundColor,getComputedStyle(finSheet).backgroundColor,getComputedStyle(t).fontFamily,getComputedStyle(s).fontFamily,getComputedStyle(t).color]})()")
        check('%d ultramarine card on cream, Antonio headline, DM Sans body, cream text' % W, sty[0] == ULTRA and sty[1] == CREAM and 'Antonio' in sty[2] and 'DM Sans' in sty[3] and sty[4] == CREAM, sty)
        bt = pg.evaluate("[...document.querySelectorAll('.fin-btns button')].map(b=>{const r=b.getBoundingClientRect(),c=getComputedStyle(b);return [b.textContent,c.backgroundColor,c.color,Math.round(r.width),Math.round(r.height)]})")
        check('%d buttons: Done primary persimmon with ink, Share, Show weights, all 44 px or more' % W, bt[0][0] == 'Done' and bt[0][1] == PERS and bt[0][2] == INK and bt[1][0] == 'Share' and 'Show weights' in bt[2][0] and all(x[3] >= 44 and x[4] >= 44 for x in bt), bt)
        txt = pg.evaluate("finSheet.innerText")
        check('%d copy: no dashes, exclamation marks or emoji' % W, not any(c in txt for c in '-–—!') and all(ord(c) < 0x2000 for c in txt), txt)
        check('%d fits with no sideways scroll' % W, pg.evaluate("finSheet.scrollWidth<=innerWidth&&document.documentElement.scrollWidth<=innerWidth&&[...document.querySelectorAll('.fin-card *')].every(e=>e.getBoundingClientRect().right<=innerWidth+0.5)"))
        check('%d no animation on the card' % W, pg.evaluate("getComputedStyle(finSheet).animationName==='none'&&getComputedStyle(document.querySelector('.fin-card')).animationName==='none'"))
        pg.screenshot(path=shot('841-a-%d.png' % W))
        check('%d DONE saves nothing new to sets' % W, pg.evaluate("localStorage.getItem('monk_sessions_v1')") == before)
        check('%d DONE marks the day finished, f 2' % W, pg.evaluate("finTimes['2026-11-19|upper-b'].f") == 2)
        # Share: weights hidden by default, the image has no weights.
        check('%d Show weights is off by default' % W, pg.evaluate("finShowW.getAttribute('aria-checked')") == 'false' and pg.evaluate("FIN.showW") is False)
        check('%d weights hidden: the image line has no number' % W, pg.evaluate("FIN.sum.msg.headNoW") == 'A new best on ' + n0 + '.' and not any(ch.isdigit() for ch in pg.evaluate("FIN.sum.msg.headNoW+FIN.sum.msg.subNoW")))
        check('%d weights hidden: no volume in the image stats' % W, pg.evaluate("finStats(FIN.sum,false).map(x=>x[1])") == ['Sets', 'Minutes'])
        if W == 390:
            pg.wait_for_timeout(600)
            check('the image is ready before Share is tapped, 1080 by 1350', pg.evaluate("!!FIN.blob&&FIN.blob.type==='image/png'") and pg.evaluate("(()=>{const c=finDrawImage(FIN.sum,false);return [c.width,c.height]})()") == [1080, 1350])
            pg.evaluate("window._shared=null;navigator.canShare=f=>!!(f&&f.files);navigator.share=o=>{window._shared=o.files.map(f=>[f.name,f.type,f.size]);return Promise.resolve()};0")
            pg.click('#finShareBtn'); pg.wait_for_timeout(300)
            sh = pg.evaluate("window._shared")
            check('Share hands the PNG to the share sheet', sh and sh[0][1] == 'image/png' and sh[0][0] == 'run-the-weights-2026-11-19.png', sh)
            pg.click('#finShowW'); pg.wait_for_timeout(500)
            check('Show weights turns on and redraws', pg.evaluate("finShowW.getAttribute('aria-checked')") == 'true' and pg.evaluate("FIN.showW") is True)
            for sw, nm in [(False, 'hidden'), (True, 'shown')]:
                data = pg.evaluate("finDrawImage(FIN.sum,%s).toDataURL('image/png')" % ('true' if sw else 'false'))
                open(shot('841-image-weights-%s.png' % nm), 'wb').write(base64.b64decode(data.split(',')[1]))
        # Done returns to Today, finished state, next workout, no In progress.
        pg.click('.fin-done'); pg.wait_for_timeout(500)
        check('%d Done closes the card and goes to Today' % W, pg.evaluate("finSheet.hidden&&document.body.dataset.tab==='today'"))
        tt = pg.evaluate("document.getElementById('todayB').innerText")
        check('%d Today: no In progress and no Continue workout' % W, 'IN PROGRESS' not in tt.upper() and 'CONTINUE WORKOUT' not in tt.upper(), tt[:300])
        check('%d Today: upper-b shows done this week' % W, pg.evaluate("dayDoneOn('upper-b',5,'2026-11-16','2026-11-22')"))
        check('%d Today: the next workout leads, not the finished one' % W, 'NEXT WORKOUT' in tt.upper() and 'START WORKOUT' in tt.upper() and '\nUPPER B\n' not in tt.upper(), tt[:400])
        pg.screenshot(path=shot('841-today-after-%d.png' % W))
        check('%d no page errors' % W, not errs, errs); ctx.close()
    # ---------- b. rep PR at the same weight, counted against last time ----------
    o = {'week': 5, 'ub': [[0, 3, [[100, 8]]], [0, 4, [[100, 7]]]], 'today': [[0, [[100, 9], [100, 8], [100, 8]]]]}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('b: rep PR reads Name 100, 9 reps. Two more than last time.', full(m) == name(pg, 0) + ' 100, 9 reps. Two more than last time.', full(m))
    check('b: hidden weights drop the weight only', m['headNoW'] == name(pg, 0) + ', 9 reps.', m['headNoW'])
    pg.screenshot(path=shot('841-b-390.png')); ctx.close()
    # ---------- c. volume up on the same day last week ----------
    o = {'week': 5, 'ub': [[0, 4, [[100, 8], [100, 8]]], [1, 4, [[60, 8], [60, 8]]]], 'today': [[0, [[100, 8], [100, 8], [100, 8]]], [1, [[60, 8], [60, 8], [60, 8]]]]}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('c: Volume up 50 percent on last week.', full(m) == 'Volume up 50 percent on last week.', full(m))
    pg.screenshot(path=shot('841-c-390.png')); ctx.close()
    # ---------- d. weeks in a row ----------
    o = {'week': 5, 'full': [3, 4], 'days': ['upper-a', 'lower-a', 'lower-b'], 'today': ub_all([[50, 8], [50, 8]])}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('d: 3 weeks in a row. Every planned day done.', full(m) == '3 weeks in a row. Every planned day done.', full(m))
    pg.screenshot(path=shot('841-d-390.png')); ctx.close()
    # one full week only is not a streak, the sessions line instead
    o = {'week': 5, 'full': [3], 'days': ['upper-a', 'lower-a', 'lower-b'], 'today': ub_all([[50, 8], [50, 8]])}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('d: a streak needs this week and the week before', full(m) == '4 of 4 done this week.', full(m)); ctx.close()
    # ---------- e. done this week, empty history (a restored backup with no history) ----------
    o = {'week': 5, 'days': ['upper-a'], 'today': [[0, [[300, 5], [300, 5], [300, 5]]]]}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('e and no false PR: a first ever log is not a PR, 2 of 4 done this week.', full(m) == '2 of 4 done this week.', full(m))
    pg.screenshot(path=shot('841-e-390.png')); ctx.close()
    o = {'week': 0, 'today': [[0, [[100, 5], [100, 5], [100, 5]]]], 'times': {}}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('empty history, week 1: 1 of 4 done this week.', full(m) == '1 of 4 done this week.', full(m))
    stats = pg.evaluate("[...document.querySelectorAll('.fin-stats li')].map(l=>l.innerText.replace(/\\s+/g,' '))")
    check('no session clock: no minutes, never a made up time', stats == ['3 Sets', '1,500 Volume, lb'], stats)
    check('empty history: no page errors', not errs, errs); ctx.close()
    # ---------- f. one or two sets: fallback only, even with a PR ----------
    o = {'week': 5, 'ub': [[0, 4, [[100, 8]]]], 'today': [[0, [[150, 8], [150, 8]]]]}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    nx = pg.evaluate("SPLIT_DAYS[findNextUnloggedDay()].title.replace(/\\.$/,'')")
    check('f: two sets read Logged. Next up is the workout Today leads with.', full(m) == 'Logged. Next up is ' + nx + '.', (full(m), nx))
    pg.screenshot(path=shot('841-f-390.png'))
    pg.click('.fin-done'); pg.wait_for_timeout(500)
    lead = pg.evaluate("(document.querySelector('#todayB .tb-day')||{}).innerText||''")
    check('f: Today leads with the same workout the card named', lead.strip().upper() == nx.upper(), (lead, nx)); ctx.close()
    ctx, pg, errs = setup(b, {'week': 5, 'today': [[0, [[100, 8]], '2026-11-17']]}, clock=datetime.datetime(2026, 11, 17, 10, 0, 0))
    pg.evaluate("localStorage.setItem('monk_session_times_v1','{}')")
    pg.evaluate("PA.day='upper-b'"); pg.evaluate("finDone()"); pg.wait_for_timeout(300)
    m2 = full(pg.evaluate("FIN.sum&&FIN.sum.msg"))
    check('f: a missed earlier day is named, as Today shows it (Upper A on Tuesday)', m2 == 'Logged. Next up is Upper A.', m2); ctx.close()
    # ---------- priority: every message possible, the higher one wins ----------
    hist = [[0, 4, [[100, 7], [100, 7]]], [0, 3, [[100, 8]]]]
    o = {'week': 5, 'full': [3, 4], 'days': ['upper-a', 'lower-a', 'lower-b'], 'ub': hist, 'today': [[0, [[105, 6], [100, 9], [100, 8], [100, 8]]]] + ub_all([[50, 8], [50, 8], [50, 8]], 6, 1)}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('priority: weight PR beats rep PR, volume and streak', m['k'] == 'a', full(m)); ctx.close()
    o['today'] = [[0, [[100, 9], [100, 8], [100, 8]]]] + ub_all([[50, 8], [50, 8], [50, 8]], 6, 1)
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('priority: rep PR beats volume and streak', m['k'] == 'b', full(m)); ctx.close()
    o['today'] = [[0, [[100, 7], [100, 7], [100, 7]]]] + ub_all([[50, 8], [50, 8], [50, 8]], 6, 1)
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('priority: volume beats streak', m['k'] == 'c', full(m)); ctx.close()
    # equal to the best is not a PR
    o = {'week': 5, 'ub': [[0, 4, [[100, 8], [100, 8]]]], 'today': [[0, [[100, 8], [100, 8]]], [1, [[50, 8]]]]}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('no false PR: matching the best is not a PR', m['k'] not in ('a', 'b'), full(m)); ctx.close()
    # ---------- easy week: no comparisons ----------
    o = {'week': 3, 'full': [1, 2], 'ub': [[0, 2, [[100, 8]]]], 'today': [[0, [[110, 8], [110, 8], [110, 8]]]]}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    check('easy week 4: no PR or volume, the sessions line', full(m) == '1 of 4 done this week.', full(m)); ctx.close()
    # ---------- kg ----------
    o = {'week': 5, 'kg': True, 'ub': [[0, 4, [[100, 8]]]], 'today': [[0, [[105, 6], [100, 8], [100, 8]]]]}
    ctx, pg, errs = setup(b, o)
    m = tap_done(pg)
    want = name(pg, 0) + ' ' + pg.evaluate("String(wNum(105))") + ' for 6. Your best yet.'
    check('kg: the PR is in kg', full(m) == want and pg.evaluate("wLb()") == 'kg', [full(m), want])
    stats = pg.evaluate("[...document.querySelectorAll('.fin-stats li')].map(l=>l.innerText.replace(/\\s+/g,' '))")
    check('kg: volume says kg', any(s.endswith('Volume, kg') for s in stats), stats)
    pg.screenshot(path=shot('841-kg-390.png'))
    check('kg: no page errors', not errs, errs); ctx.close()
    # ---------- double tap ----------
    o = {'week': 5, 'today': ub_all([[50, 8], [50, 8]], 3)}
    ctx, pg, errs = setup(b, o)
    open_lift(pg)
    before = pg.evaluate("localStorage.getItem('monk_sessions_v1')")
    pg.evaluate("document.getElementById('paDoneBtn').click();finDone();finDone()"); pg.wait_for_timeout(300)
    check('double tap: one card, focus stays, sets unchanged', pg.evaluate("document.querySelectorAll('#finSheet').length") == 1 and pg.evaluate("document.activeElement.id") == 'finTitle' and pg.evaluate("localStorage.getItem('monk_sessions_v1')") == before)
    pg.click('.fin-done'); pg.wait_for_timeout(300)
    open_lift(pg); pg.click('#paDoneBtn' if pg.evaluate("!!document.getElementById('paDoneBtn')") else '#paFinishBtn'); pg.wait_for_timeout(300)
    check('DONE again later: same day, same flag, the card opens again', pg.evaluate("!finSheet.hidden&&finTimes['2026-11-19|upper-b'].f===2"))
    check('double tap: no page errors', not errs, errs); ctx.close()
    # ---------- no sets: no DONE ----------
    ctx, pg, errs = setup(b, {'week': 5, 'times': {}})
    open_lift(pg)
    check('no set logged: no DONE button', not pg.evaluate("!!document.getElementById('paDoneBtn')||!!document.getElementById('paFinishBtn')"))
    pg.evaluate("PA.day='upper-b';finDone()")
    check('no set logged: finDone opens nothing', pg.evaluate("!document.getElementById('finSheet')||finSheet.hidden"))
    # 70 percent by logging alone counts as done, no card
    pg.evaluate("tbStart('upper-b')"); pg.wait_for_timeout(300)
    for i in range(40):
        if pg.evaluate("dayDoneOn('upper-b',5,'2026-11-16','2026-11-22')") or not pg.evaluate("!!document.getElementById('paLogBtn')"): break
        pg.evaluate("if(!(PA.wLb>0))paSet('w','50')"); pg.click('#paLogBtn'); pg.wait_for_timeout(120); pg.evaluate("dismissTimer&&dismissTimer();document.querySelectorAll('.rest-modal-overlay').forEach(m=>m.classList.remove('visible'))")
    check('70 percent logged counts as done without a tap', pg.evaluate("dayDoneOn('upper-b',5,'2026-11-16','2026-11-22')") and pg.evaluate("!(finTimes['2026-11-19|upper-b']||{}).f"))
    check('the card never opens by itself', pg.evaluate("!document.getElementById('finSheet')||finSheet.hidden"))
    check('logging: no page errors', not errs, errs); ctx.close()
    # ---------- finished on a different date than it started ----------
    clock = datetime.datetime(2026, 11, 20, 0, 20, 0)
    o = {'week': 5, 'today': [[0, [[50, 8], [50, 8]], '2026-11-19'], [1, [[50, 8], [50, 8]], '2026-11-19'], [2, [[50, 8]], '2026-11-20']],
         'times': {'2026-11-19|upper-b': {'s': 1795131600000, 'l': 1795133700000}}}
    ctx, pg, errs = setup(b, o, clock=clock)
    pg.evaluate("localStorage.setItem('monk_session_times_v1',JSON.stringify({'2026-11-19|upper-b':{s:Date.now()-40*60000,l:Date.now()-5*60000}}));finTimes=finCleanTimes(JSON.parse(localStorage.getItem('monk_session_times_v1')))")
    pg.evaluate("PA.day='upper-b';finDone()"); pg.wait_for_timeout(300)
    s = pg.evaluate("[FIN.sum.dates,FIN.sum.sets,FIN.sum.mins]")
    check('past midnight: the session takes both dates, 5 sets, 40 min', s == [['2026-11-20', '2026-11-19'], 5, 40], s)
    check('past midnight: both dates are marked finished', pg.evaluate("[finTimes['2026-11-19|upper-b'].f,finTimes['2026-11-20|upper-b'].f]") == [2, 2])
    check('past midnight: no page errors', not errs, errs); ctx.close()
    # ---------- backups carry the DONE flag ----------
    o = {'week': 5, 'today': ub_all([[50, 8], [50, 8]], 3)}
    ctx, pg, errs = setup(b, o)
    tap_done(pg)
    bk = pg.evaluate("(()=>{let out=null;const o=URL.createObjectURL;const a=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};URL.createObjectURL=function(bl){out=bl;return 'blob:x'};exportData();URL.createObjectURL=o;HTMLAnchorElement.prototype.click=a;return out?out.text():null})()")
    check('backup carries f 2', json.loads(bk)['sessionTimes']['2026-11-19|upper-b'].get('f') == 2)
    check('restore keeps f 2, other values dropped', pg.evaluate("JSON.stringify(finCleanTimes({'2026-11-19|upper-b':{f:2},'2026-11-18|lower-a':{f:3}}))") == '{"2026-11-19|upper-b":{"f":2}}')
    check('Finish for today stays f 1 and is not done', pg.evaluate("finishForToday('lower-b'),finTimes[todayKey()+'|lower-b'].f") == 1)
    ctx.close()
    b.close()
sys.exit(1 if done() else 0)
