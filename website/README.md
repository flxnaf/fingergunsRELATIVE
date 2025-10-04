# FingerGuns Website

Professional marketing website for FingerGuns - a computer vision application that enables Counter-Strike: Global Offensive players to control the game using hand gestures and head tracking.

## Design Philosophy

- **Minimal, high-contrast design**: Black, white, and shades of gray
- **Modern tech aesthetic**: Clean and professional (Apple/Vercel style)
- **Sharp, angular elements**: No rounded corners
- **Maximum readability**: Plenty of whitespace and clear typography

## Tech Stack

- **Next.js 14+** with App Router
- **TypeScript**
- **Tailwind CSS**
- **Lucide React** for icons

## Typography System

The website uses a semantic class-based typography system defined in `app/globals.css`:

- `.brand-text` - For FingerGuns logo only (uses custom NextF Games Black Italic font)
- `.h1-text` - Hero headlines
- `.h2-text` - Section titles
- `.h3-text` - Subsection titles
- `.h4-text` - Card titles
- `.body-text` - All paragraph text

All typography can be adjusted globally by editing the CSS classes in `globals.css`.

## Custom Font Setup

**IMPORTANT:** The FingerGuns brand name uses the NextF Games Black Italic font. You need to add the font files to the project:

1. Place your NextF Games Black Italic font files in `/public/fonts/`
2. Supported formats (add what you have):
   - `NextF-Games-Black-Italic.woff2`
   - `NextF-Games-Black-Italic.woff`
   - `NextF-Games-Black-Italic.ttf`

The font is already configured in `globals.css` and will load automatically once the files are in place.

## Pages

- **Home** (`/`) - Hero, features, demo section, and CTA
- **About** (`/about`) - Mission, technology, and team information
- **Documentation** (`/docs`) - Quick start, system requirements, gesture controls, troubleshooting
- **Download** (`/download`) - Download page (currently placeholder)

## Development

First, install dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
website/
├── app/
│   ├── layout.tsx          # Root layout with Navigation & Footer
│   ├── page.tsx            # Home page
│   ├── globals.css         # Global styles & typography system
│   ├── about/
│   │   └── page.tsx        # About page
│   ├── docs/
│   │   └── page.tsx        # Documentation page
│   └── download/
│       └── page.tsx        # Download page
├── components/
│   ├── Navigation.tsx      # Header navigation
│   └── Footer.tsx          # Footer with links
└── public/
    └── fonts/              # Custom brand font (add your files here)
```

## Color Palette

- **Primary Background**: `#000000` (pure black)
- **Alternate Background**: `gray-950`
- **Card Backgrounds**: `gray-900/gray-800`
- **Text**: White (`#ffffff`)
- **Muted Text**: Gray shades (`gray-300/400/500`)
- **Borders**: `gray-800`

## Components

### Navigation
- Fixed header with FingerGuns logo (custom font)
- Desktop menu with Home, About, Docs, Download
- Responsive hamburger menu for mobile
- Semi-transparent black background with backdrop blur

### Footer
- Brand logo and description
- Social media icons (GitHub, Twitter, Email)
- Product and Support link columns
- Copyright information

## Typography Guidelines

- **Only use the custom font** for the FingerGuns brand name
- **System fonts** for all other text (clean, readable)
- **Bold** (700) for H1, **Semibold** (600) for H2-H4
- **Negative letter-spacing** on headings for tight, modern look
- **Comfortable line-height** (1.7) on body text for readability

## Build for Production

```bash
npm run build
npm start
```

## Content Tone

Professional, technical, and informative. Focus on innovation and technology. Accessible but not dumbed down. Suitable for both gamers and tech enthusiasts.
