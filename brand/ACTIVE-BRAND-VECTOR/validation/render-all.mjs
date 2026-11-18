import fs from 'node:fs';
import path from 'node:path';
import { chromium } from '/tmp/opencode/pw/node_modules/playwright-core/index.mjs';

const ROOT = '/oc/zb-active-watch/brand/ACTIVE-BRAND-VECTOR';
const OUT = path.join(ROOT, 'validation');
const read = (p) => fs.readFileSync(path.join(ROOT, p)).toString('utf8');
const data = (s) => `data:image/svg+xml;base64,${Buffer.from(s).toString('base64')}`;

const browser = await chromium.launch({ executablePath: '/snap/bin/chromium', args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
const svg = read('master/active-symbol.svg');

// full validation sheet: backgrounds + all assets + sizes
const cell = (svgData, w, h, bg, label) => {
  const checker = bg === 'checker'
    ? 'background:repeating-conic-gradient(#ccc 0% 25%,#fff 0% 50%) 50% / 16px 16px;'
    : `background:${bg};`;
  return `<div style="display:flex;flex-direction:column;align-items:center;gap:6px;padding:12px;border:1px solid #444;${checker}">
    <img src="${svgData}" width="${w}" height="${h}"/><span style="font:11px monospace;color:#888">${label}</span></div>`;
};

let html = `<html><body style="margin:0;background:#181818;color:#fff;font-family:sans-serif;padding:18px">`;
html += `<h2>Backgrounds (ACTIVE symbol)</h2><div style="display:flex;gap:12px">`;
for (const [bg, lab] of [['#000000','black'],['#07111F','navy'],['#FFFFFF','white'],['checker','transparent']])
  html += cell(data(svg), 200, 135, bg, lab);
html += `</div><h2>Sub-brand icons (24px)</h2><div style="display:flex;gap:12px;background:#07111F;padding:12px">`;
for (const k of ['health','running','cycling','hiking'])
  html += cell(data(read(`sub-brands/${k}.svg`)), 48, 48, '#07111F', k);
html += `</div><h2>WATCH + lockups</h2><div style="display:flex;gap:12px;background:#07111F;padding:12px">`;
html += cell(data(read('watch/active-watch-symbol.svg')), 64, 64, '#07111F','watch');
html += cell(data(read('master/active-logo-horizontal.svg')), 300, 86, '#07111F','horizontal');
html += cell(data(read('master/active-logo-vertical.svg')), 120, 100, '#07111F','vertical');
html += cell(data(read('favicon/favicon.svg')), 64, 64, '#07111F','favicon');
html += `</div><h2>Sizes (navy)</h2><div style="display:flex;gap:8px;align-items:flex-end;background:#07111F;padding:12px">`;
for (const s of [16,24,32,48,64,128,256,512,1024]) html += cell(data(svg), Math.min(s,200), Math.round(Math.min(s,200)*116/172), '#07111F', `${s}px`);
html += `</div></body></html>`;
await page.setContent(html, { waitUntil: 'load' });
await page.screenshot({ path: path.join(OUT, 'all-assets.png'), fullPage: true });

// PNG exports from vector (rasterised at exact sizes)
const exportPng = async (svgData, w, h, file) => {
  await page.setContent(`<html><body style="margin:0"><img src="${svgData}" width="${w}" height="${h}"/></body></html>`, { waitUntil: 'load' });
  await page.setViewportSize({ width: w, height: h });
  await page.screenshot({ path: path.join(ROOT, file), omitBackground: true });
};
await exportPng(data(read('master/active-logo-horizontal.svg')), 1024, 294, 'png/active-logo-transparent-1024.png');
await exportPng(data(read('master/active-logo-horizontal.svg')), 2048, 589, 'png/active-logo-transparent-2048.png');
await exportPng(data(read('master/active-logo-horizontal.svg')), 4096, 1178, 'png/active-logo-transparent-4096.png');
await exportPng(data(read('master/active-logo-white.svg')), 1024, 294, 'png/active-logo-dark-1024.png');
await exportPng(data(read('master/active-logo-horizontal.svg')), 1024, 294, 'png/active-logo-light-1024.png');

// favicon PNGs
for (const [s, f] of [[16,'favicon-16.png'],[32,'favicon-32.png'],[64,'favicon-64.png'],[180,'apple-touch-icon.png']])
  await exportPng(data(read('favicon/favicon.svg')), s, s, `favicon/${f}`);

console.log('rendered all assets + PNG exports');
await browser.close();
