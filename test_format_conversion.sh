#!/bin/bash

# Test Format Conversion Script
echo "Testing Builder → Viewer format conversion..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Running format converter${NC}"
cd /home/cdc/projects/boxiii/builder/backend

# Run the converter
python3 format_converter.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Format conversion completed successfully${NC}"
else
    echo -e "${RED}✗ Format conversion failed${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 2: Checking output files${NC}"
cd /home/cdc/projects/boxiii/viewer/public/data

if [ -f "creators.json" ] && [ -f "content_sets.json" ] && [ -f "cards.json" ]; then
    echo -e "${GREEN}✓ All JSON files generated${NC}"
    
    echo "File sizes:"
    ls -lh *.json
    
    echo ""
    echo "Creator count: $(jq length creators.json)"
    echo "Content set count: $(jq length content_sets.json)"
    echo "Card count: $(jq length cards.json)"
    
else
    echo -e "${RED}✗ Missing output files${NC}"
    ls -la
    exit 1
fi

echo -e "${YELLOW}Step 3: Validating JSON format${NC}"
for file in creators.json content_sets.json cards.json; do
    if jq empty "$file" 2>/dev/null; then
        echo -e "${GREEN}✓ $file is valid JSON${NC}"
    else
        echo -e "${RED}✗ $file has invalid JSON${NC}"
    fi
done

echo -e "${YELLOW}Step 4: Checking PWA compatibility${NC}"
cd /home/cdc/projects/boxiii/viewer

# Check if we can start the dev server (just verify, don't actually start)
if [ -f "package.json" ]; then
    echo -e "${GREEN}✓ PWA structure found${NC}"
    echo "Available scripts:"
    jq -r '.scripts | keys[]' package.json
else
    echo -e "${RED}✗ PWA package.json not found${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Format conversion test complete!${NC}"
echo ""
echo -e "${YELLOW}To test the PWA viewer:${NC}"
echo "cd /home/cdc/projects/boxiii/viewer"
echo "npm install"
echo "npm start"
echo ""
echo -e "${YELLOW}To deploy to GitHub Pages:${NC}"
echo "npm run build"
echo "# Deploy build/ folder to GitHub Pages"