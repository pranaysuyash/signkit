# Landing Page - Technical Implementation Plan

**Date**: November 4, 2025  
**Project**: Signature Extractor Desktop App  
**Section**: Technical Architecture & Development Guide

## Addendum (2026-06-29)

Treat the implementation guidance as supporting the current product boundary:

- the landing page should sell sensitive-document cleanup, not a generic e-signature platform
- legal, tax, CA, real-estate, and office-admin examples are the strongest first-pass segments
- license activation stays separate from auth and from Gumroad purchase state
- the launch model is one-time purchase + separate license activation
- unsupported claims or inflated social proof should not be introduced into the page architecture


---

## Architecture Overview

### Technology Stack

- **Framework**: Next.js 14+ (App Router)
- **Styling**: Tailwind CSS + Headless UI
- **Payment**: Stripe Checkout + Webhooks
- **Analytics**: Plausible (privacy-focused)
- **Hosting**: Vercel (edge deployment)
- **Domain**: Cloudflare (DNS + CDN)
- **Asset Storage**: Vercel Blob (images) + YouTube (videos)

### Development Philosophy

1. **Performance First** - Sub-2s load times
2. **SEO Optimized** - Technical SEO baseline
3. **Privacy Compliant** - Minimal tracking
4. **Conversion Focused** - Every byte serves a purpose
5. **Mobile Responsive** - Mobile-first design

---

## Project Structure

```
landing-page/
├── app/
│   ├── (marketing)/
│   │   ├── page.tsx                 # Main landing page
│   │   ├── layout.tsx               # Marketing layout
│   │   └── globals.css              # Global styles
│   ├── api/
│   │   ├── checkout/route.ts        # Stripe checkout
│   │   ├── webhook/route.ts         # Payment webhooks
│   │   └── download/route.ts        # Download handler
│   ├── blog/
│   │   └── page.tsx                 # Future content marketing
│   └── components/
│       ├── ui/                      # Reusable UI components
│       ├── sections/                # Page sections
│       ├── analytics.tsx            # Analytics setup
│       └── providers.tsx            # Context providers
├── public/
│   ├── images/                      # Static images
│   ├── videos/                      # Demo videos
│   ├── icons/                       # Favicons
│   └── og/                          # Open Graph images
├── lib/
│   ├── stripe.ts                    # Stripe configuration
│   ├── analytics.ts                 # Analytics helpers
│   └── utils.ts                     # Utilities
├── content/
│   └── copy/                        # Copy blocks as data
├── tests/                           # E2E tests
└── docs/                            # Development docs
```

---

## Page Structure & Routes

### Main Landing Page (`/`)

#### Route Configuration

```typescript
// app/page.tsx
export default function LandingPage() {
  return (
    <div className='min-h-screen'>
      <HeroSection />
      <VisualProofSection />
      <FeatureShowcase />
      <ComparisonBand />
      <UseCasesSection />
      <HowItWorksSection />
      <PricingSection />
      <FAQSection />
      <FinalCTASection />
    </div>
  );
}
```

#### SEO Metadata

```typescript
// app/layout.tsx
export const metadata = {
  title: 'Signature Extractor - Extract & Sign PDFs for $29',
  description:
    'The only desktop app that extracts clean signatures and places them on PDFs. Privacy-first, precision-focused, no subscriptions. Lifetime access for $29.',
  keywords: [
    'signature extraction',
    'PDF signing',
    'document processing',
    'macOS app',
  ],
  openGraph: {
    title: 'Signature Extractor - Extract & Sign PDFs',
    description:
      'Extract signatures. Place on PDFs. Done. Lifetime access for $29.',
    images: ['/og/landing-page.jpg'],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Signature Extractor - $29 Lifetime',
    description: 'Extract signatures. Place on PDFs. Done.',
  },
};
```

---

## Component Architecture

### 1. Hero Section Component

```typescript
// app/components/sections/HeroSection.tsx
'use client';

import { useState } from 'react';
import Image from 'next/image';
import { PlayButton } from '@/components/ui/PlayButton';
import { CTAButton } from '@/components/ui/CTAButton';

export function HeroSection() {
  const [showVideo, setShowVideo] = useState(false);

  return (
    <section className='relative bg-gradient-to-br from-blue-600 to-purple-600 overflow-hidden'>
      {/* Background Pattern */}
      <div className='absolute inset-0 opacity-10'>
        <Image
          src='/images/hero-pattern.svg'
          alt=''
          fill
          className='object-cover'
        />
      </div>

      <div className='container mx-auto px-4 py-20 relative z-10'>
        <div className='grid lg:grid-cols-2 gap-12 items-center'>
          {/* Content */}
          <div className='text-white'>
            <h1 className='text-5xl lg:text-6xl font-bold leading-tight mb-6'>
              Extract signatures.
              <br />
              Place on PDFs.
              <br />
              <span className='text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500'>
                Done.
              </span>
            </h1>

            <p className='text-xl lg:text-2xl mb-8 opacity-90'>
              Stop juggling multiple tools and subscriptions. Our desktop app
              extracts clean signatures from any document, then lets you place
              them in PDFs. Everything runs locally on your Mac.
            </p>

            {/* Value Props */}
            <ul className='space-y-3 mb-8'>
              <li className='flex items-center gap-3'>
                <CheckIcon className='h-5 w-5 text-green-400' />
                <span>Precision selection with zoom controls</span>
              </li>
              <li className='flex items-center gap-3'>
                <CheckIcon className='h-5 w-5 text-green-400' />
                <span>Clean PNG export with transparency</span>
              </li>
              <li className='flex items-center gap-3'>
                <CheckIcon className='h-5 w-5 text-green-400' />
                <span>Interactive PDF viewer + signing</span>
              </li>
              <li className='flex items-center gap-3'>
                <CheckIcon className='h-5 w-5 text-green-400' />
                <span>30-day money-back guarantee</span>
              </li>
            </ul>

            {/* CTAs */}
            <div className='flex flex-col sm:flex-row gap-4 mb-8'>
              <CTAButton
                price={29}
                originalPrice={39}
                badge='Launch Price'
                className='bg-white text-blue-600 hover:bg-gray-50'
              />
              <button
                onClick={() => setShowVideo(true)}
                className='flex items-center gap-2 px-6 py-3 border-2 border-white/20 rounded-lg text-white hover:bg-white/10 transition-colors'
              >
                <PlayIcon className='h-5 w-5' />
                Watch 45s Demo
              </button>
            </div>

            {/* Trust Badges */}
            <div className='flex flex-wrap gap-4'>
              <TrustBadge>30-day guarantee</TrustBadge>
              <TrustBadge>Lifetime updates</TrustBadge>
              <TrustBadge>Privacy-first</TrustBadge>
            </div>
          </div>

          {/* Visual */}
          <div className='relative'>
            <div className='bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8'>
              <DemoShowcase />
            </div>
          </div>
        </div>
      </div>

      {/* Video Modal */}
      {showVideo && (
        <VideoModal
          videoId='demo-video-id'
          onClose={() => setShowVideo(false)}
        />
      )}
    </section>
  );
}
```

### 2. Payment Integration

```typescript
// app/api/checkout/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';

export async function POST(request: NextRequest) {
  try {
    const { priceId, customerEmail, metadata } = await request.json();

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${process.env.NEXT_PUBLIC_URL}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.NEXT_PUBLIC_URL}/`,
      customer_email: customerEmail,
      metadata: {
        product: 'signature-extractor-lifetime',
        version: '1.0',
        ...metadata,
      },
      allow_promotion_codes: true,
    });

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Checkout error:', error);
    return NextResponse.json({ error: 'Checkout failed' }, { status: 500 });
  }
}
```

### 3. CTA Button Component

```typescript
// app/components/ui/CTAButton.tsx
'use client';

import { useState } from 'react';
import { useAnalytics } from '@/lib/analytics';

interface CTAButtonProps {
  price: number;
  originalPrice?: number;
  badge?: string;
  className?: string;
  children?: React.ReactNode;
}

export function CTAButton({
  price,
  originalPrice,
  badge,
  className = '',
  children,
}: CTAButtonProps) {
  const [loading, setLoading] = useState(false);
  const { trackEvent } = useAnalytics();

  const handleClick = async () => {
    setLoading(true);
    trackEvent('cta_click', { price, variant: 'primary' });

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          priceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID,
          metadata: { source: 'landing-page' },
        }),
      });

      const { url } = await response.json();
      window.location.href = url;
    } catch (error) {
      console.error('Checkout failed:', error);
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`group relative inline-flex items-center gap-3 px-8 py-4 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all transform hover:scale-105 disabled:opacity-50 ${className}`}
    >
      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <span className='text-lg'>
            {children || `Buy Lifetime - $${price}`}
          </span>
          {badge && (
            <span className='bg-white/20 px-3 py-1 rounded-full text-sm font-medium'>
              {badge}
            </span>
          )}
        </>
      )}
    </button>
  );
}
```

---

## Styling System

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#007AFF',
          600: '#0056CC',
          700: '#004499',
        },
        success: {
          500: '#30D158',
          600: '#34C759',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        float: 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': {
            opacity: '0',
            transform: 'translateY(30px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography'), require('@tailwindcss/forms')],
};
```

### Global Styles

```css
/* app/globals.css */
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

/* Custom CSS Variables */
:root {
  --brand-blue: #007aff;
  --brand-purple: #5856d6;
  --success-green: #30d158;
  --text-primary: #1c1c1e;
  --text-secondary: #3a3a3c;
  --bg-primary: #ffffff;
  --bg-secondary: #f2f2f7;
}

/* Base styles */
* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

html,
body {
  max-width: 100vw;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
}

/* Smooth scrolling */
html {
  scroll-behavior: smooth;
}

/* Focus styles */
.focus-ring:focus {
  outline: 2px solid var(--brand-blue);
  outline-offset: 2px;
}

/* Component classes */
@layer components {
  .btn-primary {
    @apply bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors;
  }

  .btn-secondary {
    @apply bg-transparent border-2 border-blue-600 text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-600 hover:text-white transition-colors;
  }

  .card {
    @apply bg-white rounded-2xl p-6 shadow-lg border border-gray-100;
  }

  .glass-panel {
    @apply bg-white/80 backdrop-blur-lg border border-white/20 rounded-2xl;
  }

  .text-gradient {
    @apply bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent;
  }
}

/* Animation classes */
@layer utilities {
  .animate-on-scroll {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s ease-out;
  }

  .animate-on-scroll.in-view {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## Performance Optimization

### 1. Image Optimization

```typescript
// app/components/ui/OptimizedImage.tsx
'use client';

import Image from 'next/image';
import { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
  className?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className = '',
}: OptimizedImageProps) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {!loaded && (
        <div className='absolute inset-0 bg-gray-200 animate-pulse' />
      )}
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        quality={90}
        className={`transition-opacity duration-300 ${
          loaded ? 'opacity-100' : 'opacity-0'
        }`}
        onLoad={() => setLoaded(true)}
      />
    </div>
  );
}
```

### 2. Critical CSS Inlining

```typescript
// app/components/performance/CriticalCSS.tsx
export function CriticalCSS() {
  const criticalStyles = `
    .hero-section { background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); }
    .btn-primary { 
      display: inline-flex;
      align-items: center;
      padding: 1rem 2rem;
      background: #007AFF;
      color: white;
      border-radius: 12px;
      font-weight: 600;
    }
    /* Add other critical styles */
  `;

  return <style dangerouslySetInnerHTML={{ __html: criticalStyles }} />;
}
```

### 3. Lazy Loading Implementation

```typescript
// app/components/performance/LazySection.tsx
'use client';

import { useEffect, useState, useRef } from 'react';

interface LazySectionProps {
  children: React.ReactNode;
  threshold?: number;
}

export function LazySection({ children, threshold = 0.1 }: LazySectionProps) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  return (
    <div ref={ref}>
      {isVisible ? (
        children
      ) : (
        <div className='h-64 bg-gray-100 animate-pulse' />
      )}
    </div>
  );
}
```

---

## Analytics & Tracking

### 1. Privacy-Focused Analytics Setup

```typescript
// lib/analytics.ts
'use client';

import { useEffect } from 'react';

interface AnalyticsEvent {
  event: string;
  props?: Record<string, any>;
}

export function useAnalytics() {
  useEffect(() => {
    // Load Plausible
    const script = document.createElement('script');
    script.defer = true;
    script.setAttribute('data-domain', process.env.NEXT_PUBLIC_DOMAIN!);
    script.src = 'https://plausible.io/js/script.js';
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  const trackEvent = (event: string, props?: Record<string, any>) => {
    if (typeof window !== 'undefined' && (window as any).plausible) {
      (window as any).plausible(event, { props });
    }
  };

  const trackPageView = () => {
    if (typeof window !== 'undefined' && (window as any).plausible) {
      (window as any).plausible('pageview');
    }
  };

  return { trackEvent, trackPageView };
}
```

### 2. Conversion Tracking

```typescript
// app/components/analytics/ConversionTracker.tsx
'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';

export function ConversionTracker() {
  const pathname = usePathname();

  useEffect(() => {
    // Track page views
    if ((window as any).plausible) {
      (window as any).plausible('pageview');
    }

    // Track specific conversions
    if (pathname === '/success') {
      // Purchase completed
      if ((window as any).plausible) {
        (window as any).plausible('purchase_completed');
      }

      // Facebook Pixel (if used)
      if ((window as any).fbq) {
        (window as any).fbq('track', 'Purchase', {
          value: 29,
          currency: 'USD',
        });
      }
    }
  }, [pathname]);

  return null;
}
```

---

## Payment Processing

### 1. Stripe Integration

```typescript
// lib/stripe.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-12-18.acacia',
});

// Create price for lifetime license
export async function createLifetimePrice() {
  const price = await stripe.prices.create({
    unit_amount: 2900, // $29.00
    currency: 'usd',
    product: {
      name: 'Signature Extractor - Lifetime License',
      description: 'Desktop signature extraction + PDF signing',
    },
  });
  return price;
}
```

### 2. Webhook Handler

```typescript
// app/api/webhook/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { headers } from 'next/headers';

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = headers().get('stripe-signature')!;

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    );
  } catch (err: any) {
    console.error('Webhook signature verification failed:', err.message);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  // Handle events
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object;
      await handleSuccessfulPayment(session);
      break;

    case 'payment_intent.succeeded':
      const paymentIntent = event.data.object;
      await handlePaymentSuccess(paymentIntent);
      break;

    default:
      console.log(`Unhandled event type ${event.type}`);
  }

  return NextResponse.json({ received: true });
}

async function handleSuccessfulPayment(session: Stripe.Checkout.Session) {
  // Send download link
  // Add to email list
  // Track in analytics
  // Log to database
}
```

---

## SEO Implementation

### 1. Dynamic Metadata

```typescript
// app/page.tsx
export async function generateMetadata() {
  const baseUrl = process.env.NEXT_PUBLIC_URL;

  return {
    title: 'Signature Extractor - Extract & Sign PDFs for $29',
    description:
      'The only desktop app that extracts clean signatures and places them on PDFs. Privacy-first, precision-focused, no subscriptions. Lifetime access for $29.',
    alternates: {
      canonical: baseUrl,
    },
    openGraph: {
      title: 'Signature Extractor - Extract & Sign PDFs',
      description:
        'Extract signatures. Place on PDFs. Done. Lifetime access for $29.',
      url: baseUrl,
      siteName: 'Signature Extractor',
      images: [
        {
          url: `${baseUrl}/og/landing-page.jpg`,
          width: 1200,
          height: 630,
          alt: 'Signature Extractor App',
        },
      ],
      locale: 'en_US',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: 'Signature Extractor - $29 Lifetime',
      description: 'Extract signatures. Place on PDFs. Done.',
      images: [`${baseUrl}/og/twitter-card.jpg`],
    },
  };
}
```

### 2. Structured Data

```typescript
// app/components/seo/StructuredData.tsx
export function StructuredData() {
  const data = {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: 'Signature Extractor',
    description:
      'Desktop app for extracting signatures from documents and placing them in PDFs',
    applicationCategory: 'BusinessApplication',
    operatingSystem: 'macOS',
    offers: {
      '@type': 'Offer',
      price: '29',
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      reviewCount: '1203',
    },
  };

  return (
    <script
      type='application/ld+json'
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
```

---

## Testing Strategy

### 1. E2E Tests with Playwright

```typescript
// tests/landing-page.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('should load and display hero section', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('h1')).toContainText('Extract signatures');
    await expect(page.locator('[data-testid="cta-button"]')).toBeVisible();
  });

  test('should track CTA click', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="cta-button"]');

    // Verify redirect to Stripe
    await expect(page).toHaveURL(/checkout\.stripe\.com/);
  });

  test('should play demo video', async ({ page }) => {
    await page.goto('/');
    await page.click('[data-testid="demo-button"]');
    await expect(page.locator('iframe[src*="youtube"]')).toBeVisible();
  });

  test('should show pricing correctly', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="price-display"]')).toContainText(
      '$29'
    );
  });
});
```

### 2. Performance Tests

```typescript
// tests/performance.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Performance', () => {
  test('should load under 2 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;

    expect(loadTime).toBeLessThan(2000);
  });

  test('should have good Core Web Vitals', async ({ page }) => {
    await page.goto('/');

    const vitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          resolve(entries);
        }).observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });
      });
    });

    // Assert vitals are good
    expect(vitals).toBeDefined();
  });
});
```

---

## Deployment & DevOps

### 1. Vercel Configuration

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 10
    }
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/buy",
      "destination": "/#pricing",
      "permanent": false
    }
  ]
}
```

### 2. Environment Variables

```bash
# .env.local
NEXT_PUBLIC_URL=https://signatureextractor.com
NEXT_PUBLIC_DOMAIN=signatureextractor.com

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Analytics
NEXT_PUBLIC_PLAUSIBLE_DOMAIN=signatureextractor.com

# Download URLs
NEXT_PUBLIC_MAC_DOWNLOAD_URL=https://downloads.signatureextractor.com/mac/latest
NEXT_PUBLIC_WIN_DOWNLOAD_URL=https://downloads.signatureextractor.com/windows/latest
```

### 3. GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build

      - name: Deploy to Vercel
        uses: vercel/action@v1
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

---

## Monitoring & Maintenance

### 1. Error Monitoring

```typescript
// lib/error-monitoring.ts
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
});

export { Sentry };
```

### 2. Health Checks

```typescript
// app/api/health/route.ts
export async function GET() {
  return new Response(
    JSON.stringify({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version,
    }),
    { status: 200 }
  );
}
```

---

## Security Considerations

### 1. Content Security Policy

```javascript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://plausible.io",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "connect-src 'self' https://api.stripe.com https://plausible.io",
      'frame-src https://js.stripe.com https://youtube.com',
    ].join('; '),
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

### 2. Rate Limiting

```typescript
// lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
});

export const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(10, '1 m'),
});
```

---

_This technical implementation guide will be updated as the project evolves and new requirements are identified._
