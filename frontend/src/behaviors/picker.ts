import Combobox from "@github/combobox-nav";

const activeComboboxes = new WeakMap<HTMLInputElement, Combobox>();

function formForDialog(dialog: HTMLDialogElement): HTMLFormElement | null {
  return document.querySelector<HTMLFormElement>("[data-current-conversion-form]");
}

function refreshAfterSelection(form: HTMLFormElement): void {
  if (form.dataset.hasResult === "true") {
    form.requestSubmit();
  }
}

function commitOption(dialog: HTMLDialogElement, option: HTMLElement): void {
  const side = dialog.dataset.pickerDialog;
  const form = formForDialog(dialog);
  if (!side || !form) return;

  const countrySelect = form.querySelector<HTMLSelectElement>(`[name="${side}_country"]`);
  const currencySelect = form.querySelector<HTMLSelectElement>(`[name="${side}_currency"]`);
  const trigger = document.querySelector<HTMLButtonElement>(`[data-picker-trigger="${side}"]`);
  if (!countrySelect || !currencySelect || !trigger) return;

  const countryCode = option.dataset.countryCode ?? "";
  const currencyCode = option.dataset.currencyCode ?? "";
  if (!currencyCode) return;

  countrySelect.value = countryCode;
  currencySelect.value = currencyCode;

  const media = trigger.querySelector<HTMLElement>(".qa-selector-trigger__media");
  const country = trigger.querySelector<HTMLElement>(".qa-selector-trigger__country");
  const currency = trigger.querySelector<HTMLElement>(".qa-selector-trigger__currency");

  if (media) media.textContent = countryCode || currencyCode || "FX";
  if (country) country.textContent = option.dataset.countryName || "No country context";
  if (currency) {
    const currencyName = option.dataset.currencyName || currencyCode;
    currency.textContent = `${currencyName} · ${currencyCode}`;
  }

  const input = dialog.querySelector<HTMLInputElement>('input[type="search"]');
  if (input) input.value = "";

  dialog.close();
  refreshAfterSelection(form);
}

function wireCombobox(dialog: HTMLDialogElement): void {
  const input = dialog.querySelector<HTMLInputElement>('input[role="combobox"]');
  const list = dialog.querySelector<HTMLElement>('[role="listbox"]');
  if (!input || !list) return;

  activeComboboxes.get(input)?.destroy();

  const combobox = new Combobox(input, list, {
    tabInsertsSuggestions: false,
    firstOptionSelectionMode: "none",
    scrollIntoViewOptions: { block: "nearest" },
  });
  combobox.start();
  activeComboboxes.set(input, combobox);

  if (list.dataset.commitWired !== "true") {
    list.dataset.commitWired = "true";
    list.addEventListener("combobox-commit", (event) => {
      const target = event.target;
      const option =
        target instanceof Element ? target.closest<HTMLElement>("[data-picker-option]") : null;
      if (option) commitOption(dialog, option);
    });
  }
}

function enhanceDialog(dialog: HTMLDialogElement): void {
  const side = dialog.dataset.pickerDialog;
  if (!side) return;

  if (dialog.dataset.enhanced !== "true") {
    dialog.dataset.enhanced = "true";
    const trigger = document.querySelector<HTMLButtonElement>(`[data-picker-trigger="${side}"]`);
    const fallback = document.querySelector<HTMLElement>(`[data-native-selection="${side}"]`);
    const close = dialog.querySelector<HTMLButtonElement>(`[data-picker-close="${side}"]`);

    if (trigger) {
      trigger.hidden = false;
      trigger.addEventListener("click", () => {
        if (!dialog.open) dialog.showModal();
        dialog.querySelector<HTMLInputElement>('input[type="search"]')?.focus();
      });
    }
    if (fallback) fallback.hidden = true;
    close?.addEventListener("click", () => dialog.close());
  }

  wireCombobox(dialog);
}

function enhanceAutoRefresh(form: HTMLFormElement): void {
  if (form.dataset.autoRefreshWired === "true") return;
  form.dataset.autoRefreshWired = "true";

  form.addEventListener("change", (event) => {
    if (form.dataset.hasResult !== "true") return;
    const target = event.target;
    if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) return;
    if (target.type === "hidden") return;
    form.requestSubmit();
  });
}

export function enhanceCurrentConverter(): void {
  const form = document.querySelector<HTMLFormElement>("[data-current-conversion-form]");
  if (form) enhanceAutoRefresh(form);

  for (const dialog of document.querySelectorAll<HTMLDialogElement>("[data-picker-dialog]")) {
    enhanceDialog(dialog);
  }
}

document.addEventListener("DOMContentLoaded", enhanceCurrentConverter);
document.addEventListener("htmx:afterSwap", enhanceCurrentConverter);
