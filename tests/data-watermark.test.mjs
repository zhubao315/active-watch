import test from 'node:test';
import assert from 'node:assert/strict';
import { validateWatermark } from '../scripts/data-watermark.mjs';

const NOW = Date.parse('2026-11-18T00:00:00Z');
const sha = 'sha256:' + 'a'.repeat(64);

const watermark = (overrides = {}) => ({
  schema_version: 1,
  site: 'running',
  generated_at: '2026-11-18T00:00:00Z',
  latest_activity_date: '2026-11-17',
  activity_count: 2039,
  source_updated_at: '2026-11-18T00:00:00Z',
  data_checksum: sha,
  build_version: 'a6d19ad',
  status: 'ok',
  ...overrides,
});

const opts = (overrides = {}) => ({
  site: 'running',
  maxSourceAgeDays: 3,
  maxActivityAgeDays: 14,
  baseline: 2039,
  now: NOW,
  ...overrides,
});

test('a fresh, consistent watermark passes', () => {
  assert.deepEqual(validateWatermark(watermark(), opts()), []);
});

test('stale sync timestamp is rejected', () => {
  const failures = validateWatermark(
    watermark({ source_updated_at: '2026-11-01T00:00:00Z' }),
    opts()
  );
  assert.ok(failures.some((f) => f.includes('last sync')));
});

test('very old activity date is rejected, a quiet fortnight is not', () => {
  assert.deepEqual(
    validateWatermark(watermark({ latest_activity_date: '2026-11-05' }), opts()),
    []
  );
  const failures = validateWatermark(
    watermark({ latest_activity_date: '2026-10-01' }),
    opts()
  );
  assert.ok(failures.some((f) => f.includes('latest activity')));
});

test('count collapse against the baseline is an incident', () => {
  const failures = validateWatermark(watermark({ activity_count: 1500 }), opts());
  assert.ok(failures.some((f) => f.includes('dropped')));
});

test('wrong site, bad checksum, missing build version are rejected', () => {
  const failures = validateWatermark(
    watermark({ site: 'cycling', data_checksum: 'md5:nope', build_version: '' }),
    opts()
  );
  assert.ok(failures.some((f) => f.includes('site')));
  assert.ok(failures.some((f) => f.includes('data_checksum')));
  assert.ok(failures.some((f) => f.includes('build_version')));
});

test('non-ok status and malformed object are rejected', () => {
  assert.ok(validateWatermark(watermark({ status: 'degraded' }), opts()).some((f) => f.includes('status')));
  assert.deepEqual(validateWatermark(null, opts()), ['data-watermark.json is not an object']);
});

test('hiking weekly cadence tolerates a quiet month but not a stale sync', () => {
  const w = watermark({
    site: 'hiking',
    activity_count: 344,
    latest_activity_date: '2026-10-27', // 22 days old — legitimate
    source_updated_at: '2026-11-16T00:00:00Z', // synced 2 days ago
  });
  assert.deepEqual(
    validateWatermark(w, opts({ site: 'hiking', maxSourceAgeDays: 10, maxActivityAgeDays: 60, baseline: 344 })),
    []
  );
  const staleSync = watermark({ ...w, source_updated_at: '2026-11-10T00:00:00Z' });
  assert.ok(
    validateWatermark(staleSync, opts({ site: 'hiking', maxSourceAgeDays: 3, baseline: 344 })).some((f) =>
      f.includes('last sync')
    )
  );
});
