"""8.27 Quick Log Add exercise, logo (8.37: no menu), About merged into The Edge, rest timer over sheets."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, datetime, re, html as H
from playwright.sync_api import sync_playwright
from common import SEED, URL, ORIGIN, shot, baseline, HERE
T0=datetime.datetime(2026,11,18,10,0,0); RES=[]
def check(n, ok, d=''): RES.append((n,bool(ok),str(d)[:200])); print(('PASS ' if ok else 'FAIL ')+n+('  ['+str(d)[:200]+']' if d!='' else ''))
# text of About and Edge before this build, to prove nothing is lost
pre=open(os.path.join(HERE,'baselines','827-about-edge-before.html')).read()
def txt(fr): return [t for t in (re.sub(r'\s+',' ',H.unescape(x)).strip() for x in re.split(r'<[^>]+>', fr)) if t and len(t)>2]
about_old=txt(re.search(r'<section id="about" class="about-short">(.*?)</section>', pre, re.S).group(1))
edge_old=txt(re.search(r'<section id="edge"[^>]*>(.*?)</section>', pre, re.S).group(1))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':360,'height':780}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d:d.accept())
    pg.clock.install(time=T0)
    pg.add_init_script("localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');")
    pg.goto(URL); pg.wait_for_timeout(1000); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    ev=pg.evaluate
    QN=lambda: ev("Object.values(sessions).reduce((n,a)=>n+a.filter(e=>e.quickLog&&e.d===todayKey()).length,0)")
    q0=QN()
    ev("goTab('quicklog');scrollTo(0,0)"); pg.wait_for_timeout(400)
    check('short on time path and time choices unchanged', pg.locator('#qlHeading').is_visible() and pg.locator('#qlTimes button').count()>=4 and pg.locator('#qlToday').is_visible())
    # 1. recent in 3 taps
    taps=0
    pg.locator('#qlAddExBtn').click(); taps+=1; pg.wait_for_timeout(250)
    check('Add exercise opens a sheet with recents first', pg.locator('#exSheet').is_visible() and 'Recent' in ev("document.getElementById('exSheetList').innerText"))
    first=pg.locator('#exSheetList .ex-row').first; rid=first.get_attribute('data-id'); first.click(); taps+=1; pg.wait_for_timeout(250)
    pre_w=pg.locator('#qsw-0-0').input_value(); pre_r=pg.locator('#qsr-0-0').input_value()
    check('last numbers prefilled for the recent lift', pre_w!='' and pre_r!='', (pre_w,pre_r))
    pg.locator('#qs-0 .set-done-btn').first.click(); taps+=1; pg.wait_for_timeout(250)
    check('recent lift reaches its first logged set in 3 taps', taps<=3 and QN()==q0+1, (taps, QN()-q0))
    # 2. searched
    pg.locator('#qlAddExBtn').click(); pg.wait_for_timeout(200); pg.locator('#exSheetQ').fill('lateral raise'); pg.wait_for_timeout(250)
    rows=ev("[...document.querySelectorAll('#exSheetList .ex-row')].map(r=>r.innerText.replace(/\\n/g,' | '))")
    check('search covers the library, rows are ruled', len(rows)>0 and ev("getComputedStyle(document.querySelector('#exSheetList .ex-row')).borderBottomStyle")=='solid', rows[:3])
    sid=pg.locator('#exSheetList .ex-row[data-id]').first.get_attribute('data-id'); pg.locator('#exSheetList .ex-row[data-id]').first.click(); pg.wait_for_timeout(250)
    check('searched exercise added second, in order', ev("_qs.items.map(i=>i.exId).join()")==rid+','+sid)
    # 3. typed new with muscle
    pg.locator('#qlAddExBtn').click(); pg.wait_for_timeout(200); pg.locator('#exSheetQ').fill('Zercher Hold'); pg.wait_for_timeout(250)
    fr=pg.locator('#exSheetList .ex-row').first.inner_text()
    check('no exact match: first row offers to add the typed text', fr=='Add "Zercher Hold" as a new exercise', fr)
    pg.locator('#exSheetList .ex-row').first.click(); pg.wait_for_timeout(200)
    check('asks one tap for the primary muscle', pg.locator('#exSheetList .muscle-pick-row button').count()==10)
    pg.locator('#exSheetList .muscle-pick-row button', has_text='Core').click(); pg.wait_for_timeout(300)
    cid=ev("_qs.items[2]&&_qs.items[2].exId")
    rec=ev("(customEx.any||[]).find(r=>r.id==='%s')"%cid)
    check('new exercise saved as custom, any day group, muscle core', rec and rec['name']=='Zercher Hold' and rec.get('muscle')=='core', rec)
    check('focus goes to the first empty field', ev("document.activeElement&&document.activeElement.id")=='qsw-2-0', ev("document.activeElement&&document.activeElement.id"))
    check('exact match shows no add row', (lambda: (pg.locator('#qlAddExBtn').click(), pg.wait_for_timeout(150), pg.locator('#exSheetQ').fill('Zercher Hold'), pg.wait_for_timeout(200), pg.locator('#exSheetList .ex-row-new').count()==0)[-1])())
    ev("closeExSheet()")
    check('new exercise shows up in search', ev("exerciseSearch('zercher').map(e=>e.id).join()")==cid)
    # own plan
    ev("setTrainStyle('own',3);openOwnPlanEditor();opOpenAdd(0)"); pg.wait_for_timeout(300); pg.locator('#opSearch').fill('zercher'); pg.wait_for_timeout(200)
    check('new exercise shows up in an own plan search and adds', pg.locator('#opResults .ex-result[data-id="%s"]'%cid).count()==1 and (pg.locator('#opResults .ex-result[data-id="%s"]'%cid).click() or True) and ev("ownPlan.days[0].ex.some(x=>x.id==='%s')"%cid))
    ev("closeOwnPlanEditor();setTrainStyle('plan')"); pg.wait_for_timeout(300)
    ev("goTab('quicklog')"); pg.wait_for_timeout(300)
    check('session kept across tab switches', ev("_qs.items.length")==3)
    # 4. log sets in all three, add set
    pg.locator('#qsw-1-0').fill('20'); pg.locator('#qsr-1-0').fill('12'); pg.locator('#qs-1 .set-done-btn').first.click(); pg.wait_for_timeout(200)
    pg.locator('#qs-1 .qs-addset').click(); pg.wait_for_timeout(200)
    check('Add set adds a row with the last values', pg.locator('#qsw-1-1').input_value()=='20' and ev("document.activeElement.id")=='qsw-1-1')
    pg.locator('#qs-1 .set-done-btn').nth(1).click(); pg.wait_for_timeout(200)
    pg.locator('#qsw-2-0').fill('0'); pg.locator('#qsr-2-0').fill('30'); pg.locator('#qs-2 .set-done-btn').first.click(); pg.wait_for_timeout(200)
    check('sets logged in all three exercises', QN()==q0+4 and ev("[0,1,2].every(i=>_qs.items[i].rows.some(r=>r.done))"), QN()-q0)
    check('each set is a new Quick Log entry', ev("(sessions['%s']||[]).filter(e=>e.quickLog&&e.d===todayKey()).length"%sid)==2)
    pg.screenshot(path=shot('o827-session-360.png'), full_page=False)
    # 5. second session same day
    pg.locator('#qlNewSession').click(); pg.wait_for_timeout(200)
    check('new session starts empty', ev("_qs.items.length")==0)
    pg.locator('#qlAddExBtn').click(); pg.wait_for_timeout(200); pg.locator('#exSheetList .ex-row[data-id="%s"]'%sid).first.click(); pg.wait_for_timeout(200)
    pg.locator('#qs-0 .set-done-btn').first.click(); pg.wait_for_timeout(200)
    ents=ev("(sessions['%s']||[]).filter(e=>e.quickLog&&e.d===todayKey()).map(e=>e.ts)"%sid)
    check('two Quick Log sessions on one day stay separate entries', len(ents)==3 and len(set(ents))==3, ents)
    # remove with confirm
    ev("qsRemove(0)"); pg.wait_for_timeout(200)
    check('remove from session keeps logged sets', ev("_qs.items.length")==0 and len(ev("(sessions['%s']||[]).filter(e=>e.quickLog&&e.d===todayKey())"%sid))==3)
    # form path: Choose a different lift opens the sheet
    ev("toggleOldQuickLog()"); pg.wait_for_timeout(200)
    check('old 4 lift limit removed', ev("document.querySelectorAll('.quicklog-lift-btn').length")==0)
    pg.locator('#quicklogPicker button').click(); pg.wait_for_timeout(200); pg.locator('#exSheetQ').fill('zercher'); pg.wait_for_timeout(200)
    pg.locator('#exSheetList .ex-row[data-id="%s"]'%cid).click(); pg.wait_for_timeout(200)
    check('Choose a lift opens the sheet and fills the form', pg.locator('#quicklogFormTitle').inner_text()=='Zercher Hold')
    pg.locator('#quicklogForm .quicklog-back').click(); pg.wait_for_timeout(200)
    check('Choose a different lift opens the same sheet', pg.locator('#exSheet').is_visible()); ev("closeExSheet()")
    # tap targets in the sheet and session
    ev("qsAdd('%s')"%sid); pg.wait_for_timeout(200); ev("openExSheet('session')"); pg.wait_for_timeout(200)
    small=ev("[...document.querySelectorAll('#exSheet button, #exSheet input, #qlSession button, #qlSession input')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [e.innerText||e.id,Math.round(r.width),Math.round(r.height)]}).filter(x=>x[1]<44||x[2]<44)")
    check('sheet and session tap targets at least 44 px', not small, small)
    ev("closeExSheet()")
    # Part B: 8.37 removed the logo menu. The rare items moved: Week review to
    # Progress, The Edge and Why I built this to Settings. t837_b_nav covers them.
    ev("goTab('calendar')"); pg.wait_for_timeout(200); pg.locator('#navLogo').click(); pg.wait_for_timeout(400)
    check('the logo goes to Today, no menu, running off', ev("document.body.dataset.tab")=='today' and not ev("!!document.querySelector('#navMenu,[role=menu]')"))
    ev("setRunning(true)"); ev("goTab('calendar')"); pg.locator('#navLogo').click(); pg.wait_for_timeout(400)
    check('with running on the logo does the same', ev("document.body.dataset.tab")=='today' and not ev("!!document.querySelector('#navMenu,[role=menu]')"))
    ev("setRunning(false)")
    # About links
    for how in ["goTab('info');goSec('about')", "goTab('about')", "onbFlowExploreAbout()"]:
        ev(how); pg.wait_for_timeout(300)
        check('old About link lands on The Edge: '+how, ev("document.getElementById('sec-edge').style.display")=='block' and ev("getComputedStyle(document.getElementById('about')).display")!='none')
    et=re.sub(r'\s+',' ',ev("document.getElementById('sec-edge').textContent"))
    # The About lead was shortened on purpose: no college or team claims.
    LEAD_OLD="I'm Billy. I captained Division 1 cross country in college, and I've lifted and run for years."
    check('the About lead is the short version', "I'm Billy. I've lifted and run for years." in et and LEAD_OLD not in et)
    miss=[t for t in about_old+edge_old if t not in et and t!=LEAD_OLD]
    check('every About and Edge line kept, About first', not miss and -1<et.find("I'm Billy.")<et.find('STRONG'), miss[:3])
    check('subnav has no separate About', ev("!document.getElementById('sb-about')"))
    pg.screenshot(path=shot('o827-edge-360.png'))
    # intro once
    ev("localStorage.removeItem('monk_about_seen_v1');maybeShowAboutIntro()"); pg.wait_for_timeout(300)
    shown=pg.locator('#aboutIntro').is_visible(); itx=ev("document.getElementById('aboutIntroBody').innerText")
    ev("closeAboutIntro();maybeShowAboutIntro()"); pg.wait_for_timeout(200)
    check('first run intro shows once only, with the About facts', shown and 'Billy' in itx and 'instagram' in itx.lower() and not pg.locator('#aboutIntro').is_visible())
    # Part C: rest timer on, every modal and sheet
    ev("startTimer(180,'Bench',true)"); pg.wait_for_timeout(300)
    check('rest timer running', pg.locator('#timerBar').is_visible())
    openers=[('settingsModal','openSettingsModal()'),('changePlanModal','openChangePlanModal()'),('maxesModal','openMaxesModal()'),
             ('goingOutSheet',"openGoingOut(findNextUnloggedDay()||activeSplit().week.find(d=>d!=='rest'))"),('swapSheet',"openSwapSheet('flat-bb-bench')"),
             ('exSheet',"openExSheet('session')"),('ownPlanModal','openOwnPlanEditor()'),('aboutIntro',"localStorage.removeItem('monk_about_seen_v1');maybeShowAboutIntro()"),
             ('runSetupModal','setRunning(true);openRunSetupModal()'),('runLogSheet',"setRunning(true);goTab('running');openRunLog('easy')"),('onbWizard','openOnboardingWizard()')]
    for mid,op in openers:
        try: ev(op)
        except Exception as e: check('open '+mid, False, e); continue
        pg.wait_for_timeout(350)
        if not ev("(()=>{const m=document.getElementById('%s');return m&&getComputedStyle(m).display!=='none'})()"%mid): check('open '+mid, False, 'not visible'); continue
        res=ev("""(id)=>{const m=document.getElementById(id);const out=[];let n=0;m.querySelectorAll('button').forEach(b=>{if(!b.offsetParent||b.disabled)return;b.scrollIntoView({block:'center'});const r=b.getBoundingClientRect();if(r.width<2)return;n++;const x=r.left+r.width/2,y=r.top+r.height/2;const hit=document.elementFromPoint(x,y);if(!hit||!(b===hit||b.contains(hit)))out.push((b.innerText||b.getAttribute('aria-label')||'?').trim().slice(0,24)+' under '+(hit?(hit.id||hit.className):'none'))});return [n,out]}""", mid)
        check('rest timer on: every button tappable in '+mid, res[1]==[] and res[0]>0, res)
        ev("""['settingsModal','changePlanModal','maxesModal','goingOutSheet','swapSheet','exSheet','ownPlanModal','aboutIntro','runSetupModal','runLogSheet','onbWizard'].forEach(i=>{const m=document.getElementById(i);if(m)m.style.display='none'})""")
    ev("setRunning(false)")
    # backup and restore keeps custom exercises
    bk=ev("""()=>new Promise(res=>{const o=URL.createObjectURL;URL.createObjectURL=bl=>{bl.text().then(res);return o.call(URL,bl)};exportData();})""")
    snap=ev("JSON.stringify(customEx)")
    ev("""()=>new Promise(r=>{localStorage.removeItem('monk_custom_ex_v1');const q=indexedDB.deleteDatabase('monk_mode_store');q.onsuccess=q.onerror=q.onblocked=()=>r()})"""); pg.reload(); pg.wait_for_timeout(1500)
    check('wiped custom exercises', 'Zercher' not in ev("JSON.stringify(customEx)"))
    ev("""(txt)=>{const dt=new DataTransfer();dt.items.add(new File([txt],'b.json'));const i=document.createElement('input');i.type='file';i.files=dt.files;importData(i);}""", bk); pg.wait_for_timeout(2000)
    check('restore keeps the new custom exercises', ev("JSON.stringify(customEx)")==snap and ev("exerciseSearch('zercher').length")==1)
    check('no page errors', not errs, errs[:3])
    b.close()
n=sum(1 for r in RES if not r[1]); print('\n%d checks, %d failed'%(len(RES),n)); sys.exit(1 if n else 0)
