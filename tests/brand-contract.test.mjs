import test from 'node:test';
import assert from 'node:assert/strict';
import {
  checkBrandReport,
  CURRENT_BRAND,
  LEGACY_BRANDS,
  SITE_KEYS,
} from '../brand/brand-contract.mjs';

const healthy = (siteKey) => ({
  title: `ACTIVE / ${siteKey.toUpperCase()}｜测试`,
  siteKeys: [...SITE_KEYS],
  brandLink: true,
  brandText: `${CURRENT_BRAND} 跑步 ${siteKey.toUpperCase()}`,
  logo: true,
  markSrc: '/brand/active-mark.png',
  legacyInTitle: false,
  legacyInText: false,
  navCount: 8,
  navIcons: 4,
  currentCount: 1,
  theme: 'dark',
  overflow: 0,
  brokenImages: 0,
});

test('a healthy page passes', () => {
  assert.deepEqual(checkBrandReport(healthy('running'), { siteKey: 'running' }), []);
});

test('the current brand is ACTIVE and the retired name is retired', () => {
  assert.equal(CURRENT_BRAND, 'ACTIVE');
  assert.deepEqual(LEGACY_BRANDS, ['ZB ACTIVE']);
});

test('the old ZB ACTIVE wordmark is a failure, never a pass', () => {
  const r = healthy('running');
  r.brandText = 'ZB ACTIVE 跑步 RUNNING';
  r.legacyInText = true;
  r.legacyInTitle = true;
  const failures = checkBrandReport(r, { siteKey: 'running' });
  assert.ok(failures.some((f) => f.includes('wordmark "ACTIVE" missing')));
  assert.ok(failures.some((f) => f.includes('legacy brand "ZB ACTIVE" in document.title')));
  assert.ok(failures.some((f) => f.includes('legacy brand "ZB ACTIVE" in body text')));
});

test('stable DOM contract: logo, site name, four nav sites, one current item', () => {
  const r = healthy('cycling');
  r.logo = false;
  r.brandText = 'ACTIVE 跑步'; // no site name
  r.siteKeys = ['running', 'cycling', 'hiking'];
  r.navIcons = 3;
  r.currentCount = 0;
  const failures = checkBrandReport(r, { siteKey: 'cycling' });
  assert.ok(failures.some((f) => f.includes('logo')));
  assert.ok(failures.some((f) => f.includes('site name "CYCLING"')));
  assert.ok(failures.some((f) => f.includes('nav missing site health')));
  assert.ok(failures.some((f) => f.includes('nav icons 3')));
  assert.ok(failures.some((f) => f.includes('current nav item count 0')));
});

test('the v3 mark is the sliced A, not the retired Z symbol', () => {
  const old = healthy('running');
  old.markSrc = '/brand/zhubao-symbol.png';
  const failures = checkBrandReport(old, { siteKey: 'running' });
  assert.ok(failures.some((f) => f.includes('not the ACTIVE A-mark slice')));
  assert.ok(failures.some((f) => f.includes('retired Z-symbol')));
});

test('runtime health: theme, overflow and broken images', () => {
  const r = healthy('health');
  r.theme = '';
  r.overflow = 12;
  r.brokenImages = 2;
  const failures = checkBrandReport(r, { siteKey: 'health' });
  assert.ok(failures.some((f) => f.includes('theme')));
  assert.ok(failures.some((f) => f.includes('overflow 12px')));
  assert.ok(failures.some((f) => f.includes('broken images 2')));
});
