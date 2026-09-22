import {
  type LocalPreferencesV1,
  type PairContext,
  type RateMode,
  type ReadResult,
  type RecentConversion,
  readState,
  writeState,
} from "./local-saved-state-store";

const WRITE_FAILURE_MESSAGE =
  "Browser storage could not be updated. Your converter still works and no data was sent to the server.";

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

function persistAndRender(state: LocalPreferencesV1, successMessage: string): void {
  renderSavedPage(writeState(state) ? successMessage : WRITE_FAILURE_MESSAGE);
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
        const next = {
          ...read.state,
          favourites: read.state.favourites.filter((item) => item.id !== favourite.id),
        };
        persistAndRender(next, "Removed from saved.");
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

function renderRecents(page: HTMLElement, state: LocalPreferencesV1, converterUrl: string): void {
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
        const next = {
          ...read.state,
          recent: read.state.recent.filter((item) => item.id !== recent.id),
        };
        persistAndRender(next, "Recent conversion removed.");
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
    status.dataset.storageTone = "feedback";
    status.textContent = overrideMessage;
  } else if (read.status === "unavailable") {
    status.dataset.storageTone = "warning";
    status.textContent =
      "Browser storage is unavailable. Saved pairs and recent history are disabled; conversion still works.";
  } else if (read.status === "recovered") {
    status.dataset.storageTone = "warning";
    status.textContent =
      "Some local saved data was unreadable or outdated and has been ignored. Nothing was sent to the server.";
  } else {
    status.dataset.storageTone = "neutral";
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
  if (clearFavourites) {
    const canClearFavourites = !unavailable && read.state.favourites.length > 0;
    clearFavourites.hidden = !canClearFavourites;
    clearFavourites.disabled = !canClearFavourites;
  }
  if (clearRecents) {
    const canClearRecents = !unavailable && read.state.recent.length > 0;
    clearRecents.hidden = !canClearRecents;
    clearRecents.disabled = !canClearRecents;
  }

  renderFavourites(page, read.state, converterUrl);
  renderRecents(page, read.state, converterUrl);
}

export function wireSavedPage(): void {
  const page = document.querySelector<HTMLElement>("[data-local-saved-state-page]");
  if (!page) return;

  if (page.dataset.localStateWired !== "true") {
    page.dataset.localStateWired = "true";
    page
      .querySelector<HTMLButtonElement>("[data-clear-favourites]")
      ?.addEventListener("click", () => {
        const read = readState();
        if (read.status === "unavailable") return renderSavedPage();
        persistAndRender(
          { ...read.state, favourites: [] },
          "Saved pairs cleared from this browser.",
        );
      });
    page.querySelector<HTMLButtonElement>("[data-clear-recents]")?.addEventListener("click", () => {
      const read = readState();
      if (read.status === "unavailable") return renderSavedPage();
      persistAndRender({ ...read.state, recent: [] }, "Recent history cleared from this browser.");
    });
  }

  renderSavedPage();
}
