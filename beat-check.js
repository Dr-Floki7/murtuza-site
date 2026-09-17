/* Do the six captions land on the footage they describe?
   Real cut: real estate 0-8s, electronics 8-16s, clinical 16-22.04s. */
const { chromium } = require('playwright');

const EXPECT = [
  { band: [0.07, 0.18],   stage: 'real estate', head: 'Now I price buildings.' },
  { band: [0.21, 0.33],   stage: 'real estate', head: 'The launch is one day.' },
  { band: [0.40, 0.52],   stage: 'electronics', head: 'Before this, I moved phones.' },
  { band: [0.55, 0.67],   stage: 'electronics', head: 'You learn to fix it live.' },
  { band: [0.74, 0.845],  stage: 'clinical',    head: 'I started holding a drill.' },
  { band: [0.865, 0.945], stage: 'clinical',    head: 'That is where I learned demand.' },
];

const stageAt = (t) => (t < 8 ? 'real estate' : t < 16 ? 'electronics' : 'clinical');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://127.0.0.1:8099/index.html', { waitUntil: 'load' });
  await page.waitForTimeout(600);

  // banner must fall back to its poster while banner.mp4 does not exist
  const banner = await page.evaluate(() => {
    const v = document.getElementById('banner-film');
    return { src: v.getAttribute('src'), poster: v.getAttribute('poster'), err: v.error ? v.error.code : null };
  });
  console.log(`banner: src=${banner.src} poster=${banner.poster} error=${banner.err} ` +
    `(error expected until the clip is generated; poster carries it)`);

  const act = await page.evaluate(() => {
    const a = document.getElementById('act');
    return { top: a.getBoundingClientRect().top + window.scrollY, h: a.offsetHeight };
  });

  const fails = [];
  console.log('\nbeat            progress   video-t   stage-on-screen   caption');
  for (const e of EXPECT) {
    const mid = (e.band[0] + e.band[1]) / 2;
    await page.evaluate(([t, h, f]) =>
      window.scrollTo({ top: t + (h - window.innerHeight) * f, behavior: 'instant' }),
      [act.top, act.h, mid]);
    await page.waitForTimeout(650);

    const s = await page.evaluate(() => {
      const f = document.getElementById('film');
      const on = [...document.querySelectorAll('.panel[data-on]')];
      return {
        t: +f.currentTime.toFixed(2),
        n: on.length,
        head: on.length ? on[0].querySelector('h2').textContent.trim() : null,
        label: on.length ? on[0].querySelector('.panel__year').textContent.trim() : null,
      };
    });

    const shown = stageAt(s.t);
    const okStage = shown === e.stage;
    const okHead = s.head === e.head;
    const okOne = s.n === 1;
    console.log(`  ${(okStage && okHead && okOne) ? 'ok  ' : 'FAIL'} ` +
      `p=${mid.toFixed(3)}  t=${String(s.t).padStart(5)}s  ${shown.padEnd(16)} ${s.head}`);
    if (!okOne) fails.push(`${e.head}: ${s.n} panels visible`);
    if (!okHead) fails.push(`expected "${e.head}", got "${s.head}"`);
    if (!okStage) fails.push(`"${e.head}" shows over ${shown} footage, should be ${e.stage}`);
  }

  // no two captions should describe the same thing
  const heads = EXPECT.map(e => e.head);
  if (new Set(heads).size !== heads.length) fails.push('duplicate captions');

  await browser.close();
  console.log();
  if (fails.length) { console.log('FAILURES'); fails.forEach(f => console.log('  - ' + f)); process.exit(1); }
  console.log('All six beats land on the footage they describe, one at a time.');
})();
