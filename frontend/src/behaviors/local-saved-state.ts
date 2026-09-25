import {
  accountFavouriteSyncAvailable,
  saveFavouriteToAccount,
  syncLocalFavouritesToAccount,
} from "./account-favourites";
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

let savedPageModulePromise: Promise<typeof import("./local-saved-state-page")> | null = null;

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

function setAnonymousFavouriteButtonState(
  snapshot: HTMLElement,
  state: LocalPreferencesV1,
  storageStatus: ReadStatus,
): void {
  const button = snapshot.querySelector<HTMLButtonElement>("[data-save-pair]");
  const label = snapshot.querySelector<HTMLElement>("[data-save-pair-label]");
  const pair = pairFromSnapshot(snapshot);
  if (!button || !label || !pair) return;

  button.hidden = false;
  const saved = isFavourite(pair, state);
  button.setAttribute("aria-pressed", saved ? "true" : "false");
  button.setAttribute("aria-label", saved ? "Remove saved pair" : "Save pair");
  button.dataset.saved = saved ? "true" : "false";
  label.textContent = saved ? "Saved" : "Save pair";

  if (storageStatus === "unavailable") button.dataset.storageUnavailable = "true";
  else delete button.dataset.storageUnavailable;
}

function setAccountFavouriteButtonState(snapshot: HTMLElement, saved: boolean): void {
  const button = snapshot.querySelector<HTMLButtonElement>("[data-save-pair]");
  const label = snapshot.querySelector<HTMLElement>("[data-save-pair-label]");
  if (!button || !label) return;

  button.removeAttribute("aria-pressed");
  button.setAttribute("aria-label", saved ? "Pair saved to account" : "Save pair to account");
  button.dataset.saved = saved ? "true" : "false";
  button.disabled = saved;
  delete button.dataset.storageUnavailable;
  label.textContent = saved ? "Saved to account" : "Save to account";
}

function saveStatus(snapshot: HTMLElement, message: string): void {
  const status = snapshot.querySelector<HTMLElement>("[data-save-pair-status]");
  if (status) status.textContent = message;
}

async function saveAccountFavourite(snapshot: HTMLElement): Promise<void> {
  const pair = pairFromSnapshot(snapshot);
  const button = snapshot.querySelector<HTMLButtonElement>("[data-save-pair]");
  if (!pair || !button) return;

  button.disabled = true;
  saveStatus(snapshot, "Saving pair to your account…");
  try {
    const created = await saveFavouriteToAccount(pair);
    snapshot.dataset.accountSaved = "true";
    setAccountFavouriteButtonState(snapshot, true);
    saveStatus(
      snapshot,
      created ? "Saved to your account." : "This pair is already saved to your account.",
    );
  } catch {
    saveStatus(
      snapshot,
      "The pair could not be saved to your account. Your conversion is unchanged.",
    );
  } finally {
    button.disabled = snapshot.dataset.accountSaved === "true";
  }
}

function toggleAnonymousFavourite(snapshot: HTMLElement): void {
  const pair = pairFromSnapshot(snapshot);
  if (!pair) return;

  const read = readState();
  if (read.status === "unavailable") {
    saveStatus(
      snapshot,
      "Saved pairs are unavailable because browser storage is blocked. Conversion still works.",
    );
    setAnonymousFavouriteButtonState(snapshot, read.state, read.status);
    return;
  }

  const toggled = toggleFavouriteInState(read.state, pair);
  if (!writeState(toggled.state)) {
    saveStatus(snapshot, "The pair could not be saved because browser storage is unavailable.");
    return;
  }

  setAnonymousFavouriteButtonState(snapshot, toggled.state, "ok");
  saveStatus(snapshot, toggled.saved ? "Saved in this browser." : "Removed from saved.");
}

function enhanceConversionSnapshots(): void {
  const read = readState();
  const accountMode = accountFavouriteSyncAvailable();

  for (const snapshot of document.querySelectorAll<HTMLElement>(
    "[data-local-conversion-snapshot]",
  )) {
    if (accountMode) {
      setAccountFavouriteButtonState(snapshot, snapshot.dataset.accountSaved === "true");
    } else {
      setAnonymousFavouriteButtonState(snapshot, read.state, read.status);
    }

    if (snapshot.dataset.localStateWired !== "true") {
      snapshot.dataset.localStateWired = "true";
      snapshot
        .querySelector<HTMLButtonElement>("[data-save-pair]")
        ?.addEventListener("click", () => {
          if (accountMode) void saveAccountFavourite(snapshot);
          else toggleAnonymousFavourite(snapshot);
        });
    }

    if (snapshot.dataset.recentRecorded !== "true") {
      snapshot.dataset.recentRecorded = "true";
      if (snapshot.dataset.accountRecentRecorded !== "true") addRecent(snapshot);
    }
  }
}

function showSavedPageEnhancementFailure(error: unknown): void {
  console.error("Saved & recent enhancement failed to load.", error);
  const status = document.querySelector<HTMLElement>("[data-local-storage-status]");
  if (!status) return;

  status.dataset.storageTone = "warning";
  status.setAttribute("aria-live", "polite");
  status.textContent =
    "Saved state could not be loaded in this browser. Reload to try again; conversion still works.";
}

function enhanceSavedPage(): void {
  const page = document.querySelector<HTMLElement>("[data-local-saved-state-page]");
  if (!page) return;

  const status = page.querySelector<HTMLElement>("[data-local-storage-status]");
  if (status) status.hidden = false;

  savedPageModulePromise ??= import("./local-saved-state-page");
  void savedPageModulePromise
    .then(({ wireSavedPage }) => wireSavedPage())
    .catch((error: unknown) => {
      savedPageModulePromise = null;
      showSavedPageEnhancementFailure(error);
    });
}

function syncLocalAccountFavourites(): void {
  if (!accountFavouriteSyncAvailable()) return;

  void syncLocalFavouritesToAccount()
    .then((mergedCount) => {
      if (
        mergedCount > 0 &&
        document.querySelector<HTMLElement>(
          '[data-local-saved-state-page][data-account-mode="true"]',
        )
      ) {
        window.location.reload();
      }
    })
    .catch((error: unknown) => {
      console.error("Local favourites could not be merged into the account.", error);
      const status = document.querySelector<HTMLElement>("[data-local-storage-status]");
      if (status) {
        status.hidden = false;
        status.dataset.storageTone = "warning";
        status.setAttribute("aria-live", "polite");
        status.textContent =
          "Your browser-local saved pairs could not be synced. They remain on this device.";
      }
    });
}

function enhanceLocalSavedState(): void {
  enhanceConversionSnapshots();
  enhanceSavedPage();
  syncLocalAccountFavourites();
}

document.addEventListener("DOMContentLoaded", enhanceLocalSavedState);
document.addEventListener("htmx:afterSwap", enhanceLocalSavedState);
window.addEventListener("storage", (event) => {
  if (event.key === STORAGE_KEY) enhanceLocalSavedState();
});
