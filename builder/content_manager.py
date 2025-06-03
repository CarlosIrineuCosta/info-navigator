#!/usr/bin/env python3
"""
Content Manager - Handle content generation flow, topic extraction, and card creation.
"""

import json
import os
import asyncio
import traceback
import re # Ensure re is imported
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum # Ensure Enum is imported for the fallback LLMProvider
from datetime import datetime

# Assuming unified_generator.py and core_models.py are in the same directory or Python path
try:
    from unified_generator import get_unified_generator, LLMProvider, ContentGenerationError
    UNIFIED_GENERATOR_AVAILABLE = True
except ImportError:
    UNIFIED_GENERATOR_AVAILABLE = False
    print("Critical Warning: unified_generator.py not found or has issues. Content generation will likely fail.")
    # Define fallback LLMProvider if unified_generator is missing, to allow parsing
    class LLMProvider(Enum):
        GEMINI_OPENAI = "gemini_openai"
        ANTHROPIC = "anthropic"
        OPENAI = "openai"
    class ContentGenerationError(Exception): pass


try:
    from core_models import ContentType # Assuming ContentType enum from core_models.py
except ImportError:
    print("Critical Warning: core_models.py not found. Using dummy ContentType.")
    class ContentType(Enum): # Dummy for parsing if core_models is missing
        GENERAL = "general"
        SPACE_EXPLORATION = "space_exploration"
        WELLNESS = "wellness"
        NUTRITION = "nutrition"
        EARTH_MYSTERIES = "earth_mysteries"
        TECHNOLOGY_GAMING = "technology_gaming"
        # Add others from your actual core_models.py as needed for determine_creator_style

try:
    from json_database import JSONDatabaseManager # For DB interactions
except ImportError:
    print("Critical Warning: json_database.py not found. Database interactions will fail.")
    # Dummy DB Manager if not found
    class JSONDatabaseManager:
        def __init__(self, data_dir: str = "data"): print("Dummy JSONDatabaseManager initialized.")
        def list_creators(self): return []
        def get_creator(self, creator_id): return None
        def add_card(self, card): print(f"Dummy DB: Add card {card}"); return True
        def generate_homepage_data(self): return {"dummy_homepage": True}


class ContentManager:
    """Manages content generation flow including topic extraction and card creation."""
    
    def __init__(self, db: JSONDatabaseManager):
        self.db = db
        self.content_generator = None
        self._auto_initialize_generator()
    
    def _auto_initialize_generator(self):
        """Initializes the UnifiedContentGenerator."""
        if not UNIFIED_GENERATOR_AVAILABLE:
            print("Content generator cannot be initialized: unified_generator module is missing.")
            return
        try:
            # get_unified_generator handles API key loading from env vars
            self.content_generator = get_unified_generator()
            if self.content_generator and self.content_generator.get_available_providers():
                print("✅ ContentManager: UnifiedContentGenerator initialized successfully.")
            else:
                print("⚠️ ContentManager: UnifiedContentGenerator initialized, but no providers are configured/available.")
        except ContentGenerationError as e: # Catch specific error from get_unified_generator
            print(f"❌ ContentManager: Failed to initialize UnifiedContentGenerator: {e}")
            self.content_generator = None # Ensure it's None on failure
        except Exception as e:
            print(f"❌ ContentManager: Unexpected error during UnifiedContentGenerator initialization: {e}")
            traceback.print_exc()
            self.content_generator = None

    def _ensure_generator(self):
        """Ensures the content generator is initialized, attempting re-initialization if necessary."""
        if not self.content_generator or not self.content_generator.get_available_providers():
            print("Attempting to re-initialize content generator...")
            self._auto_initialize_generator()
        if not self.content_generator or not self.content_generator.get_available_providers():
            raise ContentGenerationError("Content generator is not available or not properly initialized. Check API keys and console logs.")

    def extract_topics_with_ai(self, content: str, guidance: str, creator_name: str, provider_str: str) -> List[str]:
        """Extracts topics from content using the AI generator."""
        try:
            self._ensure_generator() # Ensure generator is ready
            
            sanitized_content = self.sanitize_content(content)
            print(f"\n🔍 DEBUG: Topic Extraction (ContentManager)")
            print(f"   Creator: {creator_name}, Provider Str: {provider_str}")
            print(f"   Original content length: {len(content)}, Sanitized: {len(sanitized_content)}")
            
            # Refined prompt for better topic extraction
            prompt = f"""Você é um assistente de IA especializado em análise de texto para extrair tópicos educacionais.
Analise o seguinte conteúdo fornecido e extraia de 5 a 10 tópicos específicos, concisos e acionáveis para a criação de cartões de conteúdo educacional.

---
Conteúdo para Análise:
{sanitized_content}
---

Informações Adicionais para guiar a extração:
- Nome do Criador: {creator_name}
- Orientação Geral de Conteúdo: {guidance}

Requisitos Estritos para a Lista de Tópicos:
1.  Cada tópico deve ser uma frase curta ou um termo específico (5-50 caracteres).
2.  Os tópicos devem estar em Português (Brasil).
3.  A lista deve conter entre 5 e 10 tópicos únicos.
4.  Formato da Resposta: APENAS a lista de tópicos, um tópico por linha. NÃO inclua números, marcadores, saudações ou qualquer outro texto.

Exemplo de formato de saída esperado:
Benefícios da água alcalina
Como calcular sua hidratação diária
Mitos sobre a desidratação
Impacto da água na performance física
Qualidade da água potável no Brasil
"""
            # print(f"   Topic Extraction Prompt (first 300 chars): {prompt[:300]}...") # For debug

            try:
                provider_enum = LLMProvider(provider_str)
            except ValueError:
                print(f"Warning: Invalid provider string '{provider_str}' for topic extraction. Using default.")
                provider_enum = self.content_generator.default_provider
                if not provider_enum: # Should not happen if _ensure_generator worked
                    raise ContentGenerationError("No default provider available after invalid choice.")
            
            print(f"   Calling LLM ({provider_enum.value}) for topic extraction...")
            
            raw_llm_response = asyncio.run(
                self.content_generator.generate_generic_text(
                    prompt_text=prompt,
                    system_prompt="Você é um especialista em extrair tópicos chave de um texto.",
                    provider=provider_enum,
                    max_tokens=200, # Usually enough for a list of 10 short topics
                    temperature=0.3 # Lower for more deterministic extraction
                )
            )
            # print(f"   Raw LLM response for topics: '{raw_llm_response}'") # For debug
            
            topics = self.parse_topics_from_response(raw_llm_response)
            print(f"✅ Extracted {len(topics)} topics by ContentManager: {topics}")
            return topics
            
        except ContentGenerationError as e: # Catch specific errors from generator
            print(f"❌ Topic extraction failed (ContentGenerationError): {e}")
            # traceback.print_exc() # Already printed in generator usually
            return []
        except Exception as e:
            print(f"❌ Unexpected error during topic extraction: {e}")
            traceback.print_exc()
            return []

    def sanitize_content(self, content: str) -> str:
        """Basic sanitization and length limiting for content passed to LLM for topic extraction."""
        if not isinstance(content, str): return ""
        
        # Limit length to prevent excessive token usage for topic extraction
        max_chars_for_topic_extraction = 15000 # Roughly 3k-5k tokens
        if len(content) > max_chars_for_topic_extraction:
            print(f"Warning: Input content for topic extraction truncated from {len(content)} to {max_chars_for_topic_extraction} chars.")
            content = content[:max_chars_for_topic_extraction]
        
        # Remove typical non-textual or problematic characters. Keep basic punctuation.
        sanitized = re.sub(r'[^\w\s\.,;:!?\-áàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ]', ' ', content, flags=re.UNICODE)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip() # Normalize whitespace
        return sanitized

    def parse_topics_from_response(self, response_text: str) -> List[str]:
        """Robustly parses a list of topics, one per line, from AI response."""
        if not response_text or not isinstance(response_text, str): return []
        
        topics = []
        lines = response_text.split('\n')
        for line in lines:
            clean_line = line.strip()
            # Remove common prefixes/markers if AI doesn't follow instructions perfectly
            clean_line = re.sub(r'^\s*[\d\W]*\s*', '', clean_line) # Removes leading numbers, bullets, spaces
            
            if 5 <= len(clean_line) <= 60: # Adjusted max length slightly for flexibility
                if clean_line not in topics: # Avoid duplicates
                    topics.append(clean_line)
            elif clean_line: # Log if a non-empty line was skipped
                print(f"Info: Topic candidate skipped (length/format): '{clean_line}'")

        return topics[:15] # Return max 15 topics

    def generate_cards_from_topics(self, creator_name: str, guidance: str, topics: List[str], provider_str: str, set_id_placeholder: str = "default_set_id") -> bool:
        """Generates content cards for given topics and saves them (conceptual)."""
        try:
            self._ensure_generator() # Ensure generator is ready

            creator_data = self.db.get_creator_by_display_name(creator_name) # Assumes this method exists or you adapt it
            if not creator_data:
                # Fallback or direct use if get_creator_by_display_name is not available
                creators = self.db.list_creators()
                creator_data = next((c for c in creators if c.get('display_name') == creator_name), None)
                if not creator_data:
                    print(f"❌ Creator '{creator_name}' not found in DB.")
                    return False

            print(f"\n🔄 Starting card generation for {len(topics)} topics, Creator: {creator_name}, Provider: {provider_str}")
            
            try:
                provider_enum = LLMProvider(provider_str)
            except ValueError:
                print(f"Warning: Invalid provider string '{provider_str}' for card generation. Using default.")
                provider_enum = self.content_generator.default_provider
                if not provider_enum: raise ContentGenerationError("No default provider for card gen.")

            # Determine content type for cards - this might need more sophisticated logic
            # For now, using a general content type or one derived from guidance.
            # This should ideally come from user input in Gradio for the set.
            main_category_str = creator_data.get('categories', ["general"])[0] # Take first category or general
            try:
                content_type_for_cards = ContentType(main_category_str)
            except ValueError:
                print(f"Warning: Category '{main_category_str}' not a valid ContentType. Defaulting to GENERAL.")
                content_type_for_cards = ContentType.GENERAL

            # Create ContentSet if it doesn't exist
            from core_models import ContentSet, NavigationType
            import uuid
            
            # Generate unique set ID based on creator and timestamp
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M")
            actual_set_id = f"{creator_data['creator_id']}_{content_type_for_cards.value}_{timestamp_str}"
            
            # Check if set already exists
            existing_set = self.db.get_content_set(actual_set_id)
            if not existing_set:
                # Create new ContentSet
                content_set = ContentSet(
                    set_id=actual_set_id,
                    creator_id=creator_data['creator_id'],
                    title=f"Conteúdo sobre {guidance[:50]}..." if guidance else f"Tópicos de {creator_name}",
                    description=f"Conjunto de cartões educativos gerados para {creator_name}. Orientação: {guidance}",
                    category=content_type_for_cards,
                    card_count=len(topics),
                    supported_navigation=[NavigationType.THEMATIC, NavigationType.RANDOM],
                    status="published"
                )
                
                # Save ContentSet to database
                set_created = self.db.add_content_set(content_set)
                if set_created:
                    print(f"✅ Created new ContentSet: {actual_set_id}")
                else:
                    print(f"⚠️ ContentSet creation failed, using placeholder: {actual_set_id}")
            else:
                print(f"📁 Using existing ContentSet: {actual_set_id}")
            
            # Use the actual set ID instead of placeholder
            set_id_placeholder = actual_set_id

            generated_card_count = 0
            for i, topic_text in enumerate(topics, 1):
                print(f"   Generating card {i}/{len(topics)} for topic: '{topic_text}'...")
                card_context = f"Card {i} of {len(topics)} for a set by {creator_name}. Overall guidance: {guidance}"
                
                try:
                    card_data_dict = asyncio.run(
                        self.content_generator.generate_content_card(
                            topic=topic_text,
                            content_type=content_type_for_cards,
                            card_context=card_context,
                            provider=provider_enum
                        )
                    )
                    
                    # Convert card_data_dict to ContentCard and save to database
                    from core_models import ContentCard
                    import uuid
                    
                    # Generate unique card ID
                    card_id = f"{set_id_placeholder}_card_{uuid.uuid4().hex[:8]}"
                    
                    # Create ContentCard instance
                    new_card = ContentCard(
                        card_id=card_id,
                        set_id=set_id_placeholder,
                        creator_id=creator_data['creator_id'],
                        title=card_data_dict.get('title', f"Card {i}: {topic_text}"),
                        summary=card_data_dict.get('summary', "Generated content summary"),
                        detailed_content=card_data_dict.get('detailed_content', "Generated detailed content"),
                        order_index=i,
                        tags=card_data_dict.get('keywords', []),
                        domain_data={
                            'difficulty': card_data_dict.get('difficulty', 'intermediate'),
                            'topic': topic_text,
                            'guidance': guidance
                        }
                    )
                    
                    # Save card to database
                    success = self.db.add_card(new_card)
                    if success:
                        print(f"   ✅ Card for '{topic_text}' saved to database: {new_card.title[:40]}...")
                        generated_card_count += 1
                    else:
                        print(f"   ⚠️ Card for '{topic_text}' generated but failed to save to database")
                except Exception as card_e:
                    print(f"   ❌ Failed to generate/process card for topic '{topic_text}': {card_e}")
                    # Optionally continue to next topic or re-raise

            print(f"✅ Successfully generated {generated_card_count} cards (conceptually).")
            return True

        except ContentGenerationError as e:
            print(f"❌ Card generation process failed (ContentGenerationError): {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during card generation process: {e}")
            traceback.print_exc()
            return False
            
    def determine_creator_style(self, categories: List[str]) -> str:
        """Determines a general content style hint based on creator categories."""
        if not categories or not isinstance(categories, list): return 'default'
        # Ensure comparison is with enum values if categories are stored as enum values,
        # or with strings if categories are strings. core_models.Creator stores them as ContentType enums.
        # The `creator_data` from `json_database` will have them as strings.
        
        category_values = categories # Assuming they are already string values from DB
        
        if any(cat_val in [ContentType.WELLNESS.value, ContentType.HEALTH_FITNESS.value, ContentType.NUTRITION.value] for cat_val in category_values):
            return 'wellness'
        elif any(cat_val in [ContentType.SPACE_EXPLORATION.value, ContentType.EDUCATION_SCIENCE.value, ContentType.TECHNOLOGY_GAMING.value] for cat_val in category_values):
            return 'scientific'
        else:
            return 'default'

    def get_available_providers(self) -> List[str]:
        """Gets list of available provider string names for UI dropdowns."""
        if self.content_generator and hasattr(self.content_generator, 'get_available_providers'):
            provider_enums = self.content_generator.get_available_providers()
            return [p.value for p in provider_enums]
        # Fallback if generator had issues during init
        return [p.value for p in LLMProvider] # Returns all defined, UI must handle if not truly available

    def get_generator_status(self) -> str:
        """Gets a display string for the generator's status."""
        if self.content_generator:
            providers = self.get_available_providers()
            if providers:
                return f"Ready. Available: {', '.join(providers)}. Default: {self.content_generator.default_provider.value if self.content_generator.default_provider else 'None'}"
            else:
                return "Initialized, but NO providers are configured/available. Check API keys."
        return "Not initialized. Check .env file for API keys & console logs for errors."

    def get_homepage_preview(self) -> str:
        """Generates a JSON string preview of the homepage data structure."""
        try:
            homepage_data = self.db.generate_homepage_data() # Assumes this method exists and is robust
            return json.dumps(homepage_data, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error generating homepage preview: {e}")
            return json.dumps({"error": f"Failed to generate homepage preview: {str(e)}"}, indent=2)

if __name__ == '__main__':
    # Basic test for ContentManager (requires .env and other modules)
    async def test_content_manager():
        print("Testing ContentManager...")
        # Ensure .env is loaded if running this directly and .env is in parent
        from pathlib import Path
        dotenv_path = Path(__file__).resolve().parent.parent / ".env"
        if dotenv_path.exists():
            from dotenv import load_dotenv
            print(f"Loading .env file from: {dotenv_path}")
            load_dotenv(dotenv_path=dotenv_path)
        else:
            print(f".env file not found at {dotenv_path}. API keys must be in environment.")

        # Dummy DB for testing if json_database is complex to init standalone
        class DummyDB:
            def list_creators(self): return [{"display_name": "Test Creator", "creator_id": "test001", "categories": ["general"]}]
            def get_creator_by_display_name(self, name): 
                if name == "Test Creator": return {"display_name": "Test Creator", "creator_id": "test001", "categories": ["general"]}
                return None
            def add_card(self, card): print(f"DummyDB: Would add card: {card.title if hasattr(card,'title') else 'Unknown title'}")
            def generate_homepage_data(self): return {"title": "Dummy Homepage"}

        # db_manager = JSONDatabaseManager(data_dir="temp_test_data") # Or use DummyDB for isolated test
        db_manager = DummyDB()
        content_manager = ContentManager(db_manager)
        
        print(f"Generator Status: {content_manager.get_generator_status()}")

        if not content_manager.content_generator or not content_manager.content_generator.get_available_providers():
            print("Cannot run tests as no content generator provider is available.")
            return

        print("\nTesting Topic Extraction...")
        sample_text = "A água é essencial para a vida. Ela regula a temperatura corporal, transporta nutrientes e oxigênio para as células, e ajuda na eliminação de resíduos. Beber água suficiente melhora a função cerebral e os níveis de energia. A desidratação pode levar a problemas de saúde."
        topics = content_manager.extract_topics_with_ai(
            content=sample_text,
            guidance="Foco em saúde e bem-estar.",
            creator_name="Test Creator",
            provider_str=content_manager.content_generator.default_provider.value # Use default
        )
        print(f"Extracted topics: {topics}")

        if topics:
            print("\nTesting Card Generation from extracted topics...")
            success = content_manager.generate_cards_from_topics(
                creator_name="Test Creator",
                guidance="Foco em saúde e bem-estar, cards educativos.",
                topics=topics,
                provider_str=content_manager.content_generator.default_provider.value,
                set_id_placeholder="test_set_health_01"
            )
            print(f"Card generation success status: {success}")

    if __name__ == '__main__':
        asyncio.run(test_content_manager())