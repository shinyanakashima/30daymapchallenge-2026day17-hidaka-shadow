// Visual check: console errors, failed requests, and the screenshot used in the README.
// Usage: node scripts/check_site.mjs [base_url] (default http://localhost:8000/)
import { createRequire } from "module";
const { chromium } = createRequire(import.meta.url)("playwright");

const base = process.argv[2] || "http://localhost:8000/";
const browser = await chromium.launch();
const problems = [];

async function open(url, opts = {}) {
  const page = await browser.newPage({ viewport: opts.viewport || { width: 1200, height: 900 }, deviceScaleFactor: 1, ...opts.ctx });
  page.on("console", (m) => { if (m.type() === "error") problems.push(`console: ${m.text()} @ ${url}`); });
  page.on("pageerror", (e) => problems.push(`pageerror: ${e.message} @ ${url}`));
  page.on("response", (r) => { if (r.status() >= 400) problems.push(`${r.status()} ${r.url()}`); });
  page.on("requestfailed", (r) => problems.push(`failed ${r.url()} ${r.failure()?.errorText}`));
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  return page;
}

// Winter solstice, 14 minutes before the flat-horizon sunset in Obihiro.
const p1 = await open(`${base}?date=winter&t=76`);
await p1.screenshot({ path: "docs/screenshot.png" });
console.log("headline:", await p1.textContent("#headline"));
console.log("clock:", await p1.textContent("#clock"));

// Interactions
await p1.click('#views button[data-view="taken"]');
await p1.mouse.click(760, 450);
await p1.waitForTimeout(500);
console.log("info:", (await p1.textContent("#info")).replace(/\s+/g, " ").trim());
await p1.click("#lang");
console.log("ja headline:", await p1.textContent("#headline"));
for (const d of ["equinox", "summer", "today"]) {
  await p1.click(`#dates button[data-date="${d}"]`);
  await p1.waitForTimeout(800);
}
await p1.screenshot({ path: "data/check_taken.png" });

// Phone
const p2 = await open(`${base}?date=winter&t=80`, { viewport: { width: 390, height: 844 }, ctx: { isMobile: true, hasTouch: true, deviceScaleFactor: 2 } });
await p2.screenshot({ path: "data/check_phone.png" });
const overflow = await p2.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
if (overflow) problems.push("horizontal overflow on phone");

// Reduced motion: must not autoplay
const ctx = await browser.newContext({ reducedMotion: "reduce", viewport: { width: 1200, height: 900 } });
const p3 = await ctx.newPage();
await p3.goto(base, { waitUntil: "networkidle" });
const f0 = await p3.inputValue("#slider");
await p3.waitForTimeout(1500);
const f1 = await p3.inputValue("#slider");
if (f0 !== f1) problems.push("autoplay under reduced motion");

await browser.close();
if (problems.length) { console.error(problems.join("\n")); process.exit(1); }
console.log("OK: no console errors, no failed requests");
