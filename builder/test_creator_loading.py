#!/usr/bin/env python3
"""
Test script to debug creator loading issues
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from json_database import JSONDatabaseManager
from creator_manager import CreatorManager

def test_creator_loading():
    """Test if creators are loading correctly"""
    print("🧪 Testing Creator Loading...")
    
    # Initialize database
    db = JSONDatabaseManager("data")
    creator_manager = CreatorManager(db)
    
    # Test direct database access
    print("\n1. Testing direct database access:")
    try:
        creators = db.list_creators()
        print(f"   Found {len(creators)} creators in database")
        for creator in creators:
            print(f"   - {creator['display_name']} (ID: {creator['creator_id']})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test creator manager dropdown
    print("\n2. Testing creator manager dropdown:")
    try:
        dropdown_choices = creator_manager.get_creators_for_dropdown()
        print(f"   Dropdown choices: {len(dropdown_choices)}")
        for display_name, creator_id in dropdown_choices:
            print(f"   - {display_name} → {creator_id}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test individual creator access
    print("\n3. Testing individual creator access:")
    if creators:
        first_creator_id = creators[0]['creator_id']
        try:
            creator = db.get_creator(first_creator_id)
            print(f"   Retrieved creator: {creator['display_name']}")
        except Exception as e:
            print(f"   Error retrieving creator: {e}")
    
    # Test category formatting
    print("\n4. Testing category formatting:")
    try:
        formatted_cats = creator_manager.get_formatted_categories()
        print(f"   Available categories: {len(formatted_cats)}")
        for value, display in formatted_cats[:3]:  # Show first 3
            print(f"   - {value} → {display}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_creator_loading()
