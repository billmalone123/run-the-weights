"""8.30 item 6, updated for 8.37: no logo menu. The logo goes to Today by touch and mouse and presses nothing else.
Week review (from Progress) and The Edge (from Settings) open the same screens as their direct routes. The gear tip."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
def tpage(b, W=360, touch=True):
    ctx=b.new_context(viewport={'width':W,'height':700}, service_workers='block', has_touch=touch, is_mobile=touch); pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.clock.install(time=T0); pg.add_init_script(INIT)
    pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    return ctx,pg,errs
GUARD="window._hit=0;document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('button')&&!e.target.closest('#navLogo'))window._hit++},true)"
TIP='The gear at the top opens Settings, The Edge and Why I built this.'
with sync_playwright() as p:
    b=p.chromium.launch()
    for touch in (True, False):
        how='touch' if touch else 'mouse'
        ctx,pg,errs=tpage(b, 360 if touch else 390, touch)
        go(pg,'calendar'); pg.evaluate(GUARD)
        (pg.tap if touch else pg.click)('#navLogo'); pg.wait_for_timeout(400)
        check('%s: the logo goes to Today and presses nothing else'%how, pg.evaluate("[document.body.dataset.tab,window._hit,!!document.querySelector('#navMenu,[role=menu],.navmenu')]")==['today',0,False], pg.evaluate("[document.body.dataset.tab,window._hit]"))
        r=pg.evaluate("(()=>{var r=navLogo.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})()")
        check('%s: the logo is a 44 px target'%how, r[0]>=44 and r[1]>=44, r)
        go(pg,'calendar'); (pg.tap if touch else pg.click)('#progressHome .prog-review'); pg.wait_for_timeout(500)
        new=pg.evaluate("[document.getElementById('sec-overview').style.display==='block',document.getElementById('sec-overview').innerText.length]")
        pg.evaluate("goTab('info');goSec('overview')"); pg.wait_for_timeout(300)
        old=pg.evaluate("[document.getElementById('sec-overview').style.display==='block',document.getElementById('sec-overview').innerText.length]")
        check('%s: Week review from Progress opens the same screen as before'%how, new[0] and new==old, (new,old))
        go(pg,'today'); (pg.tap if touch else pg.click)('#navGear'); pg.wait_for_timeout(300)
        (pg.tap if touch else pg.click)('#settingsModal .settings-about button:has-text("The Edge")'); pg.wait_for_timeout(500)
        new=pg.evaluate("[document.getElementById('sec-edge').style.display==='block',document.getElementById('sec-edge').innerText.length]")
        pg.evaluate("goTab('info');goSec('edge')"); pg.wait_for_timeout(300)
        old=pg.evaluate("[document.getElementById('sec-edge').style.display==='block',document.getElementById('sec-edge').innerText.length]")
        check('%s: The Edge from Settings opens the same screen as before'%how, new[0] and new==old, (new,old))
        check('no page errors (%s)'%how, not errs, errs[:3]); ctx.close()
    ctx,pg,errs=tpage(b)
    pg.evaluate("goTab('info');goSec('about')"); pg.wait_for_timeout(300)
    check('Old About route still lands on The Edge', pg.evaluate("document.getElementById('sec-edge').style.display==='block'"))
    check('The menu tip now names the gear', pg.evaluate("TIP_DEFS.find(d=>d.id==='menu').t")==TIP)
    ctx.close()
    ctx=b.new_context(viewport={'width':360,'height':700}, service_workers='block'); pg=ctx.new_page(); pg.clock.install(time=T0)
    pg.add_init_script("localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');localStorage.setItem('monk_tips_seen_v1',JSON.stringify({v:1,seen:{today:1,plan:1,lnote:1,wnote:1,quicklog:1,progress:1,run:1,food:1,style:1}}));")
    pg.goto(URL); pg.wait_for_timeout(900); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1800)
    pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none');goTab('today')"); pg.wait_for_timeout(800)
    t=pg.evaluate("(()=>{const t=document.querySelector('.tip');return t?t.innerText.replace('Got it','').trim():null})()")
    check('An existing user sees the gear tip', t==TIP, t); ctx.close()
sys.exit(1 if done() else 0)
