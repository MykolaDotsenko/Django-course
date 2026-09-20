let restoreFocusId: string | null = null;

document.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof Element)) return;
  const swap = target.closest<HTMLButtonElement>("#swap-contexts");
  if (swap) restoreFocusId = swap.id;
});

document.addEventListener("htmx:afterSwap", () => {
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
