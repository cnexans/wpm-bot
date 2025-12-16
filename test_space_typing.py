#!/usr/bin/env python3
"""
Test script to verify space characters are typed correctly.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

def test_space_typing():
    """Test typing text with spaces."""
    print("🧪 Testing space character typing...")
    
    # Setup Chrome
    options = Options()
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to a simple text area
        driver.get("data:text/html,<html><body><textarea id='test' style='width:100%;height:100%;font-size:24px;font-family:monospace'></textarea></body></html>")
        time.sleep(1)
        
        # Find the textarea
        textarea = driver.find_element("id", "test")
        textarea.click()
        
        # Test text with spaces
        test_text = "def longestCommonPrefix(strs):"
        
        print(f"\n📝 Typing: {repr(test_text)}")
        print("\nCharacter by character:")
        
        for i, char in enumerate(test_text):
            actions = ActionChains(driver)
            
            if char.isupper():
                print(f"  [{i}] {char} (UPPERCASE)")
                actions.key_down(Keys.SHIFT).send_keys(char.lower()).key_up(Keys.SHIFT).perform()
            elif char == ' ':
                print(f"  [{i}] SPACE (using Keys.SPACE)")
                actions.send_keys(Keys.SPACE).perform()
            else:
                print(f"  [{i}] {char}")
                actions.send_keys(char).perform()
            
            time.sleep(0.05)
        
        time.sleep(1)
        
        # Get the actual text
        actual_text = textarea.get_attribute('value')
        print(f"\n✅ Typed text: {repr(actual_text)}")
        print(f"📊 Expected:   {repr(test_text)}")
        
        if actual_text == test_text:
            print("\n🎉 SUCCESS! Spaces typed correctly!")
        else:
            print("\n❌ MISMATCH!")
            print(f"   Missing chars: {set(test_text) - set(actual_text)}")
        
        time.sleep(2)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_space_typing()

