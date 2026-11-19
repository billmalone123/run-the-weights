"""8.30 item 5: chart date labels never collide at 320, 360 and 390."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
LAB="""(sel)=>{const out=[];document.querySelectorAll(sel).forEach(svg=>{if(!svg.getBoundingClientRect().width)return;const sr=svg.getBoundingClientRect();
 const t=[...svg.querySelectorAll('text.ch-x')].map(e=>{const r=e.getBoundingClientRect();return {s:e.textContent,l:r.left,r:r.right,rot:e.getAttribute('transform')||getComputedStyle(e).transform}}).sort((a,b)=>a.l-b.l);
 let minGap=1e9;for(let i=1;i<t.length;i++)minGap=Math.min(minGap,t[i].l-t[i-1].r);
 out.push({n:t.length,labels:t.map(x=>x.s),minGap:Math.round(minGap*10)/10,inside:t.every(x=>x.l>=sr.left-0.5&&x.r<=sr.right+0.5),rot:t.some(x=>x.rot&&x.rot!=='none')})});return out}"""
SETUP="""(()=>{
 // lift with dates bunched together, the known case: Sep 28 and Oct 5
 const ds=['2026-09-28','2026-10-05','2026-10-06','2026-10-08','2026-10-19','2026-10-20','2026-11-02','2026-11-03','2026-11-04','2026-11-16','2026-11-17','2026-11-18'];
 sessions['lat-pulldown']=['2026-09-28','2026-10-05','2026-11-16','2026-11-18'].map((d,i)=>({d:d,week:0,weight:90+i*5,reps:8,quickLog:true,ts:Date.parse(d)}));
 sessions['flat-bb-bench']=ds.map((d,i)=>({d:d,week:0,weight:100+i*5,reps:5,quickLog:true,ts:Date.parse(d)}));saveSessions();
 const bw={};['2026-09-28','2026-10-05','2026-10-06','2026-10-07','2026-10-12','2026-10-30','2026-11-01','2026-11-02','2026-11-10','2026-11-11','2026-11-17','2026-11-18','2026-11-19'].forEach((d,i)=>bw[d]=180+i*0.3);bodyweight=bw;persistBodyweight();
 ['2026-09-28','2026-10-06','2026-10-13','2026-10-21','2026-10-27','2026-11-04','2026-11-10','2026-11-17'].forEach((d,i)=>runLogs[d]={miles:3+i,secs:1800+i*60,type:'easy'});persistRunLogs();
})()"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for W in (320,360,390):
        ctx,pg,errs=page(b,W,700); pg.evaluate(SETUP)
        charts={}
        go(pg,'calendar'); pg.evaluate("_progEx='flat-bb-bench';setProgView('lifts')"); pg.wait_for_timeout(200)
        sel=pg.evaluate("document.querySelector('#progView select')&&document.querySelector('#progView select').value")
        charts['Progress Lifts']=pg.evaluate(LAB,'#progView svg.mini-chart')
        pg.screenshot(path=shot('p5-lifts-%d.png')%W, clip={'x':0,'y':0,'width':W,'height':700}) if False else None
        pg.evaluate("document.querySelector('#progView svg').scrollIntoView({block:'center'})"); pg.wait_for_timeout(100); pg.screenshot(path=shot('p5-lifts-%d.png')%W)
        pg.evaluate("_progEx='lat-pulldown';setProgView('lifts')"); pg.wait_for_timeout(200)
        k4=pg.evaluate(LAB,'#progView svg.mini-chart')[0]
        check('%d Progress Lifts, four close dates (Sep 28 and Oct 5): no overlap, first and last kept'%W, k4['minGap']>=7.5 and k4['inside'] and k4['labels'][0]=='Sep 28' and k4['labels'][-1]=='Nov 18', k4)
        pg.evaluate("setProgView('body')"); pg.wait_for_timeout(200); charts['Progress Body']=pg.evaluate(LAB,'#progView svg.mini-chart')
        pg.evaluate("setProgView('week')"); pg.wait_for_timeout(200)
        wk=pg.evaluate("(()=>{const t=[...document.querySelectorAll('#progView .pw-dow')].map(e=>e.getBoundingClientRect());let g=1e9;for(let i=1;i<t.length;i++)g=Math.min(g,t[i].left-t[i-1].right);return [t.length,Math.round(g*10)/10]})()")
        check('%d Progress Week: day labels do not overlap'%W, wk[0]==7 and wk[1]>=0, wk)
        go(pg,'running'); charts['Run weekly distance']=pg.evaluate(LAB,'#runDistChart svg')
        pg.evaluate("document.querySelector('#runDistChart svg').scrollIntoView({block:'center'})"); pg.wait_for_timeout(100); pg.screenshot(path=shot('p5-run-%d.png')%W)
        pg.evaluate("toggleRunPlanWrap();document.getElementById('run-race-date').value='2027-06-14';onRunInput()"); pg.wait_for_timeout(400)
        charts['Run race plan']=pg.evaluate(LAB,'.run-chart-body svg')
        go(pg,'food'); charts['Food bodyweight']=pg.evaluate(LAB,'#foodWeight svg')
        for name,cs in charts.items():
            if not cs: check('%d %s: chart shows'%(W,name), False); continue
            c=cs[0]
            check('%d %s: no labels overlap (8 px clear), none past the edge, none rotated'%(W,name), c['minGap']>=7.5 and c['inside'] and not c['rot'] and c['n']>=2, c)
        lab=charts['Progress Lifts'][0]['labels'] if charts['Progress Lifts'] else []
        check('%d Progress Lifts: first and last dates always kept (Sep 28 and Nov 18)'%W, lab[:1]==['Sep 28'] and lab[-1:]==['Nov 18'], lab)
        print('   %d lifts %s | body %s | run %s | plan %d labels'%(W,lab,charts['Progress Body'][0]['labels'],charts['Run weekly distance'][0]['labels'],charts['Run race plan'][0]['n']))
        check('%d Progress Body: first and last kept'%W, charts['Progress Body'][0]['labels'][0]=='Sep 28' and charts['Progress Body'][0]['labels'][-1]=='Nov 19', charts['Progress Body'][0]['labels'])
        check('%d no page errors'%W, not errs, errs[:3]); ctx.close()
    # unit level: the picker against a dense case and a two point case
    ctx,pg,errs=page(b,360,700,seed=False)
    r=pg.evaluate("""(()=>{const one=axisLabels([{x:170,s:'Nov 2'}],340,12,160,{edge:false});
      const two=axisLabels([{x:40,s:'Sep 28'},{x:326,s:'Oct 5'}],340,12,160,{edge:true});
      const dense=axisLabels(Array.from({length:30},(_,i)=>({x:40+i*9.8,s:'Oct '+(i+1)})),340,12,160,{edge:true});
      const d=new DOMParser().parseFromString('<svg xmlns="http://www.w3.org/2000/svg">'+dense+'</svg>','image/svg+xml');
      const xs=[...d.querySelectorAll('text')].map(t=>t.textContent);return [one,two.match(/<text/g).length,xs[0],xs[xs.length-1],xs.length]})()""")
    check('Picker: one label stays centred, two labels both kept', 'text-anchor="middle"' in r[0] and r[1]==2, r[:2])
    check('Picker: dense case keeps first and last and thins the middle', r[2]=='Oct 1' and r[3]=='Oct 30' and 2<r[4]<30, r[2:])
    ctx.close()
sys.exit(1 if done() else 0)
