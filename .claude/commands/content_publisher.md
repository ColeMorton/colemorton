# Content Publisher

**Command Classification**: 📊 **Core Product Command**
**Knowledge Domain**: `content-publication-workflow`
**Ecosystem Version**: `2.1.0` *(Last Updated: 2025-07-18)*
**Outputs To**: `frontend/src/content/blog/`

## Script Integration Mapping

**Primary Script**: `{SCRIPTS_BASE}/content_publishing/content_publisher_script.py`
**Script Class**: `ContentPublisherScript`
**Registry Name**: `content_publisher`
**Content Types**: `["blog_publication", "asset_coordination", "comparative_analysis"]`
**Requires Validation**: `true`
**Implementation**: Publisher sub-agent with content publication specialization

**Registry Decorator**:
```python
@twitter_script(
    name="content_publisher",
    content_types=["blog_publication", "asset_coordination", "comparative_analysis"],
    requires_validation=True
)
class ContentPublisherScript(BaseScript):
    """Transform analytical insights into publication-ready blog content with absolute content fidelity"""
```

**Additional Scripts** (multi-phase workflow):
```yaml
discovery_script:
  path: "{SCRIPTS_BASE}/content_publishing/content_discovery.py"
  class: "ContentDiscoveryScript"
  phase: "Phase 1 - Content Discovery & Assessment"

asset_script:
  path: "{SCRIPTS_BASE}/content_publishing/asset_coordinator.py"
  class: "AssetCoordinatorScript"
  phase: "Phase 2 - Asset Management & Synchronization"

transformation_script:
  path: "{SCRIPTS_BASE}/content_publishing/content_transformer.py"
  class: "ContentTransformerScript"
  phase: "Phase 3 - Content Transformation"

publication_script:
  path: "{SCRIPTS_BASE}/content_publishing/frontend_publisher.py"
  class: "FrontendPublisherScript"
  phase: "Phase 4 - Publication & Validation"

comparative_analysis_discovery_script:
  path: "{SCRIPTS_BASE}/comparative_analysis/comparative_discovery.py"
  class: "ComparativeDiscoveryScript"
  phase: "DASV Phase 1 - Comparative Discovery"

comparative_analysis_script:
  path: "{SCRIPTS_BASE}/comparative_analysis/comparative_analyzer.py"
  class: "ComparativeAnalyzerScript"
  phase: "DASV Phase 2 - Comparative Analysis"

comparative_synthesis_script:
  path: "{SCRIPTS_BASE}/comparative_analysis/comparative_synthesizer.py"
  class: "ComparativeSynthesizerScript"
  phase: "DASV Phase 3 - Comparative Synthesis"
```

## Purpose

You are the Content Publication Strategy Specialist, responsible for defining comprehensive content publication requirements for publisher-generated blog-ready content. This command implements content publication strategic requirements, focusing on content discovery specifications and publication quality standards while delegating implementation methodology to the publisher sub-agent.

### Content Fidelity Mandate

**CRITICAL**: This command defines content fidelity requirements for publisher implementation. All analytical content must preserve 100% accuracy without transformation, summarization, or editorial modification. The only permitted change is removing the H1 title heading to prevent duplication with frontmatter titles.

**Output Location**: Published content in `frontend/src/content/blog/` with supporting assets in `frontend/public/images/` (publisher-generated)

## Template Integration Architecture

**Template Directory**: `{TEMPLATES_BASE}/content_publishing/`

**Template Mappings**:
| Template ID | File Path | Selection Criteria | Purpose |
|------------|-----------|-------------------|---------|
| fundamental_analysis_blog | `publishing/fundamental_analysis_blog.j2` | Content type fundamental analysis | Investment research blog posts |
| trade_history_blog | `publishing/trade_history_blog.j2` | Content type trade history | Trading performance blog posts |
| sector_analysis_blog | `publishing/sector_analysis_blog.j2` | Content type sector analysis | Sector analysis blog posts |
| comparative_analysis_blog | `publishing/comparative_analysis_blog.j2` | Content type comparative analysis | Cross-stock comparative investment analysis |
| blog_frontmatter | `publishing/blog_frontmatter.j2` | All blog content | Standardized frontmatter generation |

**Shared Components**:
```yaml
frontmatter_base:
  path: "{TEMPLATES_BASE}/content_publishing/shared/frontmatter_base.j2"
  purpose: "Base frontmatter template with common metadata and SEO optimization"

content_fidelity:
  path: "{TEMPLATES_BASE}/content_publishing/shared/content_fidelity.j2"
  purpose: "Content preservation template ensuring 100% analytical integrity"

asset_integration:
  path: "{TEMPLATES_BASE}/content_publishing/shared/asset_integration.j2"
  purpose: "Asset coordination and image optimization templates"
```

**Template Selection Algorithm**:
```python
def select_publication_template(content_analysis):
    """Select optimal template for content publication"""

    # Fundamental analysis blog template
    if content_analysis.get('content_type') == 'fundamental_analysis':
        return 'publishing/fundamental_analysis_blog.j2'

    # Trade history blog template
    elif content_analysis.get('content_type') == 'trade_history':
        return 'publishing/trade_history_blog.j2'

    # Sector analysis blog template
    elif content_analysis.get('content_type') == 'sector_analysis':
        return 'publishing/sector_analysis_blog.j2'

    # Comparative analysis blog template
    elif content_analysis.get('content_type') == 'comparative_analysis':
        return 'publishing/comparative_analysis_blog.j2'

    # Default blog template
    return 'publishing/blog_frontmatter.j2'
```

## Content Publication Strategy Requirements

### Content Discovery Requirements
**Content Audit Specifications**:
- Multi-source content discovery across all analytical output directories
- Publication gap analysis comparing existing blog content against available outputs
- Content readiness assessment with quality standard evaluation
- Priority optimization based on relevance, timeliness, and audience value
- Cross-content type integration for unified discovery workflows

### Asset Coordination Requirements
**Asset Management Specifications**:
- Image discovery and mapping protocols for all visualization types
- Asset synchronization with frontend integration requirements
- Responsive optimization for web presentation standards
- Path validation with consistent naming convention enforcement
- Multi-type asset management across tradingview/, trendspider_full/, sector_analysis/, comparative_analysis/

### Content Transformation Standards
**Content Fidelity Requirements**:
- **ZERO TRANSFORMATION POLICY**: 100% preservation of analytical content
- **STRATEGIC H1 REMOVAL**: Remove only title heading to prevent frontmatter duplication
- **ANALYTICAL INTEGRITY**: Preserve all confidence scores, recommendations, financial data, methodology
- **FRONTMATTER STANDARDIZATION**: Apply content type-specific templates with proper metadata
- **QUALITY GATE ENFORCEMENT**: Fail-fast protocols for content modification attempts

### Publication Integration Standards
**Frontend Compatibility Requirements**:
- Astro framework compatibility with content collection standards
- Development server validation with rendering verification
- Cross-browser testing and mobile responsiveness
- SEO optimization with social sharing metadata
- Search functionality integration for content discoverability

## Publisher Integration Specifications

**Content Delegation Framework**:
- **Tool Integration**: Automated `content_publisher_script.py` execution via publisher sub-agent
- **Quality Enforcement**: Publisher implements ≥95% publication success rate with content fidelity validation
- **Professional Generation**: Publication-ready blog content with frontend integration specialization
- **Multi-Content Expertise**: Publisher handles all content types (fundamental, trade history, sector, comparative)

**Content Publication Enhancement Requirements**:
- **Content Discovery Implementation**: Publisher executes multi-source content discovery with gap analysis
- **Asset Coordination Implementation**: Publisher manages image optimization and frontend integration workflows
- **Content Fidelity Implementation**: Publisher enforces 100% content preservation with strategic H1 removal
- **Frontend Integration Implementation**: Publisher ensures Astro framework compatibility and validation protocols

**Quality Assurance Protocol**:
- **Methodology Compliance**: Publisher implements content publication standards and validation workflows
- **Asset Integration**: Publisher manages responsive optimization and web presentation requirements
- **Publication Logic Verification**: Publisher ensures content readiness and frontend compatibility
- **Professional Standards**: Publisher delivers publication-ready content with quality gate enforcement

**Content Authority Standards**:
- **Source Content Authority**: Data outputs maintain highest authority for analytical accuracy
- **Template Authority**: Frontmatter templates control metadata structure and standardization
- **Framework Authority**: Astro framework requirements govern final presentation compatibility
- **Conflict Resolution**: Publisher implements content precedence with fidelity preservation strategy

## Data Flow & File References

**Input Sources**:
```yaml
fundamental_analysis:
  path: "{DATA_OUTPUTS}/fundamental_analysis/{TICKER}_{YYYYMMDD}.md"
  format: "markdown"
  required: true
  description: "Fundamental analysis reports for publication"

trade_history:
  path: "{DATA_OUTPUTS}/trade_history/trading-performance-{TYPE}-{YYYYMMDD}.md"
  format: "markdown"
  required: false
  description: "Trade history reports for publication"

sector_analysis:
  path: "{DATA_OUTPUTS}/sector_analysis/{SECTOR}-sector-analysis-{YYYYMMDD}.md"
  format: "markdown"
  required: false
  description: "Sector analysis reports for publication"

comparative_analysis:
  path: "{DATA_OUTPUTS}/comparative_analysis/{TICKER_1}_vs_{TICKER_2}_{YYYYMMDD}.md"
  format: "markdown"
  required: false
  description: "Cross-stock comparative analysis reports for publication"

visual_assets:
  path: "{DATA_IMAGES}/{asset_type}/{IDENTIFIER}_{YYYYMMDD}.png"
  format: "png|jpg"
  required: false
  description: "Visual assets for content enhancement"
```

**Output Structure**:
```yaml
blog_content:
  path: "frontend/src/content/blog/{identifier}-{type}-{YYYYMMDD}.md"
  format: "markdown"
  description: "Published blog content with standardized frontmatter (includes comparative analysis: {ticker1}-vs-{ticker2}-comparative-analysis-{YYYYMMDD}.md)"

optimized_images:
  path: "frontend/public/images/{asset_type}/{IDENTIFIER}_{YYYYMMDD}.png"
  format: "png|jpg"
  description: "Optimized images for web presentation"

publication_metadata:
  path: "{DATA_OUTPUTS}/content_publication/{IDENTIFIER}_{YYYYMMDD}_metadata.json"
  format: "json"
  description: "Publication metadata and validation results"
```

## Parameters

### Core Parameters
- `content_type`: Content type to publish - `fundamental_analysis` | `trade_history` | `sector_analysis` | `comparative_analysis` | `all` (optional, default: all)
- `ticker`: Specific ticker to publish (optional)
- `priority`: Publication priority - `high` | `medium` | `low` (optional, default: medium)
- `mode`: Publication mode - `full` | `assets_only` | `validation_only` (optional, default: full)

### Advanced Parameters
- `scope`: Publication scope - `comprehensive` | `selective` | `targeted` (optional, default: comprehensive)
- `validation_level`: Validation depth - `basic` | `standard` | `comprehensive` (optional, default: standard)
- `asset_optimization`: Enable image optimization - `true` | `false` (optional, default: true)
- `frontend_validation`: Enable frontend rendering validation - `true` | `false` (optional, default: true)

### Workflow Parameters (Multi-Phase Commands)
- `phase_start`: Starting phase - `discovery` | `asset` | `transformation` | `publication` (optional)
- `phase_end`: Ending phase - `discovery` | `asset` | `transformation` | `publication` (optional)
- `continue_on_error`: Continue workflow despite errors - `true` | `false` (optional, default: false)
- `report_type`: Trade history report type - `historical` | `internal` | `live_signals` (optional)

## Fundamental Analysis Standard Template

### MANDATORY FRONTMATTER TEMPLATE

All fundamental analysis posts MUST use this exact template with NO deviations:

```yaml
---
title: "{Company Name} ({TICKER}) - Fundamental Analysis"
meta_title: "{Company Name} ({TICKER}) Fundamental Analysis - {RATING} Rating"
description: "Comprehensive fundamental analysis of {Company Name} ({TICKER}) with {RATING} recommendation. Fair value ${LOW}-${HIGH} vs current ${CURRENT}. {Brief investment thesis 1-2 sentences}."
date: {YYYY-MM-DD}T{HH:MM:SS}Z
image: "/images/tradingview/{TICKER}_{YYYYMMDD}.png"
authors: ["Cole Morton", "Claude"]
categories: ["Investing", "Analysis", "Fundamental Analysis", "{Sector}", "{Industry}"]
tags: ["{ticker-lowercase}", "fundamental-analysis", "{rating-lowercase}", "{sector-tag}", "{key-theme-1}", "{key-theme-2}"]
draft: false
---
```

### STRICT STANDARDIZATION RULES

#### Title Standards
- **Format**: `{Company Name} ({TICKER}) - Fundamental Analysis`
- **Remove**: ALL ratings, returns, and specific themes from title
- **Example**: `"Amazon.com Inc. (AMZN) - Fundamental Analysis"`

#### Meta_title Standards
- **Always include** for SEO optimization
- **Format**: `{Company Name} ({TICKER}) Fundamental Analysis - {RATING} Rating`
- **Example**: `"Amazon (AMZN) Fundamental Analysis - BUY Rating"`

#### Description Standards
- **Length**: 150-200 characters
- **Include**: Rating, fair value range, current price, key thesis
- **Template**: `"Comprehensive fundamental analysis of {Company} ({TICKER}) with {RATING} recommendation. Fair value ${LOW}-${HIGH} vs current ${CURRENT}. {Investment thesis}."`

#### Date Standards
- **Format**: ISO 8601 with timezone `YYYY-MM-DDTHH:MM:SSZ`
- **Example**: `2025-07-02T10:00:00Z`
- **Required**: Must include timezone Z suffix

#### Authors Standards
- **Field**: Use `authors` (NOT `author`)
- **Value**: `["Cole Morton", "Claude"]` (EXACT format)
- **Required**: Present in ALL posts

#### Categories Standards
- **Order**: `["Investing", "Analysis", "Fundamental Analysis", "{Sector}", "{Industry}"]`
- **Count**: Exactly 5 categories
- **Sectors**: Technology, Healthcare, Financial Services, Consumer Discretionary, Industrials, etc.
- **Industries**: Specific industry within sector

#### Tags Standards
- **Ticker**: ALWAYS lowercase (`amzn`, NOT `AMZN`)
- **Required**: `"fundamental-analysis"` in ALL posts
- **Rating**: Include rating tag (`"buy"`, `"hold"`, `"sell"`)
- **Count**: 5-7 tags maximum
- **Format**: Lowercase with hyphens

#### Image Standards
- **Path**: `/images/tradingview/{TICKER}_{YYYYMMDD}.png`
- **Ticker**: Uppercase in filename
- **Date**: Match publication date exactly

### STANDARDIZATION VALIDATION PROTOCOL

**MANDATORY PRE-PUBLICATION CHECKS**: Every fundamental analysis post MUST pass ALL validation checks before publication:

```
FRONTMATTER COMPLIANCE VALIDATION:
□ **TITLE FORMAT**: Exact format "{Company Name} ({TICKER}) - Fundamental Analysis"
□ **META_TITLE PRESENCE**: Must exist with rating information
□ **DESCRIPTION LENGTH**: 150-200 characters with required elements
□ **DATE FORMAT**: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)
□ **AUTHORS FORMAT**: Exact format ["Cole Morton", "Claude"]
□ **CATEGORIES STRUCTURE**: Exact format ["Investing", "Analysis", "Fundamental Analysis", "{Sector}", "{Industry}"]
□ **TAGS COMPLIANCE**: Lowercase ticker + "fundamental-analysis" + rating + themes
□ **IMAGE PATH**: Correct format with uppercase ticker and matching date
□ **DRAFT STATUS**: Set to false for publication
```

**AUTOMATIC REJECTION**: Any post that fails validation MUST be corrected before publication. No exceptions.

**STANDARDIZATION ENFORCEMENT**: The content_publisher command will automatically verify and correct any frontmatter issues to ensure 100% compliance with the standard template.

**CRITICAL COMPLIANCE NOTE**: All existing fundamental analysis posts have been standardized to this template. The content_publisher command MUST maintain this standardization for all future publications and validate existing content against these rules.

## Sector Analysis Standard Template

### MANDATORY FRONTMATTER TEMPLATE

All sector analysis posts MUST use this exact template with NO deviations:

```yaml
---
title: "{Sector Name} Sector Analysis - {Month} {YYYY}"
meta_title: "{Sector Name} Sector Analysis - {RECOMMENDATION} Rating | {Month} {YYYY}"
description: "Comprehensive {Sector Name} sector analysis with {RECOMMENDATION} recommendation. Fair value ${LOW}-${HIGH} with {CONFIDENCE}% confidence. {Brief sector thesis 1-2 sentences}."
date: {YYYY-MM-DD}T{HH:MM:SS}Z
image: "/images/sector_analysis/{sector-slug}_{YYYYMMDD}.png"
authors: ["Cole Morton", "Claude"]
categories: ["Investing", "Analysis", "Sector Analysis", "{Sector}", "Market Analysis"]
tags: ["{sector-slug}", "sector-analysis", "{recommendation-lowercase}", "{economic-indicator}", "{key-theme-1}", "{key-theme-2}"]
draft: false
sector_data:
  confidence: {0.XX}
  data_quality: {0.XX}
  economic_context: "{Current/Expansion/Contraction}"
  recommendation: "{BUY/HOLD/SELL}"
  position_size: "{XX-XX%}"
  fair_value_range: "${XX.XX} - ${XX.XX}"
  expected_return: "{XX.X%}"
  risk_score: "{X.X/5.0}"
---
```

### STRICT STANDARDIZATION RULES

#### Title Standards
- **Format**: `{Sector Name} Sector Analysis - {Month} {YYYY}`
- **Remove**: ALL specific ratings, returns, and complex themes from title
- **Example**: `"Technology Sector Analysis - July 2025"`

#### Meta_title Standards
- **Always include** for SEO optimization
- **Format**: `{Sector Name} Sector Analysis - {RECOMMENDATION} Rating | {Month} {YYYY}`
- **Example**: `"Technology Sector Analysis - BUY Rating | July 2025"`

#### Description Standards
- **Length**: 150-200 characters
- **Include**: Recommendation, fair value range, confidence level, key thesis
- **Template**: `"Comprehensive {Sector} sector analysis with {RECOMMENDATION} recommendation. Fair value ${LOW}-${HIGH} with {CONFIDENCE}% confidence. {Sector thesis}."`

#### Date Standards
- **Format**: ISO 8601 with timezone `YYYY-MM-DDTHH:MM:SSZ`
- **Example**: `2025-07-10T10:00:00Z`
- **Required**: Must include timezone Z suffix

#### Authors Standards
- **Field**: Use `authors` (NOT `author`)
- **Value**: `["Cole Morton", "Claude"]` (EXACT format)
- **Required**: Present in ALL posts

#### Categories Standards
- **Order**: `["Investing", "Analysis", "Sector Analysis", "{Sector}", "Market Analysis"]`
- **Count**: Exactly 5 categories
- **Sectors**: Technology, Healthcare, Finance, Energy, Consumer Discretionary, etc.
- **Required**: "Market Analysis" as 5th category

#### Tags Standards
- **Sector**: ALWAYS lowercase with hyphens (`technology`, `healthcare`, `finance`)
- **Required**: `"sector-analysis"` in ALL posts
- **Recommendation**: Include recommendation tag (`"buy"`, `"hold"`, `"sell"`)
- **Economic**: Include economic indicator tag (`"mid-cycle"`, `"expansion"`, `"contraction"`)
- **Count**: 5-7 tags maximum
- **Format**: Lowercase with hyphens

#### Image Standards
- **Path**: `/images/sector_analysis/{sector-slug}_{YYYYMMDD}.png`
- **Sector**: Lowercase with hyphens in filename
- **Date**: Match publication date exactly

#### Sector Data Standards
- **Confidence**: Decimal format (0.XX) matching source analysis
- **Data Quality**: Decimal format (0.XX) matching source analysis
- **Economic Context**: One of "Current", "Expansion", "Contraction"
- **Recommendation**: One of "BUY", "HOLD", "SELL"
- **Position Size**: Percentage range format "XX-XX%"
- **Fair Value Range**: Dollar range format "${XX.XX} - ${XX.XX}"
- **Expected Return**: Percentage format with decimal "XX.X%"
- **Risk Score**: Decimal format "X.X/5.0"

### STANDARDIZATION VALIDATION PROTOCOL

**MANDATORY PRE-PUBLICATION CHECKS**: Every sector analysis post MUST pass ALL validation checks before publication:

```
FRONTMATTER COMPLIANCE VALIDATION:
□ **TITLE FORMAT**: Exact format "{Sector Name} Sector Analysis - {Month} {YYYY}"
□ **META_TITLE PRESENCE**: Must exist with recommendation information
□ **DESCRIPTION LENGTH**: 150-200 characters with required elements
□ **DATE FORMAT**: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)
□ **AUTHORS FORMAT**: Exact format ["Cole Morton", "Claude"]
□ **CATEGORIES STRUCTURE**: Exact format ["Investing", "Analysis", "Sector Analysis", "{Sector}", "Market Analysis"]
□ **TAGS COMPLIANCE**: Lowercase sector + "sector-analysis" + recommendation + economic indicator + themes
□ **IMAGE PATH**: Correct format with lowercase sector slug and matching date
□ **SECTOR DATA STRUCTURE**: Complete sector_data object with all required fields
□ **CONFIDENCE SCORES**: Decimal format matching source analysis confidence and data quality
□ **ECONOMIC CONTEXT**: Valid economic context matching source analysis
□ **DRAFT STATUS**: Set to false for publication
```

**AUTOMATIC REJECTION**: Any post that fails validation MUST be corrected before publication. No exceptions.

**STANDARDIZATION ENFORCEMENT**: The content_publisher command will automatically verify and correct any frontmatter issues to ensure 100% compliance with the sector analysis standard template.

## Comparative Analysis Standard Template

### MANDATORY FRONTMATTER TEMPLATE

All comparative analysis posts MUST use this exact template with NO deviations:

```yaml
---
title: "{Company_1_Name} ({TICKER_1}) vs {Company_2_Name} ({TICKER_2}) - Comparative Investment Analysis"
meta_title: "{Company_1_Name} vs {Company_2_Name} Comparative Analysis - Investment Decision Framework"
description: "Institutional-quality comparative analysis of {Company_1_Name} ({TICKER_1}) vs {Company_2_Name} ({TICKER_2}) with cross-sector investment framework. {Primary_recommendation} vs {Secondary_recommendation} with {confidence}% confidence."
date: {YYYY-MM-DD}T{HH:MM:SS}Z
image: "/images/comparative_analysis/{TICKER_1}_vs_{TICKER_2}_{YYYYMMDD}.png"
authors: ["Cole Morton", "Claude"]
categories: ["Investing", "Analysis", "Comparative Analysis", "{Sector_1}", "{Sector_2}"]
tags: ["{ticker1-lowercase}", "{ticker2-lowercase}", "comparative-analysis", "{primary-recommendation-lowercase}", "{cross-sector}", "{investment-theme}"]
draft: false
comparative_data:
  comparison_confidence: {0.XX}
  data_quality: {0.XX}
  economic_context: "{Current/Expansion/Contraction}"
  primary_recommendation: "{BUY/HOLD/SELL}"
  secondary_recommendation: "{BUY/HOLD/SELL}"
  risk_adjusted_winner: "{TICKER_1/TICKER_2}"
  portfolio_allocation: "{XX%} {TICKER_1} / {XX%} {TICKER_2}"
  expected_returns: "{XX.X%} vs {XX.X%}"
  risk_differential: "{X.X/5.0} vs {X.X/5.0}"
---
```

### STRICT STANDARDIZATION RULES

#### Title Standards
- **Format**: `{Company_1_Name} ({TICKER_1}) vs {Company_2_Name} ({TICKER_2}) - Comparative Investment Analysis`
- **Remove**: ALL specific ratings, returns, and complex themes from title
- **Example**: `"Amazon.com Inc. (AMZN) vs Microsoft Corporation (MSFT) - Comparative Investment Analysis"`

#### Meta_title Standards
- **Always include** for SEO optimization
- **Format**: `{Company_1_Name} vs {Company_2_Name} Comparative Analysis - Investment Decision Framework`
- **Example**: `"Amazon vs Microsoft Comparative Analysis - Investment Decision Framework"`

#### Description Standards
- **Length**: 150-200 characters
- **Include**: Both recommendations, confidence level, cross-sector context
- **Template**: `"Institutional-quality comparative analysis of {Company_1} ({TICKER_1}) vs {Company_2} ({TICKER_2}) with cross-sector investment framework. {Primary_rec} vs {Secondary_rec} with {confidence}% confidence."`

#### Date Standards
- **Format**: ISO 8601 with timezone `YYYY-MM-DDTHH:MM:SSZ`
- **Example**: `2025-08-01T16:30:00Z`
- **Required**: Must include timezone Z suffix

#### Authors Standards
- **Field**: Use `authors` (NOT `author`)
- **Value**: `["Cole Morton", "Claude"]` (EXACT format)
- **Required**: Present in ALL posts

#### Categories Standards
- **Order**: `["Investing", "Analysis", "Comparative Analysis", "{Sector_1}", "{Sector_2}"]`
- **Count**: Exactly 5 categories
- **Cross-Sector**: Include both sectors when different (Technology, Healthcare, Financial Services, etc.)
- **Same-Sector**: Use sector twice when comparing within same sector

#### Tags Standards
- **Tickers**: ALWAYS lowercase (`amzn`, `msft`, NOT `AMZN`, `MSFT`)
- **Required**: `"comparative-analysis"` in ALL posts
- **Cross-Sector**: Include `"cross-sector"` when companies from different sectors
- **Recommendations**: Include both recommendation tags (`"buy"`, `"hold"`, `"sell"`) when different
- **Count**: 6-8 tags maximum
- **Format**: Lowercase with hyphens

#### Image Standards
- **Path**: `/images/comparative_analysis/{TICKER_1}_vs_{TICKER_2}_{YYYYMMDD}.png`
- **Tickers**: Uppercase in filename
- **Date**: Match publication date exactly
- **Order**: Primary ticker first (typically the focus or winner)

#### Comparative Data Standards
- **Comparison Confidence**: Decimal format (0.XX) matching source analysis
- **Data Quality**: Decimal format (0.XX) matching source analysis
- **Economic Context**: One of "Current", "Expansion", "Contraction"
- **Recommendations**: Both as "BUY", "HOLD", or "SELL"
- **Risk Adjusted Winner**: The ticker symbol of the preferred choice after risk adjustment
- **Portfolio Allocation**: Suggested allocation percentages for both stocks
- **Expected Returns**: Expected return percentages for both stocks
- **Risk Differential**: Risk scores in format "X.X/5.0" for both stocks

### STANDARDIZATION VALIDATION PROTOCOL

**MANDATORY PRE-PUBLICATION CHECKS**: Every comparative analysis post MUST pass ALL validation checks before publication:

```
FRONTMATTER COMPLIANCE VALIDATION:
□ **TITLE FORMAT**: Exact format "{Company_1} ({TICKER_1}) vs {Company_2} ({TICKER_2}) - Comparative Investment Analysis"
□ **META_TITLE PRESENCE**: Must exist with comparative framework information
□ **DESCRIPTION LENGTH**: 150-200 characters with required elements
□ **DATE FORMAT**: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)
□ **AUTHORS FORMAT**: Exact format ["Cole Morton", "Claude"]
□ **CATEGORIES STRUCTURE**: Exact format ["Investing", "Analysis", "Comparative Analysis", "{Sector_1}", "{Sector_2}"]
□ **TAGS COMPLIANCE**: Lowercase tickers + "comparative-analysis" + recommendations + themes
□ **IMAGE PATH**: Correct format with uppercase tickers and matching date
□ **COMPARATIVE DATA STRUCTURE**: Complete comparative_data object with all required fields
□ **CONFIDENCE SCORES**: Decimal format matching source analysis confidence and data quality
□ **RECOMMENDATIONS**: Valid recommendations for both stocks with risk-adjusted winner
□ **DRAFT STATUS**: Set to false for publication
```

**AUTOMATIC REJECTION**: Any post that fails validation MUST be corrected before publication. No exceptions.

**STANDARDIZATION ENFORCEMENT**: The content_publisher command will automatically verify and correct any frontmatter issues to ensure 100% compliance with the comparative analysis standard template.

## Content Publication Quality Standards

### Publication Requirements Specification

**Content Type Requirements**:
- **Fundamental Analysis**: Publisher implements ticker-based naming and frontmatter compliance
- **Sector Analysis**: Publisher implements sector-slug naming and economic context metadata
- **Trade History**: Publisher implements performance-focused schema and trading categorization
- **Comparative Analysis**: Publisher implements cross-stock naming and comparative data objects

**Universal Publication Standards**:
- **Asset Integration**: Publisher ensures consistent image paths across all visualization types
- **SEO Optimization**: Publisher implements complete metadata and social sharing requirements
- **Template Compliance**: Publisher enforces mandatory frontmatter standardization per content type
- **Quality Validation**: Publisher executes comprehensive publication readiness assessment

### Quality Assurance Standards
**Content Fidelity Enforcement Requirements**:
- **Content Preservation**: Publisher must preserve 100% of source analytical content without transformations
- **Strategic Modification**: Publisher removes only H1 title heading while maintaining all other content
- **Data Integrity**: Publisher preserves all confidence scores, financial data, trading metrics, and methodology
- **Analytical Accuracy**: Publisher maintains investment recommendations, valuations, and risk assessments exactly
- **Performance Preservation**: Publisher keeps win rates, statistical analysis, and comparative frameworks identical
- **Economic Data Accuracy**: Publisher preserves GDP correlations, sector metrics, and economic analysis unchanged

**Publication Validation Requirements**:
- **Template Compliance**: Publisher enforces frontmatter standardization per content type
- **Metadata Standards**: Publisher implements author, category, tag, and date standardization
- **Asset Integration**: Publisher ensures image accessibility and responsive optimization
- **Frontend Validation**: Publisher confirms development server rendering and cross-browser compatibility
- **SEO Optimization**: Publisher validates metadata completeness and search functionality integration

### Post-Publication Standards
**Integration Validation Requirements**:
- **Frontend Display**: Publisher validates content rendering across devices and browsers
- **Asset Functionality**: Publisher ensures image rendering and responsive behavior
- **Link Validation**: Publisher tests internal linking and cross-reference functionality
- **Search Integration**: Publisher confirms content discoverability and analytics implementation
- **Social Sharing**: Publisher validates metadata functionality for social platforms

## Content State Management Requirements

### Publication Tracking Strategy
**Publisher Content Monitoring Requirements**:
- **Publication Timeline Tracking**: Publisher monitors existing blog content for freshness assessment
- **Content Gap Analysis**: Publisher identifies opportunities for content updates and new publications
- **Calendar Management**: Publisher maintains publication scheduling and content pipeline optimization
- **Performance Monitoring**: Publisher tracks audience engagement and content effectiveness metrics

### Publication Queue Strategy
**Publisher Queue Management Requirements**:
- **Systematic Processing**: Publisher processes unpublished analysis with strategic prioritization
- **Pipeline Optimization**: Publisher manages content flow for maximum publication efficiency
- **Quality Coordination**: Publisher balances publication velocity with content quality standards

## Publication Success Criteria

### Content Quality Standards
**Publisher Quality Metrics Requirements**:
- **Content Fidelity Achievement**: Publisher must deliver 100% analytical content preservation
- **Publication Readiness Assessment**: Publisher evaluates content completeness and quality standards
- **Asset Integration Excellence**: Publisher ensures proper visual asset coordination and optimization
- **SEO Performance**: Publisher implements complete metadata and search optimization
- **Cross-Reference Integration**: Publisher manages internal linking and content interconnection

### Performance Success Indicators
**Publisher Performance Requirements**:
- **Publication Efficiency**: Publisher optimizes time from analysis generation to blog publication
- **Content Timeliness**: Publisher ensures market analysis publication freshness and relevance
- **Engagement Optimization**: Publisher supports reader interaction and social sharing capabilities
- **Search Visibility**: Publisher enables organic discovery and keyword ranking performance

## Strategic Integration Requirements

### Data Pipeline Strategy
**Publisher Data Coordination Requirements**:
- **Content Monitoring**: Publisher monitors data outputs for new analytical content availability
- **Timing Coordination**: Publisher coordinates with upstream analysis commands for optimal publication scheduling
- **Automated Discovery**: Publisher maintains content freshness through systematic discovery protocols

### Frontend Platform Strategy
**Publisher Platform Integration Requirements**:
- **Framework Compatibility**: Publisher ensures Astro 5.7+ framework compliance and compatibility
- **Styling Consistency**: Publisher maintains TailwindCSS 4+ styling standards and responsive design
- **Type Safety**: Publisher supports TypeScript integration and React component compatibility
- **Content Format Support**: Publisher validates MDX content processing and shortcode functionality

### Quality Strategy
**Publisher Quality Enforcement Requirements**:
- **Standards Compliance**: Publisher enforces comprehensive publication quality standards
- **Style Consistency**: Publisher maintains established content style guide and presentation standards
- **Cross-Platform Validation**: Publisher ensures responsive design and browser compatibility
- **Optimization Integration**: Publisher implements SEO optimization and social media integration protocols

## Quality Standards Framework

### Publication Quality Requirements
**Publisher Performance Thresholds**:
- **Content Fidelity**: Publisher must achieve 100% preservation of source analytical content
- **Template Compliance**: Publisher must maintain 100% adherence to standardized frontmatter
- **Asset Integration**: Publisher must deliver ≥95% successful optimization and frontend linking
- **Frontend Compatibility**: Publisher must ensure ≥98% rendering compatibility across devices

### Validation Protocol Standards
**Publisher Implementation Requirements**:
- **Content Integrity**: Publisher must maintain 0% variance from source analytical content
- **Metadata Accuracy**: Publisher must achieve 100% frontmatter template compliance
- **Asset Performance**: Publisher must optimize images to <500KB with responsive breakpoints
- **Frontend Health**: Publisher must validate development server rendering and compatibility

### Quality Gate Specifications
**Publisher Validation Phases**:
1. **Discovery Phase**: Publisher assesses content completeness and publication readiness
2. **Asset Phase**: Publisher executes image optimization and responsive generation
3. **Transformation Phase**: Publisher enforces content fidelity and frontmatter compliance
4. **Publication Phase**: Publisher validates frontend compatibility and cross-platform performance

## Cross-Command Integration

### Cross-Command Integration Strategy
**Upstream Content Sources**:
- **fundamental_analyst**: Publisher processes fundamental analysis outputs for blog publication
- **trade_history**: Publisher handles trade history reports with performance-focused presentation
- **sector_analyst**: Publisher manages sector analysis content with economic context integration
- **comparative_analyst**: Publisher processes DASV framework comparative analysis outputs

**Downstream Quality Assurance**:
- **content_evaluator**: Evaluates publisher-generated blog content for quality validation
- **documentation_owner**: Documents publisher workflows and content publication standards

**Publication Orchestration Requirements**:
- **Sequential Workflows**: Publisher executes content-specific publication following analytical generation
- **Multi-Content Processing**: Publisher handles batch publication across all content types
- **Quality Integration**: Publisher coordinates with downstream evaluation and documentation commands
- **Strategic Timing**: Publisher optimizes publication scheduling based on content freshness and market relevance

## Strategic Usage Requirements

### Content Publication Strategy
**Basic Publication Requirements**:
- Publisher executes comprehensive content discovery and publication workflows
- Publisher implements content type-specific processing with quality validation
- Publisher handles multi-content type publication with unified standards

**Advanced Publication Strategy**:
- Publisher optimizes content prioritization with market relevance assessment
- Publisher implements comprehensive validation with frontend compatibility testing
- Publisher coordinates asset optimization with responsive web presentation

**Specialized Publication Requirements**:
- **Comparative Analysis Focus**: Publisher handles cross-stock comparative content with specialized metadata
- **Asset-Only Processing**: Publisher manages image optimization workflows independently
- **Validation-Only Mode**: Publisher executes quality assurance without content publication
- **Comprehensive Scope**: Publisher processes all available content types with strategic prioritization

---

**Integration with Framework**: This command defines strategic content publication requirements for publisher-generated blog content within the broader Colemorton ecosystem through standardized template specifications, quality enforcement protocols, and cross-command coordination.

**Author**: Cole Morton
**Framework**: Content Publication Strategy Framework
**Implementation**: Publisher sub-agent with content publication specialization
**Confidence**: High - Strategic publication methodology with publisher delegation
**Data Quality**: High - Content fidelity preservation through publisher implementation

## Trade History Report Management

### Trade History Content Types

**HISTORICAL_PERFORMANCE_REPORT**: Comprehensive analysis of closed trading positions
- **Content Structure**: Performance metrics, trade analysis, quality distribution, temporal analysis
- **Key Metrics**: Win rate, profit factor, average returns, risk-reward profiles
- **Publication Priority**: High - provides validated trading system performance data

**INTERNAL_TRADING_REPORT**: Internal trading system analysis and optimization insights
- **Content Structure**: System performance, signal quality, operational metrics
- **Key Metrics**: Signal accuracy, execution efficiency, system reliability
- **Publication Priority**: Medium - technical insights for trading system development

**LIVE_SIGNALS_MONITOR**: Real-time signal monitoring and market analysis
- **Content Structure**: Current signals, market conditions, real-time analysis
- **Key Metrics**: Active signals, market sentiment, timing analysis
- **Publication Priority**: High - time-sensitive market insights

### Trade History Publication Workflow

```
TRADE HISTORY SPECIFIC PIPELINE:
1. **Content Discovery**: Scan @{DATA_OUTPUTS}/trade_history/ for unpublished reports
2. **Report Classification**: Identify report type (HISTORICAL, INTERNAL, LIVE_SIGNALS)
3. **Asset Mapping**: Link to performance charts and trading visualizations
4. **Schema Application**: Apply trading-specific frontmatter templates
5. **Fidelity Preservation**: Maintain 100% accuracy of trading metrics and analysis
6. **Publication**: Deploy to @frontend/src/content/blog/ with trading categories
7. **Validation**: Verify trading data accuracy and chart accessibility
```

### Trade History Quality Gates

```
TRADING CONTENT VALIDATION:
□ **PERFORMANCE METRICS ACCURACY**: Win rates, profit factors, return percentages exactly preserved
□ **TRADE DATA INTEGRITY**: Entry/exit dates, prices, durations, and tickers unchanged
□ **STATISTICAL ANALYSIS PRESERVATION**: Quality distributions, temporal analysis, strategy performance maintained
□ **RISK ASSESSMENT FIDELITY**: Risk-reward profiles, drawdown analysis, volatility metrics preserved
□ **METHODOLOGY DOCUMENTATION**: Trading system logic and signal generation process unchanged
□ **VISUAL ASSET COORDINATION**: Performance charts and trading visualizations properly linked
```

## Content Fidelity Enforcement

**PUBLISHER IMPLEMENTATION REQUIREMENT**: Publisher sub-agent must implement zero-tolerance policy for analytical content modification, serving as faithful custodian through systematic preservation protocols:

**Content Preservation Standards**:
- **Investment Recommendations**: Publisher maintains BUY/SELL/HOLD ratings exactly as generated
- **Confidence Scores**: Publisher preserves all analytical confidence metrics precisely
- **Financial Data**: Publisher keeps valuations, price targets, and risk assessments unchanged
- **Trading Performance Data**: Publisher maintains win rates, profit factors, and statistical metrics exactly
- **Comparative Analysis Data**: Publisher preserves cross-stock comparisons and portfolio allocations
- **Methodology Integrity**: Publisher maintains analysis methodology and data sources verbatim
- **Author Voice Preservation**: Publisher preserves analytical voice and technical language completely

Publisher implementation ensures readers receive exact analytical output with maintained credibility and accuracy.

## Sector Analysis Content Management

### Sector Analysis Content Types

**SECTOR_ANALYSIS_REPORT**: Comprehensive cross-sector analysis with economic integration
- **Content Structure**: Economic sensitivity matrix, market positioning, valuation framework, risk assessment
- **Key Metrics**: GDP correlation, employment sensitivity, interest rate impacts, sector rotation scores
- **Publication Priority**: High - provides strategic sector allocation guidance

**SECTOR_COMPARATIVE_ANALYSIS**: Multi-sector comparison with relative performance metrics
- **Content Structure**: Cross-sector valuations, performance attribution, risk-adjusted returns
- **Key Metrics**: Relative P/E ratios, sector betas, correlation analysis, momentum indicators
- **Publication Priority**: Medium - tactical sector rotation insights

**SECTOR_THEMATIC_ANALYSIS**: Sector-specific thematic deep dives with catalyst identification
- **Content Structure**: Industry dynamics, competitive positioning, regulatory environment, innovation trends
- **Key Metrics**: Market share analysis, R&D intensity, regulatory impact scores, disruptive risk assessment
- **Publication Priority**: Medium - long-term sector positioning insights

### Sector Analysis Publication Workflow

```
SECTOR ANALYSIS SPECIFIC PIPELINE:
1. **Content Discovery**: Scan @{DATA_OUTPUTS}/sector_analysis/ for unpublished sector reports
2. **Report Classification**: Identify sector type (Technology, Healthcare, Finance, Energy, etc.)
3. **Asset Mapping**: Link to sector charts, economic indicators, and comparative visualizations
4. **Schema Application**: Apply sector-specific frontmatter templates with confidence scores
5. **Fidelity Preservation**: Maintain 100% accuracy of economic data, correlations, and risk assessments
6. **Publication**: Deploy to @frontend/src/content/blog/ with sector analysis categories
7. **Validation**: Verify economic data accuracy and sector-specific chart accessibility
```

### Sector Analysis Quality Gates

```
SECTOR ANALYSIS CONTENT VALIDATION:
□ **ECONOMIC DATA ACCURACY**: GDP correlations, employment sensitivity, interest rate impacts exactly preserved
□ **SECTOR METRICS INTEGRITY**: P/E ratios, sector betas, performance attribution, and risk metrics unchanged
□ **CORRELATION ANALYSIS PRESERVATION**: Cross-sector correlations, VIX relationships, and economic sensitivity maintained
□ **CONFIDENCE SCORE FIDELITY**: Analysis confidence and data quality metrics preserved exactly
□ **METHODOLOGY DOCUMENTATION**: Economic integration methodology and data sources unchanged
□ **SECTOR DATA OBJECT COMPLETION**: Complete sector_data frontmatter with all required fields
□ **VISUAL ASSET COORDINATION**: Sector charts and comparative visualizations properly linked
□ **ECONOMIC CONTEXT ACCURACY**: Current economic cycle positioning and recession probabilities preserved
```

## Comparative Analysis Content Management

### Comparative Analysis Content Types

**CROSS_STOCK_COMPARATIVE_ANALYSIS**: Institutional-quality comparative investment analysis with cross-sector framework
- **Content Structure**: Comparative company intelligence, financial health comparison, risk-adjusted recommendations, portfolio allocation guidance
- **Key Metrics**: Cross-stock confidence scores, comparative risk matrices, winner determinations, expected returns differential
- **Publication Priority**: High - provides sophisticated investment decision frameworks for portfolio construction

**SECTOR_COMPARATIVE_ANALYSIS**: Cross-sector comparative analysis with economic integration
- **Content Structure**: Sector positioning comparison, economic sensitivity differential, regulatory environment analysis
- **Key Metrics**: Sector rotation scores, economic context impact, cross-sector valuation metrics
- **Publication Priority**: Medium - strategic sector allocation insights with comparative framework

**INDUSTRY_COMPARATIVE_ANALYSIS**: Within-industry comparative analysis with competitive intelligence
- **Content Structure**: Market positioning comparison, competitive moat analysis, industry dynamics assessment
- **Key Metrics**: Market share analysis, competitive advantage scoring, industry disruption risk assessment
- **Publication Priority**: Medium - tactical positioning insights within industry contexts

### Comparative Analysis Publication Workflow

```
COMPARATIVE ANALYSIS SPECIFIC PIPELINE:
1. **Content Discovery**: Scan @{DATA_OUTPUTS}/comparative_analysis/ for unpublished comparative reports
2. **Report Classification**: Identify comparison type (Cross-Stock, Cross-Sector, Within-Industry)
3. **Asset Mapping**: Link to comparative charts, side-by-side visualizations, and cross-stock analysis
4. **Schema Application**: Apply comparative-specific frontmatter templates with confidence scores
5. **Fidelity Preservation**: Maintain 100% accuracy of comparative metrics, risk matrices, and investment recommendations
6. **Publication**: Deploy to @frontend/src/content/blog/ with comparative analysis categories
7. **Validation**: Verify comparative data accuracy and cross-stock chart accessibility
```

### Comparative Analysis Quality Gates

```
COMPARATIVE ANALYSIS CONTENT VALIDATION:
□ **COMPARATIVE METRICS ACCURACY**: Cross-stock financial ratios, valuation comparisons, and performance attribution exactly preserved
□ **RISK MATRIX INTEGRITY**: Probability-impact matrices, stress testing scenarios, and risk differential analysis unchanged
□ **INVESTMENT RECOMMENDATION PRESERVATION**: Primary and secondary recommendations, portfolio allocations, and winner determinations maintained
□ **CONFIDENCE SCORE FIDELITY**: Comparative analysis confidence and data quality metrics preserved exactly
□ **METHODOLOGY DOCUMENTATION**: Cross-stock analytical framework and comparative selection rationale unchanged
□ **COMPARATIVE DATA OBJECT COMPLETION**: Complete comparative_data frontmatter with all required fields
□ **VISUAL ASSET COORDINATION**: Comparative charts and cross-stock visualizations properly linked
□ **ECONOMIC CONTEXT ACCURACY**: Interest rate sensitivity differential and economic impact analysis preserved
```

## Multi-Content Type Integration

### Unified Content Pipeline

The content_publisher command now supports four distinct content types with unified quality standards:

1. **Fundamental Analysis**: Company-specific investment analysis with valuation models
2. **Trade History Reports**: Trading performance analysis with statistical validation
3. **Sector Analysis**: Sector-level strategic analysis with economic integration
4. **Comparative Analysis**: Cross-stock comparative investment analysis with risk-adjusted decision frameworks

### Content Type Detection

```
AUTOMATED CONTENT TYPE DETECTION:
- **Fundamental Analysis**: Files matching pattern `[ticker]-fundamental-analysis-[YYYYMMDD].md`
- **Trade History**: Files matching pattern `trading-performance-[type]-[YYYYMMDD].md`
- **Sector Analysis**: Files matching pattern `[sector]-sector-analysis-[YYYYMMDD].md`
- **Comparative Analysis**: Files matching pattern `[ticker1]_vs_[ticker2]_[YYYYMMDD].md`
```

### Cross-Content Type Validation

```
UNIVERSAL CONTENT STANDARDS:
□ **100% Content Fidelity**: All analytical content preserved without transformation
□ **Standardized Frontmatter**: Proper template compliance per content type
□ **Asset Integration**: Consistent image linking and optimization
□ **SEO Optimization**: Complete metadata and social sharing tags
□ **Publication Readiness**: Quality gates passed for all content types
```
