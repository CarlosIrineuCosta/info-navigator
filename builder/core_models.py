#!/usr/bin/env python3
"""
Core Data Models for Content Management System
Minimal viable structure supporting multiple content types and creators
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import json
import uuid


class ContentType(Enum):
    """Common content categories for creators"""
    TECHNOLOGY_GAMING = "technology_gaming"
    HEALTH_FITNESS = "health_fitness"
    FOOD_COOKING = "food_cooking"
    TRAVEL_LIFESTYLE = "travel_lifestyle"
    EDUCATION_SCIENCE = "education_science"
    ENTERTAINMENT_POPCULTURE = "entertainment_popculture"
    BUSINESS_FINANCE = "business_finance"
    ARTS_CRAFTS = "arts_crafts"
    PARENTING_FAMILY = "parenting_family"
    FASHION_BEAUTY = "fashion_beauty"
    SPACE_EXPLORATION = "space_exploration"
    WELLNESS = "wellness"
    NUTRITION = "nutrition"
    EARTH_MYSTERIES = "earth_mysteries"
    GENERAL = "general"


class NavigationType(Enum):
    """Navigation patterns - extensible for different content types"""
    TIMELINE = "timeline"          # chronological (space missions, historical events)
    THEMATIC = "thematic"          # by categories (wellness topics, nutrition types)
    DIFFICULTY = "difficulty"      # beginner to advanced (learning progression)
    RANDOM = "random"             # always available
    # Future: GEOGRAPHIC, ALPHABETICAL, POPULARITY, etc.


class MediaType(Enum):
    """Media content types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    INTERACTIVE = "interactive"


@dataclass
class Creator:
    """Content creator profile - Netflix-style creator cards"""
    creator_id: str
    display_name: str
    platform: str  # youtube, instagram, tiktok, website
    platform_handle: str
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    description: str = ""
    categories: List[ContentType] = field(default_factory=list)
    follower_count: Optional[int] = None
    verified: bool = False
    
    # Future-ready fields (empty for now)
    social_links: Dict[str, str] = field(default_factory=dict)
    expertise_areas: List[str] = field(default_factory=list)
    content_style: str = "educational"
    
    # System fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON storage"""
        return {
            "creator_id": self.creator_id,
            "display_name": self.display_name,
            "platform": self.platform,
            "platform_handle": self.platform_handle,
            "avatar_url": self.avatar_url,
            "banner_url": self.banner_url,
            "description": self.description,
            "categories": [cat.value for cat in self.categories],
            "follower_count": self.follower_count,
            "verified": self.verified,
            "social_links": self.social_links,
            "expertise_areas": self.expertise_areas,
            "content_style": self.content_style,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class MediaReference:
    """Media content reference with validation fields"""
    media_type: MediaType
    url: str
    alt_text: str = ""
    source: str = ""
    license: str = "unknown"
    
    # Future-ready validation fields
    validation_status: str = "pending"  # pending, verified, failed
    last_checked: Optional[datetime] = None
    backup_url: Optional[str] = None
    
    # Video-specific fields (when applicable)
    start_time: Optional[int] = None
    duration: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "media_type": self.media_type.value,
            "url": self.url,
            "alt_text": self.alt_text,
            "source": self.source,
            "license": self.license,
            "validation_status": self.validation_status,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "backup_url": self.backup_url,
            "start_time": self.start_time,
            "duration": self.duration
        }


@dataclass
class NavigationContext:
    """Flexible navigation context for each card"""
    nav_type: NavigationType
    position: int
    total_items: int
    
    # Context-specific data (flexible for different navigation types)
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nav_type": self.nav_type.value,
            "position": self.position,
            "total_items": self.total_items,
            "context_data": self.context_data
        }


@dataclass
class ContentCard:
    """Individual content card - flexible structure"""
    card_id: str
    set_id: str
    creator_id: str
    
    # Core content (LLM-generated)
    title: str
    summary: str
    detailed_content: str
    
    # Navigation and ordering
    order_index: int
    navigation_contexts: Dict[str, NavigationContext] = field(default_factory=dict)
    
    # Media content
    media: List[MediaReference] = field(default_factory=list)
    
    # Future-ready flexible fields (domain-specific data)
    domain_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # System fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "card_id": self.card_id,
            "set_id": self.set_id,
            "creator_id": self.creator_id,
            "title": self.title,
            "summary": self.summary,
            "detailed_content": self.detailed_content,
            "order_index": self.order_index,
            "navigation_contexts": {
                nav_type: context.to_dict() 
                for nav_type, context in self.navigation_contexts.items()
            },
            "media": [media.to_dict() for media in self.media],
            "domain_data": self.domain_data,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass 
class ContentSet:
    """Collection of cards from a creator - Netflix-style content packages"""
    set_id: str
    creator_id: str
    title: str
    description: str
    category: ContentType
    
    # Display metadata
    thumbnail_url: Optional[str] = None
    banner_url: Optional[str] = None
    
    # Content metadata
    card_count: int = 0
    estimated_time_minutes: int = 30
    difficulty_level: str = "intermediate"  # beginner, intermediate, advanced
    target_audience: str = "general_public"
    
    # Supported navigation types for this set
    supported_navigation: List[NavigationType] = field(default_factory=list)
    
    # Content style and approach
    content_style: str = "question_first"  # question_first, story_driven, quiz, documentary
    
    # Future-ready fields
    tags: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    learning_outcomes: List[str] = field(default_factory=list)
    
    # Analytics (future)
    stats: Dict[str, Any] = field(default_factory=dict)
    
    # System fields
    status: str = "draft"  # draft, review, published, archived
    language: str = "pt-BR"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "set_id": self.set_id,
            "creator_id": self.creator_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "thumbnail_url": self.thumbnail_url,
            "banner_url": self.banner_url,
            "card_count": self.card_count,
            "estimated_time_minutes": self.estimated_time_minutes,
            "difficulty_level": self.difficulty_level,
            "target_audience": self.target_audience,
            "supported_navigation": [nav.value for nav in self.supported_navigation],
            "content_style": self.content_style,
            "tags": self.tags,
            "prerequisites": self.prerequisites,
            "learning_outcomes": self.learning_outcomes,
            "stats": self.stats,
            "status": self.status,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# Utility functions for ID generation
def generate_creator_id(platform_handle: str) -> str:
    """Generate deterministic creator ID"""
    clean_handle = platform_handle.replace("@", "").lower()
    return f"{clean_handle}_{uuid.uuid4().hex[:8]}"


def generate_set_id(creator_id: str, title: str) -> str:
    """Generate deterministic set ID"""
    clean_title = "".join(c for c in title.lower() if c.isalnum() or c in [' ', '-']).replace(' ', '_')
    return f"{creator_id}_{clean_title}_{uuid.uuid4().hex[:8]}"


def generate_card_id(set_id: str, order_index: int) -> str:
    """Generate deterministic card ID"""
    return f"{set_id}_card_{order_index:03d}"


if __name__ == "__main__":
    # Test the data models
    creator = Creator(
        creator_id="canal_astrofisico_abc123",
        display_name="Dr. João Silva - Canal do Astrofísico",
        platform="youtube",
        platform_handle="@canaldoastrofisico",
        description="Física e astronomia descomplicadas",
        categories=[ContentType.SPACE, ContentType.SOLAR_SYSTEM]
    )
    
    print("Creator JSON:")
    print(json.dumps(creator.to_dict(), indent=2, ensure_ascii=False))
