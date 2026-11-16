const { chromium } = require("playwright");
const { mkdirSync, readFileSync } = require("node:fs");
const assert = require("node:assert/strict");
const base = process.env.GRAPH_TEST_BASE || "http://127.0.0.1:8766/",
  out = process.env.GRAPH_TEST_OUTPUT || "/tmp/pibs-focus-check";
mkdirSync(out, { recursive: true });
const aiaURL = JSON.parse(readFileSync("site/aia-source.json")).url;
const bank = "pib:standard:PSU 905",
  uuid = "11111111-1111-4111-8111-111111111111";
const fixture = {
  package_id: uuid,
  title_en: "Fixture Algorithmic Assessment",
  title_fr: "Évaluation algorithmique de test",
  organization_en: "Treasury Board of Canada Secretariat",
  organization_fr: "Secrétariat du Conseil du Trésor du Canada",
  dataset_url: "https://example.test/dataset/" + uuid,
  version: "v1.0.1",
  source: "published",
  data: {
    ADMresponsible: "Example Official",
    aboutDataSource12: "PSU 905",
    projectDetailsDescription: "Synthetic browser fixture.",
  },
  translationsOnResult: { ADMresponsible: "Example Official" },
  derived: { impact_level: 2 },
};
(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.BROWSER_EXECUTABLE,
    args: ["--no-sandbox"],
  });
  try {
    const context = await browser.newContext({
      viewport: { width: 1500, height: 1000 },
    });
    await context.route(aiaURL, (r) =>
      r.fulfill({
        status: 200,
        body: JSON.stringify(fixture) + "\n",
        headers: { "access-control-allow-origin": "*" },
      }),
    );
    const page = await context.newPage(),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(base + "graph.html", { waitUntil: "domcontentloaded" });
    await page.waitForSelector("#stories .story");
    assert.equal(await page.locator("#stories .story").count(), 3);
    assert.equal(await page.locator("#exploration").isHidden(), true);
    assert.equal(
      await page
        .locator("#node-type,#relation,#fullscreen,#tour-launch,#browser-panel")
        .count(),
      0,
      "No independent navigation modes or diagram settings",
    );
    assert.ok(
      !(await page.locator("gcds-header").textContent()).includes("navPia"),
    );
    await page.locator("#stories .story").first().click();
    await page.waitForSelector('[data-attribute="pib_type_details"]');
    assert.equal(new URL(page.url()).searchParams.get("node"), bank);
    assert.equal(await page.locator("#detail details[open]").count(), 0);
    assert.equal(
      await page.locator('.connection-group[data-node-type="pia"]').count(),
      1,
    );
    assert.equal(
      await page.locator('.connection-group[data-node-type="aia"]').count(),
      1,
    );
    assert.equal(
      await page.locator("#map-links path").count(),
      await page.locator(".connection-group").count(),
    );
    const group = page.locator('.connection-group[data-node-type="pia"]'),
      before = await group.locator("li").count();
    await group.locator(".more-connections").click();
    assert.ok((await group.locator("li").count()) > before);
    assert.equal(new URL(page.url()).searchParams.get("node"), bank);
    await group.locator(".evidence-button").first().click();
    assert.equal(
      await page.locator(".edge-evidence").evaluate((n) => n.open),
      false,
    );
    await page.locator(".edge-evidence>summary").click();
    await page.waitForSelector(".graph-evidence blockquote");
    assert.ok(await page.locator('.graph-evidence a[href*="#L"]').count());
    const evidenceURL = page.url();
    await page.reload();
    await page.locator(".edge-evidence>summary").click();
    await page.waitForSelector(".graph-evidence blockquote");
    assert.equal(page.url(), evidenceURL);
    await page
      .locator('.connection-group[data-node-type="pia"] .connection-title')
      .first()
      .click();
    assert.equal(await page.locator("#trail button").count(), 2);
    const target = new URL(page.url()).searchParams.get("node");
    assert.notEqual(target, bank);
    await page.locator("#back").click();
    assert.equal(new URL(page.url()).searchParams.get("node"), bank);
    await page.locator(".bridge-proof").first().click();
    assert.equal(await page.locator(".path-evidence").count(), 2);
    await page.locator(".path-evidence .edge-evidence>summary").first().click();
    await page.waitForSelector(".path-evidence .graph-evidence");
    await page.locator(".bridge-target").first().click();
    assert.equal(await page.locator("#trail button").count(), 3);
    const pathURL = page.url(),
      pathTitle = await page.locator("#focus-heading").textContent();
    await page.reload();
    await page.waitForSelector("#focus-heading");
    assert.equal(await page.locator("#focus-heading").textContent(), pathTitle);
    assert.equal(await page.locator("#trail button").count(), 3);
    assert.equal(page.url(), pathURL);
    await page.locator("#toggle-panel").click();
    assert.equal(await page.locator("#inspector").isVisible(), false);
    assert.equal(await page.locator("#connection-groups").isVisible(), true);
    await page.locator("#toggle-panel").click();
    assert.equal(await page.locator("#inspector").isVisible(), true);
    await page.locator("#search").fill("Fixture Algorithmic");
    await page.locator("#results button").first().click();
    assert.equal(new URL(page.url()).searchParams.get("node"), "aia:" + uuid);
    assert.ok(
      (await page.locator("#detail").textContent()).includes(
        "Example Official",
      ),
    );
    assert.equal(await page.locator("#detail details[open]").count(), 0);
    await page.screenshot({ path: out + "/focus-desktop.png", fullPage: true });
    await page
      .locator("gcds-header")
      .getByText("Français", { exact: true })
      .click();
    await page.waitForSelector("#focus-heading");
    assert.equal(await page.locator("html").getAttribute("lang"), "fr");
    assert.equal(new URL(page.url()).searchParams.get("node"), "aia:" + uuid);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator("#close-panel").click();
    assert.equal(await page.locator("#inspector").isVisible(), false);
    await page.locator(".connection-title").first().click();
    assert.equal(await page.locator("#inspector").isVisible(), true);
    assert.equal(await page.locator("#detail details[open]").count(), 0);
    await page.locator("#close-panel").click();
    assert.ok(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    );
    await page.screenshot({
      path: out + "/focus-mobile-fr.png",
      fullPage: true,
    });
    const fail = await context.newPage();
    await fail.route("**/data/graph.json", (r) =>
      r.fulfill({ status: 503, body: "{}" }),
    );
    await fail.goto(base + "graph.html");
    await fail.waitForSelector('#load-status[role="alert"]');
    const outage = await context.newPage();
    await outage.route(aiaURL, (r) => r.abort());
    await outage.goto(base + "graph.html?node=" + encodeURIComponent(bank));
    await outage.waitForSelector("#focus-heading");
    assert.ok(
      (await outage.locator("#load-status").textContent()).includes(
        "unavailable",
      ),
    );
    assert.ok(await outage.locator(".connection-group").count());
    await outage.goto(base + "graph.html?node=unknown-node");
    await outage.waitForSelector("#stories .story");
    assert.ok(
      (await outage.locator("#load-status").textContent()).includes(
        "not in the current collection",
      ),
    );
    assert.deepEqual(errors, []);
    console.log(
      "Passed: simple landing, complete typed connections, source evidence, continuation, valid two-step paths, URL/history, AIA names, collapsed attributes, panel toggle, French mobile, missing feed/record and load failure.",
    );
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
