"""8.40.1: the block card on the 8.39.1 date rule. Week 10 done at 70 percent of each day's lifts, and a workout
in progress today comes before the block card."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
BS = open(os.path.join(HERE, 'block_seed.js')).read()
def card(pg): return pg.evaluate("!!document.querySelector('#tbWork.tb-block #blkHead')")
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx, pg, errs = page(b, 390, 844, seed=False)
    pg.evaluate(BS, {}); pg.reload(); pg.wait_for_timeout(1500); go(pg, 'today')
    check('week 10 fully logged: block card shows', card(pg))
    # Drop one lift from every day of week 10: still at least 70 percent, still done.
    pg.evaluate("""(()=>{splitDayIds().forEach(d=>{const ex=buildSession(d,9).list.slice(-1)[0];sessions[ex.id]=(sessions[ex.id]||[]).filter(e=>!(e.week===9&&e.day===d))});saveSessions();})()""")
    pg.reload(); pg.wait_for_timeout(1500); go(pg, 'today')
    check('one lift short a day (70 percent or more) still ends the block', pg.evaluate("blockEnded()") and card(pg))
    # Half of one day: not done, so the block is not over while the week runs.
    pg.evaluate("""(()=>{const d=splitDayIds()[0],l=buildSession(d,9).list;l.slice(0,Math.ceil(l.length/2)).forEach(ex=>{sessions[ex.id]=(sessions[ex.id]||[]).filter(e=>!(e.week===9&&e.day===d))});saveSessions();})()""")
    pg.reload(); pg.wait_for_timeout(1500); go(pg, 'today')
    check('a day under 70 percent keeps the block open this week', not pg.evaluate("blockEnded()") and not card(pg), pg.evaluate("tbWork.innerText")[:80])
    ctx.close()
    # A workout logged in the last hours leads over the block card; Finish for today hands it back.
    ctx, pg, errs = page(b, 390, 844, seed=False)
    pg.evaluate(BS, {'shift': 1}); pg.reload(); pg.wait_for_timeout(1500); go(pg, 'today')
    check('week 10 was last calendar week: block card shows', card(pg) and pg.evaluate("blockEnded()"))
    pg.evaluate("""(()=>{const d=todayDayId()||splitDayIds()[0],ex=buildSession(d,9).list[0],t=todayKey();
      (sessions[ex.id]=sessions[ex.id]||[]).push({d:t,week:9,day:d,weight:100,reps:5,s1:{w:100,r:5},variant:activeVariant(ex)});saveSessions();
      finTimes[t+'|'+d]={s:Date.now(),l:Date.now()};finSaveTimes();window._d=d})()""")
    pg.reload(); pg.wait_for_timeout(1500); go(pg, 'today')
    c = pg.evaluate("tbWork.innerText").upper()
    check('a workout in progress today leads, the block card waits', not card(pg) and 'CONTINUE WORKOUT' in c, c[:120])
    pg.evaluate("finishForToday(window._d||todayDayId())"); pg.wait_for_timeout(300)
    check('after Finish for today the block card shows', card(pg))
    check('no page errors', not errs, errs); ctx.close()
    b.close()
sys.exit(1 if done() else 0)
