# ⏭️ Skip Unknown Functions

## Problem
When the bot can't find a function in the database, falling back to full OCR produces **buggy code** with errors:

### Example: plusOne
```python
# Database (correct):
def plusOne(digits):
    n = len(digits)
    for i in range(n - 1, -1, -1):
        if digits[i] < 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    return [1] + digits

# Full OCR (WRONG):
defpllusOne(digits):      # ❌ defpllusOne
= lLen(digits)            # ❌ lLen
for i in range(€n - 1, -1, -1):  # ❌ €n
if digits[i] < 3:         # ❌ < 3 (should be < 9)
digits[i] += 1
return digits
digits[i] = 0
return [4] + digits       # ❌ [4] (should be [1])
```

**Result:** Game rejects the code, bot gets stuck!

## Solution
**Skip unknown challenges instead of typing buggy code**

### New Behavior
```
OCR: "defpllusone"
   ↓
Check database
   ↓
Not found ❌
   ↓
Save screenshot 📸
   ↓
Skip challenge ⏭️ (press ESC)
   ↓
Continue to next challenge ✅
```

### Old Behavior (Disabled)
```
OCR: "defpllusone"
   ↓
Check database
   ↓
Not found ❌
   ↓
Fall back to full OCR
   ↓
Type buggy code ❌
   ↓
Game rejects, bot stuck ❌
```

## Implementation

```python
def extract_code_area(self):
    function_name = self.extract_function_name()
    
    if function_name:
        code = self.get_code_from_database(function_name)
        if code:
            return code  # ✅ Found in database
    
    # Don't use buggy OCR
    print("⚠️  Cannot find function - skipping")
    return None  # ⏭️ Skip this challenge
```

## What Happens When Skipped

1. **Screenshot saved** to `unknown_snippets_history/`
2. **Info file created** with correction command
3. **ESC pressed** to skip challenge
4. **Bot continues** to next challenge
5. **No buggy code typed** ✅

## Adding Corrections

After the bot runs, check the saved screenshots:

```bash
# View saved screenshots
ls -la unknown_snippets_history/

# Example files:
# 20251215_211932_001_defpllusone.png
# 20251215_211932_001_defpllusone_processed.png
# 20251215_211932_001_defpllusone.txt
```

Add correction:
```bash
python add_ocr_correction.py "defpllusone" "plusone"
```

Next run, the bot will recognize it!

## Benefits

### Before (Full OCR Fallback)
- ❌ Types incorrect code
- ❌ Game rejects input
- ❌ Bot gets stuck
- ❌ Wastes time
- ❌ Ruins score

### After (Skip Unknown)
- ✅ Skips unknown functions
- ✅ Saves screenshot for analysis
- ✅ Continues to next challenge
- ✅ Only types perfect code
- ✅ Maintains high accuracy

## Statistics

With skip behavior:
- **Known functions**: 100% accuracy ✅
- **Unknown functions**: Skipped (0% attempted) ⏭️
- **Overall**: Only types perfect code ✅

## Workflow

1. **Run bot** - It skips unknown functions
2. **Check history** - Review saved screenshots
3. **Add corrections** - Map OCR errors to correct names
4. **Run again** - Bot now recognizes more functions
5. **Repeat** - Bot gets smarter over time

## Example Session

```
Challenge 1: plusOne
✅ Found in database → Types perfect code

Challenge 2: defpllusone (OCR error)
❌ Not in database
📸 Saved screenshot
⏭️  Skipping (ESC)

Challenge 3: twoSum
✅ Found in database → Types perfect code

Challenge 4: deftwwosum (OCR error)
❌ Not in database
📸 Saved screenshot
⏭️  Skipping (ESC)

...continues...
```

## After Adding Corrections

```bash
python add_ocr_correction.py "defpllusone" "plusone"
python add_ocr_correction.py "deftwwosum" "twosum"
```

Next run:
```
Challenge 1: plusOne
✅ Found in database → Types perfect code

Challenge 2: defpllusone
🔧 OCR correction → plusone
✅ Found in database → Types perfect code

Challenge 3: twoSum
✅ Found in database → Types perfect code

Challenge 4: deftwwosum
🔧 OCR correction → twosum
✅ Found in database → Types perfect code

...100% success rate!
```

## Configuration

To re-enable full OCR fallback (not recommended):
```python
# In extract_code_area(), uncomment the OCR code
# But expect errors!
```

## Recommendation

**Keep skip behavior enabled** and build up your OCR corrections database over time. This ensures:
- 100% accuracy on known functions
- No buggy code typed
- Self-improving system

