# 📸 Unknown Functions History

## Purpose
When the bot encounters a function name it can't match (even with fuzzy matching), it automatically saves screenshots and info to help you add corrections.

## What Gets Saved

For each unknown function, the bot saves:

1. **Full screenshot** - `game_screen.png` copy
2. **Processed OCR area** - Enhanced image used for OCR
3. **Info file** - Text file with details and instructions

### File Naming
```
unknown_snippets_history/
  20231216_143052_001_deftwwosum.png
  20231216_143052_001_deftwwosum_processed.png
  20231216_143052_001_deftwwosum.txt
  └─ timestamp_counter_ocrname.ext
```

## Info File Contents

```
OCR Detected: deftwwosum
Timestamp: 20231216_143052
Selected Language: python

To add correction:
python add_ocr_correction.py 'deftwwosum' 'correct_name'

Available functions:
  - twosum
  - ispalindrome
  - ...
```

## Workflow

### 1. Bot Encounters Unknown Function
```
📸 Taking screenshot...
📝 OCR extracted text: deftwwoSum(nums, target)
✅ Detected function name: deftwwosum
❌ Function 'deftwwosum' not found in database
📸 Saved unknown function screenshot: unknown_snippets_history/...
💡 To add correction: python add_ocr_correction.py 'deftwwosum' 'correct_name'
```

### 2. Review Screenshot
Open the saved screenshot to see what the actual function name is:
```bash
open unknown_snippets_history/20231216_143052_001_deftwwosum.png
```

### 3. Add Correction
```bash
python add_ocr_correction.py "deftwwosum" "twosum"
```

### 4. Bot Now Recognizes It
Next time the bot sees `deftwwosum`, it will:
```
🔧 OCR correction: 'deftwwosum' → 'twosum'
✅ Found exact match for 'twosum' in database
```

## Example Corrections Added

Based on saved screenshots:

```json
{
  "deftwwosum": "twosum",
  "deftwosum": "twosum",
  "inordertraversait": "inordertraversal",
  "dfs": "inordertraversal"
}
```

## Benefits

- ✅ **Automatic tracking** - No manual screenshot needed
- ✅ **Complete context** - Full game screen + processed OCR
- ✅ **Easy correction** - Command provided in info file
- ✅ **Historical record** - See all OCR issues over time
- ✅ **Self-improving** - Bot gets better as you add corrections

## Analyzing Patterns

Review the history folder to find patterns:
```bash
ls -la unknown_snippets_history/
```

Common OCR errors:
- `l` (lowercase L) → `I` (uppercase i)
- `rn` → `m`
- Double letters: `ww` instead of `w`
- Missing spaces: `deftwoSum` instead of `def twoSum`

## Cleanup

To clear old unknown functions:
```bash
rm unknown_snippets_history/*
```

Or keep for reference to improve OCR preprocessing.

## Statistics

Track your correction rate:
```bash
# Count unknown functions
ls unknown_snippets_history/*.txt | wc -l

# Count corrections
python add_ocr_correction.py | wc -l
```

## Integration

The bot automatically:
1. Creates `unknown_snippets_history/` folder on startup
2. Increments counter for each unknown function
3. Saves all relevant files
4. Prints instructions for adding correction
5. Continues with fallback OCR

No manual intervention needed during bot execution!

