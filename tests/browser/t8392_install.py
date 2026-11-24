"""8.39.2 install notice: iPhone browser tab gets Add to Home Screen first, once. Standalone with no data gets Coming from Safari on Today. Settings has Moving to the Home Screen. 390 and 320."""
import sys, os, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from playwright.sync_api import sync_playwright
IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'
ANDROID = 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36'
STANDALONE = "Object.defineProperty(Navigator.prototype,'standalone',{get:()=>true,configurable:true});"
SAFARI_TAB = "Object.defineProperty(Navigator.prototype,'standalone',{get:()=>false,configurable:true});"
MEDIA = "(function(){var m=window.matchMedia;window.matchMedia=function(q){if(/display-mode: *standalone/.test(q))return {matches:true,media:q,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}};return m.call(window,q)}})();"
CARD = "getComputedStyle(installCard).display!=='none'"
INTRO = "getComputedStyle(introStory).display!=='none'"
MOVE = "getComputedStyle(todayMove).display!=='none'"
TITLE = 'Add to Home Screen first'
BODY = 'Tap Share, then Add to Home Screen, then open Run the Weights from your Home Screen. Do this before you log anything, because Safari and the Home Screen app do not share data.'
def ctx_for(b, ua=None, init='', w=390, h=844):
    kw = {'viewport': {'width': w, 'height': h}, 'service_workers': 'block', 'has_touch': True}
    if ua: kw['user_agent'] = ua
    ctx = b.new_context(**kw); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.clock.install(time=T0)
    if init: pg.add_init_script(init)
    pg.goto(URL); pg.wait_for_timeout(2000)
    return ctx, pg, errs
def lum(c):
    v = [int(x) / 255 for x in re.findall(r'\d+', c)[:3]]
    v = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]
def ratio(a, b):
    la, lb = lum(a), lum(b); return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
with sync_playwright() as p:
    b = p.chromium.launch()
    # 1. iPhone Safari tab, fresh: the card is the first screen.
    for W in [390, 320]:
        ctx, pg, errs = ctx_for(b, IPHONE, SAFARI_TAB, w=W)
        check('%d safari: the install card shows first' % W, pg.evaluate(CARD) and not pg.evaluate(INTRO) and pg.evaluate("onbFlow.style.display") == 'none')
        check('%d safari: title and body read as written' % W, pg.evaluate("installH.textContent") == TITLE and pg.evaluate("installP.textContent") == BODY)
        check('%d safari: buttons read I added it and Keep using Safari' % W, pg.evaluate("[installAdded.textContent,installKeep.textContent]") == ['I added it', 'Keep using Safari'])
        txt = pg.evaluate("installCard.innerText")
        check('%d safari: no dashes or exclamation marks' % W, not any(c in txt for c in '-–—!'), txt)
        check('%d safari: focus starts on the title' % W, pg.evaluate("document.activeElement.id") == 'installH')
        sizes = pg.evaluate("[installAdded,installKeep].map(e=>{var r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})")
        check('%d safari: both controls are 44 px or larger' % W, all(w >= 44 and h >= 44 for w, h in sizes), sizes)
        fit = pg.evaluate("[installCard.scrollWidth<=installCard.clientWidth,document.documentElement.scrollWidth<=innerWidth,[installH,installP,installAdded,installKeep].every(e=>{var r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+0.5})]")
        check('%d safari: fits with no sideways scroll' % W, all(fit), fit)
        cols = pg.evaluate("[getComputedStyle(installP).color,getComputedStyle(installCard).backgroundColor,getComputedStyle(installKeep).color,getComputedStyle(installAdded).color,getComputedStyle(installAdded).backgroundColor]")
        r1, r2, r3 = ratio(cols[0], cols[1]), ratio(cols[2], cols[1]), ratio(cols[3], cols[4])
        check('%d safari: body, link and button text pass 4.5 to 1' % W, min(r1, r2, r3) >= 4.5, [round(r1, 1), round(r2, 1), round(r3, 1)])
        pg.screenshot(path=shot('8392-install-%d.png' % W))
        check('%d safari: no page errors' % W, not errs, errs); ctx.close()
    # I added it: remembered, goes on to the story, not shown again.
    ctx, pg, errs = ctx_for(b, IPHONE, SAFARI_TAB)
    pg.click('#installAdded'); pg.wait_for_timeout(300)
    check('I added it: saved as added, the story follows', pg.evaluate("localStorage.getItem('monk_install_choice_v1')") == 'added' and not pg.evaluate(CARD) and pg.evaluate(INTRO))
    pg.reload(); pg.wait_for_timeout(2000)
    check('I added it: not shown again in this browser', not pg.evaluate(CARD) and pg.evaluate(INTRO))
    check('I added it: no page errors', not errs, errs); ctx.close()
    # Keep using Safari: remembered, story follows.
    ctx, pg, errs = ctx_for(b, IPHONE, SAFARI_TAB)
    pg.click('#installKeep'); pg.wait_for_timeout(300)
    check('Keep using Safari: saved as safari, the story follows', pg.evaluate("localStorage.getItem('monk_install_choice_v1')") == 'safari' and not pg.evaluate(CARD) and pg.evaluate(INTRO))
    pg.reload(); pg.wait_for_timeout(2000)
    check('Keep using Safari: not shown again', not pg.evaluate(CARD))
    check('Keep using Safari: no page errors', not errs, errs); ctx.close()
    # Desktop and Android browsers skip it.
    for name, ua in [('desktop', None), ('android', ANDROID)]:
        ctx, pg, errs = ctx_for(b, ua)
        check('%s: no install card, the story shows' % name, not pg.evaluate(CARD) and pg.evaluate(INTRO))
        check('%s: no page errors' % name, not errs, errs); ctx.close()
    # iPhone Safari with data already: no card, nothing changes.
    ctx, pg, errs = ctx_for(b, IPHONE, SAFARI_TAB + INIT)
    pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1800)
    check('safari with data: no install card, no story', not pg.evaluate(CARD) and not pg.evaluate(INTRO))
    pg.evaluate("renderToday()")
    check('safari with data: no Coming from Safari card', not pg.evaluate(MOVE))
    ctx.close()
    # 2. Standalone fresh: no install card, the story runs as before.
    ctx, pg, errs = ctx_for(b, IPHONE, STANDALONE)
    check('standalone fresh: no install card, the story shows', not pg.evaluate(CARD) and pg.evaluate(INTRO))
    ctx.close()
    # 3. Standalone, set up, nothing logged: the Today card.
    for W in [390, 320]:
        ctx, pg, errs = ctx_for(b, IPHONE, STANDALONE + INIT, w=W)
        pg.evaluate("setRunning(true);document.querySelectorAll('.settings-modal-overlay').forEach(m=>m.style.display='none');renderToday()")
        check('%d standalone empty: Coming from Safari shows on Today' % W, pg.evaluate(MOVE) and pg.evaluate("todayMoveH.textContent") == 'Coming from Safari?')
        mt = pg.evaluate("todayMove.innerText")
        check('%d standalone empty: the steps read as written' % W, 'Open the app in Safari, export a backup in Settings, then restore it here.' in mt and not any(c in mt for c in '-–—!'), mt)
        btn = pg.evaluate("(()=>{var e=todayMove.querySelector('button'),r=e.getBoundingClientRect();return [e.textContent,Math.round(r.width),Math.round(r.height)]})()")
        check('%d standalone empty: Dismiss is 44 px or larger' % W, btn[0] == 'Dismiss' and btn[1] >= 44 and btn[2] >= 44, btn)
        cols = pg.evaluate("[getComputedStyle(todayMove.querySelector('p')).color,getComputedStyle(todayMove).backgroundColor]")
        check('%d standalone empty: text passes 4.5 to 1' % W, ratio(*cols) >= 4.5, [cols, round(ratio(*cols), 1)])
        check('%d standalone empty: fits' % W, pg.evaluate("document.documentElement.scrollWidth<=innerWidth"))
        pg.evaluate("todayMove.scrollIntoView({block:'center'})"); pg.screenshot(path=shot('8392-move-%d.png' % W))
        # 4. Dismissed: gone, stays gone.
        pg.click('#todayMove button'); pg.wait_for_timeout(200)
        check('%d dismissed: the card hides and is remembered' % W, not pg.evaluate(MOVE) and pg.evaluate("localStorage.getItem('monk_move_card_v1')") == 'dismissed')
        pg.reload(); pg.wait_for_timeout(1500); pg.evaluate("renderToday()")
        check('%d dismissed: still hidden after reopening' % W, not pg.evaluate(MOVE))
        check('%d standalone: no page errors' % W, not errs, errs); ctx.close()
    # Standalone found by display-mode alone.
    ctx, pg, errs = ctx_for(b, IPHONE, MEDIA + INIT)
    pg.evaluate("renderToday()")
    check('display-mode standalone counts too', pg.evaluate("isStandalone()") and pg.evaluate(MOVE))
    ctx.close()
    # Standalone with data: no card.
    ctx, pg, errs = ctx_for(b, IPHONE, STANDALONE + INIT)
    pg.evaluate(SEED); pg.reload(); pg.wait_for_timeout(1800); pg.evaluate("renderToday()")
    check('standalone with data: no Coming from Safari card', not pg.evaluate(MOVE) and not pg.evaluate(CARD))
    pg.evaluate("localStorage.removeItem('monk_move_card_v1');renderToday()")
    check('standalone with data: logged sets keep it hidden', not pg.evaluate(MOVE))
    check('standalone with data: no page errors', not errs, errs); ctx.close()
    # A browser tab with nothing logged never shows the Today card.
    ctx, pg, errs = ctx_for(b, IPHONE, SAFARI_TAB + INIT)
    pg.evaluate("renderToday()")
    check('safari tab, nothing logged: no Today card', not pg.evaluate(MOVE))
    ctx.close()
    # Settings section.
    for W in [390, 320]:
        ctx, pg, errs = ctx_for(b, None, INIT, w=W)
        pg.evaluate("openSettingsModal()"); pg.wait_for_timeout(300)
        st = pg.evaluate("moveSec.innerText")
        check('%d settings: Moving to the Home Screen with three steps' % W, st.startswith('Moving to the Home Screen'.upper()) or st.startswith('Moving to the Home Screen'), st[:80])
        check('%d settings: steps name Backup, Add to Home Screen and Restore' % W, pg.evaluate("moveSec.querySelectorAll('li').length") == 3 and all(w in st for w in ['Backup', 'Add to Home Screen', 'Restore']) and not any(c in st for c in '-–—!'), st)
        check('%d settings: fits' % W, pg.evaluate("moveSec.scrollWidth<=moveSec.clientWidth+1"))
        pg.evaluate("moveSec.scrollIntoView({block:'center'})"); pg.screenshot(path=shot('8392-settings-%d.png' % W))
        check('%d settings: no page errors' % W, not errs, errs); ctx.close()
    b.close()
sys.exit(1 if done() else 0)
