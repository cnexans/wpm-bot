#!/usr/bin/env python3
"""
Test function name extraction and database lookup.
"""

import json
import re
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np


def load_code_blocks():
    """Load the code blocks database."""
    with open('CodeBlocks.json', 'r') as f:
        blocks = json.load(f)
    
    lookup = {}
    for block in blocks:
        title = block['title'].lower()
        language = block.get('language', 'unknown')
        code = ''.join(block['blocks'])
        
        if title not in lookup:
            lookup[title] = {}
        lookup[title][language] = code
    
    print(f"✅ Loaded {len(blocks)} code blocks ({len(lookup)} unique functions)")
    return lookup


def preprocess_image(img):
    """Preprocess image for OCR."""
    img = img.convert('L')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.3)
    img = img.filter(ImageFilter.SHARPEN)
    
    img_array = np.array(img)
    threshold = 100
    img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
    img = Image.fromarray(img_array)
    
    new_size = (img.width * 2, img.height * 2)
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    return img


def extract_function_name(screenshot_path):
    """Extract function name from screenshot."""
    img = Image.open(screenshot_path)
    width, height = img.size
    
    # Focus on top area where function name is
    title_region = (
        int(width * 0.20),
        int(height * 0.08),
        int(width * 0.70),
        int(height * 0.20)
    )
    
    title_img = img.crop(title_region)
    title_img.save("test_function_name_area.png")
    
    processed = preprocess_image(title_img)
    processed.save("test_function_name_processed.png")
    
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(processed, config=custom_config)
    
    print("\n" + "="*60)
    print("OCR TEXT FROM FUNCTION AREA:")
    print("="*60)
    print(text)
    print("="*60)
    
    # Extract function name
    patterns = [
        r'var\s+(\w+)\s*=',
        r'function\s+(\w+)\s*\(',
        r'def\s+(\w+)\s*\(',
        r'const\s+(\w+)\s*=',
        r'let\s+(\w+)\s*=',
        r'(\w+)\s*=\s*function',
        r'export\s+function\s+(\w+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            func_name = match.group(1)
            print(f"\n✅ Detected function name: {func_name}")
            return func_name.lower()
    
    # Try to find camelCase words
    words = re.findall(r'\b[a-z][a-zA-Z0-9_]+\b', text)
    if words:
        keywords = {'var', 'let', 'const', 'function', 'def', 'class', 'return', 'if', 'else', 'for', 'while'}
        candidates = [w for w in words if w.lower() not in keywords and len(w) > 3]
        if candidates:
            func_name = candidates[0]
            print(f"\n🔍 Best guess: {func_name}")
            return func_name.lower()
    
    print("\n❌ Could not detect function name")
    return None


def main():
    print("🧪 Testing Function Name Extraction & Database Lookup\n")
    
    # Load database
    code_blocks = load_code_blocks()
    
    # Extract function name
    func_name = extract_function_name("game_screen.png")
    
    if func_name:
        # Look up in database
        print(f"\n🔍 Looking up '{func_name}' in database...")
        
        if func_name in code_blocks:
            variants = code_blocks[func_name]
            print(f"✅ EXACT MATCH FOUND!")
            print(f"   Available languages: {', '.join(variants.keys())}\n")
            
            # Show all variants
            for lang, code in variants.items():
                print("="*60)
                print(f"CODE FROM DATABASE ({lang.upper()}):")
                print("="*60)
                print(code)
                print("="*60)
                print()
        else:
            # Try fuzzy match
            print(f"⚠️  No exact match, trying fuzzy search...")
            for key in code_blocks.keys():
                if func_name in key or key in func_name:
                    variants = code_blocks[key]
                    print(f"✅ FUZZY MATCH: '{func_name}' → '{key}'")
                    print(f"   Available languages: {', '.join(variants.keys())}\n")
                    
                    for lang, code in variants.items():
                        print("="*60)
                        print(f"CODE FROM DATABASE ({lang.upper()}):")
                        print("="*60)
                        print(code)
                        print("="*60)
                        print()
                    break
            else:
                print(f"❌ Not found in database")
                print(f"\nAvailable functions:")
                for i, key in enumerate(list(code_blocks.keys())[:20]):
                    variants = code_blocks[key]
                    print(f"  - {key} ({', '.join(variants.keys())})")
    
    print("\n📁 Files created:")
    print("  - test_function_name_area.png")
    print("  - test_function_name_processed.png")


if __name__ == "__main__":
    main()

