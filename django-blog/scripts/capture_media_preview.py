from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


BASE_URL = os.environ.get(
    "MEDIA_PREVIEW_URL",
    "http://127.0.0.1:8000/_design/media/",
)
OUTPUT_DIR = Path(
    os.environ.get(
        "MEDIA_PREVIEW_SCREENSHOT_DIR",
        "artifacts/media-preview",
    )
)

VIEWPORTS = (
    ("desktop-1440", 1440, 1200),
    ("tablet-768", 768, 1024),
    ("mobile-390", 390, 844),
)


def _load_lazy_images(page: Page) -> None:
    """Bring every preview image into the loading viewport before validation."""

    images = page.locator("img")
    for index in range(images.count()):
        image = images.nth(index)
        image.scroll_into_view_if_needed()
        image.evaluate(
            """element => element.complete
                ? Promise.resolve()
                : new Promise((resolve, reject) => {
                    element.addEventListener("load", resolve, {once: true});
                    element.addEventListener("error", reject, {once: true});
                })"""
        )

    page.evaluate("window.scrollTo(0, 0)")


def _assert_preview_integrity(page: Page) -> None:
    title = page.locator("h1").inner_text()
    if title.strip() != "Quiet Atlas media system":
        raise RuntimeError(f"Unexpected preview heading: {title!r}")

    image_count = page.locator("img").count()
    if image_count != 32:
        raise RuntimeError(
            f"Expected 32 preview images, found {image_count}",
        )

    broken_images = page.locator("img").evaluate_all(
        """images => images
            .filter(image => !image.complete || image.naturalWidth === 0)
            .map(image => image.src)"""
    )
    if broken_images:
        raise RuntimeError(
            "Broken preview images: " + ", ".join(broken_images),
        )

    overflow = page.evaluate(
        """() => ({
            scrollWidth: document.documentElement.scrollWidth,
            clientWidth: document.documentElement.clientWidth,
        })"""
    )
    if overflow["scrollWidth"] > overflow["clientWidth"] + 1:
        raise RuntimeError(
            "Horizontal overflow detected: "
            f"{overflow['scrollWidth']} > {overflow['clientWidth']}",
        )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        for name, width, height in VIEWPORTS:
            context = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=1,
            )
            page = context.new_page()
            console_errors: list[str] = []

            page.on(
                "console",
                lambda message: (
                    console_errors.append(message.text)
                    if message.type == "error"
                    else None
                ),
            )

            response = page.goto(BASE_URL, wait_until="networkidle")
            if response is None or not response.ok:
                status = response.status if response else "no response"
                raise RuntimeError(
                    f"Preview request failed for {name}: {status}",
                )

            _load_lazy_images(page)
            _assert_preview_integrity(page)

            if console_errors:
                raise RuntimeError(
                    f"Browser console errors for {name}: "
                    + " | ".join(console_errors),
                )

            page.screenshot(
                path=str(OUTPUT_DIR / f"{name}.png"),
                full_page=True,
            )
            context.close()

        browser.close()


if __name__ == "__main__":
    main()
