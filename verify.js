/* Width self-check demanded by "My site flow.pdf".
   Drives the installed Chrome (no bundled browser download available). */
const { chromium } = require('playwright');
const path = require('path');

const URL = 'http://127.0.0.1:8099/index.html';

const WIDTHS = [320, 360, 390, 414, 768, 834, 1024, 1280, 1440, 1920, 2560];
// Short viewports get their own cases: a landscape phone, and the laptop-window
// size where the headline was crowding the photograph.
const SHORT = [
  { w: 740, h: 360, name: 'landscape-phone' },
  { w: 1024, h: 455, name: 'short-laptop' },
  { w: 1366, h: 500, name: 'short-wide' },
];

(async () => {
  const browser = await chromium.launch({
    channel: 'chrome',
    args: ['--autoplay-policy=no-user-gesture-required'],
  });

  const results = [];
  let hardFail = 0;

  async function audit(page, label, w, h) {
    /* Skip-link check must run FIRST. scrollIntoView() later in this function moves
       Chrome's sequential-focus navigation starting point, so a Tab pressed after it
       resumes from the footer instead of the document start. */
    await page.keyboard.press('Tab');
    const skipReachable = await page.evaluate(() => {
      const s = document.querySelector('.skip');
      const b = s.getBoundingClientRect();
      return { ok: b.top >= 0 && document.activeElement === s, top: Math.round(b.top) };
    });
    await page.evaluate(() => document.activeElement.blur());

    /* Capture the banner's first beat before this audit scrolls anywhere else.
       The reveal is intentionally one-way and removes its listener at completion,
       so scrolling to the film and back is not the initial state. */
    const beat1 = await page.evaluate(() => {
      const stage = document.querySelector('.banner__stage').getBoundingClientRect();
      const copy = getComputedStyle(document.getElementById('banner-copy'));
      return {
        stageFills: stage.height >= window.innerHeight - 2,
        copyOpacity: parseFloat(copy.opacity),
        stageH: Math.round(stage.height), vh: window.innerHeight,
      };
    });

    const r = await page.evaluate(() => {
      const out = {
        docW: document.documentElement.scrollWidth,
        winW: window.innerWidth,
        overflow: [],
        tinyTap: [],
        smallText: [],
        stickyWorks: null,
        videoCovers: null,
        ctaVisible: null,
        skipReachable: null,
      };

      /* Elements wider than the viewport, EXCEPT those inside a clipping ancestor.
         A marquee track is deliberately wider than the screen and is clipped by its
         parent; that is not a layout bug. The real invariant is that the document
         does not scroll horizontally, asserted separately via docW vs winW. */
      const vw = window.innerWidth;
      const isClipped = (el) => {
        for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
          const ov = getComputedStyle(p);
          if (/hidden|clip|auto|scroll/.test(ov.overflowX)) return true;
        }
        return false;
      };
      document.querySelectorAll('body *').forEach((el) => {
        const b = el.getBoundingClientRect();
        if (b.width === 0 && b.height === 0) return;
        if (b.right > vw + 1.5 || b.left < -1.5) {
          const cs = getComputedStyle(el);
          if (cs.position === 'fixed') return;   // skip link parks off-screen by design
          if (isClipped(el)) return;
          out.overflow.push(
            (el.tagName + (el.className ? '.' + String(el.className).split(' ')[0] : '')) +
            ' L' + Math.round(b.left) + ' R' + Math.round(b.right)
          );
        }
      });

      // tap targets on real interactive elements
      document.querySelectorAll('a[href], button').forEach((el) => {
        const b = el.getBoundingClientRect();
        if (b.width === 0 || b.height === 0) return;
        const cs = getComputedStyle(el);
        if (cs.visibility === 'hidden' || cs.position === 'fixed') return;
        if (b.height < 44 || b.width < 44) {
          out.tinyTap.push((el.textContent || el.tagName).trim().slice(0, 28) +
            ' ' + Math.round(b.width) + 'x' + Math.round(b.height));
        }
      });

      // body copy must stay legible on mobile
      document.querySelectorAll('p, li').forEach((el) => {
        if (!el.textContent.trim() || el.textContent.trim().length < 25) return;
        const fs = parseFloat(getComputedStyle(el).fontSize);
        if (fs < 15.5) out.smallText.push(fs.toFixed(1) + 'px: ' + el.textContent.trim().slice(0, 30));
      });

      return out;
    });

    /* The act is mid-page, so scroll to a point genuinely inside its spacer.
       behavior:'instant' matters: the page sets scroll-behavior:smooth, so a plain
       scrollTo animates and the assertion below would measure mid-flight. */
    await page.evaluate(() => {
      const act = document.getElementById('act');
      const top = act.getBoundingClientRect().top + window.scrollY;
      window.scrollTo({ top: top + act.offsetHeight * 0.25, behavior: 'instant' });
    });
    await new Promise((res) => setTimeout(res, 350));
    const sticky = await page.evaluate(() => {
      const st = document.querySelector('.act__stage');
      if (!st) return { ok: false, why: 'no stage' };
      const b = st.getBoundingClientRect();
      return { ok: Math.abs(b.top) < 2, top: Math.round(b.top), h: Math.round(b.height) };
    });
    r.stickyWorks = sticky;

    // exactly one stage panel showing a quarter of the way into the act
    r.panelState = await page.evaluate(() => {
      const on = [...document.querySelectorAll('.panel')].filter((p) => p.hasAttribute('data-on'));
      return { visible: on.length, text: on[0] ? on[0].querySelector('h2').textContent.trim() : null };
    });

    /* Banner is a two-beat reveal: beat one was captured above before any scroll;
       beat two writes the copy on and must fit inside the viewport. */
    await page.evaluate(() => {
      const b = document.getElementById('banner');
      window.scrollTo({ top: (b.offsetHeight - window.innerHeight) * 0.75, behavior: 'instant' });
    });
    await new Promise((res) => setTimeout(res, 420));
    const beat2 = await page.evaluate(() => {
      const copy = document.getElementById('banner-copy');
      const cs = getComputedStyle(copy);
      const h1 = copy.querySelector('h1').getBoundingClientRect();
      const cta = copy.querySelector('a[download]').getBoundingClientRect();
      return {
        opacity: parseFloat(cs.opacity),
        h1Top: Math.round(h1.top), h1Bottom: Math.round(h1.bottom),
        ctaBottom: Math.round(cta.bottom), ctaH: Math.round(cta.height),
        fits: h1.top >= 0 && cta.bottom <= window.innerHeight + 1 && cta.height >= 44,
      };
    });

    r.banner = {
      ok: beat1.stageFills && beat1.copyOpacity < 0.1 &&
          beat2.opacity > 0.95 && beat2.fits,
      beat1, beat2,
    };

    // Desktop keeps the scrub video; mobile uses three native-playback scenes.
    r.videoCovers = await page.evaluate(() => {
      const mobile = window.matchMedia('(max-width:48rem), (pointer:coarse)').matches &&
        !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (mobile) {
        const scenes = [...document.querySelectorAll('.mobile-scene')];
        const act = document.getElementById('act');
        return {
          ok: scenes.length === 3 && getComputedStyle(act).display === 'none',
          w: window.innerWidth, h: window.innerHeight,
          fit: 'native-story',
          scenes: scenes.length,
        };
      }
      const v = document.querySelector('.act__video');
      const b = v.getBoundingClientRect();
      return {
        ok: b.width >= window.innerWidth - 1 && b.height >= window.innerHeight - 1,
        w: Math.round(b.width), h: Math.round(b.height),
        fit: getComputedStyle(v).objectFit,
      };
    });

    // primary CTA present and tappable in the closing band
    await page.evaluate(() => {
      document.getElementById('contact').scrollIntoView({ behavior: 'instant', block: 'center' });
    });
    await new Promise((res) => setTimeout(res, 200));
    r.ctaVisible = await page.evaluate(() => {
      const a = document.querySelector('#contact a[download]');
      if (!a) return { ok: false };
      const b = a.getBoundingClientRect();
      const mid = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
      return {
        ok: b.height >= 44 && b.width >= 44 && (a === mid || a.contains(mid)),
        size: Math.round(b.width) + 'x' + Math.round(b.height),
        hitBlockedBy: a === mid || a.contains(mid) ? null : (mid ? mid.tagName + '.' + mid.className : 'none'),
      };
    });

    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
    r.skipReachable = skipReachable;

    const fails = [];
    if (r.docW > r.winW + 1) fails.push('H-SCROLL ' + r.docW + '>' + r.winW);
    if (r.overflow.length) fails.push('OVERFLOW ' + r.overflow.slice(0, 3).join('; '));
    if (r.tinyTap.length) fails.push('TAP<44 ' + r.tinyTap.slice(0, 3).join('; '));
    if (r.smallText.length) fails.push('TEXT<16 ' + r.smallText.slice(0, 2).join('; '));
    if (!r.stickyWorks.ok) fails.push('STICKY BROKEN top=' + r.stickyWorks.top);
    if (r.panelState.visible !== 1) fails.push('PANELS visible=' + r.panelState.visible);
    if (!r.banner.ok) fails.push('BANNER ' + JSON.stringify(r.banner));
    if (!r.videoCovers.ok) fails.push('VIDEO NOT COVERING ' + r.videoCovers.w + 'x' + r.videoCovers.h);
    if (!r.ctaVisible.ok) fails.push('CTA ' + JSON.stringify(r.ctaVisible));
    if (!r.skipReachable.ok) fails.push('SKIP LINK ' + JSON.stringify(r.skipReachable));

    if (fails.length) hardFail++;
    results.push({ label, size: w + 'x' + h, fails });
    console.log(
      (fails.length ? 'FAIL ' : 'pass ') + String(w + 'x' + h).padEnd(10) +
      (fails.length ? fails.join(' | ') : '')
    );
  }

  for (const w of WIDTHS) {
    const h = w <= 500 ? 780 : 900;
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto(URL, { waitUntil: 'load' });
    await page.waitForTimeout(450);
    await audit(page, 'w' + w, w, h);
    await page.close();
  }

  // short viewports, where the headline is most likely to crowd the image
  for (const s of SHORT) {
    const page = await browser.newPage({ viewport: { width: s.w, height: s.h } });
    await page.goto(URL, { waitUntil: 'load' });
    await page.waitForTimeout(450);
    await audit(page, s.name, s.w, s.h);
    await page.close();
  }

  // reduced-motion must show every stage panel, not hide them
  {
    const ctx = await browser.newContext({
      viewport: { width: 390, height: 780 },
      reducedMotion: 'reduce',
    });
    const page = await ctx.newPage();
    await page.goto(URL, { waitUntil: 'load' });
    await page.waitForTimeout(400);
    const rm = await page.evaluate(() => {
      const panels = [...document.querySelectorAll('.panel')];
      const vis = panels.filter((p) => {
        const cs = getComputedStyle(p);
        return cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0.5;
      });
      return {
        total: panels.length,
        visible: vis.length,
        actHeight: Math.round(document.querySelector('.act').getBoundingClientRect().height),
        docW: document.documentElement.scrollWidth,
        winW: window.innerWidth,
      };
    });
    const ok = rm.visible === rm.total && rm.docW <= rm.winW + 1;
    if (!ok) hardFail++;
    console.log((ok ? 'pass ' : 'FAIL ') + 'reduced-motion'.padEnd(10) +
      ' panels ' + rm.visible + '/' + rm.total + ' actH=' + rm.actHeight +
      ' docW=' + rm.docW + '/' + rm.winW);
    await ctx.close();
  }

  // screenshots for the record
  for (const w of [390, 1024, 1920]) {
    const page = await browser.newPage({ viewport: { width: w, height: w <= 500 ? 780 : 900 } });
    await page.goto(URL, { waitUntil: 'load' });
    await page.waitForTimeout(400);
    await page.screenshot({ path: `_shot_${w}_hero.png` });
    await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight * 0.93, behavior: 'instant' }));
    await page.waitForTimeout(500);
    await page.screenshot({ path: `_shot_${w}_end.png` });
    await page.close();
  }

  await browser.close();
  console.log('\n' + (hardFail === 0
    ? 'ALL CHECKS PASSED across ' + (WIDTHS.length + SHORT.length + 1) + ' cases'
    : hardFail + ' CASE(S) FAILED'));
  process.exit(hardFail === 0 ? 0 : 1);
})();
