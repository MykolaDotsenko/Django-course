const STORAGE_KEY = "cultural-currency:local-preferences:v1";
const STORAGE_VERSION = 1 as const;
const MAX_FAVOURITES = 12;
const MAX_RECENTS = 10;
const STORAGE_PROBE_KEY = "cultural-currency:storage-probe";

type RateMode = "latest" | "historical";
type ReadStatus = "ok" | "recovered" | "unavailable";

interface PairContext {
  sourceCurrency: string;
  destinationCurrency: string;
  sourceCountry: string;
  destinationCountry: string;
  sourceCountryName: string;
  destinationCountryName: string;
}

interface FavouritePair extends PairContext {
  id: string;
  savedAt: string;
}

interface RecentConversion extends PairContext {
  id: string;
  amount: string;
  outputAmount: string;
  rateMode: RateMode;
  requestedDate: string;
  effectiveDate: string;
  convertedAt: string;
}

interface LocalPreferencesV1 {
  version: typeof STORAGE_VERSION;
  favourites: FavouritePair[];
  recent: RecentConversion[];
}

interface ReadResult {
  state: LocalPreferencesV1;
  status: ReadStatus;
}

let cachedStorage: Storage | null | undefined;

function emptyState(): LocalPreferencesV1 {
  return { version: STORAGE_VERSION, favourites: [], recent: [] };
}

function localStorageOrNull(): Storage | null {
  if (cachedStorage !== undefined) return cachedStorage;
  try {
    const storage = window.localStorage;
    storage.setItem(STORAGE_PROBE_KEY, "1");
    storage.removeItem(STORAGE_PROBE_KEY);
    cachedStorage = storage;
  } catch {
    cachedStorage = null;
  }
  return cachedStorage;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizedString(value: unknown, maxLength: number): string | null {
  return typeof value === "string" && value.length <= maxLength ? value : null;
}

function normalizedCurrencyCode(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const code = value.toUpperCase();
  return /^[A-Z]{3}$/.test(code) ? code : null;
}

function normalizedCountryCode(value: unknown): string | null {
  if (value === "") return "";
  if (typeof value !== "string") return null;
  const code = value.toUpperCase();
  return /^[A-Z]{2}$/.test(code) ? code : null;
}

function normalizedIsoDate(value: unknown, allowEmpty = false): string | null {
  if (allowEmpty && value === "") return "";
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  return Number.isNaN(Date.parse(`${value}T00:00:00Z`)) ? null : value;
}

function normalizedTimestamp(value: unknown): string | null {
  return typeof value === "string" && !Number.isNaN(Date.parse(value)) ? value : null;
}

function normalizedAmount(value: unknown): string | null {
  if (typeof value !== "string" || value.length > 64) return null;
  return /^\d+(?:\.\d+)?$/.test(value) ? value : null;
}

function normalizePair(value: Record<string, unknown>): PairContext | null {
  const sourceCurrency = normalizedCurrencyCode(value.sourceCurrency);
  const destinationCurrency = normalizedCurrencyCode(value.destinationCurrency);
  const sourceCountry = normalizedCountryCode(value.sourceCountry);
  const destinationCountry = normalizedCountryCode(value.destinationCountry);
  const sourceCountryName = normalizedString(value.sourceCountryName, 120);
  const destinationCountryName = normalizedString(value.destinationCountryName, 120);

  if (
    sourceCurrency === null ||
    destinationCurrency === null ||
    sourceCountry === null ||
    destinationCountry === null ||
    sourceCountryName === null ||
    destinationCountryName === null
  ) {
    return null;
  }
  return {
    sourceCurrency,
    destinationCurrency,
    sourceCountry,
    destinationCountry,
    sourceCountryName,
    destinationCountryName,
  };
}

function pairId(pair: PairContext): string {
  return [
    pair.sourceCountry || "_",
    pair.sourceCurrency,
    ">",
    pair.destinationCountry || "_",
    pair.destinationCurrency,
  ].join(":");
}

function normalizeFavourite(value: unknown): FavouritePair | null {
  if (!isRecord(value)) return null;
  const pair = normalizePair(value);
  const savedAt = normalizedTimestamp(value.savedAt);
  if (!pair || savedAt === null) return null;
  return { ...pair, id: pairId(pair), savedAt };
}

function recentId(
  pair: PairContext,
  amount: string,
  rateMode: RateMode,
  requestedDate: string,
): string {
  return `${pairId(pair)}|${rateMode}|${requestedDate || "latest"}|${amount}`;
}

function normalizeRecent(value: unknown): RecentConversion | null {
  if (!isRecord(value)) return null;
  const pair = normalizePair(value);
  const amount = normalizedAmount(value.amount);
  const outputAmount = normalizedAmount(value.outputAmount);
  const rateMode =
    value.rateMode === "historical"
      ? "historical"
      : value.rateMode === "latest"
        ? "latest"
        : null;
  const requestedDate = normalizedIsoDate(value.requestedDate, true);
  const effectiveDate = normalizedIsoDate(value.effectiveDate);
  const convertedAt = normalizedTimestamp(value.convertedAt);
  if (
    !pair ||
    amount === null ||
    outputAmount === null ||
    rateMode === null ||
    requestedDate === null ||
    effectiveDate === null ||
    convertedAt === null ||
    (rateMode === "historical" && requestedDate === "")
  ) {
    return null;
  }
  return {
    ...pair,
    id: recentId(pair, amount, rateMode, requestedDate),
    amount,
    outputAmount,
    rateMode,
    requestedDate,
    effectiveDate,
    convertedAt,
  };
}

function dedupeById<T extends { id: string }>(items: T[], limit: number): T[] {
  const seen = new Set<string>();
  const result: T[] = [];
  for (const item of items) {
    if (seen.has(item.id)) continue;
    seen.add(item.id);
    result.push(item);
    if (result.length >= limit) break;
  }
  return result;
}

function readState(): ReadResult {
  const storage = localStorageOrNull();
  if (!storage) return { state: emptyState(), status: "unavailable" };

  const raw = storage.getItem(STORAGE_KEY);
  if (raw === null) return { state: emptyState(), status: "ok" };

  try {
    const parsed: unknown = JSON.parse(raw);
    if (!isRecord(parsed) || parsed.version !== STORAGE_VERSION) {
      return { state: emptyState(), status: "recovered" };
    }
    const rawFavourites = Array.isArray(parsed.favourites) ? parsed.favourites : [];
    const rawRecent = Array.isArray(parsed.recent) ? parsed.recent : [];
    const favourites = dedupeById(
      rawFavourites.map(normalizeFavourite).filter((item): item is FavouritePair => item !== null),
      MAX_FAVOURITES,
    );
    const recent = dedupeById(
      rawRecent.map(normalizeRecent).filter((item): item is RecentConversion => item !== null),
      MAX_RECENTS,
    );
    const recovered =
      !Array.isArray(parsed.favourites) ||
      !Array.isArray(parsed.recent) ||
      favourites.length !== Math.min(rawFavourites.length, MAX_FAVOURITES) ||
      recent.length !== Math.min(rawRecent.length, MAX_RECENTS);
    return {
      state: { version: STORAGE_VERSION, favourites, recent },
      status: recovered ? "recovered" : "ok",
    };
  } catch {
    return { state: emptyState(), status: "recovered" };
  }
}

function writeState(state: LocalPreferencesV1): boolean {
  const storage = localStorageOrNull();
  if (!storage) return false;
  try {
    storage.setItem(STORAGE_KEY, JSON.stringify(state));
    return true;
  } catch {
    return false;
  }
}

function pairFromSnapshot(element: HTMLElement): PairContext | null {
  return normalizePair({
    sourceCurrency: element.dataset.sourceCurrency ?? "",
    destinationCurrency: element.dataset.destinationCurrency ?? "",
    sourceCountry: element.dataset.sourceCountry ?? "",
    destinationCountry: element.dataset.destinationCountry ?? "",
    sourceCountryName: element.dataset.sourceCountryName ?? "",
    destinationCountryName: element.dataset.destinationCountryName ?? "",
  });
}

function recentFromSnapshot(element: HTMLElement): RecentConversion | null {
  const pair = pairFromSnapshot(element);
  if (!pair) return null;
  const amount = normalizedAmount(element.dataset.inputAmount);
  const outputAmount = normalizedAmount(element.dataset.outputAmount);
  const rateMode: RateMode | null =
    element.dataset.rateMode === "historical"
      ? "historical"
      : element.dataset.rateMode === "latest"
        ? "latest"
        : null;
  const requestedDate = normalizedIsoDate(element.dataset.requestedDate ?? "", true);
  const effectiveDate = normalizedIsoDate(element.dataset.effectiveDate);
  if (
    amount === null ||
    outputAmount === null ||
    rateMode === null ||
    requestedDate === null ||
    effectiveDate === null ||
    (rateMode === "historical" && requestedDate === "")
  ) {
    return null;
  }
  return {
    ...pair,
    id: recentId(pair, amount, rateMode, requestedDate),
    amount,
    outputAmount,
    rateMode,
    requestedDate,
    effectiveDate,
    convertedAt: new Date().toISOString(),
  };
}

function addRecent(snapshot: HTMLElement): void {
  const recent = recentFromSnapshot(snapshot);
  if (!recent) return;
  const read = readState();
  if (read.status === "unavailable") return;
  read.state.recent = [recent, ...read.state.recent.filter((item) => item.id !== recent.id)].slice(
    0,
    MAX_RECENTS,
  );
  writeState(read.state);
}

function isFavourite(pair: PairContext, state: LocalPreferencesV1): boolean {
  return state.favourites.some((item) => item.id === pairId(pair));
}

function setFavouriteButtonState(
  snapshot: HTMLElement,
  state: LocalPreferencesV1,
  storageStatus: ReadStatus,
): void {
  const button = snapshot.querySelector<HTMLButtonElement>("[data-save-pair]");
  const label = snapshot.querySelector<HTMLElement>("[data-save-pair-label]");
  const pair = pairFromSnapshot(snapshot);
  if (!button || !label || !pair) return;

  const saved = isFavourite(pair, state);
  button.setAttribute("aria-pressed", saved ? "true" : "false");
  button.setAttribute("aria-label", saved ? "Remove saved pair" : "Save pair");
  button.dataset.saved = saved ? "true" : "false";
  label.textContent = saved ? "Saved" : "Save pair";

  if (storageStatus === "unavailable") button.dataset.storageUnavailable = "true";
  else delete button.dataset.storageUnavailable;
}

function saveStatus(snapshot: HTMLElement, message: string): void {
  const status = snapshot.querySelector<HTMLElement>("[data-save-pair-status]");
  if (status) status.textContent = message;
}

function toggleFavourite(snapshot: HTMLElement): void {
  const pair = pairFromSnapshot(snapshot);
  if (!pair) return;
  const read = readState();

  if (read.status === "unavailable") {
    saveStatus(
      snapshot,
      "Saved pairs are unavailable because browser storage is blocked. Conversion still works.",
    );
    setFavouriteButtonState(snapshot, read.state, read.status);
    return;
  }

  const id = pairId(pair);
  const existing = read.state.favourites.some((item) => item.id === id);
  if (existing) {
    read.state.favourites = read.state.favourites.filter((item) => item.id !== id);
  } else {
    read.state.favourites = [
      { ...pair, id, savedAt: new Date().toISOString() },
      ...read.state.favourites.filter((item) => item.id !== id),
    ].slice(0, MAX_FAVOURITES);
  }

  if (!writeState(read.state)) {
    saveStatus(snapshot, "The pair could not be saved because browser storage is unavailable.");
    return;
  }

  setFavouriteButtonState(snapshot, read.state, "ok");
  saveStatus(snapshot, existing ? "Removed from saved." : "Saved in this browser.");
}

function enhanceConversionSnapshots(): void {
  const read = readState();
  for (const snapshot of document.querySelectorAll<HTMLElement>(
    "[data-local-conversion-snapshot]",
  )) {
    setFavouriteButtonState(snapshot, read.state, read.status);

    if (snapshot.dataset.localStateWired !== "true") {
      snapshot.dataset.localStateWired = "true";
      snapshot.querySelector<HTMLButtonElement>("[data-save-pair]")?.addEventListener("click", () => {
        toggleFavourite(snapshot);
      });
    }
    if (snapshot.dataset.recentRecorded !== "true") {
      snapshot.dataset.recentRecorded = "true";
      addRecent(snapshot);
    }
  }
}

function countryLabel(code: string, name: string): string {
  return name || code || "No country context";
}

function countrySummary(pair: PairContext): string {
  return `${countryLabel(pair.sourceCountry, pair.sourceCountryName)} → ${countryLabel(
    pair.destinationCountry,
    pair.destinationCountryName,
  )}`;
}

function dateLabel(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${value}T00:00:00Z`));
}

function savedAtLabel(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function dayGroupLabel(value: string): string {
  const date = new Date(value);
  const localDay = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const dayDifference = Math.round((today.getTime() - localDay.getTime()) / 86_400_000);
  if (dayDifference === 0) return "Today";
  if (dayDifference === 1) return "Yesterday";
  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

function linkForPair(
  converterUrl: string,
  pair: PairContext,
  options: { amount?: string; rateMode?: RateMode; requestedDate?: string; swap?: boolean } = {},
): string {
  const url = new URL(converterUrl, window.location.origin);
  const sourceCurrency = options.swap ? pair.destinationCurrency : pair.sourceCurrency;
  const destinationCurrency = options.swap ? pair.sourceCurrency : pair.destinationCurrency;
  const sourceCountry = options.swap ? pair.destinationCountry : pair.sourceCountry;
  const destinationCountry = options.swap ? pair.sourceCountry : pair.destinationCountry;

  if (options.amount) {
    url.searchParams.set("convert", "1");
    url.searchParams.set("amount", options.amount);
  } else {
    url.searchParams.set("load", "1");
  }
  url.searchParams.set("source_currency", sourceCurrency);
  url.searchParams.set("destination_currency", destinationCurrency);
  if (sourceCountry) url.searchParams.set("source_country", sourceCountry);
  if (destinationCountry) url.searchParams.set("destination_country", destinationCountry);
  if (options.rateMode === "historical" && options.requestedDate) {
    url.searchParams.set("rate_mode", "historical");
    url.searchParams.set("requested_date", options.requestedDate);
  }
  return `${url.pathname}${url.search}`;
}

function actionLink(text: string, href: string): HTMLAnchorElement {
  const element = document.createElement("a");
  element.className = "qa-secondary-button";
  element.textContent = text;
  element.href = href;
  return element;
}

function actionButton(text: string, action: () => void): HTMLButtonElement {
  const element = document.createElement("button");
  element.className = "qa-secondary-button";
  element.type = "button";
  element.textContent = text;
  element.addEventListener("click", action);
  return element;
}

function renderFavourites(
  page: HTMLElement,
  state: LocalPreferencesV1,
  converterUrl: string,
): void {
  const list = page.querySelector<HTMLElement>("[data-favourites-list]");
  const empty = page.querySelector<HTMLElement>("[data-favourites-empty]");
  if (!list || !empty) return;

  list.replaceChildren();
  empty.hidden = state.favourites.length > 0;

  for (const favourite of state.favourites) {
    const article = document.createElement("article");
    article.className = "qa-saved-row";
    article.dataset.savedPairId = favourite.id;

    const copy = document.createElement("div");
    copy.className = "qa-saved-row__copy";
    const title = document.createElement("h3");
    title.textContent = `${favourite.sourceCurrency} → ${favourite.destinationCurrency}`;
    const countries = document.createElement("p");
    countries.textContent = countrySummary(favourite);
    const meta = document.createElement("p");
    meta.className = "qa-saved-row__meta";
    meta.textContent = `Saved ${savedAtLabel(favourite.savedAt)} · amount is not stored`;
    copy.append(title, countries, meta);

    const actions = document.createElement("div");
    actions.className = "qa-saved-row__actions";
    actions.append(
      actionLink("Use pair", linkForPair(converterUrl, favourite)),
      actionLink("Reverse pair", linkForPair(converterUrl, favourite, { swap: true })),
      actionButton("Remove", () => {
        const read = readState();
        read.state.favourites = read.state.favourites.filter((item) => item.id !== favourite.id);
        if (writeState(read.state)) renderSavedPage("Removed from saved.");
      }),
    );
    article.append(copy, actions);
    list.append(article);
  }
}

function recentMeta(recent: RecentConversion): string {
  if (recent.rateMode === "historical") {
    return `Historical · requested ${dateLabel(recent.requestedDate)} · observation ${dateLabel(
      recent.effectiveDate,
    )}`;
  }
  return `Latest available · effective ${dateLabel(recent.effectiveDate)}`;
}

function renderRecents(
  page: HTMLElement,
  state: LocalPreferencesV1,
  converterUrl: string,
): void {
  const list = page.querySelector<HTMLElement>("[data-recents-list]");
  const empty = page.querySelector<HTMLElement>("[data-recents-empty]");
  if (!list || !empty) return;

  list.replaceChildren();
  empty.hidden = state.recent.length > 0;
  let activeDay = "";

  for (const recent of state.recent) {
    const day = dayGroupLabel(recent.convertedAt);
    if (day !== activeDay) {
      activeDay = day;
      const heading = document.createElement("h3");
      heading.className = "qa-saved-list__date";
      heading.textContent = day;
      list.append(heading);
    }

    const article = document.createElement("article");
    article.className = "qa-saved-row";
    article.dataset.recentConversionId = recent.id;

    const copy = document.createElement("div");
    copy.className = "qa-saved-row__copy";
    const title = document.createElement("h4");
    title.textContent = `${recent.amount} ${recent.sourceCurrency} → ${recent.outputAmount} ${recent.destinationCurrency}`;
    const countries = document.createElement("p");
    countries.textContent = countrySummary(recent);
    const meta = document.createElement("p");
    meta.className = "qa-saved-row__meta";
    meta.textContent = recentMeta(recent);
    copy.append(title, countries, meta);

    const actions = document.createElement("div");
    actions.className = "qa-saved-row__actions";
    actions.append(
      actionLink(
        "Repeat",
        linkForPair(converterUrl, recent, {
          amount: recent.amount,
          rateMode: recent.rateMode,
          requestedDate: recent.requestedDate,
        }),
      ),
      actionLink(
        "Swap",
        linkForPair(converterUrl, recent, {
          amount: recent.amount,
          rateMode: recent.rateMode,
          requestedDate: recent.requestedDate,
          swap: true,
        }),
      ),
      actionButton("Remove", () => {
        const read = readState();
        read.state.recent = read.state.recent.filter((item) => item.id !== recent.id);
        if (writeState(read.state)) renderSavedPage("Recent conversion removed.");
      }),
    );
    article.append(copy, actions);
    list.append(article);
  }
}

function setStorageStatus(page: HTMLElement, read: ReadResult, overrideMessage = ""): void {
  const status = page.querySelector<HTMLElement>("[data-local-storage-status]");
  if (!status) return;
  if (overrideMessage) {
    status.textContent = overrideMessage;
  } else if (read.status === "unavailable") {
    status.textContent =
      "Browser storage is unavailable. Saved pairs and recent history are disabled; conversion still works.";
  } else if (read.status === "recovered") {
    status.textContent =
      "Some local saved data was unreadable or outdated and has been ignored. Nothing was sent to the server.";
  } else {
    status.textContent = `Stored locally in this browser · ${read.state.favourites.length} saved · ${read.state.recent.length} recent.`;
  }
}

function renderSavedPage(overrideMessage = ""): void {
  const page = document.querySelector<HTMLElement>("[data-local-saved-state-page]");
  if (!page) return;

  const read = readState();
  const converterUrl = page.dataset.converterUrl ?? "/";
  setStorageStatus(page, read, overrideMessage);

  const clearFavourites = page.querySelector<HTMLButtonElement>("[data-clear-favourites]");
  const clearRecents = page.querySelector<HTMLButtonElement>("[data-clear-recents]");
  const unavailable = read.status === "unavailable";
  if (clearFavourites) clearFavourites.disabled = unavailable || read.state.favourites.length === 0;
  if (clearRecents) clearRecents.disabled = unavailable || read.state.recent.length === 0;

  renderFavourites(page, read.state, converterUrl);
  renderRecents(page, read.state, converterUrl);
}

function wireSavedPage(): void {
  const page = document.querySelector<HTMLElement>("[data-local-saved-state-page]");
  if (!page) return;

  if (page.dataset.localStateWired !== "true") {
    page.dataset.localStateWired = "true";
    page
      .querySelector<HTMLButtonElement>("[data-clear-favourites]")
      ?.addEventListener("click", () => {
        const read = readState();
        if (read.status === "unavailable") return renderSavedPage();
        read.state.favourites = [];
        if (writeState(read.state)) renderSavedPage("Saved pairs cleared from this browser.");
      });
    page.querySelector<HTMLButtonElement>("[data-clear-recents]")?.addEventListener("click", () => {
      const read = readState();
      if (read.status === "unavailable") return renderSavedPage();
      read.state.recent = [];
      if (writeState(read.state)) renderSavedPage("Recent history cleared from this browser.");
    });
  }
  renderSavedPage();
}

function enhanceLocalSavedState(): void {
  enhanceConversionSnapshots();
  wireSavedPage();
}

document.addEventListener("DOMContentLoaded", enhanceLocalSavedState);
document.addEventListener("htmx:afterSwap", enhanceLocalSavedState);
window.addEventListener("storage", (event) => {
  if (event.key === STORAGE_KEY) enhanceLocalSavedState();
});
