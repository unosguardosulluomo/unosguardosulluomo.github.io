"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [baseUrl, executablePath, outputDir] = process.argv.slice(2);
if (!baseUrl || !executablePath || !outputDir) {
  throw new Error("Usage: check-search-browser.cjs BASE_URL BROWSER_EXE OUTPUT_DIR");
}
fs.mkdirSync(outputDir, { recursive: true });

async function inspect(browser, name, viewport) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  const errors = [];
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", (error) => errors.push(error.message));

  const response = await page.goto(`${baseUrl}/ricerca-indagini.html`, { waitUntil: "networkidle" });
  if (!response || !response.ok()) throw new Error(`${name}: HTTP ${response && response.status()}`);

  const initial = await page.evaluate(() => ({
    count: document.querySelector("#search-count")?.textContent.trim(),
    cards: document.querySelectorAll(".search-result").length,
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    navLinks: document.querySelectorAll("nav.nav a").length,
    formRight: document.querySelector(".search-controls")?.getBoundingClientRect().right,
    viewportWidth: window.innerWidth,
  }));
  if (initial.cards !== 51 || initial.count !== "51 indagini") {
    throw new Error(`${name}: archivio incompleto (${initial.cards}, ${initial.count})`);
  }
  if (initial.navLinks !== 6) throw new Error(`${name}: navigazione incompleta`);
  if (initial.scrollWidth > initial.clientWidth + 1) {
    throw new Error(`${name}: overflow orizzontale ${initial.scrollWidth}/${initial.clientWidth}`);
  }
  if (initial.formRight > initial.viewportWidth + 1) {
    throw new Error(`${name}: modulo oltre il viewport ${initial.formRight}/${initial.viewportWidth}`);
  }

  await page.locator("#search-query").fill("Schlein");
  await page.waitForTimeout(100);
  const queryResult = await page.evaluate(() => ({
    count: document.querySelector("#search-count")?.textContent.trim(),
    campoLargoVisible: !document.querySelector('[data-dossier="article-geopolitica-politica-italiana-schlein-conte-primarie-campo-largo.html"]')?.hidden,
  }));
  if (!queryResult.campoLargoVisible || queryResult.count === "0 indagini") {
    throw new Error(`${name}: ricerca testuale non funzionante`);
  }

  await page.locator("#search-query").fill("");
  await page.locator("#search-category").selectOption("Economia");
  await page.waitForTimeout(100);
  const wrongCategory = await page.locator('.search-result:not([hidden]):not([data-category="Economia"])').count();
  if (wrongCategory) throw new Error(`${name}: filtro categoria non funzionante`);

  await page.locator("#search-reset").click();
  await page.waitForTimeout(100);
  const resetCount = await page.locator(".search-result:not([hidden])").count();
  if (resetCount !== 51) throw new Error(`${name}: azzeramento filtri non funzionante`);

  if (errors.length) throw new Error(`${name}: errori console ${errors.join(" | ")}`);
  await page.screenshot({ path: path.join(outputDir, `${name}.png`) });
  await page.close();
  return { name, ...initial, queryCount: queryResult.count, resetCount };
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const results = [];
    results.push(await inspect(browser, "search-desktop", { width: 1440, height: 900 }));
    results.push(await inspect(browser, "search-tablet", { width: 820, height: 900 }));
    results.push(await inspect(browser, "search-mobile", { width: 390, height: 844 }));
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
