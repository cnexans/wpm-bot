#!/usr/bin/env python3
"""
Tool to add OCR corrections to the mapping file.
Usage: python add_ocr_correction.py <ocr_error> <correct_name>
"""

import json
import sys


def add_correction(ocr_error, correct_name):
    """Add a new OCR correction to the map."""
    # Load existing corrections
    try:
        with open('ocr_corrections.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"comment": "Map common OCR errors to correct function names", "corrections": {}}
    
    # Add new correction
    ocr_lower = ocr_error.lower()
    correct_lower = correct_name.lower()
    
    data['corrections'][ocr_lower] = correct_lower
    
    # Save back
    with open('ocr_corrections.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Added correction: '{ocr_error}' → '{correct_name}'")
    print(f"   Total corrections: {len(data['corrections'])}")


def list_corrections():
    """List all current corrections."""
    try:
        with open('ocr_corrections.json', 'r') as f:
            data = json.load(f)
        
        corrections = data.get('corrections', {})
        print(f"Current OCR Corrections ({len(corrections)}):")
        print("="*60)
        
        for ocr, correct in sorted(corrections.items()):
            print(f"  {ocr:30} → {correct}")
    except FileNotFoundError:
        print("No corrections file found.")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments, list corrections
        list_corrections()
    elif len(sys.argv) == 3:
        # Add new correction
        ocr_error = sys.argv[1]
        correct_name = sys.argv[2]
        add_correction(ocr_error, correct_name)
    else:
        print("Usage:")
        print("  python add_ocr_correction.py                    # List all corrections")
        print("  python add_ocr_correction.py <error> <correct>  # Add new correction")
        print()
        print("Example:")
        print("  python add_ocr_correction.py 'inordertraversait' 'inordertraversal'")

