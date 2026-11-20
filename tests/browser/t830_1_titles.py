"""8.30 item 1: no repeated title under each hero, 24 px gap, Run unit toggle, Week review and The Edge headlines."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
from common import *
from playwright.sync_api import sync_playwright
VIS="""(t)=>{const h=document.getElementById('hero-'+t);const word=h.querySelector('.rtwh-word').innerText.replace(/[^A-Z ]/g,'').trim();
const tab=document.getElementById('tab-'+t);const out=[];const hb=h.getBoundingClientRect().bottom;
tab.querySelectorAll('h1,h2,h3,.today-date,.section-label,.section-title,.more-title,.ql-heading').forEach(e=>{if(!e.offsetParent)return;const r=e.getBoundingClientRect();if(r.height<1||r.top>hb+400)return;
out.push([e.className||e.tagName,e.innerText.replace(/\\s+/g,' ').trim(),Math.round(parseFloat(getComputedStyle(e).fontSize))])});return {word,hidden:h.hidden,heads:out}}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for W in (360,390):
        ctx,pg,errs=page(b,W,700)
        for t in ['quicklog','calendar','running','food']:  # 8.34: Today and Plan use the reference headers
            go(pg,t); i=pg.evaluate(VIS,t)
            words=set(i['word'].split())
            rep=[h for h in i['heads'] if words & set(h[1].upper().replace('.','').split()) and h[2]>18]
            check('%d %s: no heading under the hero repeats %s'%(W,t,i['word']), not i['hidden'] and not rep, rep or i['heads'][:3])
            g=pg.evaluate(GAPFN,t)
            check('%d %s: gap hero to first element about 24 px'%(W,t), 20<=g[1]<=30, g)
        go(pg,'today')
        d=pg.evaluate("(()=>{const e=document.getElementById('tbDow');return [e.innerText,parseFloat(getComputedStyle(e).fontSize),getComputedStyle(e).backgroundColor]})()")
        check('%d Today: day kept as a small line'%W, d[0]=='Thursday' and d[1]<=16 and d[2] in ('rgba(0, 0, 0, 0)','transparent'), d)
        go(pg,'running')
        r=pg.evaluate("(()=>{const u=document.getElementById('runUnits').getBoundingClientRect(),h=document.getElementById('hero-running').getBoundingClientRect(),c=document.getElementById('runTodayCard');const top=document.querySelector('#runHome .run-home-top');return {ur:Math.round(u.right),ut:Math.round(u.top-h.bottom),btn:c.innerText.trim(),bt:Math.round(c.getBoundingClientRect().top-u.bottom),firstKid:top===document.getElementById('runHome').firstElementChild,big:[...document.querySelectorAll('#runHome .today-date')].filter(e=>e.offsetParent).length,ubtn:[...document.querySelectorAll('#runUnits button')].map(b=>[b.innerText,Math.round(b.getBoundingClientRect().height),Math.round(b.getBoundingClientRect().width)])}})()")
        check('%d Run: RUN block gone, mi km toggle right aligned just under the hero'%W, r['big']==0 and abs(r['ur']-(W-20))<=1 and 20<=r['ut']<=30 and r['firstKid'], r)
        check('%d Run: toggle buttons 44 px, Log a run unchanged under it'%W, all(x[1]>=44 and x[2]>=44 for x in r['ubtn']) and r['btn']=='Log a run' and 0<=r['bt']<=24, r)
        pg.click('#runUnits button:has-text("km")'); pg.wait_for_timeout(200)
        check('%d Run: toggle still switches units'%W, pg.evaluate("runUnits")=='km'); pg.click('#runUnits button:has-text("mi")'); pg.wait_for_timeout(200)
        go(pg,'calendar')
        c=pg.evaluate("[document.querySelectorAll('#progTiles .prog-tile').length,!!document.querySelector('#progTabLifts').offsetParent,!!document.querySelector('#progTabBody').offsetParent,!!document.querySelector('#progTabWeek').offsetParent]")
        check('%d Progress: three stat cards and the Lifts Body Week switch kept'%W, c==[3,True,True,True], c)
        go(pg,'food')
        f=pg.evaluate("[...document.querySelectorAll('#foodSection > .section-label, #foodSection > .section-title')].map(e=>!!e.offsetParent)")
        check('%d Food: Food label and LOG WHAT YOU EAT gone'%W, f==[False,False], f)
        go(pg,'training')
        check('%d Plan: PLAN eyebrow gone, controls kept'%W, pg.evaluate("!document.querySelector('#plan > .section-label').offsetParent && !!document.querySelector('.lift-toolbar').offsetParent && !!document.querySelector('#tab-training .lift-row')"))
        # Week review and The Edge keep their own headlines
        for sec in ('overview','edge'):
            HF="(s)=>{const el=document.getElementById('sec-'+s)||document.getElementById(s);const hs=[...el.querySelectorAll('h1,h2')].filter(e=>e.offsetParent);return hs.length?[hs[0].innerText.replace(/\\s+/g,' '),parseFloat(getComputedStyle(hs[0]).fontSize)]:null}"
            pg.evaluate("goTab('info');goSec('%s');scrollTo(0,0)"%sec); pg.wait_for_timeout(400); hv=pg.evaluate(HF,sec)
            check('%d %s keeps its own headline, same as the saved baseline'%(W,sec), hv and hv==baseline('830-headline-%s-%d'%(sec,W),hv), hv)
        check('%d no page errors'%W, not errs, errs[:3]); ctx.close()
    # rest day: hero hidden on Today, old day block stays
    common.T0=datetime.datetime(2026,11,18,10,0,0)
    ctx,pg,errs=page(b,360,700); go(pg,'today')
    d=pg.evaluate("[document.getElementById('hero-today').hidden,document.getElementById('todayDate').innerText,parseFloat(getComputedStyle(document.getElementById('todayDate')).fontSize)]")
    check('rest day: Today hero hidden, the day block keeps its old size', d[0] and d[2]>30, d); ctx.close()
sys.exit(1 if done() else 0)
