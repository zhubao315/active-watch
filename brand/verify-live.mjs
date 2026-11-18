/**
 * Live brand / runtime verification for the four ACTIVE sites.
 *
 * Brand assertions live in `brand-contract.mjs` so they can be unit-tested
 * without a browser. The retired name "ZB ACTIVE" is explicitly a FAILURE,
 * never the expected wordmark.
 *
 *   node brand/verify-live.mjs
 */
import { chromium } from 'playwright';
import { collectBrandReport, checkBrandReport } from './brand-contract.mjs';

const PAGES = process.env.ACTIVE_PAGES || 'https://zhubao315.github.io';
const SITES = [
  ['health', `${PAGES}/health/`],
  ['running', `${PAGES}/running/`],
  ['cycling', `${PAGES}/cycling/`],
  ['hiking', `${PAGES}/hiking/`],
];

const browser = await chromium.launch();
const failures = [];

// GitHub Pages occasionally returns a transient 5xx for a subresource. A
// single such console line is not a brand regression — retry the page once
// before treating it as a real failure. JS exceptions are never retried away.
const isTransientResourceError = (msg) =>
  /Failed to load resource: the server responded with a status of (502|503|504)/.test(
    msg
  );

for (const [siteKey, url] of SITES) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text().slice(0, 120));
  });
  page.on('pageerror', (e) => errors.push('PAGEERROR ' + e.message.slice(0, 120)));
  const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1200);

  if (errors.length && errors.every(isTransientResourceError)) {
    console.log(siteKey, 'transient 5xx resource — retrying once');
    errors.length = 0;
    await page.reload({ waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(1200);
  }

  const report = await page.evaluate(collectBrandReport);
  console.log(siteKey, JSON.stringify({ status: response?.status(), ...report }));

  if (response?.status() !== 200) failures.push(`${siteKey}: status ${response?.status()}`);
  failures.push(...checkBrandReport(report, { siteKey }).map((f) => `${siteKey}: ${f}`));
  if (errors.length) failures.push(`${siteKey}: console ${JSON.stringify(errors.slice(0, 2))}`);

  // Each site's accent must be its own colour, not a copied one.
  const accent = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()
  );
  console.log(siteKey, 'accent', accent);
  await page.close();
}

// Mobile: the bottom bar must exist and the page must not overflow.
for (const [siteKey, url] of SITES) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(900);
  const report = await page.evaluate(() => ({
    bar: !!document.querySelector('nav[aria-label="四站导航"]'),
    overflow:
      document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));
  console.log(siteKey, 'mobile', JSON.stringify(report));
  if (!report.bar) failures.push(`${siteKey}: mobile bottom nav missing`);
  if (report.overflow > 1) failures.push(`${siteKey}: mobile overflow ${report.overflow}`);
  await page.close();
}

console.log('\nfailures:', failures.length ? failures : 'none');
await browser.close();
process.exit(failures.length ? 1 : 0);
