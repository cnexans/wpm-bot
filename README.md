# WPM Bot 🤖⌨️

An automated bot that plays the typing game at [wpm.silver.dev](https://wpm.silver.dev) using OCR to read code snippets from the canvas.

## Features

- ✅ Navigates through game menus automatically
- ✅ Uses Tesseract OCR to read function names from WebGL canvas
- ✅ **Smart database lookup** - 100% accurate code from official database
- ✅ **OCR error correction** - Maps common OCR mistakes to correct names (28+ corrections)
- ✅ **Fuzzy matching** - Finds closest match when OCR is unclear
- ✅ **Skip unknown functions** - Doesn't type buggy OCR code, saves screenshot instead
- ✅ **Unknown function history** - Auto-saves screenshots for later correction
- ✅ Types code at superhuman speeds with perfect casing
- ✅ **Skips indentation** - Game auto-indents, bot only types code
- ✅ **Language-aware** - Remembers selected language (Python/JavaScript/Go)
- ✅ Saves screenshots at each step for debugging
- ✅ Anti-detection measures with undetected-chromedriver

## Requirements

- Python 3.7+
- Chrome browser
- Tesseract OCR (already installed via Homebrew)
- Internet connection

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run with defaults (Python language, fast speed)
python wpm_bot.py

# Run with custom typing speed (seconds per character)
python wpm_bot.py 0.05   # Slower, more human-like
python wpm_bot.py 0.01   # Super fast

# Run with specific language
python wpm_bot.py 0.02 javascript   # JavaScript challenges
python wpm_bot.py 0.02 python       # Python challenges (default)
python wpm_bot.py 0.02 golang       # Go challenges
```

## How It Works

### Game Flow
1. **Start Screen** → Types "start"
2. **Audio Option** → Types "no"
3. **Language Selection** → Types "python"
4. **Mode Selection** → Types "interview"
5. **Typing Game** → Loops:
   - Takes screenshot of game canvas
   - **Uses OCR to identify function name only** (e.g., "deleteDuplicates")
   - **Looks up exact code from database** (100% accurate!)
   - Types the perfect code character by character
   - Waits for next challenge
6. **Results** → Captures final score

### Smart Code Extraction (NEW!)
The bot uses a **hybrid approach** for maximum accuracy:

1. **OCR for function name only** - Much more reliable than full code OCR
2. **Database lookup** - Gets exact code from [CodeBlocks.json](https://github.com/silver-dev-org/wpm/blob/main/game/src/data/CodeBlocks.json)
3. **100% accuracy** - No OCR errors in the typed code!
4. **Fallback to full OCR** - If function not found in database

This means the bot types **perfect code every time** with zero typos!

### WebGL Support
The bot enables WebGL using:
- `--use-gl=angle` - Use ANGLE for GL rendering
- `--use-angle=swiftshader` - Software rendering (no GPU required)
- `--enable-webgl` - Enable WebGL API

## Screenshots

The bot saves screenshots at each step:
- `01_initial.png` - Initial screen
- `02_audio.png` - Audio selection
- `03_language.png` - Language selection
- `04_mode.png` - Mode selection
- `05_game_start.png` - Game starting
- `game_screen.png` - Current game screen
- `code_area.png` - Cropped code area for OCR
- `final_results.png` - Final results
- `error_screenshot.png` - If an error occurs

## Typing Speed

The `typing_speed` parameter controls delay between keystrokes:
- `0.01` = ~100 characters/second (superhuman)
- `0.02` = ~50 characters/second (very fast)
- `0.05` = ~20 characters/second (fast human)
- `0.1` = ~10 characters/second (average human)

## Troubleshooting

### WebGL Not Supported Error
- The bot uses SwiftShader for software WebGL rendering
- No GPU required
- Should work on any system

### OCR Not Reading Code Correctly
- Check `code_area.png` to see what region is being captured
- Adjust the `code_region` coordinates in `extract_code_area()`
- Tesseract works best with clear, high-contrast text

### Bot Types Wrong Characters
- OCR may misread similar characters (0/O, 1/l, etc.)
- Consider preprocessing images (increase contrast, denoise)
- May need to fine-tune Tesseract config

## Notes

- Browser window must stay visible (not minimized)
- First run downloads ChromeDriver automatically
- Press Ctrl+C to stop the bot anytime
- The bot uses `undetected-chromedriver` to avoid detection
- All screenshots are saved in the project directory

## Dependencies

- `selenium` - Browser automation
- `undetected-chromedriver` - Anti-detection
- `pytesseract` - OCR engine wrapper
- `Pillow` - Image processing
- `webdriver-manager` - Automatic ChromeDriver management

## License

Educational purposes only. Use responsibly.
