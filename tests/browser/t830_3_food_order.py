"""8.30 item 3: Food weigh in first, meal input above the totals, other blocks keep their order."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'t830_2_recent_workouts.py')).read().split('with sync_playwright')[0].split('from playwright.sync_api import sync_playwright')[1])  # LUM
ORDER="""()=>[...document.getElementById('foodSection').children].filter(e=>e.offsetParent||e.id==='foodDraft').map(e=>e.id||(e.querySelector('#foodNote')?'mealInput':e.querySelector('.quicklog-recent-title')?e.querySelector('.quicklog-recent-title').innerText:e.className))"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for W in (360,390):
        ctx,pg,errs=page(b,W,700)
        pg.evaluate(FOOD_ON)
        pg.evaluate("bodyweight['2026-11-17']=184;persistBodyweight()")
        go(pg,'food')
        o=pg.evaluate(ORDER); oo=baseline('830-food-order-%d'%W,o)
        print('  new',o); print('  old',oo)
        check('%d Food: weigh in is the first thing under the hero'%W, o[0]=='foodWeighTop', o[:2])
        check('%d Food: meal input sits above the daily totals'%W, o.index('mealInput')<o.index('foodTotals'), o)
        rest_new=[x for x in o if x not in ('foodWeighTop','mealInput','foodDraft')]; rest_old=[x for x in oo if x not in ('mealInput','foodDraft','section-label','section-title train-title')]
        check('%d Food: every other block kept in its order'%W, rest_new==[x for x in rest_old if x!='foodWeighTop'], (rest_new,rest_old))
        top=pg.evaluate("(()=>{const h=document.getElementById('hero-food').getBoundingClientRect().bottom;const w=document.getElementById('foodWeighTop').getBoundingClientRect();const i=document.getElementById('foodWeighToday').getBoundingClientRect();return [Math.round(w.top-h),Math.round(i.height)]})()")
        check('%d Food: weigh in directly under the hero, field 44 px tall'%W, 20<=top[0]<=30 and top[1]>=44, top)
        last=pg.evaluate("(()=>{const e=document.getElementById('foodWeighLast');return [e.innerText,parseFloat(getComputedStyle(e).fontSize)]})()")
        check('%d Food: last weigh in shown small'%W, last[0]=='Last weigh in: 184 lb, Nov 17.' and last[1]<=14, last)
        cr=pg.eval_on_selector('#foodWeighLast',LUM); check('%d Food: last weigh in contrast 4.5:1 or better'%W, cr>=4.5, round(cr,2))
        check('%d Food: one weigh in field on the screen'%W, pg.evaluate("document.querySelectorAll('#foodSection input[id*=Weigh]').length")==1 and pg.evaluate("!document.getElementById('foodWeighIn')"))
        pg.fill('#foodWeighToday','185.24'); pg.press('#foodWeighToday','Tab'); pg.wait_for_timeout(200)
        check('%d Food: typing a weight saves it to bodyweight for today'%W, pg.evaluate("bodyweight['2026-11-19']")==185.2 and pg.evaluate("JSON.parse(localStorage.getItem('monk_bodyweight_v1'))['2026-11-19']")==185.2)
        go(pg,'today'); check('%d Today shows the same weight'%W, pg.evaluate("document.getElementById('todayWeight').value")=='185.2', pg.evaluate("document.getElementById('todayWeight').value"))
        pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')"); pg.evaluate(FOOD_ON); go(pg,'food')
        check('%d Food: logged today shows in the field after reload'%W, pg.evaluate("document.getElementById('foodWeighToday').value")=='185.2')
        pg.fill('#foodWeighToday','186'); pg.press('#foodWeighToday','Tab'); pg.wait_for_timeout(200)
        check('%d Food: it can be edited'%W, pg.evaluate("bodyweight['2026-11-19']")==186)
        bwt=pg.evaluate("document.getElementById('foodWeight').innerText")
        check('%d Food: Bodyweight block keeps its weekly average and notes'%W, 'Weekly average' in bwt and 'weekly average matters' in bwt, bwt[:80])
        # stepping to another day keeps the weigh in as today
        pg.evaluate("stepFoodDay(-1)"); pg.wait_for_timeout(200)
        check('%d Food: the weigh in stays today when another day is shown'%W, pg.evaluate("document.getElementById('foodWeighToday').value")=='186')
        pg.evaluate("stepFoodDay(0)")
        pg.screenshot(path=shot('p3-%d.png')%W)
        check('%d no page errors'%W, not errs, errs[:3]); ctx.close()
    # fresh install: the Food tip is true and anchored at the weigh in
    ctx,pg,errs=page(b,360,700,seed=False,init="localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');")
    pg.evaluate(FOOD_ON); go(pg,'food'); pg.wait_for_timeout(600)
    t=pg.evaluate("(()=>{const t=document.querySelector('.tip');return t?[t.innerText.replace('Got it','').trim(),t.previousElementSibling&&t.previousElementSibling.id]:null})()")
    check('Fresh install: Food tip shows under the weigh in, under 15 words', t and t[1]=='foodWeighTop' and len(t[0].split())<15 and '-' not in t[0], t)
    check('no page errors (fresh)', not errs, errs[:3]); ctx.close()
sys.exit(1 if done() else 0)
