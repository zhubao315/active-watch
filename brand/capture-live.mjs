import { chromium } from 'playwright';

const SITES = [
  ['health', 'https://zhubao315.github.io/health/'],
  ['running', 'https://zhubao315.github.io/running/'],
  ['cycling', 'https://zhubao315.github.io/cycling/'],
  ['hiking', 'https://zhubao315.github.io/hiking/'],
];
const OUT = '/oc/active/brand/generated/shots';
const browser = await chromium.launch();

for (const [name, url] of SITES) {
  for (const [width, height, suffix] of [
    [1440, 1000, 'desktop'],
    [390, 844, 'mobile'],
  ]) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    await page.evaluate(async () => {
      await document.fonts.ready;
      document.querySelectorAll('img').forEach((img) => { img.loading = 'eager'; });
    }).catch(() => {});
    await page.waitForTimeout(1400);
    await page.screenshot({ path: `${OUT}/${name}-${suffix}.png` });
    console.log(name, suffix);
    await page.close();
  }
}
await browser.close();
