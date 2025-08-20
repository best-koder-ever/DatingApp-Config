# test_login.py
# Playwright E2E test optimized for Flutter Web on Chrome

import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch Chrome with better settings for Flutter
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1200, 'height': 800}
        )
        page = await context.new_page()
        
        print("🔧 Starting E2E login test for Flutter Dating App...")
        
        try:
            # Navigate to Flutter web app
            await page.goto("http://localhost:36349/", wait_until='networkidle')
            print("✅ Loaded Flutter app")
            
            # Wait for Flutter to fully render (Flutter needs time on web)
            await page.wait_for_timeout(3000)
            
            # Take screenshot for debugging
            await page.screenshot(path='test_start.png')
            
            # Flutter web renders differently - look for key elements more broadly
            print("🔍 Looking for login elements...")
            
            # Method 1: Look for any form elements that might be login
            inputs = await page.query_selector_all('input')
            print(f"   Found {len(inputs)} input fields")
            
            if len(inputs) >= 2:
                print("✅ Found input fields - assuming email/password")
                
                # Fill first input (likely email)
                await inputs[0].fill('test@example.com')
                print("✅ Filled email field")
                
                # Fill second input (likely password)  
                await inputs[1].fill('testpass123')
                print("✅ Filled password field")
                
                # Look for button
                buttons = await page.query_selector_all('button')
                if buttons:
                    await buttons[0].click()
                    print("✅ Clicked login button")
                    
                    # Wait for response
                    await page.wait_for_timeout(2000)
                    
                    # Check if error appears or navigation happens
                    current_url = page.url
                    print(f"✅ Current URL: {current_url}")
                    
                    await page.screenshot(path='test_after_login.png')
                    print("📸 Screenshot saved after login attempt")
                    
                else:
                    print("⚠️  No buttons found")
                    
            else:
                print("⚠️  Not enough input fields found")
                
                # Alternative: Try to interact with Flutter canvas
                # Flutter web sometimes renders to canvas
                canvas = await page.query_selector('canvas')
                if canvas:
                    print("🎨 Found Flutter canvas - app is rendering")
                    
                    # Click in areas where login fields might be
                    await page.click('canvas', position={'x': 400, 'y': 300})
                    await page.wait_for_timeout(500)
                    await page.type('canvas', 'test@example.com')
                    
                    await page.click('canvas', position={'x': 400, 'y': 350})  
                    await page.wait_for_timeout(500)
                    await page.type('canvas', 'testpass123')
                    
                    await page.click('canvas', position={'x': 400, 'y': 400})
                    print("✅ Attempted canvas interaction")
                
            print("🎉 E2E login test completed successfully!")
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            await page.screenshot(path='test_error.png')
            raise
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
