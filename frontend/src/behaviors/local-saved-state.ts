import { wireSavedPage } from "./local-saved-state-page";
import {
  isFavourite,
  type LocalPreferencesV1,
  normalizePair,
  normalizeRecent,
  type PairContext,
  type ReadStatus,
  readState,
  STORAGE_KEY,
  toggleFavouriteInState,
  upsertRecent,
  writeState,
} from "./local-saved-state-store";

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

function recentFromSnapshot(element: HTMLElement) {
  return normalizeRecent({
    sourceCurrency: element.dataset.sourceCurrency ?? "",
    destinationCurrency: element.dataset.destinationCurrency ?? "",
    sourceCountry: element.dataset.sourceCountry ?? "",
    destinationCountry: element.dataset.destinationCountry ?? "",
    sourceCountryName: element.dataset.sourceCountryName ?? "",
    destinationCountryName: element.dataset.destinationCountryName ?? "",
    amount: element.dataset.inputAmount ?? "",
    outputAmount: element.dataset.outputAmount ?? "",
    rateMode: element.dataset.rateMode ?? "",
    requestedDate: element.dataset.requestedDate ?? "",
    effectiveDate: element.dataset.effectiveDate ?? "",
    convertedAt: new Date().toISOString(),
  });
}

function addRecent(snapshot: HTMLElement): void {
  const recent = recentFromSnapshot(snapshot);
  if (!recent) return;

  const read = readState();
  if (read.status === "unavailable") return;
  writeState(upsertRecent(read.state, recent));
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

  const toggled = toggleFavouriteInState(read.state, pair);
  if (!writeState(toggled.state)) {
    saveStatus(snapshot, "The pair could not be saved because browser storage is unavailable.");
    return;
  }

  setFavouriteButtonState(snapshot, toggled.state, "ok");
  saveStatus(snapshot, toggled.saved ? "Saved in this browser." : "Removed from saved.");
}

function enhanceConversionSnapshots(): void {
  const read = readState();
  for (const snapshot of document.querySelectorAll<HTMLElement>(
    "[data-local-conversion-snapshot]",
  )) {
    setFavouriteButtonState(snapshot, read.state, read.status);

    if (snapshot.dataset.localStateWired !== "true") {
      snapshot.dataset.localStateWired = "true";
      snapshot
        .querySelector<HTMLButtonElement>("[data-save-pair]")
        ?.addEventListener("click", () => {
          toggleFavourite(snapshot);
        });
    }

    if (snapshot.dataset.recentRecorded !== "true") {
      snapshot.dataset.recentRecorded = "true";
      addRecent(snapshot);
    }
  }
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
