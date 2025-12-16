# WPM Bot Usage Guide

## Quick Start

```bash
cd "/Users/carlos/wpm cheat"
source venv/bin/activate
python wpm_bot.py
```

## Testing OCR Before Running

To test OCR accuracy on a screenshot without running the full bot:

```bash
python test_ocr.py game_screen.png
```

This will:
- Crop to the code area
- Preprocess the image
- Run OCR
- Apply error corrections
- Save processed images and output

**Check these files:**
- `test_processed.png` - See what the OCR engine sees
- `ocr_output.txt` - The extracted code text

## Adjusting OCR Region

If the bot is capturing the wrong area, edit `wpm_bot.py` line ~165:

```python
code_region = (
    int(width * 0.20),   # x: adjust left edge
    int(height * 0.08),  # y: adjust top edge
    int(width * 0.95),   # width: adjust right edge
    int(height * 0.92)   # height: adjust bottom edge
)
```

## OCR Improvements Made

### Image Preprocessing
1. **Grayscale conversion** - Removes color noise
2. **Contrast enhancement** (2.5x) - Makes text stand out
3. **Brightness boost** (1.3x) - Lightens dark text
4. **Sharpening** - Clarifies edges
5. **Thresholding** - Pure white text on black background
6. **2x upscaling** - Larger text = better OCR

### Error Corrections
The bot automatically fixes common OCR mistakes:

| OCR Error | Correction |
|-----------|------------|
| `.,` | `.` |
| `aif` | `if` |
| `le sie:` | `else:` |
| `retum` | `return` |
| `whiie` | `while` |
| `seif` | `self` |
| `cun.mext` | `cur.next` |
| `s_f` | `def` |
| `;:` | `:` |
| Missing `:` after `if/while/for` | Adds automatically |

### Regex Fixes
- Converts commas to dots in code: `word,word` → `word.word`
- Removes semicolons from Python code
- Removes single-letter OCR artifacts at line starts

## Typing Speed

Adjust speed by passing a number (seconds per character):

```bash
python wpm_bot.py 0.01   # Very fast (100 chars/sec)
python wpm_bot.py 0.02   # Fast (50 chars/sec) - default
python wpm_bot.py 0.05   # Human-like (20 chars/sec)
```

## Game Flow

The bot automatically:
1. Types "start" → starts game
2. Types "no" → disables audio
3. Types "python" → selects Python language
4. Types "interview" → selects interview mode
5. **Loops:**
   - Screenshots the canvas
   - OCR extracts code
   - Types the code
   - Waits for next challenge
6. Captures final results

## Screenshots Saved

- `01_initial.png` - Start screen
- `02_audio.png` - Audio selection
- `03_language.png` - Language selection
- `04_mode.png` - Mode selection
- `05_game_start.png` - Game starting
- `game_screen.png` - Current game view
- `code_area_raw.png` - Cropped code area
- `code_area_processed.png` - After preprocessing
- `final_results.png` - Results screen

## Troubleshooting

### OCR reads wrong text
1. Run `python test_ocr.py game_screen.png`
2. Check `test_processed.png` - is the text clear?
3. Check `ocr_output.txt` - what did it extract?
4. Adjust crop region if needed
5. Add more error corrections to `fix_common_ocr_errors()`

### WebGL not working
- The bot uses SwiftShader (software rendering)
- No GPU required
- Should work on any Mac

### Bot types too fast/slow
- Adjust with command line argument
- Lower number = faster typing

### Game doesn't start
- Check screenshots to see where it stopped
- Verify the menu navigation sequence

## Advanced: Adding More Error Corrections

Edit `wpm_bot.py` in the `fix_common_ocr_errors()` method:

```python
replacements = {
    'wrong_text': 'correct_text',
    # Add your corrections here
}
```

Or add regex patterns:

```python
text = re.sub(r'pattern', r'replacement', text)
```

## Performance

With current settings (v2.0):
- **Code accuracy**: **100%** (database lookup)
- **Function name OCR**: ~95% (good enough for matching)
- **Typing speed**: 50-100 chars/second
- **Game completion**: ~2-3 minutes per session

## Testing Function Lookup

Test the smart lookup system:

```bash
python test_function_lookup.py
```

This will:
1. Load the CodeBlocks.json database (68 functions)
2. Extract function name from screenshot using OCR
3. Look up exact code in database
4. Display the perfect code

Example output:
```
✅ Detected function name: deleteduplicates
✅ EXACT MATCH FOUND!
[Perfect code from database displayed]
```

