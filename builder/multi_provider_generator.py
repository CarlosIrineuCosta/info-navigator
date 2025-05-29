#!/usr/bin/env python3
"""
Multi-Provider LLM Generator
Supports OpenAI-compatible APIs (Claude, Gemini, OpenAI)
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import os

try:
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai library not available. Install with: pip install openai")

from core_models import ContentType, NavigationType


class LLMProvider(Enum):
    """Supported LLM providers"""
    GEMINI = "gemini"
    ANTHROPIC = "anthropic" 
    OPENAI = "openai"


@dataclass
class ProviderConfig:
    """Configuration for each LLM provider"""
    provider: LLMProvider
    api_key: str
    base_url: str
    model_name: str
    input_cost_per_1k: float
    output_cost_per_1k: float


class MultiProviderGenerator:
    """Multi-provider LLM content generator with cost optimization"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup available providers from environment variables"""
        
        # Gemini (OpenAI-compatible, cheapest!)
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            self.providers[LLMProvider.GEMINI] = ProviderConfig(
                provider=LLMProvider.GEMINI,
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                model_name="gemini-1.5-flash",
                input_cost_per_1k=0.0001,
                output_cost_per_1k=0.0007
            )
            self.default_provider = LLMProvider.GEMINI
        
        # Anthropic Claude (via OpenAI-compatible if available)
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            self.providers[LLMProvider.ANTHROPIC] = ProviderConfig(
                provider=LLMProvider.ANTHROPIC,
                api_key=claude_key,
                base_url="https://api.anthropic.com/v1/",  # Note: Not OpenAI compatible
                model_name="claude-3-haiku-20240307",
                input_cost_per_1k=0.00025,
                output_cost_per_1k=0.00125
            )
            if not self.default_provider:
                self.default_provider = LLMProvider.ANTHROPIC
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers[LLMProvider.OPENAI] = ProviderConfig(
                provider=LLMProvider.OPENAI,
                api_key=openai_key,
                base_url="https://api.openai.com/v1/",
                model_name="gpt-4o-mini",
                input_cost_per_1k=0.00015,
                output_cost_per_1k=0.0006
            )
            if not self.default_provider:
                self.default_provider = LLMProvider.OPENAI
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return [provider.value for provider in self.providers.keys()]
    
    def get_cost_estimate(self, provider: LLMProvider, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost estimate for a provider"""
        if provider not in self.providers:
            return float('inf')
        
        config = self.providers[provider]
        input_cost = (input_tokens / 1000) * config.input_cost_per_1k
        output_cost = (output_tokens / 1000) * config.output_cost_per_1k
        return input_cost + output_cost
    
    def get_cheapest_provider(self, input_tokens: int = 800, output_tokens: int = 600) -> Optional[LLMProvider]:
        """Get the cheapest available provider for estimated token usage"""
        if not self.providers:
            return None
        
        costs = {
            provider: self.get_cost_estimate(provider, input_tokens, output_tokens)
            for provider in self.providers.keys()
        }
        
        return min(costs, key=costs.get)
    
    async def generate_content(self, 
                              prompt: str,
                              provider: Optional[LLMProvider] = None,
                              max_tokens: int = 600) -> Dict[str, Any]:
        """Generate content using specified or optimal provider"""
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library required for multi-provider support")
        
        # Use specified provider or find cheapest
        if provider is None:
            provider = self.get_cheapest_provider()
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available. Available: {self.get_available_providers()}")
        
        config = self.providers[provider]
        
        try:
            # For Anthropic, use different approach (not OpenAI compatible yet)
            if provider == LLMProvider.ANTHROPIC:
                return await self._generate_anthropic(prompt, config, max_tokens)
            else:
                # Use OpenAI-compatible interface for Gemini and OpenAI
                return await self._generate_openai_compatible(prompt, config, max_tokens)
                
        except Exception as e:
            # Fallback to next cheapest provider
            available = [p for p in self.providers.keys() if p != provider]
            if available:
                print(f"Provider {provider.value} failed, trying fallback...")
                fallback = min(available, key=lambda p: self.get_cost_estimate(p, 800, 600))
                return await self.generate_content(prompt, fallback, max_tokens)
            else:
                raise e
    
    async def _generate_openai_compatible(self, prompt: str, config: ProviderConfig, max_tokens: int) -> Dict[str, Any]:
        """Generate using OpenAI-compatible interface"""
        
        client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
        try:
            response = await client.chat.completions.create(
                model=config.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful educational content creator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return {
                "content": response.choices[0].message.content,
                "provider": config.provider.value,
                "model": config.model_name,
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_cost": self.get_cost_estimate(
                    config.provider,
                    response.usage.prompt_tokens if response.usage else 0,
                    response.usage.completion_tokens if response.usage else 0
                )
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate with {config.provider.value}: {str(e)}")
    
    async def _generate_anthropic(self, prompt: str, config: ProviderConfig, max_tokens: int) -> Dict[str, Any]:
        """Generate using Anthropic's native API (fallback)"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=config.api_key)
            
            response = await client.messages.create(
                model=config.model_name,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            
            return {
                "content": response.content[0].text,
                "provider": config.provider.value,
                "model": config.model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_cost": self.get_cost_estimate(config.provider, input_tokens, output_tokens)
            }
            
        except ImportError:
            raise ImportError("anthropic library required for Anthropic provider")
        except Exception as e:
            raise Exception(f"Failed to generate with Anthropic: {str(e)}")


class StructuredContentGenerator:
    """Enhanced structured content generator with multi-provider support"""
    
    def __init__(self):
        self.multi_provider = MultiProviderGenerator()
        self.card_schema = self._create_card_schema()
    
    def _create_card_schema(self) -> Dict[str, Any]:
        """JSON schema for content validation"""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Engaging question format, max 200 characters"},
                "summary": {"type": "string", "description": "Brief answer in 2-3 sentences, max 300 characters"},
                "detailed_content": {"type": "string", "description": "Full explanation in 3-4 paragraphs, max 1500 characters"},
                "keywords": {"type": "array", "items": {"type": "string"}, "description": "5-7 relevant keywords"},
                "difficulty_tags": {"type": "array", "items": {"type": "string"}, "description": "Difficulty level tags"}
            },
            "required": ["title", "summary", "detailed_content", "keywords", "difficulty_tags"]
        }
    
    def get_available_providers(self) -> List[str]:
        """Get available providers"""
        return self.multi_provider.get_available_providers()
    
    def get_cost_comparison(self, card_count: int = 10) -> Dict[str, Dict[str, Any]]:
        """Get cost comparison for different providers"""
        input_tokens_per_card = 800
        output_tokens_per_card = 600
        
        comparison = {}
        for provider in self.multi_provider.providers.keys():
            total_cost = self.multi_provider.get_cost_estimate(
                provider,
                input_tokens_per_card * card_count,
                output_tokens_per_card * card_count
            )
            
            config = self.multi_provider.providers[provider]
            comparison[provider.value] = {
                "model": config.model_name,
                "cost_per_card": total_cost / card_count,
                "total_cost": total_cost,
                "input_cost_per_1k": config.input_cost_per_1k,
                "output_cost_per_1k": config.output_cost_per_1k
            }
        
        return comparison
    
    async def generate_content_card(self, 
                                   topic: str,
                                   content_type: ContentType,
                                   provider: Optional[str] = None,
                                   card_context: str = "") -> Dict[str, Any]:
        """Generate a content card with provider selection"""
        
        # Convert string provider to enum
        provider_enum = None
        if provider:
            try:
                provider_enum = LLMProvider(provider)
            except ValueError:
                print(f"Invalid provider {provider}, using default")
        
        # Build structured prompt
        prompt = self._build_structured_prompt(topic, content_type, card_context)
        
        # Generate content
        response = await self.multi_provider.generate_content(
            prompt=prompt,
            provider=provider_enum,
            max_tokens=800
        )
        
        # Parse structured response
        try:
            parsed_content = self._parse_structured_response(response["content"])
            
            # Add generation metadata
            parsed_content["generation_metadata"] = {
                "provider": response["provider"],
                "model": response["model"],
                "input_tokens": response["input_tokens"],
                "output_tokens": response["output_tokens"],
                "cost": response["total_cost"]
            }
            
            return parsed_content
            
        except Exception as e:
            raise ValueError(f"Failed to parse generated content: {str(e)}")
    
    def _build_structured_prompt(self, topic: str, content_type: ContentType, context: str) -> str:
        """Build structured prompt for reliable parsing"""
        
        content_guidance = {
            ContentType.SPACE: "Focus on historical facts, scientific accuracy, and inspiring achievement stories.",
            ContentType.WELLNESS: "Emphasize practical advice, scientific backing, and holistic health approaches.", 
            ContentType.NUTRITION: "Provide evidence-based information, practical tips, and myth-busting facts.",
            ContentType.EARTH_MYSTERIES: "Balance scientific explanation with fascinating unknowns.",
            ContentType.SOLAR_SYSTEM: "Combine wonder about space with factual astronomical information."
        }
        
        guidance = content_guidance.get(content_type, "Provide accurate, engaging educational content.")
        
        return f"""Create educational content about: {topic}
Content Type: {content_type.value}
Context: {context}

Guidelines: {guidance}

Generate content in Portuguese (Brazil) using EXACTLY this format:

TITLE: [Engaging question that creates curiosity, max 200 characters]
SUMMARY: [Brief answer in 2-3 sentences, max 300 characters]
DETAILED: [Full explanation in 3-4 paragraphs, max 1500 characters]
KEYWORDS: [keyword1, keyword2, keyword3, keyword4, keyword5]
DIFFICULTY: [beginner/intermediate/advanced]

Requirements:
1. Start TITLE with an engaging question
2. Make SUMMARY satisfying but brief
3. Include interesting facts in DETAILED
4. Use accessible language for general audiences
5. Maintain scientific accuracy

Do not include any other text or formatting."""
    
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse structured response with robust error handling"""
        import re
        
        patterns = {
            'title': r'TITLE:\s*(.+?)(?=\n|$)',
            'summary': r'SUMMARY:\s*(.+?)(?=DETAILED:|$)',
            'detailed_content': r'DETAILED:\s*(.+?)(?=KEYWORDS:|$)',
            'keywords': r'KEYWORDS:\s*(.+?)(?=DIFFICULTY:|$)',
            'difficulty': r'DIFFICULTY:\s*(.+?)(?=\n|$)'
        }
        
        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                if field == 'keywords':
                    # Parse comma-separated keywords
                    extracted[field] = [k.strip() for k in value.split(',') if k.strip()]
                elif field == 'difficulty':
                    extracted['difficulty_tags'] = [value.lower()]
                else:
                    extracted[field] = value
            else:
                # Provide sensible defaults
                if field == 'title':
                    extracted[field] = f"Conteúdo Educativo sobre {response[:50]}..."
                elif field == 'summary':
                    extracted[field] = "Informação educativa interessante."
                elif field == 'detailed_content':
                    extracted[field] = "Conteúdo detalhado sobre o tópico."
                elif field == 'keywords':
                    extracted[field] = ["educação", "aprendizado"]
                elif field == 'difficulty':
                    extracted['difficulty_tags'] = ["intermediate"]
        
        # Validate lengths
        if len(extracted.get('title', '')) > 200:
            extracted['title'] = extracted['title'][:197] + "..."
        
        if len(extracted.get('summary', '')) > 300:
            extracted['summary'] = extracted['summary'][:297] + "..."
        
        if len(extracted.get('detailed_content', '')) > 1500:
            extracted['detailed_content'] = extracted['detailed_content'][:1497] + "..."
        
        # Add domain-specific data placeholder
        extracted['domain_specific'] = {}
        
        return extracted


# Factory function
def get_multi_provider_generator() -> StructuredContentGenerator:
    """Get the multi-provider content generator"""
    return StructuredContentGenerator()


if __name__ == "__main__":
    # Test the multi-provider system
    import asyncio
    
    async def test_providers():
        generator = get_multi_provider_generator()
        
        print("Available providers:", generator.get_available_providers())
        print("\nCost comparison for 10 cards:")
        
        costs = generator.get_cost_comparison(10)
        for provider, info in costs.items():
            print(f"{provider}: ${info['total_cost']:.4f} total (${info['cost_per_card']:.4f} per card)")
        
        # Test generation if providers are available
        if generator.get_available_providers():
            print("\nTesting content generation...")
            try:
                result = await generator.generate_content_card(
                    topic="alimentos fermentados",
                    content_type=ContentType.NUTRITION
                )
                print(f"Generated with {result['generation_metadata']['provider']}")
                print(f"Cost: ${result['generation_metadata']['cost']:.6f}")
                print(f"Title: {result['title']}")
            except Exception as e:
                print(f"Generation test failed: {e}")
    
    # Run test
    asyncio.run(test_providers())
