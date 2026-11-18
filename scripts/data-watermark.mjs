/**
 * Pure validation of a sport site's data watermark. Shared by patrol.mjs and
 * tests/data-watermark.test.mjs — no I/O, no clock reads (pass `now`).
 *
 * Two independent clocks matter:
 *   - source_updated_at: did the sync actually run recently? (strict)
 *   - latest_activity_date: is there genuinely new activity data? (generous;
 *     a hiker may not walk for weeks without the system being broken)
 */

const SHA256 = /^sha256:[0-9a-f]{64}$/;
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

/**
 * @param {any} w parsed data-watermark.json
 * @param {{ site: string, maxSourceAgeDays: number, maxActivityAgeDays: number,
 *          baseline?: number, minCountRatio?: number, now?: number }} opts
 * @returns {string[]} failures (empty = watermark is healthy)
 */
export function validateWatermark(w, opts) {
  const failures = [];
  const now = opts.now ?? Date.now();
  const site = opts.site;
  const minRatio = opts.minCountRatio ?? 0.9;

  if (!w || typeof w !== 'object' || Array.isArray(w)) {
    return ['data-watermark.json is not an object'];
  }
  if (w.schema_version !== 1) {
    failures.push(`schema_version ${w.schema_version} != 1`);
  }
  if (w.site !== site) failures.push(`site "${w.site}" != "${site}"`);
  if (w.status !== 'ok') failures.push(`status "${w.status}" != "ok"`);

  // Clock 1: last successful sync. Must be recent for every site.
  const synced = Date.parse(w.source_updated_at);
  if (Number.isNaN(synced)) {
    failures.push(`source_updated_at invalid: "${w.source_updated_at}"`);
  } else {
    const ageDays = (now - synced) / 86_400_000;
    if (ageDays > opts.maxSourceAgeDays + 1) {
      failures.push(
        `last sync ${w.source_updated_at} is ${ageDays.toFixed(1)} days old (limit ${opts.maxSourceAgeDays})`
      );
    }
  }
  if (Number.isNaN(Date.parse(w.generated_at))) {
    failures.push(`generated_at invalid: "${w.generated_at}"`);
  }

  // Clock 2: newest real activity. Generous, sport-specific threshold.
  const date = String(w.latest_activity_date || '');
  if (!ISO_DATE.test(date) || Number.isNaN(Date.parse(date + 'T00:00:00Z'))) {
    failures.push(`latest_activity_date invalid: "${date}"`);
  } else {
    const ageDays = (now - Date.parse(date + 'T00:00:00Z')) / 86_400_000;
    if (ageDays > opts.maxActivityAgeDays) {
      failures.push(
        `latest activity ${date} is ${ageDays.toFixed(1)} days old (limit ${opts.maxActivityAgeDays})`
      );
    }
  }

  if (!Number.isInteger(w.activity_count) || w.activity_count <= 0) {
    failures.push(`activity_count invalid: ${w.activity_count}`);
  } else if (opts.baseline && w.activity_count < opts.baseline * minRatio) {
    failures.push(
      `activity_count ${w.activity_count} dropped >${Math.round((1 - minRatio) * 100)}% from baseline ${opts.baseline}`
    );
  }

  if (!SHA256.test(String(w.data_checksum || ''))) {
    failures.push(`data_checksum invalid: "${w.data_checksum}"`);
  }
  if (typeof w.build_version !== 'string' || !w.build_version) {
    failures.push('build_version missing');
  }
  return failures;
}
