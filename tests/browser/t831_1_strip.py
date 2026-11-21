"""8.31 item 1: the top strip shows Home, The Edge, Week review; the old Progression route opens Progress."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
STRIP="[...document.querySelectorAll('#info-subnav button')].filter(b=>b.offsetParent).map(b=>b.innerText.trim())"
STY="(()=>{const s=getComputedStyle(document.getElementById('info-subnav')),b=getComputedStyle(document.getElementById('sb-home'));return [s.backgroundColor,s.height,s.borderBottom,b.fontFamily,b.fontSize,b.color,b.padding]})()"
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=page(b,360,700)
    a=pg.evaluate("(()=>{const s=document.getElementById('sec-progression');const pc=document.getElementById('progressCards');return {txt:s.innerText.trim().length,inAll:!!pc.closest('#progAll'),intro:!!document.getElementById('prog-intro').closest('#progAll')}})()")
    check('old Progression screen is empty at load, its cards and intro sit on Progress', a['txt']==0 and a['inAll'] and a['intro'], a)
    for sec,name in (('home','Home'),('edge','The Edge'),('overview','Week review')):
        pg.evaluate("goTab('info');goSec('%s')"%sec); pg.wait_for_timeout(300)
        st=pg.evaluate(STRIP)
        check('strip on %s shows exactly Home, The Edge, Week review'%name, st==['Home','The Edge','Week review'], st)
        on=pg.evaluate("document.querySelector('#info-subnav button.on').innerText")
        check('strip marks %s as current'%name, on==name, on)
    pg.evaluate("goTab('info');goSec('home')")
    sty=pg.evaluate(STY)
    check('strip look unchanged against the saved baseline', sty==baseline('831-strip-style',sty), sty)
    check('no Progression anywhere in visible nav or menu text', pg.evaluate("!document.getElementById('sb-progression') && ![...document.querySelectorAll('#info-subnav,#navMenu,#tab-more,.tabbar')].some(e=>/Progression/.test(e.textContent))"))
    pg.evaluate("goTab('info');goSec('progression')"); pg.wait_for_timeout(500)
    r=pg.evaluate("[document.querySelector('.tab-main[style*=\"block\"], .tab-main.on') && [...document.querySelectorAll('.tab-main')].filter(t=>t.offsetParent||getComputedStyle(t).display!='none').map(t=>t.id), !!document.getElementById('tab-calendar').offsetParent, document.getElementById('info-subnav').style.display]")
    check('old Progression route lands on Progress', r[1] and r[2]=='none', r)
    pg.evaluate("goTab('info');goSec('home')"); pg.wait_for_timeout(200)
    pg.evaluate("goSec('progression')"); pg.wait_for_timeout(400)
    check('goSec progression alone also lands on Progress', pg.evaluate("!!document.getElementById('tab-calendar').offsetParent"))
    pg.evaluate("toggleProgAll&&(document.getElementById('progAll').style.display=='none')&&toggleProgAll()"); pg.wait_for_timeout(300)
    check('lift progress cards still reachable on Progress', pg.evaluate("!!document.getElementById('progressCards').offsetParent && !!document.getElementById('prog-intro').offsetParent"))
    go(pg,'more')
    m=pg.evaluate("[...document.querySelectorAll('#tab-more .more-row-title')].filter(e=>e.offsetParent).map(e=>e.innerText.trim())")
    check('More lists only Week review and The Edge', m==['Week review','The Edge'], m)
    pg.evaluate("openNavMenu()"); pg.wait_for_timeout(300)
    mi=pg.evaluate("[...document.querySelectorAll('#navMenu .navmenu-item')].map(e=>e.dataset.sec||e.dataset.tab||e.dataset.action)")
    check('logo menu is the 8.35b set', mi==['quicklog','overview','edge','settings'], mi)
    pg.evaluate("closeNavMenu&&closeNavMenu()")
    for sec in ('home','edge','overview'):
        pg.evaluate("goTab('info');goSec('%s')"%sec); pg.wait_for_timeout(200)
        check('%s screen shows content'%sec, pg.evaluate("document.getElementById('sec-%s').innerText.trim().length>40"%sec))
    check('no page errors', not errs, errs)
    n=sum(1 for r in RES if not r[1]); print('\n%d checks, %d failed'%(len(RES),n))
sys.exit(1 if done() else 0)
