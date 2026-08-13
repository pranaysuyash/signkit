# Landing Page - Visual Design & UI Components

**Date**: November 4, 2025  
**Project**: Signature Extractor Desktop App  
**Section**: Visual Design System & Component Library

---

## Design Philosophy

### Core Principles

1. **Premium macOS Aesthetic** - Native feel, not cross-platform compromise
2. **Clean Minimalism** - Focus on content, not decoration
3. **Conversion-Focused** - Every element drives toward purchase
4. **Performance-First** - Fast loading, optimized assets

### Design Inspirations

- **Apple.com** - Clean, spacious, premium feel
- **Linear** - Modern SaaS aesthetic with subtle gradients
- **Notion** - Card-based layout with excellent typography
- **Figma** - Tool-focused design with clear CTAs

---

## Color Palette

### Primary Colors

```css
/* Brand Colors */
--primary-blue: #007aff; /* macOS blue, primary CTAs */
--primary-purple: #5856d6; /* Secondary actions */
--success-green: #30d158; /* Success states, guarantees */

/* Text Colors */
--text-primary: #1c1c1e; /* Headlines, important text */
--text-secondary: #3a3a3c; /* Body text */
--text-tertiary: #8e8e93; /* Captions, fine print */

/* Background Colors */
--bg-primary: #ffffff; /* Main background */
--bg-secondary: #f2f2f7; /* Section backgrounds */
--bg-tertiary: #f9f9fb; /* Card backgrounds */

/* Neutral Colors */
--neutral-dark: #1c1c1e; /* Dark mode elements */
--neutral-medium: #8e8e93; /* Dividers, borders */
--neutral-light: #e5e5ea; /* Subtle borders */
--neutral-lighter: #f2f2f7; /* Very light backgrounds */
```

### Glassmorphism Effects

```css
/* Glass panel styling */
.glass-panel {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .glass-panel {
    background: rgba(28, 28, 30, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
}
```

### Gradients

```css
/* Primary gradient for hero section */
.hero-gradient {
  background: linear-gradient(135deg, #007aff 0%, #5856d6 100%);
}

/* Success gradient for CTAs */
.success-gradient {
  background: linear-gradient(135deg, #30d158 0%, #34c759 100%);
}

/* Subtle section gradients */
.section-gradient {
  background: linear-gradient(
    180deg,
    rgba(242, 242, 247, 0.8) 0%,
    rgba(249, 249, 251, 0.8) 100%
  );
}
```

---

## Typography System

### Font Stack

```css
/* Primary font - System fonts for performance */
--font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
  'Helvetica Neue', Arial, sans-serif;

/* Monospace for code/technical content */
--font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas,
  'Courier New', monospace;
```

### Type Scale

```css
/* Display styles */
.text-display-xl {
  font-size: 4rem; /* 64px */
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.text-display-lg {
  font-size: 3rem; /* 48px */
  line-height: 1.1;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.text-display {
  font-size: 2.25rem; /* 36px */
  line-height: 1.2;
  font-weight: 600;
}

/* Heading styles */
.text-heading-1 {
  font-size: 2rem; /* 32px */
  line-height: 1.3;
  font-weight: 600;
}

.text-heading-2 {
  font-size: 1.5rem; /* 24px */
  line-height: 1.4;
  font-weight: 600;
}

.text-heading-3 {
  font-size: 1.25rem; /* 20px */
  line-height: 1.4;
  font-weight: 500;
}

/* Body text */
.text-body-xl {
  font-size: 1.25rem; /* 20px */
  line-height: 1.6;
  font-weight: 400;
}

.text-body {
  font-size: 1rem; /* 16px */
  line-height: 1.6;
  font-weight: 400;
}

.text-body-sm {
  font-size: 0.875rem; /* 14px */
  line-height: 1.5;
  font-weight: 400;
}

/* Captions */
.text-caption {
  font-size: 0.75rem; /* 12px */
  line-height: 1.4;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### Text Color Classes

```css
.text-primary {
  color: var(--text-primary);
}
.text-secondary {
  color: var(--text-secondary);
}
.text-tertiary {
  color: var(--text-tertiary);
}
.text-success {
  color: var(--success-green);
}
.text-blue {
  color: var(--primary-blue);
}
```

---

## Component Library

### 1. Button Components

#### Primary Button

```html
<button class="btn btn-primary btn-lg">
  <span class="btn-text">Buy Lifetime - $29</span>
  <span class="btn-badge">Launch Price</span>
</button>
```

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: none;
  border-radius: 12px;
  font-family: var(--font-primary);
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.btn-primary {
  background: var(--primary-blue);
  color: white;
  padding: 1rem 2rem;
  font-size: 1rem;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.4);
  background: #0056cc;
}

.btn-lg {
  padding: 1.25rem 2.5rem;
  font-size: 1.125rem;
  border-radius: 16px;
}

.btn-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}
```

#### Secondary Button

```css
.btn-secondary {
  background: transparent;
  color: var(--primary-blue);
  border: 2px solid var(--primary-blue);
  padding: 0.875rem 2rem;
}

.btn-secondary:hover {
  background: var(--primary-blue);
  color: white;
  transform: translateY(-1px);
}
```

#### Ghost Button

```css
.btn-ghost {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.875rem 2rem;
  backdrop-filter: blur(10px);
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.2);
}
```

### 2. Card Components

#### Feature Card

```html
<div class="card feature-card">
  <div class="card-icon">
    <svg><!-- Icon --></svg>
  </div>
  <h3 class="card-title">Precision Extraction</h3>
  <p class="card-description">
    Zoom controls for pixel-perfect selection with threshold and color
    adjustment.
  </p>
</div>
```

```css
.card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.12);
}

.feature-card {
  text-align: center;
  max-width: 320px;
}

.card-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #007aff, #5856d6);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.card-description {
  color: var(--text-secondary);
  line-height: 1.6;
}
```

#### Pricing Card

```css
.pricing-card {
  background: white;
  border: 2px solid var(--primary-blue);
  border-radius: 24px;
  padding: 3rem 2rem;
  text-align: center;
  position: relative;
  box-shadow: 0 16px 48px rgba(0, 122, 255, 0.15);
}

.pricing-card::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(135deg, #007aff, #5856d6);
  border-radius: 24px;
  z-index: -1;
}

.pricing-badge {
  background: var(--success-green);
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  display: inline-block;
  margin-bottom: 1rem;
}

.price-display {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.price-original {
  text-decoration: line-through;
  color: var(--text-tertiary);
  font-size: 1.5rem;
  margin-right: 1rem;
}

.price-note {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 2rem;
}
```

### 3. Section Layouts

#### Hero Section

```html
<section class="hero">
  <div class="container">
    <div class="hero-content">
      <div class="hero-text">
        <h1 class="hero-title">
          Extract signatures.<br />
          Place on PDFs.<br />
          <span class="text-gradient">Done.</span>
        </h1>
        <p class="hero-subtitle">
          The only desktop app that extracts clean signatures and places them on
          PDFs. Privacy-first, precision-focused, no subscriptions.
        </p>
        <div class="hero-cta">
          <button class="btn btn-primary btn-lg">
            Buy Lifetime - $29
            <span class="btn-badge">Launch Price</span>
          </button>
          <button class="btn btn-secondary">Watch 45s Demo</button>
        </div>
        <div class="hero-badges">
          <span class="badge">30-day guarantee</span>
          <span class="badge">Lifetime updates</span>
          <span class="badge">Privacy-first</span>
        </div>
      </div>
      <div class="hero-visual">
        <div class="demo-showcase">
          <!-- Before/after slider or GIF -->
        </div>
      </div>
    </div>
  </div>
</section>
```

```css
.hero {
  background: linear-gradient(135deg, #007aff 0%, #5856d6 100%);
  color: white;
  padding: 6rem 0;
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg>...</svg>') repeat;
  opacity: 0.1;
  pointer-events: none;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.text-gradient {
  background: linear-gradient(135deg, #ffd700, #ffa500);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 1.5rem;
}

.hero-subtitle {
  font-size: 1.25rem;
  line-height: 1.6;
  margin-bottom: 3rem;
  opacity: 0.9;
}

.hero-cta {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.hero-badges {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.hero-visual {
  position: relative;
}

.demo-showcase {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  backdrop-filter: blur(20px);
  padding: 2rem;
  min-height: 400px;
}
```

#### Comparison Table

```html
<table class="comparison-table">
  <thead>
    <tr>
      <th>Feature</th>
      <th class="highlight">Signature Extractor</th>
      <th>Adobe Acrobat Pro</th>
      <th>DocuSign</th>
      <th>Smallpdf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Pricing</td>
      <td class="highlight">$29 lifetime</td>
      <td>$240/year</td>
      <td>$120/year</td>
      <td>$144/year</td>
    </tr>
    <tr>
      <td>Local Processing</td>
      <td class="highlight">✅ Yes</td>
      <td>❌ No</td>
      <td>❌ No</td>
      <td>❌ No</td>
    </tr>
  </tbody>
</table>
```

```css
.comparison-table {
  width: 100%;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin: 2rem 0;
}

.comparison-table th,
.comparison-table td {
  padding: 1.5rem;
  text-align: left;
  border-bottom: 1px solid var(--neutral-lighter);
}

.comparison-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.comparison-table .highlight {
  background: rgba(0, 122, 255, 0.05);
  color: var(--primary-blue);
  font-weight: 600;
}
```

### 4. Interactive Components

#### Before/After Image Slider

```html
<div class="before-after-slider">
  <div class="before-image">
    <img src="messy-scan.jpg" alt="Messy scanned signature" />
    <span class="image-label">Before</span>
  </div>
  <div class="after-image">
    <img src="clean-signature.png" alt="Clean transparent signature" />
    <span class="image-label">After</span>
  </div>
  <input type="range" class="slider-input" min="0" max="100" value="50" />
</div>
```

#### Use Case Cards

```html
<div class="use-case-grid">
  <div class="use-case-card">
    <div class="use-case-icon">⚖️</div>
    <h3>Legal Contracts</h3>
    <p>
      Extract client signatures from scanned contracts for e-signing platforms.
    </p>
    <div class="use-case-tag">Popular</div>
  </div>
  <div class="use-case-card">
    <div class="use-case-icon">🏠</div>
    <h3>Real Estate</h3>
    <p>Speed up closings by reusing client signatures across documents.</p>
  </div>
  <div class="use-case-card">
    <div class="use-case-icon">🏥</div>
    <h3>Healthcare</h3>
    <p>HIPAA-compliant extraction of patient consent form signatures.</p>
  </div>
</div>
```

```css
.use-case-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
}

.use-case-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
}

.use-case-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.use-case-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.use-case-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.use-case-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.use-case-tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: var(--success-green);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}
```

---

## Responsive Design Breakpoints

```css
/* Mobile First Approach */

/* Small phones */
@media (max-width: 480px) {
  .hero-title {
    font-size: 2.5rem;
  }
  .hero-cta {
    flex-direction: column;
  }
  .btn {
    width: 100%;
  }
}

/* Large phones */
@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 2rem;
    text-align: center;
  }

  .hero-title {
    font-size: 3rem;
  }
  .comparison-table {
    font-size: 0.875rem;
  }
  .comparison-table th,
  .comparison-table td {
    padding: 1rem;
  }
}

/* Tablets */
@media (max-width: 1024px) {
  .hero-title {
    font-size: 3.5rem;
  }
  .use-case-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop */
@media (min-width: 1025px) {
  .hero-title {
    font-size: 4rem;
  }
  .use-case-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## Animation Guidelines

### CSS Transitions

```css
/* Standard transition timing */
.transition-standard {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Faster transitions for interactive elements */
.transition-fast {
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Smooth entrance animations */
.fade-in-up {
  opacity: 0;
  transform: translateY(30px);
  animation: fadeInUp 0.6s ease forwards;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover effects */
.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}
```

### Loading States

```css
.loading-skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
```

---

## Accessibility Guidelines

### Color Contrast

- **Normal text**: 4.5:1 contrast ratio minimum
- **Large text**: 3:1 contrast ratio minimum
- **Interactive elements**: 3:1 contrast ratio minimum

### Focus States

```css
.btn:focus,
input:focus,
textarea:focus {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}

/* Custom focus ring for better visibility */
.focus-ring:focus {
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.3);
}
```

### Screen Reader Support

```html
<!-- Descriptive button text -->
<button aria-label="Buy Signature Extractor lifetime license for $29">
  Buy Now
</button>

<!-- Image alt text -->
<img
  src="signature-demo.gif"
  alt="Animation showing signature extraction from document"
/>

<!-- Skip to content link -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

---

## Asset Requirements

### Image Specifications

| Asset Type          | Format  | Dimensions | Size Limit  |
| ------------------- | ------- | ---------- | ----------- |
| Hero Background     | WebP    | 1920x1080  | <500KB      |
| App Screenshots     | WebP    | 1200x800   | <300KB each |
| Before/After Images | WebP    | 800x600    | <200KB each |
| Icons               | SVG     | Scalable   | <5KB each   |
| Demo GIF            | GIF/MP4 | 800x600    | <2MB        |

### Video Specifications

| Video Type   | Format  | Dimensions | Duration   | Size Limit |
| ------------ | ------- | ---------- | ---------- | ---------- |
| Demo Video   | MP4     | 1280x720   | 45 seconds | <10MB      |
| Workflow GIF | GIF/MP4 | 800x600    | 15 seconds | <5MB       |

---

_This document will be updated as the design evolves and new components are added._
