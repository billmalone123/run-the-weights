"""8.32 Food locked: only the hero and the coming soon message, Open Body, no food inputs reachable, data kept."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
EXPORT="(()=>{let out=null;const o=URL.createObjectURL;const a=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};URL.createObjectURL=function(bl){out=bl;return 'blob:x'};exportData();URL.createObjectURL=o;HTMLAnchorElement.prototype.click=a;return out?out.text():null})()"
STORE="(()=>{const o={};['monk_food_logs_v1','monk_food_targets_v1','monk_bodyweight_v1','monk_goal_mode_v1'].forEach(k=>o[k]=localStorage.getItem(k));return o})()"
VIS="""()=>{const tab=document.getElementById('tab-food');return [...tab.children].filter(c=>c.offsetParent).map(c=>c.id||c.className)}"""
CTRL="""()=>[...document.querySelectorAll('#tab-food input,#tab-food select,#tab-food textarea,#tab-food button,#tab-food a[href],#tab-food [contenteditable],#tab-food [tabindex]')].filter(e=>e.offsetParent||e.getClientRects().length).map(e=>e.id||e.innerText.trim()||e.tagName)"""
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=page(b,360,700)
    pg.evaluate("""localStorage.setItem('monk_food_logs_v1',JSON.stringify({'2026-11-18':[{id:'m1',name:'Oats',time:'08:00',items:[{name:'Oats',cal:300,protein:10,carb:50,fat:6}]}],'2026-11-19':[{id:'m2',name:'Eggs',time:'07:30',items:[{name:'Eggs',cal:210,protein:18,carb:1,fat:15}]}]}));
      localStorage.setItem('monk_food_targets_v1',JSON.stringify({cal:2400,protein:150,goalWeight:180}));localStorage.setItem('monk_goal_mode_v1','cut');
      localStorage.setItem('monk_bodyweight_v1',JSON.stringify({'2026-11-01':180,'2026-11-12':184.6,'2026-11-19':183.2}))""")
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    before=pg.evaluate(STORE)
    check('seeded food data present', before['monk_food_logs_v1'] not in (None,'{}'), (before['monk_food_logs_v1'] or '')[:80])
    check('flag is off', pg.evaluate("FOOD_ENABLED===false && document.documentElement.classList.contains('food-off')"))
    go(pg,'food')
    v=pg.evaluate(VIS)
    check('Food tab shows only the hero and the coming soon message', v==['hero-food','foodSoon'], v)
    h=pg.evaluate("(()=>{const h=document.getElementById('hero-food');return [h.hidden,h.querySelector('.rtwh-word').innerText.replace(/[^A-Z]/g,''),getComputedStyle(h.querySelector('.rtwh-dot')).backgroundColor,h.querySelector('.rtwh-line').textContent]})()")
    check('hero stays: FOOD with the persimmon square', h[0]==False and h[1]=='FOOD' and h[2]=='rgb(242, 85, 44)', h)
    t=pg.evaluate("[...document.querySelectorAll('#foodSoon p')].map(e=>e.innerText.trim())")
    check('message and line read exactly as specified', t==['Food tracking is coming soon.','Log your weight on Progress, then Body.'], t)
    copy=' '.join(t)+' '+pg.evaluate("document.querySelector('#foodSoon button').innerText")
    check('no dashes or exclamation marks in the new copy', not any(c in copy for c in '-–—!'), copy)
    g=pg.evaluate("(()=>{const h=document.getElementById('hero-food').getBoundingClientRect(),m=document.getElementById('foodSoonMsg').getBoundingClientRect();return Math.round(m.top-h.bottom)})()")
    check('message sits under the hero line, about 24 px below', 20<=g<=30, g)
    c=pg.evaluate(CTRL)
    check('the only control on the Food tab is the Body button', c==['Open Body'], c)
    bb=pg.evaluate("(()=>{const r=document.querySelector('#foodSoon button').getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})()")
    check('button is 44 px tall or more', bb[1]>=44, bb)
    pg.evaluate("document.activeElement&&document.activeElement.blur();scrollTo(0,0)"); seen=[]
    for i in range(40):
        pg.keyboard.press('Tab'); seen.append(pg.evaluate("(()=>{const a=document.activeElement;return a?(a.closest('#foodSection')?'FOOD':(a.closest('#tab-food')?'tab':'other')):'none'})()"))
    check('keyboard Tab never reaches a food input', 'FOOD' not in seen, seen[:12])
    check('food inputs are kept in the page behind the flag', pg.evaluate("!!document.getElementById('foodWeighToday')&&!!document.getElementById('foodNote')&&getComputedStyle(document.getElementById('foodSection')).display==='none'"))
    check('no horizontal scroll at 360', pg.evaluate("document.documentElement.scrollWidth<=innerWidth"))
    pg.screenshot(path=shot('832-food-360.png'))
    # turning the flag on brings Food back as it was in 8.31
    pg.evaluate(FOOD_ON); go(pg,'food')
    on=pg.evaluate("(()=>{const h=document.getElementById('hero-food').getBoundingClientRect(),w=document.getElementById('foodWeighTop').getBoundingClientRect();return [getComputedStyle(document.getElementById('foodSoon')).display,!!document.getElementById('foodWeighToday').offsetParent,Math.round(w.top-h.bottom)]})()")
    check('with the flag on, Food returns with its 24 px gap and no coming soon block', on[0]=='none' and on[1] and 20<=on[2]<=30, on)
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')"); go(pg,'food')
    pg.click('#foodSoon button'); pg.wait_for_timeout(500)
    o=pg.evaluate("[!!document.getElementById('tab-calendar').offsetParent,_progView,!!(document.getElementById('bwForm')||{}).offsetParent,document.getElementById('progTabBody').getAttribute('aria-selected')]")
    check('button opens Progress on the Body view', o==[True,'body',True,'true'], o)
    rows=pg.evaluate("[...document.querySelectorAll('#progView .bw-row')].map(r=>r.innerText.replace(/\\s+/g,' '))")
    check('weights saved from Food still show on Body', any('Nov 19 183.2 lb' in r for r in rows) and any('Nov 12 184.6 lb' in r for r in rows), rows[:3])
    # 8.37: while Food is locked the bar has four tabs and no Food; there is no menu to hold it.
    check('Food is out of the bar while locked, four tabs', pg.evaluate("!document.querySelector('#tabbar [data-tab=food]').offsetParent&&[...document.querySelectorAll('#tabbar .tabbar-btn')].filter(b=>b.offsetParent).length===4&&!document.getElementById('navMenu')"))
    # Today and onboarding
    go(pg,'today')
    td=pg.evaluate("[!!document.querySelector('.today-food-card').offsetParent,[...document.querySelectorAll('#tab-today button,#tab-today a')].filter(e=>e.offsetParent).map(e=>e.innerText.trim()).filter(t=>/meal|food/i.test(t)),!!document.getElementById('todayWeight').offsetParent]")
    check('Today has no food card and nothing that points to logging food', td[0]==False and td[1]==[], td)
    check('Today keeps its bodyweight card', td[2])
    check('setup finish has no Log a meal button', pg.evaluate("getComputedStyle(document.querySelector('.onb-finish-food')).display")=='none')
    check('Start lifting stays on the setup finish', pg.evaluate("[...document.querySelectorAll('#onbFlowScreen3 button')].some(b=>b.innerText.trim()==='Start lifting'&&getComputedStyle(b).display!=='none')"))
    # data survives
    pg.reload(); pg.wait_for_timeout(1500)
    check('food and weight data unchanged after a reload', pg.evaluate(STORE)==before)
    bk=pg.evaluate(EXPORT); data=json.loads(bk)
    check('backup still carries food logs, targets, weights and goal mode', data.get('foodLogs')==json.loads(before['monk_food_logs_v1']) and data.get('bodyweight')==json.loads(before['monk_bodyweight_v1']) and 'foodTargets' in data, sorted(k for k in data if 'ood' in k or 'body' in k.lower()))
    errs1=list(errs); ctx.close()
    ctx,pg,errs=page(b,360,700,seed=False); pg.on('dialog', lambda d: d.accept())
    pg.set_input_files('input[type=file][accept*=json] >> nth=0', files=[{'name':'b.json','mimeType':'application/json','buffer':bk.encode()}]); pg.wait_for_timeout(900)
    pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    aft=pg.evaluate(STORE)
    check('restore brings back the food logs and weights unchanged', json.loads(aft['monk_food_logs_v1'])==json.loads(before['monk_food_logs_v1']) and json.loads(aft['monk_bodyweight_v1'])==json.loads(before['monk_bodyweight_v1']), [str(aft)[:120]])
    go(pg,'food')
    check('after restore Food still shows only the coming soon state', pg.evaluate(VIS)==['hero-food','foodSoon'])
    check('no page errors', not errs1 and not errs, errs1+errs); ctx.close()
    # fresh install: the Food tip never shows
    ctx,pg,errs=page(b,360,700,init="localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');localStorage.setItem('monk_tips_seen_v1',JSON.stringify({v:1,seen:{today:1,plan:1,lnote:1,wnote:1,quicklog:1,progress:1,run:1,style:1,menu:1,body:1}}));")
    go(pg,'food'); pg.evaluate("tipSchedule(0)"); pg.wait_for_timeout(500)
    check('the Food tip does not show', not pg.evaluate("!!document.getElementById('tipBox')"), pg.evaluate("_tipId"))
    check('no page errors (tip)', not errs, errs); ctx.close()
sys.exit(1 if done() else 0)
