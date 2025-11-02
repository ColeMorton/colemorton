# Astro Blog Post Frontmatter Guide

A comprehensive guide to the YAML frontmatter structure used in Cole Morton's Astro blog system, located in `frontend/src/content/blog/`.

## What is Frontmatter?

Frontmatter is the YAML metadata block at the top of each Markdown blog post, enclosed by triple dashes (`---`). It defines the post's metadata, publication settings, and content categorization for Astro's content collection system.

## Core Frontmatter Fields

### Required Fields

#### `title` (string)
- **Purpose**: Main heading displayed on the post and in listings
- **Best Practice**: Be descriptive and include key identifiers (e.g., stock tickers)
- **Examples**:
  ```yaml
  title: "ASML Holding N.V. (ASML) - Fundamental Analysis"
  title: "Historical Trading Performance - Closed Positions Analysis"
  ```

#### `description` (string)
- **Purpose**: SEO meta description and post summary in listings
- **Best Practice**: 150-160 characters, comprehensive summary with key metrics
- **Example**:
  ```yaml
  description: "Comprehensive fundamental analysis of ASML with investment thesis, competitive position assessment, and valuation analysis"
  ```

#### `date` (string)
- **Purpose**: Publication date for sorting and display
- **Formats**: ISO 8601 with or without timezone
- **Examples**:
  ```yaml
  date: 2025-06-24T10:00:00Z    # With timezone
  date: 2025-07-02T00:00:00Z    # UTC format
  date: 2025-06-26              # Date only
  ```

#### `draft` (boolean)
- **Purpose**: Controls publication status
- **Values**: `true` (hidden) or `false` (published)
- **Example**:
  ```yaml
  draft: false  # Published
  draft: true   # Hidden from production
  ```

### Content Organization

#### `categories` (array)
- **Purpose**: Broad content classification for navigation
- **Structure**: Array of strings
- **Common Categories**:
  ```yaml
  categories: ["Analysis", "Fundamental Analysis", "Technology"]
  categories: ["Trading", "Analysis", "Fundamental Analysis", "Stocks"]
  categories: ["Technical Analysis", "Equity Strategies"]
  ```

#### `tags` (array)
- **Purpose**: Specific keywords for detailed categorization and search
- **Format**: Lowercase with hyphens
- **Examples**:
  ```yaml
  tags: ["asml", "semiconductor", "fundamental-analysis", "stocks"]
  tags: ["moving-average", "crossover", "aapl", "technical-analysis"]
  ```

### Visual Content

#### `image` (string)
- **Purpose**: Featured image path for social sharing and post headers
- **Pattern**: Always starts with `/images/`
- **Examples**:
  ```yaml
  image: "/images/tradingview/ASML_20250624.png"
  image: "/images/crypto_kangaroo_ledger.png"
  ```

### Optional Fields

#### `meta_title` (string)
- **Purpose**: SEO-specific title (differs from display title)
- **Usage**: Can be empty string or omitted
- **Example**:
  ```yaml
  meta_title: "ASML Fundamental Analysis - Investment Thesis & Valuation"
  meta_title: ""  # Empty but present
  ```

#### Author Attribution

**Two formats supported:**

**Single Author (legacy):**
```yaml
author: "Cole Morton"
```

**Multiple Authors (preferred):**
```yaml
authors: ["Cole Morton"]
authors:
  - Cole Morton
```

## Content Type Patterns

### Fundamental Analysis Posts
```yaml
---
title: "[Company] ([TICKER]) - Fundamental Analysis"
description: "Comprehensive fundamental analysis of [TICKER] with investment thesis, competitive position assessment, and valuation analysis"
date: 2025-07-02T00:00:00Z
image: "/images/tradingview/[TICKER]_[YYYYMMDD].png"
categories: ["Trading", "Analysis", "Fundamental Analysis", "Stocks"]
tags: ["[ticker-lowercase]", "[sector]", "fundamental-analysis", "stock-analysis"]
draft: false
---
```

### Technical Analysis Posts
```yaml
---
title: "[Strategy Name] for [TICKER]"
description: "Technical analysis of [strategy] applied to [company] with backtesting and implementation"
date: 2025-07-02T00:00:00Z
image: "/images/analysis/[descriptor].png"
categories: ["Technical Analysis", "Equity Strategies"]
tags: ["[strategy-name]", "[ticker-lowercase]", "technical-analysis"]
draft: false
---
```

### Performance Reports
```yaml
---
title: "[Report Type] - [Time Period]"
description: "Performance analysis showing key metrics and insights for optimization"
date: 2025-07-02
categories: ["trading-performance", "analysis"]
tags: ["performance-metrics", "trade-analysis", "signals"]
image: "/images/tradingview/[REPORT_TYPE]_[YYYYMMDD].png"
authors: ["Cole Morton"]
draft: false
---
```

## Best Practices

### Naming Conventions
- **Files**: `[ticker]-fundamental-analysis-[YYYYMMDD].md`
- **Tags**: Lowercase with hyphens
- **Categories**: Title Case, descriptive
- **Images**: Match date patterns with content

### SEO Optimization
- **Title**: Include primary keywords and identifiers
- **Description**: 150-160 characters with key metrics
- **Meta_title**: Use when different from display title
- **Tags**: Include primary keyword variations

### Content Management
- **Dates**: Use consistent timezone (UTC preferred)
- **Draft Status**: Set `true` for work-in-progress
- **Images**: Ensure paths exist in `/images/` directory
- **Authors**: Use array format for consistency

### Quality Checklist
✅ Title includes primary subject identifier  
✅ Description under 160 characters  
✅ Date in ISO format  
✅ Categories match existing taxonomy  
✅ Tags in lowercase-hyphen format  
✅ Image path exists and follows naming convention  
✅ Draft status set appropriately  
✅ Authors field uses array format  

## Common Issues & Solutions

**Issue**: Post doesn't appear in production  
**Solution**: Check `draft: false` and valid date format

**Issue**: Image not displaying  
**Solution**: Verify image exists at exact path in `/images/`

**Issue**: Inconsistent categorization  
**Solution**: Review existing posts for category patterns

**Issue**: SEO issues  
**Solution**: Ensure description length and meta_title optimization

This frontmatter system provides flexible content management while maintaining consistency across Cole Morton's financial analysis blog platform.

## Integration with Content Publisher Command

The `content_publisher.md` command has been updated to enforce these standardization rules automatically. All fundamental analysis posts are now required to follow the **Fundamental Analysis Standard Template** with mandatory compliance validation.

### Automated Enforcement

The content publisher command includes:
- **FRONTMATTER COMPLIANCE VALIDATION**: 9-point checklist ensuring template adherence
- **AUTOMATIC REJECTION**: Non-compliant posts are rejected until corrected
- **STANDARDIZATION ENFORCEMENT**: Automatic verification and correction of frontmatter issues

This ensures 100% consistency across all fundamental analysis publications while maintaining analytical integrity and improving SEO performance.