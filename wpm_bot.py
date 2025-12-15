#!/usr/bin/env python3
"""
WPM Bot - Automated typing bot for https://wpm.silver.dev
Plays the coding typing game by reading code snippets and typing them automatically.
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Try to import undetected-chromedriver for better anti-detection
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("⚠️  undetected-chromedriver not available, using standard Selenium")


class WPMBot:
    def __init__(self, typing_speed=0.02, headless=False, use_undetected=True, gl_mode="auto"):
        """
        Initialize the WPM Bot.
        
        Args:
            typing_speed: Delay between each character (lower = faster)
            headless: Run browser in headless mode (NOT recommended - WebGL may not work)
            use_undetected: Use undetected-chromedriver if available (better anti-detection)
            gl_mode: Graphics backend: "auto" (try default then fallback), "angle", "swiftshader", "desktop"
        """
        self.typing_speed = typing_speed
        self.driver = None
        self.headless = headless
        self.use_undetected = use_undetected and UC_AVAILABLE
        self.gl_mode = gl_mode
        
        if headless:
            print("⚠️  Warning: Headless mode may cause WebGL issues. The game requires WebGL!")
        
    def _apply_gl_flags(self, add_argument):
        """
        Apply Chrome flags related to WebGL / GPU.
        We keep this conservative because the wrong GL backend on macOS can *disable* WebGL.
        """
        # If Chrome thinks your GPU is on a denylist, WebGL contexts can fail.
        add_argument("--ignore-gpu-blocklist")

        # Prefer ANGLE (Metal) on macOS; it's the most reliable for WebGL in automation.
        if self.gl_mode in ("auto", "angle"):
            add_argument("--use-gl=angle")
            add_argument("--use-angle=metal")
        elif self.gl_mode == "swiftshader":
            # Force software rendering (often works even when GPU/Metal is blocked)
            add_argument("--use-gl=swiftshader")
        elif self.gl_mode == "desktop":
            add_argument("--use-gl=desktop")

    def setup_driver(self):
        """Setup Chrome WebDriver with anti-detection measures."""
        if self.use_undetected:
            print("🛡️  Using undetected-chromedriver for better anti-detection...")
            options = uc.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            chrome_options.add_argument("--use-gl=angle")
            chrome_options.add_argument("--use-angle=swiftshader")
            chrome_options.add_argument("--enable-webgl")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox") # Often necessary for Linux/Docker environments


            self._apply_gl_flags(options.add_argument)
            
            self.driver = uc.Chrome(options=options, version_main=None)
            self.driver.implicitly_wait(10)
        else:
            print("🔧 Using standard Selenium with anti-detection measures...")
            chrome_options = Options()
            
            # Anti-detection measures
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Standard options
            if self.headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--use-gl=angle")
            chrome_options.add_argument("--use-angle=swiftshader")
            chrome_options.add_argument("--enable-webgl")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox") # Often necessary for Linux/Docker environments

            self._apply_gl_flags(chrome_options.add_argument)
            
            # Enable WebGL via preferences
            prefs = {
                "profile.default_content_setting_values": {
                    "webgl": 1
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Set a real user agent
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(10)

    def check_webgl_support(self):
        """
        Run a small in-page WebGL probe and print what we find.
        Returns True if a WebGL context can be created.
        """
        probe = """
        const canvas = document.createElement('canvas');
        const results = { webgl: false, webgl2: false, error: null, ua: navigator.userAgent };
        try {
          const gl = canvas.getContext('webgl');
          results.webgl = !!gl;
        } catch (e) { results.error = String(e); }
        try {
          const gl2 = canvas.getContext('webgl2');
          results.webgl2 = !!gl2;
        } catch (e) { results.error = results.error || String(e); }
        return results;
        """
        try:
            res = self.driver.execute_script(probe)
            print(f"🧪 WebGL probe: webgl={res.get('webgl')} webgl2={res.get('webgl2')} gl_mode={self.gl_mode}")
            if res.get("error"):
                print(f"🧪 WebGL probe error: {res.get('error')}")
            return bool(res.get("webgl") or res.get("webgl2"))
        except Exception as e:
            print(f"🧪 WebGL probe failed to run: {e}")
            return False
        
    def navigate_to_game(self):
        """Navigate to the WPM game website."""
        print("🌐 Navigating to wpm.silver.dev...")
        self.driver.get("https://wpm.silver.dev")
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(5)  # Give more time for the page to load
        
        # Check if page loaded
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("✅ Page loaded successfully")
        except:
            print("⚠️  Page may still be loading...")
        
        # Take a screenshot for debugging
        try:
            self.driver.save_screenshot("page_screenshot.png")
            print("📸 Screenshot saved as page_screenshot.png")
        except Exception as e:
            print(f"Could not save screenshot: {e}")

        # WebGL is required for this game (Kaplay/Kaboom). Probe it early.
        self.check_webgl_support()
        
    def print_screen(self):
        """Print the current screen content for debugging."""
        print("\n" + "="*60)
        print("📺 CURRENT SCREEN CONTENT:")
        print("="*60)
        try:
            # Get page source info
            print(f"Page URL: {self.driver.current_url}")
            print(f"Page Title: {self.driver.title}")
            print(f"Page Ready State: {self.driver.execute_script('return document.readyState')}")
            
            # Check for common elements
            body = self.driver.find_element(By.TAG_NAME, "body")
            body_text = body.text[:2000] if len(body.text) > 2000 else body.text
            print(f"\nBody text length: {len(body.text)}")
            print(f"Body text preview:\n{body_text}")
            
            # Check for any visible elements
            try:
                all_elements = self.driver.find_elements(By.XPATH, "//*")
                visible_count = sum(1 for el in all_elements[:50] if el.is_displayed())
                print(f"\nVisible elements (first 50 checked): {visible_count}")
            except:
                pass
                
        except Exception as e:
            print(f"Could not get screen content: {e}")
            import traceback
            traceback.print_exc()
        print("="*60 + "\n")
        
    def find_input_and_type(self, text):
        """Find the active input element and type into it."""
        # Try different strategies to find the input
        input_selectors = [
            "input[type='text']",
            "input:not([type='hidden'])",
            "textarea",
            "[contenteditable='true']",
            "input",
        ]
        
        input_element = None
        for selector in input_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.is_enabled():
                        input_element = el
                        break
                if input_element:
                    break
            except:
                continue
        
        if not input_element:
            # Try focusing the body and typing directly
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.click()
            time.sleep(0.5)
            
            # Type using Actions
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            for char in text:
                actions.send_keys(char)
                actions.perform()
                actions = ActionChains(self.driver)
                time.sleep(self.typing_speed)
            return
        
        input_element.click()
        time.sleep(0.3)
        
        for char in text:
            input_element.send_keys(char)
            time.sleep(self.typing_speed)
            
    def type_with_actions(self, text):
        """Type text using ActionChains (useful when no specific input is focused)."""
        from selenium.webdriver.common.action_chains import ActionChains
        
        actions = ActionChains(self.driver)
        for char in text:
            if char == '\n':
                actions.send_keys(Keys.ENTER)
            elif char == '\t':
                actions.send_keys(Keys.TAB)
            else:
                actions.send_keys(char)
            actions.perform()
            actions = ActionChains(self.driver)
            time.sleep(self.typing_speed)
            
    def start_game(self):
        """Start the game by typing 'start'."""
        print("🎮 Starting the game by typing 'start'...")
        time.sleep(1)
        
        self.print_screen()
        
        # Click on the page first to focus
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.click()
        except:
            pass
        
        time.sleep(0.5)
        self.type_with_actions("start")
        time.sleep(1)
        self.type_with_actions("\n")
        time.sleep(2)
        
        self.print_screen()
        
    def select_python(self):
        """Select Python as the language."""
        print("🐍 Selecting Python language...")
        
        time.sleep(1)
        self.type_with_actions("python")
        time.sleep(0.5)
        self.type_with_actions("\n")
        time.sleep(2)
        
        self.print_screen()
        
    def get_code_snippet(self):
        """Extract the code snippet to type from the screen."""
        print("📝 Extracting code snippet...")
        
        # Try various selectors that might contain the code
        code_selectors = [
            "pre code",
            "code",
            "pre",
            ".code",
            ".snippet",
            "[class*='code']",
            "[class*='text']",
            "[class*='prompt']",
            ".typing-text",
            "#text",
            ".text-to-type",
        ]
        
        code_text = ""
        
        for selector in code_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for el in elements:
                    if el.is_displayed() and el.text.strip():
                        text = el.text.strip()
                        if len(text) > 10:  # Likely actual code content
                            code_text = text
                            print(f"Found code using selector: {selector}")
                            break
                if code_text:
                    break
            except:
                continue
        
        if not code_text:
            # Try to get all visible text and find the code section
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                all_text = body.text
                # The code is usually the longest continuous block
                print("Attempting to extract code from page body...")
                code_text = all_text
            except:
                pass
        
        print("\n" + "="*60)
        print("📋 CODE SNIPPET TO TYPE:")
        print("="*60)
        print(code_text)
        print("="*60 + "\n")
        
        return code_text
        
    def type_code(self, code):
        """Type the code snippet character by character."""
        print(f"⌨️  Typing code ({len(code)} characters)...")
        
        # Focus on the typing area
        try:
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.click()
        except:
            pass
        
        time.sleep(0.5)
        
        char_count = 0
        total_chars = len(code)
        
        for char in code:
            self.type_with_actions(char)
            char_count += 1
            
            # Progress update every 50 characters
            if char_count % 50 == 0:
                progress = (char_count / total_chars) * 100
                print(f"   Progress: {char_count}/{total_chars} ({progress:.1f}%)")
        
        print(f"✅ Finished typing {char_count} characters!")
        
    def run(self):
        """Run the full bot sequence."""
        try:
            print("\n" + "🤖 WPM Bot Starting..." + "\n")
            
            self.setup_driver()
            self.navigate_to_game()

            # If WebGL is not available, auto-fallback to SwiftShader (software WebGL).
            if self.gl_mode == "auto" and not self.check_webgl_support():
                print("⚠️  WebGL is not available in this Chrome session. Restarting with SwiftShader (software WebGL)...")
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
                self.gl_mode = "swiftshader"
                self.setup_driver()
                self.navigate_to_game()
                if not self.check_webgl_support():
                    print("❌ Still no WebGL after SwiftShader fallback.")
                    print("   Next steps:")
                    print("   - Ensure Chrome 'Use hardware acceleration' is enabled")
                    print("   - Try running: python wpm_bot.py 0.015 --gl=angle OR --gl=swiftshader")
                    print("   - Open `chrome://gpu` in normal Chrome and confirm WebGL is enabled")
            
            # Start the game
            self.start_game()
            
            # Select Python
            self.select_python()
            
            # Wait for the game to load the code
            time.sleep(2)
            
            # Get the code snippet
            code = self.get_code_snippet()
            
            if code:
                # Type the code
                self.type_code(code)
                
                # Wait to see results
                time.sleep(3)
                self.print_screen()
            else:
                print("❌ Could not extract code snippet!")
                
            print("\n🏁 Bot finished! Press Enter to close browser...")
            input()
            
        except KeyboardInterrupt:
            print("\n⚠️  Bot interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Browser closed.")


def main():
    # Typing speed: lower = faster (0.01 = very fast, 0.1 = slower)
    typing_speed = 0.015
    gl_mode = "auto"
    
    # Very small arg parser:
    # - positional 1: typing_speed
    # - optional: --gl=auto|angle|swiftshader|desktop
    for arg in sys.argv[1:]:
        if arg.startswith("--gl="):
            gl_mode = arg.split("=", 1)[1].strip()
        else:
            try:
                typing_speed = float(arg)
            except ValueError:
                print(f"Invalid argument: {arg}")
    
    print(f"⚡ Typing speed set to: {typing_speed}s per character")
    print(f"🖥️  GL mode: {gl_mode}")
    
    bot = WPMBot(typing_speed=typing_speed, gl_mode=gl_mode)
    bot.run()


if __name__ == "__main__":
    main()

