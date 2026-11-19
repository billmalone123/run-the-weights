"""8.31 item 2: a run note saves only with its run; notes on dates with no run stay stored and hidden."""
import sys, os, json, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
STORE="JSON.parse(localStorage.getItem('monk_run_notes_v1')||'{\"notes\":{}}').notes"
D='2026-11-17'
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=page(b,360,700)
    pg.evaluate("delete runLogs['%s'];persistRunLogs()"%D)
    # start a note, cancel with the Cancel button
    pg.evaluate("openRunLog(null,'%s')"%D); pg.wait_for_timeout(200)
    pg.click('#rlNoteBtn'); pg.type('#rlNote','Hills, felt slow'); pg.wait_for_timeout(600)
    pg.evaluate("document.getElementById('rlNote').blur()"); pg.wait_for_timeout(100)
    check('typing and blur on an unsaved run store nothing', D not in pg.evaluate(STORE), pg.evaluate(STORE))
    pg.click('#rlNoteBtn'); pg.wait_for_timeout(100)
    check('closing the note row stores nothing', D not in pg.evaluate(STORE))
    pg.click('#runLogSheet .settings-cancel-btn'); pg.wait_for_timeout(200)
    check('Cancel discards the note', D not in pg.evaluate(STORE), pg.evaluate(STORE))
    pg.evaluate("openRunLog(null,'%s')"%D); pg.wait_for_timeout(200)
    check('reopened sheet has an empty note field', pg.evaluate("[document.getElementById('rlNote').value,document.getElementById('rlNoteBtn').innerText]")==['','Add a note'])
    pg.click('#rlNoteBtn'); pg.type('#rlNote','Tap outside'); pg.wait_for_timeout(500)
    pg.mouse.click(5,5); pg.wait_for_timeout(300)
    check('tapping outside the sheet discards the note', D not in pg.evaluate(STORE) and pg.evaluate("document.getElementById('runLogSheet').style.display")=='none')
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    check('after reload still no note for that date', D not in pg.evaluate(STORE))
    # save the run with a note
    pg.evaluate("openRunLog(null,'%s')"%D); pg.wait_for_timeout(200)
    pg.click('#rlNoteBtn'); pg.type('#rlNote','Hills, felt slow')
    pg.fill('#rlDist','4'); pg.fill('#rlMin','36'); pg.fill('#rlSec','0'); pg.click('#runLogSheet .today-start'); pg.wait_for_timeout(500)
    check('Save stores the note with the run', pg.evaluate(STORE).get(D)=='Hills, felt slow' and pg.evaluate("!!runLogs['%s']"%D))
    pg.evaluate("goTab('running')"); pg.wait_for_timeout(300)
    check('note appears in run history', 'Hills, felt slow' in pg.evaluate("document.getElementById('runTable').innerText"))
    # edit saved run's note: autosaves
    pg.evaluate("openRunLog(null,'%s')"%D); pg.wait_for_timeout(200)
    check('saved run reopens with its note', pg.evaluate("document.getElementById('rlNote').value")=='Hills, felt slow')
    pg.click('#rlNoteBtn'); pg.fill('#rlNote','Hills, felt strong'); pg.evaluate("document.getElementById('rlNote').dispatchEvent(new Event('input'))"); pg.wait_for_timeout(600)
    check('editing a saved run note autosaves while typing', pg.evaluate(STORE).get(D)=='Hills, felt strong')
    pg.fill('#rlNote','Hills, final'); pg.click('#runLogSheet .settings-cancel-btn'); pg.wait_for_timeout(200)
    check('closing a saved run keeps its edited note', pg.evaluate(STORE).get(D)=='Hills, final')
    # orphans from 8.30
    pg.evaluate("localStorage.setItem('monk_run_notes_v1',JSON.stringify({v:1,notes:Object.assign(%s,{'2026-11-03':'orphan one','2026-11-04':'orphan two'})}));delete runLogs['2026-11-03'];delete runLogs['2026-11-04'];persistRunLogs()"%STORE)
    pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none');goTab('running')"); pg.wait_for_timeout(300)
    check('orphan notes counted', pg.evaluate("orphanRunNoteCount()")==2, pg.evaluate("orphanRunNoteCount()"))
    check('orphan notes not shown in run history', 'orphan' not in pg.evaluate("document.body.innerText"))
    pg.evaluate("openRunLog(null,'2026-11-03')"); pg.wait_for_timeout(200)
    check('orphan note not shown in the Log a run sheet', pg.evaluate("[document.getElementById('rlNote').value,document.getElementById('rlNoteBtn').innerText]")==['','Add a note'])
    pg.fill('#rlDist','3'); pg.fill('#rlMin','27'); pg.click('#runLogSheet .today-start'); pg.wait_for_timeout(400)
    check('saving a run with an empty note keeps the old stored note', pg.evaluate(STORE).get('2026-11-03')=='orphan one')
    check('orphan notes kept in storage', pg.evaluate(STORE).get('2026-11-04')=='orphan two')
    check('no page errors', not errs, errs)
sys.exit(1 if done() else 0)
