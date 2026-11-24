"""8.34 fix (8.37: Short button and Restore line replace the Normal/Short toggle): switch a workout between Short and Normal at any time, both ways, with sets already logged. Logged data never changes."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
#  8.39: Today opens today's planned workout. These checks need a day Short
#  shortens (Upper A); Upper B is not shortened, so the clock sits on Monday.
import common, datetime; common.T0 = datetime.datetime(2026, 11, 16, 10, 0, 0)
from playwright.sync_api import sync_playwright
LOGS="(()=>{const o={};Object.keys(sessions).sort().forEach(k=>o[k]=sessions[k]);return JSON.stringify(o)})()"
STORE="(()=>{const o=JSON.parse(localStorage.getItem('monk_sessions_v1')||'{}');const r={};Object.keys(o).sort().forEach(k=>r[k]=o[k]);return JSON.stringify(r)})()"
def ids(pg, d): return pg.evaluate("paList('%s').map(e=>e.id)"%d)
def log_on(pg, ex, w, r):
    pg.evaluate("PA.ex='%s';PA.slot=null;PA.key=null;renderPlanActive()"%ex)
    pg.evaluate("PA.wLb=%s;PA.r=%s"%(w,r)); pg.click('#paLogBtn'); pg.wait_for_timeout(350)
    pg.evaluate("dismissTimer&&dismissTimer();document.querySelectorAll('.rest-modal-overlay').forEach(m=>m.classList.remove('visible'))")
# 8.37: Short is one pressed button in the day row; Normal comes back through the Restore line.
ADJ={'#planActive':'#planActive .day-adj','#tbWork':'#tbAdj .day-adj'}
def pressed(pg, sel):
    v=pg.evaluate("(()=>{const b=document.querySelector('%s .day-adj-btn');return b?b.getAttribute('aria-pressed'):null})()"%ADJ[sel])
    return 'Normal:%s,Short:%s'%('false' if v=='true' else 'true', v)
def restore(pg, sel): pg.click(sel+' .restore-btn')
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg,errs=page(b,390,844)
    go(pg,'today'); pg.click('.tb-start'); pg.wait_for_timeout(500)
    D=pg.evaluate("PA.day")
    full=ids(pg,D)
    check('Plan card shows Normal pressed before the workout', pressed(pg,'#planActive')=='Normal:true,Short:false', pressed(pg,'#planActive'))
    tg=pg.evaluate("[...document.querySelectorAll('#planActive .day-adj-btn')].map(b=>{const r=b.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})")
    check('Short and Change workout are 44 px or taller', all(h>=44 and w>=44 for w,h in tg), tg)
    # what Short keeps and drops, without changing anything
    # before the workout: Short, then Normal, nothing logged yet
    pg.evaluate("setSessionLength('%s','short')"%D); pg.wait_for_timeout(400)
    shortList=ids(pg,D)
    check('Short before the workout', pg.evaluate("sessionIsShort('%s')"%D) and pressed(pg,'#planActive')=='Normal:false,Short:true')
    restore(pg,'#planActive'); pg.wait_for_timeout(400)
    check('Normal again before the workout', not pg.evaluate("sessionIsShort('%s')"%D) and ids(pg,D)==full, ids(pg,D))
    dropped=[x for x in full if x not in shortList]; kept=[x for x in full if x in shortList]
    check('the short session is shorter than the normal one', len(shortList)<len(full) and kept and dropped, [len(full),len(shortList)])
    # log before switching: two sets on a kept lift, one on a lift Short drops
    log_on(pg,kept[0],135,8); log_on(pg,kept[0],135,7); log_on(pg,dropped[-1],40,12)
    before=pg.evaluate(LOGS); storedBefore=pg.evaluate(STORE)
    check('three sets are logged', pg.evaluate("[slotLogged(EX_BY_ID['%s'],'s1'),slotLogged(EX_BY_ID['%s'],'s2'),slotLogged(EX_BY_ID['%s'],'s1')]"%(kept[0],kept[0],dropped[-1]))==[True,True,True])
    # Normal to Short during the workout
    pg.evaluate("setSessionLength('%s','short')"%D); pg.wait_for_timeout(500)
    # 8.35b: a lift Short drops stays on the day, marked added, once a set is logged on it.
    check('Short is on and the card shows the short list plus the logged lift', pg.evaluate("sessionIsShort('%s')"%D) and ids(pg,D)==shortList+[dropped[-1]] and pressed(pg,'#planActive')=='Normal:false,Short:true', [ids(pg,D),shortList])
    check('switching to Short changes no logged data', pg.evaluate(LOGS)==before)
    check('the stored copy is unchanged too', pg.evaluate(STORE)==storedBefore)
    check('the set on the dropped lift is still logged', pg.evaluate("slotLogged(EX_BY_ID['%s'],'s1')"%dropped[-1]))
    # log during Short
    k2=kept[1] if len(kept)>1 else kept[0]
    log_on(pg,k2,95,10)
    mid=pg.evaluate(LOGS); storedMid=pg.evaluate(STORE); mo=json.loads(mid); bo=json.loads(before)
    check('logging during Short adds only the new set', all(mo.get(k)==v for k,v in bo.items() if k!=k2) and k2 in mo, [k for k in mo if mo.get(k)!=bo.get(k)])
    # Short back to Normal during the workout
    restore(pg,'#planActive'); pg.wait_for_timeout(500)
    check('Normal is back with the full list', not pg.evaluate("sessionIsShort('%s')"%D) and ids(pg,D)==full and pressed(pg,'#planActive')=='Normal:true,Short:false', ids(pg,D))
    check('switching back to Normal changes no logged data', pg.evaluate(LOGS)==mid and pg.evaluate(STORE)==storedMid)
    vals=pg.evaluate("['s1w-%s','s2w-%s','s1w-%s'].map(i=>document.getElementById(i)&&document.getElementById(i).value)"%(kept[0],kept[0],dropped[-1]))
    check('every logged set shows again in its row', vals and abs(float(vals[0])-135)<0.01 and abs(float(vals[1])-135)<0.01 and abs(float(vals[2])-40)<0.01, vals)
    # and back again, from Today, before going on
    go(pg,'today')
    check('Today shows the same choice', pressed(pg,'#tbWork')=='Normal:true,Short:false', pressed(pg,'#tbWork'))
    pg.evaluate("setSessionLength('%s','short')"%D); pg.wait_for_timeout(400)
    check('Short from Today', pg.evaluate("sessionIsShort('%s')"%D) and pressed(pg,'#tbWork')=='Normal:false,Short:true')
    restore(pg,'#tbWork'); pg.wait_for_timeout(400)
    check('Normal from Today', not pg.evaluate("sessionIsShort('%s')"%D))
    check('Today switches change no logged data', pg.evaluate(LOGS)==mid)
    # the choice and the data survive a reload
    pg.evaluate("setSessionLength('%s','short')"%D); pg.wait_for_timeout(300)
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    check('after a reload Short is kept and the data is unchanged', pg.evaluate("sessionIsShort('%s')"%D) and pg.evaluate(LOGS)==mid and pg.evaluate(STORE)==storedMid)
    # the old path that failed: Quick Log now aims at this day and offers the full plan
    pg.evaluate("openQuickLog(null,'%s')"%D); pg.wait_for_timeout(400)
    check('Quick Log aims at the short day that has sets logged', pg.evaluate("quickTargetDay()")==D, pg.evaluate("quickTargetDay()"))
    check('Quick Log offers Use the full plan instead', pg.evaluate("!!document.querySelector('#qlToday .quicklog-back')"))
    pg.click('#qlToday .quicklog-back'); pg.wait_for_timeout(400)
    check('Use the full plan instead brings Normal back', not pg.evaluate("sessionIsShort('%s')"%D) and pg.evaluate(LOGS)==mid)
    an=pg.evaluate("lenSay.textContent")
    check('the switch is announced without dashes or exclamation marks', not any(c in an for c in '-–—!'), an)
    # 8.35b: tapping Short opens the time picker instead of trimming in place.
    go(pg,'today'); pg.click('#tbAdj .day-adj-btn:has-text("Short")'); pg.wait_for_timeout(400)
    check('8.35b: Short opens the time picker', pg.evaluate("document.body.dataset.tab")=='quicklog' and pg.evaluate("quicklogSection.classList.contains('ql-short')"))
    check('no page errors', not errs, errs); ctx.close()
sys.exit(1 if done() else 0)
