/**
 * ACTIVE brand social-card build.
 *
 * All brand raster assets (mark, icons, favicons, lockups) are PNG slices of
 * the supplied identity board and are produced by `brand/slice-board.py`.
 * This script only composes the 1200x630 social cards from those slices —
 * it never redraws or regenerates the logo itself.
 *
 *   CHROME_PATH=/path/to/chromium node brand/build-assets.mjs
 * Env: ACTIVE_BRAND_DIR, ACTIVE_ASSET_OUT, CHROME_PATH.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.dirname(HERE);
const BRAND = path.resolve(process.env.ACTIVE_BRAND_DIR || HERE);
const OUT = path.resolve(process.env.ACTIVE_ASSET_OUT || path.join(BRAND, 'generated'));
const ASSETS = path.join(BRAND, 'assets');

const SITES = [
  { key: 'running', zh: '跑步', en: 'RUNNING', title: 'zhubao315 的跑步生涯', tagline: '用脚步丈量城市，也用数据记住每一次出发。', accent: '#D9F36A' },
  { key: 'cycling', zh: '骑行', en: 'CYCLING', title: 'zhubao315 的骑行生涯', tagline: '两轮丈量城市与郊野，每一次踩踏都算数。', accent: '#FBBF24' },
  { key: 'hiking', zh: '徒步', en: 'HIKING', title: 'zhubao315 的徒步与山野', tagline: '去山里，把呼吸和海拔一起记录下来。', accent: '#34D399' },
  { key: 'health', zh: '健康', en: 'HEALTH', title: 'zhubao315 的健康数据', tagline: '睡眠、HRV、静息心率、压力与训练负荷，全部对比个人 7 天均值与 28 天基线。', accent: '#38BDF8' },
];

fs.mkdirSync(OUT, { recursive: true });
const b64 = (name) => fs.readFileSync(path.join(ASSETS, name)).toString('base64');
const lockup = `data:image/png;base64,${b64('lockup-dark.png')}`;
const mark = `data:image/png;base64,${b64('active-mark.png')}`;

const browser = await chromium.launch({
  headless: true,
  ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
  args: ['--no-sandbox'],
});
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });

for (const site of SITES) {
  const artPath = path.join(OUT, `hero-${site.key}.webp`);
  const art = fs.existsSync(artPath) ? fs.readFileSync(artPath).toString('base64') : '';
  await page.setContent(
    `<!doctype html><html><head><meta charset="utf-8"><style>
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { width: 1200px; height: 630px; background: #07111F; color: #f7faff;
        font-family: 'Inter', 'Noto Sans CJK SC', system-ui, sans-serif; position: relative; overflow: hidden; }
      .art { position: absolute; inset: 0; background: url(data:image/webp;base64,${art}) center/cover no-repeat; opacity: .5; }
      .veil { position: absolute; inset: 0; background: linear-gradient(100deg, rgba(7,17,31,.94) 30%, rgba(7,17,31,.45) 100%); }
      .content { position: relative; padding: 64px 72px; display: flex; flex-direction: column; justify-content: space-between; height: 100%; }
      .top img { height: 60px; width: auto; display: block; }
      .en { margin-left: auto; font: 500 15px/1 ui-monospace, monospace; letter-spacing: .3em; color: ${site.accent}; }
      .mid h1 { font-size: 64px; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; }
      .mid .zh { margin-top: 14px; font-size: 30px; font-weight: 600; color: #cbd5e1; }
      .mid p { margin-top: 18px; font-size: 22px; color: #94a3b8; max-width: 760px; }
      .foot { display: flex; align-items: center; gap: 14px; font: 500 16px/1 ui-monospace, monospace; letter-spacing: .1em; color: #94a3b8; }
      .dot { width: 8px; height: 8px; border-radius: 50%; background: ${site.accent}; }
    </style></head><body>
      <div class="art"></div><div class="veil"></div>
      <div class="content">
        <div class="top"><img src="${lockup}" alt="ACTIVE" /><span class="en">${site.en}</span></div>
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

// brand poster
await page.setContent(
  `<!doctype html><html><head><meta charset="utf-8"><style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { width: 1200px; height: 630px; background: #07111F; color: #f7faff; font-family: 'Inter', system-ui, sans-serif; }
    .content { height: 100%; padding: 66px 72px; display: flex; flex-direction: column; justify-content: space-between; }
    .top img { height: 60px; }
    .sub { margin-left: auto; font: 500 12px/1 ui-monospace, monospace; letter-spacing: .16em; color: #94a3b8; }
    h1 { font-size: 58px; font-weight: 800; margin-top: 40px; }
    p { margin-top: 16px; font-size: 24px; color: #cbd5e1; }
    .foot { display: flex; gap: 26px; font: 600 19px/1 system-ui; }
  </style></head><body><div class="content">
    <div class="top"><img src="${mark}" alt="ACTIVE" /><span class="sub">MOVE · MEASURE · EXPLORE</span></div>
    <div><h1>用数据记录每一次前进。</h1><p>朱宝 · 运动与健康数字档案 — RUN · RIDE · HIKE · HEALTH</p></div>
    <div class="foot"><span style="color:#38bdf8">HEALTH</span><span style="color:#d9f36a">RUNNING</span><span style="color:#fbbf24">CYCLING</span><span style="color:#34d399">HIKING</span></div>
  </div></body></html>`,
  { waitUntil: 'load' }
);
await page.setViewportSize({ width: 1200, height: 630 });
fs.writeFileSync(path.join(OUT, 'og-brand.png'), await page.screenshot());
console.log('brand poster written');
await browser.close();
