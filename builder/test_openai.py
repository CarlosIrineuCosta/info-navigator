#!/usr/bin/env python3
"""
Test OpenAI API as backup
"""

import os
from dotenv import load_dotenv

load_dotenv("../.env")

def test_openai():
    """Test OpenAI API"""
    print("🧪 Testing OpenAI API")
    
    openai_key = os.getenv("OPENAI_API_KEY", "")
    print(f"OpenAI Key: {len(openai_key)} chars")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=openai_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Responda em português: liste 3 tópicos sobre meditação"}
            ],
            max_tokens=100
        )
        
        print(f"✅ OpenAI Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI failed: {e}")
        return False

if __name__ == "__main__":
    test_openai()
