let restoreFocusId: string | null = null;
let focusFeedbackAfterSwap = false;

type HtmxRequestDetail = {
  elt?: Element;
  target?: Element;
  xhr?: XMLHttpRequest;
  shouldSwap?: boolean;
  isError?: boolean;
};

function htmxDetail(event: Event): HtmxRequestDetail {
  return (event as CustomEvent<HtmxRequestDetail>).detail ?? {};
}

function targetsConverterPanel(event: Event): boolean {
  const detail = htmxDetail(event);
  if (detail.target instanceof Element) return detail.target.id === "converter-panel";

  const requester =
    detail.elt instanceof Element
      ? detail.elt
      : event.target instanceof Element
        ? event.target
        : null;
  const targetOwner = requester?.closest<HTMLElement>("[hx-target]");
  return targetOwner?.getAttribute("hx-target") === "#converter-panel";
}

function setConversionBusy(busy: boolean): void {
  const region = document.getElementById("conversion-result-region");
  if (!region) return;
  if (busy) {
    region.setAttribute("aria-busy", "true");
  } else {
    region.removeAttribute("aria-busy");
  }
}

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

  form.addEventListener("submit", (event) => {
    const submitter = (event as SubmitEvent).submitter;
    focusFeedbackAfterSwap =
      submitter instanceof HTMLButtonElement && submitter.classList.contains("qa-primary-button");
  });

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

function announceConversionResult(target: EventTarget | null, status: number | undefined): void {
  if (status !== 200 || !(target instanceof Element) || target.id !== "converter-panel") return;

  const announcer = document.getElementById("conversion-announcer");
  const payload = target.querySelector<HTMLElement>("[data-conversion-announcement]");
  const message = payload?.textContent?.trim();
  if (!announcer || !message) return;

  announcer.textContent = "";
  window.setTimeout(() => {
    announcer.textContent = message;
  }, 0);
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
  if (!targetsConverterPanel(event)) return;

  setConversionBusy(true);
  const note = document.querySelector<HTMLElement>("[data-previous-result-note]");
  if (note) {
    note.hidden = false;
    note.textContent = "Updating — this result still belongs to the previous inputs.";
  }
});

document.addEventListener("htmx:beforeSwap", (event) => {
  const detail = htmxDetail(event);
  const status = detail.xhr?.status;
  if (status === undefined || ![422, 502, 503].includes(status)) return;

  if (targetsConverterPanel(event)) {
    const note = document
      .getElementById("conversion-result-region")
      ?.querySelector<HTMLElement>("[data-previous-result-note]");
    if (note) {
      note.hidden = false;
      note.textContent =
        status === 422
          ? "Previous result — fix the changed inputs to update it."
          : "Previous result — the new rate could not be loaded.";
    }
  }

  detail.shouldSwap = true;
  detail.isError = false;
});

document.addEventListener("DOMContentLoaded", enhanceCurrentConverterBehavior);
document.addEventListener("htmx:afterSwap", (event) => {
  enhanceCurrentConverterBehavior();
  const detail = htmxDetail(event);
  const converterSwap = targetsConverterPanel(event);

  if (converterSwap) {
    setConversionBusy(false);
    announceConversionResult(event.target, detail.xhr?.status);

    if (focusFeedbackAfterSwap && [422, 502, 503].includes(detail.xhr?.status ?? 0)) {
      const feedback =
        document.getElementById("conversion-error-summary") ??
        document.getElementById("conversion-error-alert");
      feedback?.focus();
    }
    focusFeedbackAfterSwap = false;
  }

  if (!restoreFocusId) return;
  document.getElementById(restoreFocusId)?.focus();
  restoreFocusId = null;
});

function resetRequestUiState(): void {
  setConversionBusy(false);
  focusFeedbackAfterSwap = false;
  restoreFocusId = null;
}

document.addEventListener("htmx:responseError", resetRequestUiState);
document.addEventListener("htmx:sendError", resetRequestUiState);
