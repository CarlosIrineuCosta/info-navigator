#!/usr/bin/env python3
"""
Standalone API Test - Test Gemini API call directly
This will help us debug the topic extraction issue
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

def test_basic_api_connection():
    """Test basic API connection and response"""
    print("🧪 Testing Gemini API Connection")
    print("=" * 50)
    
    # Check API key
    google_key = os.getenv("GOOGLE_API_KEY", "")
    print(f"API Key loaded: {len(google_key)} characters")
    print(f"Key starts with: {google_key[:10]}..." if google_key else "NO KEY")
    
    if not google_key or len(google_key) < 10:
        print("❌ No valid Google API key found!")
        return False
    
    try:
        # Test OpenAI-compatible endpoint (same as our app)
        from openai import OpenAI
        
        client = OpenAI(
            api_key=google_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        print("✅ OpenAI client created successfully")
        
        # Simple test prompt
        test_prompt = """
Você é um assistente em português brasileiro.
Responda apenas: "Conexão funcionando!"
"""
        
        print(f"\n📤 Sending test prompt...")
        print(f"Prompt: {test_prompt}")
        
        response = client.chat.completions.create(
            model="gemini-2.5-pro-exp-03-25",
            messages=[
                {"role": "system", "content": "Você é um assistente útil em português brasileiro."},
                {"role": "user", "content": test_prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"\n📥 Response received!")
        print(f"Full response object: {response}")
        print(f"Content: {response.choices[0].message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_topic_extraction():
    """Test the actual topic extraction"""
    print("\n🎯 Testing Topic Extraction")
    print("=" * 50)
    
    # Sample content (your example)
    sample_content = """
A gente cuida da casa, da família, dos outros mas e da nossa mente, do nosso coração, da nossa essência? Há alguns anos, fiz um compromisso comigo mesma: criar o hábito de meditar. E posso dizer com todo carinho foi uma das melhores escolhas que já fiz! A meditação me trouxe mais clareza, equilíbrio emocional e a capacidade de enxergar a vida com mais leveza. Um espaço só meu, para reconectar com a minha essência e transformar a forma como eu reajo às situações. Se você ainda não experimentou, fica aqui o convite: pare, respire, e dê esse presente pra você.
"""
    
    try:
        from openai import OpenAI
        
        google_key = os.getenv("GOOGLE_API_KEY", "")
        client = OpenAI(
            api_key=google_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        # Topic extraction prompt
        prompt = f"""
Você é um especialista em análise de conteúdo educacional em português brasileiro.

Analise o seguinte conteúdo e extraia 5-8 tópicos específicos para criação de conteúdo educacional.

Criador: Longe Vida
Orientação de Conteúdo: 50+ female health, emotional and wellness content, in a soft, endearing personal voice; creator is a female

Conteúdo para analisar:
{sample_content}

Requisitos:
- Extraia 5-8 tópicos específicos em português
- Cada tópico deve ter 5-50 caracteres
- Tópicos devem ser relevantes ao estilo do criador
- Retorne APENAS a lista de tópicos, um por linha
- Sem numeração, sem bullets, sem texto adicional

Exemplo de formato:
benefícios da meditação
equilíbrio emocional
redução do estresse
práticas de mindfulness
rotinas de autocuidado
"""
        
        print(f"Content length: {len(sample_content)}")
        print(f"Prompt length: {len(prompt)}")
        
        response = client.chat.completions.create(
            model="gemini-2.5-pro-exp-03-25",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        print(f"\n📥 Raw AI Response:")
        print(f"'{content}'")
        
        # Parse topics
        topics = []
        for line in content.split('\n'):
            line = line.strip()
            if line and 5 <= len(line) <= 50:
                topics.append(line)
        
        print(f"\n🎯 Extracted Topics ({len(topics)}):")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic} ({len(topic)} chars)")
        
        return topics
        
    except Exception as e:
        print(f"❌ Topic extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """Run all tests"""
    print("🚀 Gemini API Test Suite")
    print("=" * 60)
    
    # Test 1: Basic connection
    if not test_basic_api_connection():
        print("\n❌ Basic API test failed - stopping here")
        return
    
    # Test 2: Topic extraction
    topics = test_topic_extraction()
    
    if topics:
        print(f"\n✅ SUCCESS! Extracted {len(topics)} topics")
        print("Topic extraction is working correctly!")
    else:
        print(f"\n❌ FAILED! No topics extracted")
        print("There's an issue with the topic extraction logic")

if __name__ == "__main__":
    main()
