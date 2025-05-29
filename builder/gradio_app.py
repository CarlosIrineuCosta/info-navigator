#!/usr/bin/env python3
"""
Minimal Gradio Interface for Infogen Content Generation
Simple UI for testing and generating structured content
"""

import gradio as gr
import json
import asyncio
from typing import Dict, List, Any, Tuple
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

# Import our modules
from json_database import JSONDatabaseManager, migrate_existing_lunar_cards
from core_models import Creator, ContentSet, ContentCard, ContentType, NavigationType
from core_models import generate_creator_id, generate_set_id, generate_card_id
from multi_provider_generator import get_multi_provider_generator, ContentGenerationRequest


class InfogenApp:
    """Simple Gradio app for content generation and testing"""
    
    def __init__(self, data_dir: str = "data"):
        self.db = JSONDatabaseManager(data_dir)
        self.content_generator = None
        
        # Initialize with existing data if available
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with existing data"""
        try:
            # Try to migrate existing lunar cards
            migrate_existing_lunar_cards(self.db)
            print("✅ Existing lunar cards migrated successfully")
        except Exception as e:
            print(f"ℹ️  No existing data to migrate: {e}")
    
    def setup_content_generator(self, preferred_provider: str = "gemini") -> str:
        """Setup the content generator with preferred provider"""
        try:
            self.content_generator = get_multi_provider_generator(preferred_provider)
            
            available_providers = self.content_generator.get_available_providers()
            costs = self.content_generator.get_provider_costs()
            
            cost_info = []
            for provider in available_providers:
                cost_info.append(f"{provider}: ${costs[provider]:.4f} per card")
            
            return f"✅ Multi-provider generator initialized\nAvailable: {', '.join(available_providers)}\nCosts: {' | '.join(cost_info)}"
            
        except Exception as e:
            return f"❌ Failed to initialize generator: {str(e)}"
    
    def create_new_creator(self, display_name: str, platform: str, 
                          handle: str, description: str, 
                          categories: List[str]) -> Tuple[str, str]:
        """Create a new content creator"""
        if not display_name or not handle:
            return "❌ Name and handle are required", ""
        
        try:
            # Convert category strings to ContentType enums
            category_enums = []
            for cat in categories:
                try:
                    category_enums.append(ContentType(cat))
                except ValueError:
                    pass  # Skip invalid categories
            
            creator = Creator(
                creator_id=generate_creator_id(handle),
                display_name=display_name,
                platform=platform,
                platform_handle=handle,
                description=description,
                categories=category_enums
            )
            
            if self.db.add_creator(creator):
                creator_json = json.dumps(creator.to_dict(), indent=2, ensure_ascii=False)
                return f"✅ Creator '{display_name}' created successfully", creator_json
            else:
                return f"❌ Creator with handle '{handle}' already exists", ""
                
        except Exception as e:
            return f"❌ Error creating creator: {str(e)}", ""
    
    def list_existing_creators(self) -> str:
        """List all existing creators"""
        creators = self.db.list_creators()
        if not creators:
            return "No creators found"
        
        creator_list = []
        for creator in creators:
            creator_list.append(f"• {creator['display_name']} (@{creator['platform_handle']})")
        
        return "\n".join(creator_list)
    
    def generate_content_preview(self, creator_id: str, topic: str, 
                               content_type: str, card_count: int) -> Tuple[str, str]:
        """Generate a preview of content structure"""
        if not self.content_generator:
            return "❌ Content generator not initialized. Please provide API key first.", ""
        
        if not creator_id or not topic:
            return "❌ Creator and topic are required", ""
        
        try:
            # Check if creator exists
            creator = self.db.get_creator(creator_id)
            if not creator:
                return f"❌ Creator '{creator_id}' not found", ""
            
            # Create content generation request
            request = ContentGenerationRequest(
                topic=topic,
                content_type=ContentType(content_type),
                card_count=card_count
            )
            
            # For now, create a mock structure since we can't run async in Gradio easily
            # To use real generation, need to implement async wrapper
            mock_structure = {
                "set_metadata": {
                    "title": f"Explorando {topic.title()}",
                    "description": f"Conteúdo educativo sobre {topic}",
                    "creator": creator['display_name'],
                    "card_count": card_count,
                    "content_type": content_type
                },
                "sample_card": {
                    "title": f"Pergunta interessante sobre {topic}?",
                    "summary": f"Resumo educativo sobre {topic}.",
                    "keywords": ["educação", topic, "aprendizado"],
                    "status": "This is a mock preview - actual generation requires async processing"
                }
            }
            
            preview_json = json.dumps(mock_structure, indent=2, ensure_ascii=False)
            return "✅ Content structure preview generated", preview_json
            
        except Exception as e:
            return f"❌ Error generating preview: {str(e)}", ""
    
    def get_homepage_preview(self) -> str:
        """Generate homepage structure preview"""
        try:
            homepage_data = self.db.generate_homepage_data()
            return json.dumps(homepage_data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error generating homepage: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""
        
        with gr.Blocks(title="Infogen - Content Generator") as interface:
            gr.Markdown("# 🚀 Infogen - Structured Content Generator")
            gr.Markdown("Generate educational content with structured validation for the card explorer system.")
            
            with gr.Tab("Setup"):
                gr.Markdown("## 🔑 API Configuration")
                api_key_input = gr.Textbox(
                    label="Anthropic API Key",
                    type="password",
                    placeholder="sk-ant-..."
                )
                setup_btn = gr.Button("Initialize Content Generator")
                setup_status = gr.Textbox(label="Setup Status", interactive=False)
                
                setup_btn.click(
                    fn=self.setup_content_generator,
                    inputs=[api_key_input],
                    outputs=[setup_status]
                )
            
            with gr.Tab("Creators"):
                gr.Markdown("## 👨‍🏫 Content Creator Management")
                
                with gr.Row():
                    with gr.Column():
                        creator_name = gr.Textbox(label="Display Name", placeholder="Dr. João Silva - Canal do Astrofísico")
                        creator_platform = gr.Dropdown(
                            choices=["youtube", "instagram", "tiktok", "website"],
                            label="Platform",
                            value="youtube"
                        )
                        creator_handle = gr.Textbox(label="Handle", placeholder="@canaldoastrofisico")
                        creator_description = gr.Textbox(
                            label="Description",
                            placeholder="Física e astronomia descomplicadas",
                            lines=2
                        )
                        creator_categories = gr.CheckboxGroup(
                            choices=["space", "wellness", "nutrition", "earth_mysteries", "solar_system"],
                            label="Content Categories"
                        )
                        create_creator_btn = gr.Button("Create Creator")
                    
                    with gr.Column():
                        creator_status = gr.Textbox(label="Creation Status", interactive=False)
                        creator_json = gr.JSON(label="Created Creator Data")
                
                create_creator_btn.click(
                    fn=self.create_new_creator,
                    inputs=[creator_name, creator_platform, creator_handle, 
                           creator_description, creator_categories],
                    outputs=[creator_status, creator_json]
                )
                
                gr.Markdown("### Existing Creators")
                list_creators_btn = gr.Button("List All Creators")
                creators_list = gr.Textbox(label="Creators", lines=5, interactive=False)
                
                list_creators_btn.click(
                    fn=self.list_existing_creators,
                    outputs=[creators_list]
                )
            
            with gr.Tab("Content Generation"):
                gr.Markdown("## 📝 Generate Content Sets")
                
                with gr.Row():
                    with gr.Column():
                        gen_creator_id = gr.Textbox(
                            label="Creator ID",
                            placeholder="lunar_explorer_original"
                        )
                        gen_topic = gr.Textbox(
                            label="Topic",
                            placeholder="alimentos fermentados"
                        )
                        gen_content_type = gr.Dropdown(
                            choices=["space", "wellness", "nutrition", "earth_mysteries", "solar_system"],
                            label="Content Type",
                            value="nutrition"
                        )
                        gen_card_count = gr.Slider(
                            minimum=3,
                            maximum=20,
                            value=10,
                            step=1,
                            label="Number of Cards"
                        )
                        generate_preview_btn = gr.Button("Generate Preview")
                    
                    with gr.Column():
                        generation_status = gr.Textbox(label="Generation Status", interactive=False)
                        content_preview = gr.JSON(label="Content Structure Preview")
                
                generate_preview_btn.click(
                    fn=self.generate_content_preview,
                    inputs=[gen_creator_id, gen_topic, gen_content_type, gen_card_count],
                    outputs=[generation_status, content_preview]
                )
            
            with gr.Tab("Homepage Preview"):
                gr.Markdown("## 🏠 Homepage Structure Preview")
                gr.Markdown("Preview the Netflix-style homepage structure with current data.")
                
                homepage_btn = gr.Button("Generate Homepage Preview")
                homepage_json = gr.JSON(label="Homepage Structure")
                
                homepage_btn.click(
                    fn=self.get_homepage_preview,
                    outputs=[homepage_json]
                )
            
            with gr.Tab("Database Status"):
                gr.Markdown("## 📊 Current Database Status")
                
                def get_db_status():
                    creators = len(self.db.list_creators())
                    sets = len(self.db._load_collection(self.db.content_sets_file))
                    cards = len(self.db._load_collection(self.db.cards_file))
                    
                    return f"""Database Statistics:
• Creators: {creators}
• Content Sets: {sets}  
• Cards: {cards}

Data Directory: {self.db.data_dir}
Files: creators.json, content_sets.json, cards.json"""
                
                status_btn = gr.Button("Check Database Status")
                db_status = gr.Textbox(label="Database Status", lines=8, interactive=False)
                
                status_btn.click(
                    fn=get_db_status,
                    outputs=[db_status]
                )
        
        return interface


def main():
    """Launch the Infogen application"""
    print("🚀 Starting Infogen Content Generator...")
    
    # Load API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print("✅ API key loaded from .env file")
    else:
        print("⚠️  No API key found in .env file")
    
    # Initialize the app
    app = InfogenApp()
    
    # Create and launch interface
    interface = app.create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=5002,
        share=False,
        debug=True
    )


if __name__ == "__main__":
    main()
