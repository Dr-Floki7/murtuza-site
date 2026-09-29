/* Essential copy must never be hidden by decorative motion. */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const fails = [];
  for (const spec of [{ name: 'mobile', width: 375, height: 812, mobile: true }, { name: 'desktop', width: 1440, height: 900, mobile: false }]) {
    const page = await browser.newPage({ viewport: { width: spec.width, height: spec.height }, isMobile: spec.mobile, hasTouch: spec.mobile });
    await page.goto('http://127.0.0.1:8099/index.html', { waitUntil: 'load' });
    const initial = await page.evaluate(() => {
      const p = document.querySelector('[data-track="intro"] [data-words]');
      const h = document.querySelector('[data-track="intro"] .reveal-lines');
      return {
        paragraphOpacity: parseFloat(getComputedStyle(p).opacity),
        headingOpacity: parseFloat(getComputedStyle(h).opacity),
        wordSpans: document.querySelectorAll('.w').length,
        marquee: !!document.querySelector('.ticker'),
      };
    });
    if (initial.paragraphOpacity < 0.6) fails.push(`${spec.name}: paragraph starts unreadable at ${initial.paragraphOpacity}`);
    if (initial.headingOpacity < 0.5) fails.push(`${spec.name}: heading starts unreadable at ${initial.headingOpacity}`);
    if (initial.wordSpans) fails.push(`${spec.name}: ${initial.wordSpans} delayed word spans remain`);
    if (initial.marquee) fails.push(`${spec.name}: decorative marquee remains`);

    await page.locator('[data-track="intro"]').evaluate((el) => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
    await page.waitForTimeout(550);
    const settled = await page.evaluate(() => ({
      paragraph: parseFloat(getComputedStyle(document.querySelector('[data-track="intro"] [data-words]')).opacity),
      heading: parseFloat(getComputedStyle(document.querySelector('[data-track="intro"] .reveal-lines')).opacity),
    }));
    if (settled.paragraph < 0.99 || settled.heading < 0.99) fails.push(`${spec.name}: reveal did not settle within 550ms`);
    await page.screenshot({
      path: path.join('.gstack', 'design-reports', 'design-audit-murtuza-bharmal-2026-09-16', 'screenshots', `finding-004-after-${spec.name}.jpg`),
      type: 'jpeg', quality: 70,
    });
    console.log(spec.name, { initial, settled });
    await page.close();
  }
  await browser.close();
  if (fails.length) { console.log('FAILURES'); fails.forEach((f) => console.log(' - ' + f)); process.exit(1); }
  console.log('Essential copy stays readable, settles within 550ms, and marquee is removed.');
})();
