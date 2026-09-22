import {
  type FavouritePair,
  type PairContext,
  readState,
  writeState,
} from "./local-saved-state-store";

interface AccountSyncConfig {
  url: string;
  csrfToken: string;
}

interface AccountSyncResponse {
  createdCount: number;
}

let localMergePromise: Promise<number> | null = null;

function accountSyncConfig(): AccountSyncConfig | null {
  const { accountAuthenticated, accountFavouriteSyncUrl: url, accountCsrfToken: csrfToken } =
    document.body.dataset;
  if (accountAuthenticated !== "true" || !url || !csrfToken) return null;
  return { url, csrfToken };
}

export function accountFavouriteSyncAvailable(): boolean {
  return accountSyncConfig() !== null;
}

function pairPayload(pair: PairContext) {
  return {
    sourceCurrency: pair.sourceCurrency,
    destinationCurrency: pair.destinationCurrency,
    sourceCountry: pair.sourceCountry,
    destinationCountry: pair.destinationCountry,
  };
}

async function postFavourites(pairs: PairContext[]): Promise<AccountSyncResponse> {
  const config = accountSyncConfig();
  if (!config) throw new Error("Account favourite sync is not available.");

  const response = await fetch(config.url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": config.csrfToken,
    },
    body: JSON.stringify({ favourites: pairs.map(pairPayload) }),
  });
  if (!response.ok) {
    throw new Error(`Favourite sync failed with status ${response.status}.`);
  }
  return (await response.json()) as AccountSyncResponse;
}

export async function saveFavouriteToAccount(pair: PairContext): Promise<boolean> {
  const response = await postFavourites([pair]);
  return response.createdCount > 0;
}

export function syncLocalFavouritesToAccount(): Promise<number> {
  if (localMergePromise) return localMergePromise;

  const config = accountSyncConfig();
  if (!config) return Promise.resolve(0);

  const read = readState();
  if (read.status === "unavailable" || read.state.favourites.length === 0) {
    return Promise.resolve(0);
  }

  const localFavourites: FavouritePair[] = [...read.state.favourites];
  localMergePromise = postFavourites(localFavourites)
    .then((response) => {
      const latest = readState();
      if (latest.status !== "unavailable") {
        const mergedIds = new Set(localFavourites.map((item) => item.id));
        writeState({
          ...latest.state,
          favourites: latest.state.favourites.filter((item) => !mergedIds.has(item.id)),
        });
      }
      window.dispatchEvent(
        new CustomEvent("account:favourites-synced", {
          detail: { createdCount: response.createdCount, mergedCount: localFavourites.length },
        }),
      );
      return localFavourites.length;
    })
    .catch((error: unknown) => {
      localMergePromise = null;
      throw error;
    });

  return localMergePromise;
}
