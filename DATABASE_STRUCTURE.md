# Database Structure Documentation

## Overview
The Info Navigator PWA uses JSON files to store educational content organized in a three-tier structure: Creators → Content Sets → Cards.

## File Structure
```
public/data/
├── creators.json     # Creator profiles and metadata
├── content_sets.json # Content collections (like YouTube playlists)
└── cards.json        # Individual educational cards
```

## Image Organization
```
public/images/
└── sets/
    ├── s001/           # Set folder (using set_number)
    │   ├── banner.jpg    # Hero banner for set
    │   ├── thumbnail.jpg # Grid thumbnail for set
    │   └── cards/
    │       ├── c001.jpg  # Individual card images
    │       └── c002.jpg
    └── s002/
        ├── banner.jpg
        ├── thumbnail.jpg
        └── cards/
            └── c001.jpg
```

---

## creators.json Structure

**Purpose**: Store creator profiles (think YouTube channels)

```json
{
  "creator_id": "string", // Short, meaningful ID (e.g., "carlosi", "anahealth") - must be unique, checked by system
  "display_name": "string", // Full real name for display (e.g., "Carlos Irineu da Costa", "Ana Silva")
  "bio": "string", // Brief creator description for profile pages
  "avatar_url": "string", // Profile image URL - relative path preferred (./images/avatars/creator_id.jpg)
  "social_links": {
    "website": "string", // Full URL to creator's website (optional)
    "linkedin": "string", // LinkedIn profile URL (optional)
    "instagram": "string" // Instagram handle (optional)
  },
  "specialties": ["array"], // Areas of expertise (e.g., ["Wellness", "Nutrition", "Space Science"])
  "created_at": "string", // ISO 8601 timestamp
  "updated_at": "string", // ISO 8601 timestamp
  "status": "string" // "active" | "inactive" | "pending"
}
```

---

## content_sets.json Structure

**Purpose**: Store content collections (think YouTube playlists, 50-100 cards each)

```json
{
  "set_id": "string", // Full unique identifier (auto-generated: creator_id_category_timestamp)
  "set_number": "string", // Short reference ID (e.g., "s001", "s002") - for file organization and quick reference
  "creator_id": "string", // References creators.json creator_id
  "title": "string", // Display title for the set (e.g., "Bem-Estar Após os 50")
  "description": "string", // Detailed description shown on set page
  "category": "string", // Content category (e.g., "wellness", "space_exploration", "nutrition")
  "thumbnail_url": "string", // Grid thumbnail - preferred path: ./images/sets/{set_number}/thumbnail.jpg
  "banner_url": "string", // Hero banner - preferred path: ./images/sets/{set_number}/banner.jpg
  "card_count": "number", // Expected: 50-100 cards per set
  "estimated_time_minutes": "number", // Time to complete entire set
  "difficulty_level": "string", // "beginner" | "intermediate" | "advanced"
  "target_audience": "string", // Free text describing intended audience
  "color_scheme": {
    "primary": "string", // Hex color code for main UI elements
    "secondary": "string", // Hex color code for secondary buttons
    "accent": "string" // Hex color code for highlights
  },
  "supported_navigation": ["array"], // ["thematic", "random", "sequential"]
  "content_style": "string", // "question_first" | "story_driven" | "quiz" | "tutorial"
  "tags": ["array"], // SEO and filtering tags (English)
  "tags_pt": ["array"], // Display tags in Portuguese
  "is_hero": "boolean", // Whether this set appears as homepage hero (only one should be true)
  "prerequisites": ["array"], // What user should know before starting
  "learning_outcomes": ["array"], // What user will learn after completion
  "stats": {
    "views": "number", // Usage statistics
    "completion_rate": "number" // Decimal (0.0 to 1.0)
  },
  "status": "string", // "published" | "draft" | "archived"
  "language": "string", // ISO language code (e.g., "pt-BR")
  "created_at": "string", // ISO 8601 timestamp
  "updated_at": "string" // ISO 8601 timestamp
}
```

---

## cards.json Structure

**Purpose**: Individual educational content cards within sets

```json
{
  "card_id": "string", // Full unique identifier (auto-generated: set_id_card_XXX)
  "card_number": "string", // Short reference (e.g., "c001", "c002") - for file organization
  "set_id": "string", // References content_sets.json set_id
  "creator_id": "string", // References creators.json creator_id
  "title": "string", // Card question/title (displayed prominently in quiz)
  "summary": "string", // Brief hint/tip (shown before revealing answer)
  "detailed_content": "string", // Full answer/explanation (shown after "Mostrar Resposta")
  "order_index": "number", // Position within the set (1-based)
  "navigation_contexts": {
    "thematic": {
      "position": "number", // Position within thematic grouping
      "total_items": "number", // Total items in this theme
      "context_data": {
        "theme": "string" // Theme name for grouping
      }
    }
  },
  "media": [
    {
      "media_type": "string", // "image" | "video" | "audio"
      "url": "string", // Preferred path: ./images/sets/{set_number}/cards/{card_number}.jpg
      "alt_text": "string", // Accessibility description
      "source": "string", // Attribution source
      "license": "string", // Usage rights
      "validation_status": "string", // "verified" | "pending" | "needs_review"
      "last_checked": "string" // ISO 8601 timestamp
    }
  ],
  "domain_data": {
    "related_concepts": ["array"] // Related topics for cross-linking
  },
  "tags": ["array"], // Content tags for filtering
  "created_at": "string", // ISO 8601 timestamp
  "updated_at": "string" // ISO 8601 timestamp
}
```

---

## Builder Integration Notes

### Required Builder Changes:
1. **Set Numbering**: Auto-generate `set_number` (s001, s002, etc.) and check for duplicates
2. **Card Numbering**: Auto-generate `card_number` (c001, c002, etc.) within each set
3. **Creator ID Validation**: Check `creator_id` availability before creation
4. **Image Path Generation**: Auto-generate standardized paths using set/card numbers
5. **Color Scheme Selection**: Provide UI for choosing per-set color themes

### Migration Notes:
- Current data can be migrated by adding `set_number` and `card_number` fields
- Image paths can be updated systematically
- Existing IDs should be preserved for data continuity
