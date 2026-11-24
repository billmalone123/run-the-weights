"""8.35b Part A: one day, one log. Cases A to E on three plans, reloads, Short and Normal storage, backups, old Quick Log totals."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
#  8.39: Today opens today's planned workout. These checks need a day Short
#  shortens (Upper A); Upper B is not shortened, so the clock sits on Monday.
import common, datetime; common.T0 = datetime.datetime(2026, 11, 16, 10, 0, 0)
from playwright.sync_api import sync_playwright
PLANS = [('upper and lower', ''), ('arnold', "setSplit('arnold')"), ('advanced runner', "setAdvanced(true);setRunning(true)")]
STORE = "JSON.stringify([localStorage.getItem('monk_sessions_v1'),localStorage.getItem('monk_day_added_v1')])"
CLOSE = "document.querySelectorAll('.settings-modal-overlay').forEach(m=>{if(m.id!=='dayTakeover')m.style.display='none'})"
def ids(pg, d): return pg.evaluate("paList('%s').map(e=>e.id)" % d)
def log_on(pg, ex, w, r):
    pg.evaluate("PA.ex='%s';PA.slot=null;PA.key=null;renderPlanActive()" % ex)
    pg.evaluate("PA.wLb=%s;PA.r=%s" % (w, r)); pg.click('#paLogBtn'); pg.wait_for_timeout(300)
    pg.evaluate("dismissTimer&&dismissTimer();document.querySelectorAll('.rest-modal-overlay').forEach(m=>m.classList.remove('visible'))")
def logged(pg, d, ex): return pg.evaluate("(()=>{var e=EX_BY_ID['%s'];for(var n=1;n<=6;n++)if(slotLogged(e,'s'+n))return true;return quickSetsOn('%s','%s').length>0})()" % (ex, d, ex))
def reload(pg, d):
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate(CLOSE)
    pg.evaluate("goTab('training');switchDay('%s');PA.day='%s';renderPlanActive()" % (d, d)); pg.wait_for_timeout(300)
def fresh(b, setup):
    ctx, pg, errs = page(b, 390, 844)
    if setup: pg.evaluate(setup); pg.reload(); pg.wait_for_timeout(1500); pg.evaluate(CLOSE)
    go(pg, 'today'); pg.click('.tb-start'); pg.wait_for_timeout(400)
    return ctx, pg, errs, pg.evaluate("PA.day")
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, setup in PLANS:
        # A: log, then Short. A logged lift that Short drops stays on the day, marked added.
        ctx, pg, errs, D = fresh(b, setup); full = ids(pg, D)
        pg.evaluate("setSessionLength('%s','short')" % D); sh = ids(pg, D); pg.evaluate("setSessionLength('%s','normal')" % D)
        dropped = [x for x in full if x not in sh]
        check(name + ': Short drops a lift on this plan', len(dropped) > 0, [len(full), len(sh)])
        log_on(pg, dropped[-1], 40, 12); before = pg.evaluate(STORE)
        pg.evaluate("setSessionLength('%s','short')" % D); pg.wait_for_timeout(300)
        check(name + ' A: the logged lift stays on the short day', dropped[-1] in ids(pg, D) and logged(pg, D, dropped[-1]))
        check(name + ' A: it is marked added', pg.evaluate("isAddedOn('%s','%s')" % (D, dropped[-1])))
        check(name + ' A: Short changes no stored data', pg.evaluate(STORE) == before)
        reload(pg, D)
        check(name + ' A after reload', pg.evaluate("sessionIsShort('%s')" % D) and dropped[-1] in ids(pg, D) and logged(pg, D, dropped[-1]))
        check(name + ' A: no page errors', not errs, errs); ctx.close()
        # B: a Quick Log set on a planned lift shows and counts on that day.
        ctx, pg, errs, D = fresh(b, setup); ex = ids(pg, D)[0]
        pr0 = pg.evaluate("dayProgress('%s')" % D)
        pg.evaluate("quickLogSet('%s',100,5,null,'')" % ex)
        go(pg, 'training'); pg.evaluate("switchDay('%s');PA.day='%s';PA.ex='%s';renderPlanActive()" % (D, D, ex))
        pr1 = pg.evaluate("dayProgress('%s')" % D)
        check(name + ' B: the Quick Log set counts for the day', pg.evaluate("hasLogsForDay('%s',currentTrainWeek)" % D) and pr1['done'] == pr0['done'] + 1, [pr0, pr1])
        check(name + ' B: the card shows it (8.37 copy: Single sets)', 'Single sets' in pg.evaluate("document.querySelector('.pa-sub').textContent"))
        check(name + ' B: the entry carries the day', pg.evaluate("(sessions['%s']||[]).slice(-1)[0].day" % ex) == D)
        reload(pg, D)
        check(name + ' B after reload (case D)', pg.evaluate("dayProgress('%s').done" % D) == pr1['done'] and pg.evaluate("hasLogsForDay('%s',currentTrainWeek)" % D))
        check(name + ' B: no page errors', not errs, errs); ctx.close()
        # C: Short first, log, back to Normal.
        ctx, pg, errs, D = fresh(b, setup)
        pg.evaluate("setSessionLength('%s','short')" % D); k0 = ids(pg, D)[0]
        log_on(pg, k0, 95, 8); before = pg.evaluate(STORE)
        pg.evaluate("setSessionLength('%s','normal')" % D); pg.wait_for_timeout(300)
        check(name + ' C: back to Normal keeps the set', not pg.evaluate("sessionIsShort('%s')" % D) and logged(pg, D, k0) and pg.evaluate(STORE) == before)
        reload(pg, D)
        check(name + ' C after reload', not pg.evaluate("sessionIsShort('%s')" % D) and logged(pg, D, k0))
        ctx.close()
        # E: pick a Quick Log workout after logging on the planned day.
        ctx, pg, errs, D = fresh(b, setup); first = ids(pg, D)[0]
        log_on(pg, first, 135, 8); before = pg.evaluate("localStorage.getItem('monk_sessions_v1')")
        go(pg, 'today'); pg.evaluate("openQuickLog(null,'%s')" % D); pg.wait_for_timeout(300)
        check(name + ' E: the target is today, not the next day', pg.evaluate("quickTargetDay()") == D, pg.evaluate("quickTargetDay()"))
        pg.evaluate("_qlOpen='full';renderQuickLog()"); pg.click('#qlOthers .today-start'); pg.wait_for_timeout(300)
        msg = pg.evaluate("document.getElementById('dayTakeover').style.display!=='none'&&dayTakeoverMsg.textContent")
        check(name + ' E: asks first', msg == 'Switch today to Full body? Your logged sets stay.', msg)
        check(name + ' E: nothing changed before the answer', not pg.evaluate("quickFor('%s',currentTrainWeek)" % D))
        pg.click('#dayTakeoverYes'); pg.wait_for_timeout(500)
        q = pg.evaluate("quickFor('%s',currentTrainWeek)" % D)
        check(name + ' E: takes over today', bool(q) and pg.evaluate("PA.day") == D)
        check(name + ' E: logged sets stay', pg.evaluate("localStorage.getItem('monk_sessions_v1')") == before and logged(pg, D, first))
        if first not in q['ids']: check(name + ' E: the logged lift shows as added', first in ids(pg, D) and pg.evaluate("isAddedOn('%s','%s')" % (D, first)))
        reload(pg, D)
        check(name + ' E after reload', bool(pg.evaluate("quickFor('%s',currentTrainWeek)" % D)) and logged(pg, D, first))
        check(name + ' E: no page errors', not errs, errs); ctx.close()
    # Backups: old file without the new key, new file with it, bad values.
    ctx, pg, errs = page(b, 390, 844)
    pg.evaluate("dayAdded={'6|upper-a':['flat-bb-bench']};persistDayAdded();sessions['flat-bb-bench'].push({d:'2026-11-19',week:6,weight:100,reps:5,s1:{w:100,r:5},day:'upper-a'});saveSessions()")
    with pg.expect_download() as dl: pg.evaluate("exportData()")
    data = json.load(open(dl.value.path()))
    check('backup holds the new key', data.get('dayAdded') == {'6|upper-a': ['flat-bb-bench']}, data.get('dayAdded'))
    check('backup holds the day label', data['sessions']['flat-bb-bench'][-1].get('day') == 'upper-a')
    def restore(obj):
        f = os.path.join(SHOTS, '_restore.json'); json.dump(obj, open(f, 'w'))
        pg.set_input_files('#settingsModal input[type=file], input[onchange="importData(this)"] >> nth=0', f); pg.wait_for_timeout(800)
        pg.evaluate(CLOSE)
    old = dict(data); old.pop('dayAdded'); old['sessions'] = json.loads(json.dumps(data['sessions'])); old['sessions']['flat-bb-bench'][-1].pop('day')
    restore(old)
    check('an old backup loads', pg.evaluate("sessions['flat-bb-bench'].length") == len(old['sessions']['flat-bb-bench']) and 'day' not in pg.evaluate("sessions['flat-bb-bench'].slice(-1)[0]"))
    check('an old backup leaves the new key as it was', pg.evaluate("JSON.stringify(dayAdded)") == '{"6|upper-a":["flat-bb-bench"]}')
    new = json.loads(json.dumps(data)); new['dayAdded'] = {'3|lower-a': ['bb-squat']}
    restore(new)
    check('a new backup restores the key', pg.evaluate("JSON.stringify(dayAdded)") == '{"3|lower-a":["bb-squat"]}' and pg.evaluate("localStorage.getItem('monk_day_added_v1')") == '{"3|lower-a":["bb-squat"]}')
    bad = json.loads(json.dumps(data)); bad['dayAdded'] = {'999|upper-a': ['bb-squat'], 'nope': ['bb-squat'], '2|upper-a': ['Bad Id', 'bb-squat', 'bb-squat', 5], '4|<b>': ['bb-squat']}
    bad['sessions']['flat-bb-bench'][-1]['day'] = '<img src=x>'; bad['sessions']['flat-bb-bench'][-2]['day'] = 'upper-b'
    restore(bad)
    check('out of range values are rejected', pg.evaluate("JSON.stringify(dayAdded)") == '{"2|upper-a":["bb-squat"]}', pg.evaluate("JSON.stringify(dayAdded)"))
    check('a bad day label is dropped, a good one kept', 'day' not in pg.evaluate("sessions['flat-bb-bench'].slice(-1)[0]") and pg.evaluate("sessions['flat-bb-bench'].slice(-2)[0].day") == 'upper-b')
    check('a non object key is ignored', pg.evaluate("JSON.stringify(cleanDayAdded([1,2]))+JSON.stringify(cleanDayAdded('x'))") == '{}{}')
    check('backups: no page errors', not errs, errs); ctx.close()
    # Old Quick Log entries (no day field) load with the same totals as master.
    OLDQ = """(()=>{var s=JSON.parse(localStorage.getItem('monk_sessions_v1'));
      [['flat-bb-bench','2026-11-12',5,135,5],['bb-squat','2026-11-13',5,185,3],['flat-bb-bench','2026-11-17',6,140,5],['bb-deadlift','2026-11-18',6,225,2]].forEach(function(r){
        (s[r[0]]=s[r[0]]||[]).push({d:r[1],ts:Date.parse(r[1]+'T12:00:00'),week:r[2],weight:r[3],reps:r[4],quickLog:true});});
      localStorage.setItem('monk_sessions_v1',JSON.stringify(s));})();0"""
    ctx, pg, errs = page(b, 390, 844); pg.evaluate(OLDQ); pg.reload(); pg.wait_for_timeout(1500)
    tot = pg.evaluate("[lastWeekVolume(),weekStreak(),paSessionsIn('2026-11-09','2026-11-16'),paSessionsIn('2026-11-16','2026-11-23'),allQuickLogEntries().length]")
    #  Values measured on master (2ff0525 tree, build 8.34) with the same data.
    check('old Quick Log entries give the same totals as before', tot == [96350, 6, 6, 2, 4], tot)
    check('old Quick Log entries are not rewritten', pg.evaluate("Object.values(sessions).flat().filter(e=>e.quickLog&&!e.ts).length") == 0 and pg.evaluate("Object.values(sessions).flat().filter(e=>e.quickLog&&'day' in e).length") == 0)
    print('totals', tot)
    check('totals: no page errors', not errs, errs); ctx.close()
sys.exit(1 if done() else 0)
