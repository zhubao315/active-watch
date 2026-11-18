/**
 * ACTIVE brand raster build (v3.0 — PRECISION MOTION).
 *
 * Inputs are the canonical SVGs in brand/assets. Favicons are generated from
 * the single shared favicon.svg so all four sites serve byte-identical files
 * (the daily patrol asserts this). Social cards use each site's own accent.
 *
 *   CHROME_PATH=/path/to/chromium node brand/build-assets.mjs
 *
 * Env: ACTIVE_BRAND_DIR, ACTIVE_ART_DIR, ACTIVE_ASSET_OUT, CHROME_PATH.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.dirname(HERE);
const BRAND = path.resolve(process.env.ACTIVE_BRAND_DIR || HERE);
const ART = path.resolve(process.env.ACTIVE_ART_DIR || path.join(REPO, 'brand', 'art'));
const OUT = path.resolve(process.env.ACTIVE_ASSET_OUT || path.join(BRAND, 'generated'));

const SITES = [
  { key: 'running', zh: '跑步', en: 'RUNNING', title: 'zhubao315 的跑步生涯', tagline: '用脚步丈量城市，也用数据记住每一次出发。', accent: '#D9F36A' },
  { key: 'cycling', zh: '骑行', en: 'CYCLING', title: 'zhubao315 的骑行生涯', tagline: '两轮丈量城市与郊野，每一次踩踏都算数。', accent: '#FBBF24' },
  { key: 'hiking', zh: '徒步', en: 'HIKING', title: 'zhubao315 的徒步与山野', tagline: '去山里，把呼吸和海拔一起记录下来。', accent: '#34D399' },
  { key: 'health', zh: '健康', en: 'HEALTH', title: 'zhubao315 的健康数据', tagline: '睡眠、HRV、静息心率、压力与训练负荷，全部对比个人 7 天均值与 28 天基线。', accent: '#38BDF8' },
];

fs.mkdirSync(OUT, { recursive: true });
fs.mkdirSync(path.join(OUT, 'per-site'), { recursive: true });

const markSvg = fs.readFileSync(path.join(BRAND, 'assets/active-mark.svg'), 'utf8');
const faviconSvg = fs.readFileSync(path.join(BRAND, 'assets/favicon.svg'), 'utf8');
const lockupSvg = fs.readFileSync(path.join(BRAND, 'assets/active-logo.svg'), 'utf8');

const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
  args: ['--no-sandbox'],
});

const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });

async function rasterise(svg, px) {
  const sized = svg
    .replace(/<svg([^>]*)>/, (_, attrs) =>
      `<svg${attrs.replace(/\s?(width|height)="[^"]*"/g, '')} width="${px}" height="${px}">`
    );
  await page.setContent(
    `<!doctype html><html><body style="margin:0">${sized}</body></html>`,
    { waitUntil: 'load' }
  );
  await page.setViewportSize({ width: px, height: px });
  return page.screenshot({ omitBackground: true });
}

// ------------------------------------------------------- shared favicons ---
// One file set for all four sites: the master A on Midnight Canvas.
const faviconNames = {
  32: 'favicon-32.png',
  64: 'favicon-64.png',
  180: 'apple-touch-icon.png',
  192: 'icon-192.png',
  512: 'icon-512.png',
};
for (const px of [32, 64, 180, 192, 512]) {
  const buf = await rasterise(faviconSvg, px);
  fs.writeFileSync(path.join(BRAND, 'assets', faviconNames[px]), buf);
  fs.writeFileSync(path.join(OUT, faviconNames[px]), buf);
  console.log('favicon', px);
}

// ------------------------------------------------------------- social cards --
for (const site of SITES) {
  const artPath = path.join(BRAND, 'generated', `hero-${site.key}.webp`);
  const art = fs.existsSync(artPath)
    ? fs.readFileSync(artPath).toString('base64')
    : '';
  const lock = lockupSvg.replaceAll('currentColor', '#f7faff');
  await page.setContent(
    `<!doctype html><html><head><meta charset="utf-8"><style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { width: 1200px; height: 630px; background: #07111F; color: #f7faff;
        font-family: 'Inter', 'Noto Sans CJK SC', system-ui, sans-serif; position: relative; overflow: hidden; }
      .art { position: absolute; inset: 0; background: url(data:image/webp;base64,${art}) center/cover no-repeat; opacity: .5; }
      .veil { position: absolute; inset: 0; background: linear-gradient(100deg, rgba(7,17,31,.94) 30%, rgba(7,17,31,.45) 100%); }
      .content { position: relative; padding: 64px 72px; display: flex; flex-direction: column; justify-content: space-between; height: 100%; }
      .top { display: flex; align-items: center; gap: 18px; }
      .en { margin-left: auto; font: 500 15px/1 ui-monospace, Menlo, monospace; letter-spacing: .3em; color: ${site.accent}; }
      .mid h1 { font-size: 64px; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; }
      .mid .zh { margin-top: 14px; font-size: 30px; font-weight: 600; color: #cbd5e1; }
      .mid p { margin-top: 18px; font-size: 22px; color: #94a3b8; max-width: 760px; }
      .foot { display: flex; align-items: center; gap: 14px; font: 500 16px/1 ui-monospace, Menlo, monospace; letter-spacing: .1em; color: #94a3b8; }
      .dot { width: 8px; height: 8px; border-radius: 50%; background: ${site.accent}; }
    </style></head><body>
      <div class="art"></div><div class="veil"></div>
      <div class="content">
        <div class="top">${lock}<span class="en">${site.en}</span></div>
        <div class="mid">
          <h1>${site.title}</h1>
          <div class="zh">ACTIVE / ${site.en} · ${site.zh}</div>
          <p>${site.tagline}</p>
        </div>
        <div class="foot"><span class="dot"></span> ZHUBAO315.GITHUB.IO/${site.key.toUpperCase()} · 用数据记录每一次前进。</div>
      </div>
    </body></html>`,
    { waitUntil: 'load' }
  );
  await page.setViewportSize({ width: 1200, height: 630 });
  fs.writeFileSync(path.join(OUT, `og-${site.key}.png`), await page.screenshot());
  console.log('social card', site.key);
}

// -------------------------------------------------------------- brand poster --
const heroArt = fs.existsSync(path.join(ART, 'brand-hero.png'))
  ? fs.readFileSync(path.join(ART, 'brand-hero.png')).toString('base64')
  : '';
await page.setContent(
  `<!doctype html><html><head><meta charset="utf-8"><style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { width: 1200px; height: 630px; background: #07111F; color: #f7faff;
      font-family: 'Inter', system-ui, sans-serif; position: relative; overflow: hidden; }
    .art { position: absolute; inset: 0; background: url(data:image/png;base64,${heroArt}) center/cover no-repeat; opacity: .85; }
    .veil { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(7,17,31,.55), rgba(7,17,31,.25) 40%, rgba(7,17,31,.8)); }
    .content { position: relative; height: 100%; padding: 66px 72px; display: flex; flex-direction: column; justify-content: space-between; }
    .top { display: flex; align-items: center; gap: 16px; }
    .sub { margin-left: auto; font: 500 12px/1 ui-monospace, Menlo, monospace; letter-spacing: .16em; white-space: nowrap; color: #94a3b8; }
    .mid h1 { font-size: 58px; font-weight: 800; letter-spacing: -.02em; line-height: 1.15; max-width: 900px; }
    .mid p { margin-top: 16px; font-size: 24px; color: #cbd5e1; }
    .foot { display: flex; gap: 26px; font: 600 19px/1 system-ui; color: #f7faff; }
    .foot span { display: inline-flex; align-items: center; gap: 9px; }
  </style></head><body>
    <div class="art"></div><div class="veil"></div>
    <div class="content">
      <div class="top">${lockupSvg}<span class="sub">MOVE · MEASURE · EXPLORE</span></div>
      <div class="mid"><h1>用数据记录每一次前进。</h1><p>朱宝 · 运动与健康数字档案 — RUN · RIDE · HIKE · HEALTH</p></div>
      <div class="foot">
        <span><b style="color:#38bdf8">HEALTH</b> 身体与恢复</span>
        <span><b style="color:#d9f36a">RUNNING</b> 跑步与耐力</span>
        <span><b style="color:#fbbf24">CYCLING</b> 骑行与远行</span>
        <span><b style="color:#34d399">HIKING</b> 徒步与山野</span>
      </div>
    </div>
  </body></html>`,
  { waitUntil: 'load' }
);
await page.setViewportSize({ width: 1200, height: 630 });
fs.writeFileSync(path.join(OUT, 'og-brand.png'), await page.screenshot());
console.log('brand poster written');

await browser.close();
