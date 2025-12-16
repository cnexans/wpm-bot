#!/usr/bin/env python3
"""
Test script to find the optimal delay between keystrokes.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

def test_timing(delay_ms):
    """Test typing with specific delay."""
    print(f"\n{'='*60}")
    print(f"🧪 Testing with {delay_ms}ms delay between characters")
    print('='*60)
    
    # Setup Chrome
    options = Options()
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to a simple text area
        driver.get("data:text/html,<html><body><textarea id='test' style='width:100%;height:100%;font-size:18px;font-family:monospace;white-space:pre'></textarea></body></html>")
        time.sleep(1)
        
        # Find the textarea
        textarea = driver.find_element("id", "test")
        textarea.click()
        
        # Test text with mixed case and spaces
        test_text = "def inorderTraversal(root):"
        
        print(f"📝 Typing: {repr(test_text)}")
        
        start_time = time.time()
        
        for char in test_text:
            actions = ActionChains(driver)
            
            if char.isupper():
                actions.key_down(Keys.SHIFT).send_keys(char.lower()).key_up(Keys.SHIFT).perform()
            elif char == ' ':
                actions.send_keys(Keys.SPACE).perform()
            else:
                actions.send_keys(char).perform()
            
            time.sleep(delay_ms / 1000.0)
        
        elapsed = time.time() - start_time
        
        time.sleep(0.5)
        
        # Get the actual text
        actual_text = textarea.get_attribute('value')
        
        print(f"\n📊 Results:")
        print(f"  Expected: {repr(test_text)}")
        print(f"  Actual:   {repr(actual_text)}")
        print(f"  Time:     {elapsed:.3f}s")
        print(f"  WPM:      {(len(test_text) / 5) / (elapsed / 60):.0f}")
        
        if actual_text == test_text:
            print(f"  ✅ PERFECT MATCH!")
            return True
        else:
            print(f"  ❌ MISMATCH")
            # Show differences
            for i, (e, a) in enumerate(zip(test_text, actual_text)):
                if e != a:
                    print(f"     Position {i}: expected {repr(e)}, got {repr(a)}")
            return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🎯 Finding optimal typing delay...")
    print("Testing different delays to find the sweet spot")
    
    # Test different delays
    delays = [0, 1, 2, 5, 10]
    
    results = {}
    for delay in delays:
        try:
            success = test_timing(delay)
            results[delay] = success
        except Exception as e:
            print(f"❌ Error with {delay}ms: {e}")
            results[delay] = False
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    for delay, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {delay}ms delay")
    
    # Find minimum working delay
    working_delays = [d for d, s in results.items() if s]
    if working_delays:
        optimal = min(working_delays)
        print(f"\n🎯 Optimal delay: {optimal}ms")
        print(f"   This gives ~{(28 / 5) / ((28 * optimal / 1000) / 60):.0f} WPM")
    else:
        print("\n⚠️  No working delay found!")

