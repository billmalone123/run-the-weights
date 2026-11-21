"""8.30 item 6, updated for 8.35b: logo menu holds Quick Log, Week review, The Edge, Settings; menu tip; taps outside the open menu only close it."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
def tpage(b, W=360, touch=True):
    ctx=b.new_context(viewport={'width':W,'height':700}, service_workers='block', has_touch=touch, is_mobile=touch); pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.clock.install(time=T0); pg.add_init_script(INIT)
    pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none');if(_navMenu){_navMenu.remove();_navMenu=null}")
    return ctx,pg,errs
def center(pg,sel): r=pg.locator(sel).first.bounding_box(); return (r['x']+r['width']/2, r['y']+r['height']/2)
MENU="[...document.querySelectorAll('#navMenu .navmenu-item')].map(b=>({quicklog:'Quick Log',overview:'Week review',edge:'The Edge',settings:'Settings'})[b.dataset.sec||b.dataset.tab||b.dataset.action])"
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=tpage(b)
    go(pg,'today')
    pg.tap('#navLogo'); pg.wait_for_timeout(250)
    m=pg.evaluate(MENU)
    check('Menu order: Quick Log, Week review, The Edge, Settings', m==['Quick Log','Week review','The Edge','Settings'], m)
    check('Menu has no About row and no places from the bar', not any(x in m for x in ('About','Today','Lift','Run','Progress','More')), m)
    hs=pg.evaluate("[...document.querySelectorAll('#navMenu .navmenu-item')].map(b=>Math.round(b.getBoundingClientRect().height))")
    check('Menu rows 44 px or taller', min(hs)>=44, hs)
    # ghost tap: tap Start workout under the open menu area (outside the panel)
    sx,sy=center(pg,'.tb-start')
    inside=pg.evaluate("([x,y])=>{const r=document.getElementById('navMenu').getBoundingClientRect();return x>=r.left&&x<=r.right&&y>=r.top&&y<=r.bottom}",[sx,sy])
    if inside: sx,sy=(sx, pg.evaluate("document.getElementById('navMenu').getBoundingClientRect().bottom")+30)
    pg.evaluate("window._hit=0;document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('button:not(.navmenu-item)'))window._hit++},true)")
    pg.touchscreen.tap(sx,sy); pg.wait_for_timeout(400)
    st=pg.evaluate("[navMenuOpen(),window._hit,localStorage.getItem('rtw_last_tab')||document.querySelector('.tab-main[style*=\"display: block\"]')?.id,!!document.querySelector('.guided')&&getComputedStyle(document.querySelector('.guided')).display!=='none', document.getElementById('tab-today').style.display]")
    check('Touch outside the open menu only closes it (Start workout not pressed)', st[0]==False and st[1]==0 and not st[3], st)
    # tab bar under the scrim
    pg.tap('#navLogo'); pg.wait_for_timeout(250)
    fx,fy=center(pg,'.tabbar-btn[data-tab="calendar"]'); pg.touchscreen.tap(fx,fy); pg.wait_for_timeout(400)
    check('Touch on the tab bar with the menu open only closes it', pg.evaluate("[navMenuOpen(),getComputedStyle(document.getElementById('tab-calendar')).display]")==[False,'none'], pg.evaluate("[navMenuOpen(),getComputedStyle(document.getElementById('tab-calendar')).display]"))
    pg.wait_for_timeout(500); pg.touchscreen.tap(fx,fy); pg.wait_for_timeout(500)
    check('Once closed, the next tap works normally', pg.evaluate("getComputedStyle(document.getElementById('tab-calendar')).display")!='none')
    pg.tap('#navLogo'); pg.wait_for_timeout(250)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    check('Escape closes the menu and returns focus to the logo', pg.evaluate("[navMenuOpen(),document.activeElement.id,_navScrim.classList.contains('on')]")==[False,'navLogo',False])
    for name,sec in (('Week review','overview'),('The Edge','edge')):
        pg.evaluate("goTab('today');scrollTo(0,0)"); pg.wait_for_timeout(300)
        pg.tap('#navLogo'); pg.wait_for_timeout(250); pg.tap('#navMenu .navmenu-item[data-sec="%s"]'%sec); pg.wait_for_timeout(500)
        new=pg.evaluate("(s)=>[document.getElementById('sec-'+s).style.display==='block',document.getElementById('sec-'+s).innerText.length]",sec)
        pg.evaluate("goTab('info');goSec('%s')"%sec); pg.wait_for_timeout(300)
        old=pg.evaluate("(s)=>[document.getElementById('sec-'+s).style.display==='block',document.getElementById('sec-'+s).innerText.length]",sec)
        check('Menu, %s opens the same screen as before'%name, new[0] and new==old, (new,old))
    pg.evaluate("goTab('info');goSec('about')"); pg.wait_for_timeout(300)
    check('Old About route still lands on The Edge', pg.evaluate("document.getElementById('sec-edge').style.display==='block'"))
    check('Logo menu tip text', pg.evaluate("TIP_DEFS.find(d=>d.id==='menu').t")=='Week review, The Edge and Settings live here.')
    check('no page errors (touch)', not errs, errs[:3]); ctx.close()
    # mouse: click outside only closes
    ctx,pg,errs=tpage(b,390,touch=False); go(pg,'today')
    pg.click('#navLogo'); pg.wait_for_timeout(250)
    sx,sy=center(pg,'.tb-start')
    if pg.evaluate("([x,y])=>{const r=document.getElementById('navMenu').getBoundingClientRect();return y<=r.bottom}",[sx,sy]): sy=pg.evaluate("document.getElementById('navMenu').getBoundingClientRect().bottom")+30
    pg.evaluate("window._hit=0;document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('button:not(.navmenu-item)'))window._hit++},true)")
    pg.mouse.click(sx,sy); pg.wait_for_timeout(300)
    check('390 mouse: click outside the menu only closes it', pg.evaluate("[navMenuOpen(),window._hit,_navScrim.classList.contains('on')]")==[False,0,False], pg.evaluate("[navMenuOpen(),window._hit]"))
    pg.click('#navLogo'); pg.wait_for_timeout(250); pg.click('#navMenu .navmenu-item[data-tab="quicklog"]'); pg.wait_for_timeout(400)
    check('390 mouse: a menu item still navigates', pg.evaluate("getComputedStyle(document.getElementById('tab-quicklog')).display")!='none')
    # menu tip for an existing user (tips seen except menu) mentions More
    check('no page errors (mouse)', not errs, errs[:3]); ctx.close()
    ctx=b.new_context(viewport={'width':360,'height':700}, service_workers='block'); pg=ctx.new_page(); pg.clock.install(time=T0)
    pg.add_init_script("localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');localStorage.setItem('monk_tips_seen_v1',JSON.stringify({v:1,seen:{today:1,plan:1,lnote:1,wnote:1,quicklog:1,progress:1,run:1,food:1,style:1}}));")
    pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1800)
    pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none');goTab('today')"); pg.wait_for_timeout(800)
    t=pg.evaluate("(()=>{const t=document.querySelector('.tip');return t?t.innerText.replace('Got it','').trim():null})()")
    check('Logo menu tip shows the new words', t=='Week review, The Edge and Settings live here.', t); ctx.close()
sys.exit(1 if done() else 0)
