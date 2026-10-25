import asyncio
import base64
import json
from pathlib import Path

from playwright.async_api import async_playwright


INPUT_FILE = "urls.input"
OUTPUT_DIR = Path("output")
BROWSER_TIMEOUT = 300000


def list_urls(filename: str) -> list[str]:
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def save(data: dict, index: int) -> None:
    url_dir = OUTPUT_DIR / f"url_{index}"
    url_dir.mkdir(parents=True, exist_ok=True)

    output_path = url_dir / "browse.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    screenshot_path = url_dir / "screenshot.png"

    with open(screenshot_path, "wb") as file:
        file.write(base64.b64decode(data["screenshot"]))


async def scrape_websites(urls: list[str]) -> None:

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        try:

            page = await browser.new_page()

            for index, url in enumerate(urls, start=1):
                try:
                    await page.goto(
                        url,
                        wait_until="load",
                        timeout=BROWSER_TIMEOUT,
                    )

                    html = await page.content()

                    links = await page.locator("a[href]").evaluate_all(
                        "(elements) => elements.map(element => element.href)"
                    )

                    screenshot_bytes = await page.screenshot(full_page=True)
                    screenshot_base64 = base64.b64encode(
                        screenshot_bytes
                    ).decode("utf-8")

                    data = {
                        "url": url,
                        "html": html,
                        "links": links,
                        "screenshot": screenshot_base64,
                    }

                    save(data, index)
                    print(f"Successfully scraped: {url}")

                except Exception as error:
                    print(f"Failed to scrape {url}: {error}")

        finally:
            # CHANGED: Await browser cleanup.
            await browser.close()


def main() -> None:
    urls = list_urls(INPUT_FILE)

    # CHANGED: Run the asynchronous function.
    asyncio.run(scrape_websites(urls))\
    


if __name__ == "__main__":
    main()