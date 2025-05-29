# Info Navigator - Educational Content Platform

**Master Project Structure**

## 🎯 Project Overview
Info Navigator is a dual-system platform for creating and exploring educational content through interactive cards. It consists of two main components working together to provide a Netflix-style learning experience.

## 📁 Project Structure

```
info-navigator/                    # Master project folder
├── viewer/                       # Content exploration & display system
│   ├── app.py                   # Flask web application  
│   ├── templates/               # HTML templates
│   ├── static/                  # CSS, JS, images
│   ├── data/                    # Content data files
│   └── documentation/           # Viewer documentation
└── builder/                     # Content generation system
    ├── core_models.py          # Data structure definitions
    ├── json_database.py        # Database management
    ├── structured_generator.py # LLM content generation
    ├── gradio_app.py          # Content creation UI
    └── test_system.py         # System validation
```

## 🚀 Quick Start

### Viewer (Content Explorer)
```bash
cd /home/cdc/projects/info-navigator/viewer
source venv/bin/activate
python app.py
# Access at: http://localhost:5001
```

### Builder (Content Generator)  
```bash
cd /home/cdc/projects/info-navigator/builder
source ../viewer/venv/bin/activate
export ANTHROPIC_API_KEY='your-key'
python gradio_app.py
# Access at: http://localhost:5002
```

## 🎮 System Components

### 🎭 **Viewer** (Netflix-style Explorer)
- **Purpose**: Explore and navigate educational content
- **Features**: Multiple navigation modes, responsive design, card-based learning
- **Content**: Space exploration, wellness, nutrition, earth mysteries
- **Navigation**: Timeline, thematic, difficulty, random modes

### 🛠️ **Builder** (Content Generation Engine)
- **Purpose**: Create structured educational content with AI assistance
- **Features**: Multi-domain content generation, creator management, validation
- **Integration**: Bulletproof LLM validation, relationship integrity, batch processing
- **Output**: Structured JSON compatible with viewer system

## 🔗 System Integration

The **Builder** generates content that the **Viewer** consumes:
- Builder creates creators, content sets, and cards
- Viewer provides the exploration interface
- Shared data format ensures compatibility
- Netflix-style content discovery connects both systems

## 📊 Current Status

### ✅ **Viewer (Production Ready)**
- Complete Flask application with 10 lunar exploration cards
- Three navigation modes working
- Professional space-themed UI
- Mobile responsive design
- Video and image integration

### ✅ **Builder (Core Complete)**
- Flexible data models for multiple content domains
- JSON database with relationship integrity
- Structured LLM generation with validation
- Creator management system
- Homepage API generation

## 🎯 Content Domains Supported

- **🚀 Space Exploration**: Timeline and thematic navigation
- **💚 Wellness**: Thematic and difficulty navigation
- **🥗 Nutrition**: Thematic and difficulty navigation  
- **🌍 Earth Mysteries**: Thematic and random navigation
- **🪐 Solar System**: Timeline and thematic navigation

## 📍 Windows Access Paths

**Viewer:**
```
\\wsl.localhost\Ubuntu\home\cdc\projects\info-navigator\viewer\
```

**Builder:**
```
\\wsl.localhost\Ubuntu\home\cdc\projects\info-navigator\builder\
```

## 🏗️ Architecture Highlights

### Data Flow
1. **Builder** → Generate structured content with AI
2. **JSON Database** → Store with relationship integrity
3. **Viewer** → Netflix-style content discovery and exploration
4. **User Experience** → Seamless learning through interactive cards

### Key Design Principles
- **Separation of Concerns**: Generation vs. consumption
- **Bulletproof Validation**: LLM chaos controlled by Python structure
- **Flexible Domains**: Support for any educational content type
- **Netflix UX**: Familiar, engaging content discovery
- **Relationship Integrity**: Scalable to millions of interconnected records

## 🎉 Ready for Development

Both systems are **tested and functional**. The project structure provides:
- Clear separation between content creation and consumption
- Shared data models and formats
- Independent development and deployment
- Scalable architecture for multiple content domains

**Next Steps**: Enhance Builder UI, add image generation, implement advanced navigation features.
