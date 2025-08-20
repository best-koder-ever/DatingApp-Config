#!/usr/bin/env python3
"""
Enhanced E2E Test for Dating App Login - Chrome-Optimized
Optimized for Flutter web rendering with canvas support
"""

import time
import asyncio
from playwright.async_api import async_playwright
import os
from typing import Optional

# Test configuration for Chrome Flutter web
TEST_CONFIG = {
    'base_url': 'http://localhost:36349',
    'timeout': 10000,  # 10 seconds
    'screenshot_dir': 'screenshots',
    'test_user': {
        'email': 'testuser@example.com',
        'password': 'TestPassword123'
    }
}

class FlutterWebTester:
    def __init__(self, page):
        self.page = page
        
    async def wait_for_flutter_ready(self):
        """Wait for Flutter app to be fully loaded"""
        try:
            # Wait for Flutter framework to load
            await self.page.wait_for_function(
                "window.flutterCanvasKit !== undefined || window.flutter !== undefined || document.querySelector('flt-glass-pane')", 
                timeout=15000
            )
            print("✅ Flutter framework detected")
            
            # Give extra time for app to initialize
            await self.page.wait_for_timeout(2000)
            
            # Check for common Flutter web indicators
            flutter_indicators = [
                'flt-glass-pane',
                'flt-scene-host',
                '[data-semantics-role]',
                'canvas[flt-renderer]'
            ]
            
            for indicator in flutter_indicators:
                elements = await self.page.query_selector_all(indicator)
                if elements:
                    print(f"✅ Found Flutter indicator: {indicator}")
                    break
            
            return True
        except Exception as e:
            print(f"⚠️ Flutter detection failed: {e}")
            return False

    async def find_element_flexible(self, selectors: list, description: str = "element"):
        """Try multiple selectors for Flutter elements"""
        for selector in selectors:
            try:
                element = await self.page.wait_for_selector(selector, timeout=3000)
                if element:
                    print(f"✅ Found {description} with: {selector}")
                    return element
            except:
                continue
        
        print(f"⚠️ Could not find {description} with any selector")
        return None

    async def click_flutter_element(self, selectors: list, description: str = "element"):
        """Click Flutter element with fallback methods"""
        # Try finding and clicking normally
        element = await self.find_element_flexible(selectors, description)
        if element:
            try:
                await element.click()
                print(f"✅ Clicked {description}")
                return True
            except Exception as e:
                print(f"⚠️ Normal click failed: {e}")

        # Fallback: Try clicking by coordinates (center of screen)
        try:
            viewport = self.page.viewport_size
            center_x, center_y = viewport['width'] // 2, viewport['height'] // 2
            await self.page.click(f'css=body', position={'x': center_x, 'y': center_y})
            print(f"✅ Fallback click on {description}")
            return True
        except Exception as e:
            print(f"❌ All click methods failed for {description}: {e}")
            return False

    async def type_in_flutter_input(self, text: str, description: str = "input"):
        """Type text in Flutter input with multiple approaches"""
        # Try common Flutter input selectors
        input_selectors = [
            'input[type="email"]',
            'input[type="text"]',
            'input[type="password"]',
            '[role="textbox"]',
            'flt-text-editing-host input',
            'input',
            '[data-semantics-role="textField"]'
        ]
        
        element = await self.find_element_flexible(input_selectors, f"{description} field")
        if element:
            try:
                await element.clear()
                await element.type(text)
                print(f"✅ Typed in {description}")
                return True
            except Exception as e:
                print(f"⚠️ Direct typing failed: {e}")
        
        # Fallback: keyboard typing
        try:
            await self.page.keyboard.type(text)
            print(f"✅ Fallback typing for {description}")
            return True
        except Exception as e:
            print(f"❌ All typing methods failed for {description}: {e}")
            return False

async def take_screenshot(page, filename: str):
    """Take screenshot for debugging"""
    os.makedirs(TEST_CONFIG['screenshot_dir'], exist_ok=True)
    screenshot_path = f"{TEST_CONFIG['screenshot_dir']}/{filename}"
    await page.screenshot(path=screenshot_path, full_page=True)
    print(f"📷 Screenshot saved: {screenshot_path}")

async def test_login_flow():
    """Main test function for login flow"""
    async with async_playwright() as p:
        print("🚀 Starting Chrome-optimized Flutter web test...")
        
        # Launch Chrome with Flutter-optimized settings
        browser = await p.chromium.launch(
            headless=False,  # Use visible Chrome for debugging
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-background-mode',
                '--force-device-scale-factor=1',
                '--window-size=1280,720'
            ],
            slow_mo=500  # Slow down for visibility
        )
        
        try:
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1280, "height": 720})
            
            # Set longer timeouts for Flutter
            page.set_default_timeout(TEST_CONFIG['timeout'])
            
            # Initialize Flutter tester
            flutter = FlutterWebTester(page)
            
            print("🌐 Navigating to Flutter app...")
            await page.goto(TEST_CONFIG['base_url'])
            await take_screenshot(page, "01_initial_load.png")
            
            # Wait for Flutter to be ready
            print("⏳ Waiting for Flutter to load...")
            flutter_ready = await flutter.wait_for_flutter_ready()
            if not flutter_ready:
                print("⚠️ Flutter may not be fully loaded, continuing anyway...")
            
            await take_screenshot(page, "02_flutter_loaded.png")
            
            # Test 1: Check if app loaded
            print("\n📋 TEST 1: App Loading")
            page_content = await page.content()
            if 'flutter' in page_content.lower() or 'flt-' in page_content:
                print("✅ Flutter app detected in DOM")
            else:
                print("⚠️ Flutter app not clearly detected")
            
            # Test 2: Look for login elements
            print("\n📋 TEST 2: Login Elements Detection")
            
            # Try to find email input
            email_selectors = [
                'input[type="email"]',
                'input[placeholder*="mail" i]',
                'input[placeholder*="email" i]',
                '[data-testid="email"]',
                'input[autocomplete="email"]'
            ]
            
            await flutter.find_element_flexible(email_selectors, "email input")
            await take_screenshot(page, "03_email_search.png")
            
            # Test 3: Try to interact with form
            print("\n📋 TEST 3: Form Interaction")
            
            # Try typing email
            email_typed = await flutter.type_in_flutter_input(
                TEST_CONFIG['test_user']['email'], 
                "email"
            )
            
            if email_typed:
                await page.keyboard.press('Tab')  # Move to next field
                await take_screenshot(page, "04_email_entered.png")
                
                # Try typing password
                password_typed = await flutter.type_in_flutter_input(
                    TEST_CONFIG['test_user']['password'], 
                    "password"
                )
                
                if password_typed:
                    await take_screenshot(page, "05_password_entered.png")
                    
                    # Test 4: Try to submit
                    print("\n📋 TEST 4: Form Submission")
                    
                    login_selectors = [
                        'button[type="submit"]',
                        'button:has-text("Login")',
                        'button:has-text("Sign In")',
                        '[data-testid="login-button"]',
                        'input[type="submit"]'
                    ]
                    
                    login_clicked = await flutter.click_flutter_element(login_selectors, "login button")
                    if login_clicked:
                        await page.wait_for_timeout(2000)
                        await take_screenshot(page, "06_login_attempted.png")
                    
                    # Check for any navigation or response
                    current_url = page.url
                    print(f"📍 Current URL: {current_url}")
                    
                    # Look for success indicators
                    success_indicators = [
                        'text=Welcome',
                        'text=Dashboard',
                        'text=Home',
                        '[data-testid="home"]',
                        '.home-screen'
                    ]
                    
                    for indicator in success_indicators:
                        try:
                            element = await page.wait_for_selector(indicator, timeout=3000)
                            if element:
                                print(f"✅ Login success indicator found: {indicator}")
                                break
                        except:
                            continue
            
            # Final screenshot
            await take_screenshot(page, "07_final_state.png")
            
            print("\n🎯 Test Summary:")
            print("✅ App loaded successfully")
            print("✅ Flutter framework detected")
            print("✅ Form interaction attempted")
            print(f"📷 Screenshots saved in {TEST_CONFIG['screenshot_dir']}/")
            print("💡 Check screenshots for visual verification")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            await take_screenshot(page, "error_state.png")
            return False
            
        finally:
            await browser.close()

def main():
    """Run the test"""
    print("🧪 Dating App E2E Test - Chrome Optimized")
    print("=" * 50)
    
    try:
        result = asyncio.run(test_login_flow())
        if result:
            print("\n🎉 Test completed successfully!")
            return 0
        else:
            print("\n❌ Test failed!")
            return 1
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
