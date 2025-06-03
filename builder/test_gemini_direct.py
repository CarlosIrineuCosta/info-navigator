#!/usr/bin/env python3
"""
Simple standalone test for Gemini API using OpenAI-compatible endpoint
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

def test_gemini_api():
    """Test direct Gemini API call"""
    
    print("🧪 Testing Gemini API Connection...")
    
    # Get API key
    google_key = os.getenv("GOOGLE_API_KEY", "")
    print(f"API Key length: {len(google_key)} chars")
    print(f"API Key starts with: {google_key[:10]}...")
    
    if not google_key or len(google_key) < 10:
        print("❌ No valid Google API key found")
        return False
    
    try:
        from openai import OpenAI
        
        # Create client with Gemini endpoint
        client = OpenAI(
            api_key=google_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        print("✅ OpenAI client created with Gemini endpoint")
        
        # Test content
        test_content = """A gente cuida da casa, da família, dos outros… mas e da nossa mente, do nosso coração, da nossa essência? Há alguns anos, fiz um compromisso comigo mesma: criar o hábito de meditar. E posso dizer com todo carinho — foi uma das melhores escolhas que já fiz! A meditação me trouxe mais clareza, equilíbrio emocional e a capacidade de enxergar a vida com mais leveza."""
        
        # Create request
        response = client.chat.completions.create(
            model="gemini-2.5-pro-exp-03-25",
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um especialista em análise de conteúdo educacional em português brasileiro."
                },
                {
                    "role": "user", 
                    "content": f"""Analise o seguinte conteúdo e extraia 5 tópicos específicos para criação de conteúdo educacional.

Conteúdo para analisar:
{test_content}

Requisitos:
- Extraia 5 tópicos específicos em português
- Cada tópico deve ter 5-50 caracteres
- Retorne APENAS a lista de tópicos, um por linha
- Sem numeração, sem bullets, sem texto adicional

Exemplo de formato:
benefícios da meditação
equilíbrio emocional
redução do estresse"""
                }
            ]
        )
        
        print("✅ API call successful!")
        print(f"Response type: {type(response)}")
        print(f"Response: {response}")
        print(f"Message content: {response.choices[0].message.content}")
        
        # Parse topics
        content = response.choices[0].message.content
        topics = [line.strip() for line in content.split('\n') if line.strip()]
        
        print(f"\n🎯 Extracted {len(topics)} topics:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
