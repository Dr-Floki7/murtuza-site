/* Width self-check demanded by "My site flow.pdf".
   Drives the installed Chrome (no bundled browser download available). */
const { chromium } = require('playwright');
const path = require('path');

const URL = 'http://127.0.0.1:8099/index.html';

const WIDTHS = [320, 360, 390, 414, 768, 834, 1024, 1280, 1440, 1920, 2560];
const LANDSCAPE = { w: 740, h: 360, name: 'landscape-phone' };

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

      // any element wider than the viewport
      const vw = window.innerWidth;
      document.querySelectorAll('body *').forEach((el) => {
        const b = el.getBoundingClientRect();
        if (b.width === 0 && b.height === 0) return;
        if (b.right > vw + 1.5 || b.left < -1.5) {
          const cs = getComputedStyle(el);
          if (cs.position === 'fixed') return; // skip link parks off-screen by design
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

    // does position:sticky survive overflow-x:clip on body?
    await page.evaluate(() => window.scrollTo(0, window.innerHeight * 2.5));
    await new Promise((res) => setTimeout(res, 260));
    const sticky = await page.evaluate(() => {
      const st = document.querySelector('.act__stage');
      if (!st) return { ok: false, why: 'no stage' };
      const b = st.getBoundingClientRect();
      return { ok: Math.abs(b.top) < 2, top: Math.round(b.top), h: Math.round(b.height) };
    });
    r.stickyWorks = sticky;

    // the video element must fill its viewport at this ratio
    r.videoCovers = await page.evaluate(() => {
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

    await page.evaluate(() => window.scrollTo(0, 0));
    r.skipReachable = skipReachable;

    const fails = [];
    if (r.docW > r.winW + 1) fails.push('H-SCROLL ' + r.docW + '>' + r.winW);
    if (r.overflow.length) fails.push('OVERFLOW ' + r.overflow.slice(0, 3).join('; '));
    if (r.tinyTap.length) fails.push('TAP<44 ' + r.tinyTap.slice(0, 3).join('; '));
    if (r.smallText.length) fails.push('TEXT<16 ' + r.smallText.slice(0, 2).join('; '));
    if (!r.stickyWorks.ok) fails.push('STICKY BROKEN top=' + r.stickyWorks.top);
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

  // short-and-wide case the spec calls out explicitly
  {
    const page = await browser.newPage({ viewport: { width: LANDSCAPE.w, height: LANDSCAPE.h } });
    await page.goto(URL, { waitUntil: 'load' });
    await page.waitForTimeout(450);
    await audit(page, LANDSCAPE.name, LANDSCAPE.w, LANDSCAPE.h);
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
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.93));
    await page.waitForTimeout(500);
    await page.screenshot({ path: `_shot_${w}_end.png` });
    await page.close();
  }

  await browser.close();
  console.log('\n' + (hardFail === 0
    ? 'ALL CHECKS PASSED across ' + (WIDTHS.length + 2) + ' cases'
    : hardFail + ' CASE(S) FAILED'));
  process.exit(hardFail === 0 ? 0 : 1);
})();
