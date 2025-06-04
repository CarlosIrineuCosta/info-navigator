# Image Migration Plan

## Current Structure
Images are currently using placeholder URLs from placehold.co:
- Banner URLs: `https://placehold.co/1280x720/...`
- Thumbnail URLs: `https://placehold.co/400x225/...`

## Target Structure for GitHub Pages
```
public/
  images/
    banners/
      space-health-banner.jpg
      wellness-50-banner.jpg
      nutrition-astronaut-banner.jpg
    thumbnails/
      space-health-thumb.jpg
      wellness-50-thumb.jpg
      nutrition-astronaut-thumb.jpg
```

## Updated Paths in content_sets.json
Replace placeholder URLs with:
- Banner URLs: `./images/banners/filename.jpg`
- Thumbnail URLs: `./images/thumbnails/filename.jpg`

## Notes
- Using relative paths (`./images/`) ensures compatibility with GitHub Pages
- Images should be optimized for web (JPEG for photos, PNG for graphics)
- Recommended sizes:
  - Banners: 1280x720px
  - Thumbnails: 400x225px
