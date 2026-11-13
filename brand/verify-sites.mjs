import { chromium } from 'playwright';

const SITES = [
  { name: 'running', port: 4601 },
  { name: 'cycling', port: 4602 },
  { name: 'hiking', port: 4603 },
  { name: 'health', port: 4604 },
];

const WIDTHS = [1440, 1280, 768, 390, 360];
const browser = await chromium.launch();
const failures = [];

for (const site of SITES) {
  const url = `http://127.0.0.1:${site.port}/${site.name}/`;

  for (const width of WIDTHS) {
    const page = await browser.newPage({ viewport: { width, height: width > 500 ? 1000 : 844 } });
    const errors = [];
    page.on('console', (m) => {
      if (m.type() === 'error') errors.push(m.text().slice(0, 140));
    });
    page.on('pageerror', (e) => errors.push('PAGEERROR ' + e.message.slice(0, 140)));
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(900);
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth
    );
    const broken = await page.evaluate(
      () => [...document.images].filter((i) => !i.complete || i.naturalWidth === 0).length
    );
    const brand = await page.evaluate(() => ({
      mark: !!document.querySelector('.brand-mark, svg[aria-label="ZB ACTIVE"]'),
      navIcons: document.querySelectorAll('a[data-site] svg').length,
    }));
    if (overflow > 1) failures.push(`${site.name}@${width} overflow ${overflow}`);
    if (broken > 0) failures.push(`${site.name}@${width} broken images ${broken}`);
    if (errors.length) failures.push(`${site.name}@${width} console ${JSON.stringify(errors.slice(0, 2))}`);
    if (!brand.mark) failures.push(`${site.name}@${width} brand mark missing`);
    console.log(`${site.name} @${width}: overflow ${overflow}, broken ${broken}, mark ${brand.mark}, errors ${errors.length}`);
    await page.close();
  }

  // theme switch + persistence
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text().slice(0, 140));
  });
  page.on('pageerror', (e) => errors.push('PAGEERROR ' + e.message.slice(0, 140)));
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.click('#theme-toggle, .theme-toggle, button[aria-label*="主题"]');
  await page.waitForTimeout(400);
  const theme = await page.evaluate(() => ({
    attr: document.documentElement.dataset.theme,
    stored: localStorage.getItem('zhubao315-theme'),
  }));
  if (theme.attr !== 'light' || theme.stored !== 'light') {
    failures.push(`${site.name} theme switch ${JSON.stringify(theme)}`);
  }
  console.log(`${site.name} theme ->`, theme);

  // the four-site navigation points at the four sites
  const nav = await page.evaluate(() =>
    [...document.querySelectorAll('a[data-site]')].map((a) => a.getAttribute('href'))
  );
  const expected = ['health', 'running', 'cycling', 'hiking'];
  for (const key of expected) {
    if (!nav.some((href) => href && href.includes(`/${key}/`))) {
      failures.push(`${site.name} nav missing ${key}`);
    }
  }
  console.log(`${site.name} nav ->`, nav.join(' '));

  // a calendar day still opens (running / cycling / hiking)
  if (site.name !== 'health') {
    const cells = page.locator('[data-date], [class*="hcell"], [class*="heat"]');
    const count = await cells.count();
    if (count > 0) {
      await cells.nth(Math.min(5, count - 1)).click({ force: true });
      await page.waitForTimeout(600);
      const url2 = page.url();
      console.log(`${site.name} calendar cell -> ${url2}`);
      if (!url2.includes('date=') && !url2.includes('year=')) {
        failures.push(`${site.name} calendar cell did not change the url`);
      }
    } else {
      console.log(`${site.name} no calendar cell found`);
    }
  }
  if (errors.length) failures.push(`${site.name} interaction console ${JSON.stringify(errors.slice(0, 2))}`);
  await page.close();
}

console.log('\nfailures:', failures.length ? failures : 'none');
await browser.close();
process.exit(failures.length ? 1 : 0);
