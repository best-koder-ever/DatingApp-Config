# test_login.py
# Simple Playwright E2E test for logging in to the Flutter web app

import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        # Use the Flutter dev server URL as the entrypoint for the web app
        await page.goto("http://localhost:36349/")

        # Wait for the login form to appear (update selectors as needed)
        await page.wait_for_selector('input[type="email"]')
        await page.fill('input[type="email"]', 'TestUser1@example.com')
        await page.fill('input[type="password"]', 'TestUser1!')
        await page.click('button[type="submit"]')

        # Wait for a successful login indication (update selector as needed)
        # Example: check for a dashboard or logout button
        try:
            await page.wait_for_selector('text=Logout', timeout=5000)
            print("Login test passed!")
        except Exception:
            print("Login test failed or selector not found.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
