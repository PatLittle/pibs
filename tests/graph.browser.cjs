// Run against a static server; needs Playwright and Chromium.
const { chromium } = require('playwright');
const { readFileSync, existsSync, mkdirSync } = require('node:fs');
const assert = require('node:assert/strict');
const graph = JSON.parse(readFileSync('site/data/graph.json', 'utf8'));
const pia = graph.nodes.find(n => n.id === 'pia:ati-schedule-i-administrative-tribunals-support-service-of-canada/pia-95a42118fc3d');
const base = process.env.GRAPH_TEST_BASE || 'http://127.0.0.1:8766/';
const output = process.env.GRAPH_TEST_OUTPUT || 'work';
mkdirSync(output, { recursive: true });
const degrees = new Map();
for (const e of graph.edges) for (const id of [e.source, e.target]) degrees.set(id, (degrees.get(id) || 0) + 1);
const institution = graph.nodes.filter(n => n.type === 'institution').sort((a, b) => degrees.get(b.id) - degrees.get(a.id))[0];
const nodeURL = id => base + 'graph.html?node=' + encodeURIComponent(id);
const ready = page => page.waitForFunction(() => document.getElementById('view-status').textContent.includes('visible nodes'));

(async () => {
  const browser = await chromium.launch({ headless: true,
    executablePath: process.env.BROWSER_EXECUTABLE || (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined), args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
    const errors = [], evidenceRequests = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => { if (r.url().includes('/graph-evidence/')) evidenceRequests.push(r.url()); });
    await page.goto(nodeURL(pia.id)); await ready(page);
    assert.equal(await page.locator('#cy canvas').count(), 3);
    assert.equal(evidenceRequests.length, 0, 'Evidence is loaded on demand');
    assert.equal(await page.locator('.record-card').getAttribute('data-node-type'), 'pia');
    assert.equal(await page.locator('.record-card').evaluate(n => getComputedStyle(n).borderTopColor), 'rgb(8, 122, 130)');
    assert.ok((await page.locator('#detail').textContent()).includes(pia.label_en));
    await page.locator('#tab-browser').click();
    await page.locator('#connections .evidence-button').filter({ hasText: 'References' }).first().click();
    await page.waitForSelector('.graph-evidence');
    assert.ok(evidenceRequests.length > 0);
    assert.ok((await page.locator('#detail a[href*="#L"]').count()) > 0);
    const edgeURL = page.url();
    await page.reload(); await page.waitForSelector('.graph-evidence'); assert.equal(page.url(), edgeURL);
    await page.locator('#language').click(); assert.equal(await page.locator('html').getAttribute('lang'), 'fr');
    await page.goBack(); assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    await page.locator('#search-heading').click(); await page.locator('#search').fill('POU 905');
    await page.locator('#results button').filter({ hasText: 'PSU 905' }).first().click();
    assert.equal(await page.locator('.record-card').getAttribute('data-node-type'), 'pib');
    assert.equal(await page.locator('.record-card').evaluate(n => getComputedStyle(n).borderTopColor), 'rgb(31, 90, 148)');
    // Colour-coded summary chips open the corresponding list of real neighbours.
    await page.locator('.type-chips button[data-node-type="pia"]').click();
    assert.equal(await page.locator('#browser-type').inputValue(), 'pia');
    assert.ok((await page.locator('#connections li').evaluateAll(ns => ns.map(n => n.dataset.nodeType))).every(type => type === 'pia'));

    // Full screen retains a pageable list, independent of graph expansion.
    await page.goto(nodeURL(institution.id)); await ready(page);
    assert.ok((await page.locator('#view-status').textContent()).startsWith('26 visible nodes'));
    await page.locator('#expand').click();
    assert.ok((await page.locator('#view-status').textContent()).startsWith('51 visible nodes'));
    await page.locator('#fullscreen').click(); await page.waitForSelector('#explorer.is-expanded');
    await page.waitForFunction(() => document.fullscreenElement?.id === 'explorer');
    assert.equal(await page.locator('#explorer').getAttribute('aria-modal'), 'true');
    assert.equal(await page.locator('#search-panel').evaluate(n => n.inert), true);
    await page.locator('#tab-browser').click();
    assert.equal(await page.locator('#connections li').count(), 8);
    assert.ok((await page.locator('#page-status').textContent()).startsWith('Page 1 of'));
    const first = await page.locator('#connections li').evaluateAll(ns => ns.map(n => n.dataset.recordId));
    await page.evaluate(() => document.fonts.ready);
    const before = await page.locator('#cy').screenshot();
    const graphStatus = await page.locator('#view-status').textContent();
    await page.locator('#next-page').click();
    const second = await page.locator('#connections li').evaluateAll(ns => ns.map(n => n.dataset.recordId));
    assert.equal(first.some(id => second.includes(id)), false);
    assert.equal(await page.locator('#view-status').textContent(), graphStatus);
    assert.equal(Buffer.compare(before, await page.locator('#cy').screenshot()), 0, 'Paging must not move the graph');
    await page.screenshot({ path: output + '/graph-fullscreen-browser.png' });
    await page.locator('#connections .record-row-title').first().click();
    assert.equal(new URL(page.url()).searchParams.get('node'), second[0]);
    assert.ok((await page.locator('#record-position').textContent()).startsWith('Record 9 of'));
    await page.locator('#next-record').click();
    assert.equal(new URL(page.url()).searchParams.get('node'), second[1]);
    await page.locator('#previous-record').click();
    assert.equal(new URL(page.url()).searchParams.get('node'), second[0]);
    await page.locator('#tab-browser').click();
    assert.ok((await page.locator('#page-status').textContent()).startsWith('Page 2 of'));
    assert.ok((await page.locator('#browser-anchor').textContent()).includes(institution.label_en));
    await page.selectOption('#browser-scope', 'all'); await page.selectOption('#browser-type', 'pib');
    await page.selectOption('#browser-sort', 'degree');
    const ranked = await page.locator('#connections li').evaluateAll(ns => ns.map(n => n.dataset.recordId));
    assert.ok(ranked.slice(1).every((id, i) => (degrees.get(ranked[i]) || 0) >= (degrees.get(id) || 0)));
    assert.equal(degrees.get(ranked[0]), Math.max(...graph.nodes.filter(n => n.type === 'pib').map(n => degrees.get(n.id) || 0)));
    await page.locator('#browser-query').fill('POU 905');
    assert.ok((await page.locator('#connections').textContent()).includes('PSU 905'));
    assert.equal(await page.locator('#next-page').isDisabled(), true);
    await page.locator('#browser-query').fill('zz-no-matching-record'); assert.equal(await page.locator('#connections li').count(), 0);
    assert.equal(await page.locator('#next-page').isDisabled(), true);
    await page.locator('#browser-query').fill(''); await page.selectOption('#records-per-page', '16');
    assert.equal(await page.locator('#connections li').count(), 16);
    await page.locator('#toggle-panel').click(); assert.equal(await page.locator('#inspector').isVisible(), false);
    await page.locator('#toggle-panel').click(); assert.equal(await page.locator('#inspector').isVisible(), true);
    await page.locator('#highlight').uncheck(); assert.equal(await page.locator('#highlight').isChecked(), false);
    // Browser-initiated exit restores page access and keyboard focus.
    await page.evaluate(() => document.exitFullscreen()); await page.waitForSelector('#explorer:not(.is-expanded)');
    assert.equal(await page.locator('#search-panel').evaluate(n => n.inert), false);
    assert.equal(await page.locator('#fullscreen').evaluate(n => n === document.activeElement), true);

    // A portrait layout keeps both graph and browser usable in full screen.
    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    mobile.on('pageerror', e => errors.push(e.message));
    await mobile.goto(nodeURL(pia.id) + '&lang=fr'); await mobile.waitForSelector('.record-card');
    await mobile.locator('#fullscreen').click(); await mobile.waitForSelector('#explorer.is-expanded');
    await mobile.locator('#tab-browser').click(); await mobile.locator('#browser-filters summary').click(); await mobile.selectOption('#browser-scope', 'all');
    await mobile.selectOption('#browser-type', 'pib'); await mobile.locator('#browser-query').fill('POU 905');
    await mobile.locator('#connections .record-row-title').first().click();
    assert.ok((await mobile.locator('#detail').textContent()).includes('PSU 905'));
    assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true);
    const boxes = await mobile.locator('#explorer, #cy, #inspector').evaluateAll(ns => ns.map(n => { const r = n.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; }));
    assert.ok(boxes.every(b => b.x >= 0 && b.y >= 0 && b.x + b.w <= 391 && b.y + b.h <= 845));
    assert.ok(boxes[1].h >= 140 && boxes[2].h >= 190);
    await mobile.screenshot({ path: output + '/graph-fullscreen-mobile.png' });
    await mobile.locator('#workspace-language').click(); assert.equal(await mobile.locator('html').getAttribute('lang'), 'en');
    await mobile.locator('#fullscreen').click(); await mobile.waitForSelector('#explorer:not(.is-expanded)');

    // Explicit viewport fallback, Escape, tab containment and missing diagram.
    const fallback = await browser.newPage({ viewport: { width: 1280, height: 800 } });
    fallback.on('pageerror', e => errors.push(e.message));
    await fallback.addInitScript(() => Object.defineProperty(Element.prototype, 'requestFullscreen', { configurable: true, value: undefined }));
    await fallback.route('**/vendor/cytoscape-*.js', route => route.abort());
    await fallback.goto(nodeURL(pia.id)); await fallback.waitForSelector('.record-card');
    assert.ok((await fallback.locator('#view-status').textContent()).includes('connection list remain available'));
    await fallback.locator('#fullscreen').click(); await fallback.waitForSelector('#explorer.is-expanded');
    assert.equal(await fallback.evaluate(() => document.fullscreenElement), null);
    await fallback.locator('#workspace-language').focus(); await fallback.keyboard.press('Shift+Tab');
    assert.equal(await fallback.evaluate(() => document.getElementById('explorer').contains(document.activeElement)), true);
    await fallback.keyboard.press('Escape'); await fallback.waitForSelector('#explorer:not(.is-expanded)');
    assert.equal(await fallback.locator('#fullscreen').evaluate(n => n === document.activeElement), true);
    await fallback.goto(base + 'graph.html?node=nonexistent');
    await fallback.waitForFunction(() => document.getElementById('view-status').textContent.includes('not in the current graph'));
    const failed = await browser.newPage();
    await failed.route('**/data/graph.json', route => route.fulfill({ status: 503, body: '{}' }));
    await failed.goto(base + 'graph.html'); await failed.waitForSelector('#view-status[role="alert"]');
    assert.ok((await failed.locator('#view-status').textContent()).includes('could not be loaded'));
    assert.deepEqual(errors, []);
    console.log('Graph browser checks passed: native/fallback full screen, record/page navigation, fixed-map pagination, shared palette, hub sorting, bilingual mobile, evidence, history and failure states.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
