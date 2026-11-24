"""8.34 Part 3: finish card. PR and progression rules, summary, share image, edge cases."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
ULTRA='rgb(28, 47, 181)'; PERS='rgb(242, 85, 44)'; INK='rgb(20, 20, 20)'; CREAM='rgb(242, 238, 228)'
def hl(pg, items, week=6): return pg.evaluate("finHighlights(%s,%d)"%(json.dumps(items),week))
def it(name, cur, others): return {'name':name,'sets':[{'w':w,'r':r} for w,r in cur],'others':others}
def e(week, *sets, **kw):
    o={'week':week,'d':'2026-10-0%d'%(1+week%9)}
    for i,(w,r) in enumerate(sets): o['s%d'%(i+1)]={'w':w,'r':r}
    o.update(kw); return o
EXPORT="(()=>{let out=null;const o=URL.createObjectURL;const a=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};URL.createObjectURL=function(bl){out=bl;return 'blob:x'};exportData();URL.createObjectURL=o;HTMLAnchorElement.prototype.click=a;return out?out.text():null})()"
def clear_timer(pg): pg.evaluate("dismissTimer&&dismissTimer();document.querySelectorAll('.rest-modal-overlay').forEach(m=>m.classList.remove('visible'))")
with sync_playwright() as p:
    b=p.chromium.launch(); ctx,pg,errs=page(b,390,844)
    # ---------- rules, from plain data ----------
    check('first time on a lift: no PR, nothing invented', hl(pg,[it('Bench',[(135,8)],[])])==[])
    r=hl(pg,[it('Bench',[(140,6)],[e(5,(135,8),(135,7))])])
    check('weight PR beats all history', len(r)==1 and r[0]['kind']=='w' and '140 lb on Bench' in r[0]['line'] and 'best before was 135' in r[0]['line'], r)
    r=hl(pg,[it('Bench',[(135,9)],[e(5,(135,8))])])
    check('rep PR at the same weight', len(r)==1 and r[0]['kind']=='r' and r[0]['line'].startswith('9 reps at 135 lb on Bench') and 'was 8' in r[0]['line'], r)
    check('equal to the best is not a PR', hl(pg,[it('Bench',[(135,8)],[e(5,(135,8))])])==[])
    check('more reps at a weight never done before is not a rep PR', hl(pg,[it('Bench',[(130,12)],[e(5,(135,8))])])==[])
    check('a quick log counts as history', hl(pg,[it('Bench',[(145,5)],[{'quickLog':True,'weight':150,'reps':5,'d':'2026-09-01'}])])==[])
    r=hl(pg,[it('Flat Bench',[(140,5)],[e(0,(150,5)),e(3,(125,8)),e(4,(130,8)),e(5,(135,8))])])
    check('progression run: weekly top weight up 3 weeks in a row', len(r)==1 and r[0]['kind']=='p' and r[0]['line']=='3 weeks in a row adding 5 lb on Flat Bench. Real progress.', r)
    check('a run of one week is not shown', hl(pg,[it('Bench',[(140,5)],[e(0,(150,5)),e(5,(135,8))])])==[])
    r=hl(pg,[it('Flat Bench',[(140,5)],[e(0,(150,5)),e(3,(120,8)),e(4,(130,8)),e(5,(135,8))])])
    check('uneven steps read as adding weight', r and r[0]['line'].startswith('3 weeks in a row adding weight on Flat Bench'), r)
    r=hl(pg,[it('Push Up',[(0,15)],[e(5,(0,12))])])
    check('body weight lift: reps only rep PR', r and r[0]['kind']=='r' and r[0]['big']=='15 reps' and 'at body weight' in r[0]['line'] and ' lb' not in r[0]['line'], r)
    r=hl(pg,[it('A',[(140,5)],[e(0,(150,5)),e(3,(125,8)),e(4,(130,8)),e(5,(135,8))]), it('B',[(100,9)],[e(5,(100,8))]), it('C',[(200,3)],[e(5,(190,3))]), it('D',[(60,8)],[e(5,(50,8))])])
    check('max 3, ranked weight PR, rep PR, run', [x['kind'] for x in r]==['w','w','r'] and r[0]['sub']=='D', [(x['kind'],x['sub']) for x in r])
    check('one highlight per lift', len(hl(pg,[it('Bench',[(145,8),(135,12)],[e(5,(140,8),(135,10))])]))==1)
    hit=pg.evaluate("""(()=>{window._hit=null;window._x=function(a){window._hit=a};const d=document.createElement('div');d.innerHTML='<button onclick="_x(\\''+paJs("a');alert(1);('b\\\\")+'\\')">x</button>';d.firstChild.click();return window._hit})()""")
    check('an id with quotes stays a string inside onclick', hit=="a');alert(1);('b\\", hit)
    # session times are range checked
    ct=pg.evaluate("finCleanTimes({'bad key':{s:1763500000000},'2026-11-19|x':{s:'x'},'2026-11-19|upperA':{s:1763500000000,l:1763502520000},'2026-11-18|upperB':{s:1763400000000,l:1}})")
    check('session times: bad keys and values dropped, l before s dropped', ct=={'2026-11-19|upperA':{'s':1763500000000,'l':1763502520000},'2026-11-18|upperB':{'s':1763400000000}}, ct)
    # ---------- the real flow ----------
    go(pg,'today'); pg.click('.tb-start'); pg.wait_for_timeout(500)
    D=pg.evaluate("PA.day")
    for i in range(60):
        if not pg.evaluate("!!document.getElementById('paLogBtn')"): break
        pg.click('#paLogBtn'); pg.wait_for_timeout(120); clear_timer(pg)
    fb=pg.evaluate("(()=>{const b=document.getElementById('paFinishBtn');if(!b)return null;const r=b.getBoundingClientRect(),c=getComputedStyle(b);return [b.textContent,c.backgroundColor,c.color,Math.round(r.height)]})()")
    check('after the last set: Done, persimmon, 44 px or more', fb and fb[0]=='Done' and fb[1]==PERS and fb[2]==INK and fb[3]>=44, fb)
    check('the session clock started on the first set', pg.evaluate("!!finTimes[todayKey()+'|%s']"%D))
    pg.evaluate("finTimes[todayKey()+'|%s'].s-=42*60000;finSaveTimes()"%D)
    pg.click('#paFinishBtn'); pg.wait_for_timeout(400)
    st=pg.evaluate("(()=>{const f=document.getElementById('finSheet');return [!f.hidden,f.getAttribute('role'),f.getAttribute('aria-modal'),document.activeElement.id]})()")
    check('finish card opens as a dialog with focus on the title', st==[True,'dialog','true','finTitle'], st)
    sm=pg.evaluate("FIN.sum")
    exp=pg.evaluate("(()=>{let n=0,v=0;paList('%s').forEach(x=>{const e=entryForWeek(getHistory(x.id),currentTrainWeek,x);finSets(e).forEach(s=>{n++;v+=s.w*s.r})});return [n,v]})()"%D)
    check('summary: sets and volume from the logged sets', [sm['sets'],round(sm['vol'])]==[exp[0],round(exp[1])], [sm['sets'],sm['vol'],exp])
    stats=pg.evaluate("[...document.querySelectorAll('.fin-stats li')].map(l=>l.innerText.replace(/\\s+/g,' '))")
    check('stats: sets, volume, minutes', stats[0]==str(exp[0])+' Sets' and stats[1].endswith(' Volume, lb') and stats[2]=='42 Minutes', stats)
    check('day name in the kicker', pg.evaluate("document.querySelector('.fin-k').textContent").lower()==sm['title'].lower()+' done', pg.evaluate("document.querySelector('.fin-k').textContent"))
    # 8.41: one message by priority, checked in t841_finish_card.py.
    check('one message, no highlight list', pg.evaluate("!document.querySelector('.fin-hl')&&!!FIN.sum.msg.head"))
    txt=pg.evaluate("finSheet.innerText")
    check('no dashes or exclamation marks', not any(c in txt for c in '–—!') and ' - ' not in txt, txt[:200])
    bt=pg.evaluate("[...document.querySelectorAll('.fin-btns button')].map(b=>{const r=b.getBoundingClientRect(),c=getComputedStyle(b);return [b.textContent,c.backgroundColor,Math.round(r.height)]})")
    check('8.41: Done is persimmon and first, Share next, all 44 px or more', bt[0][0]=='Done' and bt[0][1]==PERS and bt[1][0]=='Share' and all(x[2]>=44 for x in bt), bt)
    check('no sideways scroll on the finish card', pg.evaluate("finSheet.scrollWidth<=innerWidth&&document.documentElement.scrollWidth<=innerWidth"))
    pg.screenshot(path=shot('834-finish-390.png'))
    # the share image
    im=pg.evaluate("(()=>{const c=finDrawImage(FIN.sum,false),g=c.getContext('2d');const px=(x,y)=>Array.from(g.getImageData(x,y,1,1).data).slice(0,3);let cream=0;const d=g.getImageData(80,150,920,300).data;for(let i=0;i<d.length;i+=4)if(d[i]>230&&d[i+1]>225&&d[i+2]>215)cream++;return [c.width,c.height,px(4,4),px(1075,1345),cream]})()")
    check('share image is 1080 x 1350 on ultramarine with cream type', im[0]==1080 and im[1]==1350 and im[2]==[28,47,181] and im[3]==[28,47,181] and im[4]>2000, im[:4]+[im[4]])
    pg.wait_for_timeout(600)
    check('the image is ready before Share is tapped', pg.evaluate("!!FIN.blob&&FIN.blob.type==='image/png'"))
    with pg.expect_download() as dl: pg.click('#finShareBtn')
    d=dl.value
    check('no Web Share: Share downloads the PNG', d.suggested_filename.startswith('run-the-weights-') and d.suggested_filename.endswith('.png'), d.suggested_filename)
    check('download is confirmed in words', pg.evaluate("finMsg.textContent")=='Image saved to your downloads.')
    pg.evaluate("window._shared=null;navigator.canShare=f=>!!(f&&f.files);navigator.share=o=>{window._shared=o.files.map(f=>[f.name,f.type,f.size]);return Promise.resolve()};0")
    pg.click('#finShareBtn'); pg.wait_for_timeout(200)
    sh=pg.evaluate("window._shared")
    check('Web Share gets the PNG file', sh and sh[0][1]=='image/png' and sh[0][2]>10000, sh)
    pg.evaluate("navigator.share=o=>Promise.reject(Object.assign(new Error('x'),{name:'AbortError'}));finMsg.textContent='';0")
    pg.click('#finShareBtn'); pg.wait_for_timeout(200)
    check('cancelling the share sheet does nothing else', pg.evaluate("finMsg.textContent")=='')
    # keyboard
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    check('Escape closes it and focus goes back to Done', pg.evaluate("finSheet.hidden&&document.activeElement.id==='paFinishBtn'"))
    # edited set: the card recomputes
    ex0=pg.evaluate("paList('%s')[0].id"%D)
    pg.evaluate("paPickEx('%s');paPick('s1')"%ex0); pg.wait_for_timeout(150)
    pg.evaluate("PA.wLb+=50"); pg.click('#paLogBtn'); pg.wait_for_timeout(200); clear_timer(pg)
    pg.evaluate("PA.ex=null;renderPlanActive()"); pg.wait_for_timeout(100)
    pg.click('#paFinishBtn'); pg.wait_for_timeout(300)
    v2=pg.evaluate("FIN.sum.vol")
    check('an edited set changes the summary', abs(v2-exp[1]-50*pg.evaluate("normSet(entryForWeek(getHistory('%s'),currentTrainWeek,EX_BY_ID['%s']),entryForWeek(getHistory('%s'),currentTrainWeek,EX_BY_ID['%s']).s1).r"%(ex0,ex0,ex0,ex0)))<0.01, [v2,exp[1]])
    check('a weight above all history shows as a weight PR', pg.evaluate("FIN.sum.msg.k")=='a', pg.evaluate("FIN.sum.msg"))
    pg.click('.fin-done'); pg.wait_for_timeout(400)
    check('Done closes it and goes to Today', pg.evaluate("finSheet.hidden&&document.body.dataset.tab==='today'"))
    # backup carries the session times
    bk=json.loads(pg.evaluate(EXPORT)) if 'EXPORT' in globals() else None
    if bk is not None: check('backup carries session times', ('%s|%s'%(pg.evaluate("todayKey()"),D)) in bk.get('sessionTimes',{}), list(bk.get('sessionTimes',{}))[:3])
    check('no page errors', not errs, errs); ctx.close()
    # ---------- kg ----------
    ctx,pg,errs=page(b,390,844)
    pg.evaluate("setWeightUnit('kg')"); pg.wait_for_timeout(1500)
    r=hl(pg,[it('Bench',[(140,6)],[e(5,(135,8))])])
    check('kg: compared in lb, shown in kg', r and r[0]['kind']=='w' and r[0]['line'].startswith('63.5 kg on Bench') and 'was 61.2' in r[0]['line'], r)
    check('kg: no page errors', not errs, errs); ctx.close()
sys.exit(1 if done() else 0)
