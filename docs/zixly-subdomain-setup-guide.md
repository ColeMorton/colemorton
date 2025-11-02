# Zixly Subdomain Setup Guide

**Complete guide for connecting your Zixly SaaS platform to your main website using a custom subdomain**

---

## 📋 Overview

This guide will walk you through setting up `zixly.colemorton.com` to point to your Vercel-hosted SaaS application, while maintaining your main website on Netlify.

### Architecture
- **Main Website**: `www.colemorton.com` (Astro on Netlify)
- **SaaS Platform**: `zixly.colemorton.com` (Hosted on Vercel)
- **DNS Provider**: Namecheap
- **Domain**: `colemorton.com`

### Benefits
✅ Professional branding under one domain
✅ Independent hosting leverages both Vercel and Netlify strengths
✅ Automatic SSL certificates on both platforms
✅ Optimal SEO for both properties
✅ Clear separation of concerns
✅ Easy to maintain and scale independently

---

## 🚀 Step 1: Vercel Domain Configuration (5 minutes)

### 1.1 Access Your Vercel Project

1. Log into [Vercel Dashboard](https://vercel.com/dashboard)
2. Navigate to your Zixly project
3. Click on **Settings** in the top navigation
4. Select **Domains** from the left sidebar

### 1.2 Add Custom Domain

1. In the "Add Domain" input field, enter:
   ```
   zixly.colemorton.com
   ```

2. Click **Add** button

3. Vercel will detect that you need to configure DNS and show you one of these options:

   **Option A: CNAME Record** (Recommended - easier to manage)
   ```
   Type: CNAME
   Name: zixly
   Value: cname.vercel-dns.com
   TTL: 3600 (or Automatic)
   ```

   **Option B: A Record** (If CNAME doesn't work)
   ```
   Type: A
   Name: zixly
   Value: 76.76.21.21
   TTL: 3600 (or Automatic)
   ```

4. **Keep this tab open** - you'll need these values for Namecheap

### 1.3 Note Your Configuration

Write down or screenshot the exact DNS records Vercel provides. The IP address or CNAME target may vary.

---

## 🌐 Step 2: Namecheap DNS Configuration (10 minutes)

### 2.1 Access Namecheap Dashboard

1. Log into [Namecheap](https://www.namecheap.com/)
2. Click **Domain List** in the left sidebar
3. Find `colemorton.com` and click **Manage**

### 2.2 Navigate to Advanced DNS

1. Click the **Advanced DNS** tab at the top
2. You'll see your current DNS records

### 2.3 Add CNAME Record for Zixly

**If using CNAME (Recommended):**

1. Click **Add New Record** button
2. Configure the new record:
   - **Type**: Select `CNAME Record` from dropdown
   - **Host**: Enter `zixly`
   - **Value**: Enter `cname.vercel-dns.com` (or the value Vercel provided)
   - **TTL**: Select `Automatic` or `1 hour`
3. Click the **✓** (checkmark) to save

**If using A Record:**

1. Click **Add New Record** button
2. Configure the new record:
   - **Type**: Select `A Record` from dropdown
   - **Host**: Enter `zixly`
   - **Value**: Enter the IP address Vercel provided (e.g., `76.76.21.21`)
   - **TTL**: Select `Automatic` or `1 hour`
3. Click the **✓** (checkmark) to save

### 2.4 Verify the Record

After saving, you should see your new record in the list:
```
CNAME Record    zixly    cname.vercel-dns.com    Automatic
```

### 2.5 DNS Propagation Time

⏱️ **Expected time**: 5 minutes to 1 hour (usually under 15 minutes for Namecheap)
🌍 **Maximum time**: Up to 48 hours globally

**How to check DNS propagation:**

```bash
# Check if DNS has propagated
nslookup zixly.colemorton.com

# Or use online tools
# Visit: https://dnschecker.org
# Enter: zixly.colemorton.com
```

---

## 🔒 Step 3: SSL Certificate Verification (Automatic)

### 3.1 Wait for DNS Propagation

Once DNS propagates, Vercel automatically provisions an SSL certificate using Let's Encrypt.

### 3.2 Check Certificate Status

1. Return to **Vercel Dashboard** → Your Project → **Settings** → **Domains**
2. Find `zixly.colemorton.com` in the domain list
3. Status should show:
   - ⏳ **Pending** - DNS not propagated yet
   - ✅ **Valid** - DNS configured and SSL active
   - ❌ **Invalid Configuration** - Check DNS settings

### 3.3 Test Your Domain

Once status shows **Valid**:

```bash
# Test HTTPS access
curl -I https://zixly.colemorton.com

# Should return: HTTP/2 200
```

Or simply visit in browser: `https://zixly.colemorton.com`

### 3.4 Troubleshooting SSL Issues

If SSL doesn't provision after 1 hour:

1. **Verify DNS**: Ensure CNAME/A record is correct in Namecheap
2. **Check Nameservers**: Ensure domain is using Namecheap nameservers
3. **Remove and Re-add**: In Vercel, remove the domain and add it again
4. **Contact Support**: Reach out to Vercel support if issues persist

---

## 🎨 Step 4: Update Main Website Navigation

### 4.1 Add Zixly to Main Navigation Menu

**File**: `frontend/src/config/menu.json`

Add Zixly to your main navigation array:

```json
{
  "main": [
    {
      "name": "Home",
      "url": "/"
    },
    {
      "name": "About",
      "url": "/about"
    },
    {
      "name": "Zixly",
      "url": "https://zixly.colemorton.com",
      "external": true
    },
    {
      "name": "Contact",
      "url": "/contact"
    },
    {
      "name": "Blog",
      "url": "/blog"
    },
    {
      "name": "Analysis",
      "url": "/categories/analysis"
    },
    {
      "name": "Charts",
      "url": "/charts"
    },
    {
      "name": "Elements",
      "url": "/elements"
    },
    {
      "name": "Pages",
      "url": "",
      "hasChildren": true,
      "children": [
        {
          "name": "Calculators",
          "url": "/calculators"
        },
        {
          "name": "Categories",
          "url": "/categories"
        },
        {
          "name": "Tags",
          "url": "/tags"
        }
      ]
    }
  ],
  "footer": [
    {
      "name": "Zixly",
      "url": "https://zixly.colemorton.com"
    },
    {
      "name": "Elements",
      "url": "/elements"
    },
    {
      "name": "Privacy Policy",
      "url": "/privacy-policy"
    }
  ]
}
```

### 4.2 Update Navigation Component TypeScript Interface

**File**: `frontend/src/layouts/partials/Header.astro`

Update the `NavigationLink` interface (around line 8-19):

```typescript
export interface ChildNavigationLink {
  name: string;
  url: string;
  external?: boolean;  // Add this optional property
}

export interface NavigationLink {
  name: string;
  url: string;
  external?: boolean;  // Add this optional property
  hasChildren?: boolean;
  children?: ChildNavigationLink[];
}
```

### 4.3 Update Link Rendering to Support External Links

**File**: `frontend/src/layouts/partials/Header.astro`

Find the main navigation link rendering (around line 131-142) and update:

```astro
<li
  class={`nav-item ${
    index === 4
      ? "hidden xl:block"
      : index >= 5
        ? "hidden 2xl:block"
        : ""
  }`}
>
  <a
    href={item.url}
    data-astro-reload={item.url === "/charts" ? true : undefined}
    target={item.external ? "_blank" : undefined}
    rel={item.external ? "noopener noreferrer" : undefined}
    class={`nav-link block cursor-pointer whitespace-nowrap ${
      (pathname === `${item.url}/` || pathname === item.url) &&
      "active"
    } ${item.external ? "flex items-center gap-1" : ""}`}
  >
    {item.name}
    {item.external && (
      <svg
        class="h-3 w-3 ml-1 inline-block"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
        />
      </svg>
    )}
  </a>
</li>
```

Also update the dropdown items rendering (around line 171-189):

```astro
{
  responsiveMenus.lg.overflowItems.map((item) => (
    <li>
      <a
        href={item.url}
        data-astro-reload={item.url === "/charts" ? true : undefined}
        target={item.external ? "_blank" : undefined}
        rel={item.external ? "noopener noreferrer" : undefined}
        class={`nav-dropdown-link block ${
          (pathname === item.url || pathname === `${item.url}/`) && "active"
        } ${item.external ? "flex items-center gap-1" : ""}`}
      >
        {item.name}
        {item.external && (
          <svg class="h-3 w-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        )}
      </a>
    </li>
  ))
}
```

### 4.4 Optional: Update Navigation Button (Hero CTA)

**File**: `frontend/src/config/config.json`

Replace or update the navigation button to promote Zixly:

```json
{
  "navigation_button": {
    "enable": true,
    "label": "Launch Zixly",
    "link": "https://zixly.colemorton.com"
  }
}
```

---

## 📄 Step 5: Create a Zixly Landing Page (Optional)

Create an informational page about Zixly on your main site at `/zixly`.

**File**: `frontend/src/pages/zixly.astro`

```astro
---
import Base from "@/layouts/Base.astro";
import { Image } from "astro:assets";
---

<Base
  title="Zixly - Business Intelligence Platform"
  meta_title="Zixly - Business Intelligence for Australian SMEs"
  description="Premium Business Intelligence for Australian SMEs. Save $53,500 annually with automated reporting and real-time insights."
  image="/images/zixly-og-image.png"
>
  <section class="section-sm pb-0">
    <div class="container">
      <div class="row justify-center">
        <div class="text-center lg:col-10">
          <h1 class="mb-6">
            Transform Your Business Intelligence
          </h1>
          <p class="mb-8 text-lg">
            Zixly helps Australian SMEs save thousands of hours and dollars
            on disconnected data. From 10 hours of manual reporting to 30 minutes
            of automated insights.
          </p>

          <div class="mb-8 flex flex-wrap justify-center gap-4">
            <a
              href="https://zixly.colemorton.com"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-primary"
            >
              Launch Dashboard
            </a>
            <a
              href="https://zixly.colemorton.com#demo"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-outline-primary"
            >
              Book a Demo
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="row justify-center">
        <div class="lg:col-10">
          <div class="mb-12 text-center">
            <h2 class="mb-4">The Hidden Cost of Manual Reporting</h2>
            <p class="text-lg">Australian SMEs waste thousands of hours and dollars on disconnected data</p>
          </div>

          <div class="mb-16 grid gap-6 md:grid-cols-4">
            <div class="rounded-lg border border-border p-6 text-center dark:border-darkmode-border">
              <div class="mb-2 text-4xl font-bold text-dark dark:text-darkmode-light">10 hrs</div>
              <div class="text-sm">Weekly manual reporting</div>
            </div>
            <div class="rounded-lg border border-border p-6 text-center dark:border-darkmode-border">
              <div class="mb-2 text-4xl font-bold text-dark dark:text-darkmode-light">$39,000</div>
              <div class="text-sm">Annual labor cost</div>
            </div>
            <div class="rounded-lg border border-border p-6 text-center dark:border-darkmode-border">
              <div class="mb-2 text-4xl font-bold text-dark dark:text-darkmode-light">$8,000</div>
              <div class="text-sm">Data entry errors</div>
            </div>
            <div class="rounded-lg border border-border p-6 text-center dark:border-darkmode-border">
              <div class="mb-2 text-4xl font-bold text-dark dark:text-darkmode-light">2-3 weeks</div>
              <div class="text-sm">Decision delays</div>
            </div>
          </div>

          <div class="mb-12 text-center">
            <h2 class="mb-4">Your Business Intelligence, Automated</h2>
            <p class="text-lg">One unified dashboard. Zero manual work. Enterprise-grade insights at SME pricing.</p>
          </div>

          <div class="mb-16 grid gap-8 md:grid-cols-3">
            <div class="rounded-lg border border-border p-8 dark:border-darkmode-border">
              <h3 class="mb-3 text-h5">Automated Data Consolidation</h3>
              <p>Connects to Xero, HubSpot, Asana, and 50+ Australian business tools. Data syncs automatically, no manual entry required.</p>
            </div>
            <div class="rounded-lg border border-border p-8 dark:border-darkmode-border">
              <h3 class="mb-3 text-h5">Custom KPI Tracking</h3>
              <p>Bespoke visualizations designed for your industry. Track the metrics that matter to YOUR business, not generic templates.</p>
            </div>
            <div class="rounded-lg border border-border p-8 dark:border-darkmode-border">
              <h3 class="mb-3 text-h5">Real-Time Insights</h3>
              <p>Updated daily via automated ETL pipelines. See cash flow, sales pipeline, and operational efficiency in real-time.</p>
            </div>
          </div>

          <div class="mb-12 text-center">
            <h2 class="mb-8">Built for Australian Industries</h2>
          </div>

          <div class="mb-16 grid gap-8 md:grid-cols-3">
            <div class="rounded-lg bg-theme-light p-6 dark:bg-darkmode-theme-light">
              <h3 class="mb-3 text-h5">Professional Services</h3>
              <ul class="space-y-2">
                <li>• Matter profitability tracking</li>
                <li>• Utilization rates analysis</li>
                <li>• Client lifetime value metrics</li>
              </ul>
            </div>
            <div class="rounded-lg bg-theme-light p-6 dark:bg-darkmode-theme-light">
              <h3 class="mb-3 text-h5">Construction & Trades</h3>
              <ul class="space-y-2">
                <li>• Job costing and materials tracking</li>
                <li>• Equipment utilization monitoring</li>
                <li>• Quote-to-completion cycle time</li>
              </ul>
            </div>
            <div class="rounded-lg bg-theme-light p-6 dark:bg-darkmode-theme-light">
              <h3 class="mb-3 text-h5">E-Commerce & Retail</h3>
              <ul class="space-y-2">
                <li>• Inventory turnover analysis</li>
                <li>• Cart abandonment tracking</li>
                <li>• Product margin analysis</li>
              </ul>
            </div>
          </div>

          <div class="mb-16 grid gap-6 md:grid-cols-3">
            <div class="text-center">
              <div class="mb-2 text-5xl font-bold text-primary">297%</div>
              <div class="text-sm font-medium">ROI in Year 1</div>
            </div>
            <div class="text-center">
              <div class="mb-2 text-5xl font-bold text-primary">94%</div>
              <div class="text-sm font-medium">Reduction in reporting time</div>
            </div>
            <div class="text-center">
              <div class="mb-2 text-5xl font-bold text-primary">3 weeks</div>
              <div class="text-sm font-medium">To production dashboard</div>
            </div>
          </div>

          <div class="mb-12 text-center">
            <h2 class="mb-8">Enterprise-Grade Technology</h2>
            <p class="mb-8 text-lg">Built with the same technology that powers Spotify, Netflix, and enterprise data warehouses</p>
          </div>

          <div class="mb-16 grid gap-6 md:grid-cols-4">
            <div class="text-center">
              <div class="mb-3 text-3xl">🇦🇺</div>
              <h3 class="mb-2 text-h6">Australian Data Residency</h3>
              <p class="text-sm">Data stored in Sydney region, never leaves Australia</p>
            </div>
            <div class="text-center">
              <div class="mb-3 text-3xl">🔒</div>
              <h3 class="mb-2 text-h6">Bank-Grade Security</h3>
              <p class="text-sm">AES-256 encryption, OAuth 2.0 authentication</p>
            </div>
            <div class="text-center">
              <div class="mb-3 text-3xl">⚡</div>
              <h3 class="mb-2 text-h6">99.9% Uptime SLA</h3>
              <p class="text-sm">Automated backups, disaster recovery tested quarterly</p>
            </div>
            <div class="text-center">
              <div class="mb-3 text-3xl">✅</div>
              <h3 class="mb-2 text-h6">Privacy Act Compliant</h3>
              <p class="text-sm">Full compliance with Australian Privacy Act 1988</p>
            </div>
          </div>

          <div class="text-center">
            <h2 class="mb-4">Ready to Transform Your Business Intelligence?</h2>
            <p class="mb-8 text-lg">
              Join Australian SMEs saving $53,500+ annually with automated reporting.
              From 10 hours of manual work to 30 minutes of insights.
            </p>
            <a
              href="https://zixly.colemorton.com"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-primary btn-lg"
            >
              Book Your Demo Today
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>
</Base>
```

This creates a beautiful landing page at `www.colemorton.com/zixly` that explains the product before redirecting users to the actual app.

---

## ✅ Step 6: Testing Checklist

### 6.1 DNS Resolution

```bash
# Test DNS propagation
nslookup zixly.colemorton.com

# Should return Vercel's IP address
# Example output:
# Server:  dns.google
# Address:  8.8.8.8
#
# Non-authoritative answer:
# Name:    zixly.colemorton.com
# Address:  76.76.21.21
```

### 6.2 HTTPS Verification

```bash
# Test SSL certificate
curl -I https://zixly.colemorton.com

# Should return HTTP/2 200 OK
```

### 6.3 Manual Browser Tests

- [ ] Visit `https://zixly.colemorton.com` - loads correctly
- [ ] SSL certificate is valid (look for padlock icon)
- [ ] No mixed content warnings in browser console
- [ ] Navigation link from main site works
- [ ] External link icon displays correctly
- [ ] Links open in new tab (`target="_blank"`)
- [ ] Mobile responsive on both sites
- [ ] Footer link works

### 6.4 Cross-Browser Testing

Test on:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### 6.5 Performance Testing

```bash
# Check page load time
curl -w "@curl-format.txt" -o /dev/null -s https://zixly.colemorton.com

# Use online tools:
# - PageSpeed Insights: https://pagespeed.web.dev/
# - GTmetrix: https://gtmetrix.com/
```

---

## 🔧 Step 7: Deploy Changes to Netlify

### 7.1 Commit Changes

```bash
# From your project root
cd /Users/colemorton/Projects/colemorton

# Check what files changed
git status

# Stage navigation config changes
git add frontend/src/config/menu.json
git add frontend/src/layouts/partials/Header.astro

# If you created the landing page
git add frontend/src/pages/zixly.astro

# Commit with descriptive message
git commit -m "feat: Add Zixly navigation and external link support"
```

### 7.2 Push to Git

```bash
# Push to your staging branch for testing
git push origin staging

# Once tested, merge to production
git checkout main
git merge staging
git push origin main
```

### 7.3 Verify Netlify Deployment

1. Go to [Netlify Dashboard](https://app.netlify.com/)
2. Find your site
3. Check **Deploys** tab
4. Wait for deploy to complete (usually 2-5 minutes)
5. Click **Preview** to test before going live

### 7.4 Production Verification

Once deployed:
- Visit `www.colemorton.com`
- Check navigation includes "Zixly" link
- Click link to verify it opens `zixly.colemorton.com` in new tab
- Check footer link as well

---

## 🌐 Step 8: SEO & Meta Configuration

### 8.1 Update Zixly Meta Tags

In your Zixly project on Vercel, ensure proper meta tags:

```html
<!-- In your Zixly index.html or layout -->
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- SEO Meta Tags -->
  <title>Zixly - Business Intelligence for Australian SMEs</title>
  <meta name="description" content="Premium Business Intelligence for Australian SMEs. Save $53,500 annually with automated reporting and real-time insights.">
  <link rel="canonical" href="https://zixly.colemorton.com" />

  <!-- Open Graph Meta Tags -->
  <meta property="og:title" content="Zixly - Business Intelligence Platform">
  <meta property="og:description" content="Premium Business Intelligence for Australian SMEs. Save $53,500 annually.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://zixly.colemorton.com">
  <meta property="og:image" content="https://zixly.colemorton.com/og-image.png">

  <!-- Twitter Card Meta Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Zixly - Business Intelligence Platform">
  <meta name="twitter:description" content="Premium Business Intelligence for Australian SMEs.">
  <meta name="twitter:image" content="https://zixly.colemorton.com/og-image.png">
</head>
```

### 8.2 Add Internal Linking

Create blog posts or analysis pages that mention Zixly:

```markdown
---
title: "How I Built a SaaS BI Platform for Australian SMEs"
description: "Behind the scenes of building Zixly..."
---

After working with numerous Australian SMEs, I built [Zixly](https://zixly.colemorton.com)
to solve their business intelligence challenges...
```

### 8.3 Create a Sitemap Entry

Ensure your Zixly landing page is in the sitemap. Astro should handle this automatically with the sitemap integration, but verify:

Visit: `https://www.colemorton.com/sitemap-0.xml`

Should include:
```xml
<url>
  <loc>https://www.colemorton.com/zixly</loc>
  <lastmod>2025-01-15</lastmod>
</url>
```

---

## 📊 Step 9: Analytics Setup (Optional)

### 9.1 Google Analytics Cross-Domain Tracking

If using Google Analytics, set up cross-domain tracking:

**In your main site (Netlify):**
```javascript
// In your GA initialization
gtag('config', 'GA_MEASUREMENT_ID', {
  'linker': {
    'domains': ['colemorton.com', 'zixly.colemorton.com']
  }
});
```

**In Zixly (Vercel):**
```javascript
// Same configuration
gtag('config', 'GA_MEASUREMENT_ID', {
  'linker': {
    'domains': ['colemorton.com', 'zixly.colemorton.com']
  }
});
```

### 9.2 Track External Link Clicks

Add event tracking to your Zixly navigation link:

```astro
<a
  href={item.url}
  target={item.external ? "_blank" : undefined}
  rel={item.external ? "noopener noreferrer" : undefined}
  onclick={item.external ? `gtag('event', 'click', {'event_category': 'External Link', 'event_label': '${item.name}', 'value': '${item.url}'})` : undefined}
  class="nav-link"
>
  {item.name}
</a>
```

---

## 🚨 Troubleshooting

### Issue: DNS Not Resolving

**Symptoms:** `zixly.colemorton.com` doesn't resolve or shows an error

**Solutions:**
1. Wait longer (DNS can take up to 48 hours, though usually < 1 hour)
2. Clear your DNS cache:
   ```bash
   # macOS
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

   # Windows
   ipconfig /flushdns

   # Linux
   sudo systemd-resolve --flush-caches
   ```
3. Check Namecheap nameservers:
   - Go to Domain List → Manage → Domain tab
   - Ensure using Namecheap BasicDNS or PremiumDNS
4. Verify CNAME record in Advanced DNS tab
5. Use online DNS checker: https://dnschecker.org

### Issue: SSL Certificate Not Provisioning

**Symptoms:** "Not Secure" or certificate errors

**Solutions:**
1. Wait for DNS to fully propagate first
2. In Vercel, remove domain and re-add it
3. Check CAA records in Namecheap (shouldn't block Let's Encrypt)
4. Contact Vercel support with domain details

### Issue: Site Shows Vercel 404 Page

**Symptoms:** Domain resolves but shows "404 - This page could not be found"

**Solutions:**
1. Check Vercel project is deployed and live
2. Verify domain is added to correct Vercel project
3. Check build logs in Vercel dashboard
4. Ensure Vercel project has an index.html or configured routing

### Issue: CORS Errors

**Symptoms:** Console errors about Cross-Origin Resource Sharing

**Solutions:**
Add CORS headers in Vercel configuration:

**File:** `vercel.json` (in Zixly project root)
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://www.colemorton.com"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        }
      ]
    }
  ]
}
```

### Issue: Navigation Link Not Working

**Symptoms:** Clicking Zixly link doesn't work or gives errors

**Solutions:**
1. Check for typos in `menu.json`
2. Ensure proper JSON syntax (commas, quotes)
3. Clear browser cache
4. Check browser console for JavaScript errors
5. Verify Header.astro changes were deployed
6. Test in incognito/private browsing mode

### Issue: External Link Icon Not Showing

**Symptoms:** Link works but no external link indicator

**Solutions:**
1. Verify SVG code is correct in Header.astro
2. Check CSS isn't hiding it
3. Inspect element in browser DevTools
4. Ensure `item.external` is true in menu.json
5. Clear browser cache and hard refresh

---

## 📋 Quick Reference

### DNS Records Summary

| Record Type | Host | Value | TTL |
|-------------|------|-------|-----|
| CNAME | `zixly` | `cname.vercel-dns.com` | Automatic |

### URL Structure

| Purpose | URL |
|---------|-----|
| Main Website | `https://www.colemorton.com` |
| Zixly SaaS App | `https://zixly.colemorton.com` |
| Zixly Landing Page | `https://www.colemorton.com/zixly` |

### Important Files Modified

| File | Purpose | Changes |
|------|---------|---------|
| `frontend/src/config/menu.json` | Navigation menu | Add Zixly links |
| `frontend/src/layouts/partials/Header.astro` | Header component | External link support |
| `frontend/src/pages/zixly.astro` | Landing page | New file (optional) |
| `frontend/src/config/config.json` | CTA button | Update button (optional) |

### Command Cheat Sheet

```bash
# Check DNS resolution
nslookup zixly.colemorton.com

# Check online DNS propagation
# Visit: https://dnschecker.org/?hostname=zixly.colemorton.com

# Test HTTPS
curl -I https://zixly.colemorton.com

# Flush local DNS cache (macOS)
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

# Git workflow
git add frontend/src/config/menu.json frontend/src/layouts/partials/Header.astro
git commit -m "feat: Add Zixly navigation"
git push origin staging

# Check Astro build
cd frontend
npm run build
```

---

## 🎯 Success Checklist

Once everything is complete, you should have:

- ✅ DNS CNAME record in Namecheap pointing `zixly` to Vercel
- ✅ Vercel shows domain as "Valid" with active SSL
- ✅ `https://zixly.colemorton.com` loads your SaaS app
- ✅ Zixly appears in main navigation on www.colemorton.com
- ✅ Navigation link opens in new tab with external icon
- ✅ Zixly appears in footer
- ✅ Optional landing page at `/zixly` provides info
- ✅ All changes committed and deployed to Netlify
- ✅ No console errors on either site
- ✅ Mobile responsive on both sites
- ✅ SSL valid on both domains

---

## 🔗 Useful Links

### Tools & Services
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Netlify Dashboard**: https://app.netlify.com/
- **Namecheap Dashboard**: https://www.namecheap.com/
- **DNS Checker**: https://dnschecker.org/
- **SSL Checker**: https://www.sslshopper.com/ssl-checker.html
- **PageSpeed Insights**: https://pagespeed.web.dev/

### Documentation
- **Vercel Custom Domains**: https://vercel.com/docs/concepts/projects/custom-domains
- **Namecheap DNS Management**: https://www.namecheap.com/support/knowledgebase/article.aspx/767/10/how-to-change-dns-for-a-domain/
- **Astro Configuration**: https://docs.astro.build/en/reference/configuration-reference/
- **Netlify Deployment**: https://docs.netlify.com/site-deploys/overview/

---

## 📝 Maintenance Notes

### Regular Tasks

**Monthly:**
- Check SSL certificate renewal (automatic but verify)
- Review Vercel and Netlify analytics
- Test both domains for uptime
- Check for broken links

**Quarterly:**
- Review DNS settings for any needed updates
- Check page load performance
- Update meta descriptions/SEO if needed
- Review Google Analytics data

**When Needed:**
- Update navigation labels if rebranding
- Add new features to landing page
- Create blog posts mentioning Zixly
- Update screenshots/images on landing page

### Future Enhancements

Consider adding:
- [ ] Customer testimonials on landing page
- [ ] Pricing page integration
- [ ] Blog posts about features
- [ ] Video demos embedded on landing page
- [ ] Live chat integration across both domains
- [ ] Newsletter signup form
- [ ] Social media integration
- [ ] Case studies page

---

## 📞 Support

If you encounter issues:

1. **Vercel Issues**: https://vercel.com/support
2. **Netlify Issues**: https://www.netlify.com/support/
3. **Namecheap Support**: https://www.namecheap.com/support/
4. **DNS Propagation**: Usually resolves with time (max 48 hours)
5. **Code Issues**: Check git commits and revert if needed

---

**Last Updated**: January 2025
**Version**: 1.0
**Author**: Cole Morton
**Project**: Zixly SaaS Integration

---

*This guide assumes you have administrative access to Vercel, Netlify, and Namecheap accounts. Keep your login credentials secure and use 2FA where available.*
