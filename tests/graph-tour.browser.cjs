// Real-browser coverage for curated starts, vocabulary navigation and every tour stop.
const { chromium } = require('playwright');
const { existsSync, mkdirSync } = require('node:fs');
const assert = require('node:assert/strict');
const base = process.env.GRAPH_TEST_BASE || 'http://127.0.0.1:8766/';
const output = process.env.GRAPH_TEST_OUTPUT || 'work';
mkdirSync(output, { recursive: true });
const ready = p => p.waitForFunction(() => document.getElementById('view-status').textContent.includes('visible nodes') || document.getElementById('view-status').textContent.includes('nœuds visibles'));
(async () => {
  const { TOUR_STEPS } = await import('../site/graph-tour.mjs');
  const browser = await chromium.launch({ headless: true, executablePath: process.env.BROWSER_EXECUTABLE || (existsSync('/usr/bin/chromium') ? '/usr/bin/chromium' : undefined), args: ['--no-sandbox'] });
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.on('pageerror', e => errors.push(e.message));
    const attributeRequests = [];
    page.on('request', r => { if (r.url().includes('/graph-attributes/')) attributeRequests.push(r.url()); });
    await page.goto(base + 'graph.html'); await ready(page);
    await page.waitForSelector('.record-attributes summary');
    assert.equal(attributeRequests.length, 1, 'Load attributes for the selected record only');
    assert.equal(await page.locator('#language, #workspace-language').count(), 0);
    assert.equal(await page.locator('[data-example]').count(), 5);
    assert.equal(await page.locator('#results button').count(), 0);
    const ids = await page.locator('[data-example]').evaluateAll(ns => ns.map(n => n.dataset.example));
    for (const id of ids) {
      await page.locator('#example-list button').evaluateAll((ns, id) => ns.find(n => n.dataset.example === id).click(), id);
      assert.equal(new URL(page.url()).searchParams.get('node'), id);
      assert.ok((await page.locator('#detail').textContent()).length > 100);
    }
    await page.locator('#search').fill('staffing');
    assert.ok(await page.locator('#results button').count() > 0);
    assert.equal(await page.locator('#examples').isHidden(), true);
    await page.locator('#search').fill('');
    await page.selectOption('#node-type', 'standard-pib');
    assert.ok((await page.locator('#search-status').textContent()).includes('49'));
    await page.selectOption('#node-type', 'standard-class');
    assert.ok((await page.locator('#search-status').textContent()).includes('33'));
    await page.selectOption('#node-type', 'category');
    await page.locator('#results button').first().click();
    assert.ok((await page.locator('#detail').textContent()).includes('estimated matches'));
    await page.locator('#tab-browser').click();
    await page.locator('#connections .evidence-button').first().click();
    await page.waitForSelector('.graph-evidence');
    assert.ok((await page.locator('#detail').textContent()).includes('Rule confidence'));
    assert.ok((await page.locator('#detail').textContent()).includes('Matching rule'));
    await page.locator('#search-heading').click(); await page.selectOption('#node-type', 'pib_type');
    await page.locator('#results button').first().click();
    assert.equal(await page.locator('.record-card').getAttribute('data-node-type'), 'pib_type');
    const before = { url: page.url(), status: await page.locator('#view-status').textContent(), text: await page.locator('#detail').textContent() };
    await page.locator('#tour-launch').click();
    assert.equal(await page.locator('#tour-step option').count(), TOUR_STEPS.length);
    for (let i = 0; i < TOUR_STEPS.length; i++) {
      const step = TOUR_STEPS[i];
      if (i) await page.locator('#tour-next').click();
      await page.waitForFunction(id => document.getElementById('graph-tour').dataset.step === id && document.querySelector('.tour-card').getAttribute('aria-busy') === 'false', step.id);
      assert.ok(await page.locator(step.target).first().isVisible(), `Tour target must be visible: ${step.id}`);
      const box = await page.locator('.tour-card').boundingBox();
      assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.width <= 1441 && box.y + box.height <= 1001, step.id);
      if (step.id === 'diagram') await page.screenshot({ path: output + '/graph-tour-desktop.png' });
      if (step.id === 'search') {
        // The tour explains real, usable controls instead of a screenshot.
        await page.locator('#search').fill('PSU 905');
        assert.ok((await page.locator('#results').textContent()).includes('Electronic Network'));
      }
    }
    await page.locator('#tour-next').click();
    await page.waitForSelector('#graph-tour[hidden]', {state:'attached'});
    assert.equal(page.url(), before.url);
    assert.equal(await page.locator('#view-status').textContent(), before.status);
    assert.equal(await page.locator('#detail').textContent(), before.text);
    assert.equal(await page.locator('#tour-launch').evaluate(n => document.activeElement === n), true);
    await page.locator('#tour-launch').click(); await page.selectOption('#tour-step', String(TOUR_STEPS.findIndex(s => s.id === 'tabs')));
    await page.waitForFunction(() => document.getElementById('graph-tour').dataset.step === 'tabs');
    await page.locator('#tour-restart').click();
    await page.waitForFunction(() => document.getElementById('graph-tour').dataset.step === 'examples');
    await page.keyboard.press('Escape');
    await page.waitForSelector('#graph-tour[hidden]', {state:'attached'});
    assert.equal(page.url(), before.url);
    await page.locator('#fullscreen').click(); await page.locator('#workspace-tour').click();
    await page.waitForFunction(() => document.getElementById('graph-tour').dataset.step === 'examples');
    assert.equal(await page.locator('#explorer').evaluate(n => n.classList.contains('is-expanded')), false);
    await page.locator('#tour-close').click();
    await page.waitForSelector('#explorer.is-expanded');
    await page.locator('#fullscreen').click();
    // Use the actual design-system language link, preserving the selected node.
    const selected = new URL(page.url()).searchParams.get('node');
    await page.locator('gcds-header').getByRole('link', { name: 'Français', exact: true }).click(); await ready(page);
    assert.equal(await page.locator('html').getAttribute('lang'), 'fr');
    assert.equal(new URL(page.url()).searchParams.get('node'), selected);
    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    mobile.on('pageerror', e => errors.push(e.message));
    await mobile.goto(base + 'graph.html?lang=fr'); await ready(mobile);
    assert.equal(await mobile.locator('[data-example]').count(), 5);
    await mobile.locator('#tour-launch').click();
    for (let i = 0; i < TOUR_STEPS.length; i++) {
      const step = TOUR_STEPS[i];
      await mobile.selectOption('#tour-step', String(i));
      await mobile.waitForFunction(id => document.getElementById('graph-tour').dataset.step === id && document.querySelector('.tour-card').getAttribute('aria-busy') === 'false', step.id);
      assert.ok(await mobile.locator(step.target).first().isVisible(), `Mobile target: ${step.id}`);
      assert.equal(await mobile.locator('#tour-title').textContent(), step.title_fr);
      const box = await mobile.locator('.tour-card').boundingBox();
      assert.ok(box.x >= 0 && box.y >= 0 && box.x + box.width <= 391 && box.y + box.height <= 845, step.id);
      assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, `Mobile overflow: ${step.id}`);
      if (step.id === 'detail') await mobile.screenshot({ path: output + '/graph-tour-mobile.png' });
    }
    await mobile.locator('#tour-close').click();
    await mobile.screenshot({ path: output + '/graph-examples-mobile.png', fullPage: true });
    const retry = await browser.newPage(); let attempts = 0;
    retry.on('pageerror', e => errors.push(e.message));
    await retry.route('**/graph-attributes/*.json', route => ++attempts === 1 ? route.fulfill({status:503, body:'{}'}) : route.continue());
    await retry.goto(base + 'graph.html?node=' + encodeURIComponent('pib:standard:PSU 905'));
    await retry.locator('.record-attributes button').click();
    await retry.waitForSelector('.record-attributes summary');
    assert.equal(attempts, 2, 'Failed attribute shards can be retried');
    assert.deepEqual(errors, []);
    console.log(`Passed five curated starts, category/type evidence, standard filters, header language switch, fullscreen restoration, and all ${TOUR_STEPS.length} tour stops on desktop and French mobile.`);
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
