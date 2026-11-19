"""8.30 item 2: Quick Log recent workouts load a session; the session list survives a reload."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
LUM="""(el)=>{const p=c=>{const m=c.match(/[\\d.]+/g).map(Number);return m};const L=c=>{const [r,g,b]=p(c).slice(0,3).map(v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)});return 0.2126*r+0.7152*g+0.0722*b};
let bg=null,e=el;while(e){const c=getComputedStyle(e).backgroundColor;if(c&&!c.startsWith('rgba(0, 0, 0, 0)')&&c!=='transparent'){bg=c;break}e=e.parentElement}bg=bg||getComputedStyle(document.body).backgroundColor;
const a=L(getComputedStyle(el).color),b=L(bg);return (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05)}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=page(b)
    # two Quick Log sessions on Nov 17, three hours apart
    pg.evaluate("""(()=>{const t=new Date(2026,10,17,7,0,0).getTime();const add=(id,w,r,ts)=>{(sessions[id]=sessions[id]||[]).push({d:'2026-11-17',ts:ts,week:currentTrainWeek,weight:w,reps:r,quickLog:true})};
      add('flat-bb-bench',100,5,t);add('lat-pulldown',90,10,t+600e3);add('seated-ohp',50,8,t+3*3600e3);saveSessions();})()""")
    go(pg,'quicklog')
    rw=pg.evaluate("""(()=>{const rows=[...document.querySelectorAll('#qlRecentWList .ql-rw')];const exp=recentWorkouts(5);
      return {n:rows.length,txt:rows.map(r=>r.innerText.replace(/\\s+/g,' ')),h:rows.map(r=>Math.round(r.getBoundingClientRect().height)),bb:rows.map(r=>getComputedStyle(r).borderBottomWidth),
      exp:exp.map(g=>[g.d,g.ids.length,g.q]),top:Math.round(document.getElementById('qlRecentW').getBoundingClientRect().top),
      add:Math.round(document.getElementById('qlAddExBtn').getBoundingClientRect().top),howlong:Math.round(document.getElementById('qlHeading').getBoundingClientRect().top),
      first:document.getElementById('quicklogSection').firstElementChild.id}})()""")
    print('  ',rw['txt'][:5]); print('  ',rw['exp'])
    check('Recent workouts: five rows, newest first, at the top of Quick Log above Add exercise', rw['n']==5 and rw['first']=='qlRecentW' and rw['top']<rw['howlong']<rw['add'] and [e[0] for e in rw['exp']]==sorted([e[0] for e in rw['exp']],reverse=True), rw)
    check('Recent workouts: ruled rows, 44 px or taller', all(h>=44 for h in rw['h']) and all(x=='1px' for x in rw['bb']), rw['h'])
    check('Recent workouts: two Quick Log sessions on Nov 17 stay separate rows', sum(1 for e in rw['exp'] if e[0]=='2026-11-17' and e[2])==2, rw['exp'])
    check('Recent workouts: each row shows the date and the lift names', all(t.split(' ')[0] in ('Mon','Tue','Wed','Thu','Fri','Sat','Sun') and ',' in t or rw['exp'][i][1]==1 for i,t in enumerate(rw['txt'])), rw['txt'])
    cr=pg.evaluate("(el)=>0",None); cr=pg.eval_on_selector('#qlRecentWList .ql-rw-lifts',LUM); cd=pg.eval_on_selector('#qlRecentWList .ql-rw-date',LUM)
    check('Recent workouts: text contrast 4.5:1 or better', cr>=4.5 and cd>=4.5, (round(cr,2),round(cd,2)))
    # load a plan session (third row is the Nov 16 plan session or similar): pick first plan row
    idx=[i for i,e in enumerate(rw['exp']) if not e[2]][0]
    before=pg.evaluate("Object.values(sessions).reduce((a,l)=>a+l.length,0)")
    pg.locator('#qlRecentWList .ql-rw').nth(idx).click(); pg.wait_for_timeout(300)
    st=pg.evaluate("""(i)=>{const g=recentWorkouts(5)[i];return {ids:g.ids,items:_qs.items.map(t=>t.exId),pre:_qs.items.map((t,k)=>{const l=latestEntry(t.exId);return [document.getElementById('qsw-'+k+'-0').value,document.getElementById('qsr-'+k+'-0').value,String(l?l.weight:''),String(l?l.reps:'')]}),
       focus:document.activeElement&&(document.activeElement.id||document.activeElement.className),n:Object.values(sessions).reduce((a,l)=>a+l.length,0)}}""",idx)
    check('Tap a recent workout: its lifts load into the session in order', st['items']==st['ids'] and len(st['ids'])>=3, st['items'])
    check('Tap a recent workout: last numbers prefilled', all(x[0]==x[2] and x[1]==x[3] for x in st['pre']), st['pre'][:3])
    check('Tap a recent workout: nothing logged yet', st['n']==before, (before,st['n']))
    check('Tap a recent workout: focus goes to the first set', 'set-done-btn' in str(st['focus']) or str(st['focus']).startswith('qs'), st['focus'])
    # speed: open Quick Log, tap row, tap done = 2 taps to first logged set
    pg.locator('#qs-0 .set-done-btn').first.click(); pg.wait_for_timeout(200)
    n2=pg.evaluate("Object.values(sessions).reduce((a,l)=>a+l.length,0)")
    check('Recent lift reaches its first logged set in 3 taps or fewer (row, then the check)', n2==before+1, (before,n2))
    last=pg.evaluate("(()=>{const l=Object.values(sessions).flat().filter(e=>e.quickLog).sort((a,b)=>b.ts-a.ts)[0];return [l.quickLog,l.d]})()")
    check('The logged set is a new Quick Log entry for today', last==[True,'2026-11-19'], last)
    # type into an unlogged row, then reload
    pg.fill('#qsw-1-0','123'); pg.fill('#qsr-1-0','7'); pg.wait_for_timeout(100)
    NORM="JSON.stringify(_qs.items.map(t=>({exId:t.exId,rows:t.rows.map(r=>[String(r.w),String(r.r),!!r.done])})))"
    snap=pg.evaluate(NORM)
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')"); go(pg,'quicklog')
    snap2=pg.evaluate(NORM)
    dom=pg.evaluate("[document.querySelectorAll('#qlSessionList .qs-ex').length,document.getElementById('qsw-1-0').value,document.getElementById('qsr-1-0').value,document.querySelector('#qs-0 .qs-set').classList.contains('done')]")
    check('Reload mid workout keeps the session list, logged marks and typed numbers', snap2==snap and dom[1:]==['123','7',True], (dom,snap2==snap))
    check('Saved session key is versioned and today', pg.evaluate("(()=>{const v=JSON.parse(localStorage.getItem('monk_ql_session_v1'));return v.v===1&&v.day==='2026-11-19'})()"))
    # backup carries it; restore on the same day brings it back
    bk=pg.evaluate("(()=>{let out=null;const o=URL.createObjectURL;const a=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};URL.createObjectURL=function(bl){out=bl;return 'blob:x'};exportData();URL.createObjectURL=o;HTMLAnchorElement.prototype.click=a;return out?out.text():null})()")
    data=json.loads(bk) if bk else {}
    check('Backup includes the Quick Log session', bool(data.get('quickLogSession')) and len(data['quickLogSession']['items'])==len(json.loads(snap)), list(data.keys())[-6:])
    pg.evaluate("newQuickSession()")
    check('Start a new session clears the saved list', pg.evaluate("localStorage.getItem('monk_ql_session_v1')") is None and pg.evaluate("_qs.items.length")==0)
    pg.on('dialog', lambda d: d.accept())
    pg.set_input_files('#importFile' if pg.locator('#importFile').count() else 'input[type=file][accept*=json]', files=[{'name':'b.json','mimeType':'application/json','buffer':bk.encode()}]); pg.wait_for_timeout(800)
    check('Restore on the same day brings the session list back', pg.evaluate("_qs.items.length")==len(json.loads(snap)), pg.evaluate("_qs.items.length"))
    # bad values in storage are range checked
    pg.evaluate("localStorage.setItem('monk_ql_session_v1',JSON.stringify({v:1,day:'2026-11-19',start:1,items:[{exId:'nope',rows:[{w:1,r:1}]},{exId:'flat-bb-bench',rows:[{w:99999,r:-3,done:true},{w:'abc',r:5}]}]}))")
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')"); go(pg,'quicklog')
    check('Saved values out of range are dropped on load', pg.evaluate("JSON.stringify(_qs.items)")=='[{"exId":"flat-bb-bench","rows":[{"w":"","r":"","done":false},{"w":"","r":5,"done":false}]}]', pg.evaluate("JSON.stringify(_qs.items)"))
    # next day: the list is cleared
    pg.clock.set_system_time(datetime.datetime(2026,11,20,9,0,0)); go(pg,'quicklog')
    check('Next day: the session list is cleared', pg.evaluate("_qs.items.length")==0 and pg.evaluate("localStorage.getItem('monk_ql_session_v1')") is None)
    check('no page errors', not errs, errs[:3]); ctx.close()
    # empty state: new user, no logs
    ctx,pg,errs=page(b,seed=False); go(pg,'quicklog')
    check('Empty state: Recent workouts hidden with no logs', pg.evaluate("getComputedStyle(document.getElementById('qlRecentW')).display")=='none')
    check('no page errors (empty)', not errs, errs[:3]); ctx.close()
sys.exit(1 if done() else 0)
