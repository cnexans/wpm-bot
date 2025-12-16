#!/usr/bin/env python3
"""
Test uppercase character typing.
"""

def test_case_preservation():
    """Test that case is preserved correctly."""
    test_strings = [
        "searchInsert",
        "addBinary", 
        "twoSum",
        "MyClass",
        "CONSTANT_VALUE",
        "mixedCASEstring"
    ]
    
    print("Testing case preservation:")
    for s in test_strings:
        # Count uppercase
        upper_count = sum(1 for c in s if c.isupper())
        lower_count = sum(1 for c in s if c.islower())
        
        print(f"  '{s}' - {upper_count} uppercase, {lower_count} lowercase")
        
        # Verify each character
        for i, char in enumerate(s):
            if char.isupper():
                print(f"    Position {i}: '{char}' is uppercase ✓")

if __name__ == "__main__":
    test_case_preservation()
    
    print("\n" + "="*60)
    print("Testing typing logic:")
    print("="*60)
    
    text = "searchInsert"
    print(f"\nTyping: '{text}'")
    
    for i, char in enumerate(text):
        if char.isupper():
            print(f"  {i}: '{char}' → SHIFT + '{char.lower()}'")
        else:
            print(f"  {i}: '{char}' → '{char}'")

