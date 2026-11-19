"""8.26 per lift notes: Note row, Last time line, swaps, Quick Log notes, backup and restore."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, datetime, re
from playwright.sync_api import sync_playwright
from common import SEED, URL, ORIGIN, shot, baseline, HERE
T0=datetime.datetime(2026,11,18,10,0,0); RES=[]
def check(n, ok, d=''): RES.append((n,bool(ok),str(d)[:200])); print(('PASS ' if ok else 'FAIL ')+n+('  ['+str(d)[:200]+']' if d!='' else ''))
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':360,'height':780}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('dialog',lambda d:d.accept())
    pg.clock.install(time=T0)
    pg.add_init_script("localStorage.setItem('monk_onboarded_v1','1');localStorage.setItem('monk_onboarding_complete_v1','true');document.addEventListener('DOMContentLoaded',()=>{const st=document.createElement('style');st.textContent='#timerBar{pointer-events:none!important}';document.head.appendChild(st)})")
    pg.goto(URL); pg.wait_for_timeout(1000); pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1500)
    ev=pg.evaluate
    ev("goTab('training');scrollTo(0,0)"); pg.wait_for_timeout(400)
    ex=ev("[...document.querySelectorAll('#tab-training .lift-row')].filter(r=>r.offsetParent)[0].id.slice(4)")
    row='#row-'+ex
    if not ev("document.querySelector('%s').classList.contains('open')"%row): pg.locator(row+' .lift-head').click(); pg.wait_for_timeout(200)
    nb=pg.locator(row+' .card-foot-btn[data-panel="show-more"]'); nb.scroll_into_view_if_needed()
    bb=nb.bounding_box(); check('Note button is a 44 px target', bb['height']>=44 and bb['width']>=44, bb)
    nb.click(); pg.wait_for_timeout(200)
    ta=pg.locator('#ln-'+ex)
    check('tapping Note shows a multiline note field', ta.is_visible() and ev("document.getElementById('ln-%s').tagName"%ex)=='TEXTAREA')
    NOTE='Grip slipped on set 2. Use chalk <b>next</b> time.'
    ta.fill(NOTE); ta.blur(); pg.wait_for_timeout(150)
    check('autosaves on blur, keyed by exercise and date', ev("liftNoteFor('%s','2026-11-18')"%ex)==NOTE)
    ta.fill(NOTE+' Extra.'); pg.locator(row+' .lift-head').click(); pg.wait_for_timeout(200)
    check('autosaves on close without blur', ev("liftNoteFor('%s','2026-11-18')"%ex)==NOTE+' Extra.')
    check('closed card shows the ruled Note marker', pg.locator('[data-notemark="%s"]'%ex).is_visible())
    check('cards without a note show no marker', ev("[...document.querySelectorAll('.lift-note-mark')].filter(m=>m.offsetParent).length")==1)
    pg.locator(row+' .lift-head').click(); pg.wait_for_timeout(150); pg.locator(row+' .card-foot-btn[data-panel="show-more"]').click(); pg.wait_for_timeout(150)
    check('reopen: note still there', pg.locator('#ln-'+ex).input_value()==NOTE+' Extra.')
    pg.screenshot(path=shot('o826-note-open-360.png'))
    pg.reload(); pg.wait_for_timeout(1500); ev("goTab('training')"); pg.wait_for_timeout(300)
    check('note survives reload', ev("document.getElementById('ln-%s').value"%ex)==NOTE+' Extra.')
    # 500 cap
    ev("(()=>{const t=document.getElementById('ln-%s');t.value='x'.repeat(700);liftNoteInput(t);saveLiftNote(t)})()"%ex)
    check('note capped at 500', len(ev("liftNoteFor('%s','2026-11-18')"%ex))==500)
    ev("(()=>{const t=document.getElementById('ln-%s');t.value=%s;liftNoteInput(t);saveLiftNote(t)})()"%(ex,json.dumps(NOTE)))
    # delete a set, remove a set, finish: note stays
    ev("(()=>{const r=document.querySelector('%s .set-done-btn');r&&r.click()})()"%row); pg.wait_for_timeout(300)
    ev("askRemoveSet('%s')"%ex); pg.wait_for_timeout(200)
    ev("(()=>{const b=document.querySelector('#rmconfirm-%s button');b&&b.click()})()"%ex); pg.wait_for_timeout(200)
    ev("clearDayLogs(Object.keys(SPLIT_DAYS).find(k=>programmedDayExercises(k).some(e=>e.id==='%s')))"%ex+""); pg.wait_for_timeout(200)
    check('note survives logging, removing a set and clearing the day', ev("liftNoteFor('%s','2026-11-18')"%ex)==NOTE)
    # swap: note stays on the same exercise
    ev("openSwapSheet('%s')"%ex); pg.wait_for_timeout(300)
    nm=ev("(document.querySelector('#swapSheetTop .swap-row')||{}).dataset")
    if nm:
        pg.locator('#swapSheetTop .swap-row').first.click(); pg.wait_for_timeout(150); pg.locator('#swapSheetChoice .today-secondary').click(); pg.wait_for_timeout(400)
    check('after Swap, note stays attached to the exercise', ev("activeVariant(EX_BY_ID['%s'])!==EX_BY_ID['%s'].name"%(ex,ex)) and ev("liftNoteFor('%s','2026-11-18')"%ex)==NOTE and ev("document.getElementById('ln-%s').value"%ex)==NOTE, ev("activeVariant(EX_BY_ID['%s'])"%ex))
    # Progress history
    ev("quickLogSet('%s',100,5,null,'')"%ex)
    ev("goTab('calendar');setProgView('lifts');setProgEx('%s')"%ex); pg.wait_for_timeout(300)
    ph=ev("(document.querySelector('.prog-notes')||{}).innerHTML||''")
    check('note shows in the lift history, escaped', 'Grip slipped' in ph and '&lt;b&gt;next&lt;/b&gt;' in ph and '<b>' not in ph, ph[:160])
    pg.screenshot(path=shot('o826-progress-notes-360.png'))
    # next week: last time
    pg.clock.set_system_time(T0+datetime.timedelta(days=7)); pg.reload(); pg.wait_for_timeout(1500)
    ev("goTab('training')"); pg.wait_for_timeout(300)
    lt=ev("(document.querySelector('#row-%s .lift-note-last')||{}).textContent||''"%ex)
    check('next week the same lift shows Last time with its date', lt.startswith('Last time, Nov 18: Grip slipped'), lt)
    check('next week the field starts empty', ev("document.getElementById('ln-%s').value"%ex)=='')
    check('Last time is one line', ev("getComputedStyle(document.querySelector('#row-%s .lift-note-last')).whiteSpace"%ex)=='nowrap')
    # Quick Log
    ev("goTab('quicklog');toggleOldQuickLog&&document.getElementById('qlOld').style.display==='none'&&toggleOldQuickLog()"); pg.wait_for_timeout(300)
    ev("selectQuickLogLift('bb-squat')"); pg.wait_for_timeout(200)
    q=pg.locator('#qln-bb-squat'); check('Quick Log lift has the Note row', q.is_visible())
    q.fill('Squat felt deep today.'); pg.locator('#qlWeight').fill('135'); pg.locator('#qlReps').fill('5')
    pg.locator('#quicklogForm .quicklog-save-btn').click(); pg.wait_for_timeout(300)
    check('Quick Log note saved by exercise and date', ev("liftNoteFor('bb-squat','2026-11-25')")=='Squat felt deep today.')
    check('Quick Log entry still a new Quick Log entry', ev("(sessions['bb-squat']||[]).slice(-1)[0].quickLog===true"))
    # custom exercise
    cid=ev("addAnyDayExercise('Sled Push','quads')"); ev("selectQuickLogLift('%s')"%cid); pg.wait_for_timeout(200)
    pg.locator('#qln-'+cid).fill('Turf was slick.'); pg.locator('#qln-'+cid).blur(); pg.wait_for_timeout(100)
    check('custom exercises get notes the same way', ev("liftNoteFor('%s','2026-11-25')"%cid)=='Turf was slick.')
    # workout note unchanged
    ev("goTab('training')"); pg.wait_for_timeout(300)
    check('workout level note unchanged', pg.locator('#workoutNote').is_visible() and ev("document.getElementById('workoutNote').placeholder")=='How it felt, what to change next time.')
    # backup / restore
    bk=ev("""()=>new Promise(res=>{const o=URL.createObjectURL;URL.createObjectURL=bl=>{bl.text().then(res);return o.call(URL,bl)};exportData();})""")
    snap=ev("JSON.stringify(liftNotes)")
    check('backup includes liftNotes', json.loads(bk).get('liftNotes')==json.loads(snap))
    ev("""()=>new Promise(r=>{localStorage.removeItem('monk_lift_notes_v1');const q=indexedDB.deleteDatabase('monk_mode_store');q.onsuccess=q.onerror=q.onblocked=()=>r()})"""); pg.reload(); pg.wait_for_timeout(1500)
    check('wiped notes gone', ev("JSON.stringify(liftNotes)")=='{}')
    ev("""(txt)=>{const dt=new DataTransfer();dt.items.add(new File([txt],'b.json'));const i=document.createElement('input');i.type='file';i.files=dt.files;importData(i);}""", bk); pg.wait_for_timeout(2000)
    check('restore brings lift notes back', ev("JSON.stringify(liftNotes)")==snap)
    pg.reload(); pg.wait_for_timeout(1500)
    check('restored notes survive reload', ev("JSON.stringify(liftNotes)")==snap)
    old=json.loads(bk); old.pop('liftNotes')
    ev("""(txt)=>{const dt=new DataTransfer();dt.items.add(new File([txt],'b.json'));const i=document.createElement('input');i.type='file';i.files=dt.files;importData(i);}""", json.dumps(old)); pg.wait_for_timeout(1800)
    check('older backup without notes restores and keeps notes', ev("JSON.stringify(liftNotes)")==snap)
    check('no page errors', not errs, errs[:3])
    b.close()
n=sum(1 for r in RES if not r[1]); print('\n%d checks, %d failed'%(len(RES),n)); sys.exit(1 if n else 0)
