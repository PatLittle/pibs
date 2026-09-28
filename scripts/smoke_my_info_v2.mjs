// Optional browser verification. Serve site/ first; requires Puppeteer + Chromium.
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import puppeteer from "puppeteer";

const base = process.env.MY_INFO_PREVIEW_URL || "http://localhost:8766";
const screenshots = fs.mkdtempSync(path.join(os.tmpdir(), "my-info-v2-review-"));
const browser = await puppeteer.launch({executablePath:process.env.CHROMIUM_PATH || "/snap/bin/chromium", headless:true, args:["--no-sandbox"]});
const page = await browser.newPage();
const errors = [];
page.on("pageerror", error=>errors.push(error.message));
const fresh = async () => {await page.goto(`${base}/my_info_v2/`); await page.waitForSelector("[data-activity]");};
const select = async id => {
  await page.evaluate(id=>document.querySelector(`[data-activity="${id}"]`).closest("details").open=true,id);
  await page.click(`[data-activity="${id}"]`);
};
const text = () => page.$eval("#panel", e=>e.textContent);
try {
  await page.setViewport({width:1280,height:950});
  await fresh();
  await select("veterans_education");
  await page.click('[data-action="find"]');
  assert.equal(await page.$("#scope-filter"),null);
  assert.match(await text(),/VAC PPU 710/);
  assert.doesNotMatch(await text(),/VAC PPU 200/);
  assert.ok(await page.$('.card a[href^="https://"]'));
  await page.screenshot({path:path.join(screenshots,"veterans-results.png"),fullPage:true});

  await fresh();
  await select("caf_regular_service");
  await page.click('[data-action="find"]');
  assert.equal(await page.$("#scope-filter"),null);
  await page.click("#refine");
  assert.match(await text(),/released/i);
  await page.type("#date-year","2000");
  await page.click("#date-save");
  assert.match(await text(),/May now be held by Library and Archives Canada/);

  await fresh();
  await page.click("#common");
  assert.equal(await page.$$eval('[data-activity]:checked',els=>els.length),4);
  await select("nexus");
  await page.click('[data-action="find"]');
  assert.match(await text(),/CBSA PPU 031/);
  assert.match(await text(),/ELECTIONS PPU 037/);
  await page.click("#language");
  assert.equal(await page.$eval("html",e=>e.lang),"fr");
  assert.match(await text(),/Vos pistes de dossiers/);
  await page.setViewport({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.screenshot({path:path.join(screenshots,"french-mobile-results.png"),fullPage:true});

  await fresh();
  await select("access_request");
  await page.click('[data-action="find"]');
  assert.ok(await page.$("#scope-filter"));
  await page.type("#scope-filter","Border Services");
  await page.click('[data-scope="ati-schedule-i-canada-border-services-agency"]');
  await page.click("#scope-continue");
  assert.match(await text(),/PSU 901/);
  assert.match(await text(),/Canada Border Services Agency/);

  await fresh();
  await page.click('[data-view="directory"]');
  await page.type("#record-search","CSA PPU 020");
  assert.match(await page.$eval("#directory-count",e=>e.textContent),/^1 /);
  assert.match(await page.$eval("#live-status",e=>e.textContent),/0 directory records/);
  await page.click(".card summary");
  await page.click("[data-record]");
  await page.click('[data-action="find"]');
  assert.match(await text(),/CSA PPU 020/);
  assert.match(await text(),/Added after you reviewed/);

  await fresh();
  await select("tax_return");
  await page.click('[data-action="find"]');
  assert.doesNotMatch(await text(),/No activities have been selected/);
  assert.match(await text(),/Canada Revenue Agency/);
  await fresh();
  await page.setViewport({width:1280,height:950});
  await page.screenshot({path:path.join(screenshots,"activity-picker.png"),fullPage:true});
  await page.goto(`${base}/my_info_compare/`);
  await page.screenshot({path:path.join(screenshots,"comparison.png"),fullPage:true});
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({status:"passed",scenarios:7,screenshots},null,2));
} finally {await browser.close();}
