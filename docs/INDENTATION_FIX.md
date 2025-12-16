# 🐛 Indentation Handling Fix

## Problem
Bot was typing **leading indentation spaces**, but the game **auto-indents** Python code!

```python
# Database has:
def searchInsert(nums, target):
    left, right = 0, len(nums) - 1
    ^^^^
    4 leading spaces

# Bot was typing:
def searchInsert(nums, target):
    left, right = 0, len(nums) - 1
    ^^^^
    Typing these 4 spaces ❌

# Game expected:
def searchInsert(nums, target):
left, right = 0, len(nums) - 1
(no leading spaces - game adds them automatically)
```

## Solution
**Skip leading whitespace, preserve inline spaces**

### What to Skip
```python
"    left = mid + 1"
^^^^
Skip these (indentation)
```

### What to Keep
```python
"left = mid + 1"
     ^     ^
Keep these (inline spaces)
```

## Implementation

```python
def type_text(self, text):
    lines = text.split('\n')
    
    for line in lines:
        # Remove leading spaces (indentation)
        stripped_line = line.lstrip()
        
        # Type the actual code
        for char in stripped_line:
            # ... type char ...
        
        # Press Enter for next line
```

## Examples

### Example 1: Simple Indentation
```python
# Original (from database):
def foo():
    return 42
    ^^^^
    4 spaces

# Bot types:
def foo():
return 42
(no leading spaces)

# Game displays:
def foo():
    return 42
    ^^^^
    Game adds indentation
```

### Example 2: Nested Indentation
```python
# Original:
def search():
    while x:
        if y:
            return z
    ^^^^    ^^^^^^^^    ^^^^^^^^^^^^
    4       8           12 spaces

# Bot types:
def search():
while x:
if y:
return z
(all leading spaces removed)

# Game displays:
def search():
    while x:
        if y:
            return z
(game adds proper indentation)
```

### Example 3: Inline Spaces Preserved
```python
# Original:
    mid = (left + right) // 2
    ^^^^  ^    ^ ^     ^ ^^ ^
    Skip  Keep all these spaces

# Bot types:
mid = (left + right) // 2
      ^    ^ ^     ^ ^^ ^
      All inline spaces preserved ✅
```

## Test Results

```
Line: "    left, right = 0, len(nums) - 1"
      ^^^^                ^          ^ ^
      Skip                Keep these spaces

Leading spaces: 4 (skipped)
Will type: "left, right = 0, len(nums) - 1"
           ✅ Inline spaces preserved
```

## Key Points

| Type | Action | Example |
|------|--------|---------|
| Leading spaces | ❌ Skip | `    return` → `return` |
| Inline spaces | ✅ Keep | `n - 1` → `n - 1` |
| Tabs | ❌ Skip | `\treturn` → `return` |
| Newlines | ✅ Type | Press ENTER |

## Why This Works

The game (like most code editors):
1. **Auto-indents** based on context (after `:`, inside blocks)
2. Expects you to type **only the code**, not the indentation
3. Adds indentation automatically when you press ENTER

## Impact
- ✅ Bot types correct code without extra spaces
- ✅ Game accepts the input
- ✅ Proper indentation shown in game
- ✅ Inline spaces preserved for operators

## Before vs After

### Before
```
Bot types: "    left = mid + 1"
           ^^^^
           Extra spaces cause errors
Game: REJECTED ❌
```

### After
```
Bot types: "left = mid + 1"
           No leading spaces
Game: ACCEPTED ✅
Game displays: "    left = mid + 1"
               ^^^^
               Game adds indentation
```

## Files Changed
- `wpm_bot.py` - Updated `type_text()` method
- `test_indentation.py` - Test indentation handling

