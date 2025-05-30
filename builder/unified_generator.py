#!/usr/bin/env python3
"""
Multi-Provider Content Generator
Supports Claude (Anthropic), Gemini (Google), and other LLM providers
with unified interface and provider switching
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import os

# Provider imports with fallbacks
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False

from core_models import ContentType, NavigationType


class LLMProvider(Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI = "openai"
    GEMINI_OPENAI = "gemini_openai"  # Gemini via OpenAI-compatible API


@dataclass
class ContentGenerationRequest:
    """Request structure for content generation"""
    topic: str
    content_type: ContentType
    card_count: int = 10
    difficulty_level: str = "intermediate"
    content_style: str = "question_first"
    target_audience: str = "general_public"
    language: str = "pt-BR"
    provider: LLMProvider = LLMProvider.GEMINI_OPENAI  # Default to cheapest


class UnifiedContentGenerator:
    """Unified content generator supporting multiple LLM providers"""
    
    def __init__(self, 
                 anthropic_api_key: Optional[str] = None,
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        
        self.providers = {}
        self.default_provider = None
        
        # Initialize available providers
        self._setup_anthropic(anthropic_api_key)
        self._setup_gemini_openai(gemini_api_key)
        self._setup_openai(openai_api_key)
        self._setup_gemini_native(gemini_api_key)
        
        # Set default provider
        if LLMProvider.GEMINI_OPENAI in self.providers:
            self.default_provider = LLMProvider.GEMINI_OPENAI
        elif LLMProvider.ANTHROPIC in self.providers:
            self.default_provider = LLMProvider.ANTHROPIC
        elif LLMProvider.OPENAI in self.providers:
            self.default_provider = LLMProvider.OPENAI
        
        self.card_schema = self._create_card_schema()
    
    def _setup_anthropic(self, api_key: Optional[str]):
        """Setup Anthropic Claude provider"""
        if ANTHROPIC_AVAILABLE and api_key:
            try:
                self.providers[LLMProvider.ANTHROPIC] = anthropic.Client(api_key=api_key)
                print("✅ Anthropic Claude provider initialized")
            except Exception as e:
                print(f"❌ Anthropic setup failed: {e}")
    
    def _setup_gemini_openai(self, api_key: Optional[str]):
        """Setup Gemini via OpenAI-compatible API (recommended)"""
        if OPENAI_AVAILABLE and api_key:
            try:
                # Gemini via OpenAI-compatible endpoint
                self.providers[LLMProvider.GEMINI_OPENAI] = OpenAI(
                    api_key=api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
                )
                print("✅ Gemini (OpenAI-compatible) provider initialized")
            except Exception as e:
                print(f"❌ Gemini OpenAI setup failed: {e}")
    
    def _setup_openai(self, api_key: Optional[str]):
        """Setup OpenAI provider"""
        if OPENAI_AVAILABLE and api_key:
            try:
                self.providers[LLMProvider.OPENAI] = OpenAI(api_key=api_key)
                print("✅ OpenAI provider initialized")
            except Exception as e:
                print(f"❌ OpenAI setup failed: {e}")
    
    def _setup_gemini_native(self, api_key: Optional[str]):
        """Setup native Gemini provider"""
        if GOOGLE_GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.providers[LLMProvider.GEMINI] = genai
                print("✅ Gemini (native) provider initialized")
            except Exception as e:
                print(f"❌ Gemini native setup failed: {e}")
    
    def _create_card_schema(self) -> Dict[str, Any]:
        """JSON schema for individual content cards"""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Engaging question format, max 200 characters"
                },
                "summary": {
                    "type": "string", 
                    "description": "Brief answer in 2-3 sentences, max 300 characters"
                },
                "detailed_content": {
                    "type": "string",
                    "description": "Full explanation in 3-4 paragraphs, max 1500 characters"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "5-7 relevant keywords for image search"
                },
                "difficulty_tags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"]
                    }
                },
                "domain_specific": {
                    "type": "object",
                    "properties": {
                        "historical_date": {"type": "string"},
                        "category_tags": {
                            "type": "array", 
                            "items": {"type": "string"}
                        },
                        "scientific_accuracy": {"type": "string"},
                        "practical_application": {"type": "string"}
                    }
                }
            },
            "required": ["title", "summary", "detailed_content", "keywords", "difficulty_tags"]
        }
    
    def get_available_providers(self) -> List[LLMProvider]:
        """Get list of initialized providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers"""
        provider_costs = {
            LLMProvider.GEMINI_OPENAI: {"cost_per_1k": 0.0001, "output_cost": 0.0007, "description": "Google Gemini 2.0 Flash (cheapest)"},
            LLMProvider.ANTHROPIC: {"cost_per_1k": 0.003, "output_cost": 0.015, "description": "Claude 3.5 Sonnet (high quality)"},
            LLMProvider.OPENAI: {"cost_per_1k": 0.00015, "output_cost": 0.0006, "description": "GPT-4o mini (balanced)"},
            LLMProvider.GEMINI: {"cost_per_1k": 0.0001, "output_cost": 0.0007, "description": "Gemini 2.0 Flash (native API)"}
        }
        
        available_info = {}
        for provider in self.providers.keys():
            available_info[provider.value] = {
                "available": True,
                **provider_costs.get(provider, {"cost_per_1k": "unknown", "description": "Unknown provider"})
            }
        
        return available_info
    
    async def generate_content_card(self, 
                                   topic: str, 
                                   content_type: ContentType,
                                   card_context: str = "",
                                   provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """Generate a single content card using specified or default provider"""
        
        if provider is None:
            provider = self.default_provider
        
        if provider not in self.providers:
            raise ContentGenerationError(f"Provider {provider.value} not available")
        
        prompt = self._build_card_prompt(topic, content_type, card_context)
        
        try:
            if provider == LLMProvider.ANTHROPIC:
                return await self._generate_with_anthropic(prompt)
            elif provider in [LLMProvider.GEMINI_OPENAI, LLMProvider.OPENAI]:
                model_name = "gemini-2.0-flash" if provider == LLMProvider.GEMINI_OPENAI else "gpt-4o-mini"
                return await self._generate_with_openai_compatible(prompt, provider, model_name)
            elif provider == LLMProvider.GEMINI:
                return await self._generate_with_gemini_native(prompt)
            else:
                raise ContentGenerationError(f"Provider {provider.value} not implemented")
                
        except Exception as e:
            raise ContentGenerationError(f"Generation failed with {provider.value}: {str(e)}")
    
    async def _generate_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Generate using Anthropic Claude"""
        client = self.providers[LLMProvider.ANTHROPIC]
        
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Cheaper Haiku model
            max_tokens=2000,
            messages=[{"role": "user", "content": self._format_structured_prompt(prompt)}]
        )
        
        return self._parse_structured_response(response.content[0].text)
    
    async def _generate_with_openai_compatible(self, prompt: str, provider: LLMProvider, model: str) -> Dict[str, Any]:
        """Generate using OpenAI-compatible API (includes Gemini)"""
        client = self.providers[provider]
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator. Generate structured content exactly as requested."},
                {"role": "user", "content": self._format_structured_prompt(prompt)}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return self._parse_structured_response(response.choices[0].message.content)
    
    async def _generate_with_gemini_native(self, prompt: str) -> Dict[str, Any]:
        """Generate using native Gemini API"""
        genai_client = self.providers[LLMProvider.GEMINI]
        model = genai_client.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content(
            self._format_structured_prompt(prompt),
            generation_config=genai_client.types.GenerationConfig(
                max_output_tokens=2000,
                temperature=0.7
            )
        )
        
        return self._parse_structured_response(response.text)
    
    def _build_card_prompt(self, topic: str, content_type: ContentType, context: str) -> str:
        """Build context-aware prompt for card generation"""
        
        content_type_guidance = {
            ContentType.SPACE: "Focus on historical facts, scientific accuracy, and inspiring human achievement stories.",
            ContentType.WELLNESS: "Emphasize practical advice, scientific backing, and holistic health approaches.",
            ContentType.NUTRITION: "Provide evidence-based information, practical tips, and myth-busting facts.",
            ContentType.EARTH_MYSTERIES: "Balance scientific explanation with fascinating unknowns and ongoing research.",
            ContentType.SOLAR_SYSTEM: "Combine wonder about space with factual astronomical information."
        }
        
        guidance = content_type_guidance.get(content_type, "Provide accurate, engaging educational content.")
        
        return f"""Create educational content about: {topic}
Content Type: {content_type.value}
Context: {context}

Guidelines: {guidance}

Generate content in Portuguese (Brazil) that:
1. Starts with an engaging question that creates curiosity
2. Provides a brief, satisfying answer
3. Includes detailed explanation with interesting facts
4. Uses accessible language for general audiences
5. Maintains scientific accuracy and educational value

The content should be engaging, informative, and inspire further learning."""
    
    def _format_structured_prompt(self, base_prompt: str) -> str:
        """Format prompt to ensure structured output"""
        return f"""{base_prompt}

RESPOND EXACTLY IN THIS FORMAT:
TITLE: [Question format, max 200 chars]
SUMMARY: [Brief answer, 2-3 sentences, max 300 chars]
DETAILED: [Full explanation, 3-4 paragraphs, max 1500 chars]
KEYWORDS: [keyword1, keyword2, keyword3, keyword4, keyword5]
DIFFICULTY: [beginner/intermediate/advanced]

Do not include any other text or formatting."""
    
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response format"""
        import re
        
        patterns = {
            'title': r'TITLE:\s*(.+)',
            'summary': r'SUMMARY:\s*(.+?)(?=DETAILED:|$)',
            'detailed_content': r'DETAILED:\s*(.+?)(?=KEYWORDS:|$)',
            'keywords': r'KEYWORDS:\s*(.+?)(?=DIFFICULTY:|$)',
            'difficulty': r'DIFFICULTY:\s*(.+)'
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field == 'keywords':
                    extracted[field] = [k.strip() for k in value.split(',')]
                elif field == 'difficulty':
                    extracted['difficulty_tags'] = [value.lower()]
                else:
                    extracted[field] = value
            else:
                # Provide defaults for missing fields
                if field == 'title':
                    extracted[field] = "Conteúdo Educativo"
                elif field == 'summary':
                    extracted[field] = "Informação educativa interessante."
                elif field == 'detailed_content':
                    extracted[field] = "Conteúdo detalhado sobre o tópico."
                elif field == 'keywords':
                    extracted[field] = ["educação", "aprendizado"]
                elif field == 'difficulty':
                    extracted['difficulty_tags'] = ["intermediate"]
        
        # Add domain_specific placeholder
        extracted['domain_specific'] = {}
        
        # Length validation
        if len(extracted["title"]) > 200:
            extracted["title"] = extracted["title"][:197] + "..."
        
        if len(extracted["summary"]) > 300:
            extracted["summary"] = extracted["summary"][:297] + "..."
        
        if len(extracted["detailed_content"]) > 1500:
            extracted["detailed_content"] = extracted["detailed_content"][:1497] + "..."
        
        return extracted


class ContentGenerationError(Exception):
    """Custom exception for content generation errors"""
    pass


# Factory function to get the unified generator
def get_unified_generator(anthropic_key: str = None, 
                         gemini_key: str = None, 
                         openai_key: str = None) -> UnifiedContentGenerator:
    """Get unified content generator with available providers"""
    
    # Try to get API keys from environment if not provided
    if not anthropic_key:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not gemini_key:
        gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not openai_key:
        openai_key = os.getenv("OPENAI_API_KEY")
    
    generator = UnifiedContentGenerator(
        anthropic_api_key=anthropic_key,
        gemini_api_key=gemini_key,
        openai_api_key=openai_key
    )
    
    available_providers = generator.get_available_providers()
    if not available_providers:
        raise ContentGenerationError("No LLM providers available. Please provide valid API keys.")
    
    print(f"🚀 Unified generator initialized with providers: {[p.value for p in available_providers]}")
    return generator


if __name__ == "__main__":
    # Test the unified generator
    import os
    
    # Test with available API keys
    generator = get_unified_generator()
    
    print("\n📊 Available Providers:")
    provider_info = generator.get_provider_info()
    for provider, info in provider_info.items():
        print(f"• {provider}: {info['description']} (${info['cost_per_1k']}/1k tokens)")
    
    # Test content generation
    request = ContentGenerationRequest(
        topic="alimentos fermentados",
        content_type=ContentType.NUTRITION,
        provider=LLMProvider.GEMINI_OPENAI  # Use cheapest provider
    )
    
    print(f"\n✨ Default provider: {generator.default_provider.value}")
    print("Ready for content generation!")
