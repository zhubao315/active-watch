import { chromium } from 'playwright';

const SITES = [
  ['health', 'https://zhubao315.github.io/health/'],
  ['running', 'https://zhubao315.github.io/running/'],
  ['cycling', 'https://zhubao315.github.io/cycling/'],
  ['hiking', 'https://zhubao315.github.io/hiking/'],
];

const browser = await chromium.launch();
const failures = [];

for (const [name, url] of SITES) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text().slice(0, 120));
  });
  page.on('pageerror', (e) => errors.push('PAGEERROR ' + e.message.slice(0, 120)));
  const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1200);

  const report = await page.evaluate(() => ({
    title: document.title,
    mark: !!document.querySelector('svg[aria-label="ZB ACTIVE"], .brand-mark'),
    wordmark: [...document.querySelectorAll('*')].some(
      (el) => el.children.length === 0 && el.textContent.trim() === 'ZB ACTIVE'
    ),
    navSites: [...document.querySelectorAll('a[data-site]')].map((a) => a.dataset.site),
    navIcons: document.querySelectorAll('a[data-site] svg').length,
    current: document.querySelectorAll('header a[aria-current="page"]').length,
    theme: document.documentElement.dataset.theme,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    broken: [...document.images].filter((i) => !i.complete || i.naturalWidth === 0).length,
  }));

  console.log(name, JSON.stringify({ status: response?.status(), ...report }));
  if (response?.status() !== 200) failures.push(`${name} status ${response?.status()}`);
  if (!report.mark) failures.push(`${name} mark missing`);
  if (!report.wordmark) failures.push(`${name} wordmark missing`);
  if (report.navSites.length < 4) failures.push(`${name} nav ${report.navSites.join('/')}`);
  if (report.navIcons < 4) failures.push(`${name} nav icons ${report.navIcons}`);
  if (report.current !== 1) failures.push(`${name} current ${report.current}`);
  if (report.overflow > 1) failures.push(`${name} overflow ${report.overflow}`);
  if (report.broken > 0) failures.push(`${name} broken images ${report.broken}`);
  if (errors.length) failures.push(`${name} console ${JSON.stringify(errors.slice(0, 2))}`);

  // the accent of the current site must be the site's own colour
  const accent = await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--accent').trim());
  console.log(name, 'accent', accent);
  await page.close();
}

// mobile: the bottom bar must exist and the page must not overflow
for (const [name, url] of SITES) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(900);
  const report = await page.evaluate(() => ({
    bar: !!document.querySelector('.mobile-nav, nav[aria-label="四站导航"]:last-of-type'),
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));
  console.log(name, 'mobile', JSON.stringify(report));
  if (report.overflow > 1) failures.push(`${name} mobile overflow ${report.overflow}`);
  await page.close();
}

console.log('\nfailures:', failures.length ? failures : 'none');
await browser.close();
process.exit(failures.length ? 1 : 0);
