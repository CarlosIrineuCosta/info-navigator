# Info Navigator Project Definition

## Project Overview

Info Navigator is an AI-powered educational content platform that combines intelligent content generation with Netflix-style discovery and presentation. The system consists of two main components designed to work together through a standardized data format.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Info Navigator System                     │
├─────────────────────────┬───────────────────────────────────┤
│      BUILDER           │           VIEWER                    │
├─────────────────────────┼───────────────────────────────────┤
│ • Gradio UI            │ • React PWA                       │
│ • Python Backend       │ • Tailwind CSS                    │
│ • Multi-LLM Support    │ • Netflix-style UI                │
│ • JSON Database        │ • Multi-language                  │
│ • Content Generation   │ • Offline capability              │
└─────────────────────────┴───────────────────────────────────┘
                          ↓
                   [Shared JSON Data Format]
```

## Component Details

### 1. Builder System (`/builder/`)

**Purpose**: Generate and manage educational content using AI

**Technology Stack**:
- Python 3.12+
- Gradio (current UI - to be migrated to React)
- Multi-provider LLM integration
- JSON-based persistence

**Key Features**:
- Creator profile management
- AI-powered topic extraction
- Multi-provider content generation (Gemini, Claude, GPT-4)
- 15 content categories
- Image management
- Cost optimization

**Main Files**:
- `card_builder.py` - Gradio application interface
- `unified_generator.py` - LLM provider abstraction
- `content_manager.py` - Content generation logic
- `creator_manager.py` - Creator profile handling
- `json_database.py` - Data persistence layer
- `core_models.py` - Data models and enums

### 2. Viewer System (PWA) (`../info-navigator-pwa/`)

**Purpose**: Present content in an engaging, Netflix-style interface

**Technology Stack**:
- React 18.2
- Tailwind CSS
- React Router DOM
- Progressive Web App features

**Key Features**:
- Homepage with hero banner
- Content browsing by sets
- Interactive quiz/card exploration
- Responsive design
- Multi-language support
- Offline capability

**Main Components**:
- `HomePage` - Netflix-style content discovery
- `ContentSetPage` - Browse card collections
- `QuizPage` - Interactive card exploration
- `dataService.js` - Data fetching and processing

## Data Model

### Core Entities

1. **Creators**
   - Profile information
   - Social media links
   - Avatar and banner images

2. **Content Sets**
   - Collection of related cards
   - Navigation metadata
   - Creator association

3. **Cards**
   - Educational content units
   - Multiple choice questions
   - Media attachments
   - Category classification

### Data Flow
```
Builder → JSON Files → PWA Viewer
         ↓
   [creators.json]
   [content_sets.json]
   [cards.json]
```

## Integration Requirements

### Current State
- Builder and Viewer operate independently
- Shared data through JSON files
- Manual file transfer between systems

### Target Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Container 1                         │
│                  [OpenWebUI + Ollama + LiteLLM]              │
└─────────────────────────┬───────────────────────────────────┘
                          ↓ API
┌─────────────────────────┴───────────────────────────────────┐
│                    Docker Container 2                         │
│                    [Info Navigator API]                       │
│  ┌─────────────────┐           ┌─────────────────┐         │
│  │  Builder API    │           │   Viewer API     │         │
│  │  (React UI)     │           │   (React PWA)    │         │
│  └─────────────────┘           └─────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Migration Plan

1. **Phase 1: UI Migration**
   - Convert Builder from Gradio to React + Tailwind
   - Maintain existing Python backend
   - Create unified React codebase

2. **Phase 2: API Development**
   - Expose Builder functionality via REST API
   - Integrate with OpenWebUI container
   - Implement authentication

3. **Phase 3: Deployment**
   - Dockerize both components
   - Deploy to VPS
   - Configure networking and security

## Development Guidelines

### Code Organization
- Modular architecture with clear separation
- Shared component library for React apps
- Consistent API contracts
- Environment-based configuration

### LLM Integration
- Use OpenWebUI as primary interface
- Support multiple providers through unified API
- Implement cost tracking and optimization
- Handle provider failures gracefully

### Data Management
- Start with JSON for rapid development
- Plan MongoDB migration for scale
- Implement data validation at all layers
- Version control for data schemas

## Immediate Tasks

1. **Repository Consolidation**
   - Merge both projects into single repository
   - Setup proper Git structure
   - Configure CI/CD pipeline

2. **React Migration**
   - Design unified component library
   - Port Gradio UI to React
   - Implement API layer

3. **OpenWebUI Integration**
   - Configure Docker container
   - Setup API endpoints
   - Test multi-model support

## Environment Setup

### Development
- WSL2 Ubuntu on Windows 11
- Python 3.12+ with virtual environment
- Node.js 18+ for React development
- Docker for containerization

### Production (Target)
- VPS with Docker support
- HTTPS with proper certificates
- Environment variable management
- Monitoring and logging

## Key Decisions

1. **Unified React Codebase**: Both Builder and Viewer will share React components
2. **API-First Design**: All functionality exposed through REST APIs
3. **Docker Deployment**: Containerized services for easy deployment
4. **OpenWebUI Integration**: Centralized LLM access point
5. **Progressive Enhancement**: Start simple, add features incrementally

## Testing Strategy

- Unit tests for core logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Performance testing for LLM operations
- Cross-browser testing for PWA

## Security Considerations

- API key management through environment variables
- Authentication for multi-user support
- Rate limiting for LLM requests
- Input validation and sanitization
- CORS configuration for API access

## Performance Optimization

- Lazy loading for React components
- Image optimization and CDN usage
- Caching strategies for LLM responses
- Database indexing for fast queries
- PWA offline capabilities

This project aims to democratize educational content creation while providing an engaging discovery experience similar to entertainment platforms.