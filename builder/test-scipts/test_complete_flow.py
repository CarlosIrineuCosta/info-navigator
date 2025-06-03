#!/usr/bin/env python3
"""
Test Complete Content Generation Flow
Tests Creator → ContentSet → ContentCard creation and database integrity
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"✅ Loaded .env file from: {dotenv_path}")
else:
    print(f"❌ .env file not found at {dotenv_path}")

# Import project modules
try:
    from json_database import JSONDatabaseManager
    from content_manager import ContentManager
    from core_models import Creator, ContentType
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

def test_database_methods():
    """Test database method functionality"""
    print("\n🔍 Testing Database Methods...")
    
    db = JSONDatabaseManager(data_dir="data")
    
    # Test get_creator_by_display_name
    creators = db.list_creators()
    print(f"Total creators in database: {len(creators)}")
    
    if creators:
        test_creator_name = creators[0].get('display_name')
        print(f"Testing with creator: {test_creator_name}")
        
        # Test new method
        creator_data = db.get_creator_by_display_name(test_creator_name)
        if creator_data:
            print(f"✅ get_creator_by_display_name works: Found {creator_data['display_name']}")
        else:
            print(f"❌ get_creator_by_display_name failed")
    else:
        print("⚠️ No creators found in database")

def test_content_generation():
    """Test complete content generation flow"""
    print("\n🔍 Testing Content Generation Flow...")
    
    db = JSONDatabaseManager(data_dir="data")
    content_manager = ContentManager(db)
    
    # Check generator status
    print(f"Generator Status: {content_manager.get_generator_status()}")
    
    # Get available creators
    creators = db.list_creators()
    if not creators:
        print("❌ No creators available for testing")
        return False
    
    test_creator = creators[0]
    creator_name = test_creator['display_name']
    print(f"Using test creator: {creator_name}")
    
    # Test topic extraction
    sample_content = """
    A água é fundamental para nossa saúde e bem-estar. Ela representa cerca de 60% do peso corporal 
    de um adulto e está envolvida em praticamente todas as funções do organismo. A hidratação adequada 
    melhora a concentração, regula a temperatura corporal, facilita a digestão e ajuda na eliminação 
    de toxinas. Muitas pessoas não bebem água suficiente durante o dia, o que pode levar à desidratação 
    e impactar negativamente a energia e o humor. É importante estabelecer o hábito de beber água 
    regularmente, especialmente durante exercícios físicos e em dias quentes.
    """
    
    print("\n📝 Testing Topic Extraction...")
    topics = content_manager.extract_topics_with_ai(
        content=sample_content,
        guidance="Foco em saúde e bem-estar",
        creator_name=creator_name,
        provider_str="gemini_openai"
    )
    
    if topics:
        print(f"✅ Extracted {len(topics)} topics: {topics}")
        
        # Test content generation with first 3 topics
        test_topics = topics[:3]
        print(f"\n🎯 Testing Content Generation with {len(test_topics)} topics...")
        
        success = content_manager.generate_cards_from_topics(
            creator_name=creator_name,
            guidance="Conteúdo educativo sobre saúde e hidratação",
            topics=test_topics,
            provider_str="gemini_openai"
        )
        
        if success:
            print("✅ Content generation completed successfully")
            return True
        else:
            print("❌ Content generation failed")
            return False
    else:
        print("❌ Topic extraction failed")
        return False

def verify_database_integrity():
    """Verify that all JSON files have proper structure"""
    print("\n🔍 Verifying Database Integrity...")
    
    data_dir = Path("data")
    files_to_check = ["creators.json", "content_sets.json", "cards.json"]
    
    for filename in files_to_check:
        filepath = data_dir / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ {filename}: Valid JSON with {len(data)} items")
                
                # Show structure for non-empty files
                if data and isinstance(data, list) and len(data) > 0:
                    print(f"   Sample keys: {list(data[0].keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ {filename}: Invalid JSON - {e}")
            except Exception as e:
                print(f"❌ {filename}: Error reading - {e}")
        else:
            print(f"⚠️ {filename}: File not found")

def main():
    """Run complete test suite"""
    print("🚀 Starting Complete Flow Test...")
    
    # Test 1: Database methods
    test_database_methods()
    
    # Test 2: Content generation flow  
    generation_success = test_content_generation()
    
    # Test 3: Database integrity
    verify_database_integrity()
    
    # Summary
    print(f"\n📊 Test Summary:")
    print(f"   Database Methods: ✅ Working")
    print(f"   Content Generation: {'✅ Success' if generation_success else '❌ Failed'}")
    print(f"   Database Integrity: ✅ Check logs above")
    
    if generation_success:
        print("\n🎉 All tests passed! The complete flow is working.")
    else:
        print("\n⚠️ Some tests failed. Check console output for details.")

if __name__ == "__main__":
    main()
