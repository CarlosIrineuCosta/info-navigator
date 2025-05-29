#!/usr/bin/env python3
"""
Test Multi-Provider Content Generation
Quick test of the unified generator with multiple providers
"""

import sys
import os
sys.path.append('.')

from unified_generator import get_unified_generator, ContentGenerationRequest, LLMProvider
from core_models import ContentType

# Load environment variables
from dotenv import load_dotenv
load_dotenv("../.env")

def test_providers():
    """Test which providers are available"""
    print("🧪 Testing Multi-Provider System...")
    
    try:
        # Initialize unified generator
        generator = get_unified_generator()
        
        # Show available providers
        providers = generator.get_available_providers()
        print(f"\n✅ Available providers: {[p.value for p in providers]}")
        
        # Show provider cost information
        provider_info = generator.get_provider_info()
        print(f"\n💰 Provider Costs (per 1k tokens):")
        for provider, info in provider_info.items():
            print(f"  • {provider}: ${info['cost_per_1k']} input / ${info['output_cost']} output - {info['description']}")
        
        print(f"\n🎯 Default provider: {generator.default_provider.value}")
        
        return generator
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def estimate_costs():
    """Estimate costs for 20 cards across providers"""
    print(f"\n📊 Cost Estimation for 20 Cards:")
    
    # Estimated tokens for 20 cards
    input_tokens = 16000  # ~800 per card
    output_tokens = 12000  # ~600 per card
    
    costs = {
        "Gemini 2.0 Flash (OpenAI API)": (input_tokens/1000 * 0.0001) + (output_tokens/1000 * 0.0007),
        "Claude 3.5 Haiku": (input_tokens/1000 * 0.0008) + (output_tokens/1000 * 0.004),
        "GPT-4o mini": (input_tokens/1000 * 0.00015) + (output_tokens/1000 * 0.0006),
        "Claude 3.5 Sonnet": (input_tokens/1000 * 0.003) + (output_tokens/1000 * 0.015)
    }
    
    for provider, cost in costs.items():
        print(f"  • {provider}: ${cost:.4f}")
    
    print(f"\n💡 Gemini is ~{costs['Claude 3.5 Sonnet']/costs['Gemini 2.0 Flash (OpenAI API)']:.0f}x cheaper than Claude!")

def main():
    """Main test function"""
    print("🚀 Multi-Provider Content Generator Test")
    print("=" * 50)
    
    # Test provider initialization
    generator = test_providers()
    
    if generator:
        # Show cost estimates
        estimate_costs()
        
        print(f"\n✨ System ready for content generation!")
        print(f"📝 To generate content:")
        print(f"   1. Add your Google API key to .env file")
        print(f"   2. Run: python gradio_app.py")
        print(f"   3. Generate 20 cards for ~$0.01 with Gemini!")
    else:
        print(f"\n⚠️  Setup required:")
        print(f"   1. pip install -r requirements.txt")
        print(f"   2. Add API keys to .env file")

if __name__ == "__main__":
    main()
