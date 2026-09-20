let restoreFocusId: string | null = null;

export function requestFocusRestore(id: string): void {
  restoreFocusId = id;
}

function syncHistoricalDateField(form: HTMLFormElement): void {
  const field = form.querySelector<HTMLElement>("[data-historical-date-field]");
  const historical = form.querySelector<HTMLInputElement>(
    'input[name="rate_mode"][value="historical"]',
  );
  if (!field || !historical) return;

  field.hidden = !historical.checked;
}

function enhanceAutoRefresh(form: HTMLFormElement): void {
  syncHistoricalDateField(form);
  if (form.dataset.autoRefreshWired === "true") return;
  form.dataset.autoRefreshWired = "true";

  let amountTimer: number | undefined;

  form.addEventListener("input", (event) => {
    if (form.dataset.hasResult !== "true") return;
    const target = event.target;
    if (!(target instanceof HTMLInputElement) || target.id !== "id_amount") return;

    window.clearTimeout(amountTimer);
    amountTimer = window.setTimeout(() => form.requestSubmit(), 400);
  });

  form.addEventListener("change", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) return;

    if (target.name === "rate_mode") {
      syncHistoricalDateField(form);
      if (form.dataset.hasResult !== "true") return;

      if (target.value === "historical") {
        const requestedDate = form.querySelector<HTMLInputElement>("#id_requested_date");
        if (!requestedDate?.value) {
          requestedDate?.focus();
          return;
        }
      }

      form.requestSubmit();
      return;
    }

    if (form.dataset.hasResult !== "true") return;
    if (target.type === "hidden" || target.id === "id_amount") return;

    if (target.id === "id_requested_date") {
      const historical = form.querySelector<HTMLInputElement>(
        'input[name="rate_mode"][value="historical"]',
      );
      if (!historical?.checked || !target.value) return;
    }

    form.requestSubmit();
  });
}

function enhanceCurrentConverterBehavior(): void {
  const form = document.querySelector<HTMLFormElement>("[data-current-conversion-form]");
  if (form) enhanceAutoRefresh(form);
}

document.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof Element)) return;
  const swap = target.closest<HTMLButtonElement>("#swap-contexts");
  if (swap) restoreFocusId = swap.id;
});

document.addEventListener("htmx:beforeRequest", (event) => {
  const target = event.target;
  if (!(target instanceof Element) || !target.closest("[data-current-conversion-form]")) return;

  const note = document.querySelector<HTMLElement>("[data-previous-result-note]");
  if (note) {
    note.hidden = false;
    note.textContent = "Updating — this result still belongs to the previous inputs.";
  }
});

document.addEventListener("htmx:beforeSwap", (event) => {
  const detail = (
    event as CustomEvent<{
      xhr: XMLHttpRequest;
      shouldSwap: boolean;
      isError: boolean;
    }>
  ).detail;

  if (![422, 502, 503].includes(detail.xhr.status)) return;

  const note = document
    .getElementById("conversion-result-region")
    ?.querySelector<HTMLElement>("[data-previous-result-note]");
  if (note) {
    note.hidden = false;
    note.textContent =
      detail.xhr.status === 422
        ? "Previous result — fix the changed inputs to update it."
        : "Previous result — the new rate could not be loaded.";
  }

  detail.shouldSwap = true;
  detail.isError = false;
});

document.addEventListener("DOMContentLoaded", enhanceCurrentConverterBehavior);
document.addEventListener("htmx:afterSwap", () => {
  enhanceCurrentConverterBehavior();

  if (!restoreFocusId) return;
  document.getElementById(restoreFocusId)?.focus();
  restoreFocusId = null;
});

document.addEventListener("htmx:responseError", () => {
  restoreFocusId = null;
});

document.addEventListener("htmx:sendError", () => {
  restoreFocusId = null;
});
