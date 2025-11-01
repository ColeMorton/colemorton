# Macro Analysis Publisher

**Command Classification**: 📊 **Macro Economics Command**
**Knowledge Domain**: `macro-analysis-publication-workflow`
**Ecosystem Version**: `2.1.0` *(Last Updated: 2025-09-06)*
**Outputs To**: `frontend/src/content/blog/`

## Script Integration Mapping

**Primary Script**: `{SCRIPTS_BASE}/macro_analysis/macro_publisher_script.py`
**Script Class**: `MacroPublisherScript`
**Registry Name**: `macro_publisher`
**Content Types**: `["macro_analysis", "economic_outlook"]`
**Requires Validation**: `true` (via macro_analysis/validate)
**Implementation**: Publisher sub-agent with macro analysis specialization
**Validation Integration**: Uses macro_analysis/validate instead of content_evaluator

**Registry Decorator**:
```python
@macro_script(
    name="macro_publisher",
    content_types=["macro_analysis", "economic_outlook"],
    requires_validation=True
)
class MacroPublisherScript(BaseScript):
    """Transform macro economic insights into publication-ready blog content with absolute content fidelity"""
```

**Macro Analysis Workflow Scripts**:
```yaml
macro_discovery_script:
  path: "{SCRIPTS_BASE}/macro_analysis/macro_content_discovery.py"
  class: "MacroContentDiscoveryScript"
  phase: "Phase 1 - Macro Content Discovery & Assessment"

macro_asset_script:
  path: "{SCRIPTS_BASE}/macro_analysis/macro_asset_coordinator.py"
  class: "MacroAssetCoordinatorScript"
  phase: "Phase 2 - Static Asset Management"

macro_transformation_script:
  path: "{SCRIPTS_BASE}/macro_analysis/macro_content_transformer.py"
  class: "MacroContentTransformerScript"
  phase: "Phase 3 - Macro Content Transformation"

macro_publication_script:
  path: "{SCRIPTS_BASE}/macro_analysis/macro_frontend_publisher.py"
  class: "MacroFrontendPublisherScript"
  phase: "Phase 4 - Macro Publication & Validation"
```

## Purpose

You are the Macro Economic Analysis Publication Strategy Specialist, responsible for defining comprehensive publication requirements for macro analysis content. This command implements macro analysis publication strategic requirements, focusing on economic outlook content discovery and publication quality standards while delegating implementation methodology to the publisher sub-agent.

### Content Fidelity Mandate

**CRITICAL**: This command defines content fidelity requirements for publisher implementation. All macro economic analytical content must preserve 100% accuracy without transformation, summarization, or editorial modification. The only permitted change is removing the H1 title heading to prevent duplication with frontmatter titles.

**Output Location**: Published macro analysis content in `frontend/src/content/blog/` with supporting static assets from `frontend/public/images/macro/`

## Template Integration Architecture

**Template Directory**: `{TEMPLATES_BASE}/macro_analysis/`

**Macro Analysis Template Mappings**:
| Template ID | File Path | Selection Criteria | Purpose |
|------------|-----------|-------------------|---------|
| macro_analysis_blog | `macro_analysis/macro_analysis_blog.j2` | Content type macro analysis | Macro economic analysis blog posts |
| economic_outlook_blog | `macro_analysis/economic_outlook_blog.j2` | Content type economic outlook | Economic outlook and forecast posts |
| macro_frontmatter | `macro_analysis/macro_frontmatter.j2` | All macro content | Standardized macro frontmatter generation |

**Macro Shared Components**:
```yaml
macro_frontmatter_base:
  path: "{TEMPLATES_BASE}/macro_analysis/shared/macro_frontmatter_base.j2"
  purpose: "Base macro frontmatter template with economic metadata and SEO optimization"

macro_content_fidelity:
  path: "{TEMPLATES_BASE}/macro_analysis/shared/macro_content_fidelity.j2"
  purpose: "Macro content preservation template ensuring 100% economic analytical integrity"

macro_static_asset_integration:
  path: "{TEMPLATES_BASE}/macro_analysis/shared/macro_static_asset_integration.j2"
  purpose: "Static macro image coordination templates for regional content"
```

**Macro Template Selection Algorithm**:
```python
def select_macro_publication_template(content_analysis):
    """Select optimal template for macro content publication"""

    # Macro economic analysis blog template
    if content_analysis.get('content_type') == 'macro_analysis':
        return 'macro_analysis/macro_analysis_blog.j2'

    # Economic outlook blog template
    elif content_analysis.get('content_type') == 'economic_outlook':
        return 'macro_analysis/economic_outlook_blog.j2'

    # Default macro template
    return 'macro_analysis/macro_frontmatter.j2'
```

## Macro Content Publication Strategy Requirements

### Macro Content Discovery Requirements
**Macro Content Audit Specifications**:
- Macro analysis content discovery from `data/outputs/macro_analysis/` directory exclusively
- Publication gap analysis comparing existing macro blog content against available macro outputs
- Economic content readiness assessment with macro-specific quality standard evaluation
- Priority optimization based on economic relevance, market timing, and policy significance
- Regional macro content integration for unified discovery workflows

### Static Asset Coordination Requirements
**Macro Asset Management Specifications**:
- Static image coordination using pre-optimized macro visualizations
- Regional asset mapping protocols for Americas, Asia, Europe, Global, and US content
- Static asset validation with consistent macro naming convention enforcement
- Direct static asset referencing from `frontend/public/images/macro/` directory

**Available Static Macro Assets**:
- `americas-min.png` - Americas regional macro analysis
- `asia-min.png` - Asia-Pacific regional macro analysis
- `europe-min.png` - European regional macro analysis
- `global-min.png` - Global macro economic analysis
- `us-min.png` - United States specific macro analysis

### Macro Content Transformation Standards
**Macro Content Fidelity Requirements**:
- **ZERO TRANSFORMATION POLICY**: 100% preservation of macro analytical content
- **STRATEGIC H1 REMOVAL**: Remove only title heading to prevent frontmatter duplication
- **MACRO ANALYTICAL INTEGRITY**: Preserve all economic confidence scores, policy assessments, recession probabilities, methodology
- **MACRO FRONTMATTER STANDARDIZATION**: Apply macro-specific templates with proper economic metadata
- **QUALITY GATE ENFORCEMENT**: Fail-fast protocols for macro content modification attempts

### Publication Integration Standards
**Frontend Compatibility Requirements**:
- Astro framework compatibility with macro content collection standards
- Development server validation with macro content rendering verification
- Cross-browser testing and mobile responsiveness for economic content
- SEO optimization with macro-specific metadata and economic keywords
- Search functionality integration for macro content discoverability

## Publisher Integration Specifications

**Macro Content Delegation Framework**:
- **Tool Integration**: Automated `macro_publisher_script.py` execution via publisher sub-agent
- **Quality Enforcement**: Publisher implements ≥95% publication success rate with macro content fidelity validation via macro_analysis/validate
- **Professional Generation**: Publication-ready macro blog content with frontend integration specialization
- **Macro Content Expertise**: Publisher handles macro analysis and economic outlook content exclusively
- **Unified Validation**: Uses macro_analysis/validate for specialized macro-economic validation logic

**Macro Content Publication Enhancement Requirements**:
- **Content Discovery Implementation**: Publisher executes macro content discovery with gap analysis
- **Asset Coordination Implementation**: Publisher manages static macro asset coordination and validation workflows
- **Content Fidelity Implementation**: Publisher enforces 100% macro content preservation with strategic H1 removal
- **Frontend Integration Implementation**: Publisher ensures Astro framework compatibility and macro validation protocols

**Quality Assurance Protocol**:
- **Methodology Compliance**: Publisher implements macro publication standards and validation workflows
- **Asset Integration**: Publisher manages static macro asset coordination and presentation requirements
- **Publication Logic Verification**: Publisher ensures macro content readiness and frontend compatibility
- **Professional Standards**: Publisher delivers publication-ready macro content with quality gate enforcement

## Data Flow & File References

**Macro Input Sources**:
```yaml
macro_analysis:
  path: "{DATA_OUTPUTS}/macro_analysis/{REGION}_{YYYYMMDD}.md"
  format: "markdown"
  required: true
  description: "Macro economic analysis reports for publication"
  regions: ["US", "Americas", "Europe", "Asia", "Global"]

economic_outlook:
  path: "{DATA_OUTPUTS}/macro_analysis/{REGION}_outlook_{YYYYMMDD}.md"
  format: "markdown"
  required: false
  description: "Economic outlook and forecast reports for publication"

static_macro_assets:
  path: "frontend/public/images/macro/{region-slug}-min.png"
  format: "png"
  required: true
  description: "Static macro visualization assets for regional content"
```

**Macro Output Structure**:
```yaml
macro_blog_content:
  path: "frontend/src/content/blog/{region-slug}-macro-analysis-{YYYYMMDD}.md"
  format: "markdown"
  description: "Published macro analysis blog content with standardized frontmatter"

static_macro_images:
  path: "frontend/public/images/macro/{region-slug}-min.png"
  format: "png"
  description: "Static macro images referenced from blog content"

macro_publication_metadata:
  path: "{DATA_OUTPUTS}/macro_analysis/publication/{REGION}_{YYYYMMDD}_metadata.json"
  format: "json"
  description: "Macro publication metadata and validation results"
```

## Parameters

### Core Macro Parameters
- `region`: Macro region to publish - `US` | `Americas` | `Europe` | `Asia` | `Global` | `all` (optional, default: all)
- `content_type`: Macro content type - `macro_analysis` | `economic_outlook` | `all` (optional, default: all)
- `priority`: Publication priority - `high` | `medium` | `low` (optional, default: medium)
- `mode`: Publication mode - `full` | `assets_only` | `validation_only` (optional, default: full)

### Advanced Macro Parameters
- `scope`: Publication scope - `comprehensive` | `selective` | `targeted` (optional, default: comprehensive)
- `validation_level`: Validation depth - `basic` | `standard` | `comprehensive` (optional, default: standard)
- `static_asset_validation`: Enable static asset validation - `true` | `false` (optional, default: true)
- `frontend_validation`: Enable frontend rendering validation - `true` | `false` (optional, default: true)

### Macro Workflow Parameters
- `phase_start`: Starting phase - `discovery` | `asset` | `transformation` | `publication` (optional)
- `phase_end`: Ending phase - `discovery` | `asset` | `transformation` | `publication` (optional)
- `continue_on_error`: Continue workflow despite errors - `true` | `false` (optional, default: false)

## Macro Analysis Standard Template

### MANDATORY MACRO FRONTMATTER TEMPLATE

All macro analysis posts MUST use this exact template with NO deviations:

```yaml
---
title: "{Region} Macro Economic Analysis - {Month} {YYYY}"
meta_title: "{Region} Macro Economic Analysis - Business Cycle Assessment | {Month} {YYYY}"
description: "Comprehensive {Region} macro economic analysis with business cycle positioning and recession probabilities. Current phase: {Economic_Phase} with {Confidence}% confidence. {Brief macro thesis 1-2 sentences}."
date: {YYYY-MM-DD}T{HH:MM:SS}Z
image: "/images/macro/{region-slug}-min.png"
authors: ["Cole Morton", "Claude"]
categories: ["Economics", "Analysis", "Macro Analysis", "{Region}", "Economic Outlook"]
tags: ["{region-slug}", "macro-analysis", "{economic-phase-lowercase}", "{policy-context}", "{key-theme-1}", "{key-theme-2}"]
draft: false
macro_data:
  confidence: {0.XX}
  data_quality: {0.XX}
  economic_phase: "{Expansion/Peak/Contraction/Trough}"
  recession_probability: "{XX.X%}"
  policy_stance: "{Accommodative/Neutral/Restrictive}"
  business_cycle_position: "{Early/Mid/Late}-{Expansion/Contraction}"
  interest_rate_environment: "{Rising/Stable/Falling}"
  inflation_trajectory: "{Rising/Stable/Falling}"
  risk_score: "{X.X/5.0}"
---
```

### STRICT MACRO STANDARDIZATION RULES

#### Title Standards
- **Format**: `{Region} Macro Economic Analysis - {Month} {YYYY}`
- **Remove**: ALL specific recommendations, probabilities, and complex themes from title
- **Example**: `"United States Macro Economic Analysis - September 2025"`

#### Meta_title Standards
- **Always include** for SEO optimization
- **Format**: `{Region} Macro Economic Analysis - Business Cycle Assessment | {Month} {YYYY}`
- **Example**: `"United States Macro Economic Analysis - Business Cycle Assessment | September 2025"`

#### Description Standards
- **Length**: 150-200 characters
- **Include**: Economic phase, recession probability, confidence level, key thesis
- **Template**: `"Comprehensive {Region} macro economic analysis with business cycle positioning and recession probabilities. Current phase: {Economic_Phase} with {Confidence}% confidence. {Macro thesis}."`

#### Date Standards
- **Format**: ISO 8601 with timezone `YYYY-MM-DDTHH:MM:SSZ`
- **Example**: `2025-09-06T10:00:00Z`
- **Required**: Must include timezone Z suffix

#### Authors Standards
- **Field**: Use `authors` (NOT `author`)
- **Value**: `["Cole Morton", "Claude"]` (EXACT format)
- **Required**: Present in ALL macro posts

#### Categories Standards
- **Order**: `["Economics", "Analysis", "Macro Analysis", "{Region}", "Economic Outlook"]`
- **Count**: Exactly 5 categories
- **Regions**: US, Americas, Europe, Asia, Global
- **Required**: "Economic Outlook" as 5th category

#### Tags Standards
- **Region**: ALWAYS lowercase with hyphens (`us`, `americas`, `europe`, `asia`, `global`)
- **Required**: `"macro-analysis"` in ALL posts
- **Economic Phase**: Include economic phase tag (`"expansion"`, `"contraction"`, `"peak"`, `"trough"`)
- **Policy Context**: Include policy context tag (`"accommodative"`, `"neutral"`, `"restrictive"`)
- **Count**: 5-7 tags maximum
- **Format**: Lowercase with hyphens

#### Static Image Standards
- **Path**: `/images/macro/{region-slug}-min.png`
- **Region**: Lowercase with hyphens in filename (`us-min.png`, `americas-min.png`, etc.)
- **Static Assets**: Must reference existing static macro visualization

#### Macro Data Standards
- **Confidence**: Decimal format (0.XX) matching source analysis
- **Data Quality**: Decimal format (0.XX) matching source analysis
- **Economic Phase**: One of "Expansion", "Peak", "Contraction", "Trough"
- **Recession Probability**: Percentage format "XX.X%"
- **Policy Stance**: One of "Accommodative", "Neutral", "Restrictive"
- **Business Cycle Position**: Format "{Early/Mid/Late}-{Expansion/Contraction}"
- **Interest Rate Environment**: One of "Rising", "Stable", "Falling"
- **Inflation Trajectory**: One of "Rising", "Stable", "Falling"
- **Risk Score**: Decimal format "X.X/5.0"

### MACRO STANDARDIZATION VALIDATION PROTOCOL

**MANDATORY PRE-PUBLICATION CHECKS**: Every macro analysis post MUST pass ALL validation checks before publication:

```
MACRO FRONTMATTER COMPLIANCE VALIDATION:
□ **TITLE FORMAT**: Exact format "{Region} Macro Economic Analysis - {Month} {YYYY}"
□ **META_TITLE PRESENCE**: Must exist with business cycle assessment information
□ **DESCRIPTION LENGTH**: 150-200 characters with required macro elements
□ **DATE FORMAT**: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)
□ **AUTHORS FORMAT**: Exact format ["Cole Morton", "Claude"]
□ **CATEGORIES STRUCTURE**: Exact format ["Economics", "Analysis", "Macro Analysis", "{Region}", "Economic Outlook"]
□ **TAGS COMPLIANCE**: Lowercase region + "macro-analysis" + economic phase + policy context + themes
□ **STATIC IMAGE PATH**: Correct format with lowercase region slug and -min.png suffix
□ **MACRO DATA STRUCTURE**: Complete macro_data object with all required economic fields
□ **CONFIDENCE SCORES**: Decimal format matching source analysis confidence and data quality
□ **ECONOMIC PHASE**: Valid economic cycle phase matching source analysis
□ **DRAFT STATUS**: Set to false for publication
```

**AUTOMATIC REJECTION**: Any post that fails validation MUST be corrected before publication. No exceptions.

**STANDARDIZATION ENFORCEMENT**: The macro_publisher command will automatically verify and correct any frontmatter issues to ensure 100% compliance with the macro analysis standard template.

## Macro Content Publication Quality Standards

### Macro Publication Requirements Specification

**Macro Content Type Requirements**:
- **Macro Analysis**: Publisher implements region-based naming and macro frontmatter compliance
- **Economic Outlook**: Publisher implements outlook-specific schema and economic forecasting metadata

**Universal Macro Publication Standards**:
- **Static Asset Integration**: Publisher ensures consistent static image paths across all regional macro content
- **SEO Optimization**: Publisher implements complete economic metadata and macro-specific keywords
- **Template Compliance**: Publisher enforces mandatory macro frontmatter standardization
- **Quality Validation**: Publisher executes comprehensive macro publication readiness assessment

### Quality Assurance Standards
**Macro Content Fidelity Enforcement Requirements**:
- **Content Preservation**: Publisher must preserve 100% of source macro analytical content without transformations
- **Strategic Modification**: Publisher removes only H1 title heading while maintaining all other macro content
- **Data Integrity**: Publisher preserves all economic confidence scores, recession probabilities, policy assessments, and methodology
- **Analytical Accuracy**: Publisher maintains business cycle assessments, economic forecasts, and risk evaluations exactly
- **Economic Data Accuracy**: Publisher preserves GDP analysis, employment metrics, inflation trajectories, and monetary policy assessments unchanged

**Publication Validation Requirements**:
- **Template Compliance**: Publisher enforces macro frontmatter standardization
- **Metadata Standards**: Publisher implements author, category, tag, and date standardization for macro content
- **Static Asset Integration**: Publisher ensures static macro image accessibility and validation
- **Frontend Validation**: Publisher confirms development server rendering and cross-browser compatibility for macro content
- **SEO Optimization**: Publisher validates economic metadata completeness and macro content discoverability

### Post-Publication Standards
**Integration Validation Requirements**:
- **Frontend Display**: Publisher validates macro content rendering across devices and browsers
- **Static Asset Functionality**: Publisher ensures static macro image rendering and accessibility
- **Link Validation**: Publisher tests internal linking and cross-reference functionality for macro content
- **Search Integration**: Publisher confirms macro content discoverability and economic keyword analytics
- **Social Sharing**: Publisher validates macro metadata functionality for economic content sharing

## Macro Content State Management Requirements

### Macro Publication Tracking Strategy
**Publisher Macro Content Monitoring Requirements**:
- **Publication Timeline Tracking**: Publisher monitors existing macro blog content for freshness assessment
- **Content Gap Analysis**: Publisher identifies opportunities for macro content updates and new regional publications
- **Economic Calendar Management**: Publisher maintains macro publication scheduling based on economic events and policy announcements
- **Performance Monitoring**: Publisher tracks audience engagement with macro economic content

### Macro Publication Queue Strategy
**Publisher Queue Management Requirements**:
- **Systematic Processing**: Publisher processes unpublished macro analysis with regional and economic prioritization
- **Pipeline Optimization**: Publisher manages macro content flow for maximum publication efficiency
- **Quality Coordination**: Publisher balances macro publication velocity with economic content quality standards

## Cross-Command Integration

### Cross-Command Integration Strategy
**Upstream Macro Content Sources**:
- **macro_analyst**: Publisher processes macro analysis outputs exclusively from DASV framework

**Downstream Quality Assurance**:
- **macro_analysis/validate**: Validates publisher-generated macro blog content using specialized macro-economic validation logic
- **documentation_owner**: Documents macro publisher workflows and content publication standards

**Macro Publication Orchestration Requirements**:
- **Sequential Workflows**: Publisher executes macro content publication following analytical generation
- **Regional Processing**: Publisher handles batch publication across all macro regions
- **Quality Integration**: Publisher coordinates with macro_analysis/validate for comprehensive validation
- **Economic Timing**: Publisher optimizes publication scheduling based on economic events and policy announcements

**Unified Validation Workflow**:
1. **Content Publication**: Publisher generates macro blog content from DASV synthesis
2. **Quality Validation**: macro_analysis/validate verifies published content using `published_content` or `comprehensive` validation modes
3. **CLI Integration**: Real-time economic data validation via production CLI services
4. **Institutional Certification**: Confidence scoring >9.5/10 for publication approval

## Strategic Usage Requirements

### Macro Content Publication Strategy
**Basic Macro Publication Requirements**:
- Publisher executes comprehensive macro content discovery and publication workflows
- Publisher implements region-specific processing with economic quality validation
- Publisher handles multi-regional macro publication with unified economic standards

**Advanced Macro Publication Strategy**:
- Publisher optimizes macro content prioritization with economic relevance assessment
- Publisher implements comprehensive validation with frontend compatibility testing for macro content
- Publisher coordinates static asset validation with economic presentation standards

**Specialized Macro Publication Requirements**:
- **Regional Focus**: Publisher handles region-specific macro content with specialized economic metadata
- **Static Asset Management**: Publisher manages static macro image validation workflows
- **Validation-Only Mode**: Publisher executes macro quality assurance without content publication
- **Comprehensive Regional Scope**: Publisher processes all available macro regions with economic prioritization

---

**Integration with Framework**: This command defines strategic macro analysis publication requirements for publisher-generated economic blog content within the broader Colemorton ecosystem through standardized macro template specifications, economic quality enforcement protocols, and macro-focused cross-command coordination.

**Author**: Cole Morton
**Framework**: Macro Analysis Publication Strategy Framework
**Implementation**: Publisher sub-agent with macro analysis publication specialization
**Confidence**: High - Strategic macro publication methodology with publisher delegation
**Data Quality**: High - Macro content fidelity preservation through publisher implementation
