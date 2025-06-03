#!/usr/bin/env python3
"""
Enhanced Gradio Interface for Multi-Provider Content Generation
Simple UI for creating structured content with cost optimization
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
from unified_generator import get_unified_generator, ContentGenerationRequest, LLMProvider


class EnhancedInfogenApp:
    """Enhanced Gradio app for multi-provider content generation"""
    
    def __init__(self, data_dir: str = "data"):
        self.db = JSONDatabaseManager(data_dir)
        self.content_generator = None
        
        # Initialize with existing data if available
        self._initialize_database()
        
        # Try to initialize content generator
        self._setup_content_generator()
    
    def _initialize_database(self):
        """Initialize database with existing data"""
        try:
            # Try to migrate existing lunar cards
            migrate_existing_lunar_cards(self.db)
            print("✅ Existing lunar cards migrated successfully")
        except Exception as e:
            print(f"ℹ️  No existing data to migrate: {e}")
    
    def _setup_content_generator(self):
        """Setup content generator with available providers"""
        try:
            self.content_generator = get_unified_generator()
            return f"✅ Multi-provider system initialized with: {[p.value for p in self.content_generator.get_available_providers()]}"
        except Exception as e:
            return f"⚠️  Content generator not available: {str(e)}"
    
    def get_provider_status(self) -> str:
        """Get current provider status and costs"""
        if not self.content_generator:
            return "❌ No providers available. Please check API keys in .env file."
        
        providers = self.content_generator.get_available_providers()
        provider_info = self.content_generator.get_provider_info()
        
        status = f"✅ Available Providers: {len(providers)}\n\n"
        status += "💰 Cost Comparison (per 1k tokens):\n"
        
        for provider_name, info in provider_info.items():
            status += f"• {provider_name}: ${info['cost_per_1k']} input / ${info['output_cost']} output\n"
            status += f"  {info['description']}\n\n"
        
        status += f"🎯 Current Default: {self.content_generator.default_provider.value}\n"
        status += f"💡 Recommendation: Use Gemini for maximum cost savings!"
        
        return status
    
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
            creator_list.append(f"• {creator['display_name']} (@{creator['platform_handle']}) - ID: {creator['creator_id']}")
        
        return "\n".join(creator_list)
    
    def generate_content_preview(self, creator_id: str, topic: str, 
                               content_type: str, card_count: int,
                               provider_choice: str) -> Tuple[str, str]:
        """Generate a preview of content structure with provider choice"""
        if not self.content_generator:
            return "❌ Content generator not initialized. Please check API keys.", ""
        
        if not creator_id or not topic:
            return "❌ Creator ID and topic are required", ""
        
        try:
            # Check if creator exists
            creator = self.db.get_creator(creator_id)
            if not creator:
                return f"❌ Creator '{creator_id}' not found", ""
            
            # Convert provider choice to enum
            try:
                provider = LLMProvider(provider_choice)
            except ValueError:
                provider = self.content_generator.default_provider
            
            # Calculate estimated cost
            input_tokens = card_count * 800  # ~800 tokens per card input
            output_tokens = card_count * 600  # ~600 tokens per card output
            
            provider_info = self.content_generator.get_provider_info()
            provider_costs = provider_info.get(provider.value, {"cost_per_1k": 0, "output_cost": 0})
            
            estimated_cost = (input_tokens/1000 * provider_costs["cost_per_1k"]) + (output_tokens/1000 * provider_costs["output_cost"])
            
            # Create preview structure
            preview_structure = {
                "generation_request": {
                    "creator": creator['display_name'],
                    "topic": topic,
                    "content_type": content_type,
                    "card_count": card_count,
                    "provider": provider.value,
                    "estimated_cost": f"${estimated_cost:.4f}"
                },
                "sample_output_structure": {
                    "title": f"Pergunta interessante sobre {topic}?",
                    "summary": f"Resumo educativo sobre {topic}.",
                    "detailed_content": f"Explicação detalhada sobre {topic} com informações interessantes...",
                    "keywords": [topic, "educação", "aprendizado"],
                    "difficulty_tags": ["intermediate"],
                    "domain_specific": {
                        "content_category": content_type,
                        "additional_metadata": "Campos específicos do domínio"
                    }
                },
                "cost_comparison": {
                    provider.value: f"${estimated_cost:.4f}",
                    "claude_3_5_sonnet": f"${(input_tokens/1000 * 0.003) + (output_tokens/1000 * 0.015):.4f}",
                    "savings": f"~{((input_tokens/1000 * 0.003) + (output_tokens/1000 * 0.015))/estimated_cost:.1f}x cheaper"
                }
            }
            
            preview_json = json.dumps(preview_structure, indent=2, ensure_ascii=False)
            return f"✅ Content preview generated with {provider.value}", preview_json
            
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
        """Create the enhanced Gradio interface"""
        
        with gr.Blocks(title="Enhanced Infogen - Multi-Provider Content Generator") as interface:
            gr.Markdown("# 🚀 Enhanced Infogen - Multi-Provider Content Generator")
            gr.Markdown("Generate educational content with cost optimization and provider flexibility.")
            
            with gr.Tab("System Status"):
                gr.Markdown("## 🔍 Multi-Provider System Status")
                
                status_btn = gr.Button("Check Provider Status")
                provider_status = gr.Textbox(
                    label="Provider Status & Costs", 
                    lines=15, 
                    interactive=False,
                    value=self.get_provider_status()
                )
                
                status_btn.click(
                    fn=self.get_provider_status,
                    outputs=[provider_status]
                )
                
                gr.Markdown("### 💡 Cost Savings with Gemini")
                gr.Markdown("""
                **Google Gemini 2.0 Flash** is ~20x cheaper than Claude and produces excellent results:
                - 20 cards with Claude: ~$0.23
                - 20 cards with Gemini: ~$0.01 
                - **Your Google Credits make it essentially FREE!**
                """)
            
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
                gr.Markdown("## 📝 Generate Content Sets with Provider Choice")
                
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
                            maximum=50,
                            value=20,
                            step=1,
                            label="Number of Cards"
                        )
                        provider_choice = gr.Dropdown(
                            choices=["gemini_openai", "openai", "gemini", "anthropic"],
                            label="Provider Choice",
                            value="gemini_openai",
                            info="Gemini is recommended for cost savings"
                        )
                        generate_preview_btn = gr.Button("Generate Preview & Cost Estimate")
                    
                    with gr.Column():
                        generation_status = gr.Textbox(label="Generation Status", interactive=False)
                        content_preview = gr.JSON(label="Content Structure Preview")
                
                generate_preview_btn.click(
                    fn=self.generate_content_preview,
                    inputs=[gen_creator_id, gen_topic, gen_content_type, gen_card_count, provider_choice],
                    outputs=[generation_status, content_preview]
                )
                
                gr.Markdown("### 💰 Cost Optimization Tips")
                gr.Markdown("""
                - **Gemini 2.0 Flash**: Best value - excellent quality at lowest cost
                - **GPT-4o mini**: Balanced option with good performance  
                - **Claude**: Highest quality but most expensive
                - **Your Google Credits**: Make Gemini essentially free!
                """)
            
            with gr.Tab("Homepage Preview"):
                gr.Markdown("## 🏠 Netflix-Style Homepage Structure")
                
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
Files: creators.json, content_sets.json, cards.json

Multi-Provider System:
• Providers Available: {len(self.content_generator.get_available_providers()) if self.content_generator else 0}
• Default Provider: {self.content_generator.default_provider.value if self.content_generator else 'None'}
• Cost Optimization: Ready for high-volume generation"""
                
                status_btn = gr.Button("Check Database Status")
                db_status = gr.Textbox(label="Database Status", lines=12, interactive=False)
                
                status_btn.click(
                    fn=get_db_status,
                    outputs=[db_status]
                )
        
        return interface


def main():
    """Launch the enhanced Infogen application"""
    print("🚀 Starting Enhanced Multi-Provider Content Generator...")
    
    # Initialize the app
    app = EnhancedInfogenApp()
    
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
