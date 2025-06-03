#!/usr/bin/env python3
"""
JSON Database Manager - Simple file-based storage with structure validation
Uses jsonformer-claude for reliable structured data generation
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from core_models import Creator, ContentSet, ContentCard, ContentType, NavigationType


class JSONDatabaseManager:
    """Simple JSON file-based database for development"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize collection files
        self.creators_file = self.data_dir / "creators.json"
        self.content_sets_file = self.data_dir / "content_sets.json" 
        self.cards_file = self.data_dir / "cards.json"
        
        # Initialize empty collections if files don't exist
        self._init_collections()
    
    def _init_collections(self):
        """Initialize empty JSON collections"""
        for file_path in [self.creators_file, self.content_sets_file, self.cards_file]:
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_collection(self, file_path: Path) -> List[Dict]:
        """Load a JSON collection file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_collection(self, file_path: Path, data: List[Dict]):
        """Save a JSON collection file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Creator operations
    def add_creator(self, creator: Creator) -> bool:
        """Add a new creator"""
        creators = self._load_collection(self.creators_file)
        
        # Check if creator already exists
        if any(c['creator_id'] == creator.creator_id for c in creators):
            return False
        
        creators.append(creator.to_dict())
        self._save_collection(self.creators_file, creators)
        return True
    
    def get_creator(self, creator_id: str) -> Optional[Dict]:
        """Get creator by ID"""
        creators = self._load_collection(self.creators_file)
        for creator in creators:
            if creator['creator_id'] == creator_id:
                return creator
        return None
    
    def list_creators(self) -> List[Dict]:
        """List all creators"""
        return self._load_collection(self.creators_file)
    
    def get_creator_by_display_name(self, display_name: str) -> Optional[Dict]:
        """Get creator by display name"""
        creators = self._load_collection(self.creators_file)
        for creator in creators:
            if creator.get('display_name') == display_name:
                return creator
        return None
    
    def delete_creator(self, creator_id: str) -> bool:
        """Delete a creator by ID"""
        creators = self._load_collection(self.creators_file)
        original_count = len(creators)
        
        # Remove creator with matching ID
        creators = [c for c in creators if c['creator_id'] != creator_id]
        
        if len(creators) < original_count:
            self._save_collection(self.creators_file, creators)
            return True
        return False
    
    # Content Set operations  
    def add_content_set(self, content_set: ContentSet) -> bool:
        """Add a new content set"""
        sets = self._load_collection(self.content_sets_file)
        
        # Check if set already exists
        if any(s['set_id'] == content_set.set_id for s in sets):
            return False
        
        sets.append(content_set.to_dict())
        self._save_collection(self.content_sets_file, sets)
        return True
    
    def get_content_set(self, set_id: str) -> Optional[Dict]:
        """Get content set by ID"""
        sets = self._load_collection(self.content_sets_file)
        for content_set in sets:
            if content_set['set_id'] == set_id:
                return content_set
        return None
    
    def list_content_sets_by_creator(self, creator_id: str) -> List[Dict]:
        """List all content sets by a creator"""
        sets = self._load_collection(self.content_sets_file)
        return [s for s in sets if s['creator_id'] == creator_id]
    
    def list_content_sets_by_category(self, category: ContentType) -> List[Dict]:
        """List all content sets in a category"""
        sets = self._load_collection(self.content_sets_file)
        return [s for s in sets if s['category'] == category.value]
    
    # Card operations
    def add_card(self, card: ContentCard) -> bool:
        """Add a new card"""
        cards = self._load_collection(self.cards_file)
        
        # Check if card already exists
        if any(c['card_id'] == card.card_id for c in cards):
            return False
        
        cards.append(card.to_dict())
        self._save_collection(self.cards_file, cards)
        return True
    
    def add_cards_batch(self, cards: List[ContentCard]) -> int:
        """Add multiple cards in batch"""
        existing_cards = self._load_collection(self.cards_file)
        existing_ids = {c['card_id'] for c in existing_cards}
        
        new_cards_data = []
        for card in cards:
            if card.card_id not in existing_ids:
                new_cards_data.append(card.to_dict())
        
        existing_cards.extend(new_cards_data)
        self._save_collection(self.cards_file, existing_cards)
        return len(new_cards_data)
    
    def get_cards_by_set(self, set_id: str) -> List[Dict]:
        """Get all cards in a content set"""
        cards = self._load_collection(self.cards_file)
        set_cards = [c for c in cards if c['set_id'] == set_id]
        return sorted(set_cards, key=lambda x: x['order_index'])
    
    def get_card(self, card_id: str) -> Optional[Dict]:
        """Get card by ID"""
        cards = self._load_collection(self.cards_file)
        for card in cards:
            if card['card_id'] == card_id:
                return card
        return None
    
    # Homepage data generation (Netflix-style)
    def generate_homepage_data(self) -> Dict[str, Any]:
        """Generate Netflix-style homepage data structure"""
        creators = self.list_creators()
        sets = self._load_collection(self.content_sets_file)
        
        # Group sets by category
        category_groups = {}
        for content_set in sets:
            if content_set['status'] == 'published':
                category = content_set['category']
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(content_set)
        
        # Build homepage structure
        homepage_data = {
            "featured_content": {
                "hero_set": sets[0] if sets else None  # First available set as hero
            },
            "content_rows": []
        }
        
        # Featured creators row
        if creators:
            homepage_data["content_rows"].append({
                "section_title": "Criadores em Destaque",
                "section_type": "creators",
                "items": creators[:6]  # Show top 6 creators
            })
        
        # Category rows
        category_names = {
            "space": "Espaço & Astronomia",
            "wellness": "Bem-estar & Saúde", 
            "nutrition": "Nutrição & Alimentação",
            "earth_mysteries": "Mistérios da Terra",
            "solar_system": "Sistema Solar",
            "general": "Conteúdo Geral"
        }
        
        for category, sets_in_category in category_groups.items():
            if sets_in_category:
                homepage_data["content_rows"].append({
                    "section_title": category_names.get(category, category.title()),
                    "section_type": "category",
                    "category": category,
                    "items": sets_in_category[:8]  # Show up to 8 sets per category
                })
        
        return homepage_data


# Migration function from existing lunar cards JSON
def migrate_existing_lunar_cards(db: JSONDatabaseManager, 
                                existing_json_path: str = "data/lunar_cards_json_10q_v1.json"):
    """Migrate existing lunar cards to new structure"""
    
    # Create default creator for existing content
    default_creator = Creator(
        creator_id="lunar_explorer_original",
        display_name="Lunar Explorer - Conteúdo Original",
        platform="website",
        platform_handle="@lunar_explorer",
        description="Exploração lunar educativa - conteúdo original do sistema",
        categories=[ContentType.SPACE_EXPLORATION]
    )
    
    # Add creator
    db.add_creator(default_creator)
    
    # Load existing cards
    if os.path.exists(existing_json_path):
        with open(existing_json_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Create content set
        lunar_set = ContentSet(
            set_id="lunar_exploration_basics_v1",
            creator_id=default_creator.creator_id,
            title="Exploração Lunar - História Completa",
            description="Jornada completa pela conquista da Lua",
            category=ContentType.SPACE_EXPLORATION,
            card_count=len(existing_data['cards']),
            supported_navigation=[NavigationType.TIMELINE, NavigationType.THEMATIC, NavigationType.RANDOM],
            status="published"
        )
        
        db.add_content_set(lunar_set)
        
        # Convert cards
        migrated_cards = []
        for card_data in existing_data['cards']:
            card = ContentCard(
                card_id=f"lunar_exploration_basics_v1_card_{card_data['id']:03d}",
                set_id=lunar_set.set_id,
                creator_id=default_creator.creator_id,
                title=card_data['titulo'],
                summary=card_data['resumo'],
                detailed_content=card_data['detalhado'],
                order_index=card_data['id']
            )
            
            # Add video if present
            if 'video_url' in card_data:
                from core_models import MediaReference, MediaType
                video_ref = MediaReference(
                    media_type=MediaType.VIDEO,
                    url=card_data['video_url'],
                    alt_text=f"Vídeo sobre {card_data['titulo'][:50]}..."
                )
                card.media.append(video_ref)
            
            migrated_cards.append(card)
        
        # Add all cards
        cards_added = db.add_cards_batch(migrated_cards)
        print(f"Migration completed: {cards_added} cards migrated")
        
        return True
    
    return False


if __name__ == "__main__":
    # Test the database
    db = JSONDatabaseManager()
    
    # Test migration
    migrate_existing_lunar_cards(db)
    
    # Test homepage generation
    homepage = db.generate_homepage_data()
    print("Homepage Structure:")
    print(json.dumps(homepage, indent=2, ensure_ascii=False)[:500] + "...")
