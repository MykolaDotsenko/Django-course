import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { gzipSync } from "node:zlib";

import AxeBuilder from "@axe-core/playwright";
import { chromium } from "playwright";

const BASE_URL = process.env.BROWSER_QUALITY_BASE_URL ?? "http://127.0.0.1:8000";
const OUTPUT_DIR = resolve(process.cwd(), "../artifacts/browser-quality");
const BUILD_ASSET_DIR = resolve(process.cwd(), "../static/build/assets");
const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

const SURFACES = [
  { name: "shell", path: "/_design/shell/" },
  { name: "converter", path: "/_design/converter/" },
];

const VIEWPORTS = [
  { name: "wide-1440", width: 1440, height: 1000 },
  { name: "transition-1023", width: 1023, height: 900 },
  { name: "transition-1025", width: 1025, height: 900 },
  { name: "mobile-390", width: 390, height: 844 },
  { name: "reflow-320", width: 320, height: 700 },
];

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function assertNoHorizontalOverflow(page, label) {
  const dimensions = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  assert(
    dimensions.scrollWidth <= dimensions.clientWidth + 1,
    `${label}: horizontal overflow ${dimensions.scrollWidth} > ${dimensions.clientWidth}`,
  );
}

async function assertAxe(page, label) {
  const results = await new AxeBuilder({ page }).withTags(WCAG_TAGS).analyze();
  if (results.violations.length > 0) {
    const details = results.violations
      .map((violation) => {
        const targets = violation.nodes
          .slice(0, 3)
          .flatMap((node) => node.target)
          .join(", ");
        return `${violation.id} [${violation.impact ?? "unknown"}]: ${targets}`;
      })
      .join("\n");
    throw new Error(`${label}: axe found ${results.violations.length} violation(s)\n${details}`);
  }
}

async function assertKeyboardFocus(page, surface) {
  await page.keyboard.press("Tab");
  const first = await page.evaluate(() => ({
    className: document.activeElement?.className ?? "",
    tagName: document.activeElement?.tagName ?? "",
  }));
  assert(
    String(first.className).includes("qa-skip-link"),
    `${surface}: skip link is not the first keyboard target: ${JSON.stringify(first)}`,
  );

  if (surface === "converter") {
    await page.keyboard.press("Tab");
    const activeId = await page.evaluate(() => document.activeElement?.id ?? "");
    assert(
      activeId === "workspace-amount",
      `converter: unexpected second focus target ${activeId}`,
    );
  }
}

async function assertReducedMotion(page, surface) {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const state = await page.evaluate(() => ({
    matches: matchMedia("(prefers-reduced-motion: reduce)").matches,
    runningAnimations: document
      .getAnimations()
      .filter((animation) => animation.playState === "running").length,
  }));
  assert(state.matches, `${surface}: reduced-motion media emulation did not apply`);
  assert(
    state.runningAnimations === 0,
    `${surface}: ${state.runningAnimations} animation(s) still running in reduced-motion mode`,
  );
  await assertNoHorizontalOverflow(page, `${surface}/reduced-motion`);
}

async function assertForcedColors(page, surface) {
  await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
  assert(
    await page.evaluate(() => matchMedia("(forced-colors: active)").matches),
    `${surface}: forced-colors media emulation did not apply`,
  );

  const focusTarget =
    surface === "converter" ? page.locator("#workspace-amount") : page.locator(".qa-skip-link");
  await focusTarget.focus();

  const focusStyles = await focusTarget.evaluate((element) => {
    const candidates = [
      element,
      element.closest(".qa-amount-control"),
      element.closest(".qa-selector-trigger"),
      element.closest(".qa-primary-button"),
      element.closest(".qa-swap-button"),
    ].filter(Boolean);

    return candidates.map((candidate) => {
      const style = getComputedStyle(candidate);
      return {
        outlineStyle: style.outlineStyle,
        outlineWidth: style.outlineWidth,
        boxShadow: style.boxShadow,
      };
    });
  });
  const hasVisibleFocus = focusStyles.some(
    (style) =>
      (style.outlineStyle !== "none" && style.outlineWidth !== "0px") || style.boxShadow !== "none",
  );
  assert(hasVisibleFocus, `${surface}: focus indicator disappears in forced-colors mode`);
  await assertNoHorizontalOverflow(page, `${surface}/forced-colors`);
}

async function assertTextExpansion(page, surface) {
  await page.emulateMedia({ forcedColors: "none", reducedMotion: "reduce" });
  await page.addStyleTag({ content: "html { font-size: 200% !important; }" });
  await assertNoHorizontalOverflow(page, `${surface}/text-200`);

  const clippedInteractive = await page
    .locator("button, input, summary, a")
    .evaluateAll((elements) =>
      elements
        .filter((element) => {
          const style = getComputedStyle(element);
          return (
            element.clientWidth > 0 &&
            element.scrollWidth > element.clientWidth + 1 &&
            style.overflowX === "hidden"
          );
        })
        .map(
          (element) =>
            element.id || element.getAttribute("aria-label") || element.textContent?.trim(),
        )
        .filter(Boolean),
    );
  assert(
    clippedInteractive.length === 0,
    `${surface}: clipped interactive text after expansion: ${clippedInteractive.join(", ")}`,
  );
}

async function assertConverterTransitionLayout(page) {
  const workspace = page.locator(".qa-workspace");
  const source = page.locator(".qa-workspace__context--source");
  const destination = page.locator(".qa-workspace__context--destination");

  for (const state of [
    { width: 767, mode: "compact" },
    { width: 768, mode: "wide" },
    { width: 769, mode: "wide" },
  ]) {
    await workspace.evaluate((element, width) => {
      element.style.width = `${width}px`;
      element.style.maxWidth = "none";
    }, state.width);

    const sourceBox = await source.boundingBox();
    const destinationBox = await destination.boundingBox();
    assert(
      sourceBox && destinationBox,
      `converter/container-${state.width}: bilateral contexts are not measurable`,
    );

    if (state.mode === "compact") {
      assert(
        destinationBox.y > sourceBox.y + 2,
        `converter/container-${state.width}: expected compact stacked bilateral layout`,
      );
    } else {
      assert(
        Math.abs(destinationBox.y - sourceBox.y) <= 2,
        `converter/container-${state.width}: expected wide simultaneous bilateral layout`,
      );
    }
  }

  await workspace.evaluate((element) => {
    element.style.removeProperty("width");
    element.style.removeProperty("max-width");
  });
}

async function collectCompressedAssetEvidence() {
  const names = await readdir(BUILD_ASSET_DIR);
  const javascript = names.filter((name) => name.endsWith(".js")).sort();
  assert(javascript.length > 0, "production build contains no JavaScript assets to measure");
  const files = [];

  for (const name of javascript) {
    const bytes = await readFile(resolve(BUILD_ASSET_DIR, name));
    files.push({
      name,
      rawBytes: bytes.length,
      gzipBytes: gzipSync(bytes, { level: 9 }).length,
    });
  }

  return {
    files,
    totalRawBytes: files.reduce((total, file) => total + file.rawBytes, 0),
    totalGzipBytes: files.reduce((total, file) => total + file.gzipBytes, 0),
  };
}

async function collectPerformance(page) {
  return page.evaluate(() => {
    const resources = performance.getEntriesByType("resource");
    const sum = (entries, key) => entries.reduce((total, entry) => total + (entry[key] || 0), 0);
    const byExtension = (extension) =>
      resources.filter((entry) => new URL(entry.name).pathname.endsWith(extension));
    const navigation = performance.getEntriesByType("navigation")[0];

    return {
      requestCount: resources.length + (navigation ? 1 : 0),
      transferBytes: sum(resources, "transferSize"),
      encodedBodyBytes: sum(resources, "encodedBodySize"),
      jsEncodedBodyBytes: sum(byExtension(".js"), "encodedBodySize"),
      cssEncodedBodyBytes: sum(byExtension(".css"), "encodedBodySize"),
      imageEncodedBodyBytes: resources
        .filter((entry) => ["img", "image"].includes(entry.initiatorType))
        .reduce((total, entry) => total + (entry.encodedBodySize || 0), 0),
      domContentLoadedMs: navigation
        ? Math.round(navigation.domContentLoadedEventEnd - navigation.startTime)
        : null,
      loadMs: navigation ? Math.round(navigation.loadEventEnd - navigation.startTime) : null,
    };
  });
}

async function openSurface(page, surface) {
  const response = await page.goto(`${BASE_URL}${surface.path}`, { waitUntil: "networkidle" });
  assert(
    response?.ok(),
    `${surface.name}: request failed with ${response?.status() ?? "no response"}`,
  );
  const h1Count = await page.locator("h1").count();
  assert(h1Count === 1, `${surface.name}: expected exactly one H1, found ${h1Count}`);
}

await mkdir(OUTPUT_DIR, { recursive: true });
const browser = await chromium.launch();
const evidence = {
  generatedAt: new Date().toISOString(),
  surfaces: {},
  budgets: {
    coreJavaScriptGzipBytes: 100 * 1024,
    source: "docs/36_PERFORMANCE_BUDGETS_AND_PROFILING.md",
  },
};

try {
  for (const surface of SURFACES) {
    evidence.surfaces[surface.name] = {};

    for (const viewport of VIEWPORTS) {
      const context = await browser.newContext({
        viewport: { width: viewport.width, height: viewport.height },
        deviceScaleFactor: 1,
      });
      const page = await context.newPage();
      const consoleErrors = [];
      page.on("console", (message) => {
        if (message.type() === "error") consoleErrors.push(message.text());
      });

      await openSurface(page, surface);
      await assertNoHorizontalOverflow(page, `${surface.name}/${viewport.name}`);
      await assertKeyboardFocus(page, surface);

      if (viewport.name === "wide-1440" || viewport.name === "mobile-390") {
        await assertAxe(page, `${surface.name}/${viewport.name}`);
      }

      if (surface.name === "converter" && viewport.name === "wide-1440") {
        await assertConverterTransitionLayout(page);
      }

      if (viewport.name === "mobile-390") {
        await assertReducedMotion(page, surface.name);
        await assertForcedColors(page, surface.name);
      }

      if (viewport.name === "reflow-320") {
        await assertTextExpansion(page, surface.name);
      }

      assert(
        consoleErrors.length === 0,
        `${surface.name}/${viewport.name}: console errors: ${consoleErrors.join(" | ")}`,
      );

      const performanceEvidence = await collectPerformance(page);
      evidence.surfaces[surface.name][viewport.name] = performanceEvidence;

      await page.screenshot({
        path: resolve(OUTPUT_DIR, `${surface.name}-${viewport.name}.png`),
        fullPage: true,
      });
      await context.close();
    }
  }

  evidence.compressedAssets = await collectCompressedAssetEvidence();
  assert(
    evidence.compressedAssets.totalGzipBytes <= evidence.budgets.coreJavaScriptGzipBytes,
    `core JavaScript gzip size ${evidence.compressedAssets.totalGzipBytes} B exceeds 100 KiB budget`,
  );

  await writeFile(
    resolve(OUTPUT_DIR, "performance-evidence.json"),
    `${JSON.stringify(evidence, null, 2)}\n`,
    "utf8",
  );
} finally {
  await browser.close();
}
