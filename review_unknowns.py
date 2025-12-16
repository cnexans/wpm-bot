#!/usr/bin/env python3
"""
Review unknown functions and suggest corrections.
"""

import os
import json
from pathlib import Path


def load_available_functions():
    """Load list of available functions from database."""
    with open('CodeBlocks.json') as f:
        blocks = json.load(f)
    return sorted(set(b['title'].lower() for b in blocks))


def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def calculate_similarity(s1, s2):
    """Calculate similarity (0.0 to 1.0) using Levenshtein distance."""
    if not s1 or not s2:
        return 0.0
    
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    
    # Convert distance to similarity
    similarity = 1.0 - (distance / max_len)
    return similarity


def suggest_corrections():
    """Review unknown functions and suggest corrections."""
    history_dir = Path('unknown_snippets_history')
    
    if not history_dir.exists():
        print("No unknown functions history found.")
        return
    
    # Find all .txt files
    txt_files = sorted(history_dir.glob('*.txt'))
    
    if not txt_files:
        print("No unknown functions found in history.")
        return
    
    print(f"📚 Found {len(txt_files)} unknown function(s)\n")
    
    # Load available functions
    available = load_available_functions()
    
    # Load existing corrections
    try:
        with open('ocr_corrections.json') as f:
            existing = json.load(f)['corrections']
    except:
        existing = {}
    
    suggestions = []
    
    for txt_file in txt_files:
        # Read the info file
        with open(txt_file) as f:
            content = f.read()
        
        # Extract OCR name
        for line in content.split('\n'):
            if line.startswith('OCR Detected:'):
                ocr_name = line.split(':', 1)[1].strip().lower()
                break
        else:
            continue
        
        # Check if already corrected
        if ocr_name in existing:
            print(f"✅ Already corrected: {ocr_name} → {existing[ocr_name]}")
            continue
        
        # Clean OCR name (remove common prefixes)
        clean_ocr = ocr_name
        for prefix in ['def', 'var', 'function', 'func', 'const', 'let']:
            if clean_ocr.startswith(prefix):
                clean_ocr = clean_ocr[len(prefix):]
                break
        
        # Find best matches
        matches = []
        for func in available:
            # Try both original and cleaned versions
            sim1 = calculate_similarity(ocr_name, func)
            sim2 = calculate_similarity(clean_ocr, func)
            similarity = max(sim1, sim2)
            
            # Also check if func is substring of ocr or vice versa
            if func in clean_ocr or clean_ocr in func:
                similarity = max(similarity, 0.8)
            
            if similarity > 0.5:
                matches.append((func, similarity))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        
        print(f"❓ Unknown: {ocr_name}")
        print(f"   Screenshot: {txt_file.stem}.png")
        
        if matches:
            print(f"   Top suggestions:")
            for func, sim in matches[:5]:
                print(f"     - {func:25} (similarity: {sim:.0%})")
            
            best_match = matches[0][0]
            suggestions.append((ocr_name, best_match))
            print(f"   💡 Suggested: python add_ocr_correction.py '{ocr_name}' '{best_match}'")
        else:
            print(f"   ⚠️  No similar functions found")
        
        print()
    
    # Summary
    if suggestions:
        print("\n" + "="*60)
        print("🔧 SUGGESTED CORRECTIONS:")
        print("="*60)
        for ocr, correct in suggestions:
            print(f"python add_ocr_correction.py '{ocr}' '{correct}'")
        print()


if __name__ == "__main__":
    suggest_corrections()

