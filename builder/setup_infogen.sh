#!/bin/bash
# Setup script for Infogen content generation system

echo "🚀 Setting up Infogen Content Generator..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r infogen/requirements.txt

echo "🔧 Setting up data directories..."
mkdir -p infogen/data

echo "📋 Testing database initialization..."
cd infogen
python json_database.py

echo "✅ Infogen setup complete!"
echo ""
echo "To run the Infogen app:"
echo "1. cd infogen"
echo "2. source ../venv/bin/activate" 
echo "3. export ANTHROPIC_API_KEY='your-api-key'"
echo "4. python gradio_app.py"
echo ""
echo "The app will be available at: http://localhost:5002"
