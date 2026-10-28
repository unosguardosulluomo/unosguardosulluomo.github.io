"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [baseUrl, executablePath, outputDir] = process.argv.slice(2);
if (!baseUrl || !executablePath || !outputDir) {
  throw new Error("Usage: check-salvini-salvezza-browser.cjs BASE_URL BROWSER_EXE OUTPUT_DIR");
}
fs.mkdirSync(outputDir, { recursive: true });

async function inspect(browser, name, viewport, url, screenshot) {
  const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));
  const response = await page.goto(baseUrl + url, { waitUntil: "networkidle" });
  if (!response || !response.ok()) throw new Error(`${name}: HTTP ${response && response.status()}`);
  await page.evaluate(async () => {
    await document.fonts.ready;
    for (const image of document.images) image.loading = "eager";
    window.scrollTo(0, document.documentElement.scrollHeight);
    await new Promise(resolve => setTimeout(resolve, 100));
    window.scrollTo(0, 0);
  });
  await page.waitForFunction(() => [...document.images].every(image => image.complete), null, { timeout: 15000 });
  const result = await page.evaluate(() => ({
    h1: document.querySelector("h1")?.textContent.trim(),
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    sources: document.querySelectorAll(".sources-list li").length,
    sourceLinks: document.querySelectorAll(".sources-list a").length,
    related: document.querySelectorAll(".related-dossiers li").length,
    figures: document.querySelectorAll("figure").length,
    captions: [...document.querySelectorAll("figure figcaption")].map(node => node.textContent.trim()),
    brokenImages: [...document.images]
      .filter(image => !image.naturalWidth && !/^https?:/i.test(image.getAttribute("src") || ""))
      .map(image => image.getAttribute("src")),
  }));
  if (result.scrollWidth > result.clientWidth + 1) throw new Error(`${name}: horizontal overflow ${result.scrollWidth}/${result.clientWidth}`);
  if (result.brokenImages.length) throw new Error(`${name}: broken images ${result.brokenImages.join(", ")}`);
  if (url.includes("salvini-salvezza-lega")) {
    if (result.h1 !== "SALVINI E LA SALVEZZA CHE ANCORA NON ARRIVA…" || result.sources !== 18 || result.sourceLinks !== 0 || result.related !== 3 || result.figures !== 2 || result.captions.some(value => value !== "Immagine prodotta da Uno Sguardo sull'Uomo")) {
      throw new Error(`${name}: incomplete dossier ${JSON.stringify(result)}`);
    }
  }
  const actionableErrors = errors.filter(error => !error.includes("ERR_BLOCKED_BY_RESPONSE.NotSameOrigin"));
  if (actionableErrors.length) throw new Error(`${name}: console errors ${actionableErrors.join(" | ")}`);
  if (screenshot) await page.screenshot({ path: path.join(outputDir, screenshot), fullPage: false });
  await page.close();
  return result;
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const article = "/article-geopolitica-politica-italiana-salvini-salvezza-lega.html";
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
})().catch(error => { console.error(error.stack || error); process.exit(1); });
