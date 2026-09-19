/* Mobile-specific performance and behavior check for the scroll-scrub film.

   Uses a 4x CPU throttle, touch input and a phone viewport. This cannot emulate
   iOS's media decoder, but it catches the regressions under our control:
   - wrong/heavy asset selected
   - 700vh sticky travel returning
   - banner continuing to decode behind the film
   - film lagging far behind scroll progress
   - a second seek loop continuing after the scroll settles
*/
const { chromium } = require('playwright');

const URL = process.argv[2] || 'http://127.0.0.1:8099/index.html';

(async () => {
  const browser = await chromium.launch({
    channel: 'chrome',
    args: ['--autoplay-policy=no-user-gesture-required'],
  });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 2,
    reducedMotion: 'no-preference',
  });
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);
  await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });

  await page.goto(URL, { waitUntil: 'load' });
  await page.waitForTimeout(700);

  // Real touch gesture: this is what unlocks seeking on mobile engines.
  await page.touchscreen.tap(195, 420);

  const act = await page.evaluate(() => {
    const a = document.getElementById('act');
    const top = a.getBoundingClientRect().top + window.scrollY;
    return {
      top,
      height: a.offsetHeight,
      viewport: window.innerHeight,
      travel: a.offsetHeight - window.innerHeight,
      cssVh: a.offsetHeight / window.innerHeight,
    };
  });

  // Enter the act to trigger lazy loading, then wait for metadata and a seekable range.
  await page.evaluate((top) => window.scrollTo({ top, behavior: 'instant' }), act.top + 10);
  await page.waitForFunction(() => {
    const f = document.getElementById('film');
    return isFinite(f.duration) && f.duration > 0 && f.seekable.length > 0;
  }, null, { timeout: 15_000 });

  const initial = await page.evaluate(() => {
    const film = document.getElementById('film');
    const banner = document.getElementById('banner-film');
    return {
      src: film.getAttribute('src'),
      width: film.videoWidth,
      height: film.videoHeight,
      duration: film.duration,
      bannerPaused: banner.paused,
    };
  });

  console.log('mobile asset:', initial);
  console.log(`act: ${act.cssVh.toFixed(2)} viewport-heights, ${Math.round(act.travel)}px travel`);

  const fails = [];
  if (initial.src !== 'scrub-mobile.mp4') fails.push(`heavy/wrong asset selected: ${initial.src}`);
  if (initial.width > 540 || initial.height > 960) {
    fails.push(`mobile raster too large: ${initial.width}x${initial.height}`);
  }
  if (act.cssVh > 4.35) fails.push(`sticky act too long: ${act.cssVh.toFixed(2)}vh units`);
  if (!initial.bannerPaused) fails.push('banner video still playing behind the scrub film');

  // Seek to several scroll positions. Under 4x CPU, the visible frame should still
  // land within 0.45s of the requested time after 180ms.
  const samples = [];
  for (const progress of [0.08, 0.16, 0.27, 0.44, 0.61, 0.78, 0.91]) {
    const top = act.top + act.travel * progress;
    const started = Date.now();
    await page.evaluate((y) => window.scrollTo({ top: y, behavior: 'instant' }), top);
    await page.waitForTimeout(180);
    const state = await page.evaluate((p) => {
      const f = document.getElementById('film');
      return {
        current: f.currentTime,
        target: p * f.duration,
        seeking: f.seeking,
      };
    }, progress);
    state.progress = progress;
    state.wallMs = Date.now() - started;
    state.lag = Math.abs(state.target - state.current);
    samples.push(state);
  }

  console.log('\nprogress  target   frame    lag   seeking');
  for (const s of samples) {
    console.log(`${s.progress.toFixed(2).padEnd(9)} ${s.target.toFixed(2).padStart(6)}s  ` +
      `${s.current.toFixed(2).padStart(6)}s  ${s.lag.toFixed(2).padStart(5)}s  ${s.seeking}`);
    if (s.lag > 0.45) fails.push(`p=${s.progress}: frame lags target by ${s.lag.toFixed(2)}s`);
  }

  // After scrolling stops there must not be a desktop-style lerp still moving the
  // film through stale intermediate frames.
  const before = await page.evaluate(() => document.getElementById('film').currentTime);
  await page.waitForTimeout(500);
  const after = await page.evaluate(() => document.getElementById('film').currentTime);
  const drift = Math.abs(after - before);
  console.log(`\npost-scroll drift over 500ms: ${drift.toFixed(3)}s`);
  if (drift > 0.08) fails.push(`film keeps drifting after scroll stopped: ${drift.toFixed(3)}s`);

  await context.close();
  await browser.close();

  console.log();
  if (fails.length) {
    console.log('FAILURES');
    fails.forEach((f) => console.log('  - ' + f));
    process.exit(1);
  }
  console.log('Mobile scrub uses the lightweight cut, short travel, one seek per frame, and no competing banner decoder.');
})();
