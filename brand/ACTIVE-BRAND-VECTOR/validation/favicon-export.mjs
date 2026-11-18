import fs from 'node:fs';
import { chromium } from '/tmp/opencode/pw/node_modules/playwright-core/index.mjs';
const ROOT = '/oc/zb-active-watch/brand/ACTIVE-BRAND-VECTOR';
const A = '/oc/zb-active-watch/brand/assets';
const svg = fs.readFileSync(`${ROOT}/favicon/favicon.svg`, 'utf8');
const data = `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`;
const browser = await chromium.launch({ executablePath: '/snap/bin/chromium', args: ['--no-sandbox'] });
const page = await browser.newPage();
for (const [s, name] of [[16,'favicon-16.png'],[32,'favicon-32.png'],[64,'favicon-64.png'],[180,'apple-touch-icon.png'],[192,'icon-192.png'],[512,'icon-512.png']]) {
  await page.setContent(`<html><body style="margin:0"><img src="${data}" width="${s}" height="${s}"/></body></html>`, { waitUntil: 'load' });
  await page.setViewportSize({ width: s, height: s });
  await page.screenshot({ path: `${A}/${name}`, omitBackground: true });
  console.log(name, s);
}
await browser.close();
