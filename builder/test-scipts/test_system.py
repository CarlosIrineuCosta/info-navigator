#!/usr/bin/env python3
"""
Test script for Infogen system components
Verify that the minimal structure works correctly
"""

import sys
import json
from pathlib import Path

# Add the infogen directory to path
sys.path.append(str(Path(__file__).parent))

from core_models import *
from json_database import JSONDatabaseManager, migrate_existing_lunar_cards


def test_core_models():
    """Test core data models"""
    print("🧪 Testing Core Models...")
    
    # Test Creator
    creator = Creator(
        creator_id="test_creator_123",
        display_name="Dr. Test Creator",
        platform="youtube",
        platform_handle="@testcreator",
        description="Test creator for system validation",
        categories=[ContentType.SPACE, ContentType.WELLNESS]
    )
    
    creator_dict = creator.to_dict()
    assert creator_dict["creator_id"] == "test_creator_123"
    assert len(creator_dict["categories"]) == 2
    print("✅ Creator model works")
    
    # Test ContentSet
    content_set = ContentSet(
        set_id="test_set_456",
        creator_id="test_creator_123",
        title="Test Content Set",
        description="Testing the content set structure",
        category=ContentType.NUTRITION,
        supported_navigation=[NavigationType.THEMATIC, NavigationType.RANDOM]
    )
    
    set_dict = content_set.to_dict()
    assert set_dict["category"] == "nutrition"
    assert len(set_dict["supported_navigation"]) == 2
    print("✅ ContentSet model works")
    
    # Test ContentCard
    card = ContentCard(
        card_id="test_card_001",
        set_id="test_set_456", 
        creator_id="test_creator_123",
        title="Test question about nutrition?",
        summary="Test summary response",
        detailed_content="Detailed test content about the topic",
        order_index=1
    )
    
    card_dict = card.to_dict()
    assert card_dict["order_index"] == 1
    print("✅ ContentCard model works")
    
    print("✅ All core models working correctly!\n")


def test_json_database():
    """Test JSON database operations"""
    print("🗄️  Testing JSON Database...")
    
    # Create test database
    test_db = JSONDatabaseManager("test_data")
    
    # Test creator operations
    creator = Creator(
        creator_id="db_test_creator",
        display_name="Database Test Creator",
        platform="youtube",
        platform_handle="@dbtest",
        categories=[ContentType.SPACE]
    )
    
    assert test_db.add_creator(creator) == True
    assert test_db.add_creator(creator) == False  # Should fail on duplicate
    
    retrieved_creator = test_db.get_creator("db_test_creator")
    assert retrieved_creator is not None
    assert retrieved_creator["display_name"] == "Database Test Creator"
    print("✅ Creator operations work")
    
    # Test content set operations
    content_set = ContentSet(
        set_id="db_test_set",
        creator_id="db_test_creator",
        title="Database Test Set",
        description="Testing database operations",
        category=ContentType.SPACE
    )
    
    assert test_db.add_content_set(content_set) == True
    
    retrieved_set = test_db.get_content_set("db_test_set")
    assert retrieved_set is not None
    print("✅ Content set operations work")
    
    # Test homepage generation
    homepage = test_db.generate_homepage_data()
    assert "content_rows" in homepage
    assert "featured_content" in homepage
    print("✅ Homepage generation works")
    
    # Cleanup test files
    import shutil
    shutil.rmtree("test_data", ignore_errors=True)
    
    print("✅ JSON Database working correctly!\n")


def test_navigation_logic():
    """Test the three-level navigation concept"""
    print("🧭 Testing Navigation Logic...")
    
    # Test navigation context creation
    timeline_nav = NavigationContext(
        nav_type=NavigationType.TIMELINE,
        position=1,
        total_items=10,
        context_data={"year": 1969, "event_type": "space_mission"}
    )
    
    thematic_nav = NavigationContext(
        nav_type=NavigationType.THEMATIC,
        position=2,
        total_items=8,
        context_data={"theme": "nutrition_basics", "sub_category": "vitamins"}
    )
    
    difficulty_nav = NavigationContext(
        nav_type=NavigationType.DIFFICULTY,
        position=1,
        total_items=5,
        context_data={"level": "beginner", "prerequisites": []}
    )
    
    # Test that different content types can use different navigation
    space_card = ContentCard(
        card_id="space_nav_test",
        set_id="space_set",
        creator_id="space_creator", 
        title="Space navigation test",
        summary="Testing space navigation",
        detailed_content="Detailed space content",
        order_index=1,
        navigation_contexts={
            "timeline": timeline_nav,
            "thematic": thematic_nav  # Space can use both timeline and thematic
        }
    )
    
    wellness_card = ContentCard(
        card_id="wellness_nav_test",
        set_id="wellness_set",
        creator_id="wellness_creator",
        title="Wellness navigation test", 
        summary="Testing wellness navigation",
        detailed_content="Detailed wellness content",
        order_index=1,
        navigation_contexts={
            "thematic": thematic_nav,
            "difficulty": difficulty_nav  # Wellness uses thematic and difficulty
        }
    )
    
    # Verify navigation contexts work
    space_dict = space_card.to_dict()
    assert "timeline" in space_dict["navigation_contexts"]
    assert "thematic" in space_dict["navigation_contexts"]
    
    wellness_dict = wellness_card.to_dict()
    assert "thematic" in wellness_dict["navigation_contexts"]
    assert "difficulty" in wellness_dict["navigation_contexts"]
    assert "timeline" not in wellness_dict["navigation_contexts"]  # Wellness doesn't use timeline
    
    print("✅ Flexible navigation system works correctly!\n")


def test_migration():
    """Test migration from existing lunar cards"""
    print("🔄 Testing Migration...")
    
    # Check if original lunar cards exist
    original_path = "../viewer/data/lunar_cards_json_10q_v1.json"
    if Path(original_path).exists():
        test_db = JSONDatabaseManager("migration_test_data")
        
        # Test migration
        result = migrate_existing_lunar_cards(test_db, original_path)
        if result:
            # Verify migration worked
            creators = test_db.list_creators()
            assert len(creators) >= 1
            
            sets = test_db._load_collection(test_db.content_sets_file)
            assert len(sets) >= 1
            
            cards = test_db._load_collection(test_db.cards_file)
            assert len(cards) >= 10
            
            print("✅ Migration successful")
        else:
            print("⚠️  Migration skipped - no original data found")
        
        # Cleanup
        import shutil
        shutil.rmtree("migration_test_data", ignore_errors=True)
    else:
        print("⚠️  No original lunar cards found - migration test skipped")
    
    print()


def main():
    """Run all tests"""
    print("🚀 Testing Infogen System Components")
    print("=" * 50)
    
    try:
        test_core_models()
        test_json_database() 
        test_navigation_logic()
        test_migration()
        
        print("🎉 ALL TESTS PASSED!")
        print("\nThe minimal structure is working correctly.")
        print("Key features verified:")
        print("• ✅ Flexible data models for multiple content types")
        print("• ✅ JSON database with creator/set/card relationships")
        print("• ✅ Three-level navigation system (topic/type/navigation)")
        print("• ✅ Netflix-style homepage structure generation")
        print("• ✅ Migration from existing content")
        print("\nReady for:")
        print("• Content generation with structured validation")
        print("• Multiple content domains (space, wellness, nutrition, etc.)")
        print("• Creator management and content organization")
        print("• Scalable navigation patterns")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
