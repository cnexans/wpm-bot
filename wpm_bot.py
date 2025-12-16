#!/usr/bin/env python3
"""
WPM Bot - Automated typing bot for https://wpm.silver.dev
Uses OCR to read code snippets from the canvas-based game and types them automatically.
"""

import time
import sys
import re
import json
import os
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import pytesseract

# Try to import undetected-chromedriver for better anti-detection
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False
    print("⚠️  undetected-chromedriver not available, using standard Selenium")


class WPMBot:
    def __init__(self, typing_speed=1, use_undetected=True):
        """
        Initialize the WPM Bot.
        
        Args:
            typing_speed: Delay between each character (lower = faster)
            use_undetected: Use undetected-chromedriver if available
        """
        self.typing_speed = typing_speed
        self.driver = None
        self.use_undetected = use_undetected and UC_AVAILABLE
        self.code_blocks = self.load_code_blocks()
        self.selected_language = None  # Track the language selected in game menu
        self.unknown_count = 0  # Counter for unknown function screenshots
        
        # Create unknown_snippets_history directory
        import os
        os.makedirs('unknown_snippets_history', exist_ok=True)
        
    def load_code_blocks(self):
        """Load the code blocks database from JSON file."""
        try:
            with open('CodeBlocks.json', 'r') as f:
                blocks = json.load(f)
            print(f"✅ Loaded {len(blocks)} code blocks from database")
            
            # Create lookup dictionary by title (case-insensitive)
            # Store all language variants
            lookup = {}
            for block in blocks:
                title = block['title'].lower()
                language = block.get('language', 'unknown')
                # Join all block lines into single string
                code = ''.join(block['blocks'])
                
                # Store by title only (will prefer based on language detection)
                if title not in lookup:
                    lookup[title] = {}
                lookup[title][language] = code
                
            print(f"   Functions: {len(lookup)} unique, {len(blocks)} total (with language variants)")
            
            # Load OCR corrections map
            try:
                with open('ocr_corrections.json', 'r') as f:
                    corrections_data = json.load(f)
                    self.ocr_corrections = corrections_data.get('corrections', {})
                print(f"   Loaded {len(self.ocr_corrections)} OCR corrections")
            except FileNotFoundError:
                print("   ⚠️  ocr_corrections.json not found, using fuzzy matching only")
                self.ocr_corrections = {}
            
            return lookup
        except FileNotFoundError:
            print("⚠️  CodeBlocks.json not found. Download it first:")
            print("   curl -o CodeBlocks.json https://raw.githubusercontent.com/silver-dev-org/wpm/main/game/src/data/CodeBlocks.json")
            return {}
        except Exception as e:
            print(f"❌ Error loading code blocks: {e}")
            return {}
        
    def setup_driver(self):
        """Setup Chrome WebDriver with WebGL support."""
        if self.use_undetected:
            print("🛡️  Using undetected-chromedriver...")
            options = uc.ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            # Enable WebGL with ANGLE/SwiftShader
            options.add_argument("--use-gl=angle")
            options.add_argument("--use-angle=swiftshader")
            options.add_argument("--enable-webgl")
            
            self.driver = uc.Chrome(options=options, version_main=None)
        else:
            print("🔧 Using standard Selenium...")
            chrome_options = Options()
            
            # Anti-detection
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Window settings
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            
            # Enable WebGL with ANGLE/SwiftShader (software rendering)
            chrome_options.add_argument("--use-gl=angle")
            chrome_options.add_argument("--use-angle=swiftshader")
            chrome_options.add_argument("--enable-webgl")
            chrome_options.add_argument("--no-sandbox")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.driver.implicitly_wait(5)
        print("✅ WebDriver initialized")
        
    def navigate_to_game(self):
        """Navigate to the WPM game website."""
        print("🌐 Navigating to wpm.silver.dev...")
        self.driver.get("https://wpm.silver.dev")
        time.sleep(3)  # Wait for WebGL canvas to initialize
        print("✅ Page loaded")
        
    def type_text(self, text):
        """
        Type text character by character with proper delays.
        Skips leading indentation (game handles auto-indent).
        Preserves spaces within code lines.
        
        Uses 100ms (0.1s) delay between characters to give the game's
        canvas event handler enough time to process each keystroke.
        Faster delays cause keys to be queued/merged by the game.
        """
        from selenium.webdriver.common.action_chains import ActionChains
        
        lines = text.split('\n')
        
        for line_idx, line in enumerate(lines):
            # Skip leading whitespace (indentation) - game auto-indents
            # But preserve the actual code content
            stripped_line = line.lstrip()

            print(f"Typing line: -->{stripped_line}<--")
            
            if not stripped_line:
                # Empty line, just press Enter
                if line_idx < len(lines) - 1:
                    ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                    time.sleep(self.typing_speed)
                continue
            
            # Type each character individually with minimal delay
            # This prevents the game from receiving too many events at once
            for char in stripped_line:
                actions = ActionChains(self.driver)
                
                if char.isupper():
                    # For uppercase, hold shift and press the lowercase letter
                    actions.key_down(Keys.SHIFT).send_keys(char.lower()).key_up(Keys.SHIFT).perform()
                elif char == ' ':
                    # Use Keys.SPACE for spaces
                    actions.send_keys(Keys.SPACE).perform()
                else:
                    actions.send_keys(char).perform()
                
                # Delay to let game process the key event
                # Game's canvas event handler needs time to process each key
                time.sleep(self.typing_speed)  # Use configured typing speed
            
            # Press Enter to go to next line (except for last line)
            if line_idx < len(lines) - 1:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                time.sleep(self.typing_speed)
            
    def take_screenshot(self, filename="screenshot.png"):
        """Take a screenshot and return as PIL Image."""
        screenshot = self.driver.get_screenshot_as_png()
        img = Image.open(BytesIO(screenshot))
        img.save(filename)
        return img
        
    def extract_text_from_screenshot(self, img=None, region=None):
        """Extract text from screenshot using OCR."""
        if img is None:
            img = self.take_screenshot()
            
        # Crop to specific region if provided (x, y, width, height)
        if region:
            img = img.crop(region)
            
        # Use Tesseract to extract text
        # PSM 6 = Assume a single uniform block of text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, config=custom_config)
        return text.strip()
        
    def preprocess_image_for_ocr(self, img):
        """Preprocess image to improve OCR accuracy for code."""
        from PIL import ImageEnhance, ImageFilter
        import numpy as np
        
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
        # Adjust threshold based on your screen - code text appears to be lighter
        threshold = 100
        img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
        
        # Convert back to PIL Image
        img = Image.fromarray(img_array)
        
        # Scale up 2x for better OCR
        new_size = (img.width * 2, img.height * 2)
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
        
    def extract_function_name(self):
        """
        Extract just the function name from the screen using OCR.
        Much more reliable than extracting entire code.
        """
        img = self.take_screenshot("game_screen.png")
        
        # Get image dimensions
        width, height = img.size
        
        # Focus on the top area where function name appears
        # Function name is usually in the first few lines
        title_region = (
            int(width * 0.20),   # x: 20% from left (skip sidebar)
            int(height * 0.08),  # y: 8% from top
            int(width * 0.70),   # width: to 70% (function name area)
            int(height * 0.20)   # height: just top 20% (first few lines)
        )
        
        # Crop and save for debugging
        title_img = img.crop(title_region)
        title_img.save("function_name_area.png")
        
        # Preprocess for better OCR
        processed_img = self.preprocess_image_for_ocr(title_img)
        processed_img.save("function_name_processed.png")
        
        # Extract text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        
        print(f"📝 OCR extracted text:\n{text[:200]}")
        
        # Extract function name from text
        # Look for patterns like: "var functionName", "function functionName", "def functionName"
        import re
        
        # Try different patterns
        patterns = [
            r'var\s+(\w+)\s*=',           # var functionName =
            r'function\s+(\w+)\s*\(',     # function functionName(
            r'def\s+(\w+)\s*\(',          # def functionName(
            r'const\s+(\w+)\s*=',         # const functionName =
            r'let\s+(\w+)\s*=',           # let functionName =
            r'(\w+)\s*=\s*function',      # functionName = function
            r'export\s+function\s+(\w+)', # export function functionName
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                func_name = match.group(1)
                print(f"✅ Detected function name: {func_name}")
                return func_name.lower()
        
        # If no pattern matches, try to find any word that looks like a function name
        # Look for camelCase or snake_case words
        words = re.findall(r'\b[a-z][a-zA-Z0-9_]+\b', text)
        if words:
            # Filter out common keywords
            keywords = {'var', 'let', 'const', 'function', 'def', 'class', 'return', 'if', 'else', 'for', 'while'}
            candidates = [w for w in words if w.lower() not in keywords and len(w) > 3]
            if candidates:
                func_name = candidates[0]
                print(f"🔍 Best guess function name: {func_name}")
                return func_name.lower()
        
        print("⚠️  Could not detect function name from OCR")
        return None
        
    def detect_language_from_screen(self):
        """
        Detect the programming language from the screen.
        Look for language indicators in the code or UI.
        """
        # Take a screenshot and look for language hints
        try:
            img = self.take_screenshot("lang_detect.png")
            width, height = img.size
            
            # Check top area for language indicators
            top_region = (0, 0, width, int(height * 0.15))
            top_img = img.crop(top_region)
            
            # Simple OCR to detect language
            text = pytesseract.image_to_string(top_img).lower()
            
            # Look for language keywords in the code itself
            # JavaScript: var, let, const, function
            # Python: def, import
            # Go: func, package
            
            if 'javascript' in text:
                return 'javascript'
            elif 'python' in text:
                return 'python'
            elif 'golang' in text or 'go' in text:
                return 'golang'
            elif 'react' in text:
                return 'react'
                
            # Default to javascript (most common)
            return 'javascript'
        except:
            return 'javascript'
    
    def fuzzy_match_function_name(self, ocr_name):
        """
        Try to find the correct function name using fuzzy matching.
        Uses Levenshtein distance to find closest match.
        """
        if not ocr_name:
            return None
        
        ocr_lower = ocr_name.lower()
        
        # Check OCR corrections map first
        if hasattr(self, 'ocr_corrections') and ocr_lower in self.ocr_corrections:
            corrected = self.ocr_corrections[ocr_lower]
            print(f"🔧 OCR correction: '{ocr_name}' → '{corrected}'")
            return corrected
        
        # Clean OCR name (remove common prefixes that OCR adds)
        clean_ocr = ocr_lower
        for prefix in ['def', 'var', 'function', 'func', 'const', 'let']:
            if clean_ocr.startswith(prefix):
                clean_ocr = clean_ocr[len(prefix):]
                break
        
        # Calculate similarity with all function names
        best_match = None
        best_score = 0
        
        for func_name in self.code_blocks.keys():
            # Try both original and cleaned versions
            sim1 = self.calculate_similarity(ocr_lower, func_name)
            sim2 = self.calculate_similarity(clean_ocr, func_name)
            similarity = max(sim1, sim2)
            
            # Boost score if substring match
            if func_name in clean_ocr or clean_ocr in func_name:
                similarity = max(similarity, 0.85)
            
            if similarity > best_score and similarity > 0.6:  # 60% threshold
                best_score = similarity
                best_match = func_name
        
        if best_match:
            print(f"🔍 Fuzzy match: '{ocr_name}' → '{best_match}' (similarity: {best_score:.2%})")
            return best_match
        
        return None
    
    def levenshtein_distance(self, s1, s2):
        """Calculate Levenshtein (edit) distance between two strings."""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def calculate_similarity(self, s1, s2):
        """Calculate similarity between two strings (0.0 to 1.0)."""
        if not s1 or not s2:
            return 0.0
        
        distance = self.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        # Convert distance to similarity
        similarity = 1.0 - (distance / max_len)
        return similarity
    
    def get_code_from_database(self, function_name, language_hint=None):
        """
        Look up the exact code from the database by function name.
        
        Args:
            function_name: The name of the function (case-insensitive)
            language_hint: Optional language hint ('javascript', 'python', etc.)
            
        Returns:
            The exact code string, or None if not found
        """
        if not function_name:
            return None
            
        func_name_lower = function_name.lower()
        
        # Try exact match first
        if func_name_lower in self.code_blocks:
            variants = self.code_blocks[func_name_lower]
            
            # Priority 1: Use the language we selected in the game menu
            if self.selected_language and self.selected_language in variants:
                print(f"✅ Found '{function_name}' for selected language: {self.selected_language}")
                return variants[self.selected_language]
            
            # Priority 2: If language hint provided, try to use it
            if language_hint and language_hint in variants:
                print(f"✅ Found '{function_name}' for language: {language_hint}")
                return variants[language_hint]
            
            # Priority 3: Detect language from screen
            detected_lang = self.detect_language_from_screen()
            if detected_lang in variants:
                print(f"✅ Found '{function_name}' (detected language: {detected_lang})")
                return variants[detected_lang]
            
            # Priority 4: Fall back to first available variant
            first_lang = list(variants.keys())[0]
            print(f"✅ Found '{function_name}' (using {first_lang} variant)")
            return variants[first_lang]
        
        # Try fuzzy match with OCR corrections and similarity
        corrected_name = self.fuzzy_match_function_name(function_name)
        if corrected_name and corrected_name in self.code_blocks:
            variants = self.code_blocks[corrected_name]
            
            # Use selected language
            if self.selected_language and self.selected_language in variants:
                print(f"✅ Using corrected function with selected language: {self.selected_language}")
                return variants[self.selected_language]
            
            # Fall back to first available
            first_lang = list(variants.keys())[0]
            print(f"✅ Using corrected function ({first_lang})")
            return variants[first_lang]
        
        # Try substring match as last resort
        for key in self.code_blocks.keys():
            if func_name_lower in key or key in func_name_lower:
                variants = self.code_blocks[key]
                first_lang = list(variants.keys())[0]
                print(f"✅ Found substring match: '{function_name}' → '{key}' ({first_lang})")
                return variants[first_lang]
        
        # Not found - save screenshot for analysis
        print(f"❌ Function '{function_name}' not found in database")
        print(f"   Available functions: {', '.join(list(self.code_blocks.keys())[:10])}...")
        self.save_unknown_function_screenshot(function_name)
        return None
    
    def save_unknown_function_screenshot(self, function_name):
        """Save screenshot of unknown function to history folder."""
        try:
            import datetime
            import shutil
            
            self.unknown_count += 1
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save game screen
            src_file = "game_screen.png"
            if os.path.exists(src_file):
                dest_file = f"unknown_snippets_history/{timestamp}_{self.unknown_count:03d}_{function_name}.png"
                shutil.copy(src_file, dest_file)
                print(f"📸 Saved unknown function screenshot: {dest_file}")
            
            # Also save the processed function name area
            src_file = "function_name_processed.png"
            if os.path.exists(src_file):
                dest_file = f"unknown_snippets_history/{timestamp}_{self.unknown_count:03d}_{function_name}_processed.png"
                shutil.copy(src_file, dest_file)
            
            # Save a text file with OCR info
            info_file = f"unknown_snippets_history/{timestamp}_{self.unknown_count:03d}_{function_name}.txt"
            with open(info_file, 'w') as f:
                f.write(f"OCR Detected: {function_name}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Selected Language: {self.selected_language}\n")
                f.write(f"\nTo add correction:\n")
                f.write(f"python add_ocr_correction.py '{function_name}' 'correct_name'\n")
                f.write(f"\nAvailable functions:\n")
                for func in sorted(self.code_blocks.keys()):
                    f.write(f"  - {func}\n")
            
            print(f"💡 To add correction: python add_ocr_correction.py '{function_name}' 'correct_name'")
            
        except Exception as e:
            print(f"⚠️  Could not save unknown function screenshot: {e}")
        
    def extract_code_area(self):
        """
        Get the code to type using the smart approach:
        1. Use OCR to identify function name
        2. Look up exact code from database
        3. Return None if database lookup fails (don't use buggy OCR)
        """
        # Try smart approach first
        function_name = self.extract_function_name()
        
        if function_name:
            code = self.get_code_from_database(function_name)
            if code:
                print("🎯 Using exact code from database (100% accurate!)")
                return code
        
        # Don't fall back to full OCR - it's too error-prone
        print("⚠️  Cannot find function in database - skipping this challenge")
        print("💡 Add OCR correction and try again")
        return None
        
        # OLD: Fall back to full OCR (disabled - too many errors)
        # img = self.take_screenshot("game_screen.png")
        
        # Get image dimensions
        width, height = img.size
        
        # Define the code area region
        code_region = (
            int(width * 0.20),   # x: 20% from left (skip sidebar)
            int(height * 0.08),  # y: 8% from top
            int(width * 0.95),   # width: to 95% of screen
            int(height * 0.92)   # height: to 92% of screen
        )
        
        # Crop and save for debugging
        code_img = img.crop(code_region)
        code_img.save("code_area_raw.png")
        
        # Preprocess for better OCR
        processed_img = self.preprocess_image_for_ocr(code_img)
        processed_img.save("code_area_processed.png")
        
        # Extract text with optimized config for code
        custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        
        # Post-process common OCR errors in code
        text = self.fix_common_ocr_errors(text)
        
        return text.strip()
        
    def fix_common_ocr_errors(self, text):
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
        
    def wait_for_screen_change(self, timeout=3):
        """Wait a bit for the screen to update."""
        time.sleep(timeout)
        
    def start_game_sequence(self, language='python', mode='interview'):
        """
        Navigate through the game menus:
        1. Type 'start' on initial screen
        2. Choose audio option (type 'no')
        3. Choose language (default: 'python', can be 'javascript', 'golang', etc.)
        4. Choose mode (default: 'interview', can be 'practice')
        """
        print("\n" + "="*60)
        print("🎮 STARTING GAME SEQUENCE")
        print("="*60)
        
        # Step 1: Start screen - type 'start'
        print("\n📝 Step 1: Typing 'start'...")
        time.sleep(2)
        self.take_screenshot("01_initial.png")
        self.type_text("start")
        self.type_text("\n")
        self.wait_for_screen_change(2)
        
        # Step 2: Audio option - type 'no'
        print("📝 Step 2: Audio option - typing 'no'...")
        self.take_screenshot("02_audio.png")
        self.type_text("no")
        self.type_text("\n")
        self.wait_for_screen_change(2)
        
        # Step 3: Language selection
        print(f"📝 Step 3: Language - typing '{language}'...")
        self.take_screenshot("03_language.png")
        self.selected_language = language  # Remember the language we selected
        self.type_text(language)
        self.type_text("\n")
        self.wait_for_screen_change(2)
        
        # Step 4: Mode selection
        print(f"📝 Step 4: Mode - typing '{mode}'...")
        self.take_screenshot("04_mode.png")
        self.type_text(mode)
        self.type_text("\n")
        self.wait_for_screen_change(3)
        
        print("✅ Game sequence complete! Game should be starting...")
        self.take_screenshot("05_game_start.png")
        
    def play_typing_challenge(self):
        """
        Main typing loop:
        1. Extract code from screen using OCR
        2. Type the code
        3. Repeat until game ends
        """
        print("\n" + "="*60)
        print("⌨️  STARTING TYPING CHALLENGE")
        print("="*60)
        
        challenge_count = 0
        max_challenges = 10  # Safety limit
        
        prev_function_name = None
        
        while challenge_count < max_challenges:
            challenge_count += 1
            print(f"\n🔄 Challenge {challenge_count}")
            
            # Wait for code to appear
            time.sleep(2)
            
            # Take screenshot and extract function name first
            print("📸 Taking screenshot...")
            current_function = self.extract_function_name()
            
            # Check if it's the same as previous (avoid re-typing)
            if current_function and current_function == prev_function_name:
                print(f"⚠️  Same function as previous ({current_function}), waiting longer...")
                time.sleep(3)
                current_function = self.extract_function_name()
                
                if current_function == prev_function_name:
                    print("⚠️  Still same function, game may have ended")
                    break
            
            # Now get the full code
            code_text = self.get_code_from_database(current_function) if current_function else None
            
            if not code_text or len(code_text) < 10:
                print("⚠️  No code detected or game may have ended")
                # Check if we see results screen
                img = self.take_screenshot(f"challenge_{challenge_count}_check.png")
                full_text = self.extract_text_from_screenshot(img)
                if "WPM" in full_text.upper() or "ACCURACY" in full_text.upper():
                    print("🏁 Game ended - results screen detected!")
                    break
                
                # Skip this challenge - press ESC to go to next
                print("⏭️  Skipping challenge (pressing ESC)...")
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(2)
                continue
            
            print("\n" + "-"*60)
            print("📋 CODE TO TYPE:")
            print("-"*60)
            print(code_text)
            print("-"*60)
            
            # Type the code
            print(f"⌨️  Typing {len(code_text)} characters...")
            self.type_text(code_text)

            # OLD: Type character by character
            # char_count = 0
            # for char in code_text:
            #     self.type_text(char)
            #     char_count += 1
            #     if char_count % 50 == 0:
            #         print(f"   Progress: {char_count}/{len(code_text)}")
            # print(f"✅ Typed {char_count} characters")
            
            # Remember this function to avoid re-typing
            prev_function_name = current_function
            
            # Wait for game to process and move to next challenge
            print("⏳ Waiting for next challenge...")
            time.sleep(2)  # Give game more time to transition
            
        print("\n🏁 Typing loop finished")
        
    def show_results(self):
        """Capture and display final results."""
        print("\n" + "="*60)
        print("📊 CAPTURING RESULTS")
        print("="*60)
        
        time.sleep(3)
        img = self.take_screenshot("final_results.png")
        results_text = self.extract_text_from_screenshot(img)
        
        print("\n" + "-"*60)
        print("RESULTS:")
        print("-"*60)
        print(results_text)
        print("-"*60)
        
    def run(self, language='python', mode='interview'):
        """Run the full bot sequence."""
        try:
            print("\n" + "🤖 "*20)
            print("WPM BOT STARTING")
            print("🤖 "*20 + "\n")
            
            self.setup_driver()
            self.navigate_to_game()
            
            # Navigate through menus
            self.start_game_sequence(language=language, mode=mode)
            
            # Play the typing game
            self.play_typing_challenge()
            
            # Show results
            self.show_results()
            
            print("\n✅ Bot completed successfully!")
            print("📸 Screenshots saved for review")
            print("\nPress Ctrl+C to close browser...")
            
            # Keep browser open to see results
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
                
        except KeyboardInterrupt:
            print("\n⚠️  Bot interrupted by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            # Take error screenshot
            try:
                self.take_screenshot("error_screenshot.png")
                print("📸 Error screenshot saved")
            except:
                pass
        finally:
            if self.driver:
                print("\n🔒 Closing browser...")
                self.driver.quit()


def main():
    # Typing speed: delay between characters above 0.005, and 0.01 is recommended
    typing_speed = 0.01  # 10ms default for reliable canvas event handling
    language = 'python'  # Default language
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        try:
            typing_speed = float(sys.argv[1])
        except ValueError:
            print(f"Invalid typing speed: {sys.argv[1]}, using default {typing_speed}")
    
    if len(sys.argv) > 2:
        language = sys.argv[2].lower()
        print(f"🌐 Language: {language}")
    
    print(f"⚡ Typing speed: {typing_speed}s per character")
    print(f"💡 Tip: python wpm_bot.py <speed> <language>")
    print(f"   Example: python wpm_bot.py 0.02 javascript")
    
    bot = WPMBot(typing_speed=typing_speed)
    bot.run(language=language)


if __name__ == "__main__":
    main()
