import fs from 'node:fs';
import { chromium } from '/tmp/opencode/pw/node_modules/playwright-core/index.mjs';
const V = '/oc/zb-active-watch/brand/ACTIVE-BRAND-VECTOR';
const data = (s) => `data:image/svg+xml;base64,${Buffer.from(s).toString('base64')}`;
const keys = ['health','running','cycling','hiking'];
const browser = await chromium.launch({ executablePath: '/snap/bin/chromium', args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 900, height: 520 } });
let html = `<html><body style="margin:0;background:#07111F;color:#94A3B8;font-family:sans-serif;padding:24px">
<h2 style="color:#F7FAFF">ACTIVE sub-brand icons — standard linear, 24×24 / 2px</h2>
<div style="display:flex;gap:24px;align-items:flex-end">`;
for (const k of keys) {
  const s = fs.readFileSync(`${V}/sub-brands/${k}.svg`,'utf8');
  html += `<div style="text-align:center"><img src="${data(s)}" width="96" height="96"/>
  <img src="${data(s)}" width="24" height="24" style="vertical-align:middle;margin-left:8px"/>
  <img src="${data(s)}" width="16" height="16" style="vertical-align:middle;margin-left:8px"/>
  <div style="margin-top:8px;color:#CBD5E1">${k}</div></div>`;
}
html += `</div></body></html>`;
await page.setContent(html, { waitUntil: 'load' });
await page.screenshot({ path: `${V}/validation/subbrand-icons.png`, fullPage: true });
console.log('saved subbrand-icons.png');
await browser.close();
