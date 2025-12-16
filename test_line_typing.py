#!/usr/bin/env python3
"""
Test script to verify line-by-line typing works correctly.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

def test_line_typing():
    """Test typing complete lines at once."""
    print("🧪 Testing line-by-line typing...")
    
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
        
        # Test Python code with spaces
        test_code = """def lengthOfLastWord(s):
    length = 0
    for i in range(len(s) - 1, -1, -1):
        if s[i] != ' ':
            length += 1
        elif length > 0:
            break
    return length"""
        
        print(f"\n📝 Typing code:")
        print(test_code)
        print("\n" + "="*60)
        
        lines = test_code.split('\n')
        
        for line_idx, line in enumerate(lines):
            stripped_line = line.lstrip()
            print(f"\nLine {line_idx + 1}: {repr(stripped_line)}")
            
            # Build action chain for the entire line
            actions = ActionChains(driver)
            
            for char in stripped_line:
                if char.isupper():
                    actions.key_down(Keys.SHIFT).send_keys(char.lower()).key_up(Keys.SHIFT)
                elif char == ' ':
                    actions.send_keys(Keys.SPACE)
                else:
                    actions.send_keys(char)
            
            # Execute all at once
            actions.perform()
            print(f"  ✅ Typed {len(stripped_line)} characters")
            
            # Press Enter (except last line)
            if line_idx < len(lines) - 1:
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                print("  ⏎ Enter")
            
            time.sleep(0.1)
        
        time.sleep(1)
        
        # Get the actual text
        actual_text = textarea.get_attribute('value')
        
        # Compare (ignoring leading whitespace on each line)
        expected_lines = [line.lstrip() for line in test_code.split('\n')]
        actual_lines = [line.lstrip() for line in actual_text.split('\n')]
        
        print("\n" + "="*60)
        print("📊 COMPARISON:")
        print("="*60)
        
        all_match = True
        for i, (exp, act) in enumerate(zip(expected_lines, actual_lines)):
            match = "✅" if exp == act else "❌"
            print(f"{match} Line {i+1}:")
            if exp != act:
                print(f"  Expected: {repr(exp)}")
                print(f"  Actual:   {repr(act)}")
                all_match = False
        
        if all_match:
            print("\n🎉 SUCCESS! All lines typed correctly!")
        else:
            print("\n❌ MISMATCH detected!")
        
        time.sleep(3)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_line_typing()


