#!/usr/bin/env python3
"""
Multi-Provider Content Generator
Supports Claude (Anthropic), Gemini (Google via OpenAI-compatible API), 
and other LLM providers with a unified interface.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import os
import traceback

# Provider imports with fallbacks
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic library not found. Run 'pip install anthropic'.")

try:
    from openai import OpenAI, AsyncOpenAI # AsyncOpenAI for potential future use
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai library not found. Run 'pip install openai'.")

# Native Google GenAI is now a secondary/removed option for simplification
# try:
#     import google.generativeai as genai
#     GOOGLE_GENAI_NATIVE_AVAILABLE = True
# except ImportError:
#     GOOGLE_GENAI_NATIVE_AVAILABLE = False
#     print("Warning: google-generativeai library not found for native access.")


# Assuming core_models.py is in the same directory or Python path
try:
    from core_models import ContentType, NavigationType
except ImportError:
    print("Error: core_models.py not found. Please ensure it's in the Python path.")
    # Define dummy enums if core_models is not found, to allow this file to be parsed
    class ContentType(Enum):
        GENERAL = "general"
    class NavigationType(Enum):
        THEMATIC = "thematic"


class LLMProvider(Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    GEMINI_OPENAI = "gemini_openai"  # Gemini via OpenAI-compatible API (Primary Gemini access)
    OPENAI = "openai"
    # GEMINI = "gemini" # Native Gemini - removing as primary to simplify to one Gemini method


@dataclass
class ContentGenerationRequest:
    """Request structure for content generation (can be expanded)"""
    topic: str
    content_type: ContentType
    card_count: int = 10
    difficulty_level: str = "intermediate"
    content_style: str = "question_first"
    target_audience: str = "general_public"
    language: str = "pt-BR"
    # Provider is handled by the generator instance or method call
    # provider: LLMProvider = LLMProvider.GEMINI_OPENAI


class ContentGenerationError(Exception):
    """Custom exception for content generation errors"""
    pass


class UnifiedContentGenerator:
    """Unified content generator supporting multiple LLM providers."""
    
    def __init__(self, 
                 anthropic_api_key: Optional[str] = None,
                 gemini_openai_api_key: Optional[str] = None, # For Google's OpenAI-compatible endpoint
                 openai_api_key: Optional[str] = None):
        
        self.providers: Dict[LLMProvider, Any] = {}
        self.provider_configs: Dict[LLMProvider, Dict[str, Any]] = {}
        self.default_provider: Optional[LLMProvider] = None
        
        # Initialize available providers
        self._setup_anthropic(anthropic_api_key)
        self._setup_gemini_openai(gemini_openai_api_key) # Primary Gemini access
        self._setup_openai(openai_api_key)
        # self._setup_gemini_native(gemini_openai_api_key) # Keeping this out for now for "one way"

        # Determine default provider based on availability and preference
        preferred_order = [LLMProvider.GEMINI_OPENAI, LLMProvider.ANTHROPIC, LLMProvider.OPENAI]
        for provider_enum in preferred_order:
            if provider_enum in self.providers:
                self.default_provider = provider_enum
                break
        
        if not self.default_provider and self.providers: # Fallback if preferred not found but others exist
            self.default_provider = list(self.providers.keys())[0]

        if self.default_provider:
            print(f"✅ Default LLM provider set to: {self.default_provider.value}")
        else:
            print("⚠️ No LLM providers initialized successfully. Content generation will fail.")
            
        self.card_schema = self._create_card_schema()

    def _setup_anthropic(self, api_key: Optional[str]):
        if ANTHROPIC_AVAILABLE and api_key and api_key != "your-anthropic-api-key-here":
            try:
                # Using AsyncAnthropic for consistency with OpenAI's async client
                # For synchronous calls, one would typically wrap async calls or use anthropic.Anthropic()
                self.providers[LLMProvider.ANTHROPIC] = anthropic.AsyncAnthropic(api_key=api_key)
                self.provider_configs[LLMProvider.ANTHROPIC] = {"model": "claude-3-haiku-20240307"}
                print("✅ Anthropic Claude provider initialized (claude-3-haiku).")
            except Exception as e:
                print(f"❌ Anthropic setup failed: {e}")
                traceback.print_exc()

    def _setup_gemini_openai(self, api_key: Optional[str]):
        """Setup Gemini via OpenAI-compatible API."""
        if OPENAI_AVAILABLE and api_key and api_key != "your-google-gemini-api-key-here": # Check against placeholder
            try:
                self.providers[LLMProvider.GEMINI_OPENAI] = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://generativelanguage.googleapis.com/v1beta" # Corrected base URL structure
                )
                # Model will be specified per call, e.g., "models/gemini-1.5-flash-latest"
                self.provider_configs[LLMProvider.GEMINI_OPENAI] = {"model_prefix": "models/"} # Store prefix
                print("✅ Gemini (OpenAI-compatible API) provider initialized.")
            except Exception as e:
                print(f"❌ Gemini (OpenAI-compatible API) setup failed: {e}")
                traceback.print_exc()
    
    def _setup_openai(self, api_key: Optional[str]):
        if OPENAI_AVAILABLE and api_key and api_key != "your-openai-api-key-here":
            try:
                self.providers[LLMProvider.OPENAI] = AsyncOpenAI(api_key=api_key)
                self.provider_configs[LLMProvider.OPENAI] = {"model": "gpt-3.5-turbo"} # Or "gpt-4o-mini"
                print("✅ OpenAI provider initialized (gpt-3.5-turbo).")
            except Exception as e:
                print(f"❌ OpenAI setup failed: {e}")
                traceback.print_exc()

    def _create_card_schema(self) -> Dict[str, Any]:
        """JSON schema for individual content cards - simplified for clarity."""
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Engaging question, max 200 chars"},
                "summary": {"type": "string", "description": "Brief answer, 2-3 sentences, max 300 chars"},
                "detailed_content": {"type": "string", "description": "Full explanation, 3-4 paragraphs, max 1500 chars"},
                "keywords": {"type": "array", "items": {"type": "string"}, "description": "5-7 relevant keywords"},
                "difficulty_tags": {
                    "type": "array", 
                    "items": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]}
                }
            },
            "required": ["title", "summary", "detailed_content", "keywords", "difficulty_tags"]
        }

    def get_available_providers(self) -> List[LLMProvider]:
        return list(self.providers.keys())

    async def _call_anthropic_api(self, client: anthropic.AsyncAnthropic, model: str, system_prompt: Optional[str], user_prompt: str, max_tokens: int, temperature: float) -> str:
        messages = [{"role": "user", "content": user_prompt}]
        # Anthropic's new messages API takes an optional system prompt
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt if system_prompt else None,
            messages=messages
        )
        return response.content[0].text

    async def _call_openai_compatible_api(self, client: AsyncOpenAI, model: str, system_prompt: Optional[str], user_prompt: str, max_tokens: int, temperature: float) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            # response_format={"type": "json_object"} # if LLM supports and strict JSON needed
        )
        return response.choices[0].message.content

    async def generate_generic_text(self, 
                                    prompt_text: str,
                                    system_prompt: Optional[str] = "You are a helpful assistant.",
                                    provider: Optional[LLMProvider] = None,
                                    max_tokens: int = 500,
                                    temperature: float = 0.5) -> str:
        """Generate generic text using specified or default provider."""
        
        current_provider = provider if provider is not None else self.default_provider
        
        if not current_provider or current_provider not in self.providers:
            available = self.get_available_providers()
            if not available:
                raise ContentGenerationError("No LLM providers available or initialized.")
            # Fallback to the first available provider if current_provider is invalid
            current_provider = available[0]
            print(f"Warning: Provider '{provider.value if provider else 'default'}' not found or invalid. Falling back to '{current_provider.value}'.")

        client_instance = self.providers[current_provider]
        provider_config = self.provider_configs[current_provider]

        try:
            if current_provider == LLMProvider.ANTHROPIC:
                model_to_use = provider_config.get("model", "claude-3-haiku-20240307")
                return await self._call_anthropic_api(client_instance, model_to_use, system_prompt, prompt_text, max_tokens, temperature)
            
            elif current_provider == LLMProvider.GEMINI_OPENAI:
                # For Gemini via OpenAI API, model name needs prefix, e.g., "models/gemini-1.5-flash-latest"
                model_prefix = provider_config.get("model_prefix", "models/")
                model_to_use = f"{model_prefix}gemini-1.5-flash-latest" # Specify a default model
                return await self._call_openai_compatible_api(client_instance, model_to_use, system_prompt, prompt_text, max_tokens, temperature)

            elif current_provider == LLMProvider.OPENAI:
                model_to_use = provider_config.get("model", "gpt-3.5-turbo")
                return await self._call_openai_compatible_api(client_instance, model_to_use, system_prompt, prompt_text, max_tokens, temperature)
            
            else:
                # This case should ideally not be reached if current_provider is validated from self.providers
                raise ContentGenerationError(f"Provider {current_provider.value} not implemented for generic text generation.")
                
        except Exception as e:
            error_message = f"Generic text generation failed with {current_provider.value}: {str(e)}"
            print(f"Error details: {traceback.format_exc()}")
            # Consider logging the prompt for debugging (be careful with sensitive data)
            # print(f"Failed prompt for {current_provider.value}: {prompt_text[:200]}...") 
            raise ContentGenerationError(error_message)

    def _parse_structured_response(self, response_text: str) -> Dict[str, Any]:
        """Parses a structured response text (TITLE, SUMMARY, etc.) into a dictionary."""
        import re
        parsed_data = {}
        # Expected keys roughly based on _format_structured_prompt in earlier versions
        # This regex approach is fragile; true JSON output from LLM is better.
        patterns = {
            'title': r'TITLE:\s*(.+)',
            'summary': r'SUMMARY:\s*(.+)',
            'detailed_content': r'DETAILED:\s*(.+)',
            'keywords': r'KEYWORDS:\s*(.+)',
            'difficulty_tags': r'DIFFICULTY:\s*(.+)' # Matches the whole line for difficulty
        }

        # Try to parse TITLE (often on its own line)
        title_match = re.search(r'^TITLE:\s*(.+?)(?=\nSUMMARY:|\nDETAILED:|\nKEYWORDS:|\nDIFFICULTY:|$)', response_text, re.MULTILINE | re.IGNORECASE)
        if title_match:
            parsed_data['title'] = title_match.group(1).strip()

        summary_match = re.search(r'^SUMMARY:\s*(.+?)(?=\nDETAILED:|\nKEYWORDS:|\nDIFFICULTY:|$)', response_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if summary_match:
            parsed_data['summary'] = summary_match.group(1).strip()

        detailed_match = re.search(r'^DETAILED:\s*(.+?)(?=\nKEYWORDS:|\nDIFFICULTY:|$)', response_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if detailed_match:
            parsed_data['detailed_content'] = detailed_match.group(1).strip()
        
        keywords_match = re.search(r'^KEYWORDS:\s*(.+?)(?=\nDIFFICULTY:|$)', response_text, re.MULTILINE | re.IGNORECASE)
        if keywords_match:
            parsed_data['keywords'] = [k.strip() for k in keywords_match.group(1).split(',') if k.strip()]
        
        difficulty_match = re.search(r'^DIFFICULTY:\s*(.+?)(?=\n|$)', response_text, re.MULTILINE | re.IGNORECASE)
        if difficulty_match:
            parsed_data['difficulty_tags'] = [d.strip().lower() for d in difficulty_match.group(1).split(',') if d.strip()]


        # Apply schema defaults or validation if needed
        schema = self.card_schema
        for key, prop_details in schema["properties"].items():
            if key not in parsed_data:
                if prop_details.get("type") == "array":
                    parsed_data[key] = []
                elif prop_details.get("type") == "string":
                    parsed_data[key] = f"Default {key} - parsing failed or not provided"
                else:
                    parsed_data[key] = None # Or some other default
        
        if not parsed_data.get('title'): # Fallback if regex fails badly
             parsed_data['title'] = "Content Title (Parsing Issue)"
        if not parsed_data.get('summary'):
             parsed_data['summary'] = "Content Summary (Parsing Issue)"
        if not parsed_data.get('detailed_content'):
             parsed_data['detailed_content'] = "Detailed Content (Parsing Issue)"
        if not parsed_data.get('keywords'):
             parsed_data['keywords'] = ["keyword_parse_issue"]
        if not parsed_data.get('difficulty_tags'):
             parsed_data['difficulty_tags'] = ["intermediate_parse_issue"]

        return parsed_data

    async def generate_content_card(self, 
                                   topic: str, 
                                   content_type: ContentType, # Assuming ContentType enum from core_models
                                   card_context: str = "",   # Additional context for this specific card
                                   provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """
        Generates a single content card with structured output.
        It now relies on the LLM to follow structured prompt instructions.
        """
        
        # 1. Build the Prompt for structured output
        system_prompt_for_card = "You are an expert educational content creator. Generate structured content exactly as requested in the user prompt, following the specified format strictly."
        
        # Guidance based on content type
        content_type_guidance = {
            ContentType.SPACE_EXPLORATION: "Focus on historical facts, scientific accuracy, and inspiring human achievement stories.",
            # Add other ContentType enum members from core_models.py
            ContentType.WELLNESS: "Emphasize practical advice, scientific backing, and holistic health approaches.",
            ContentType.NUTRITION: "Provide evidence-based information, practical tips, and myth-busting facts.",
            ContentType.EARTH_MYSTERIES: "Balance scientific explanation with fascinating unknowns and ongoing research.",
            ContentType.GENERAL: "Provide accurate, engaging educational content.",
            # ... add all your ContentType enum cases from core_models.py
        }
        # Default guidance if content_type is not in the map or is a generic type
        guidance = content_type_guidance.get(content_type, "Provide accurate, engaging educational content. Ensure all requested fields are present in the output.")


        user_prompt_for_card = f"""
Context for this card: {card_context}
Topic to address: {topic}
Content Type: {content_type.value if hasattr(content_type, 'value') else str(content_type)}
Specific Guidelines for this content: {guidance}

Please generate content in Portuguese (Brazil).

Your response MUST strictly follow this format, with each field on a new line:
TITLE: [An engaging title, often in a question format, related to the topic. Max 200 characters.]
SUMMARY: [A brief answer or overview of the topic. 2-3 sentences, max 300 characters.]
DETAILED: [A more comprehensive explanation. 3-4 paragraphs, max 1500 characters. Include interesting facts and use accessible language.]
KEYWORDS: [Provide 5 to 7 relevant keywords, comma-separated. Example: keyword1, keyword2, keyword3]
DIFFICULTY: [Choose one: beginner, intermediate, or advanced. Example: intermediate]

Ensure every field (TITLE, SUMMARY, DETAILED, KEYWORDS, DIFFICULTY) is present. Do not add any extra text, greetings, or explanations outside this structure.
"""
        # 2. Call the generic text generation method
        raw_llm_response = await self.generate_generic_text(
            prompt_text=user_prompt_for_card,
            system_prompt=system_prompt_for_card,
            provider=provider,
            max_tokens=2000, # Increased for potentially longer detailed content
            temperature=0.6 # Slightly lower for more factual card content
        )

        # 3. Parse the (hopefully) structured response
        # This parsing needs to be robust.
        parsed_card_data = self._parse_structured_response(raw_llm_response)
        
        # Add some metadata from the generation process
        parsed_card_data['generation_metadata'] = {
            'provider_used': (provider or self.default_provider).value if (provider or self.default_provider) else "unknown",
            'topic_requested': topic,
            'content_type_requested': content_type.value if hasattr(content_type, 'value') else str(content_type)
        }
        
        return parsed_card_data


def get_unified_generator(anthropic_key: Optional[str] = None, 
                         gemini_openai_key: Optional[str] = None, # Renamed for clarity
                         openai_key: Optional[str] = None) -> UnifiedContentGenerator:
    """Factory function to get unified content generator with available providers."""
    
    # Try to get API keys from environment if not provided
    # Check against common placeholder values
    def get_key(env_var_names: List[str], provided_key: Optional[str]) -> Optional[str]:
        if provided_key and provided_key.strip() and not provided_key.startswith("your-") and not provided_key.endswith("-here"):
            return provided_key
        for var_name in env_var_names:
            env_key = os.getenv(var_name)
            if env_key and env_key.strip() and not env_key.startswith("your-") and not env_key.endswith("-here"):
                return env_key
        return None

    anthropic_k = get_key(["ANTHROPIC_API_KEY"], anthropic_key)
    gemini_k = get_key(["GOOGLE_API_KEY", "GEMINI_API_KEY"], gemini_openai_key) # For OpenAI-compatible
    openai_k = get_key(["OPENAI_API_KEY"], openai_key)
    
    generator = UnifiedContentGenerator(
        anthropic_api_key=anthropic_k,
        gemini_openai_api_key=gemini_k,
        openai_api_key=openai_k
    )
    
    available_providers = generator.get_available_providers()
    if not available_providers:
        print("⚠️ Unified generator initialized, but NO LLM providers are available/configured. Content generation will fail.")
        print("Please check your .env file for ANTHROPIC_API_KEY, GOOGLE_API_KEY/GEMINI_API_KEY, and/or OPENAI_API_KEY.")
    else:
        print(f"🚀 Unified generator initialized. Available providers: {[p.value for p in available_providers]}")
    
    return generator


if __name__ == "__main__":
    # This basic test needs to be run in an async context
    async def main_test():
        print("Testing UnifiedContentGenerator...")
        
        # The factory function will try to load keys from .env
        # Ensure your .env file is in the parent directory or accessible.
        # Example: Create a .env file in the project root (e.g., one level above builder)
        # GOOGLE_API_KEY=your_actual_gemini_api_key
        
        # Correct relative path if this script is in 'builder' and .env is in project root
        dotenv_path = Path(__file__).resolve().parent.parent / ".env"
        if dotenv_path.exists():
            from dotenv import load_dotenv
            print(f"Loading .env file from: {dotenv_path}")
            load_dotenv(dotenv_path=dotenv_path)
        else:
            print(f".env file not found at {dotenv_path}. API keys must be in environment or passed directly.")

        try:
            generator = get_unified_generator()
            
            if not generator.get_available_providers():
                print("No providers available for testing. Exiting.")
                return

            print(f"\nDefault provider for tests: {generator.default_provider.value if generator.default_provider else 'None'}")

            # Test generic text generation (e.g., for topic extraction)
            print("\nTesting generic text generation (e.g., for topic extraction)...")
            generic_prompt = "List 3 benefits of using Python for web development."
            try:
                generic_response = await generator.generate_generic_text(
                    prompt_text=generic_prompt,
                    # provider=LLMProvider.GEMINI_OPENAI # Explicitly test one if needed
                )
                print(f"Generic Prompt: {generic_prompt}")
                print(f"Generic Response:\n{generic_response}")
            except ContentGenerationError as e:
                print(f"Generic text generation test failed: {e}")
            except Exception as e:
                print(f"An unexpected error occurred during generic text test: {e}")
                traceback.print_exc()

            # Test content card generation
            print("\nTesting content card generation...")
            try:
                # Assuming ContentType.GENERAL is defined in your core_models or the dummy above
                # Find an available ContentType from your actual core_models.py
                test_content_type = ContentType.GENERAL # Replace with a valid one from your core_models
                try:
                    from core_models import ContentType as CoreContentType
                    # Pick a specific one that you know exists in your core_models.py
                    if hasattr(CoreContentType, 'TECHNOLOGY_GAMING'):
                         test_content_type = CoreContentType.TECHNOLOGY_GAMING
                    elif hasattr(CoreContentType, 'SPACE_EXPLORATION'):
                         test_content_type = CoreContentType.SPACE_EXPLORATION
                    else: # fallback to the one defined in this file if core_models is partial
                         test_content_type = ContentType.GENERAL
                except:
                    pass


                card_data = await generator.generate_content_card(
                    topic="A Importância da Água",
                    content_type=test_content_type,
                    card_context="Este é um cartão educacional para o público em geral."
                )
                print("Generated Card Data:")
                print(json.dumps(card_data, indent=2, ensure_ascii=False))
            except ContentGenerationError as e:
                print(f"Content card generation test failed: {e}")
            except Exception as e:
                print(f"An unexpected error occurred during card generation test: {e}")
                traceback.print_exc()

        except ContentGenerationError as e:
            print(f"Failed to initialize generator for testing: {e}")
        except Exception as e:
            print(f"A critical error occurred during __main__ test setup: {e}")
            traceback.print_exc()

    if __name__ == "__main__":
        # If running Python 3.7+, asyncio.run can be used directly
        # For older versions, you might need loop.run_until_complete(main_test())
        # Ensure your environment supports asyncio.run
        from pathlib import Path # Ensure Path is imported for dotenv logic
        asyncio.run(main_test())