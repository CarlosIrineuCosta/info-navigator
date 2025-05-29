#!/bin/bash
# Lunar Cards Explorer - Quick Setup Script
# Run this in your project directory after activating your virtual environment

echo "🌙 Lunar Cards Explorer - Setup Script"
echo "======================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  Warning: No virtual environment detected. Please activate your venv first:"
    echo "   source box-i/bin/activate"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download NASA images
echo "🖼️  Downloading NASA images..."
python download_images.py

# Create any missing directories
mkdir -p static/images
mkdir -p templates
mkdir -p data

echo ""
echo "🚀 Setup complete!"
echo ""
echo "To run the application:"
echo "  python app.py"
echo ""
echo "Then open your browser to: http://localhost:5001"
echo ""
echo "Navigation tips:"
echo "  • Use arrow keys ← → to navigate between cards"
echo "  • Press H to return home"
echo "  • Choose between Timeline, Thematic, or Random navigation"
