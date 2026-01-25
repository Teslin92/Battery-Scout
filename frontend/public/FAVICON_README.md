# Favicon and OG Image Assets

## Files Created

1. **favicon.svg** - Modern SVG favicon (works in all modern browsers)
2. **og-image.svg** - Open Graph image for social media sharing (1200x630)

## Converting SVG to PNG (Optional)

Some social media platforms prefer PNG over SVG. To convert:

### Option 1: Online Tool
- Visit https://cloudconvert.com/svg-to-png
- Upload `og-image.svg`
- Set dimensions: 1200x630
- Download as `og-image.png`
- Update `index.html` to use `.png` instead of `.svg`

### Option 2: Using Node.js (if you have it)
```bash
npm install -g svg2png
svg2png og-image.svg --output og-image.png --width 1200 --height 630
```

### Option 3: Using Python (if you have it)
```bash
pip install cairosvg
cairosvg og-image.svg -o og-image.png -W 1200 -H 630
```

## Current Setup

The HTML is configured to use:
- SVG favicon (modern browsers)
- SVG OG image (works on most platforms)

If you need PNG versions for better compatibility, follow the conversion steps above.
