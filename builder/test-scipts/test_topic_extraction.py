#!/usr/bin/env python3
"""
Test the topic extraction functionality
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from content_manager import ContentManager
from json_database import JSONDatabaseManager

def test_topic_extraction():
    """Test topic extraction with the provided sample"""
    
    # Sample content (your example)
    sample_content = """
A gente cuida da casa, da família, dos outros… mas e da nossa mente, do nosso coração, da nossa essência? ✨Há alguns anos, fiz um compromisso comigo mesma: criar o hábito de meditar. E posso dizer com todo carinho — foi uma das melhores escolhas que já fiz! 🌸A meditação me trouxe mais clareza, equilíbrio emocional e a capacidade de enxergar a vida com mais leveza. Um espaço só meu, para reconectar com a minha essência e transformar a forma como eu reajo às situações.Se você ainda não experimentou, fica aqui o convite: pare, respire, e dê esse presente pra você.
"""
    
    # Initialize
    db = JSONDatabaseManager("data")
    content_manager = ContentManager(db)
    
    # Test extraction
    print("🧪 Testing Topic Extraction...")
    print(f"Content length: {len(sample_content)} chars")
    print(f"Content preview: {sample_content[:100]}...")
    
    topics = content_manager.extract_topics_with_ai(
        content=sample_content,
        guidance="50+ female health and wellness tips",
        creator_name="Longe Vida",
        provider="gemini_openai"
    )
    
    print(f"\n🎯 Extracted {len(topics)} topics:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic} ({len(topic)} chars)")
    
    return topics

if __name__ == "__main__":
    try:
        topics = test_topic_extraction()
        print(f"\n✅ Test completed! Found {len(topics)} topics")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
