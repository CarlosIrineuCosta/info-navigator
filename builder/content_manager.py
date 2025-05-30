#!/usr/bin/env python3
"""
Content Generator Manager - Handle content generation and preview
"""

import json
import os
from typing import Dict, List, Any, Tuple, Optional

# Try to import unified generator
try:
    from unified_generator import get_unified_generator, ContentGenerationRequest
    UNIFIED_GENERATOR_AVAILABLE = True
except ImportError:
    UNIFIED_GENERATOR_AVAILABLE = False
    print("Warning: unified_generator not available")

from core_models import ContentType
from json_database import JSONDatabaseManager


class ContentManager:
    """Manages content generation and preview operations"""
    
    def __init__(self, db: JSONDatabaseManager):
        self.db = db
        self.content_generator = None
        self._auto_initialize_generator()
    
    def _auto_initialize_generator(self):
        """Auto-initialize content generator on startup"""
        try:
            # Load API keys from environment
            anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
            google_key = os.getenv("GOOGLE_API_KEY", "")
            openai_key = os.getenv("OPENAI_API_KEY", "")
            
            if UNIFIED_GENERATOR_AVAILABLE and any([
                anthropic_key and anthropic_key != "your-anthropic-api-key-here",
                google_key and google_key != "your-google-gemini-api-key-here", 
                openai_key and openai_key != "your-openai-api-key-here"
            ]):
                self.content_generator = get_unified_generator(
                    anthropic_key=anthropic_key if anthropic_key != "your-anthropic-api-key-here" else None,
                    gemini_key=google_key if google_key != "your-google-gemini-api-key-here" else None,
                    openai_key=openai_key if openai_key != "your-openai-api-key-here" else None
                )
                print("Content generator auto-initialized")
        except Exception as e:
            print(f"Auto-initialization failed: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider options for dropdown"""
        if self.content_generator and hasattr(self.content_generator, 'get_available_providers'):
            return [provider.value for provider in self.content_generator.get_available_providers()]
        return ["gemini_openai", "anthropic", "openai"]  # Default options
    
    def get_generator_status(self) -> str:
        """Get current generator status"""
        if self.content_generator:
            providers = self.get_available_providers()
            return f"Ready - {len(providers)} providers available: {', '.join(providers)}"
        else:
            return "Not initialized - check .env file for API keys"
    
    def generate_content_preview(self, creator_id: str, topic: str, 
                               content_type: str, card_count: int, provider_choice: str) -> Tuple[str, str]:
        """Generate a preview of content structure with provider choice"""
        if not self.content_generator:
            return "Content generator not initialized. Please check .env file for API keys.", ""
        
        if not creator_id or not topic:
            return "Creator ID and topic are required", ""
        
        try:
            # Check if creator exists
            creator = self.db.get_creator(creator_id)
            if not creator:
                return f"Creator '{creator_id}' not found", ""
            
            # Create preview structure
            preview_structure = {
                "generation_request": {
                    "creator": creator['display_name'],
                    "topic": topic,
                    "content_type": content_type,
                    "card_count": card_count,
                    "provider": provider_choice
                },
                "sample_output_structure": {
                    "title": f"Interesting question about {topic}?",
                    "summary": f"Educational summary about {topic}.",
                    "detailed_content": f"Detailed explanation about {topic} with interesting information...",
                    "keywords": [topic, "education", "learning"],
                    "difficulty_tags": ["intermediate"],
                    "domain_specific": {
                        "content_category": content_type,
                        "additional_metadata": "Domain-specific fields"
                    }
                }
            }
            
            preview_json = json.dumps(preview_structure, indent=2, ensure_ascii=False)
            return f"Content preview generated with {provider_choice}", preview_json
            
        except Exception as e:
            return f"Error generating preview: {str(e)}", ""
    
    def get_homepage_preview(self) -> str:
        """Generate homepage structure preview"""
        try:
            homepage_data = self.db.generate_homepage_data()
            return json.dumps(homepage_data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error generating homepage: {str(e)}"
