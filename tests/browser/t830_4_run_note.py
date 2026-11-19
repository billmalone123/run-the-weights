"""8.30 item 4 (updated in 8.31): run note row, history line, length cap, backup and restore, range check."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
EXPORT="(()=>{let out=null;const o=URL.createObjectURL;const a=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};URL.createObjectURL=function(bl){out=bl;return 'blob:x'};exportData();URL.createObjectURL=o;HTMLAnchorElement.prototype.click=a;return out?out.text():null})()"
def openlog(pg): pg.evaluate("goTab('running');scrollTo(0,0)"); pg.wait_for_timeout(300); pg.click('#runTodayCard button'); pg.wait_for_timeout(300)
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=page(b,360,700); pg.on('dialog', lambda d: d.accept())
    openlog(pg)
    r=pg.evaluate("""(()=>{const bt=document.getElementById('rlNoteBtn'),f=document.getElementById('rlFeel').getBoundingClientRect(),r=bt.getBoundingClientRect(),cs=getComputedStyle(bt);
      return {txt:bt.innerText,h:Math.round(r.height),below:r.top>=f.bottom,bt:cs.borderTopWidth,bb:cs.borderBottomWidth,hidden:document.getElementById('rlNoteBody').hidden,exp:bt.getAttribute('aria-expanded'),fs:parseFloat(cs.fontSize)}})()""")
    check('Log a run: Add a note row under the feel choice, closed, small and ruled', r['txt']=='Add a note' and r['below'] and r['hidden'] and r['exp']=='false' and r['bt']=='1px' and r['bb']=='1px' and r['fs']<=15, r)
    check('Log a run: note row is 44 px tall', r['h']>=44, r['h'])
    pg.click('#rlNoteBtn'); pg.wait_for_timeout(100)
    check('Tap opens a plain text field with focus', pg.evaluate("!document.getElementById('rlNoteBody').hidden && document.activeElement.id==='rlNote' && document.activeElement.tagName==='TEXTAREA'"))
    pg.type('#rlNote','Windy, legs heavy <b>x</b>'); pg.wait_for_timeout(600)
    check('8.31: note on an unsaved run is not stored while typing', pg.evaluate("localStorage.getItem('monk_run_notes_v1')") in (None,'{"v":1,"notes":{}}'), pg.evaluate("localStorage.getItem('monk_run_notes_v1')"))
    pg.fill('#rlDist','3.1'); pg.fill('#rlMin','27'); pg.fill('#rlSec','30')
    pg.click('#runLogSheet .today-start'); pg.wait_for_timeout(400)
    h=pg.evaluate("(()=>{const r=document.querySelector('#runTable .run-note-row');return r?[r.innerText,r.querySelectorAll('b').length,r.previousElementSibling.innerText.split('\\t')[0]]:null})()")
    check('Run history shows the note under its run, as plain text', h and h[0].strip()=='Note Windy, legs heavy <b>x</b>' and h[1]==0 and h[2].startswith('Nov 19'), h)
    check('Note saved with the run (versioned key)', pg.evaluate("JSON.stringify(JSON.parse(localStorage.getItem('monk_run_notes_v1')))")=='{"v":1,"notes":{"2026-11-19":"Windy, legs heavy <b>x</b>"}}', pg.evaluate("localStorage.getItem('monk_run_notes_v1')"))
    check('The run itself saved unchanged', pg.evaluate("JSON.stringify(runLogs['2026-11-19'])")=='{"miles":3.1,"secs":1650,"hr":null,"feel":null,"type":"easy"}', pg.evaluate("JSON.stringify(runLogs['2026-11-19'])"))
    pg.screenshot(path=shot('p4-hist.png'), full_page=False)
    # reopen: closed, says Note, keeps text
    pg.evaluate("openRunLog()"); pg.wait_for_timeout(200)
    check('Reopen: closed by default, row says Note, text kept', pg.evaluate("[document.getElementById('rlNoteBody').hidden,document.getElementById('rlNoteBtn').innerText,document.getElementById('rlNote').value]")==[True,'Note','Windy, legs heavy <b>x</b>'])
    pg.click('#rlNoteBtn'); pg.fill('#rlNote','x'*600); pg.evaluate("document.getElementById('rlNote').dispatchEvent(new Event('input'))"); pg.click('#runLogSheet .settings-cancel-btn'); pg.wait_for_timeout(200)
    check('Max 500 characters, saved on close', pg.evaluate("runNoteFor('2026-11-19').length")==500)
    pg.evaluate("openRunLog()"); pg.click('#rlNoteBtn'); pg.fill('#rlNote','Easy shakeout.'); pg.evaluate("document.getElementById('rlNote').blur()"); pg.wait_for_timeout(100)
    check('Saves on blur', pg.evaluate("runNoteFor('2026-11-19')")=='Easy shakeout.')
    pg.evaluate("closeRunLog()")
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    pg.evaluate("goTab('running')"); pg.wait_for_timeout(300)
    check('After reload the note is still in history', 'Easy shakeout.' in pg.evaluate("document.getElementById('runTable').innerText"))
    bk=pg.evaluate(EXPORT); data=json.loads(bk)
    check('Backup includes run notes', data.get('runNotes')=={'v':1,'notes':{'2026-11-19':'Easy shakeout.'}}, data.get('runNotes'))
    errs1=list(errs); ctx.close()
    # restore into a fresh install
    ctx,pg,errs=page(b,360,700,seed=False); pg.on('dialog', lambda d: d.accept())
    pg.set_input_files('input[type=file][accept*=json] >> nth=0', files=[{'name':'b.json','mimeType':'application/json','buffer':bk.encode()}]); pg.wait_for_timeout(900)
    pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none');goTab('running')"); pg.wait_for_timeout(300)
    check('Restore brings the note back, shown in history', pg.evaluate("runNoteFor('2026-11-19')")=='Easy shakeout.' and 'Easy shakeout.' in pg.evaluate("document.getElementById('runTable').innerText"))
    # range check of stored values
    pg.evaluate("localStorage.setItem('monk_run_notes_v1',JSON.stringify({v:1,notes:{'2026-11-18':'ok','bad':'x','2026-13-40':'x','2026-11-17':42,'2026-11-16':'y'.repeat(900),'2026-11-15':'   '}}));runNotes=null")
    check('Stored notes are range checked on load', pg.evaluate("JSON.stringify(Object.keys(getRunNotes()).sort())+getRunNotes()['2026-11-16'].length")=='["2026-11-16","2026-11-18"]500', pg.evaluate("JSON.stringify(getRunNotes()).slice(0,80)"))
    check('no page errors', not errs1 and not errs, (errs1+errs)[:3]); ctx.close()
sys.exit(1 if done() else 0)
