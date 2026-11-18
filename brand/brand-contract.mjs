/**
 * ACTIVE brand contract — the single, testable definition of "a page speaks
 * the ACTIVE brand".
 *
 * Two consumers:
 *   - verify-live.mjs / verify-sites.mjs inject `collectBrandReport` into the
 *     browser and run `checkBrandReport` in Node;
 *   - tests/brand-contract.test.mjs exercises `checkBrandReport` against
 *     synthetic reports (no browser required).
 *
 * `collectBrandReport` MUST stay self-contained: page.evaluate serialises the
 * function, so it cannot close over module-level constants. Keep the legacy
 * names and site keys inlined here in sync with the exports below.
 */

export const CURRENT_BRAND = 'ACTIVE';
export const LEGACY_BRANDS = ['ZB ACTIVE'];
export const SITE_KEYS = ['health', 'running', 'cycling', 'hiking'];

/** Injected into the page. No closures, no imports. */
export function collectBrandReport() {
  const qa = (sel) => Array.from(document.querySelectorAll(sel));
  const brandLink = document.querySelector(
    'header a[aria-label="ACTIVE"], header a.brand'
  );
  const normalise = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const brandText = brandLink ? normalise(brandLink.textContent) : '';
  const title = document.title || '';
  const bodyText = normalise(document.body ? document.body.innerText : '');
  const nav = qa('a[data-site]');
  const siteKeys = Array.from(
    new Set(nav.map((a) => (a.getAttribute('data-site') || '').toLowerCase()))
  )
    .filter(Boolean)
    .sort();

  return {
    title,
    siteKeys,
    brandLink: !!brandLink,
    brandText,
    logo: brandLink ? !!brandLink.querySelector('img, svg') : false,
    // Whether the retired mother-brand name survives anywhere the user can
    // see it. The old name is a defect, never the expected value.
    legacyInTitle: title.includes('ZB ACTIVE'),
    legacyInText: bodyText.includes('ZB ACTIVE'),
    navCount: nav.length,
    navIcons: nav.filter((a) => a.querySelector('svg')).length,
    currentCount: qa(
      'header a[aria-current="page"], header a[aria-current="true"]'
    ).length,
    theme: document.documentElement.getAttribute('data-theme') || '',
    overflow:
      document.documentElement.scrollWidth -
      document.documentElement.clientWidth,
    brokenImages: qa('img').filter((i) => !i.complete || i.naturalWidth === 0)
      .length,
  };
}

/**
 * Pure validator. Returns a list of human-readable failures; empty means the
 * page satisfies the brand contract.
 *
 * @param {ReturnType<typeof collectBrandReport>} r
 * @param {{ siteKey?: string }} [opts]
 */
export function checkBrandReport(r, opts = {}) {
  const failures = [];
  const site = (opts.siteKey || '').toLowerCase();

  if (!r.title.startsWith('ACTIVE /')) {
    failures.push(`title "ACTIVE / …" missing (got "${r.title}")`);
  }
  if (r.legacyInTitle) failures.push('legacy brand "ZB ACTIVE" in document.title');
  if (r.legacyInText) failures.push('legacy brand "ZB ACTIVE" in body text');

  if (!r.brandLink) failures.push('header brand link missing');
  if (!r.logo) failures.push('brand logo (img/svg) missing');
  // "ZB ACTIVE" contains "ACTIVE" as a substring — strip the retired name
  // before checking the current one, otherwise the old brand silently passes.
  if (LEGACY_BRANDS.some((name) => r.brandText.includes(name))) {
    failures.push('legacy brand "ZB ACTIVE" in brand link');
  }
  const brandText = LEGACY_BRANDS.reduce(
    (s, name) => s.split(name).join(''),
    r.brandText
  );
  if (!brandText.includes(CURRENT_BRAND)) {
    failures.push(`wordmark "${CURRENT_BRAND}" missing in brand link`);
  }
  if (site && !r.brandText.toUpperCase().includes(site.toUpperCase())) {
    failures.push(`site name "${site.toUpperCase()}" missing in header`);
  }

  for (const key of SITE_KEYS) {
    if (!r.siteKeys.includes(key)) failures.push(`nav missing site ${key}`);
  }
  if (r.navIcons < SITE_KEYS.length) {
    failures.push(`nav icons ${r.navIcons} < ${SITE_KEYS.length}`);
  }
  if (r.currentCount !== 1) {
    failures.push(`current nav item count ${r.currentCount} != 1`);
  }
  if (!['dark', 'light'].includes(r.theme)) {
    failures.push(`theme attribute unexpected: "${r.theme}"`);
  }
  if (r.overflow > 1) failures.push(`horizontal overflow ${r.overflow}px`);
  if (r.brokenImages > 0) failures.push(`broken images ${r.brokenImages}`);

  return failures;
}
