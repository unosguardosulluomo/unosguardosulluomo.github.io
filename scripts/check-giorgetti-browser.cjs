"use strict";

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [baseUrl, executablePath, outputDir] = process.argv.slice(2);
if (!baseUrl || !executablePath || !outputDir) {
  throw new Error("Usage: check-giorgetti-browser.cjs BASE_URL BROWSER_EXE OUTPUT_DIR");
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
    for (let y = 0; y < document.documentElement.scrollHeight; y += Math.max(400, window.innerHeight * 0.8)) {
      window.scrollTo(0, y);
      await new Promise(resolve => setTimeout(resolve, 40));
    }
    window.scrollTo(0, document.documentElement.scrollHeight);
  });
  await page.waitForTimeout(250);
  const result = await page.evaluate(() => ({
    innerWidth: window.innerWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    title: document.title,
    h1: document.querySelector("h1")?.textContent.trim(),
    images: [...document.images].map(image => ({
      src: image.getAttribute("src"), complete: image.complete,
      naturalWidth: image.naturalWidth, renderedWidth: image.getBoundingClientRect().width,
    })),
  }));
  if (result.scrollWidth > result.clientWidth + 1) throw new Error(`${name}: horizontal overflow ${result.scrollWidth}/${result.clientWidth}`);
  for (const image of result.images) {
    if (/^https?:\/\//.test(image.src || "")) continue;
    if (!/(?:giorgetti|testata)/.test(image.src || "")) continue;
    if (!image.complete || image.naturalWidth === 0 || image.renderedWidth <= 0) {
      throw new Error(`${name}: broken image ${JSON.stringify(image)}`);
    }
  }
  if (errors.length) throw new Error(`${name}: console errors ${errors.join(" | ")}`);
  if (screenshot) await page.screenshot({ path: path.join(outputDir, screenshot), fullPage: true });
  await page.close();
  return result;
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath });
  try {
    const results = [];
    results.push(await inspect(browser, "article-desktop", { width: 1440, height: 900 }, "/article-giorgetti-pallottoliere.html", "article-desktop-full.png"));
    results.push(await inspect(browser, "article-mobile", { width: 390, height: 844 }, "/article-giorgetti-pallottoliere.html", "article-mobile-full.png"));
    results.push(await inspect(browser, "home-mobile", { width: 390, height: 844 }, "/", "home-mobile-full.png"));
    results.push(await inspect(browser, "indagini-mobile", { width: 390, height: 844 }, "/indagini.html"));
    results.push(await inspect(browser, "archive-mobile", { width: 390, height: 844 }, "/archivio-economia.html"));
    console.log(JSON.stringify(results, null, 2));
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error.stack || error);
  process.exit(1);
});
