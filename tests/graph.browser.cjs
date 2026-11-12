// Run against a static server; needs Playwright and Chromium (no app build/server).
const { chromium } = require('playwright');
const { readFileSync, existsSync, mkdirSync } = require('node:fs');
const assert = require('node:assert/strict');
const graph = JSON.parse(readFileSync('site/data/graph.json', 'utf8'));
const pia = graph.nodes.find(n => n.id === 'pia:ati-schedule-i-administrative-tribunals-support-service-of-canada/pia-95a42118fc3d');
const base = process.env.GRAPH_TEST_BASE || 'http://127.0.0.1:8766/';
const output = process.env.GRAPH_TEST_OUTPUT || 'work';
mkdirSync(output, { recursive: true });

(async () => {
  const browser = await chromium.launch({ headless: true,
    executablePath: process.env.BROWSER_EXECUTABLE || (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined), args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });
    const errors = [], evidenceRequests = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('request', r => { if (r.url().includes('/graph-evidence/')) evidenceRequests.push(r.url()); });
    await page.goto(base + 'graph.html?node=' + encodeURIComponent(pia.id));
    await page.waitForFunction(() => document.getElementById('view-status').textContent.includes('visible nodes'));
    assert.equal(await page.locator('#cy canvas').count(), 3, 'Cytoscape must render its canvas layers');
    assert.equal(evidenceRequests.length, 0, 'Evidence should be lazy loaded');
    assert.ok((await page.locator('#detail').textContent()).includes(pia.label_en));
    await page.locator('#connections button').filter({ hasText: 'Inspect evidence' }).first().click();
    await page.waitForSelector('.graph-evidence');
    assert.ok(evidenceRequests.length > 0);
    assert.ok((await page.locator('#detail').textContent()).includes('PSU'));
    assert.ok((await page.locator('#detail a[href*="#L"]').count()) > 0, 'Line-level evidence links must exist');
    const edgeURL = page.url();
    await page.reload(); await page.waitForSelector('.graph-evidence');
    assert.equal(page.url(), edgeURL);
    await page.locator('#language').click();
    assert.equal(await page.locator('html').getAttribute('lang'), 'fr');
    assert.ok((await page.locator('h1').textContent()).includes('FRP'));
    assert.ok(page.url().includes('lang=fr'));
    await page.goBack();
    assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    // Reset, search an official French bank alias and explore incoming assessments.
    await page.locator('#search-heading').click();
    await page.locator('#search').fill('POU 905');
    await page.locator('#results button').filter({ hasText: 'PSU 905' }).first().click();
    assert.ok((await page.locator('#detail').textContent()).includes('PSU 905'));
    const before = Number((await page.locator('#view-status').textContent()).match(/^\d+/)[0]);
    await page.locator('#connections button').filter({ hasText: 'Inspect evidence' }).first().click();
    await page.waitForSelector('.graph-evidence');
    // Selecting another node preserves the existing graph and adds one hop.
    await page.locator('#connections li button').first().click();
    const after = Number((await page.locator('#view-status').textContent()).match(/^\d+/)[0]);
    assert.ok(after >= before);
    await page.selectOption('#relation', 'references');
    assert.ok(!(await page.locator('#connections').textContent()).includes('Listed under institution'));
    // A high degree institution expands in explicit pages.
    const degrees = new Map();
    for (const e of graph.edges) for (const id of [e.source, e.target]) degrees.set(id, (degrees.get(id) || 0) + 1);
    const institution = graph.nodes.filter(n => n.type === 'institution').sort((a, b) => degrees.get(b.id) - degrees.get(a.id))[0];
    await page.goto(base + 'graph.html?node=' + encodeURIComponent(institution.id));
    await page.waitForSelector('#connections li');
    assert.equal(await page.locator('#connections li').count(), 25);
    await page.locator('#expand').click();
    assert.equal(await page.locator('#connections li').count(), 50);
    await page.locator('#network-heading').scrollIntoViewIfNeeded();
    await page.screenshot({ path: output + '/graph-desktop.png', fullPage: false });
    await page.locator('#search-heading').click();
    await page.locator('#search').fill('zz-no-matching-record');
    assert.equal(await page.locator('#results li').count(), 0);
    await page.locator('#search').fill('');
    await page.selectOption('#node-type', 'pia');
    await page.selectOption('#institution', pia.institution_id);
    assert.ok((await page.locator('#results').textContent()).includes(pia.label_en));
    // Unknown deep links and absent graph data are explicit, recoverable states.
    await page.goto(base + 'graph.html?node=nonexistent');
    await page.waitForFunction(() => document.getElementById('view-status').textContent.includes('not in the current graph'));
    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    mobile.on('pageerror', e => errors.push(e.message));
    await mobile.goto(base + 'graph.html?lang=fr&node=' + encodeURIComponent(pia.id));
    await mobile.waitForSelector('#connections li');
    await mobile.locator('#connections button').filter({ hasText: 'Consulter les preuves' }).first().click();
    await mobile.waitForSelector('.graph-evidence');
    assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true, 'Mobile horizontal overflow');
    await mobile.screenshot({ path: output + '/graph-mobile.png', fullPage: true });
    // Existing record pages enter the same source-scoped graph identity.
    const entry = await browser.newPage();
    entry.on('pageerror', e => errors.push(e.message));
    await entry.goto(base + pia.record_url + '&lang=fr');
    await entry.waitForSelector('#reader-content:not([hidden])');
    const graphLink = new URL(await entry.locator('#explore-network').getAttribute('href'), base);
    assert.equal(graphLink.searchParams.get('node'), pia.id);
    assert.equal(graphLink.searchParams.get('lang'), 'fr');
    const bank = graph.nodes.find(n => n.id === 'pib:standard:PSU 905');
    await entry.goto(base + bank.record_url);
    await entry.waitForSelector('#record-dialog[open]');
    const bankLink = new URL(await entry.locator('#record-dialog a[href^="graph.html"]').getAttribute('href'), base);
    assert.equal(bankLink.searchParams.get('node'), bank.id);
    await entry.close();
    // The keyboard list remains useful if the diagram library is unavailable.
    const fallback = await browser.newPage();
    await fallback.route('**/vendor/cytoscape-*.js', route => route.abort());
    await fallback.goto(base + 'graph.html?node=' + encodeURIComponent(pia.id));
    await fallback.waitForSelector('#connections li');
    assert.ok((await fallback.locator('#view-status').textContent()).includes('connection list remain available'));
    const failed = await browser.newPage();
    await failed.route('**/data/graph.json', route => route.fulfill({ status: 503, body: '{}' }));
    await failed.goto(base + 'graph.html');
    await failed.waitForSelector('#view-status[role="alert"]');
    assert.ok((await failed.locator('#view-status').textContent()).includes('could not be loaded'));
    assert.deepEqual(errors, []);
    console.log('Graph browser checks passed: real data, lazy evidence, bilingual navigation, view URLs, expansion, filters, mobile, missing-data and diagram fallback.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
