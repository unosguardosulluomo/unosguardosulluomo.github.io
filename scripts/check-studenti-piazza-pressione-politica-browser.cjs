"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [baseUrl, executablePath, outputDir] = process.argv.slice(2);
if (!baseUrl || !executablePath || !outputDir) {
  throw new Error("Usage: check-studenti-piazza-pressione-politica-browser.cjs BASE_URL BROWSER_EXE OUTPUT_DIR");
}
fs.mkdirSync(outputDir, { recursive: true });

async function inspect(browser, name, viewport, url, screenshot) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  const errors = [];
  page.on("console", message => {
    if (message.type() === "error") errors.push(message.text());
  });
  page.on("pageerror", error => errors.push(error.message));
  const response = await page.goto(baseUrl + url, { waitUntil: "networkidle" });
  if (!response || !response.ok()) throw new Error(`${name}: HTTP ${response && response.status()}`);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    for (const image of document.querySelectorAll("img[loading='lazy']")) {
      image.loading = "eager";
      image.src = image.getAttribute("src");
      image.scrollIntoView({ block: "center" });
      await new Promise(resolve => setTimeout(resolve, 120));
    }
    window.scrollTo(0, 0);
  });
  await page.waitForFunction(() => [...document.images].every(image => image.complete), null, { timeout: 10000 });
  await page.waitForTimeout(200);
  const result = await page.evaluate(() => ({
    innerWidth: window.innerWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    title: document.title,
    h1: document.querySelector("h1")?.textContent.trim(),
    tables: document.querySelectorAll("table.data-table").length,
    sources: document.querySelectorAll(".sources-list li").length,
    related: document.querySelectorAll(".related-dossiers li").length,
    images: [...document.images].map(image => ({
      src: image.getAttribute("src"), complete: image.complete,
      naturalWidth: image.naturalWidth, renderedWidth: image.getBoundingClientRect().width,
    })),
  }));
  if (result.scrollWidth > result.clientWidth + 1) throw new Error(`${name}: horizontal overflow ${result.scrollWidth}/${result.clientWidth}`);
  for (const image of result.images) {
    if (/^https?:\/\//.test(image.src || "")) continue;
    if (!image.complete || image.naturalWidth === 0 || image.renderedWidth <= 0) {
      throw new Error(`${name}: broken image ${JSON.stringify(image)}`);
    }
  }
  if (url.includes("dissenso-violenza")) {
    if (result.tables !== 9 || result.sources !== 63 || result.related !== 3) {
      throw new Error(`${name}: incomplete dossier ${JSON.stringify(result)}`);
    }
  }
  const actionableErrors = errors.filter(error => !error.includes("ERR_BLOCKED_BY_RESPONSE.NotSameOrigin"));
  if (actionableErrors.length) throw new Error(`${name}: console errors ${actionableErrors.join(" | ")}`);
  if (screenshot) {
    await page.screenshot({ path: path.join(outputDir, screenshot), fullPage: true });
    if (url.includes("dissenso-violenza")) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.screenshot({ path: path.join(outputDir, `${name}-top.png`) });
      const firstTable = page.locator("table.data-table").first();
      await firstTable.scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(outputDir, `${name}-table.png`) });
      const politicsHeading = page.getByRole("heading", { name: "La condanna che dura una frase" });
      await politicsHeading.scrollIntoViewIfNeeded();
      await page.screenshot({ path: path.join(outputDir, `${name}-politica.png`) });
    }
  }
  await page.close();
  return result;
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const article = "/article-geopolitica-politica-italiana-dissenso-violenza-autoalimentata-studenti.html";
    const results = [];
    results.push(await inspect(browser, "article-desktop", { width: 1440, height: 900 }, article, "article-desktop-full.png"));
    results.push(await inspect(browser, "article-mobile", { width: 390, height: 844 }, article, "article-mobile-full.png"));
    results.push(await inspect(browser, "home-mobile", { width: 390, height: 844 }, "/", "home-mobile-full.png"));
    results.push(await inspect(browser, "indagini-mobile", { width: 390, height: 844 }, "/indagini.html"));
    results.push(await inspect(browser, "archive-mobile", { width: 390, height: 844 }, "/archivio-politica-italiana.html"));
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error.stack || error);
  process.exit(1);
});
