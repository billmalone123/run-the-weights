"""8.35c first open story: who sees it, the flag, Skip, Next, Replay, photos, fit at 390 and 320, Why I built this, backups."""
import sys, os, json, glob; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
PHOTO = os.path.join(HERE, 'fixtures', 'intro_photo_test.jpg')
REFS = os.path.join(HERE, '..', '..', 'references')
VIS = "getComputedStyle(introStory).display!=='none'"
STEP = "_introStep"
def fresh(b, w=390, h=844, photo=False, init=''):
    ctx = b.new_context(viewport={'width': w, 'height': h}, service_workers='block', has_touch=True); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    if photo: pg.route('**/references/photo_billy_*.jpg', lambda r: r.fulfill(path=PHOTO, content_type='image/jpeg'))
    pg.clock.install(time=T0)
    if init: pg.add_init_script(init)
    pg.goto(URL); pg.wait_for_timeout(2000)
    return ctx, pg, errs
def store(pg): return pg.evaluate("JSON.stringify(Object.keys(localStorage).filter(k=>k!=='monk_intro_seen_v1').sort().map(k=>[k,localStorage.getItem(k)]))")
FIT = """(()=>{var el=introStory,out=[];
  ['#introH','#introP','#introNext','.intro-skip','#introPrivacy'].forEach(s=>{var e=el.querySelector(s);if(!e||e.hidden)return;var r=e.getBoundingClientRect();
    out.push({s:s,w:Math.round(r.width),h:Math.round(r.height),cut:e.scrollWidth>e.clientWidth+1||r.left<0||r.right>innerWidth+0.5})});
  return {ow:el.scrollWidth-el.clientWidth,dw:document.documentElement.scrollWidth-innerWidth,els:out}})()"""
with sync_playwright() as p:
    b = p.chromium.launch()
    # Who sees it.
    ctx, pg, errs = fresh(b)
    check('a new user with empty storage sees screen 1', pg.evaluate(VIS) and pg.evaluate("introH.textContent") == "HI, I'M BILLY." and pg.evaluate("onbFlow.style.display") == 'none')
    check('focus starts on the headline', pg.evaluate("document.activeElement.id") == 'introH')
    check('the story writes nothing until it ends', pg.evaluate("localStorage.getItem('monk_intro_seen_v1')") is None)
    # Next moves forward only, last button goes to setup.
    seen = []
    for i in range(3):
        seen.append(pg.evaluate("[%s,introH.textContent,document.getElementById('introNext').textContent,!introPrivacy.hidden]" % STEP))
        if i < 2: pg.click('#introNext'); pg.wait_for_timeout(250)
    check('Next goes 1, 2, 3 with the words as written', [s[:3] for s in seen] == [[0, "HI, I'M BILLY.", 'Next'], [1, 'LIFE GETS BUSY.', 'Next'], [2, 'A PLAN THAT BENDS WITH YOUR WEEK.', 'Set up my week']], seen)
    check('the privacy link shows on the last screen only', [s[3] for s in seen] == [False, False, True])
    check('the privacy link opens the privacy page', pg.evaluate("introPrivacy.getAttribute('href')") == 'privacy.html')
    pg.click('#introNext'); pg.wait_for_timeout(400)
    check('Set up my week goes to the existing setup', not pg.evaluate(VIS) and pg.evaluate("onbFlow.style.display") == 'flex')
    check('finishing sets the flag', pg.evaluate("localStorage.getItem('monk_intro_seen_v1')") == '1')
    pg.reload(); pg.wait_for_timeout(2000)
    check('the flag stops it showing twice', not pg.evaluate(VIS) and pg.evaluate("onbFlow.style.display") == 'flex')
    check('no page errors (fresh)', not errs, errs); ctx.close()
    # Swipe and Escape.
    ctx, pg, errs = fresh(b)
    pg.evaluate("(()=>{var e=introStory;function t(n,x){var o=new Touch({identifier:1,target:e,clientX:x,clientY:400});e.dispatchEvent(new TouchEvent(n,{touches:n==='touchstart'?[o]:[],changedTouches:[o],bubbles:true}))}t('touchstart',300);t('touchend',100)})()")
    check('a swipe left goes to the next screen', pg.evaluate(STEP) == 1)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    check('Escape skips and counts as seen', not pg.evaluate(VIS) and pg.evaluate("localStorage.getItem('monk_intro_seen_v1')") == '1')
    ctx.close()
    # Skip on each screen.
    for k in range(3):
        ctx, pg, errs = fresh(b)
        for _ in range(k): pg.click('#introNext'); pg.wait_for_timeout(200)
        sk = pg.locator('#introStory .intro-skip').bounding_box()
        check('screen %d: Skip is visible and 44 px' % (k + 1), sk['height'] >= 44 and sk['width'] >= 44, sk)
        pg.click('#introStory .intro-skip'); pg.wait_for_timeout(400)
        check('screen %d: Skip counts as seen and goes to setup' % (k + 1), not pg.evaluate(VIS) and pg.evaluate("localStorage.getItem('monk_intro_seen_v1')") == '1' and pg.evaluate("onbFlow.style.display") == 'flex')
        ctx.close()
    # Anyone with data never sees it, even without the intro flag or the setup flag.
    for name, init in [('a seeded user', None), ('data but no setup flag', "localStorage.setItem('monk_sessions_v1',JSON.stringify({'bb-squat':[{d:'2026-11-10',week:5,weight:185,reps:5}]}))")]:
        if init is None: ctx, pg, errs = page(b, 390, 844)
        else: ctx, pg, errs = fresh(b, init=init)
        pg.wait_for_timeout(500)
        check('%s never sees the intro' % name, not pg.evaluate(VIS))
        ctx.close()
    # Replay from Settings changes no saved data.
    ctx, pg, errs = page(b, 390, 844)
    before = store(pg)
    pg.evaluate("openSettingsModal()"); pg.wait_for_timeout(300)
    rb = pg.locator('#replayIntroBtn').bounding_box()
    check('Replay intro is in Settings, 44 px', rb['height'] >= 44, rb)
    pg.click('#replayIntroBtn'); pg.wait_for_timeout(400)
    check('Replay intro shows screen 1', pg.evaluate(VIS) and pg.evaluate(STEP) == 0)
    for _ in range(3): pg.click('#introNext'); pg.wait_for_timeout(250)
    check('Replay ends without opening setup', not pg.evaluate(VIS) and pg.evaluate("onbFlow.style.display") != 'flex')
    check('Replay changes no saved data', store(pg) == before)
    # Why I built this, from The Edge.
    pg.evaluate("goTab('info');goSec('edge')"); pg.wait_for_timeout(300)
    wl = pg.locator('#sec-edge .why-link').bounding_box()
    check('The Edge links to Why I built this, 44 px', wl['height'] >= 44, wl)
    pg.click('#sec-edge .why-link'); pg.wait_for_timeout(300)
    why = pg.evaluate("[document.getElementById('sec-why').style.display,[...whyBody.querySelectorAll('h3')].map(h=>h.textContent),[...whyBody.querySelectorAll('p')].map(h=>h.textContent)]")
    story = pg.evaluate("[INTRO_STORY.map(d=>d.h),INTRO_STORY.map(d=>d.p)]")
    check('Why I built this shows the same story', why[0] == 'block' and why[1] == story[0] and why[2] == story[1], why)
    check('the story has no D1, captain or ranking words', not any(w in ' '.join(story[0] + story[1]) for w in ['Division', 'captain', 'D1', 'rank']))
    # Backups carry the flag as a boolean.
    with pg.expect_download() as dl: pg.evaluate("exportData()")
    data = json.load(open(dl.value.path()))
    check('backup holds introSeen as a boolean', data.get('introSeen') is True)
    pg.evaluate("setIntroSeen(false)")
    for v, want in [('yes', None), (True, '1')]:
        d2 = dict(data); d2['introSeen'] = v; f = os.path.join(SHOTS, '_restore_intro.json'); json.dump(d2, open(f, 'w'))
        pg.set_input_files('input[onchange="importData(this)"] >> nth=0', f); pg.wait_for_timeout(800)
        check('restore of introSeen=%r' % (v,), pg.evaluate("localStorage.getItem('monk_intro_seen_v1')") == want)
    check('no page errors (replay)', not errs, errs); ctx.close()
    # Photos: missing and present, fit and screenshots at 390 and 320.
    for photo in [False, True]:
        for W in [390, 320]:
            ctx, pg, errs = fresh(b, W, 844 if W == 390 else 640, photo=photo)
            for i in range(3):
                pg.wait_for_timeout(300)
                ph = pg.evaluate("(()=>{var i=introPhoto.querySelector('img');return {hidden:introPhoto.hidden,h:Math.round(introPhoto.getBoundingClientRect().height),img:!!i,ok:i?i.complete&&i.naturalWidth>0:null,alt:i?i.getAttribute('alt'):null}})()")
                tag = '%d %s screen %d' % (W, 'photo' if photo else 'no photo', i + 1)
                tall = pg.evaluate("innerHeight") > 700
                if photo and tall: check(tag + ': the photo loads with empty alt', ph['img'] and ph['ok'] and ph['alt'] == '' and not ph['hidden'] and ph['h'] > 0, ph)
                elif photo: check(tag + ': short screen, the photo steps aside with no empty frame', ph['img'] and ph['ok'] and ph['h'] == 0, ph)
                else: check(tag + ': no image and no empty frame', not ph['img'] and ph['hidden'] and ph['h'] == 0, ph)
                fit = pg.evaluate(FIT)
                nb = pg.evaluate("(()=>{var r=document.getElementById('introNext').getBoundingClientRect();return [Math.round(r.bottom),innerHeight]})()")
                check(tag + ': Next is on screen without scrolling', nb[0] <= nb[1], nb)
                tx = pg.evaluate("[Math.round(introP.getBoundingClientRect().bottom),Math.round(document.querySelector('#introStory .intro-foot').getBoundingClientRect().top)]")
                check(tag + ': the whole story text shows above the footer', tx[0] <= tx[1], tx)
                check(tag + ': no sideways scroll, no cut text, 44 px targets', fit['ow'] <= 0 and fit['dw'] <= 0 and not any(e['cut'] for e in fit['els']) and all(e['h'] >= 44 for e in fit['els'] if e['s'] not in ('#introH', '#introP')), fit)
                pg.screenshot(path=shot('835c-intro-%d-%d%s.png' % (i + 1, W, '-photo' if photo else '')))
                if i < 2: pg.click('#introNext')
            check('%d %s: no page errors' % (W, 'photo' if photo else 'no photo'), not errs, errs); ctx.close()
    # Real photos, when added, must be under 150 KB.
    real = glob.glob(os.path.join(REFS, 'photo_billy_*.jpg'))
    if real: check('photos in references are under 150 KB', all(os.path.getsize(f) < 150 * 1024 for f in real), [(os.path.basename(f), os.path.getsize(f)) for f in real])
    else: print('no photo_billy files in references, size check skipped')
    check('the test photo is under 150 KB', os.path.getsize(PHOTO) < 150 * 1024)
sys.exit(1 if done() else 0)
