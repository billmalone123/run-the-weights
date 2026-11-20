"""8.29 hero: fit, font, square, spacing, Plan first card above the fold, real data lines, offline font."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, datetime, re
from playwright.sync_api import sync_playwright
from common import SEED, URL, ORIGIN, shot, baseline, HERE
T0=datetime.datetime(2026,11,19,10,0,0); RES=[]
def check(n, ok, d=''): RES.append((n,bool(ok),str(d)[:220])); print(('PASS ' if ok else 'FAIL ')+n+('  ['+str(d)[:220]+']' if d!='' else ''))
SEEN="localStorage.setItem('monk_tips_seen_v1',JSON.stringify({v:1,seen:{today:1,plan:1,lnote:1,wnote:1,quicklog:1,progress:1,run:1,food:1,style:1,menu:1}}));"
INIT="localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');"+SEEN
#  8.34: Today and Plan have their own headers from the references; their heroes are retired.
TABS=['quicklog','calendar','running','food']
MAX={'today':168,'training':96,'quicklog':168,'calendar':96,'running':168,'food':168}
HERO="""(t)=>{const h=document.getElementById('hero-'+t);if(!h||h.hidden)return null;const w=h.querySelector('.rtwh-word'),f=h.querySelector('.rtwh-fit'),d=h.querySelector('.rtwh-dot');const r=f.getBoundingClientRect(),dr=d.getBoundingClientRect(),fs=parseFloat(getComputedStyle(w).fontSize);
const lh=parseFloat(getComputedStyle(w).lineHeight);return {word:w.innerText,line:h.querySelector('.rtwh-line').hidden?'':h.querySelector('.rtwh-line').textContent,fs,left:r.left,right:r.right,lines:Math.round(r.height/lh),clip:w.scrollWidth>w.clientWidth+0.5,
fam:getComputedStyle(w).fontFamily,sq:[dr.width/fs,dr.height/fs],gap:(dr.left-(dr.left-parseFloat(getComputedStyle(d).marginLeft)))/fs,color:getComputedStyle(d).backgroundColor,ink:getComputedStyle(w).color,
top:w.getBoundingClientRect().top,navb:document.querySelector('nav').getBoundingClientRect().bottom,sticky:getComputedStyle(h).position,
lineFont:getComputedStyle(h.querySelector('.rtwh-line')).fontFamily,fontOk:document.fonts.check('700 100px "RTW Hero"')}}"""
CHROME="""()=>{const r=e=>e?JSON.stringify(e.getBoundingClientRect()):null;const nav=document.querySelector('nav');const gear=[...nav.querySelectorAll('button')].find(b=>/setting/i.test(b.getAttribute('aria-label')||b.id||''));
return {nav:r(nav),gear:r(gear),gearHTML:gear&&gear.outerHTML.length,tabbar:r(document.getElementById('tabbar')),tabbarHTML:document.getElementById('tabbar').innerHTML.length,logo:r(document.getElementById('navLogo'))}}"""
BELOW="""(t)=>{const tab=document.getElementById('tab-'+t);const kids=[...tab.children].filter(c=>!c.classList.contains('rtwh'));const top=kids.find(k=>k.offsetParent);const base=top?top.getBoundingClientRect().top:0;
return kids.filter(k=>k.offsetParent).map(k=>[k.id||k.tagName,Math.round(k.getBoundingClientRect().height),k.innerText.replace(/\\s+/g,' ').slice(0,400)])}"""
def page(b, url, w, h, sw=False, seed=True, init=INIT):
    ctx=b.new_context(viewport={'width':w,'height':h}, service_workers='allow' if sw else 'block'); pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.clock.install(time=T0); pg.add_init_script(init)
    pg.goto(url); pg.wait_for_timeout(900)
    if seed: pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    return ctx,pg,errs
def go(pg,t): pg.evaluate("goTab('%s');scrollTo(0,0)"%t); pg.wait_for_timeout(550)
with sync_playwright() as p:
    b=p.chromium.launch()
    for W in (360,390):
        ctx,pg,errs=page(b,URL,W,700)
        for t in TABS:
            go(pg,t)
            i=pg.evaluate(HERO,t)
            if not i: check('%d %s: hero shows'%(W,t), False); continue
            mn=40 if MAX[t]==96 else 56
            check('%d %s: %s, no clipping, inside 24 px gutters'%(W,t,i['word']), not i['clip'] and i['left']>=19.5 and i['right']<=W-23.5, (round(i['left']),round(i['right']),i['fs']))
            check('%d %s: size within max %d%s'%(W,t,MAX[t],'' if t in ('quicklog','training') else ' and min'), i['fs']<=MAX[t] and (t in ('quicklog','training') or i['fs']>=mn), i['fs'])
            check('%d %s: fills the width (largest size that fits) unless at max'%(W,t), i['fs']==MAX[t] or i['right']-i['left']>=(W-48)*0.9 or (t=='training'), (i['fs'],round(i['right']-i['left'])))
            check('%d %s: one line'%(W,t), i['lines']==1, i['lines'])
            check('%d %s: hero font is the bundled Antonio 700, line in body font'%(W,t), i['fam'].startswith('"RTW Hero"') and i['fontOk'] and 'DM Sans' in i['lineFont'])
            check('%d %s: square 18%% of size, persimmon, word in ink'%(W,t), abs(i['sq'][0]-0.18)<0.01 and abs(i['sq'][1]-0.18)<0.01 and i['color']=='rgb(242, 85, 44)' and i['ink']=='rgb(20, 20, 20)', i['sq'])
            check('%d %s: 16 px under the header, not sticky'%(W,t), abs(i['top']-i['navb']-16)<1 and i['sticky']=='static', (i['top'],i['navb']))
            # 8.31: the twelve "everything below the hero unchanged against 8.28"
            # checks were retired. See tests/README.md.
            ch=pg.evaluate(CHROME)
            check('%d %s: header, Settings icon and tab bar unchanged against the saved baseline'%(W,t), ch==baseline('829-chrome-%s-%d'%(t,W), ch), ch)
            if t=='training':
                top=pg.evaluate("[Math.round([...document.querySelectorAll('#tab-training .lift-row')].find(r=>r.offsetParent).getBoundingClientRect().top),Math.round(document.getElementById('tabbar').getBoundingClientRect().top)]")
                check('%dx700 Plan: first exercise card starts above the fold (44 px of it shows above the tab bar)'%W, top[0]+44<=top[1], top)
            if W==360:
                print('   %s: %s | %s | %dpx'%(t,i['word'],i['line'],i['fs']))
                pg.screenshot(path=shot('final-%s-360.png')%t)
        check('%d no page errors'%W, not errs, errs[:3]); ctx.close()
    # long names, rest day, freestyle, run plan line
    for W in (360,390):
        ctx,pg,errs=page(b,URL,W,700)
        pg.clock.set_system_time(datetime.datetime(2026,11,16,10)); pg.reload(); pg.wait_for_timeout(1400)
        pg.evaluate("setTrainStyle('free')")
        go(pg,'quicklog'); i=pg.evaluate(HERO,'quicklog')
        check('%d QUICK LOG on one line with the square after LOG'%W, i and i['lines']==1 and i['word'].startswith('QUICK LOG') and not i['clip'], i and (i['fs'],i['lines']))
        pg.evaluate("setTrainStyle('plan')")
        ctx.close()
    ctx,pg,errs=page(b,URL,360,700)
    pg.clock.set_system_time(datetime.datetime(2026,11,18,10)); pg.reload(); pg.wait_for_timeout(1400); go(pg,'today')
    check('rest day: Today keeps its current content, no hero', pg.evaluate("activeSplit().week[mondayIndex(startOfToday())]")=='rest' and pg.evaluate("document.getElementById('hero-today').hidden"))
    pg.evaluate("goTab('running');document.getElementById('run-race-date').value='2027-03-14';onRunInput()"); go(pg,'running'); i=pg.evaluate(HERO,'running')
    pr=pg.evaluate("plannedRunToday()")
    exp=pg.evaluate("(()=>{const pr=plannedRunToday(),wk=heroRunWeek();return pr?(wk?'Week '+wk+'. ':'')+runTypeLabel(pr.type)+' '+fmtDist(pr.miles)+' today.':(wk?'Week '+wk+'. No run planned today.':'')})()")
    check('Run line comes from the real plan (week left out while the plan is in its lead in week 0)', i and i['line']!='' and i['line']==exp, (i and i['line'], exp))
    if pr: check('Run line names the run planned today', ('today.' in i['line']), (i['line'],pr))
    pg.screenshot(path=shot('final-running-plan-360.png'))
    ctx.close()
    # offline font
    ctx=b.new_context(viewport={'width':360,'height':700}, service_workers='allow'); pg=ctx.new_page(); reqs=[]
    pg.on('request', lambda r: reqs.append(r.url)); pg.add_init_script(INIT)
    pg.goto(URL); pg.wait_for_timeout(2500)
    pg.evaluate("navigator.serviceWorker.ready.then(()=>1)"); pg.reload(); pg.wait_for_timeout(2500)
    ctl=pg.evaluate("!!navigator.serviceWorker.controller")
    fontreq=[u for u in reqs if 'antonio-latin-700' in u]
    check('hero font comes from this site only, no third party font request for it', fontreq and all(u.startswith(ORIGIN) for u in fontreq), fontreq[:2])
    ctx.set_offline(True); pg.reload(); pg.wait_for_timeout(2500); pg.evaluate("goTab('food')"); pg.wait_for_timeout(600)
    st=pg.evaluate("[...document.fonts].filter(f=>f.family.replace(/\"/g,'')==='RTW Hero').map(f=>f.status)")
    i=pg.evaluate(HERO,'food')
    check('offline load shows the hero in the bundled font', ctl and st==['loaded'] and i and i['fontOk'] and i['fam'].startswith('"RTW Hero"') and not i['clip'], (ctl,st,i and i['fs']))
    pg.screenshot(path=shot('o829-offline-food-360.png'))
    ctx.close(); b.close()
n=sum(1 for r in RES if not r[1]); print('\n%d checks, %d failed'%(len(RES),n)); sys.exit(1 if n else 0)
