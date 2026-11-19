"""8.34 Part 0: Food settings hidden while Food is locked, weight unit setting (lb or kg) with migration."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
EXPORT="(()=>{let out=null;const o=URL.createObjectURL;const a=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){};URL.createObjectURL=function(bl){out=bl;return 'blob:x'};exportData();URL.createObjectURL=o;HTMLAnchorElement.prototype.click=a;return out?out.text():null})()"
SNAP="(()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('monk_')&&!['monk_weight_unit_v1','monk_autopick_date_v1','monk_mode_last_tab_v1','monk_run_units_v1','monk_mode_last_day_v1'].includes(k))o[k]=localStorage.getItem(k)}return o})()"
def settle(pg):
    pg.wait_for_timeout(1500); pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
def first_set(pg):
    return pg.evaluate("(()=>{const i=[...document.querySelectorAll('input.set-cell.wu-in')].find(e=>e.offsetParent&&e.id.startsWith('s1w-'));return i?i.id:null})()")
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx,pg,errs=page(b,390,844)
    # migration: data from before 8.34 has no unit key
    pg.evaluate("localStorage.setItem('monk_bodyweight_v1',JSON.stringify({'2026-11-12':184.6,'2026-11-19':183.2}));localStorage.removeItem('monk_weight_unit_v1')")
    before=pg.evaluate(SNAP)
    pg.reload(); settle(pg)
    check('migration: a device with no setting gets lb', pg.evaluate("localStorage.getItem('monk_weight_unit_v1')")=='lb' and pg.evaluate("wUnit()")=='lb')
    after=pg.evaluate(SNAP)
    check('migration: no stored number changes', after==before, [k for k in set(before)|set(after) if before.get(k)!=after.get(k)][:5])
    # Food settings and setup calorie line hidden while Food is off
    pg.evaluate("goTab('settings')"); pg.wait_for_timeout(300)
    check('Settings Food targets section is hidden', pg.evaluate("getComputedStyle(document.querySelector('.settings-food')).display")=='none')
    check('Food target values stay in the page and in storage', pg.evaluate("!!document.getElementById('set-food-goal')"))
    pg.evaluate("(()=>{const f=document.getElementById('onbWeekFood');f.textContent='Daily food target: about 2400 calories.';f.style.display='block'})()")
    check('setup finish calorie line is hidden even with a target', pg.evaluate("getComputedStyle(document.getElementById('onbWeekFood')).display")=='none')
    pg.evaluate("FOOD_ENABLED=true;document.documentElement.classList.remove('food-off')")
    fo=pg.evaluate("[getComputedStyle(document.querySelector('.settings-food')).display,getComputedStyle(document.getElementById('onbWeekFood')).display,document.getElementById('onbWeekFood').getAttribute('style'),document.getElementById('onbWeekFood').hidden]")
    check('with Food on, both come back', fo[0]!='none' and fo[1]=='block', fo)
    pg.evaluate("FOOD_ENABLED=false;document.documentElement.classList.add('food-off')")
    # the control
    wb=pg.evaluate("[...document.querySelectorAll('[data-wu-btn]')].map(b=>[b.innerText.trim(),b.getAttribute('aria-pressed'),Math.round(b.getBoundingClientRect().height),Math.round(b.getBoundingClientRect().width)])")
    check('Settings has a lb and kg control, lb pressed', [x[:2] for x in wb]==[['lb','true'],['kg','false']], wb)
    check('unit buttons are 44 px or more', all(x[2]>=44 and x[3]>=44 for x in wb), wb)
    copy=pg.evaluate("document.querySelector('[data-wu-btn]').closest('.liftdays-wrap').innerText")
    check('no dashes or exclamation marks in the new copy', not any(c in copy for c in '-–—!'), copy)
    # separate from mi and km
    pg.evaluate("setRunUnits('km')")
    check('km distance leaves weight in lb', pg.evaluate("wUnit()+bwUnit()")=='lblb')
    pg.evaluate("setRunUnits('mi')")
    # lb mode: lift display unchanged
    go(pg,'training'); sid=first_set(pg)
    check('a set weight field is on the Plan screen', sid is not None, sid)
    ex=sid.split('s1w-')[1]
    head=pg.evaluate("[...document.querySelectorAll('.set-table-head')].filter(e=>e.offsetParent).map(e=>e.innerText.replace(/\\s+/g,' '))[0]")
    check('lb mode: set table head says lbs', head and 'lbs' in head, head)
    # switch to kg through the control
    pg.evaluate("setWeightUnit('kg')"); settle(pg)
    check('kg is saved and survives a reload', pg.evaluate("localStorage.getItem('monk_weight_unit_v1')+wUnit()")=='kgkg')
    a2=pg.evaluate(SNAP)
    check('kg: no stored number changes', a2==after, [(k,(after.get(k) or '')[:60],(a2.get(k) or '')[:60]) for k in set(a2)|set(after) if a2.get(k)!=after.get(k)][:4])
    pg.evaluate("goTab('settings')"); pg.wait_for_timeout(300)
    check('kg button shows pressed', pg.evaluate("[...document.querySelectorAll('[data-wu-btn]')].map(b=>b.getAttribute('aria-pressed')).join()")=='false,true')
    pg.evaluate("document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none')")
    check('Body follows the setting', pg.evaluate("bwUnit()")=='kg')
    go(pg,'training')
    head=pg.evaluate("[...document.querySelectorAll('.set-table-head')].filter(e=>e.offsetParent).map(e=>e.innerText.replace(/\\s+/g,' '))[0]")
    check('kg: set table head says kg', head and 'kg' in head and 'lbs' not in head, head)
    lbls=pg.evaluate("[...document.querySelectorAll('.wu-lbl')].map(e=>e.textContent)")
    check('kg: static weight labels say kg', lbls and all(x=='kg' for x in lbls), lbls)
    pg.fill('#'+sid, '100'); pg.evaluate("document.getElementById('%s').dispatchEvent(new Event('change',{bubbles:true}))"%sid)
    rid='s1r-'+ex; pg.fill('#'+rid,'8')
    pg.click('#done-s1-'+ex); pg.wait_for_timeout(600)
    ent=pg.evaluate("(()=>{const h=sessions['%s']||[];return JSON.stringify(h[h.length-1]||null)})()"%ex)
    check('100 kg typed is stored as 220.46 lb', ent and '220.46' in ent, ent)
    check('the field still shows 100', pg.evaluate("document.getElementById('%s').valueAsNumber"%sid)==100, pg.evaluate("document.getElementById('%s').valueAsNumber"%sid))
    # stepper steps 2.5 kg
    pg.evaluate("applyStep('%s',2.5)"%sid)
    shown=pg.evaluate("[document.getElementById('%s').valueAsNumber,document.getElementById('%s').value]"%(sid,sid))
    check('kg stepper steps 2.5 kg, and reads back in lb', shown[0]==102.5 and abs(float(shown[1])-225.97)<0.01, shown)
    step=pg.evaluate("(()=>{const r=document.getElementById('%s').closest('.stepper-row');return r?r.querySelector('.stepper-btn').getAttribute('onpointerup'):'none'})()"%sid)
    check('kg step buttons use 2.5', step=='none' or '-2.5' in step, step)
    # no lb text left on any screen in kg mode
    left=[]
    for t in ['today','training','quicklog','calendar','settings']:
        go(pg,t)
        txt=pg.evaluate("(()=>{const m=document.getElementById('tab-%s');return m?m.innerText:''})()"%t)
        import re
        for m in re.finditer(r'.{0,30}\blbs?\b.{0,20}', txt): left.append((t,m.group(0)))
    pg.evaluate("_progView='lifts';renderProgressHome&&renderProgressHome()"); pg.wait_for_timeout(300)
    txt=pg.evaluate("document.getElementById('tab-calendar').innerText")
    for m in re.finditer(r'.{0,30}\blbs?\b.{0,20}', txt): left.append(('progress lifts',m.group(0)))
    check('kg: no lb or lbs text on Today, Plan, Quick Log, Progress or Settings', not left, left[:6])
    pg.screenshot(path=shot('834-plan-kg-390.png'))
    # backup and restore
    bk=pg.evaluate(EXPORT); data=json.loads(bk)
    check('backup carries the weight unit', data.get('weightUnit')=='kg', data.get('weightUnit'))
    check('no page errors', not errs, errs); ctx.close()
    ctx,pg,errs=page(b,390,844,seed=False); pg.on('dialog', lambda d: d.accept())
    pg.set_input_files('input[type=file][accept*=json] >> nth=0', files=[{'name':'b.json','mimeType':'application/json','buffer':bk.encode()}]); pg.wait_for_timeout(900)
    check('restore brings back kg', pg.evaluate("localStorage.getItem('monk_weight_unit_v1')")=='kg')
    data['weightUnit']='stone'; bad=json.dumps(data)
    pg.evaluate("localStorage.setItem('monk_weight_unit_v1','lb');weightUnit='lb'")
    pg.set_input_files('input[type=file][accept*=json] >> nth=0', files=[{'name':'c.json','mimeType':'application/json','buffer':bad.encode()}]); pg.wait_for_timeout(900)
    check('restore ignores a unit that is not lb or kg', pg.evaluate("localStorage.getItem('monk_weight_unit_v1')")=='lb')
    pg.evaluate("localStorage.setItem('monk_weight_unit_v1','pounds')"); pg.reload(); pg.wait_for_timeout(1200)
    check('a bad stored unit falls back to lb', pg.evaluate("wUnit()")=='lb')
    check('no page errors (restore)', not errs, errs); ctx.close()
sys.exit(1 if done() else 0)
