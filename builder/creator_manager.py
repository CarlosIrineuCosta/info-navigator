#!/usr/bin/env python3
"""
Creator Manager - Handle all creator-related operations
Includes validation, creation, deletion, and image management
"""

import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from core_models import Creator, ContentType, generate_creator_id
from json_database import JSONDatabaseManager


class CreatorManager:
    """Manages creator operations with enhanced validation and file handling"""
    
    def __init__(self, db: JSONDatabaseManager):
        self.db = db
        self.images_dir = Path(db.data_dir) / "images"
        self.images_dir.mkdir(exist_ok=True)
    
    def format_category_name(self, category_value: str) -> str:
        """Convert 'health_fitness' -> 'Health and Fitness'"""
        return category_value.replace('_', ' ').title().replace(' And ', ' and ')
    
    def get_formatted_categories(self) -> List[Tuple[str, str]]:
        """Get categories formatted for display, sorted alphabetically"""
        category_choices = [
            "technology_gaming", "health_fitness", "food_cooking", 
            "travel_lifestyle", "education_science", "entertainment_popculture",
            "business_finance", "arts_crafts", "parenting_family", 
            "fashion_beauty", "space_exploration", "wellness", 
            "nutrition", "earth_mysteries", "general"
        ]
        
        formatted_categories = [
            (cat, self.format_category_name(cat)) for cat in category_choices
        ]
        
        # Sort by display name
        return sorted(formatted_categories, key=lambda x: x[1])
    
    def validate_creator_input(self, display_name: str, description: str) -> Optional[str]:
        """Validate basic creator input"""
        if not display_name or not display_name.strip():
            return "Display Name is required"
        if len(display_name.strip()) < 2:
            return "Display Name must be at least 2 characters"
        if len(display_name.strip()) > 100:
            return "Display Name must be less than 100 characters"
        if description and len(description) > 500:
            return "Description must be less than 500 characters"
        return None
    
    def validate_creator_uniqueness(self, display_name: str, social_links: dict) -> Optional[str]:
        """Check for duplicates across all creators"""
        existing_creators = self.db.list_creators()
        
        # Check display name uniqueness
        for creator in existing_creators:
            if creator['display_name'].lower() == display_name.lower():
                return f"Display name '{display_name}' already exists"
        
        # Check social links uniqueness
        for platform, handle in social_links.items():
            if not handle or not handle.strip():
                continue
                
            clean_handle = handle.strip().lower().replace("@", "")
            for creator in existing_creators:
                creator_links = creator.get('social_links', {})
                if platform in creator_links:
                    existing_handle = creator_links[platform].strip().lower().replace("@", "")
                    if existing_handle == clean_handle:
                        return f"{platform.title()} handle '{handle}' already exists (used by {creator['display_name']})"
        
        return None  # All unique
    
    def generate_deterministic_creator_id(self, display_name: str, social_links: dict) -> str:
        """Generate creator_id based on primary identifier + deterministic hash"""
        # Use first available social handle or display name as base
        base_handle = ""
        for platform in ["youtube", "instagram", "tiktok"]:
            if platform in social_links and social_links[platform].strip():
                base_handle = social_links[platform].strip().replace("@", "").lower()
                # Clean for folder naming - alphanumeric only
                base_handle = ''.join(c for c in base_handle if c.isalnum())[:15]
                break
        
        if not base_handle:
            # Use display name if no social handles
            base_handle = ''.join(c for c in display_name.lower() if c.isalnum())[:15]
        
        # Create deterministic hash from all data for uniqueness
        content_hash = hashlib.md5(
            f"{display_name}_{json.dumps(social_links, sort_keys=True)}".encode()
        ).hexdigest()[:8]
        
        return f"{base_handle}_{content_hash}"
    
    def handle_folder_conflict(self, creator_id: str) -> Tuple[bool, str]:
        """Handle folder existence conflicts"""
        creator_folder = self.images_dir / creator_id
        
        if creator_folder.exists():
            # Check if creator exists in database
            existing_creator = self.db.get_creator(creator_id)
            if existing_creator:
                return False, f"CONFLICT: Creator '{existing_creator['display_name']}' already exists with this ID"
            else:
                return False, f"CRITICAL ERROR: Folder '{creator_id}' exists but no creator found in database. This requires manual investigation."
        
        return True, "OK"
    
    def create_creator_folder(self, creator_id: str) -> Tuple[str, str]:
        """Create folder structure for creator content"""
        creator_folder = self.images_dir / creator_id
        
        # Check for conflicts first
        can_create, message = self.handle_folder_conflict(creator_id)
        if not can_create:
            return "", message
        
        try:
            creator_folder.mkdir(parents=True, exist_ok=False)
            return str(creator_folder), "SUCCESS: Folder created"
        except FileExistsError:
            return "", "ERROR: Folder was created by another process"
        except Exception as e:
            return "", f"ERROR: Failed to create folder - {str(e)}"
    
    def validate_and_save_image(self, image_file, creator_folder: Path, image_type: str) -> Tuple[str, str]:
        """Validate and save uploaded image"""
        if not image_file:
            return "", "No image provided"
        
        try:
            # Check file size (2MB = 2,097,152 bytes)
            file_size = Path(image_file.name).stat().st_size if hasattr(image_file, 'name') else len(image_file.read() if hasattr(image_file, 'read') else b'')
            
            if file_size > 2_097_152:
                return "", f"{image_type} must be under 2MB (current: {file_size/1024/1024:.1f}MB)"
            
            # Get file extension
            if hasattr(image_file, 'name'):
                extension = Path(image_file.name).suffix.lower()
            else:
                extension = '.jpg'  # Default
            
            if extension not in ['.jpg', '.jpeg', '.png']:
                return "", f"Invalid file type. Use JPG or PNG only."
            
            # Save with standard naming
            filename = f"{image_type}{extension}"
            file_path = creator_folder / filename
            
            # Save file
            if hasattr(image_file, 'name'):
                shutil.copy2(image_file.name, file_path)
            else:
                with open(file_path, 'wb') as f:
                    f.write(image_file.read())
            
            return str(file_path), "SUCCESS"
            
        except Exception as e:
            return "", f"Error saving {image_type}: {str(e)}"
    
    def create_new_creator(self, display_name: str, description: str,
                          categories: List[str],
                          use_youtube: bool, youtube_handle: str,
                          use_instagram: bool, instagram_handle: str, 
                          use_tiktok: bool, tiktok_handle: str,
                          use_website: bool, website_url: str,
                          creator_image_file, cover_image_file) -> Tuple[str, str]:
        """Create a new content creator with full validation"""
        
        # Step 1: Validate basic input
        error = self.validate_creator_input(display_name, description)
        if error:
            return error, ""
        
        # Step 2: Clean and prepare data
        display_name = display_name.strip()
        description = description.strip() if description else ""
        
        # Build social links dict
        social_links = {}
        if use_youtube and youtube_handle.strip():
            social_links["youtube"] = youtube_handle.strip()
        if use_instagram and instagram_handle.strip():
            social_links["instagram"] = instagram_handle.strip()
        if use_tiktok and tiktok_handle.strip():
            social_links["tiktok"] = tiktok_handle.strip()
        if use_website and website_url.strip():
            social_links["website"] = website_url.strip()
        
        # Step 3: Check uniqueness
        uniqueness_error = self.validate_creator_uniqueness(display_name, social_links)
        if uniqueness_error:
            return uniqueness_error, ""
        
        # Step 4: Generate creator ID
        creator_id = self.generate_deterministic_creator_id(display_name, social_links)
        
        # Step 5: Check for folder conflicts
        can_create_folder, folder_message = self.handle_folder_conflict(creator_id)
        if not can_create_folder:
            return folder_message, ""
        
        try:
            # Step 6: Create folder
            creator_folder_path, folder_status = self.create_creator_folder(creator_id)
            if not creator_folder_path:
                return folder_status, ""
            
            creator_folder = Path(creator_folder_path)
            
            # Step 7: Handle image uploads
            avatar_path = ""
            banner_path = ""
            
            if creator_image_file:
                avatar_path, avatar_status = self.validate_and_save_image(
                    creator_image_file, creator_folder, "avatar"
                )
                if not avatar_path and avatar_status != "No image provided":
                    # Cleanup folder on image error
                    shutil.rmtree(creator_folder, ignore_errors=True)
                    return f"Avatar upload failed: {avatar_status}", ""
            
            if cover_image_file:
                banner_path, banner_status = self.validate_and_save_image(
                    cover_image_file, creator_folder, "banner"
                )
                if not banner_path and banner_status != "No image provided":
                    # Cleanup folder on image error
                    shutil.rmtree(creator_folder, ignore_errors=True)
                    return f"Cover image upload failed: {banner_status}", ""
            
            # Step 8: Convert categories to enums
            category_enums = []
            for cat in categories:
                try:
                    category_enums.append(ContentType(cat))
                except ValueError:
                    pass  # Skip invalid categories
            
            # Step 9: Create creator object
            creator = Creator(
                creator_id=creator_id,
                display_name=display_name,
                platform="multi",  # Multi-platform support
                platform_handle="",  # Not used anymore
                description=description,
                categories=category_enums,
                social_links=social_links,
                avatar_url=avatar_path if avatar_path else None,
                banner_url=banner_path if banner_path else None
            )
            
            # Step 10: Save to database
            if self.db.add_creator(creator):
                creator_json = json.dumps(creator.to_dict(), indent=2, ensure_ascii=False)
                return f"Creator '{display_name}' added successfully", creator_json
            else:
                # Cleanup folder if database save failed
                shutil.rmtree(creator_folder, ignore_errors=True)
                return "Database error: Creator could not be saved", ""
                
        except Exception as e:
            # Cleanup on any error
            creator_folder = self.images_dir / creator_id
            if creator_folder.exists():
                shutil.rmtree(creator_folder, ignore_errors=True)
            return f"Error creating creator: {str(e)}", ""
    
    def list_creators_for_display(self) -> str:
        """List all creators with formatted display"""
        creators = self.db.list_creators()
        if not creators:
            return "No creators found"
        
        creator_list = []
        for creator in creators:
            # Format timestamp for display
            created_time = datetime.fromisoformat(creator['created_at']).strftime("%Y-%m-%d %H:%M")
            creator_list.append(
                f"• {creator['display_name']} (ID: {creator['creator_id']}) - Created: {created_time}"
            )
        
        return "\n".join(creator_list)
    
    def get_creators_for_dropdown(self) -> List[Tuple[str, str]]:
        """Get creators formatted for dropdown (display_name, creator_id)"""
        creators = self.db.list_creators()
        return [(creator['display_name'], creator['creator_id']) for creator in creators]
    
    def delete_creator(self, creator_id: str) -> Tuple[str, bool]:
        """Delete creator and all related data"""
        if not creator_id:
            return "No creator selected for deletion", False
        
        try:
            # Get creator info before deletion
            creator = self.db.get_creator(creator_id)
            if not creator:
                return f"Creator with ID '{creator_id}' not found", False
            
            # Check for related content
            related_sets = self.db.list_content_sets_by_creator(creator_id)
            
            # Remove creator from database
            if not self.db.delete_creator(creator_id):
                return f"Failed to delete creator from database", False
            
            # Remove creator folder
            creator_folder = self.images_dir / creator_id
            if creator_folder.exists():
                shutil.rmtree(creator_folder)
            
            creator_name = creator['display_name']
            return f"Creator '{creator_name}' and {len(related_sets)} related content sets deleted successfully", True
            
        except Exception as e:
            return f"Error deleting creator: {str(e)}", False
