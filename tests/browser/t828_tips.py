"""8.28 one time tips: once each, never stacked, never over a tap target, reset, backup and restore."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, datetime, re
from playwright.sync_api import sync_playwright
from common import SEED, URL, ORIGIN, shot, baseline, HERE
T0=datetime.datetime(2026,11,18,10,0,0); RES=[]
NEW={'lnote','wnote','quicklog','progress','style','menu'}; ALL=NEW|{'today','plan','run','food'}
def check(n, ok, d=''): RES.append((n,bool(ok),str(d)[:220])); print(('PASS ' if ok else 'FAIL ')+n+('  ['+str(d)[:220]+']' if d!='' else ''))
COVER="""()=>{const t=document.getElementById('tipBox');if(!t)return null;const tr=t.getBoundingClientRect();const bad=[];
const layer=t.closest('.settings-modal-overlay')||document;layer.querySelectorAll('button,a[href],input,textarea,select,label,[onclick],[role=button]').forEach(e=>{if(t.contains(e)||e.contains(t)||!e.offsetParent)return;const r=e.getBoundingClientRect();if(r.width<1||r.height<1)return;
if(r.left<tr.right-1&&r.right>tr.left+1&&r.top<tr.bottom-1&&r.bottom>tr.top+1)bad.push((e.innerText||e.id||e.className).toString().trim().slice(0,30))});
const ok=t.querySelector('.tip-ok'),orr=ok.getBoundingClientRect(),hit=document.elementFromPoint(orr.left+orr.width/2,orr.top+orr.height/2);
const cs=getComputedStyle(t);return {id:_tipId,text:t.querySelector('.tip-text').textContent,bad,okHit:hit===ok,okW:orr.width,okH:orr.height,fg:cs.color,bg:cs.backgroundColor,n:document.querySelectorAll('.tip').length,anim:cs.animationName}}"""
def lum(c):
    v=[int(x)/255 for x in re.findall(r'\d+',c)[:3]]; v=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in v]; return 0.2126*v[0]+0.7152*v[1]+0.0722*v[2]
def cr(a,b): la,lb=sorted([lum(a),lum(b)],reverse=True); return (la+0.05)/(lb+0.05)
def newpage(b, seed=False, onb=True, rm=False):
    ctx=b.new_context(viewport={'width':360,'height':780}, reduced_motion='reduce' if rm else 'no-preference'); pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d:d.accept()); pg.clock.install(time=T0)
    if onb: pg.add_init_script("localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');")
    pg.goto(URL); pg.wait_for_timeout(900)
    if seed: pg.evaluate(SEED); pg.evaluate("localStorage.removeItem('monk_tips_seen_v1')"); pg.reload(); pg.wait_for_timeout(1300)
    return ctx,pg,errs
SCREENS=['today','training','quicklog','calendar','food','running','settings']
def visit(pg, scr, shown, infos):
    ev=pg.evaluate
    if scr=='settings': ev("closeSettingsModal();openSettingsModal()")
    else: ev("closeSettingsModal();goTab('%s');scrollTo(0,0)"%scr)
    pg.wait_for_timeout(600)
    h=ev("document.documentElement.scrollHeight")
    for y in range(0, h, 260):
        info=ev(COVER)
        if info: break
        if scr=='settings': break
        ev("scrollTo({top:%d,behavior:'instant'})"%y); pg.wait_for_timeout(420)  # instant, so the tip is not placed mid scroll
    info=ev(COVER)
    if info:
        shown.append(info['id']); infos.append(info)
        pg.locator('#tipBox .tip-ok').click(); pg.wait_for_timeout(150)
def cycles(pg, n=7):
    shown=[]; infos=[]
    for _ in range(n):
        for s in SCREENS: visit(pg, s, shown, infos)
    return shown, infos
with sync_playwright() as p:
    b=p.chromium.launch()
    # 0. during onboarding: no tip
    ctx,pg,errs=newpage(b, onb=False); pg.wait_for_timeout(800)
    check('no tip while the intro story is on screen', pg.evaluate("getComputedStyle(document.getElementById('introStory')).display!=='none'") and pg.evaluate("document.querySelectorAll('.tip').length")==0)
    pg.evaluate("introDone()"); pg.wait_for_timeout(800)
    check('no tip while onboarding is on screen', pg.evaluate("getComputedStyle(document.getElementById('onbFlow')).display!=='none'") and pg.evaluate("document.querySelectorAll('.tip').length")==0)
    ctx.close()
    # 1. fresh install
    ctx,pg,errs=newpage(b); ev=pg.evaluate
    ev("setRunning(true)"); pg.wait_for_timeout(200); ev("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    check('fresh install starts with no tips seen', ev("JSON.stringify(loadTipsSeen())")=='{}')
    shown, infos = cycles(pg)
    # 8.32: the Food tip does not show while Food is locked.
    check('fresh install shows every tip once, no Food tip while Food is locked', sorted(shown)==sorted(ALL-{'food'}), shown)
    check('tips appear in place, Today first', shown and shown[0]=='today', shown[:3])
    ev("goTab('today')"); pg.wait_for_timeout(200)
    again,_=cycles(pg,2)
    check('never again after Got it, also after reload', not again and (pg.reload() or True) and (pg.wait_for_timeout(1300) or True) and not cycles(pg,1)[0], again)
    for i in infos:
        words=len(i['text'].split())
        check('tip %s: under 15 words, no dashes, no exclamation'%i['id'], words<15 and not re.search('[‐-―-]|!', i['text']), (words, i['text']))
        check('tip %s covers no tap target and Got it is tappable'%i['id'], not i['bad'] and i['okHit'], i['bad'])
        check('tip %s: Got it at least 44 px, text contrast 4.5:1'%i['id'], i['okW']>=44 and i['okH']>=44 and cr(i['fg'],i['bg'])>=4.5, (i['okW'],i['okH'],round(cr(i['fg'],i['bg']),2)))
        check('tip %s: one on screen'%i['id'], i['n']==1)
    # tap elsewhere dismisses
    ev("resetTips();closeSettingsModal();goTab('running');scrollTo(0,0)"); pg.wait_for_timeout(700)
    had=ev("_tipId"); pg.locator('#hero-running .rtwh-word').click(); pg.wait_for_timeout(200)
    check('tapping anywhere else dismisses and marks seen', had=='run' and ev("!document.getElementById('tipBox')") and ev("loadTipsSeen().run===1"), had)
    # fast switching
    ev("resetTips()"); maxn=0
    for k in range(30):
        ev("goTab('%s')"%SCREENS[k%6]); pg.wait_for_timeout(40 if k%3 else 380)
        maxn=max(maxn, ev("document.querySelectorAll('.tip').length"))
    for k in range(12):
        pg.locator('.tabbar-btn[data-tab="%s"]'%['today','training','running','calendar'][k%4]).click(); pg.wait_for_timeout(60 if k%2 else 400)
        maxn=max(maxn, ev("document.querySelectorAll('.tip').length"))
    check('switching tabs fast never stacks two tips', maxn<=1, maxn)
    # show tips again
    ev("resetTips()"); [ev("loadTipsSeen()['%s']=1"%t) for t in ALL]; ev("saveTipsSeen()")
    ev("openSettingsModal()"); pg.wait_for_timeout(300)
    btn=pg.locator('#tipsResetBtn'); btn.scroll_into_view_if_needed(); bb=btn.bounding_box(); btn.click(); pg.wait_for_timeout(200)
    check('Settings has Show tips again, 44 px, and it resets them', bb['height']>=44 and ev("Object.keys(loadTipsSeen()).length")==0 and ev("JSON.parse(localStorage.getItem('monk_tips_seen_v1')).seen")=={}, bb)
    check('reset confirms in plain words', ev("document.getElementById('tipsResetMsg').textContent")=='Tips will show again as you open each screen.')
    ev("closeSettingsModal()")
    # restore keeps seen tips
    ev("['today','plan','progress','menu'].forEach(t=>loadTipsSeen()[t]=1);saveTipsSeen()")
    bk=ev("""()=>new Promise(res=>{const o=URL.createObjectURL;URL.createObjectURL=bl=>{bl.text().then(res);return o.call(URL,bl)};exportData();})""")
    check('backup includes seen tips', json.loads(bk).get('tipsSeen',{}).get('seen')=={'today':1,'plan':1,'progress':1,'menu':1}, json.loads(bk).get('tipsSeen'))
    ev("resetTips()")
    ev("""(txt)=>{const dt=new DataTransfer();dt.items.add(new File([txt],'b.json'));const i=document.createElement('input');i.type='file';i.files=dt.files;importData(i);}""", bk); pg.wait_for_timeout(1800)
    check('restore keeps seen tips', ev("JSON.stringify(Object.keys(loadTipsSeen()).sort())")==json.dumps(sorted(['today','plan','progress','menu'])).replace(' ',''))
    pg.reload(); pg.wait_for_timeout(1300)
    check('restored seen tips survive reload', sorted(ev("Object.keys(loadTipsSeen())"))==sorted(['today','plan','progress','menu']))
    # existing user backup (pre 8.28) restored on a fresh install
    old=json.loads(bk); old.pop('tipsSeen'); ev("resetTips()")
    ev("""(txt)=>{const dt=new DataTransfer();dt.items.add(new File([txt],'b.json'));const i=document.createElement('input');i.type='file';i.files=dt.files;importData(i);}""", json.dumps(old)); pg.wait_for_timeout(1800)
    check('older backup restored: only new feature tips remain', sorted(ev("Object.keys(loadTipsSeen())"))==sorted(ALL-NEW))
    check('no page errors (fresh)', not errs, errs[:3])
    ctx.close()
    # 2. existing user upgrading to 8.28
    ctx,pg,errs=newpage(b, seed=True); ev=pg.evaluate
    ev("setRunning(true)"); pg.wait_for_timeout(200); ev("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    check('existing user starts with old tips marked seen', sorted(ev("Object.keys(loadTipsSeen())"))==sorted(ALL-NEW))
    shown, infos = cycles(pg)
    check('existing user sees only the new feature tips, each once', sorted(shown)==sorted(NEW), shown)
    for i in infos: check('existing user tip %s covers no tap target'%i['id'], not i['bad'] and i['okHit'], i['bad'])
    # screenshots of two tips
    ev("resetTips();goTab('today');scrollTo(0,0)"); pg.wait_for_timeout(700); pg.screenshot(path=shot('o828-tip-today-360.png'))
    ev("delete loadTipsSeen().quicklog;saveTipsSeen();goTab('quicklog')"); pg.wait_for_timeout(500)
    for y in range(0,3000,260):
        if ev("!!document.getElementById('tipBox')"): break
        ev("scrollTo(0,%d)"%y); pg.wait_for_timeout(400)
    pg.screenshot(path=shot('o828-tip-quicklog-360.png'))
    check('no page errors (existing user)', not errs, errs[:3])
    ctx.close()
    # 3. reduced motion
    ctx,pg,errs=newpage(b, rm=True); pg.wait_for_timeout(600)
    info=pg.evaluate(COVER)
    check('reduced motion: tip has no animation', info and info['anim']=='none', info and info['anim'])
    ctx.close(); b.close()
n=sum(1 for r in RES if not r[1]); print('\n%d checks, %d failed'%(len(RES),n)); sys.exit(1 if n else 0)
