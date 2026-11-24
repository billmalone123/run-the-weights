"""8.39.1 Today state. Fixture from the owner's Nov 23 description (hotfix_seed.js): a date's view comes
only from the plan, that date's choices and that date's sets. Reproduces on 8.37d when RTW_OLD is set."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import *
from playwright.sync_api import sync_playwright
FIX = open(os.path.join(HERE, 'hotfix_seed.js')).read()
MON = datetime.datetime(2026, 11, 23, 21, 48)
CARD = "tbWork.innerText.replace(/\\n+/g,' | ')"
STRIP = "[...document.querySelectorAll('#tbStrip .wg-day')].map(b=>b.querySelector('.wg-date').textContent+':'+(['done','part','short','rest'].find(c=>b.classList.contains(c))||'open')).join(' ')"
COUNT = "Object.values(sessions).reduce((n,h)=>n+h.reduce((m,e)=>m+['s1','s2','s3','s4','s5','s6'].filter(k=>e[k]).length,0),0)"
LAST = "Object.values(sessions).reduce((n,h)=>n+h.filter(e=>e.d>='2026-11-16'&&e.d<='2026-11-22').length,0)"
BTN = "(t)=>[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.innerText.trim().toLowerCase()===t.toLowerCase()).length"
# Log sets through the real save path: rows on Lift, values in the inputs, autoSaveExercise.
LOG = """([day,n,sets])=>{goTab('training');switchDay(day);if(window.paOn)window.paOn=()=>false;renderDaySections();renderAllRowStates();
 const ids=buildSession(day,currentTrainWeek).list.map(x=>x.id).slice(0,n);
 ids.forEach(id=>{for(let s=1;s<=sets;s++){const w=document.getElementById('s'+s+'w-'+id),r=document.getElementById('s'+s+'r-'+id);if(!w||!r)continue;w.value=w.value||'100';r.value='8'}autoSaveExercise(id)});goTab('today');return ids}"""
def open_at(b, when, W=390, fixture=True, url=URL):
    common.T0 = when
    ctx, pg, errs = page(b, W, 844, seed=False, url=url)
    if fixture: pg.evaluate(FIX); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')"); go(pg, 'today')
    return ctx, pg, errs
def card(pg): return pg.evaluate(CARD)
with sync_playwright() as p:
    b = p.chromium.launch()
    if os.environ.get('RTW_OLD'):
        ctx, pg, errs = open_at(b, MON, url=os.environ['RTW_OLD'])
        c = card(pg); print('OLD BUILD:', pg.evaluate("currentTrainWeek+1"), c, pg.evaluate(STRIP))
        check('old build shows the bug: In progress Short Chest and Back on Monday', 'IN PROGRESS' in c.upper() and 'SHORT CHEST' in c.upper(), c)
        pg.screenshot(path=shot('8391-before-390.png')); ctx.close(); b.close(); sys.exit(1 if done() else 0)
    # 1. The fixture on Monday 9:48 pm.
    for W in [390, 320]:
        ctx, pg, errs = open_at(b, MON, W)
        last0 = pg.evaluate(LAST); c = card(pg); u = c.upper()
        check('%d: plan week rolls to 7 (week 6 started on Nov 16)' % W, pg.evaluate("currentTrainWeek") == 6)
        check('%d: Monday is a fresh full Chest and Back' % W, 'TODAY' in u and 'CHEST + BACK' in u and 'SHORT' not in u and '7 LIFTS' in u, c)
        check('%d: Start workout is the primary, nothing In progress' % W, 'START WORKOUT' in u and 'IN PROGRESS' not in u and 'CONTINUE' not in u, c)
        check('%d: no stale marks on the strip' % W, pg.evaluate(STRIP) == '23:open 24:open 25:open 26:rest 27:open 28:open 29:open', pg.evaluate(STRIP))
        check('%d: no Earlier today line for last Friday' % W, 'EARLIER TODAY' not in u)
        note = pg.evaluate("(document.querySelector('.tw-note')||{}).innerText||''")
        check('%d: one line names the week' % W, note.startswith('This week is week 7. Wrong?') and 'Change week' in note, note)
        check('%d: Change week and Reset this week are visible' % W, pg.evaluate(BTN, 'Change week') >= 1 and pg.evaluate(BTN, 'Reset this week') == 1)
        check('%d: one persimmon button on Today' % W, pg.evaluate("[...document.querySelectorAll('#tab-today button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(242, 85, 44)').length") == 1)
        pg.screenshot(path=shot('8391-after-mon-%d.png' % W), full_page=True)
        pg.evaluate("selectSlot(4)"); pg.wait_for_timeout(300)
        check('%d: previewing Friday shows Do this workout today' % W, pg.evaluate(BTN, 'Do this workout today') == 1)
        small = pg.evaluate("[...document.querySelectorAll('#tab-today button')].filter(b=>b.offsetParent).map(b=>[b.innerText,Math.round(b.getBoundingClientRect().height),Math.round(b.getBoundingClientRect().width)]).filter(x=>x[1]<44||x[2]<44)")
        check('%d: every Today button is 44 px or more' % W, not small, small)
        check('%d: no sideways scroll' % W, pg.evaluate("document.documentElement.scrollWidth<=innerWidth"))
        pg.screenshot(path=shot('8391-after-fri-preview-%d.png' % W), full_page=True)
        check('%d: last week sets intact' % W, last0 > 0 and pg.evaluate(LAST) == last0, [last0])
        check('%d: no page errors' % W, not errs, errs); ctx.close()
    # 2. Logging today: recent partial leads, 70 percent is done, Finish for today and Start fresh keep sets.
    ctx, pg, errs = open_at(b, MON)
    pg.evaluate(LOG, ['chest', 3, 1]); pg.wait_for_timeout(300); c = card(pg).upper()
    check('3 of 7 lifts just now: In progress, Continue workout', 'IN PROGRESS' in c and 'CONTINUE WORKOUT' in c, c)
    check('Finish for today and Start fresh are visible', pg.evaluate(BTN, 'Finish for today') == 1 and pg.evaluate(BTN, 'Start fresh') == 1)
    check('today shows a part mark, not done', pg.evaluate(STRIP).startswith('23:part'), pg.evaluate(STRIP))
    pg.screenshot(path=shot('8391-inprogress-390.png'), full_page=True)
    n0 = pg.evaluate(COUNT); pg.evaluate("finishForToday('chest')"); pg.wait_for_timeout(300); c = card(pg)
    check('Finish for today keeps every set', pg.evaluate(COUNT) == n0, [n0, pg.evaluate(COUNT)])
    check('after Finish: the plan leads with Start workout and one Earlier today line', 'START WORKOUT' in c.upper() and 'Earlier today: Chest + Back, 3 of 7 lifts. Continue' in c, c)
    pg.screenshot(path=shot('8391-earlier-today-390.png'), full_page=True)
    pg.evaluate("startFresh('chest')"); pg.wait_for_timeout(300)
    check('Start fresh keeps every set and closes the earlier entries', pg.evaluate(COUNT) == n0 and pg.evaluate("Object.values(sessions).flat().filter(e=>e.closed).length") == 3)
    pg.evaluate(LOG, ['chest', 2, 1]); pg.wait_for_timeout(300)
    check('a set after Start fresh is a new entry, nothing overwritten', pg.evaluate(COUNT) == n0 + 2 and pg.evaluate("Object.values(sessions).flat().filter(e=>e.d==='2026-11-23').length") == 5, pg.evaluate(COUNT))
    pg.evaluate(LOG, ['chest', 5, 1]); pg.wait_for_timeout(300)
    check('5 of 7 lifts (70 percent) counts as done', pg.evaluate(STRIP).startswith('23:done'), pg.evaluate(STRIP))
    check('done: the card moves on', 'CHEST + BACK' not in card(pg).upper(), card(pg))
    check('volume and history include both sessions', pg.evaluate("Object.values(sessions).flat().filter(e=>e.d==='2026-11-23').length") == 8)
    check('no page errors', not errs, errs); ctx.close()
    # 3. An old partial from earlier today: 4 hours ago.
    ctx, pg, errs = open_at(b, MON)
    pg.evaluate(LOG, ['chest', 4, 1]); pg.evaluate("finTimes['2026-11-23|chest'].l=Date.now()-4*36e5;finSaveTimes();renderToday()"); pg.wait_for_timeout(300); c = card(pg)
    check('a partial from 4 hours ago does not lead', 'START WORKOUT' in c.upper() and 'IN PROGRESS' not in c.upper(), c)
    check('it gets one quiet line', 'Earlier today: Chest + Back, 4 of 7 lifts. Continue' in c, c)
    pg.evaluate("continueEarlier('chest')"); go(pg, 'today')
    check('Continue reopens it as In progress', 'IN PROGRESS' in card(pg).upper(), card(pg))
    ctx.close()
    # 4. Short belongs to its date. Full workout restores.
    ctx, pg, errs = open_at(b, MON)
    cuts = pg.evaluate("activeSplit().week.filter(d=>d!=='rest').map(d=>d+':'+shortCuts(d))")
    print('Short shortens (arnold):', cuts)
    pg.evaluate("setSessionLength('chest','short')"); pg.wait_for_timeout(300); c = card(pg).upper()
    check('Short labels the card Short and shows Full workout', 'SHORT CHEST' in c and pg.evaluate(BTN, 'Full workout') >= 1, c)
    check('no small Restore link', pg.evaluate("document.querySelectorAll('#tab-today .restore-line').length") == 0)
    pg.screenshot(path=shot('8391-short-390.png'), full_page=True)
    pg.evaluate("[...document.querySelectorAll('#tab-today button')].find(b=>b.innerText.trim()==='Full workout').click()"); pg.wait_for_timeout(300)
    check('Full workout restores the plan', 'SHORT' not in card(pg).upper() and '7 LIFTS' in card(pg).upper(), card(pg))
    pg.evaluate("setSessionLength('chest','short')"); pg.evaluate(LOG, ['chest', 2, 1]); ctx.close()
    ctx, pg, errs = open_at(b, MON)
    pg.evaluate("setSessionLength('chest','short');"); pg.evaluate(LOG, ['chest', 2, 1])
    st = pg.evaluate("JSON.stringify({s:shortDays,m:localStorage.getItem('monk_day_mode'),ss:localStorage.getItem('monk_sessions_v1'),t:localStorage.getItem('monk_session_times_v1')})")
    ctx.close()
    for when, name in [(datetime.datetime(2026, 11, 24, 9, 0), 'Tuesday'), (datetime.datetime(2026, 11, 30, 9, 0), 'next Monday')]:
        common.T0 = when; ctx, pg, errs = page(b, 390, 844, seed=False)
        pg.evaluate("(st)=>{st=JSON.parse(st);localStorage.setItem('monk_sessions_v1',st.ss);localStorage.setItem('monk_short_days_v1',JSON.stringify(st.s));localStorage.setItem('monk_day_mode',st.m);localStorage.setItem('monk_session_times_v1',st.t);localStorage.setItem('monk_mode_train_week_v1','6');setSplit('arnold')}", st)
        pg.reload(); pg.wait_for_timeout(1500); go(pg, 'today'); c = card(pg).upper()
        check('Short does not leak to %s' % name, 'SHORT' not in c and 'IN PROGRESS' not in c, c)
        if name == 'Tuesday': pg.screenshot(path=shot('8391-tuesday-390.png'), full_page=True)
        ctx.close()
    # 5. Anchor cases.
    ctx, pg, errs = open_at(b, MON, fixture=False)
    pg.evaluate("setSplit('arnold');localStorage.setItem('monk_mode_train_week_v1','2')"); pg.reload(); pg.wait_for_timeout(1200)
    check('anchor: no dated logs keeps the week', pg.evaluate("currentTrainWeek") == 2)
    ctx.close()
    ctx, pg, errs = open_at(b, datetime.datetime(2026, 11, 18, 9, 0))
    check('anchor: logs in this calendar week keep week 6', pg.evaluate("currentTrainWeek") == 5 and pg.evaluate("document.querySelectorAll('.tw-note').length") == 0)
    ctx.close()
    ctx, pg, errs = open_at(b, datetime.datetime(2026, 12, 2, 9, 0))
    check('anchor: two calendar weeks later is week 8', pg.evaluate("currentTrainWeek") == 7)
    ctx.close()
    # 6. Current week picker: earlier, later, current. No leaks into this week's strip.
    ctx, pg, errs = open_at(b, MON)
    n0 = pg.evaluate(COUNT)
    pg.evaluate("changeWeek()"); pg.wait_for_timeout(400)
    sec = pg.evaluate("trainSec.innerText")
    check('Settings has Training, Current week and the line', 'Training' in sec and 'Current week' in sec and 'Pick the week you are training this week.' in sec, sec[:120])
    check('the picker shows 1 to 10, week 7 pressed', pg.evaluate("[...document.querySelectorAll('#trainWeekSet .liftdays-btn')].map(b=>b.innerText+(b.getAttribute('aria-pressed')==='true'?'*':'')).join(' ')") == '1 2 3 4 5 6 7* 8 9 10')
    pg.evaluate("pickTrainWeek(6)"); ask = pg.evaluate("twAsk.innerText")
    check('confirm line for week 6, and it says it is earlier', 'This week will be week 6. Your logged sets stay.' in ask and 'earlier' not in ask.lower() and 'Targets come from week 5.' in ask, ask)
    pg.screenshot(path=shot('8391-week-picker-390.png'))
    for wk, earlier in [(6, False), (4, True), (9, False), (7, False)]:
        pg.evaluate("pickTrainWeek(%d)" % wk); ask = pg.evaluate("twAsk.innerText")
        if wk != 7: check('week %d: earlier week said plainly' % wk if earlier else 'week %d: confirm line' % wk, ('earlier than week 6' in ask) == earlier and 'This week will be week %d.' % wk in ask, ask)
        pg.evaluate("setCurrentWeek(%d);closeSettingsModal()" % wk); go(pg, 'today'); c = card(pg).upper()
        check('week %d: strip has no marks and the card is a full Chest and Back' % wk, pg.evaluate(STRIP) == '23:open 24:open 25:open 26:rest 27:open 28:open 29:open' and 'CHEST + BACK' in c and 'SHORT' not in c and 'START WORKOUT' in c, [pg.evaluate(STRIP), c])
        check('week %d: header says week %d and 0 of 6 done' % (wk, wk), pg.evaluate("document.querySelector('#tbStrip .ws-wk b').innerText").startswith('Week %d' % wk) and pg.evaluate("tbWeek.innerText").startswith('0/6'), pg.evaluate("tbWeek.innerText")[:40])
        check('week %d: sets unchanged' % wk, pg.evaluate(COUNT) == n0)
    pg.evaluate("setCurrentWeek(6)"); pg.reload(); pg.wait_for_timeout(1300)
    check('the picked week holds after a reload', pg.evaluate("currentTrainWeek") == 5)
    tg = pg.evaluate("(()=>{const ex=splitDayExercises('chest')[0];return [getSessionTarget(ex,getHistory(ex.id)).weight, prevWeekEntry(getHistory(ex.id),5,ex).week]})()")
    check('week 6 picked: targets come from week 5', tg[1] == 4, tg)
    ctx.close()
    # 7. Do this workout today.
    for when, slot, day, name in [(MON, 4, 'chest-b', 'Friday on Monday'), (datetime.datetime(2026, 11, 25, 18, 0), 1, 'arms', 'skipped Tuesday on Wednesday'), (datetime.datetime(2026, 11, 26, 18, 0), 4, 'chest-b', 'Friday on Thursday, a rest day')]:
        ctx, pg, errs = open_at(b, when)
        vol0 = pg.evaluate("lastWeekVolume()")
        pg.evaluate("selectSlot(%d)" % slot); pg.wait_for_timeout(200)
        pg.evaluate("[...document.querySelectorAll('#tab-today button')].find(b=>b.innerText.trim()==='Do this workout today').click()"); pg.wait_for_timeout(300)
        n = len(pg.evaluate(LOG, [day, 7, 2])); pg.wait_for_timeout(300)
        st = pg.evaluate(STRIP).split(' ')
        ti = pg.evaluate("wsToday()")
        check('%s: %s shows done' % (name, ['Mon','Tue','Wed','Thu','Fri'][slot]), st[slot].endswith(':done'), st)
        check('%s: today stays as planned' % name, st[ti].endswith(':open') or st[ti].endswith(':rest'), st)
        check('%s: sets are dated today under %s' % (name, day), pg.evaluate("(d)=>Object.values(sessions).flat().filter(e=>e.d===todayKey()&&e.day===d).length", day) == n)
        check('%s: last week volume unchanged' % name, pg.evaluate("lastWeekVolume()") == vol0)
        if name.startswith('Friday on Monday'):
            go(pg, 'today')
            pg.evaluate("undoTakeToday('chest-b')"); c = card(pg).upper()
            check('Restore: Monday is back to Chest and Back, Friday stays done', 'CHEST + BACK' in c and pg.evaluate(STRIP).split(' ')[4].endswith(':done'), [c, pg.evaluate(STRIP)])
        check('%s: no page errors' % name, not errs, errs); ctx.close()
    ctx, pg, errs = open_at(b, datetime.datetime(2026, 11, 27, 9, 0)); pg.screenshot(path=shot('8391-friday-390.png'), full_page=True)
    check('Friday clock: Chest B leads, no stale marks', 'TODAY' in card(pg).upper() and pg.evaluate(STRIP).count(':done') == 0, [card(pg), pg.evaluate(STRIP)]); ctx.close()
    # 8. Reset this week keeps every set.
    ctx, pg, errs = open_at(b, MON)
    pg.evaluate(LOG, ['chest', 2, 1]); pg.evaluate("setSessionLength('arms','short');addToDay&&addToDay('legs',Object.keys(EX_BY_ID).find(id=>!splitDayExercises('legs').some(x=>x.id===id)))")
    n0 = pg.evaluate(COUNT)
    pg.evaluate("askResetWeek('tbResetAsk')"); ask = pg.evaluate("tbResetAsk.innerText")
    check('Reset confirm line', 'This week goes back to your plan. Your logged sets stay.' in ask, ask)
    pg.evaluate("resetThisWeek()"); pg.wait_for_timeout(300)
    check('Reset keeps every set', pg.evaluate(COUNT) == n0, [n0, pg.evaluate(COUNT)])
    check('Reset clears Short, added lifts and the open workout', not any(k.startswith('6|') for k in pg.evaluate("Object.keys(shortDays).concat(Object.keys(dayAdded))")) and 'IN PROGRESS' not in card(pg).upper(), card(pg))
    ctx.close()
    # 9. Weight carryover.
    for unit in ['lb', 'kg']:
        ctx, pg, errs = open_at(b, MON)
        if unit == 'kg': pg.evaluate("localStorage.setItem('monk_weight_unit_v1','kg')"); pg.reload(); pg.wait_for_timeout(1300)
        r = pg.evaluate("""(()=>{const out={};
          const part=splitDayExercises('chest')[0], skip=splitDayExercises('chest')[5], full=splitDayExercises('arms-b')[0];
          for (const [k,ex] of [['one set, unfinished day',part],['skipped lift',skip],['full day',full]]) {
            const h=getHistory(ex.id), last=h.filter(e=>e.week<6&&e.weight).sort((a,b)=>a.week-b.week||(a.d<b.d?-1:1)).pop();
            out[k]=[getSessionTarget(ex,h).weight, last.week, last.weight, roundToNearestFive(last.weight*(1+WEEKLY_PCT))];}
          return out})()""")
        for k, v in r.items(): check('%s carryover, %s: target from the latest logged top set (week %d, %s) plus progression' % (unit, k, v[1] + 1, v[2]), v[0] == max(v[2], v[3]), v)
        ctx.close()
    # 10. Backups: a backup made by 8.39 loads, and the new fields round trip.
    common.T0 = MON
    ctx, pg, errs = page(b, 390, 844, seed=False, url='http://localhost:8767/index.html')
    pg.evaluate(FIX); pg.reload(); pg.wait_for_timeout(1300)
    old = pg.evaluate("""()=>new Promise(res=>{const o=URL.createObjectURL;URL.createObjectURL=bl=>{bl.text().then(res);return o.call(URL,bl)};exportData();})""")
    oldn = pg.evaluate(COUNT); ctx.close()
    ctx, pg, errs = page(b, 390, 844, seed=False)
    imp = """(txt)=>{const dt=new DataTransfer();dt.items.add(new File([txt],'b.json'));const i=document.createElement('input');i.type='file';i.files=dt.files;importData(i);}"""
    pg.evaluate(imp, old); pg.wait_for_timeout(2000); pg.reload(); pg.wait_for_timeout(1300); go(pg, 'today')
    check('an 8.39 backup loads every set', pg.evaluate(COUNT) == oldn and oldn > 0, [oldn, pg.evaluate(COUNT)])
    check('after the 8.39 backup: fresh full Chest and Back, no marks', 'CHEST + BACK' in card(pg).upper() and 'SHORT' not in card(pg).upper() and pg.evaluate(STRIP).count(':open') == 6, [card(pg), pg.evaluate(STRIP)])
    pg.evaluate(LOG, ['chest', 1, 1]); pg.evaluate("startFresh('chest');setCurrentWeek(7)")
    new = pg.evaluate("""()=>new Promise(res=>{const o=URL.createObjectURL;URL.createObjectURL=bl=>{bl.text().then(res);return o.call(URL,bl)};exportData();})""")
    nb = json.loads(new)
    check('a new backup carries the week anchor and the closed flag', nb.get('weekAnchor') == {'week': 6, 'monday': '2026-11-23'} and any(e.get('closed') for h in nb['sessions'].values() for e in h), nb.get('weekAnchor'))
    ctx.close()
    ctx, pg, errs = page(b, 390, 844, seed=False, url='http://localhost:8767/index.html')
    pg.evaluate(imp, new); pg.wait_for_timeout(2000)
    check('the new backup still loads in 8.39 with every set', pg.evaluate(COUNT) == sum(len([k for k in ['s1','s2','s3','s4','s5','s6'] if e.get(k)]) for h in nb['sessions'].values() for e in h))
    check('backups: no page errors', not errs, errs); ctx.close()
    b.close()
sys.exit(1 if done() else 0)
