#!/bin/bash

# Boxiii Git Setup Script
echo "Setting up Boxiii Git repository..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to boxiii directory
cd /home/cdc/projects/boxiii

echo -e "${YELLOW}Step 1: Initializing Git repository${NC}"
git init
git branch -m main

echo -e "${YELLOW}Step 2: Creating .gitignore${NC}"
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.env
*.pyc

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
package-lock.json

# Build directories
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
*.Zone.Identifier

# Project specific
builder/data/images/
viewer/build/
*.log
.cache/

# Environment files
.env.local
.env.development.local
.env.test.local
.env.production.local

# Large files
*.mp4
*.avi
*.mov
*.zip
*.tar.gz
EOF

echo -e "${YELLOW}Step 3: Creating environment template${NC}"
cat > .env.example << 'EOF'
# Builder Service
JWT_SECRET=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
CLAUDE_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-api-key

# Database (future)
MONGODB_URI=mongodb://localhost:27017/boxiii

# Viewer Service
REACT_APP_API_URL=http://localhost:8001
REACT_APP_ENVIRONMENT=development
EOF

echo -e "${YELLOW}Step 4: Adding files to Git${NC}"
git add .

echo -e "${YELLOW}Step 5: Creating initial commit${NC}"
git commit -m "Initial Boxiii platform structure

- Unified Info Navigator architecture
- Builder: Admin/CMS for content creation
- Viewer: PWA for content consumption
- Docker configuration for containerized deployment
- Shared schemas and migration tools

🤖 Generated with Claude Code (https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo -e "${GREEN}✓ Git repository initialized successfully!${NC}"
echo ""
echo -e "${BLUE}Repository Status:${NC}"
git status
echo ""
git log --oneline

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Choose GitHub strategy:"
echo "   A) Create new repository: gh repo create boxiii --public"
echo "   B) Add to existing: git remote add origin https://github.com/CarlosIrineuCosta/info-navigator.git"
echo ""
echo "2. Copy environment file: cp .env.example .env"
echo "3. Add your API keys to .env"
echo "4. Test format converter: cd builder/backend && python format_converter.py"

echo ""
echo -e "${GREEN}Setup complete! 🚀${NC}"