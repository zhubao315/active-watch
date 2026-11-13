#!/usr/bin/env node
// ACTIVE daily patrol: checks all four public sites and opens ONE GitHub
// issue only when something actually needs attention. No news is good news.
//
//   - every site answers HTTP 200 and speaks the ACTIVE brand
//   - brand-tokens.css is one blob across the four repos (source of truth),
//     and the favicon served online is byte-identical (deployed truth)
//   - the data behind each site is fresh (commit cadence + health quality)
//   - no workflow has failed on a default branch in the last 36 hours
//
// Runs from .github/workflows/patrol.yml with GITHUB_TOKEN available.

import { createHash } from 'node:crypto';

const API = process.env.GITHUB_API || 'https://api.github.com';
const PAGES = 'https://zhubao315.github.io';
const SITES = [
  { key: 'running', repo: 'running', branch: 'master', maxAgeDays: 3, brandPath: 'src/styles/brand-tokens.css', favicon: '/running/brand/favicon-32.png' },
  { key: 'cycling', repo: 'cycling', branch: 'main', maxAgeDays: 3, brandPath: 'src/styles/brand-tokens.css', favicon: '/cycling/brand/favicon-32.png' },
  { key: 'hiking', repo: 'hiking', branch: 'main', maxAgeDays: 8, brandPath: 'src/styles/brand-tokens.css', favicon: '/hiking/brand/favicon-32.png' }, // weekly sync by design
  { key: 'health', repo: 'health', branch: 'main', maxAgeDays: 3, brandPath: 'dashboard/brand-tokens.css', favicon: '/health/brand/favicon-32.png' },
];
for (const s of SITES) s.url = `https://zhubao315.github.io/${s.key}/`;

const incidents = [];
const notes = [];

const gh = async (path) => {
  const r = await fetch(API + path, {
    headers: {
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      'X-GitHub-Api-Version': '2022-11-28',
    },
    signal: AbortSignal.timeout(45_000),
  });
  return { status: r.status, json: r.status < 400 ? await r.json() : null };
};
const web = (url) =>
  fetch(url, { redirect: 'follow', signal: AbortSignal.timeout(45_000) });
const md5 = (buf) => createHash('md5').update(new Uint8Array(buf)).digest('hex');

// ------------------------------------------------------------ sites live ----
for (const site of SITES) {
  let res;
  try {
    res = await web(`${site.url}?nocache=${Date.now()}`);
  } catch (e) {
    incidents.push(`${site.key}: 站点无法访问（${e.message}）`);
    continue;
  }
  const html = await res.text();
  const title = html.match(/<title>([^<]*)<\/title>/)?.[1] ?? '';
  if (res.status !== 200) incidents.push(`${site.key}: 站点返回 HTTP ${res.status}`);
  else {
    if (!title.startsWith('ACTIVE /')) incidents.push(`${site.key}: 页面标题异常「${title}」`);
    if (html.includes('ZB ACTIVE')) incidents.push(`${site.key}: 页面出现旧母品牌名 ZB ACTIVE`);
  }
}

// -------------------------------------------------- brand source identity ----
const blobs = {};
for (const site of SITES) {
  const { status, json } = await gh(`/repos/zhubao315/${site.repo}/contents/${site.brandPath}?ref=${site.branch}`);
  if (status !== 200) incidents.push(`${site.key}: 无法读取 ${site.brandPath} (HTTP ${status})`);
  else blobs[site.key] = json.sha;
}
if (Object.keys(blobs).length === SITES.length && new Set(Object.values(blobs)).size > 1) {
  incidents.push(`brand-tokens.css 四仓不再同源：${Object.entries(blobs).map(([k, v]) => `${k}=${v.slice(0, 8)}`).join(' ')}`);
} else if (Object.keys(blobs).length === SITES.length) {
  notes.push(`brand-tokens.css 四仓同源 (${Object.values(blobs)[0].slice(0, 8)}) ✓`);
}

// -------------------------------------------------- brand deployed identity ----
const favicons = {};
for (const site of SITES) {
  try {
    const r = await web(`${PAGES}${site.favicon}?v=${Date.now()}`);
    if (r.status !== 200) incidents.push(`${site.key}: 线上品牌文件 ${site.favicon} HTTP ${r.status}`);
    else favicons[site.key] = md5(await r.arrayBuffer());
  } catch (e) {
    incidents.push(`${site.key}: 线上品牌文件 ${site.favicon} 拉取失败（${e.message}）`);
  }
}
if (Object.keys(favicons).length === SITES.length) {
  if (new Set(Object.values(favicons)).size > 1) incidents.push('线上 favicon-32.png 四站不一致（部署副本漂移）');
  else notes.push('线上共享品牌文件四站一致 ✓');
}

// ------------------------------------------------------- data freshness ----
for (const site of SITES) {
  const { status, json } = await gh(`/repos/zhubao315/${site.repo}/commits?sha=${site.branch}&per_page=1`);
  if (status !== 200) {
    incidents.push(`${site.key}: 无法读取最近提交 (HTTP ${status})`);
    continue;
  }
  const when = new Date(json[0]?.commit?.committer?.date ?? 0);
  const ageDays = (Date.now() - when.getTime()) / 86_400_000;
  if (ageDays > site.maxAgeDays) incidents.push(`${site.key}: 数据提交已停滞 ${ageDays.toFixed(1)} 天（阈值 ${site.maxAgeDays} 天）`);
  else notes.push(`${site.key}: 最近提交 ${ageDays.toFixed(1)} 天前 ✓`);
}

// health's own quality report
{
  try {
    const r = await web(`https://zhubao315.github.io/health/data_quality.json?_=${Date.now()}`);
    if (r.status === 200) {
      const q = await r.json();
      const lag = (Date.now() - new Date(q.latest_data_date + 'T00:00:00+08:00').getTime()) / 86_400_000;
      if (lag > 2.5) incidents.push(`health: 最新数据日期 ${q.latest_data_date} 已落后 ${lag.toFixed(1)} 天`);
      else notes.push(`health: 最新数据 ${q.latest_data_date} ✓`);
      if (q.status && q.status !== 'ok') incidents.push(`health: data_quality.status = ${q.status}`);
    } else incidents.push(`health: data_quality.json HTTP ${r.status}`);
  } catch (e) {
    incidents.push(`health: data_quality.json 拉取失败（${e.message}）`);
  }
}

// --------------------------------------------------- workflow failures ----
for (const site of SITES) {
  const { status, json } = await gh(`/repos/zhubao315/${site.repo}/actions/runs?branch=${site.branch}&per_page=8`);
  if (status !== 200) continue;
  // Judge each workflow by its newest run only: a failure that was already
  // followed by a green rerun is not an open incident.
  const newest = {};
  for (const run of json.workflow_runs ?? []) newest[run.name] ??= run;
  for (const run of Object.values(newest)) {
    if (run.conclusion === 'failure' && Date.now() - new Date(run.created_at).getTime() < 36 * 3600_000) {
      incidents.push(`${site.key}: 工作流「${run.name}」最近一次运行失败（${run.event}，${run.html_url}）`);
    }
  }
}

// --------------------------------------------------------- issue policy ----
const body = [
  '## ACTIVE 四站巡检',
  '',
  `> 巡检时间：${new Date().toISOString()}（UTC）`,
  '',
  '### 需要处理',
  ...(incidents.length ? incidents.map((i) => `- [ ] ${i}`) : ['- （无）']),
  '',
  '### 状态',
  ...notes.map((n) => `- ${n}`),
  '',
  '_巡检范围：四站可用性 / 品牌一致性（仓库源 + 线上部署）/ 数据新鲜度（提交节奏 + health 质量文件）/ 默认分支工作流失败。由 active-watch 每日自动执行；全部恢复后本 issue 自动关闭。_',
].join('\n');

const call = async (path, opts = {}) => {
  const r = await fetch(`${API}/repos/zhubao315/active-watch${path}`, {
    method: opts.method ?? 'GET',
    headers: {
      Accept: 'application/vnd.github+json',
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
    signal: AbortSignal.timeout(30_000),
  });
  return r.status < 300 ? r.json() : { status: r.status };
};

const open = (await call('/issues?labels=watch%3Aincident&state=open&per_page=1'))[0];
if (incidents.length) {
  if (open) {
    await call(`/issues/${open.number}`, { method: 'PATCH', body: { title: `[巡检] ACTIVE 四站有 ${incidents.length} 项待处理`, body } });
    console.log(`updated issue #${open.number}: ${incidents.length} incident(s)`);
  } else {
    const created = await call('/issues', {
      method: 'POST',
      body: { title: `[巡检] ACTIVE 四站有 ${incidents.length} 项待处理`, body, labels: ['watch:incident'] },
    });
    console.log(`opened issue #${created.number}: ${incidents.length} incident(s)`);
  }
} else if (open) {
  await call(`/issues/${open.number}`, { method: 'PATCH', body: { state: 'closed', state_reason: 'completed' } });
  await call(`/issues/${open.number}/comments`, { method: 'POST', body: { body: '全部恢复正常，自动关闭。' } });
  console.log(`closed issue #${open.number}`);
} else {
  console.log('all clear — nothing to report');
}
