# simple_test.py
# Basic test to see what the Flutter app actually shows

import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("🔧 Loading Flutter app...")
        
        # Navigate to Flutter web app
        await page.goto("http://localhost:36349/")
        
        # Wait for app to load
        await page.wait_for_timeout(8000)
        
        # Take screenshot to see what's displayed
        await page.screenshot(path='flutter_app_screenshot.png')
        print("📸 Screenshot saved as flutter_app_screenshot.png")
        
        # Get page content to see what's available
        content = await page.content()
        print("📝 Page title:", await page.title())
        
        # Look for any text content
        text_elements = await page.query_selector_all('*')
        print("🔍 Found elements on page:")
        
        # Try to find common elements
        common_texts = ['Login', 'Welcome', 'Email', 'Password', 'Register', 'Dating']
        for text in common_texts:
            count = await page.locator(f'text={text}').count()
            if count > 0:
                print(f"   ✅ Found '{text}' ({count} times)")
            else:
                print(f"   ❌ No '{text}' found")
        
        # Check what's actually visible
        print("🔍 Looking for any input fields...")
        inputs = await page.query_selector_all('input')
        print(f"   Found {len(inputs)} input fields")
        
        print("🔍 Looking for any buttons...")
        buttons = await page.query_selector_all('button')
        print(f"   Found {len(buttons)} buttons")
        
        await browser.close()
        print("✅ Basic test completed!")

if __name__ == "__main__":
    asyncio.run(run())
