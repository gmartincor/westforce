# SEO & Google Ads Implementation Guide

## Overview

This implementation provides comprehensive SEO optimization, Google Analytics 4 (GA4), Google Tag Manager (GTM), and Google Ads conversion tracking for the Westforce landing page.

## Features Implemented

### 1. **Google Analytics 4 (GA4)**
- Full GA4 integration with gtag.js
- Page view tracking
- Event tracking for user interactions
- Scroll depth tracking (25%, 50%, 75%, 100%)

### 2. **Google Tag Manager (GTM)**
- Centralized tag management
- NoScript fallback for better coverage
- Easy integration with additional marketing tools

### 3. **Google Ads Conversion Tracking**
- Phone click conversions
- Email click conversions
- Quote request conversions
- Configurable conversion labels per action

### 4. **SEO Optimization**
- Semantic HTML5 structure
- Meta tags (title, description, keywords)
- Open Graph tags for social sharing
- Twitter Card tags
- Canonical URLs
- robots.txt with dynamic sitemap reference
- XML sitemap (Django sitemaps)
- Structured data (Schema.org JSON-LD) for MovingCompany
- Responsive meta viewport
- PWA manifest.json

### 5. **Performance Optimization**
- Preconnect to external resources
- DNS prefetching
- Minified CSS
- Optimized font loading
- Lazy loading ready structure

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
GOOGLE_TAG_MANAGER_ID=GTM-XXXXXXX
GOOGLE_ADS_ID=AW-XXXXXXXXXX
GOOGLE_ADS_CONVERSION_ID=AW-XXXXXXXXXX
GOOGLE_ADS_PHONE_CONVERSION_LABEL=XXXX-XXXX
GOOGLE_ADS_EMAIL_CONVERSION_LABEL=XXXX-XXXX
GOOGLE_ADS_QUOTE_CONVERSION_LABEL=XXXX-XXXX
COMPANY_NAME=Westforce Moving Company
COMPANY_TAGLINE=Professional Australian Moving Company Management System
```

### Docker Environment

The `docker-compose.yml` file has been updated to pass all tracking configuration to the container. Environment variables are automatically available in both development and production.

## File Structure

```
templates/
├── components/
│   ├── analytics/
│   │   ├── gtag.html                    # Google Analytics & Ads tracking
│   │   ├── gtm.html                     # Google Tag Manager head script
│   │   ├── gtm_noscript.html           # GTM noscript fallback
│   │   ├── schema.html                  # Schema.org structured data
│   │   └── conversion_events.html       # Conversion tracking functions
│   └── seo/
│       └── meta.html                    # SEO meta tags
└── landing/
    └── index.html                       # Optimized landing page

apps/core/
├── context_processors.py                # Analytics context processor
├── sitemaps.py                         # Sitemap configuration
└── views/
    ├── landing.py                       # Landing page view
    └── seo.py                          # robots.txt view

static/
├── css/
│   └── landing.min.css                 # Minified landing page styles
├── manifest.json                        # PWA manifest
└── robots.txt                          # Static robots.txt

config/
├── settings/
│   └── base.py                         # Settings with analytics config
└── urls.py                             # URL configuration with sitemap
```

## Usage

### Setting Up Google Analytics

1. Create a GA4 property in Google Analytics
2. Get your Measurement ID (format: G-XXXXXXXXXX)
3. Add to `.env`: `GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX`

### Setting Up Google Tag Manager

1. Create a GTM container
2. Get your Container ID (format: GTM-XXXXXXX)
3. Add to `.env`: `GOOGLE_TAG_MANAGER_ID=GTM-XXXXXXX`
4. Configure tags in GTM dashboard

### Setting Up Google Ads Conversions

1. Create conversion actions in Google Ads:
   - Phone Call (Event: phone_click)
   - Email Click (Event: email_click)
   - Quote Request (Event: quote_request)

2. Get conversion IDs and labels
3. Add to `.env`:
```bash
GOOGLE_ADS_ID=AW-XXXXXXXXXX
GOOGLE_ADS_CONVERSION_ID=AW-XXXXXXXXXX
GOOGLE_ADS_PHONE_CONVERSION_LABEL=XXXX-XXXX
GOOGLE_ADS_EMAIL_CONVERSION_LABEL=XXXX-XXXX
GOOGLE_ADS_QUOTE_CONVERSION_LABEL=XXXX-XXXX
```

### Testing Conversions

Use Google Tag Assistant or Google Ads conversion tracking tag to verify:

1. **Phone Click Conversion**
   - Click "Call Us Today" button
   - Should fire: `phone_click` event and conversion

2. **Email Click Conversion**
   - Click "Get Quote" button
   - Should fire: `email_click` event and conversion

3. **Scroll Tracking**
   - Scroll down the page
   - Should fire scroll events at 25%, 50%, 75%, 100%

## Modular Architecture

### DRY Principle
- Reusable template components in `templates/components/`
- Single source of truth for analytics configuration
- Centralized context processor for settings

### SOLID Principles
- **Single Responsibility**: Each component has one purpose
- **Open/Closed**: Easy to extend with new tracking without modifying existing code
- **Liskov Substitution**: Components can be swapped with alternatives
- **Interface Segregation**: Minimal, focused includes
- **Dependency Inversion**: Depends on configuration, not hardcoded values

### KISS & YAGNI
- Simple, straightforward implementation
- Only necessary features implemented
- No over-engineering

## SEO Best Practices

### On-Page SEO
✅ Semantic HTML5 elements (`<header>`, `<main>`, `<section>`, `<article>`, `<footer>`)
✅ Proper heading hierarchy (H1 → H2 → H3)
✅ Descriptive meta tags
✅ Alt text ready structure
✅ Canonical URLs
✅ Mobile-first responsive design

### Technical SEO
✅ robots.txt
✅ XML sitemap
✅ Structured data (Schema.org)
✅ Page speed optimizations
✅ HTTPS ready
✅ Mobile-friendly

### Off-Page SEO
✅ Open Graph for social sharing
✅ Twitter Cards
✅ Rich snippets via structured data

## Performance Metrics

### Core Web Vitals Optimization
- **LCP (Largest Contentful Paint)**: Optimized with font preloading and minified CSS
- **FID (First Input Delay)**: Minimal blocking JavaScript
- **CLS (Cumulative Layout Shift)**: Stable layout with defined dimensions

### Loading Optimizations
- Preconnect to Google Fonts and GTM
- DNS prefetch for Analytics
- Minified CSS (landing.min.css)
- Lazy loading ready

## Monitoring & Analytics

### Key Metrics to Track
1. **Traffic Sources**: Organic, Paid, Direct, Referral
2. **User Behavior**: Scroll depth, time on page, bounce rate
3. **Conversions**: Phone clicks, email clicks, quote requests
4. **Page Performance**: Load time, Core Web Vitals

### Google Ads Optimization
1. Monitor conversion rates by campaign
2. Track cost per conversion
3. Optimize for phone call conversions (highest intent)
4. A/B test ad copy and landing page elements

## Production Deployment

### Checklist
- [ ] Set all environment variables in production
- [ ] Verify GTM container is published
- [ ] Confirm GA4 is receiving data
- [ ] Test all conversion tracking
- [ ] Submit sitemap to Google Search Console
- [ ] Verify robots.txt is accessible
- [ ] Enable HTTPS
- [ ] Set up Google Ads campaigns
- [ ] Configure conversion goals in Google Ads

### Docker Production

```bash
docker-compose up -d
```

All environment variables are automatically passed from `.env` to the container.

## Troubleshooting

### Analytics Not Loading
1. Check environment variables are set
2. Verify IDs format (GA4: G-XXXXXXXXXX, GTM: GTM-XXXXXXX)
3. Check browser console for errors
4. Use Google Tag Assistant Chrome extension

### Conversions Not Tracking
1. Verify conversion labels match Google Ads
2. Check onclick handlers are firing
3. Use Google Ads conversion tracking tag
4. Ensure gtag.js is loaded before conversion scripts

### SEO Issues
1. Verify robots.txt is accessible at `/robots.txt`
2. Check sitemap at `/sitemap.xml`
3. Validate structured data with Google's Rich Results Test
4. Use Google Search Console for indexing issues

## Maintenance

### Regular Tasks
- Monitor GA4 for traffic anomalies
- Review conversion rates weekly
- Update meta descriptions seasonally
- Keep structured data current
- Monitor Core Web Vitals in Search Console

### Scaling
The modular structure allows easy addition of:
- Additional conversion events
- New landing pages
- A/B testing frameworks
- Advanced tracking (heatmaps, session recording)
- Marketing automation integrations

## Support

For issues or questions about this implementation:
1. Check environment variables configuration
2. Review Django logs for template errors
3. Use browser DevTools Network tab for tracking verification
4. Consult Google Analytics and Google Ads documentation
