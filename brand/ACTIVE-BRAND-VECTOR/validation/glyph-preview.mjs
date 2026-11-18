import fs from 'node:fs';
import { chromium } from '/tmp/opencode/pw/node_modules/playwright-core/index.mjs';
const V = '/oc/zb-active-watch/brand/ACTIVE-BRAND-VECTOR';
const data = (s) => `data:image/svg+xml;base64,${Buffer.from(s).toString('base64')}`;
const keys = ['health','running','cycling','hiking'];
const b = await chromium.launch({ executablePath: '/snap/bin/chromium', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 760, height: 420 }, deviceScaleFactor: 2 });
let html = `<html><body style="margin:0;background:#07111F;color:#94A3B8;font-family:sans-serif;padding:22px">
<h2 style="color:#F7FAFF;font-size:16px">ZB ACTIVE · Navigation Icons 1.0 — Neo Sport Glyph</h2>
<div style="display:flex;gap:26px;margin-top:18px">`;
for (const k of keys) {
  const s = fs.readFileSync(`${V}/sub-brands/${k}.svg`,'utf8');
  html += `<div style="text-align:center">
    <img src="${data(s)}" width="96" height="96"/>
    <div style="font-size:11px;color:#CBD5E1;margin-top:4px">${k}</div>
    <div style="margin-top:6px;display:flex;gap:8px;align-items:center;justify-content:center">
      <img src="${data(s)}" width="24" height="24"/>
      <img src="${data(s)}" width="20" height="20"/>
      <img src="${data(s)}" width="16" height="16"/>
    </div></div>`;
}
html += `</div></body></html>`;
await p.setContent(html, { waitUntil:'load' });
await p.screenshot({ path: `${V}/validation/nav-icons-v1.png`, fullPage:true });
console.log('saved nav-icons-v1.png');
await b.close();
