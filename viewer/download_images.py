#!/usr/bin/env python3
"""
Image Download Script for Lunar Cards Project
Downloads all NASA images referenced in the JSON data file
"""

import json
import requests
import os
from urllib.parse import urlparse
import time

def download_images():
    """Download all images from the card images JSON file"""
    
    # Load image URLs
    with open('data/lunar_card_images.json', 'r') as f:
        image_data = json.load(f)
    
    # Create images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    print("🌙 Starting image download for Lunar Cards...")
    
    for card_id, url in image_data['card_images'].items():
        try:
            print(f"📥 Downloading image {card_id}...")
            
            # Get file extension from URL
            parsed_url = urlparse(url)
            filename = f"card_{card_id}.jpg"  # Default to jpg
            
            # Download the image
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save the image
            filepath = os.path.join('static', 'images', filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Saved: {filename}")
            
            # Be nice to NASA servers
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Failed to download image {card_id}: {str(e)}")
    
    print("🚀 Image download complete!")

if __name__ == "__main__":
    download_images()
