#!/usr/bin/env python3
"""
Test indentation handling - skip leading spaces, preserve inline spaces.
"""

def process_code(text):
    """Simulate the bot's typing logic."""
    lines = text.split('\n')
    result = []
    
    for line_idx, line in enumerate(lines):
        # Skip leading whitespace (indentation)
        stripped_line = line.lstrip()
        
        print(f"Line {line_idx}:")
        print(f"  Original: '{line}'")
        print(f"  Leading spaces: {len(line) - len(stripped_line)}")
        print(f"  Will type: '{stripped_line}'")
        
        result.append(stripped_line)
    
    return '\n'.join(result)


if __name__ == "__main__":
    # Example Python code with indentation
    code = """def searchInsert(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left"""
    
    print("="*60)
    print("ORIGINAL CODE:")
    print("="*60)
    print(code)
    print()
    
    print("="*60)
    print("PROCESSING:")
    print("="*60)
    processed = process_code(code)
    print()
    
    print("="*60)
    print("WHAT BOT WILL TYPE:")
    print("="*60)
    print(processed)
    print()
    
    print("="*60)
    print("KEY POINTS:")
    print("="*60)
    print("✅ Leading spaces removed (game auto-indents)")
    print("✅ Inline spaces preserved (e.g., 'n - 1')")
    print("✅ Function names preserve case (searchInsert)")

