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

# Load environment variables from root folder
load_dotenv("../.env")

# Import our modules
from json_database import JSONDatabaseManager
from creator_manager import CreatorManager
from content_manager import ContentManager


class InfogenApp:
    """Enhanced Gradio app for multi-provider content generation"""
    
    def __init__(self, data_dir: str = "data"):
        self.db = JSONDatabaseManager(data_dir)
        self.creator_manager = CreatorManager(self.db)
        self.content_manager = ContentManager(self.db)
        
        # No migration - use existing database only
    
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
    
    def get_api_status_display(self):
        """Get API status display without exposing keys"""
        try:
            # Check which API keys are configured
            anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
            google_key = os.getenv("GOOGLE_API_KEY", "")
            openai_key = os.getenv("OPENAI_API_KEY", "")
            
            status_lines = []
            
            # Check Google Gemini
            if google_key and google_key != "your-google-gemini-api-key-here" and len(google_key) > 10:
                status_lines.append("✅ **Google Gemini API** - Active")
            else:
                status_lines.append("❌ **Google Gemini API** - Not configured")
            
            # Check Anthropic Claude
            if anthropic_key and anthropic_key != "your-anthropic-api-key-here" and len(anthropic_key) > 10:
                status_lines.append("✅ **Anthropic Claude API** - Active")
            else:
                status_lines.append("❌ **Anthropic Claude API** - Not configured")
            
            # Check OpenAI
            if openai_key and openai_key != "your-openai-api-key-here" and len(openai_key) > 10:
                status_lines.append("✅ **OpenAI API** - Active")
            else:
                status_lines.append("❌ **OpenAI API** - Not configured")
            
            return "\n\n".join(status_lines)
            
        except Exception as e:
            return f"Error checking API status: {str(e)}"
    
    def get_database_status(self):
        """Get database statistics"""
        try:
            creators = len(self.db.list_creators())
            sets = len(self.db._load_collection(self.db.content_sets_file))
            cards = len(self.db._load_collection(self.db.cards_file))
            
            return f"""**Creators:** {creators}
**Content Sets:** {sets}
**Cards:** {cards}

**Data Directory:** `{self.db.data_dir}`

**Status:** {'Ready' if creators > 0 else 'No creators yet'}"""
        except Exception as e:
            return f"Error getting database status: {str(e)}"
    
    def refresh_all_status(self):
        """Refresh both API and database status"""
        return self.get_api_status_display(), self.get_database_status()
    
    def get_creator_choices_for_content(self):
        """Get creator choices for content generation (display names only)"""
        try:
            creators = self.db.list_creators()
            if not creators:
                return ["No Creators in database. Check necessary file."]
            return [creator['display_name'] for creator in creators]
        except Exception as e:
            return [f"Error loading creators: {str(e)}"]
    
    def list_existing_creators(self):
        """List all existing creators from database"""
        try:
            creators = self.db.list_creators()
            if not creators:
                return "No creators found in database. Add some creators first."
            
            creator_info = []
            for creator in creators:
                platforms = []
                if creator.get('social_links'):
                    for platform, handle in creator['social_links'].items():
                        if handle:
                            platforms.append(f"{platform}: {handle}")
                
                platform_str = " | ".join(platforms) if platforms else "No platforms"
                categories_str = ", ".join(creator.get('categories', []))
                
                creator_info.append(f"""
🎯 {creator['display_name']} (ID: {creator['creator_id']})
   📝 {creator.get('description', 'No description')}
   🌐 {platform_str}
   📂 Categories: {categories_str}
   📅 Created: {creator.get('created_at', 'Unknown')}
""")
            
            return "\n".join(creator_info)
        except Exception as e:
            return f"Error loading creators: {str(e)}"
        """List all existing creators from database"""
        try:
            creators = self.db.list_creators()
            if not creators:
                return "No creators found in database. Add some creators first."
            
            creator_info = []
            for creator in creators:
                platforms = []
                if creator.get('social_links'):
                    for platform, handle in creator['social_links'].items():
                        if handle:
                            platforms.append(f"{platform}: {handle}")
                
                platform_str = " | ".join(platforms) if platforms else "No platforms"
                categories_str = ", ".join(creator.get('categories', []))
                
                creator_info.append(f"""
🎯 {creator['display_name']} (ID: {creator['creator_id']})
   📝 {creator.get('description', 'No description')}
   🌐 {platform_str}
   📂 Categories: {categories_str}
   📅 Created: {creator.get('created_at', 'Unknown')}
""")
            
            return "\n".join(creator_info)
        except Exception as e:
            return f"Error loading creators: {str(e)}"
    
    def show_creator_details(self, creator_id: str):
        """Show detailed creator information"""
        if not creator_id:
            return ""
        
        try:
            creator = self.db.get_creator(creator_id)
            if not creator:
                return f"Creator with ID '{creator_id}' not found"
            
            return json.dumps(creator, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error loading creator details: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Create the enhanced Gradio interface"""
        
        # Get formatted categories for dropdown
        formatted_categories = self.creator_manager.get_formatted_categories()
        # Convert from (value, display) to (display, value) for Gradio
        category_choices = [(display, value) for value, display in formatted_categories]
        
        with gr.Blocks(title="Infogen - Content Generator") as interface:
            gr.Markdown("# Infogen - Structured Content Generator")
            gr.Markdown("Generate educational content with structured validation for the card explorer system.")
            
            with gr.Tab("Status"):
                gr.Markdown("## API Status")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Available Providers")
                        api_status_display = gr.Markdown(
                            value=self.get_api_status_display(),
                        )
                    
                    with gr.Column():
                        gr.Markdown("### Database Statistics")
                        db_status_display = gr.Markdown(
                            value=self.get_database_status(),
                        )
                
                refresh_status_btn = gr.Button("Refresh System Status", variant="primary")
                refresh_status_btn.click(
                    fn=self.refresh_all_status,
                    outputs=[api_status_display, db_status_display]
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
                            interactive=True,
                            value=None
                        )
                        
                        with gr.Row():
                            refresh_btn = gr.Button("Refresh List", variant="primary")
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
                
                def refresh_creators():
                    """Refresh the creators dropdown"""
                    return gr.Dropdown(choices=self.creator_manager.get_creators_for_dropdown())
                
                # Wire up creator management
                refresh_btn.click(
                    fn=refresh_creators,
                    outputs=[creators_dropdown]
                )
                
                delete_btn.click(
                    fn=self.delete_selected_creator,
                    inputs=[creators_dropdown],
                    outputs=[gr.Textbox(visible=False), creator_display, creators_dropdown]
                )
                
                # Wire up creator selection to show details
                creators_dropdown.change(
                    fn=self.show_creator_details,
                    inputs=[creators_dropdown],
                    outputs=[creator_display]
                )
                
                # Add a separate tab for listing all creators
                gr.Markdown("### All Creators List")
                list_creators_btn = gr.Button("Show All Creators", variant="primary")
                creators_list = gr.Textbox(
                    label="All Creators",
                    lines=15,
                    interactive=False,
                    value=""
                )
                
                list_creators_btn.click(
                    fn=self.list_existing_creators,
                    outputs=[creators_list]
                )
            
            with gr.Tab("Content Generation"):
                gr.Markdown("## Generate Content Sets")
                gr.Markdown("**Note**: Gemini is ~20x cheaper than Claude for content generation")
                
                with gr.Row():
                    with gr.Column():
                        gen_creator_dropdown = gr.Dropdown(
                            label="Select Creator",
                            choices=self.get_creator_choices_for_content(),
                            interactive=True,
                            value=None
                        )
                        gen_topic = gr.Textbox(
                            label="Topic",
                            placeholder="fermented foods"
                        )
                        gen_content_type = gr.Dropdown(
                            choices=category_choices,
                            label="Content Type", 
                            value="wellness"
                        )
                        gen_card_count = gr.Slider(
                            minimum=3,
                            maximum=20,
                            value=10,
                            step=1,
                            label="Number of Cards"
                        )
                        
                        # Provider selection dropdown
                        provider_dropdown = gr.Dropdown(
                            choices=["gemini_openai", "anthropic", "openai"],
                            label="LLM Provider",
                            value="gemini_openai",
                            info="Gemini recommended for cost efficiency"
                        )
                        
                        generate_preview_btn = gr.Button("Generate Preview", variant="primary")
                        
                        refresh_content_creators_btn = gr.Button("Refresh Creators", variant="secondary")
                    
                    with gr.Column():
                        generation_status = gr.Textbox(label="Generation Status", interactive=False)
                        content_preview = gr.JSON(label="Content Structure Preview")
                
                generate_preview_btn.click(
                    fn=self.content_manager.generate_content_preview,
                    inputs=[gen_creator_dropdown, gen_topic, gen_content_type, gen_card_count, provider_dropdown],
                    outputs=[generation_status, content_preview]
                )
                
                refresh_content_creators_btn.click(
                    fn=lambda: gr.Dropdown(choices=self.get_creator_choices_for_content()),
                    outputs=[gen_creator_dropdown]
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
                
                homepage_btn = gr.Button("Generate Homepage Preview", variant="primary")
                homepage_json = gr.JSON(label="Homepage Structure")
                
                homepage_btn.click(
                    fn=self.content_manager.get_homepage_preview,
                    outputs=[homepage_json]
                )
        
        return interface

    def launch(self, port: int = 5001):
        """Launch the Gradio interface"""
        interface = self.create_interface()
        interface.launch(
            server_name="localhost",
            server_port=port,
            show_api=False,
            share=False
        )


def main():
    """Main entry point"""
    app = InfogenApp()
    app.launch()


if __name__ == "__main__":
    main()
