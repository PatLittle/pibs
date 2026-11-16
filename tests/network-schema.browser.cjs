const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const model = JSON.parse(fs.readFileSync("site/data/network-schema.json"));
const base = process.env.GRAPH_TEST_BASE || "http://127.0.0.1:8766/";
(async () => {
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.BROWSER_EXECUTABLE,
    args: ["--no-sandbox"],
  });
  try {
    const page = await browser.newPage({
        viewport: { width: 1500, height: 1000 },
      }),
      errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(base + "data-model.html", {
      waitUntil: "domcontentloaded",
    });
    await page.waitForSelector("#schema-canvas svg");
    assert.equal(
      await page.locator("svg [data-table]").count(),
      model.tables.length,
    );
    assert.equal(
      await page.locator("svg [data-field]").count(),
      model.summary.fields,
    );
    assert.equal(
      await page.locator("#schema-tables>details").count(),
      model.tables.length,
    );
    await page.locator("#schema-search").fill("ADMresponsible");
    assert.ok((await page.locator("#schema-results button").count()) >= 2);
    const before = await page
      .locator("#schema-canvas svg")
      .getAttribute("viewBox");
    await page.locator("#schema-results button").first().click();
    assert.notEqual(
      await page.locator("#schema-canvas svg").getAttribute("viewBox"),
      before,
    );
    const v = (await page.locator("#schema-canvas svg").getAttribute("viewBox"))
      .split(" ")
      .map(Number);
    const box = await page
      .locator('svg [data-table="aia_answers"] [data-field="ADMresponsible"]')
      .evaluate((n) => ({ x: n.getBBox().x, y: n.getBBox().y }));
    assert.ok(
      box.x >= v[0] &&
        box.x < v[0] + v[2] &&
        box.y >= v[1] &&
        box.y < v[1] + v[3],
    );
    await page.keyboard.press("+");
    assert.notEqual(
      await page.locator("#schema-canvas svg").getAttribute("viewBox"),
      v.join(" "),
    );
    await page.locator("#schema-fit").click();
    assert.equal(
      await page.locator("#schema-canvas svg").getAttribute("viewBox"),
      before,
    );
    await page.setViewportSize({ width: 390, height: 844 });
    assert.ok(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    );
    assert.deepEqual(errors, []);
    console.log(
      "Passed full model diagram: every table and field drawn, searchable, zoomable, keyboard accessible and mobile width.",
    );
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
