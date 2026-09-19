/* Mobile native-playback story check. */
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    channel: 'chrome',
    args: ['--autoplay-policy=no-user-gesture-required'],
  });
  const page = await browser.newPage({
    viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true,
  });
  await page.goto('http://127.0.0.1:8099/index.html', { waitUntil: 'load' });
  await page.waitForTimeout(500);

  const initial = await page.evaluate(() => ({
    act: getComputedStyle(document.getElementById('act')).display,
    story: getComputedStyle(document.getElementById('mobile-story')).display,
    scenes: document.querySelectorAll('.mobile-scene').length,
  }));
  console.log('mobile structure:', initial);

  const fails = [];
  if (initial.act !== 'none') fails.push('desktop scrub is still visible on mobile');
  if (initial.story !== 'block') fails.push('mobile story is not visible');
  if (initial.scenes !== 3) fails.push(`expected 3 scenes, got ${initial.scenes}`);

  const scenes = page.locator('.mobile-scene');
  for (let i = 0; i < 3; i++) {
    await scenes.nth(i).scrollIntoViewIfNeeded();
    await page.waitForTimeout(900);
    const state = await scenes.nth(i).evaluate((scene) => {
      const video = scene.querySelector('video');
      return {
        src: video.getAttribute('src'),
        duration: Number.isFinite(video.duration) ? video.duration : null,
        paused: video.paused,
        current: video.currentTime,
        ready: scene.classList.contains('is-ready'),
        height: Math.round(scene.getBoundingClientRect().height),
      };
    });
    console.log(`scene ${i + 1}:`, state);
    if (!state.src) fails.push(`scene ${i + 1} did not lazy-load`);
    if (!state.duration) fails.push(`scene ${i + 1} has no duration`);
    if (state.paused) fails.push(`scene ${i + 1} is paused while visible`);
    if (state.current <= 0) fails.push(`scene ${i + 1} did not advance`);
    if (state.height < 700) fails.push(`scene ${i + 1} is too short`);
  }

  // Desktop still owns the scrub path.
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await desktop.goto('http://127.0.0.1:8099/index.html', { waitUntil: 'load' });
  const desktopState = await desktop.evaluate(() => ({
    act: getComputedStyle(document.getElementById('act')).display,
    story: getComputedStyle(document.getElementById('mobile-story')).display,
  }));
  console.log('desktop structure:', desktopState);
  if (desktopState.act !== 'block') fails.push('desktop scrub is hidden');
  if (desktopState.story !== 'none') fails.push('mobile story visible on desktop');

  await browser.close();
  if (fails.length) {
    console.log('FAILURES');
    fails.forEach((f) => console.log(' - ' + f));
    process.exit(1);
  }
  console.log('Mobile native story and desktop scrub paths pass.');
})();
