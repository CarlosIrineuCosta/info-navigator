#!/usr/bin/env python3
"""
Test the dropdown functionality separately
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from json_database import JSONDatabaseManager
from creator_manager import CreatorManager

def test_dropdown():
    """Test dropdown functionality"""
    print("🧪 Testing Dropdown Functionality...")
    
    db = JSONDatabaseManager("data")
    creator_manager = CreatorManager(db)
    
    # Test the dropdown method
    dropdown_choices = creator_manager.get_creators_for_dropdown()
    print(f"Dropdown choices type: {type(dropdown_choices)}")
    print(f"Dropdown choices: {dropdown_choices}")
    print(f"First choice type: {type(dropdown_choices[0]) if dropdown_choices else 'None'}")
    
    if dropdown_choices:
        print(f"First choice: {dropdown_choices[0]}")
        print(f"Structure: (display='{dropdown_choices[0][0]}', value='{dropdown_choices[0][1]}')")

if __name__ == "__main__":
    test_dropdown()
