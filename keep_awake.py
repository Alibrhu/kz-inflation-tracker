"""
Keeps the Streamlit Community Cloud site from falling asleep.

Free Streamlit apps sleep after a while without visitors. This script opens the
site in a headless browser (like a real visitor) and, if the app is asleep,
clicks the "Yes, get this app back up!" button.

Run by GitHub Actions every few hours: .github/workflows/keep_awake.yml
"""

import sys

from playwright.sync_api import sync_playwright

SITE_URL = "https://shymkent-prices.streamlit.app/"
WAKE_BUTTON = "get this app back up"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(SITE_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(10_000)

        button = page.get_by_role("button", name=WAKE_BUTTON)
        if button.count():
            print("App was asleep, waking it up")
            button.first.click()
            page.wait_for_timeout(90_000)  # give the app time to start
        else:
            print("App is awake")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
