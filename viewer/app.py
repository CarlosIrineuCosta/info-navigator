#!/usr/bin/env python3
"""
Lunar Cards Explorer - Educational Card Game about Moon Exploration
A Flask web application for exploring lunar history through interactive cards.
"""

from flask import Flask, render_template, jsonify, request
import json
import random
import os

app = Flask(__name__)

# Global data storage
cards_data = {}
images_data = {}

def load_data():
    """Load JSON data files"""
    global cards_data, images_data
    
    # Load cards data
    with open('data/lunar_cards_json_10q_v1.json', 'r', encoding='utf-8') as f:
        cards_data = json.load(f)
    
    # Load images data
    with open('data/lunar_card_images.json', 'r', encoding='utf-8') as f:
        images_data = json.load(f)
    
    print(f"📚 Loaded {len(cards_data['cards'])} cards")

def get_card_by_id(card_id):
    """Get a specific card by ID"""
    for card in cards_data['cards']:
        if card['id'] == card_id:
            return card
    return None

def get_image_path(card_id):
    """Get local image path for a card"""
    return f"images/card_{card_id}.jpg"

def process_video_url(url):
    """Process video URL to get embeddable format"""
    if not url:
        return None
    
    # Handle YouTube URLs with timestamps
    if 'youtube.com/watch' in url or 'youtu.be/' in url:
        # Extract video ID and timestamp
        if 'youtube.com/watch' in url:
            video_id = url.split('v=')[1].split('&')[0]
            if '&t=' in url:
                timestamp = url.split('&t=')[1].split('&')[0]
                if 's' in timestamp:
                    timestamp = timestamp.replace('s', '')
            else:
                timestamp = None
        elif 'youtu.be/' in url:
            video_parts = url.split('youtu.be/')[1].split('?')
            video_id = video_parts[0]
            if len(video_parts) > 1 and 't=' in video_parts[1]:
                timestamp = video_parts[1].split('t=')[1].split('&')[0]
                if 's' in timestamp:
                    timestamp = timestamp.replace('s', '')
            else:
                timestamp = None
        
        # Build embed URL
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        if timestamp:
            embed_url += f"?start={timestamp}&autoplay=0&rel=0"
        else:
            embed_url += "?autoplay=0&rel=0"
        
        return embed_url
    
    return url

def get_navigation_order(nav_type, current_id=1):
    """Get card order based on navigation type"""
    total_cards = len(cards_data['cards'])
    
    if nav_type == 'timeline':
        # Chronological order (cards are already in chronological order)
        return list(range(1, total_cards + 1))
    
    elif nav_type == 'thematic':
        # Group by themes (Soviet era, American era, Modern era)
        soviet_era = [1, 4]  # Luna missions
        american_era = [2, 3]  # Apollo and Gemini
        international_era = [5, 6, 8]  # China, India, ESA
        modern_commercial = [7, 9, 10]  # Artemis, Private, Mars prep
        return soviet_era + american_era + international_era + modern_commercial
    
    elif nav_type == 'random':
        # Random order
        order = list(range(1, total_cards + 1))
        random.shuffle(order)
        return order
    
    # Default to timeline
    return list(range(1, total_cards + 1))

@app.route('/')
def index():
    """Homepage - show first card"""
    return render_template('index.html')

@app.route('/card/<int:card_id>')
def show_card(card_id):
    """Display a specific card"""
    card = get_card_by_id(card_id)
    if not card:
        return "Card not found", 404
    
    # Add image path and video URL to card data
    card_with_media = card.copy()
    card_with_media['image_path'] = get_image_path(card_id)
    
    # Process video URL if present
    if 'video_url' in card:
        card_with_media['video_url'] = process_video_url(card['video_url'])
    else:
        card_with_media['video_url'] = None
    
    return render_template('card.html', card=card_with_media)

@app.route('/api/navigation/<nav_type>/<int:current_id>')
def get_navigation(nav_type, current_id):
    """API endpoint for navigation logic"""
    order = get_navigation_order(nav_type)
    
    try:
        current_index = order.index(current_id)
        
        next_id = order[(current_index + 1) % len(order)]
        prev_id = order[(current_index - 1) % len(order)]
        
        return jsonify({
            'next_id': next_id,
            'prev_id': prev_id,
            'current_index': current_index + 1,
            'total_cards': len(order),
            'navigation_type': nav_type
        })
    except ValueError:
        # Current ID not in order, default to first card
        return jsonify({
            'next_id': order[1] if len(order) > 1 else order[0],
            'prev_id': order[-1],
            'current_index': 1,
            'total_cards': len(order),
            'navigation_type': nav_type
        })

@app.route('/api/card/<int:card_id>')
def get_card_data(card_id):
    """API endpoint to get card data as JSON"""
    card = get_card_by_id(card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    
    card_with_media = card.copy()
    card_with_media['image_path'] = get_image_path(card_id)
    
    # Process video URL if present
    if 'video_url' in card:
        card_with_media['video_url'] = process_video_url(card['video_url'])
    else:
        card_with_media['video_url'] = None
    
    return jsonify(card_with_media)

@app.route('/api/cards/all')
def get_all_cards():
    """API endpoint to get all cards metadata"""
    cards_summary = []
    for card in cards_data['cards']:
        cards_summary.append({
            'id': card['id'],
            'titulo': card['titulo'],
            'resumo': card['resumo']
        })
    return jsonify({'cards': cards_summary})

if __name__ == '__main__':
    # Load data on startup
    load_data()
    
    # Run the app
    print("🌙 Starting Lunar Cards Explorer...")
    print("📍 Access the app at: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
