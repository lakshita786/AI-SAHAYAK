# AI Sahayak - Background Assets

## Files

1. **background-hero.svg** - Vector-based background (can be used directly in browser)
   - Location: `UI/assets/background-hero.svg`
   - Size: 1920x1080 (Full HD)
   - Format: SVG (scalable vector)

2. **background.css** - CSS classes for background styling
   - Location: `UI/styles/background.css`

## How to Convert SVG to PNG/JPG

Since macOS doesn't have ImageMagick pre-installed, here are options:

### Option 1: Online Converters
- Upload `background-hero.svg` to:
  - https://cloudconvert.com/svg-to-png
  - https://www.iloveimg.com/svg-to-png
  - https://convertio.co/svg-png/

### Option 2: Using Homebrew (Recommended)
```bash
# Install ImageMagick via Homebrew
brew install imagemagick

# Convert SVG to PNG (1920x1080)
convert UI/assets/background-hero.svg -resize 1920x1080 UI/assets/background-hero.png

# Convert to JPG (with quality)
convert UI/assets/background-hero.svg -resize 1920x1080 -quality 85 UI/assets/background-hero.jpg
```

### Option 3: Using Preview (Manual)
1. Open `background-hero.svg` in Safari
2. File → Export as PDF (or just screenshot)
3. Open exported file in Preview
4. Export as PNG/JPG

## Current Usage

The background is currently using the SVG file path in all HTML pages:
```css
background-image: 
  linear-gradient(rgba(250, 247, 244, 0.85), rgba(250, 247, 244, 0.85)),
  url('../assets/background-hero.svg');
```

To use PNG instead after conversion:
```css
background-image: 
  linear-gradient(rgba(250, 247, 244, 0.85), rgba(250, 247, 244, 0.85)),
  url('../assets/background-hero.png');
```