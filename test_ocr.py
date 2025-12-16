#!/usr/bin/env python3
"""
Test OCR on a screenshot to debug text extraction.
Usage: python test_ocr.py <screenshot_path>
"""

import sys
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np


def preprocess_image_for_ocr(img):
    """Preprocess image to improve OCR accuracy for code."""
    # Convert to grayscale
    img = img.convert('L')
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.5)
    
    # Increase brightness slightly
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.3)
    
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    
    # Convert to numpy array for thresholding
    img_array = np.array(img)
    
    # Apply threshold to make text pure white on black background
    threshold = 100
    img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
    
    # Convert back to PIL Image
    img = Image.fromarray(img_array)
    
    # Scale up 2x for better OCR
    new_size = (img.width * 2, img.height * 2)
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    return img


def fix_common_ocr_errors(text):
    """Fix common OCR mistakes in code."""
    import re
    
    # Fix dot-comma patterns (.,) which should be just dot (.)
    text = text.replace('.,', '.')
    
    # Fix commas that should be dots (common in code)
    # Pattern: word,word or word,number should be word.word
    text = re.sub(r'(\w),(\w)', r'\1.\2', text)
    
    # Fix semicolons at end of lines (Python doesn't use them)
    text = re.sub(r';:', ':', text)
    text = re.sub(r';$', '', text, flags=re.MULTILINE)
    text = re.sub(r';\s*$', '', text, flags=re.MULTILINE)
    
    # Common word replacements
    replacements = {
        'aif ': 'if ',
        ' aif ': ' if ',
        '\naif ': '\nif ',
        'le sie:': 'else:',
        'lelse:': 'else:',
        'eise:': 'else:',
        'retum ': 'return ',
        'retum\n': 'return\n',
        'whiie ': 'while ',
        'whlle ': 'while ',
        'def ': 'def ',
        'deff ': 'def ',
        's_f ': 'def ',
        'ciass ': 'class ',
        'seif': 'self',
        'seff': 'self',
        'Nione': 'None',
        'Faise': 'False',
        'Falee': 'False',
        'True': 'True',
        'Tme': 'True',
        'cun.mext': 'cur.next',
        'cun.': 'cur.',
        'mext': 'next',
        'Chead': 'head',
        'deleteDuplicates(head);': 'deleteDuplicates(head):',
    }
    
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    
    # Remove random single letters at start of lines (OCR artifacts)
    text = re.sub(r'^\s*[a-z]\s+', '', text, flags=re.MULTILINE)
    
    # Add missing colons after control structures
    # if/while/for/elif statements should end with :
    text = re.sub(r'^(\s*)(if|while|for|elif|else if)\s+(.+?)$', r'\1\2 \3:', text, flags=re.MULTILINE)
    # Don't double-add colons
    text = text.replace('::', ':')
    
    return text


def test_ocr(image_path):
    """Test OCR on an image."""
    print(f"📸 Loading image: {image_path}")
    img = Image.open(image_path)
    
    print(f"📐 Image size: {img.size}")
    
    # Test with different regions if it's a full screenshot
    width, height = img.size
    
    # Try the code area region
    if width > 1000:  # Likely a full screenshot
        print("\n🔍 Extracting code area...")
        code_region = (
            int(width * 0.20),   # Skip left sidebar
            int(height * 0.08),
            int(width * 0.95),
            int(height * 0.92)
        )
        img = img.crop(code_region)
        img.save("test_code_area.png")
        print(f"✅ Cropped to: {img.size}")
    
    # Save original
    img.save("test_original.png")
    
    # Preprocess
    print("\n🔧 Preprocessing image...")
    processed = preprocess_image_for_ocr(img)
    processed.save("test_processed.png")
    print("✅ Saved processed image")
    
    # Extract text
    print("\n📝 Extracting text with Tesseract...")
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    text = pytesseract.image_to_string(processed, config=custom_config)
    
    print("\n" + "="*60)
    print("RAW OCR OUTPUT:")
    print("="*60)
    print(text)
    print("="*60)
    
    # Fix common errors
    fixed_text = fix_common_ocr_errors(text)
    
    print("\n" + "="*60)
    print("FIXED OCR OUTPUT:")
    print("="*60)
    print(fixed_text)
    print("="*60)
    
    # Save to file
    with open("ocr_output.txt", "w") as f:
        f.write(fixed_text)
    print("\n✅ Saved to ocr_output.txt")
    
    print("\n📁 Files created:")
    print("  - test_original.png (cropped original)")
    print("  - test_processed.png (preprocessed for OCR)")
    print("  - ocr_output.txt (extracted text)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <screenshot_path>")
        print("\nExample:")
        print("  python test_ocr.py game_screen.png")
        print("  python test_ocr.py code_area.png")
        sys.exit(1)
    
    test_ocr(sys.argv[1])

