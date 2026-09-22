import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { gzipSync } from "node:zlib";

import AxeBuilder from "@axe-core/playwright";
import { chromium, firefox, webkit } from "playwright";

const BASE_URL = process.env.BROWSER_QUALITY_BASE_URL ?? "http://127.0.0.1:8000";
const BROWSER_ENGINE = process.env.BROWSER_QUALITY_ENGINE ?? "chromium";
const BROWSER_SCOPE = process.env.BROWSER_QUALITY_SCOPE ?? "full";
const BROWSER_TYPES = { chromium, firefox, webkit };
const browserType = BROWSER_TYPES[BROWSER_ENGINE];
assertBrowserConfiguration();
const OUTPUT_DIR = resolve(process.cwd(), "../artifacts/browser-quality");
const BUILD_ASSET_DIR = resolve(process.cwd(), "../static/build/assets");
const BUILD_MANIFEST_PATH = resolve(process.cwd(), "../static/build/.vite/manifest.json");
const VITE_ENTRY = "frontend/src/app.ts";
const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const LOCAL_STATE_KEY = "cultural-currency:local-preferences:v1";

const SURFACES = [
  { name: "shell", path: "/_design/shell/" },
  { name: "converter", path: "/_design/converter/" },
  { name: "current-converter", path: "/" },
  { name: "saved-state", path: "/saved/" },
  { name: "rate-series", path: "/_design/rate-series/" },
];

function assertBrowserConfiguration() {
  if (!browserType) {
    throw new Error(`Unsupported browser engine: ${BROWSER_ENGINE}`);
  }
  if (!["full", "smoke"].includes(BROWSER_SCOPE)) {
    throw new Error(`Unsupported browser quality scope: ${BROWSER_SCOPE}`);
  }
}

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
  const dimensions = await page.evaluate(() => {
    const clientWidth = document.documentElement.clientWidth;
    const offenders = [...document.querySelectorAll("body *")]
      .map((element) => {
        const rect = element.getBoundingClientRect();
        return {
          tag: element.tagName.toLowerCase(),
          id: element.id,
          className: typeof element.className === "string" ? element.className.trim() : "",
          left: Math.round(rect.left),
          right: Math.round(rect.right),
          width: Math.round(rect.width),
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
        };
      })
      .filter(
        (element) =>
          element.right > clientWidth + 1 ||
          element.left < -1 ||
          element.scrollWidth > element.clientWidth + 1,
      )
      .sort(
        (a, b) =>
          Math.max(b.right - clientWidth, b.scrollWidth - b.clientWidth) -
          Math.max(a.right - clientWidth, a.scrollWidth - a.clientWidth),
      )
      .slice(0, 5);

    return {
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth,
      offenders,
    };
  });
  assert(
    dimensions.scrollWidth <= dimensions.clientWidth + 1,
    `${label}: horizontal overflow ${dimensions.scrollWidth} > ${dimensions.clientWidth}; offenders: ${JSON.stringify(dimensions.offenders)}`,
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

  if (surface === "converter" || surface === "current-converter") {
    await page.keyboard.press("Tab");
    const activeId = await page.evaluate(() => document.activeElement?.id ?? "");
    const expected = surface === "converter" ? "workspace-amount" : "id_amount";
    assert(activeId === expected, `${surface}: unexpected second focus target ${activeId}`);

    if (surface === "current-converter") {
      for (const expectedId of [
        "source-picker-trigger",
        "swap-contexts",
        "destination-picker-trigger",
        "id_rate_mode_0",
      ]) {
        await page.keyboard.press("Tab");
        const nextId = await page.evaluate(() => document.activeElement?.id ?? "");
        assert(
          nextId === expectedId,
          `current-converter: expected focus on ${expectedId}, got ${nextId}`,
        );
      }
    }
  }
}

async function assertCurrentConverterFlow(page, consoleErrors) {
  const waitForPost = () =>
    page.waitForResponse(
      (response) =>
        response.request().method() === "POST" && new URL(response.url()).pathname === "/",
    );

  await page.locator("#id_amount").fill("-1");
  const invalidSubmit = waitForPost();
  await page.locator(".qa-primary-button").click();
  const invalidSubmitResponse = await invalidSubmit;
  assert(
    invalidSubmitResponse.status() === 422,
    `current-converter: invalid submit returned ${invalidSubmitResponse.status()} instead of 422`,
  );
  await page.getByText("Enter zero or a positive amount.").waitFor();

  await page.locator("#source-picker-trigger").click();
  const sourceDialog = page.locator('[data-picker-dialog="source"]');
  const viewport = page.viewportSize();
  if (viewport && viewport.width <= 480) {
    const dialogBox = await sourceDialog.boundingBox();
    assert(
      dialogBox &&
        dialogBox.x <= 1 &&
        dialogBox.y <= 1 &&
        Math.abs(dialogBox.width - viewport.width) <= 2 &&
        Math.abs(dialogBox.height - viewport.height) <= 2,
      "current-converter/mobile: picker must use the full viewport",
    );
  }

  const search = page.locator("#source-picker-search");
  await page.locator("#source-picker-listbox").waitFor();
  await page.waitForFunction(() => {
    const first = document.querySelector("#source-picker-listbox [data-picker-option]");
    return (
      first?.getAttribute("data-country-code") === "FI" &&
      first?.getAttribute("data-currency-code") === "EUR" &&
      first.textContent?.includes("Current selection")
    );
  });
  await search.fill("JPY");
  await page.locator("#source-picker-listbox").waitFor();
  await page.waitForFunction(() => {
    const list = document.querySelector("#source-picker-listbox");
    if (!(list instanceof HTMLElement) || list.dataset.commitWired !== "true") return false;
    const options = Array.from(list.querySelectorAll("[data-picker-option]"));
    return (
      options.length === 2 &&
      options[0]?.getAttribute("data-country-code") === "" &&
      options[0]?.getAttribute("data-currency-code") === "JPY" &&
      options[1]?.getAttribute("data-country-code") === "JP" &&
      options[1]?.getAttribute("data-currency-code") === "JPY"
    );
  });
  await search.press("ArrowDown");
  await search.press("ArrowDown");
  await search.press("Enter");
  await page.locator('[data-picker-dialog="source"]').waitFor({ state: "hidden" });
  assert(
    (await page.locator("#id_source_country").inputValue()) === "JP" &&
      (await page.locator("#id_source_currency").inputValue()) === "JPY",
    "current-converter: Japan/JPY picker selection did not commit",
  );

  await page.locator("#id_amount").fill("12");
  await Promise.all([waitForPost(), page.locator(".qa-primary-button").click()]);
  await page.locator("#current-conversion-result").waitFor();

  const resultText = await page.locator("#current-conversion-result").innerText();
  assert(resultText.includes("12 JPY"), "current-converter: same-currency input is missing");
  assert(
    resultText.includes("Exact same-currency rate"),
    "current-converter: same-currency provenance is missing",
  );
  assert(
    new URL(page.url()).searchParams.get("convert") === "1",
    "current-converter: successful HTMX conversion did not push a bookmarkable URL",
  );
  await page.waitForFunction(() =>
    document.getElementById("conversion-announcer")?.textContent?.includes("12 JPY"),
  );
  assert(
    (await page.locator("#conversion-announcer").count()) === 1,
    "current-converter: expected exactly one persistent conversion announcer",
  );
  assert(
    (await page.locator('#conversion-announcer[role="status"][aria-live="polite"]').count()) === 1,
    "current-converter: expected one persistent conversion result live region",
  );
  assert(
    (await page.locator('#conversion-result-region .qa-visually-hidden[role="status"]').count()) === 0,
    "current-converter: swapped result markup contains a duplicate hidden result announcer",
  );

  await page.getByRole("link", { name: "Everyday value" }).waitFor();
  await page.getByRole("link", { name: "Payment context" }).waitFor();
  assert(
    (await page.locator("#money-culture-story-slot[aria-live]").count()) === 0 &&
      (await page.locator("#historical-trend-slot[aria-live]").count()) === 0,
    "current-converter: large progressive fragments must not be live regions",
  );
  await page.getByText("Cup of coffee", { exact: true }).waitFor();
  await page.getByText("Tokyo Metro regular ticket", { exact: true }).waitFor();
  await page.getByRole("heading", { name: "Paying in Japan" }).waitFor();

  await page.waitForFunction((key) => {
    const raw = localStorage.getItem(key);
    if (!raw) return false;
    const parsed = JSON.parse(raw);
    return parsed.version === 1 && parsed.recent?.length === 1;
  }, LOCAL_STATE_KEY);
  await page.getByRole("button", { name: "Save pair" }).click();
  await page.getByRole("button", { name: "Remove saved pair" }).waitFor();
  const savedState = await page.evaluate(
    (key) => JSON.parse(localStorage.getItem(key) ?? "{}"),
    LOCAL_STATE_KEY,
  );
  assert(
    savedState.favourites?.length === 1,
    "current-converter: favourite was not stored locally",
  );
  assert(
    savedState.recent?.length === 1,
    "current-converter: successful conversion was not recorded once",
  );
  assert(savedState.recent[0]?.amount === "12", "current-converter: recent amount is incorrect");
  assert(
    savedState.recent[0]?.sourceCountry === "JP",
    "current-converter: recent source context is incorrect",
  );
  await assertAxe(page, "current-converter/result");

  const waitForStory = page.waitForResponse(
    (response) =>
      response.request().method() === "GET" && new URL(response.url()).pathname === "/story/",
  );
  await page.getByRole("link", { name: "Explore money & culture" }).click();
  await waitForStory;
  await page.locator(".qa-story-surface").waitFor();
  const storyText = await page.locator(".qa-story-surface").innerText();
  assert(
    storyText.includes("The sourced story behind this currency context"),
    "current-converter: progressive money-and-culture story did not render",
  );
  assert(
    storyText.includes("Temporal scope:"),
    "current-converter: story temporal provenance is missing",
  );
  assert(
    (await page.locator(".qa-story-surface a[href^='https://']").count()) > 0,
    "current-converter: story source links are missing",
  );
  await assertAxe(page, "current-converter/story");

  await page.locator("#id_rate_mode_1").check();
  await page.locator("#id_requested_date").waitFor({ state: "visible" });
  const historicalPost = waitForPost();
  await page.locator("#id_requested_date").fill("1998-06-15");
  await historicalPost;
  await page.locator("#current-conversion-result").waitFor();

  const historicalText = await page.locator("#current-conversion-result").innerText();
  assert(
    historicalText.includes("Historical exact 1:1"),
    "current-converter: historical identity status is missing",
  );
  assert(
    historicalText.includes("Requested date") && historicalText.includes("15 Jun 1998"),
    "current-converter: requested historical date is missing",
  );
  assert(
    historicalText.includes("Observation date"),
    "current-converter: historical observation date is missing",
  );
  const historicalUrl = new URL(page.url());
  assert(
    historicalUrl.searchParams.get("rate_mode") === "historical" &&
      historicalUrl.searchParams.get("requested_date") === "1998-06-15",
    "current-converter: historical conversion did not push a stable deep link",
  );

  await assertAxe(page, "current-converter/historical-result");

  const latestPost = waitForPost();
  await page.locator("#id_rate_mode_0").check();
  await latestPost;
  await page.locator("#current-conversion-result").waitFor();
  await page.locator("[data-historical-date-field]").waitFor({ state: "hidden" });

  const previousAmount = await page
    .locator("#current-conversion-result .qa-result__input")
    .innerText();
  await page.evaluate(() => {
    const announcer = document.getElementById("conversion-announcer");
    if (!announcer) throw new Error("Missing conversion announcer");
    window.__qaAnnouncerMutationCount = 0;
    window.__qaAnnouncerObserver = new MutationObserver(() => {
      window.__qaAnnouncerMutationCount += 1;
    });
    window.__qaAnnouncerObserver.observe(announcer, {
      childList: true,
      characterData: true,
      subtree: true,
    });
  });
  const invalidRefresh = waitForPost();
  await page.locator("#id_amount").fill("-1");
  const invalidRefreshResponse = await invalidRefresh;
  assert(
    invalidRefreshResponse.status() === 422,
    `current-converter: invalid progressive refresh returned ${invalidRefreshResponse.status()} instead of 422`,
  );
  await page.getByText("Enter zero or a positive amount.").waitFor();

  const preservedAmount = await page
    .locator("#current-conversion-result .qa-result__input")
    .innerText();
  assert(
    preservedAmount === previousAmount,
    "current-converter: failed refresh replaced the previous successful result",
  );
  await page.getByText("Previous result — fix the changed inputs to update it.").waitFor();
  const failedRefreshAnnouncements = await page.evaluate(() => {
    window.__qaAnnouncerObserver?.disconnect();
    return window.__qaAnnouncerMutationCount ?? 0;
  });
  assert(
    failedRefreshAnnouncements === 0,
    `current-converter: failed refresh mutated the success announcer ${failedRefreshAnnouncements} time(s)`,
  );

  const correctedRefresh = waitForPost();
  await page.locator("#id_amount").fill("12");
  await correctedRefresh;
  await page.locator("#current-conversion-result").waitFor();
  await page.waitForFunction(
    () => document.querySelector("[data-previous-result-note]")?.hidden === true,
  );

  await Promise.all([waitForPost(), page.locator("#swap-contexts").click()]);
  await page.waitForFunction(() => document.querySelector(".htmx-request") === null);
  const focused = await page.evaluate(() => document.activeElement?.id ?? "");
  assert(focused === "swap-contexts", `current-converter: swap focus moved to ${focused}`);

  const loadingState = await page.locator("#conversion-loading").evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      requestActive: element.classList.contains("htmx-request"),
      opacity: style.opacity,
      visibility: style.visibility,
      display: style.display,
    };
  });
  assert(
    !loadingState.requestActive &&
      (loadingState.opacity === "0" ||
        loadingState.visibility === "hidden" ||
        loadingState.display === "none"),
    `current-converter: loading indicator remained visually active after swap: ${JSON.stringify(loadingState)}`,
  );

  for (const message of consoleErrors.filter(
    (entry) =>
      entry.includes("422") &&
      (entry.includes("Unprocessable Content") || entry.includes("Unprocessable Entity")),
  )) {
    consoleErrors.splice(consoleErrors.indexOf(message), 1);
  }
}

async function assertSavedStateFlow(page) {
  const sampleState = {
    version: 1,
    favourites: [
      {
        id: "FI:EUR:>:JP:JPY",
        sourceCurrency: "EUR",
        destinationCurrency: "JPY",
        sourceCountry: "FI",
        destinationCountry: "JP",
        sourceCountryName: "Finland",
        destinationCountryName: "Japan",
        savedAt: "2026-09-21T12:00:00.000Z",
      },
    ],
    recent: [
      {
        id: "FI:EUR:>:JP:JPY|latest|latest|100",
        sourceCurrency: "EUR",
        destinationCurrency: "JPY",
        sourceCountry: "FI",
        destinationCountry: "JP",
        sourceCountryName: "Finland",
        destinationCountryName: "Japan",
        amount: "100",
        outputAmount: "17450",
        rateMode: "latest",
        requestedDate: "",
        effectiveDate: "2026-09-18",
        convertedAt: "2026-09-21T12:00:00.000Z",
      },
      {
        id: "FI:FIM:>:US:USD|historical|1998-06-15|100",
        sourceCurrency: "FIM",
        destinationCurrency: "USD",
        sourceCountry: "FI",
        destinationCountry: "US",
        sourceCountryName: "Finland",
        destinationCountryName: "United States",
        amount: "100",
        outputAmount: "21.35",
        rateMode: "historical",
        requestedDate: "1998-06-15",
        effectiveDate: "1998-06-15",
        convertedAt: "2026-09-20T12:00:00.000Z",
      },
    ],
  };

  await page.evaluate(({ key, state }) => localStorage.setItem(key, JSON.stringify(state)), {
    key: LOCAL_STATE_KEY,
    state: sampleState,
  });
  await page.reload({ waitUntil: "networkidle" });

  await page.getByRole("heading", { name: "EUR → JPY" }).waitFor();
  await page.getByText("100 EUR → 17450 JPY", { exact: true }).waitFor();
  await page.getByText("100 FIM → 21.35 USD", { exact: true }).waitFor();

  const savedRow = page.locator("[data-saved-pair-id]").first();
  const usePairHref = await savedRow.getByRole("link", { name: "Use pair" }).getAttribute("href");
  assert(usePairHref, "saved-state: favourite is missing its Use pair URL");
  const usePair = new URL(usePairHref, BASE_URL);
  assert(usePair.searchParams.get("load") === "1", "saved-state: favourite does not use pair-load mode");
  assert(usePair.searchParams.get("amount") === null, "saved-state: favourite unexpectedly stores amount");
  assert(
    usePair.searchParams.get("source_country") === "FI",
    "saved-state: favourite source country missing",
  );

  const latestRecent = page.locator("[data-recent-conversion-id]").first();
  const repeatHref = await latestRecent.getByRole("link", { name: "Repeat" }).getAttribute("href");
  assert(repeatHref, "saved-state: recent conversion is missing Repeat URL");
  const repeat = new URL(repeatHref, BASE_URL);
  assert(repeat.searchParams.get("convert") === "1", "saved-state: repeat does not request conversion");
  assert(repeat.searchParams.get("amount") === "100", "saved-state: repeat amount missing");

  const swapHref = await latestRecent.getByRole("link", { name: "Swap" }).getAttribute("href");
  assert(swapHref, "saved-state: recent conversion is missing Swap URL");
  const swap = new URL(swapHref, BASE_URL);
  assert(
    swap.searchParams.get("source_currency") === "JPY" &&
      swap.searchParams.get("destination_currency") === "EUR",
    "saved-state: swap URL did not reverse the pair",
  );

  await latestRecent.getByRole("button", { name: "Remove" }).click();
  await page.waitForFunction(
    (key) => JSON.parse(localStorage.getItem(key) ?? "{}").recent?.length === 1,
    LOCAL_STATE_KEY,
  );
  await page.getByRole("button", { name: "Clear recent history" }).click();
  await page.getByText("Recent history cleared from this browser.", { exact: true }).waitFor();
  await page.getByText("No recent conversions in this browser yet.", { exact: true }).waitFor();

  await page.getByRole("button", { name: "Clear saved pairs" }).click();
  await page.getByText("Saved pairs cleared from this browser.", { exact: true }).waitFor();
  await page.getByText("No saved pairs yet.", { exact: false }).waitFor();

  await page.evaluate((key) => localStorage.setItem(key, "{broken"), LOCAL_STATE_KEY);
  await page.reload({ waitUntil: "networkidle" });
  await page
    .getByText("Some local saved data was unreadable or outdated and has been ignored.", {
      exact: false,
    })
    .waitFor();

  await page.evaluate(({ key, state }) => localStorage.setItem(key, JSON.stringify(state)), {
    key: LOCAL_STATE_KEY,
    state: sampleState,
  });
  await page.reload({ waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "EUR → JPY" }).waitFor();
  await assertAxe(page, "saved-state/populated");
}

async function assertReducedMotion(page, surface) {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.waitForFunction(
    () => document.getAnimations().every((animation) => animation.playState !== "running"),
    null,
    { timeout: 500 },
  );
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

  await page.evaluate(() => {
    if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
  });
  // Establish keyboard modality first. Headless Chromium can otherwise treat a direct
  // programmatic focus after pointer-driven flows as not :focus-visible.
  await page.keyboard.press("Tab");
  const focusTarget =
    surface === "converter"
      ? page.locator("#workspace-amount")
      : surface === "current-converter"
        ? page.locator("#id_amount")
        : page.locator(".qa-skip-link");
  await focusTarget.focus();

  const focusState = await focusTarget.evaluate((element) => {
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
  const hasVisibleFocus = focusState.some(
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

  const manifest = JSON.parse(await readFile(BUILD_MANIFEST_PATH, "utf8"));
  const entry = manifest[VITE_ENTRY];
  assert(entry?.file, `Vite manifest entry ${VITE_ENTRY} is missing`);

  const coreManifestKeys = new Set();
  const visitStaticImports = (key) => {
    if (coreManifestKeys.has(key)) return;
    const item = manifest[key];
    assert(item?.file, `Vite manifest static import ${key} is missing`);
    coreManifestKeys.add(key);
    for (const imported of item.imports ?? []) {
      visitStaticImports(imported);
    }
  };
  visitStaticImports(VITE_ENTRY);

  const coreAssetNames = new Set(
    [...coreManifestKeys]
      .map((key) => manifest[key]?.file)
      .filter((file) => typeof file === "string" && file.endsWith(".js"))
      .map((file) => file.split("/").at(-1)),
  );

  const files = [];
  for (const name of javascript) {
    const bytes = await readFile(resolve(BUILD_ASSET_DIR, name));
    files.push({
      name,
      rawBytes: bytes.length,
      gzipBytes: gzipSync(bytes, { level: 9 }).length,
      loadingClass: coreAssetNames.has(name) ? "core" : "dynamic",
    });
  }

  const coreFiles = files.filter((file) => file.loadingClass === "core");
  const dynamicFiles = files.filter((file) => file.loadingClass === "dynamic");
  return {
    files,
    coreFiles,
    dynamicFiles,
    coreRawBytes: coreFiles.reduce((total, file) => total + file.rawBytes, 0),
    coreGzipBytes: coreFiles.reduce((total, file) => total + file.gzipBytes, 0),
    dynamicRawBytes: dynamicFiles.reduce((total, file) => total + file.rawBytes, 0),
    dynamicGzipBytes: dynamicFiles.reduce((total, file) => total + file.gzipBytes, 0),
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
      jsPaths: byExtension(".js").map((entry) => new URL(entry.name).pathname),
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
const browser = await browserType.launch();
const activeSurfaces =
  BROWSER_SCOPE === "full"
    ? SURFACES
    : SURFACES.filter((surface) => ["current-converter", "saved-state", "rate-series"].includes(surface.name));
const activeViewports =
  BROWSER_SCOPE === "full"
    ? VIEWPORTS
    : VIEWPORTS.filter((viewport) => ["wide-1440", "mobile-390"].includes(viewport.name));
const evidence = {
  browserEngine: BROWSER_ENGINE,
  scope: BROWSER_SCOPE,
  generatedAt: new Date().toISOString(),
  surfaces: {},
  budgets: {
    coreJavaScriptGzipBytes: 100 * 1024,
    source: "docs/36_PERFORMANCE_BUDGETS_AND_PROFILING.md",
  },
};

try {
  for (const surface of activeSurfaces) {
    evidence.surfaces[surface.name] = {};

    for (const viewport of activeViewports) {
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

      if (
        BROWSER_SCOPE === "full" &&
        surface.name === "converter" &&
        viewport.name === "wide-1440"
      ) {
        await assertConverterTransitionLayout(page);
      }

      if (
        surface.name === "current-converter" &&
        (viewport.name === "wide-1440" ||
          (BROWSER_SCOPE === "full" && viewport.name === "mobile-390"))
      ) {
        await assertCurrentConverterFlow(page, consoleErrors);
      }

      if (surface.name === "saved-state" && viewport.name === "wide-1440") {
        await assertSavedStateFlow(page);
      }

      if (viewport.name === "mobile-390") {
        await assertReducedMotion(page, surface.name);
        if (BROWSER_SCOPE === "full") {
          await assertForcedColors(page, surface.name);
        }
      }

      if (BROWSER_SCOPE === "full" && viewport.name === "reflow-320") {
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

  if (BROWSER_SCOPE === "full") {
    evidence.compressedAssets = await collectCompressedAssetEvidence();
    assert(
      evidence.compressedAssets.coreGzipBytes <= evidence.budgets.coreJavaScriptGzipBytes,
      `core JavaScript gzip size ${evidence.compressedAssets.coreGzipBytes} B exceeds 100 KiB budget`,
    );

    const dynamicAssetNames = new Set(
      evidence.compressedAssets.dynamicFiles.map((file) => file.name),
    );
    const requestedDynamicAssets = (surfaceName) =>
      new Set(
        Object.values(evidence.surfaces[surfaceName] ?? {})
          .flatMap((measurement) => measurement.jsPaths ?? [])
          .map((path) => path.split("/").at(-1))
          .filter((name) => dynamicAssetNames.has(name)),
      );

    assert(
      requestedDynamicAssets("current-converter").size === 0,
      "current converter unexpectedly loaded a dynamic historical-chart JavaScript chunk",
    );
    assert(
      requestedDynamicAssets("rate-series").size > 0,
      "historical rate-series surface did not load its dynamic chart JavaScript chunk",
    );
  }

  await writeFile(
    resolve(OUTPUT_DIR, `performance-evidence-${BROWSER_ENGINE}.json`),
    `${JSON.stringify(evidence, null, 2)}\n`,
    "utf8",
  );
} finally {
  await browser.close();
}
