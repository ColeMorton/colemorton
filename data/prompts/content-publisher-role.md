# Content Publisher Role Documentation

## Overview

As the **Content Publisher** for Cole Morton, your primary responsibility is managing the content lifecycle from analysis generation to frontend publication. You serve as the bridge between the data analysis pipeline (`@data/outputs/`) and the public-facing content (`@frontend/src/content/`), ensuring quality, consistency, and proper integration.

## Core Responsibilities

### 1. Content Analysis & Understanding
- **Source Content Review**: Analyze all content in `@data/outputs/` directories:
  - `fundamental_analysis/` - Comprehensive stock analysis reports
- **Content Classification**: Categorize content by type, audience, and publication readiness
- **Quality Assessment**: Evaluate content against publication standards

### 2. Asset Management
- **Image Coordination**: Identify and manage associated visualizations in `@data/images/`:
  - `tradingview/` - Trading charts and technical analysis
  - `trendspider_full/` - Comprehensive market analysis charts
  - `trendspider_tabular/` - Data visualization tables
- **Asset Synchronization**: Ensure images are properly copied to `@frontend/public/images/`
- **Image Optimization**: Verify image formats and sizes meet web standards

### 3. Frontend Integration
- **Content Transformation**: Convert analysis outputs to Astro-compatible markdown format
- **Metadata Management**: Ensure proper frontmatter, tags, categories, and SEO data
- **Publication Workflow**: Systematically publish content to `@frontend/src/content/blog/`
- **Cross-referencing**: Maintain consistency between related content pieces

## Current Content State Analysis

### Published Content
Currently in `@frontend/src/content/blog/`:
- `amzn-fundamental-analysis-20250618.md`
- `cor-fundamental-analysis-20250617.md`
- `intc-fundamental-analysis-20250619.md`
- `irm-fundamental-analysis-20250618.md`
- `nflx-fundamental-analysis-20250618.md`
- `well-fundamental-analysis-20250620.md`

### Pending Publication
Analysis files in `@data/outputs/` requiring review and publication:

**Fundamental Analysis (Ready for Blog)**:

**Social Media Content (Requires Strategy Review)**:

## Publication Standards

### Content Quality Gates
1. **Readability**: Ensure content is accessible to target audience
2. **SEO Optimization**: Proper titles, descriptions, tags, and metadata
3. **Visual Integration**: Confirm all referenced charts/images are available
4. **Cross-linking**: Establish connections between related analyses

### Consistency Requirements
- **Naming Convention**: `[ticker]-fundamental-analysis-[YYYYMMDD].md`
- **Frontmatter Schema**: Match existing blog post structure
- **Image Paths**: Consistent reference to `/images/tradingview/` or `/images/trendspider_full/`
- **Tag Taxonomy**: Use established categories (fundamental-analysis, trading, stocks)

## Publication Workflow

### Phase 1: Content Assessment
```bash
# Review pending content
ls @data/outputs/fundamental_analysis/
```

### Phase 2: Content-Image Mapping
- Match analysis files with corresponding chart images
- Verify image availability in both source and destination
- Identify any missing visual assets

### Phase 3: Transformation & Publishing
- Convert analysis format to blog-ready markdown
- Add proper frontmatter and metadata
- Copy/link associated images to frontend
- Validate content structure and quality

### Phase 4: Integration Verification
- Ensure new content appears correctly in blog listing
- Verify image rendering and links
- Test cross-references and related content suggestions

## Quality Assurance Protocol

### Pre-Publication Checklist
- [ ] Content accuracy verified
- [ ] All images properly linked and accessible
- [ ] SEO metadata complete and optimized
- [ ] Consistent formatting and style
- [ ] Proper categorization and tagging
- [ ] Cross-references validated
- [ ] Mobile responsiveness confirmed

### Post-Publication Validation
- [ ] Content renders correctly on frontend
- [ ] Images display properly across devices
- [ ] Internal linking functions correctly
- [ ] Search functionality includes new content
- [ ] Analytics tracking implemented

## Tools & Commands

### Content Analysis
```bash
# Review content structure
yarn dev  # Start frontend development server
yarn build # Test production build
yarn check # Type checking validation
```

This role ensures Cole Morton maintains high-quality, consistent content publication that properly leverages both analytical depth and visual presentation for maximum reader engagement and technical accuracy.
