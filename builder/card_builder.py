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
from typing import Optional
import pandas as pd # Import pandas for DataFrame operations

# Load environment variables from root folder
# Assuming card_builder.py is in 'builder' and .env is in 'info-navigator' (parent of builder)
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded .env file from: {dotenv_path}")
else:
    print(f"Warning: .env file not found at {dotenv_path}. API keys should be set in environment.")


# Import our modules
try:
    from json_database import JSONDatabaseManager
    from creator_manager import CreatorManager
    from content_manager import ContentManager
    from core_models import ContentType # For category choices if needed, though manager handles it
    from unified_generator import LLMProvider # For default provider value
except ImportError as e:
    print(f"Critical Error: Failed to import one or more project modules: {e}")
    print("Please ensure all .py files (json_database, creator_manager, content_manager, core_models, unified_generator) are in the 'builder' directory and there are no circular dependencies.")
    # Define dummy classes if imports fail, so Gradio can at least attempt to load the UI structure.
    class JSONDatabaseManager:
        def __init__(self, data_dir="data"): self.data_dir=Path(data_dir); print("Dummy DB used")
        def list_creators(self): return []
        def _load_collection(self, fp): return[]
        def get_creator(self,id): return None
        def generate_homepage_data(self): return {"error":"DB module missing"}
    class CreatorManager:
        def __init__(self,db): print("Dummy CreatorManager used")
        def get_formatted_categories(self): return [("General","general")]
        def create_new_creator(self, *args, **kwargs): return "Error: CreatorManager module missing", "{}"
        def get_creators_for_dropdown(self): return []
        def delete_creator(self,id): return "Error: CreatorManager module missing", False
    class ContentManager:
        def __init__(self,db): print("Dummy ContentManager used")
        def extract_topics_with_ai(self, *args, **kwargs): return "Error: ContentManager module missing", None, gr.update(visible=False), gr.update(visible=False)
        def generate_cards_from_topics(self, *args, **kwargs): return "Error: ContentManager module missing"
        def get_available_providers(self): return ["gemini_openai"]
        def get_generator_status(self): return "Error: ContentManager module missing"
        def get_homepage_preview(self): return "{}"
    class LLMProvider(Enum): GEMINI_OPENAI = "gemini_openai"


class InfogenApp:
    """Enhanced Gradio app for multi-provider content generation"""
    
    def __init__(self, data_dir: str = "data"):
        # Ensure data_dir is relative to the builder script if not absolute
        # If card_builder.py is in 'builder/', then 'data/' is 'builder/data/'
        script_dir = Path(__file__).parent
        self.data_dir_path = script_dir / data_dir
        
        self.db = JSONDatabaseManager(data_dir=str(self.data_dir_path))
        self.creator_manager = CreatorManager(self.db)
        self.content_manager = ContentManager(self.db)
        print(f"InfogenApp initialized. Data directory resolved to: {self.data_dir_path.resolve()}")
    
    def create_new_creator_with_clear(self, display_name: str, description: str,
                                    categories, use_youtube: bool, youtube_handle: str,
                                    use_instagram: bool, instagram_handle: str,
                                    use_tiktok: bool, tiktok_handle: str,
                                    use_website: bool, website_url: str,
                                    creator_image_file, cover_image_file):
        """Create creator and return clear values for form fields"""
        
        status, creator_data_json = self.creator_manager.create_new_creator(
            display_name, description, categories, # categories is already a list of values
            use_youtube, youtube_handle,
            use_instagram, instagram_handle,
            use_tiktok, tiktok_handle,
            use_website, website_url,
            creator_image_file, cover_image_file
        )
        
        # Determine if successful for clearing fields
        is_success = "successfully" in status.lower() if isinstance(status, str) else False
        
        # Prepare outputs for clearing or retaining form data
        form_outputs = [
            status, # This will be the notification
            creator_data_json if creator_data_json else "{}", # Display JSON or empty
            display_name if not is_success else "",
            description if not is_success else "",
            categories if not is_success else [],
            use_youtube if not is_success else False, youtube_handle if not is_success else "",
            use_instagram if not is_success else False, instagram_handle if not is_success else "",
            use_tiktok if not is_success else False, tiktok_handle if not is_success else "",
            use_website if not is_success else False, website_url if not is_success else "",
            None if is_success else creator_image_file, # Clear file inputs with None
            None if is_success else cover_image_file
        ]
        return form_outputs
    
    def delete_selected_creator(self, selected_creator_id: str):
        """Delete selected creator with confirmation"""
        if not selected_creator_id:
            return "No creator selected for deletion.", "{}", [] # Status, JSON display, updated dropdown choices
        
        status_msg, success = self.creator_manager.delete_creator(selected_creator_id)
        
        updated_creators_dropdown_choices = self.creator_manager.get_creators_for_dropdown()
        
        return status_msg, "{}", updated_creators_dropdown_choices # Clear JSON display after deletion
    
    def get_api_status_display(self) -> str:
        """Get API status display (delegated to ContentManager)."""
        try:
            return self.content_manager.get_generator_status()
        except Exception as e:
            return f"Error getting API status: {str(e)}"
    
    def get_database_status(self) -> str:
        """Get database statistics"""
        try:
            creators_count = len(self.db.list_creators())
            # Assuming content_sets_file and cards_file are accessible paths
            sets_count = len(self.db._load_collection(self.db.content_sets_file))
            cards_count = len(self.db._load_collection(self.db.cards_file))
            
            return f"""**Creators:** {creators_count}
**Content Sets:** {sets_count}
**Cards:** {cards_count}

**Data Directory:** `{self.data_dir_path.resolve()}`
**Status:** {'Ready' if creators_count > 0 else 'Database empty or no creators yet.'}"""
        except Exception as e:
            return f"Error getting database status: {str(e)}"
    
    def refresh_all_status(self):
        """Refresh both API and database status"""
        return self.get_api_status_display(), self.get_database_status()
    
    def get_creator_choices_for_content(self) -> list:
        """Get creator choices for content generation (display names only)"""
        try:
            creators = self.db.list_creators()
            if not creators:
                return ["No creators in DB. Add one first."]
            # Assuming creator dicts have 'display_name'
            return [c['display_name'] for c in creators if 'display_name' in c]
        except Exception as e:
            return [f"Error loading creators: {str(e)}"]
    
    def extract_topics_from_content(self, creator_name, guidance, input_method, content_text, content_file, provider_str):
        """Extract topics from user content using AI"""
        try:
            print(f"\n🔍 UI: extract_topics_from_content called")
            print(f"   Creator: {creator_name}, Guidance: '{guidance[:50]}...', Input: {input_method}, Provider: {provider_str}")
            
            content_to_process = ""
            if input_method == "File Upload" and content_file:
                # content_file is a TemporaryFileWrapper or similar from Gradio
                content_to_process = self.read_uploaded_file(content_file)
                print(f"   File content read, length: {len(content_to_process)}")
            elif input_method == "Text Input" and content_text:
                content_to_process = content_text
                print(f"   Using text input, length: {len(content_to_process)}")
            
            if not content_to_process or len(content_to_process.strip()) < 50:
                msg = "❌ Content too short (min 50 chars)."
                print(msg)
                return (msg, "", gr.update(choices=[], value=[]), [], "", gr.update(visible=False), 
                       gr.update(visible=False), gr.update(visible=False))
            
            if not creator_name or creator_name.startswith("No creators") or creator_name.startswith("Error loading"):
                msg = "❌ Please select a valid creator first."
                print(msg)
                return (msg, "", gr.update(choices=[], value=[]), [], "", gr.update(visible=False), 
                       gr.update(visible=False), gr.update(visible=False))
            
            print(f"   Content and creator validated, calling ContentManager for AI extraction...")
            
            topics_list = self.content_manager.extract_topics_with_ai(content_to_process, guidance, creator_name, provider_str)
            
            print(f"   ContentManager returned {len(topics_list)} topics: {topics_list}")
            
            if not topics_list:
                msg = "❌ Failed to extract topics. Check content, API keys, or console logs."
                print(msg)
                return (msg, "", gr.update(choices=[], value=[]), [], "", gr.update(visible=False), 
                       gr.update(visible=False), gr.update(visible=False))
            
            # Format topics for display
            topic_display_html = f"<div style='padding: 10px; background: #f5f5f5; border-radius: 8px;'>"
            topic_display_html += f"<h4>Extracted {len(topics_list)} Topics:</h4><ul>"
            for i, topic in enumerate(topics_list, 1):
                topic_display_html += f"<li><strong>{i}.</strong> {topic}</li>"
            topic_display_html += "</ul></div>"
            
            # Initial selection count
            count_html = f"<p><strong>Selected:</strong> 0 of {len(topics_list)} topics</p>"
            
            return (
                f"✅ Extracted {len(topics_list)} topics. Select the ones you want to generate cards for:",
                topic_display_html,
                gr.update(choices=topics_list, value=[]),  # Update checkboxes with new choices and empty selection
                topics_list,  # store in state for select all functionality
                count_html,
                gr.update(visible=True),  # Show topic_selection_row
                gr.update(visible=True),  # Show validate_topics_btn
                gr.update(visible=False)  # Hide generate_cards_btn until validation
            )
            
        except Exception as e:
            print(f"💥 Exception in UI extract_topics_from_content: {e}")
            traceback.print_exc()
            return (f"❌ Error extracting topics: {str(e)}", "", gr.update(choices=[], value=[]), [], "", 
                   gr.update(visible=False), gr.update(visible=False), gr.update(visible=False))

    def read_uploaded_file(self, temp_file_wrapper) -> str:
        """Reads content from a Gradio temporary file object."""
        if temp_file_wrapper is None: return ""
        try:
            # The 'name' attribute of the TemporaryFileWrapper is the actual path to the temp file
            with open(temp_file_wrapper.name, 'r', encoding='utf-8') as f:
                content = f.read()
            return content.strip()
        except Exception as e:
            print(f"Error reading uploaded file: {e}")
            return f"Error reading file: {e}"
    
    def update_selection_count(self, selected_topics, available_topics):
        """Update the selection counter"""
        selected_count = len(selected_topics) if selected_topics else 0
        total_count = len(available_topics) if available_topics else 0
        return f"<p><strong>Selected:</strong> {selected_count} of {total_count} topics</p>"

    def validate_topic_format(self, selected_topics):
        """Validate selected topics format and constraints."""
        try:
            if not selected_topics:
                return "❌ No topics selected. Please select at least 3 topics."
            
            topics = [topic.strip() for topic in selected_topics if topic.strip()]

            if not topics:
                return "❌ No valid topics found after cleaning. Ensure topics are not empty."

            if len(topics) < 3:
                return f"❌ Minimum 3 topics required. Selected: {len(topics)}"
            if len(topics) > 15:
                return f"❌ Maximum 15 topics allowed. Selected: {len(topics)}"
            
            for i, topic in enumerate(topics, 1):
                if not (5 <= len(topic) <= 60):
                    return f"❌ Topic {i} ('{topic[:60]}...') length invalid (must be 5-60 chars). Length: {len(topic)}"
            
            topic_lower = [t.lower() for t in topics]
            if len(set(topic_lower)) != len(topics):
                return "❌ Duplicate topics found (case-insensitive). Please ensure all topics are unique."
            
            return f"✅ {len(topics)} topics validated successfully. Ready to generate content cards!"
            
        except Exception as e:
            print(f"💥 Exception in validate_topic_format: {e}")
            traceback.print_exc()
            return f"❌ Error validating topics: {str(e)}"
    
    def generate_content_from_topics(self, creator_name, guidance, selected_topics, provider_str):
        """Generate content cards from selected topics."""
        try:
            validation_result = self.validate_topic_format(selected_topics)
            if not validation_result.startswith("✅"):
                return f"Validation Failed: {validation_result}"
            
            topics = [topic.strip() for topic in selected_topics if topic.strip()]
            
            print(f"UI: Generating content for {len(topics)} selected topics. Creator: {creator_name}, Provider: {provider_str}")
            
            # The set_id would typically come from a selected ContentSet in the UI, or be newly created.
            # For this flow, it's simplified.
            success = self.content_manager.generate_cards_from_topics(
                creator_name, 
                guidance, 
                topics, 
                provider_str,
                set_id_placeholder=f"{creator_name.lower().replace(' ','_')}_topic_set"
            )
            
            if success:
                return f"✅ Content generation completed for {len(topics)} selected topics. Check database files!"
            else:
                return f"❌ Content generation failed. Check console logs for details."
            
        except Exception as e:
            print(f"💥 Exception in UI generate_content_from_topics: {e}")
            traceback.print_exc()
            return f"❌ Error generating content: {str(e)}"
            return f"❌ Generation error: {str(e)}"

    def list_existing_creators(self) -> str:
        """List all existing creators from database for display."""
        try:
            creators = self.db.list_creators() # Returns list of dicts
            if not creators:
                return "No creators found in database. Add some creators first."
            
            creator_info_parts = []
            for creator_dict in creators:
                platforms = []
                if isinstance(creator_dict.get('social_links'), dict):
                    for platform, handle in creator_dict['social_links'].items():
                        if handle and str(handle).strip():
                            platforms.append(f"{platform.title()}: {handle}")
                
                platform_str = " | ".join(platforms) if platforms else "No social platforms"
                
                # Categories should be a list of strings from the DB if using Creator.to_dict()
                categories_list = creator_dict.get('categories', [])
                categories_str = ", ".join(categories_list) if categories_list else "No categories"
                
                creator_info_parts.append(f"""
🎯 {creator_dict.get('display_name', 'N/A Name')} (ID: {creator_dict.get('creator_id', 'N/A ID')})
   📝 Desc: {creator_dict.get('description', 'No description')[:100]}...
   🌐 Platforms: {platform_str}
   📂 Categories: {categories_str}
   📅 Created: {creator_dict.get('created_at', 'Unknown')}
""")
            return "\n".join(creator_info_parts)
        except Exception as e:
            print(f"Error formatting creator list: {e}")
            traceback.print_exc()
            return f"Error loading creators for display: {str(e)}"
    
    def show_creator_details(self, selected_creator_id: str) -> str:
        """Show detailed creator information as JSON."""
        if not selected_creator_id:
            return "{}" # Return empty JSON string
        
        try:
            creator_dict = self.db.get_creator(selected_creator_id) # Returns a dict or None
            if not creator_dict:
                return json.dumps({"error": f"Creator with ID '{selected_creator_id}' not found"}, indent=2)
            
            return json.dumps(creator_dict, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error loading creator details for ID {selected_creator_id}: {e}")
            traceback.print_exc()
            return json.dumps({"error": f"Error loading details: {str(e)}"}, indent=2)

    def create_interface(self) -> gr.Blocks:
        """Create the enhanced Gradio interface"""
        
        formatted_category_choices = self.creator_manager.get_formatted_categories()
        
        with gr.Blocks(title="Infogen - Content Generator", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🤖 Infogen - Structured Content Generator")
            gr.Markdown("Create educational content with AI, manage creators, and organize content sets.")
            
            with gr.Tab("📊 Status & Overview"):
                gr.Markdown("## System Status")
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 🧬 LLM Providers")
                        api_status_display = gr.Markdown(value=self.get_api_status_display())
                    with gr.Column(scale=1):
                        gr.Markdown("### 💾 Database")
                        db_status_display = gr.Markdown(value=self.get_database_status())
                refresh_status_btn = gr.Button("🔄 Refresh System Status")
                refresh_status_btn.click(fn=self.refresh_all_status, outputs=[api_status_display, db_status_display])

            with gr.Tab("🧑‍🎨 Creator Management"):
                gr.Markdown("## Content Creator Profiles")
                with gr.Row():
                    with gr.Column(scale=2): # Creator Form
                        gr.Markdown("### Add New Creator Profile")
                        creator_name_inp = gr.Textbox(label="Display Name", placeholder="e.g., 'Canal Ciência Divertida'")
                        creator_desc_inp = gr.Textbox(label="Short Description", placeholder="Focus, style, target audience", lines=2)
                        creator_categories_inp = gr.Dropdown(choices=formatted_category_choices, label="Content Categories", multiselect=True, info="Select primary content areas.")
                        
                        gr.Markdown("#### Social Media Handles (Optional)")
                        with gr.Accordion("Platform Links", open=False):
                            with gr.Row():
                                yt_cb = gr.Checkbox(label="YouTube")
                                yt_handle_inp = gr.Textbox(label="YT Handle", placeholder="@channel", scale=3)
                            with gr.Row():
                                ig_cb = gr.Checkbox(label="Instagram")
                                ig_handle_inp = gr.Textbox(label="IG Handle", placeholder="@username", scale=3)
                            with gr.Row():
                                tk_cb = gr.Checkbox(label="TikTok")
                                tk_handle_inp = gr.Textbox(label="TikTok Handle", placeholder="@username", scale=3)
                            with gr.Row():
                                wb_cb = gr.Checkbox(label="Website")
                                wb_url_inp = gr.Textbox(label="Website URL", placeholder="https://...", scale=3)
                        
                        gr.Markdown("#### Branding Images (Optional)")
                        creator_img_inp = gr.File(label="Creator Avatar (JPG/PNG, max 2MB)", file_types=[".jpg", ".jpeg", ".png"])
                        cover_img_inp = gr.File(label="Profile Banner (JPG/PNG, max 2MB)", file_types=[".jpg", ".jpeg", ".png"])
                        
                        add_creator_btn = gr.Button("➕ Add Creator Profile", variant="primary")
                        creator_form_status_txt = gr.Textbox(label="Form Status", interactive=False, show_label=False, lines=1, placeholder="...")

                    with gr.Column(scale=1): # Existing Creators & Deletion
                        gr.Markdown("### Manage Existing Creators")
                        creators_dd_manage = gr.Dropdown(label="Select Creator", choices=self.creator_manager.get_creators_for_dropdown(), value=None, interactive=True)
                        creator_details_json_manage = gr.JSON(label="Creator Data Preview", scale=2)
                        
                        with gr.Row():
                            refresh_creators_btn_manage = gr.Button("🔄 Refresh List")
                            delete_creator_btn_manage = gr.Button("🗑️ Delete Selected Creator", variant="stop")
                        delete_status_txt = gr.Textbox(label="Deletion Status", show_label=False, interactive=False, placeholder="...")
                        
                        gr.Markdown("--- \n### All Creators Overview")
                        list_all_creators_btn = gr.Button("📋 Show All Creator Summaries")
                        all_creators_display_txt = gr.Textbox(label="All Creator Summaries", lines=10, interactive=False, show_copy_button=True)

                # Creator Form Wiring
                creator_form_inputs = [
                    creator_name_inp, creator_desc_inp, creator_categories_inp,
                    yt_cb, yt_handle_inp, ig_cb, ig_handle_inp, tk_cb, tk_handle_inp, wb_cb, wb_url_inp,
                    creator_img_inp, cover_img_inp
                ]
                creator_form_outputs_for_clear = [ # Order matches inputs for easy clearing
                    creator_name_inp, creator_desc_inp, creator_categories_inp,
                    yt_cb, yt_handle_inp, ig_cb, ig_handle_inp, tk_cb, tk_handle_inp, wb_cb, wb_url_inp,
                    creator_img_inp, cover_img_inp
                ]
                add_creator_btn.click(
                    fn=self.create_new_creator_with_clear,
                    inputs=creator_form_inputs,
                    # Outputs: status_msg, json_preview, then all form fields for clearing
                    outputs=[creator_form_status_txt, creator_details_json_manage] + creator_form_outputs_for_clear
                ).then(
                    fn=lambda: gr.Dropdown(choices=self.creator_manager.get_creators_for_dropdown()), outputs=[creators_dd_manage] # Refresh dropdown
                )

                # Manage Existing Creators Wiring
                creators_dd_manage.change(fn=self.show_creator_details, inputs=[creators_dd_manage], outputs=[creator_details_json_manage])
                refresh_creators_btn_manage.click(fn=lambda: gr.Dropdown(choices=self.creator_manager.get_creators_for_dropdown()), outputs=[creators_dd_manage])
                delete_creator_btn_manage.click(
                    fn=self.delete_selected_creator, 
                    inputs=[creators_dd_manage], 
                    outputs=[delete_status_txt, creator_details_json_manage, creators_dd_manage]
                )
                list_all_creators_btn.click(fn=self.list_existing_creators, outputs=[all_creators_display_txt])
            
            with gr.Tab("📝 Content Generation"):
                gr.Markdown("## AI-Powered Content Card Generation")
                gr.Markdown("Use AI to extract discussion topics from provided content, then generate educational cards.")
                
                with gr.Row():
                    with gr.Column(scale=1): # Setup Column
                        gr.Markdown("### 1. Setup & Content Input")
                        content_gen_creator_dd = gr.Dropdown(label="Select Creator Profile", choices=self.get_creator_choices_for_content(), interactive=True)
                        content_gen_guidance_txt = gr.Textbox(label="Overall Content Guidance / Theme", placeholder="e.g., 'História da exploração lunar para leigos', 'Dicas de bem-estar para mulheres 50+'", lines=2)
                        
                        input_method_radio = gr.Radio(choices=["Text Input", "File Upload"], label="Content Source for Topic Extraction", value="Text Input")
                        content_text_inp = gr.Textbox(label="Paste Content Here (for topic extraction)", lines=8, max_lines=20, visible=True)
                        content_file_inp = gr.File(label="Upload Text File (.txt, .md)", file_types=[".txt", ".md"], visible=False)
                        
                        # Dynamically get provider choices
                        available_llm_providers = self.content_manager.get_available_providers()
                        default_llm_provider = LLMProvider.GEMINI_OPENAI.value # Default
                        if not available_llm_providers: available_llm_providers = [default_llm_provider] # Fallback
                        if default_llm_provider not in available_llm_providers and available_llm_providers: default_llm_provider = available_llm_providers[0]


                        content_gen_provider_dd = gr.Dropdown(choices=available_llm_providers, value=default_llm_provider, label="Select AI Provider", info="Gemini Flash (via OpenAI API) is often cheapest.")
                        
                        extract_topics_btn = gr.Button("🔍 Extract Topics with AI", variant="primary")
                        content_gen_refresh_creators_btn = gr.Button("🔄 Refresh Creator List")


                    with gr.Column(scale=1): # Topics & Generation Column
                        gr.Markdown("### 2. Review & Generate Cards")
                        extraction_status_txt = gr.Textbox(label="Extraction & Validation Status", interactive=False, placeholder="Status updates will appear here...")
                        
                        # Topic Selection UI
                        available_topics_state = gr.State([])  # Store available topics
                        with gr.Row(visible=False) as topic_selection_row:
                            with gr.Column():
                                topic_display = gr.HTML(label="Extracted Topics", value="")
                                with gr.Row():
                                    select_all_btn = gr.Button("Select All", variant="secondary", size="sm")
                                    clear_selection_btn = gr.Button("Clear Selection", variant="secondary", size="sm")
                                topic_checkboxes = gr.CheckboxGroup(
                                    choices=[], label="Select Topics to Generate Cards", 
                                    value=[], interactive=True
                                )
                                selected_count = gr.HTML(value="")
                        
                        validate_topics_btn = gr.Button("✔️ Validate Selected Topics", variant="secondary", visible=False)
                        generate_cards_btn = gr.Button("✨ Generate Content Cards from Topics", variant="primary", visible=False)
                
                # Content Generation UI Logic
                input_method_radio.change(
                    fn=lambda method: (gr.update(visible=method=="Text Input"), gr.update(visible=method=="File Upload")),
                    inputs=[input_method_radio], outputs=[content_text_inp, content_file_inp]
                )
                
                extract_topics_btn.click(
                    fn=self.extract_topics_from_content,
                    inputs=[content_gen_creator_dd, content_gen_guidance_txt, input_method_radio, content_text_inp, content_file_inp, content_gen_provider_dd],
                    outputs=[extraction_status_txt, topic_display, topic_checkboxes, available_topics_state, selected_count, topic_selection_row, validate_topics_btn, generate_cards_btn]
                )
                
                # Topic selection controls  
                select_all_btn.click(
                    fn=lambda available_topics: gr.update(value=available_topics),
                    inputs=[available_topics_state],
                    outputs=[topic_checkboxes]
                ).then(
                    fn=self.update_selection_count,
                    inputs=[topic_checkboxes, available_topics_state],
                    outputs=[selected_count]
                )
                
                clear_selection_btn.click(
                    fn=lambda: gr.update(value=[]),
                    outputs=[topic_checkboxes]
                ).then(
                    fn=self.update_selection_count,
                    inputs=[topic_checkboxes, available_topics_state],
                    outputs=[selected_count]
                )
                
                # Update count when selection changes
                topic_checkboxes.change(
                    fn=self.update_selection_count,
                    inputs=[topic_checkboxes, available_topics_state],
                    outputs=[selected_count]
                )
                
                validate_topics_btn.click(
                    fn=self.validate_topic_format,
                    inputs=[topic_checkboxes],
                    outputs=[extraction_status_txt]
                ).then(
                    fn=lambda status: gr.update(visible=status.startswith("✅")),
                    inputs=[extraction_status_txt],
                    outputs=[generate_cards_btn]
                )
                
                generate_cards_btn.click(
                    fn=self.generate_content_from_topics,
                    inputs=[content_gen_creator_dd, content_gen_guidance_txt, topic_checkboxes, content_gen_provider_dd],
                    outputs=[extraction_status_txt] # Status of generation
                )
                def refresh_content_gen_controls():
                    creator_choices = self.get_creator_choices_for_content()
                    provider_choices = self.content_manager.get_available_providers()
                    default_prov = LLMProvider.GEMINI_OPENAI.value
                    if not provider_choices : provider_choices = [default_prov]
                    if default_prov not in provider_choices and provider_choices: default_prov = provider_choices[0]

                    return gr.update(choices=creator_choices), gr.update(choices=provider_choices, value=default_prov)

                content_gen_refresh_creators_btn.click(
                    fn=refresh_content_gen_controls,
                    outputs=[content_gen_creator_dd, content_gen_provider_dd]
                )

            with gr.Tab("👁️ Homepage Preview"):
                gr.Markdown("## Netflix-Style Homepage Data Structure")
                gr.Markdown("Preview the JSON data structure that would be used to render a dynamic homepage with content rows and categories.")
                
                gen_homepage_preview_btn = gr.Button("🔄 Generate Homepage JSON Preview", variant="primary")
                homepage_json_preview = gr.JSON(label="Homepage Data Structure (Read-only)")
                
                gen_homepage_preview_btn.click(fn=self.content_manager.get_homepage_preview, outputs=[homepage_json_preview])
        
        return interface

    def launch(self, default_port: int = 5001, try_next_port: bool = True):
        """Launch the Gradio interface, trying alternative port if default is busy."""
        interface = self.create_interface()
        current_port = default_port
        
        while True:
            try:
                print(f"Attempting to launch Gradio app on port: {current_port}")
                interface.launch(
                    server_name="0.0.0.0", # Listen on all interfaces for easier access if needed
                    server_port=current_port,
                    show_api=False, # Keep False unless you need API
                    share=False     # Keep False for local development
                )
                break # Launched successfully
            except OSError as e:
                if ("Address is already in use" in str(e) or "Cannot find empty port" in str(e)) and try_next_port:
                    print(f"Warning: Port {current_port} is in use or unavailable.")
                    current_port += 1
                    if current_port > default_port + 10: # Try up to 10 alternative ports
                        print("Error: Could not find an available port after several attempts.")
                        raise
                    print(f"Retrying on port {current_port}...")
                else:
                    print(f"Failed to launch Gradio app: {e}")
                    raise # Re-raise if it's another OSError or if not trying next port
            except Exception as e: # Catch other potential launch errors
                print(f"An unexpected error occurred during Gradio launch: {e}")
                raise


def main():
    """Main entry point for the Gradio application."""
    # Determine the root directory of the project (e.g., 'info-navigator')
    # The script is in 'builder', so parent.parent is 'info-navigator'
    project_root = Path(__file__).resolve().parent.parent
    print(f"Project root (for .env and data): {project_root}")
    
    # Data directory is relative to the 'builder' script location
    # So, 'builder/data'
    app_data_dir = "data" 
    
    app = InfogenApp(data_dir=app_data_dir)
    app.launch(default_port=5003) # Start with a less common port like 5003


if __name__ == "__main__":
    main()