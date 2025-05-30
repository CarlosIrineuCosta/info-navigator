#!/usr/bin/env python3
"""
Enhanced Infogen - Multi-Provider Content Generator
Main application with improved UI and modular structure
"""

import gradio as gr
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

# Import our modules
from json_database import JSONDatabaseManager, migrate_existing_lunar_cards
from creator_manager import CreatorManager
from content_manager import ContentManager


class InfogenApp:
    """Enhanced Gradio app for multi-provider content generation"""
    
    def __init__(self, data_dir: str = "data"):
        self.db = JSONDatabaseManager(data_dir)
        self.creator_manager = CreatorManager(self.db)
        self.content_manager = ContentManager(self.db)
        
        # Initialize with existing data if available
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with existing data"""
        try:
            migrate_existing_lunar_cards(self.db)
            print("Existing lunar cards migrated successfully")
        except Exception as e:
            print(f"No existing data to migrate: {e}")
    
    def create_new_creator_with_clear(self, display_name: str, description: str,
                                    categories, use_youtube: bool, youtube_handle: str,
                                    use_instagram: bool, instagram_handle: str,
                                    use_tiktok: bool, tiktok_handle: str,
                                    use_website: bool, website_url: str,
                                    creator_image_file, cover_image_file):
        """Create creator and return clear values for form fields"""
        
        # Create the creator
        status, creator_data = self.creator_manager.create_new_creator(
            display_name, description, categories,
            use_youtube, youtube_handle,
            use_instagram, instagram_handle,
            use_tiktok, tiktok_handle,
            use_website, website_url,
            creator_image_file, cover_image_file
        )
        
        # Return status, data, and empty values for all input fields
        if "successfully" in status:
            # Clear all fields on success
            return [
                status, creator_data,
                "", "", [], False, "", False, "", False, "", False, "", None, None
            ]
        else:
            # Keep fields on error
            return [
                status, creator_data,
                display_name, description, categories,
                use_youtube, youtube_handle,
                use_instagram, instagram_handle,
                use_tiktok, tiktok_handle,
                use_website, website_url,
                creator_image_file, cover_image_file
            ]
    
    def delete_selected_creator(self, selected_creator_id: str):
        """Delete selected creator with confirmation"""
        if not selected_creator_id:
            return "No creator selected for deletion", "", []
        
        status, success = self.creator_manager.delete_creator(selected_creator_id)
        
        # Refresh creator list
        updated_creators = self.creator_manager.get_creators_for_dropdown()
        
        return status, "", updated_creators
    
    def create_interface(self) -> gr.Blocks:
        """Create the enhanced Gradio interface"""
        
        # Get formatted categories for dropdown
        formatted_categories = self.creator_manager.get_formatted_categories()
        category_choices = [(display, value) for value, display in formatted_categories]
        
        with gr.Blocks(title="Infogen - Content Generator") as interface:
            gr.Markdown("# Infogen - Structured Content Generator")
            gr.Markdown("Generate educational content with structured validation for the card explorer system.")
            
            with gr.Tab("Setup"):
                gr.Markdown("## System Status")
                gr.Markdown("Content generator auto-initializes on startup using .env file API keys.")
                
                status_display = gr.Textbox(
                    label="Generator Status",
                    value=self.content_manager.get_generator_status(),
                    interactive=False
                )
            
            with gr.Tab("Creators"):
                gr.Markdown("## Content Creator Management")
                
                with gr.Row():
                    # Left column - Creator form
                    with gr.Column(scale=1):
                        gr.Markdown("### Add New Creator")
                        
                        # Basic Information
                        creator_name = gr.Textbox(
                            label="Display Name", 
                            placeholder="Content Creator Name or Channel Title"
                        )
                        creator_description = gr.Textbox(
                            label="Description",
                            placeholder="Brief description of content focus and style",
                            lines=3
                        )
                        
                        # Categories
                        creator_categories = gr.Dropdown(
                            choices=category_choices,
                            label="Content Categories",
                            multiselect=True,
                            value=[]
                        )
                        
                        # Platform Handles
                        gr.Markdown("### Platform Handles")
                        
                        with gr.Row():
                            use_youtube = gr.Checkbox(label="YouTube", value=False)
                            youtube_handle = gr.Textbox(
                                label="YouTube Handle", 
                                placeholder="@channelname"
                            )
                        
                        with gr.Row():
                            use_instagram = gr.Checkbox(label="Instagram", value=False)
                            instagram_handle = gr.Textbox(
                                label="Instagram Handle",
                                placeholder="@username"
                            )
                        
                        with gr.Row():
                            use_tiktok = gr.Checkbox(label="TikTok", value=False)
                            tiktok_handle = gr.Textbox(
                                label="TikTok Handle",
                                placeholder="@username"
                            )
                        
                        with gr.Row():
                            use_website = gr.Checkbox(label="Website", value=False)
                            website_url = gr.Textbox(
                                label="Website URL",
                                placeholder="https://website.com"
                            )
                        
                        # Image Uploads
                        gr.Markdown("### Images")
                        creator_image = gr.File(
                            label="Creator Image (JPG/PNG, max 2MB)", 
                            file_types=[".jpg", ".jpeg", ".png"],
                            file_count="single"
                        )
                        cover_image = gr.File(
                            label="Cover Image (JPG/PNG, max 2MB)", 
                            file_types=[".jpg", ".jpeg", ".png"],
                            file_count="single"
                        )
                        
                        add_creator_btn = gr.Button("Add Creator", variant="primary")
                    
                    # Right column - Creator management
                    with gr.Column(scale=1):
                        gr.Markdown("### Existing Creators")
                        
                        creators_dropdown = gr.Dropdown(
                            label="Select Creator",
                            choices=self.creator_manager.get_creators_for_dropdown(),
                            interactive=True
                        )
                        
                        with gr.Row():
                            refresh_btn = gr.Button("Refresh List")
                            delete_btn = gr.Button("Delete Selected Creator", variant="secondary")
                        
                        gr.Markdown("⚠️ **Warning**: Deleting a creator will also delete all related content and images")
                        
                        # Large area for creator data display
                        creator_display = gr.Code(
                            label="Creator Data",
                            language="json",
                            lines=20,
                            value=""
                        )
                
                # Wire up the creator form
                all_inputs = [
                    creator_name, creator_description, creator_categories,
                    use_youtube, youtube_handle,
                    use_instagram, instagram_handle,
                    use_tiktok, tiktok_handle,
                    use_website, website_url,
                    creator_image, cover_image
                ]
                
                all_outputs = [
                    gr.Textbox(visible=False),  # Status (will be shown as notification)
                    creator_display
                ] + all_inputs  # All input fields for clearing
                
                add_creator_btn.click(
                    fn=self.create_new_creator_with_clear,
                    inputs=all_inputs,
                    outputs=all_outputs
                )
                
                # Wire up creator management
                refresh_btn.click(
                    fn=lambda: self.creator_manager.get_creators_for_dropdown(),
                    outputs=[creators_dropdown]
                )
                
                delete_btn.click(
                    fn=self.delete_selected_creator,
                    inputs=[creators_dropdown],
                    outputs=[gr.Textbox(visible=False), creator_display, creators_dropdown]
                )
            
            with gr.Tab("Content Generation"):
                gr.Markdown("## Generate Content Sets")
                gr.Markdown("**Note**: Gemini is ~20x cheaper than Claude for content generation")
                
                with gr.Row():
                    with gr.Column():
                        gen_creator_id = gr.Textbox(
                            label="Creator ID",
                            placeholder="creator_id_from_above"
                        )
                        gen_topic = gr.Textbox(
                            label="Topic",
                            placeholder="fermented foods"
                        )
                        gen_content_type = gr.Dropdown(
                            choices=category_choices,
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
                        
                        provider_dropdown = gr.Dropdown(
                            choices=["gemini_openai", "anthropic", "openai"],
                            label="LLM Provider",
                            value="gemini_openai",
                            info="Gemini recommended for cost efficiency"
                        )
                        
                        generate_preview_btn = gr.Button("Generate Preview", variant="primary")
                    
                    with gr.Column():
                        generation_status = gr.Textbox(label="Generation Status", interactive=False)
                        content_preview = gr.JSON(label="Content Structure Preview")
                
                generate_preview_btn.click(
                    fn=self.content_manager.generate_content_preview,
                    inputs=[gen_creator_id, gen_topic, gen_content_type, gen_card_count, provider_dropdown],
                    outputs=[generation_status, content_preview]
                )
                
                gr.Markdown("### Cost Comparison")
                gr.Markdown("""
                | Provider | Cost per 20 Cards | Notes |
                |----------|-------------------|-------|
                | **Gemini 2.0 Flash** | **$0.01** | **Recommended** (Google credits) |
                | GPT-4o mini | $0.01 | Good alternative |
                | Claude 3.5 Haiku | $0.02 | Higher quality, more expensive |
                """)
            
            with gr.Tab("Homepage Preview"):
                gr.Markdown("## Homepage Structure Preview")
                gr.Markdown("Preview the Netflix-style content discovery interface.")
                
                homepage_btn = gr.Button("Generate Homepage Preview")
                homepage_json = gr.JSON(label="Homepage Structure")
                
                homepage_btn.click(
                    fn=self.content_manager.get_homepage_preview,
                    outputs=[homepage_json]
                )
            
            with gr.Tab("Database Status"):
                gr.Markdown("## System Information")
                
                def get_system_status():
                    creators = len(self.db.list_creators())
                    sets = len(self.db._load_collection(self.db.content_sets_file))
                    cards = len(self.db._load_collection(self.db.cards_file))
                    
                    status = f"""**Database Statistics:**
- Creators: {creators}
- Content Sets: {sets}  
- Cards: {cards}

**Data Directory:** {self.db.data_dir}

**Generator Status:** {self.content_manager.get_generator_status()}

**Available Providers:** {len(self.content_manager.get_available_providers())}

**Next Steps:**
1. Add your Google API key to .env file for cost-effective generation
2. Create content creators with multiple platforms
3. Generate content sets with Gemini (~$0.01 per 20 cards)
"""
                    return status
                
                status_btn = gr.Button("Check System Status")
                system_status = gr.Markdown()
                
                status_btn.click(
                    fn=get_system_status,
                    outputs=[system_status]
                )
        
        return interface


def main():
    """Launch the enhanced Infogen application"""
    print("Starting Enhanced Infogen Content Generator...")
    
    # Initialize the app
    app = InfogenApp()
    
    # Create and launch interface
    interface = app.create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=5003,
        share=False,
        debug=True
    )


if __name__ == "__main__":
    main()
