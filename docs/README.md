# GitMind Landing Page

## Overview

This is the landing page for GitMind - AI-powered code review for GitLab.

## Quick Preview

To preview locally:
```bash
cd landing-page
python3 -m http.server 8080
# Open http://localhost:8080
```

Or open `index.html` directly in browser.

## Features

- Modern, responsive design
- Dark theme
- Animated stats
- Pricing tiers (Free/Pro/Team)
- How It Works section
- Feature highlights

## Deployment

### Option 1: GitHub Pages (Free)
1. Push to GitHub repo
2. Go to Settings → Pages
3. Select `main` branch and `/landing-page` folder
4. Your site will be live at: `username.github.io/repo-name`

### Option 2: Netlify (Free)
1. Go to netlify.com
2. Drag and drop the `landing-page` folder
3. Get instant URL

### Option 3: Vercel (Free)
1. Go to vercel.com
2. Import project
3. Set root directory to `landing-page`
4. Deploy

## Customization

### Change Logo
Replace the emoji in `.logo-icon` or use an SVG image.

### Update Stats
Edit the `.stat-number` values in `index.html`.

### Change Colors
Modify CSS variables in `:root`:
```css
--primary: #6366f1;
--secondary: #22c55e;
--dark: #0f172a;
```

### Update Pricing
Edit the `.pricing-card` sections.

## Sections

1. **Hero** - Main headline and demo
2. **Stats** - Key metrics
3. **Features** - What GitMind does
4. **How It Works** - 3-step process
5. **Pricing** - Tier comparison
6. **CTA** - Call to action
7. **Footer** - Links

## Tech Stack

- HTML5
- CSS3 (no frameworks)
- Vanilla JavaScript
- Google Fonts (Inter)

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

MIT
