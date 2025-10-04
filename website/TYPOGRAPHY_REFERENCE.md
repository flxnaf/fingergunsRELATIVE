# Typography Reference Guide

This document shows exactly how to use the semantic typography classes throughout the FingerGuns website.

## 🎯 Core Principle

**Every heading and paragraph must use semantic classes.** Never use inline styles or Tailwind's text sizing utilities for typography. All typography is controlled from `app/globals.css`.

## 📋 The Six Semantic Classes

### 1. `.brand-text` - Brand Name Only
```tsx
<span className="brand-text text-2xl text-white">FingerGuns</span>
```
- **Purpose**: FingerGuns logo/brand name ONLY
- **Font**: NextF Games Black Italic (custom)
- **Usage**: Navigation logo, footer logo
- **Notes**: The ONLY place the custom font appears

### 2. `.h1-text` - Hero Headlines
```tsx
<h1 className="h1-text text-white mb-6">
  Control CSGO with Hand Gestures
</h1>
```
- **Purpose**: Page heroes, main headlines
- **Size**: 60px desktop / 40px mobile
- **Weight**: Bold (700)
- **Letter-spacing**: -3%
- **Font**: System fonts

### 3. `.h2-text` - Section Titles
```tsx
<h2 className="h2-text text-white mb-4">Advanced Features</h2>
```
- **Purpose**: Major section headings
- **Size**: 40px desktop / 32px mobile
- **Weight**: Semibold (600)
- **Letter-spacing**: -2.5%
- **Font**: System fonts

### 4. `.h3-text` - Subsection Titles
```tsx
<h3 className="h3-text text-white mb-4">Our Mission</h3>
```
- **Purpose**: Subsection headings within sections
- **Size**: 30px desktop / 24px mobile
- **Weight**: Semibold (600)
- **Letter-spacing**: -2%
- **Font**: System fonts

### 5. `.h4-text` - Card Titles
```tsx
<h4 className="h4-text text-white mb-3">Finger Tracking</h4>
```
- **Purpose**: Card titles, smaller headings
- **Size**: 24px desktop / 20px mobile
- **Weight**: Semibold (600)
- **Letter-spacing**: -1.5%
- **Font**: System fonts

### 6. `.body-text` - All Paragraphs
```tsx
<p className="body-text text-gray-300 mb-4">
  Revolutionary computer vision technology...
</p>
```
- **Purpose**: All paragraph text, descriptions, body copy
- **Size**: 18px desktop / 16px mobile
- **Weight**: Regular (400)
- **Letter-spacing**: 0
- **Line-height**: 1.7 (comfortable reading)
- **Font**: System fonts

## ✅ Correct Usage Examples

### Navigation Link
```tsx
<Link href="/" className="body-text text-sm text-gray-300">
  Home
</Link>
```

### Hero Section
```tsx
<h1 className="h1-text text-white mb-6">Control CSGO with Hand Gestures</h1>
<p className="body-text text-gray-300 mb-12">
  Revolutionary computer vision technology...
</p>
```

### Feature Card
```tsx
<div className="p-8">
  <h3 className="h4-text text-white mb-4">Finger Tracking</h3>
  <p className="body-text text-gray-400">
    Precision hand gesture recognition...
  </p>
</div>
```

### Table Cell Text
```tsx
<td className="body-text text-sm text-gray-300 p-4">Index Finger Point</td>
```

## ❌ Incorrect Usage (Don't Do This)

```tsx
<!-- DON'T: Using Tailwind text sizes -->
<h1 className="text-6xl font-bold">Bad</h1>

<!-- DON'T: Inline styles -->
<h1 style={{fontSize: '60px', fontWeight: 700}}>Bad</h1>

<!-- DON'T: Missing semantic class -->
<h1 className="text-white">Bad</h1>

<!-- DON'T: Custom font on regular text -->
<p className="brand-text">This should be body-text</p>
```

## 🎨 Color Modifiers

You can (and should) add color utilities to semantic classes:

```tsx
<h2 className="h2-text text-white">White heading</h2>
<p className="body-text text-gray-300">Light gray text</p>
<p className="body-text text-gray-400">Medium gray text</p>
<p className="body-text text-gray-500">Dark gray text</p>
```

## 📐 Size Modifiers for Body Text

For body text variants (nav links, table cells, small print):

```tsx
<p className="body-text text-sm">Smaller body text</p>
<p className="body-text">Normal body text (default)</p>
<p className="body-text text-xs">Tiny text (copyright, etc)</p>
```

## 🔧 Adjusting Typography Site-Wide

To change typography across the ENTIRE site, edit `app/globals.css`:

```css
/* Want bigger headlines? Edit here */
.h1-text {
  font-size: 4rem; /* Changed from 3.75rem */
}

/* Want different body text spacing? Edit here */
.body-text {
  line-height: 1.8; /* Changed from 1.7 */
}

/* Want a different font family? Edit here */
:root {
  --font-system: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

Changes will apply automatically to every instance across all pages.

## 📱 Responsive Breakpoints

The semantic classes automatically adjust for mobile:

- **Desktop**: Above 768px
- **Mobile**: 768px and below

No need to add responsive utilities—it's built into the semantic classes.

## 🎯 Summary

1. **Always use semantic classes** for typography
2. **Never use Tailwind text sizes** (text-xl, text-2xl, etc) for content
3. **Only `.brand-text`** uses the custom font
4. **Everything else** uses system fonts
5. **Adjust globally** by editing `globals.css`
6. **Add color utilities** as needed (text-white, text-gray-300, etc)

---

**Result**: Clean, maintainable typography that can be adjusted site-wide from a single CSS file.

