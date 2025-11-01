# Cole Morton Frontend Style Guide

> **Version**: 1.0.0  
> **Framework**: Astro 5.7+ with Tailwind CSS 4+  
> **Build System**: Vite with TailwindCSS Plugin  
> **Last Updated**: September 2025

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Theme System](#theme-system)
3. [Typography & Font System](#typography--font-system)
4. [Color System & Palettes](#color-system--palettes)
5. [Component Styling Architecture](#component-styling-architecture)
6. [Utility Classes & Custom CSS](#utility-classes--custom-css)
7. [Chart & Data Visualization Theming](#chart--data-visualization-theming)
8. [Build System Integration](#build-system-integration)
9. [Development Guidelines](#development-guidelines)
10. [Technical Reference](#technical-reference)

---

## Architecture Overview

### Tech Stack Foundation

The Cole Morton frontend implements a modern, performance-optimized styling system built on:

- **Astro 5.7+**: Static site generation with component islands
- **Tailwind CSS 4.0**: Utility-first CSS framework with custom plugin architecture
- **TypeScript**: Type-safe styling configurations and theme management
- **Vite**: Build system with TailwindCSS Vite plugin for optimized processing
- **React Integration**: For interactive components with theme-aware styling

### Key Architectural Decisions

**1. JSON-Driven Theme Configuration**
- Centralized theme management via `src/config/theme.json`
- Build-time CSS custom property generation
- Type-safe theme integration across components

**2. Custom Tailwind Plugin System**
- Extended Tailwind functionality via `src/tailwind-plugin/tw-theme.js`
- Dynamic utility class generation from theme configuration
- CSS custom properties for runtime theme switching

**3. Self-Hosted Font Strategy**
- Optimized font loading with local TTF files
- Performance-first approach with `font-display: swap`
- Reduced external dependencies and improved loading times

**4. Layer-Based CSS Architecture**
```css
@layer base {
  /* Typography, resets, base styles */
}

@layer components {
  /* Reusable component styles */
}

@layer utilities {
  /* Custom utility classes */
}
```

---

## Theme System

### Theme Configuration Structure

The theme system is driven by `src/config/theme.json`, providing centralized control over all visual aspects:

```json
{
  "colors": {
    "default": {
      "theme_color": {
        "primary": "#1A1A1A",
        "body": "#FFFFFF",
        "border": "#DDE2E6",
        "light": "#F5F7FA",
        "dark": "#1A1A1A"
      },
      "text_color": {
        "text": "#3E4C59",
        "text-dark": "#1A1A1A",
        "text-light": "#6B7280"
      }
    },
    "darkmode": {
      "theme_color": {
        "primary": "#F9FAFB",
        "body": "#1E1F22",
        "border": "#3B3F46",
        "light": "#2A2C2F",
        "dark": "#1E1F22"
      },
      "text_color": {
        "text": "#D1D5DB",
        "text-dark": "#F9FAFB",
        "text-light": "#9CA3AF"
      }
    },
    "data": {
      "primary_data": "#00BCD4",
      "secondary_data": "#9575CD",
      "tertiary_data": "#4285F4",
      "quaternary": "#FF7043",
      "neutral_data": "#90A4AE"
    }
  },
  "fonts": {
    "font_family": {
      "primary": "Heebo:wght@400;600",
      "primary_type": "sans-serif",
      "secondary": "Heebo:wght@700;800",
      "secondary_type": "sans-serif"
    },
    "font_size": {
      "base": "16",
      "scale": "1.2"
    }
  }
}
```

### Custom Tailwind Plugin Implementation

The theme system is powered by `src/tailwind-plugin/tw-theme.js`, which:

**1. Processes Theme Configuration**
```javascript
// Extract font families dynamically
const fontFamilies = Object.entries(themeConfig.fonts.font_family)
  .filter(([key]) => !key.includes("type"))
  .reduce((acc, [key, font]) => {
    acc[key] = `${findFont(font)}, ${themeConfig.fonts.font_family[`${key}_type`] || "sans-serif"}`;
    return acc;
  }, {});
```

**2. Generates CSS Custom Properties**
```javascript
// Build CSS variables for colors
const getVars = (groups) => {
  const vars = {};
  groups.forEach(({ colors, prefix }) => {
    Object.entries(colors).forEach(([k, v]) => {
      const cssKey = k.replace(/_/g, "-");
      vars[`--color-${prefix}${cssKey}`] = v;
    });
  });
  return vars;
};
```

**3. Creates Dynamic Utility Classes**
```javascript
// Generate font and color utilities
matchUtilities({
  bg: (value) => ({ backgroundColor: value }),
  text: (value) => ({ color: value }),
  border: (value) => ({ borderColor: value }),
  fill: (value) => ({ fill: value }),
  stroke: (value) => ({ stroke: value }),
}, {
  values: colorsMap,
  type: "color",
});
```

### Dark Mode Implementation

**Theme Switching Logic** (`src/layouts/components/ThemeSwitcher.astro`):

```javascript
function toggleTheme(themeSwitch) {
  const defaultTheme = 
    config.settings.default_theme === "system"
      ? matchMedia.matches ? "dark" : "light"
      : config.settings.default_theme;
      
  const currentTheme = localStorage.getItem("theme") || defaultTheme;
  const isDarkTheme = currentTheme === "dark";

  themeSwitch.forEach((sw) => (sw.checked = isDarkTheme));
  document.documentElement.classList.toggle("dark", isDarkTheme);
}
```

**CSS Variables Application**:
```css
:root {
  --color-primary: #1A1A1A;
  --color-body: #FFFFFF;
  /* ... other light theme variables */
}

.dark {
  --color-primary: #F9FAFB;
  --color-body: #1E1F22;
  /* ... other dark theme variables */
}
```

---

## Typography & Font System

### Heebo Font Family

**Font Configuration**:
- **Primary Font**: Heebo (Google Fonts, self-hosted)
- **Weights Available**: 400 (Regular), 600 (Semi-bold), 700 (Bold), 800 (Extra-bold)
- **Format**: TTF with optimized loading strategy
- **Location**: `public/fonts/heebo/`

**Font Face Declarations** (`public/fonts/heebo/heebo.css`):
```css
@font-face {
  font-family: 'Heebo';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('./heebo-400.ttf') format('truetype');
}

@font-face {
  font-family: 'Heebo';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('./heebo-600.ttf') format('truetype');
}

@font-face {
  font-family: 'Heebo';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('./heebo-700.ttf') format('truetype');
}

@font-face {
  font-family: 'Heebo';
  font-style: normal;
  font-weight: 800;
  font-display: swap;
  src: url('./heebo-800.ttf') format('truetype');
}
```

### Brand Font System

**Paytone One Font Family**:
- **Purpose**: Exclusive brand identity font for "Cole Morton" text
- **Usage**: Limited to brand/logo elements only
- **Format**: Google Fonts with optimized loading strategy
- **Implementation**: Via AstroFont configuration in `Base.astro`

**Font Configuration** (`Base.astro` lines 110-123):
```javascript
<AstroFont
  config={[
    {
      name: "Paytone One",
      fallback: "sans-serif",
      cssVariable: "font-brand",
      googleFontsURL: "https://fonts.googleapis.com/css2?family=Paytone+One:wght@400&display=swap",
      display: "swap"
    }
  ]}
/>
```

**CSS Variable Generation**:
```css
:root {
  --font-brand: 'Paytone One', sans-serif;
}
```

**Brand Text Implementation** (`navigation.css` lines 22-26):
```css
.brand-text {
  font-family: var(--font-brand), sans-serif !important;
  @apply flex items-center;
  transform: translateY(-5px); /* Visual alignment optimization */
}
```

**Usage Locations**:
1. **Navigation Logo** (`Logo.astro`): `<h1 class="brand-text m-0 font-semibold">`
2. **LogoDisplay Component** (`LogoDisplay.tsx`): Reusable component with size variants
3. **Photo Booth/Dashboard Displays**: High-resolution brand representation

## Brand Typography Usage

Cole Morton implements a strategic dual brand approach using the Paytone One font for both personal identity and content attribution. Complete CSS specifications have been extracted using automated browser analysis to ensure pixel-perfect recreation.

### Personal Brand: "Cole Morton"

**Usage Context**: Primary brand identity for website navigation, user interface elements, and direct user interactions.

**Complete CSS Specification** (extracted from rendered browser elements):
```css
.personal-brand-complete {
  font-family: "Paytone One", sans-serif;
  font-size: 72px;
  font-weight: 600;
  line-height: 90px;
  word-spacing: 0px;
  color: rgb(249, 250, 251);
  display: flex;
  align-items: center;
  transform: matrix(1, 0, 0, 1, 0, -5); /* translateY(-5px) */
  margin: 0px;
  padding: 0px;
  text-align: start;
  vertical-align: baseline;
  text-decoration: none solid rgb(249, 250, 251);
  text-transform: none;
  text-shadow: none;
  opacity: 1;
  position: static;
  box-sizing: border-box;
  width: 431.141px;
  height: 90px;
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    font-size: 2rem;
  }
}

/* Simplified implementation using existing classes */
.brand-text {
  font-family: var(--font-brand), sans-serif !important;
  @apply flex items-center;
  transform: translateY(-5px);
}
```

**Implementation Locations**:
- **Navigation Header** (`Logo.astro`): `<h1 class="brand-text m-0 font-semibold">Cole Morton</h1>`
- **Logo Generation Dashboard** (`PhotoBoothDisplay.tsx`): Large display for brand showcase
- **LogoDisplay Component** (`LogoDisplay.tsx`): Reusable component with configurable sizing

### Attribution Brand: "colemorton.com"

**Usage Context**: Website attribution for exported chart images and shareable content to drive traffic back to the website.

**Complete CSS Specification** (extracted from rendered browser elements):
```css
.attribution-brand-complete {
  font-family: "Paytone One", sans-serif;
  font-size: 72px;
  font-weight: 600;
  line-height: 90px;
  word-spacing: 0px;
  color: rgb(249, 250, 251);
  display: flex;
  align-items: center;
  transform: matrix(1, 0, 0, 1, 0, -5); /* translateY(-5px) */
  margin: 0px;
  padding: 0px;
  text-align: start;
  vertical-align: baseline;
  text-decoration: none solid rgb(249, 250, 251);
  text-transform: none;
  text-shadow: none;
  opacity: 1;
  position: static;
  box-sizing: border-box;
  width: 594.367px; /* Wider due to longer text */
  height: 90px;
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
}
```

**Implementation Details**:
```tsx
{isPortfolioHistoryPortrait && (
  <div className="dashboard-footer flex justify-center">
    <h1 className="brand-text text-text-dark dark:text-darkmode-text-dark m-0 mb-8 text-4xl font-semibold">
      colemorton.com
    </h1>
  </div>
)}
```

**Location**: Portfolio History Portrait Dashboard Footer (`PhotoBoothDisplay.tsx` lines 894-898)

### Dark Mode Variations

Both brands automatically adapt to dark mode:
```css
.dark .personal-brand-complete,
.dark .attribution-brand-complete {
  color: rgb(224, 224, 224); /* Adjusted for dark backgrounds */
}
```

### Strategic Rationale

**Personal Brand ("Cole Morton")**:
- Builds personal brand recognition and authority
- Creates direct connection between user and creator
- Emphasizes individual expertise and reputation
- Primary identity for direct user interactions

**Attribution Brand ("colemorton.com")**:
- Drives traffic back to website from shared content
- Maintains professional web presence in exported materials
- Provides clear source attribution for viral/shared content
- Balances personal branding with website marketing goals

### Technical Implementation Notes

- **Font Loading**: Paytone One loaded via Google Fonts with CSS variable `--font-brand`
- **Transform Precision**: `translateY(-5px)` applied as `matrix(1, 0, 0, 1, 0, -5)` for pixel alignment
- **Responsive Strategy**: Font sizes scale down proportionally on mobile devices
- **Color Management**: Uses theme-aware color tokens for light/dark mode compatibility

### Typography Scale System

**Base Configuration**:
- **Base Size**: 16px
- **Scale Ratio**: 1.2 (Major Third)
- **Responsive Strategy**: Mobile-first with desktop overrides

**Calculated Font Sizes**:

| Element | Mobile Size | Desktop Size | Weight | Usage |
|---------|-------------|--------------|--------|-------|
| H1 | 2.69rem (43.04px) | 2.99rem (47.84px) | 800 | Page titles |
| H2 | 2.24rem (35.84px) | 2.49rem (39.84px) | 700 | Section headers |
| H3 | 1.87rem (29.92px) | 2.07rem (33.12px) | 600 | Subsections |
| H4 | 1.56rem (24.96px) | 1.73rem (27.68px) | 600 | Card titles |
| H5 | 1.30rem (20.8px) | 1.44rem (23.04px) | 400 | Small headers |
| H6 | 1.08rem (17.28px) | 1.20rem (19.2px) | 400 | Captions |
| Base | 14.4px | 16px | 400 | Body text |

**CSS Implementation** (`src/styles/base.css`):
```css
:root {
  --font-primary: "Heebo", sans-serif;
  --font-secondary: "Heebo", sans-serif;
}

body {
  @apply bg-body dark:bg-darkmode-body font-primary text-text dark:text-darkmode-text text-base leading-relaxed font-normal;
}

h1, .h1 {
  font-size: 2.6873856rem;
  font-weight: 800;
}

@media (min-width: 768px) {
  h1, .h1 {
    font-size: 2.9859839999999997rem;
  }
}
```

### Font Loading Optimization

**Performance Strategy**:
1. **Self-Hosting**: Heebo fonts eliminate external dependencies
2. **Font-Display Swap**: Ensures text visibility during font load for both font families
3. **Preload Critical Fonts**: Heebo primary weights loaded early
4. **Google Fonts Optimization**: Paytone One loaded via optimized Google Fonts with preconnect
5. **Format Optimization**: TTF format for Heebo, WOFF2 for Paytone One

**Integration with Theme System**:
```javascript
// Font families processed by theme plugin
const fontFamilies = {
  primary: "Heebo, sans-serif",
  secondary: "Heebo, sans-serif",
  brand: "Paytone One, sans-serif" // Brand font via AstroFont
};

// CSS custom properties generated
const fontVars = {
  '--font-primary': 'Heebo, sans-serif',
  '--font-secondary': 'Heebo, sans-serif',
  '--font-brand': 'Paytone One, sans-serif'
};
```

---

## Color System & Palettes

### Semantic Color Architecture

**Color Naming Convention**:
- **Theme Colors**: `primary`, `body`, `border`, `light`, `dark`
- **Text Colors**: `text`, `text-dark`, `text-light`
- **Data Colors**: `primary-data`, `secondary-data`, `tertiary-data`, `quaternary`, `neutral-data`

### Light Theme Color Palette

| Color Name | Hex Value | Usage | CSS Variable |
|------------|-----------|-------|--------------|
| Primary | `#1A1A1A` | Brand color, CTAs | `--color-primary` |
| Body | `#FFFFFF` | Background | `--color-body` |
| Border | `#DDE2E6` | Borders, dividers | `--color-border` |
| Light | `#F5F7FA` | Light backgrounds | `--color-light` |
| Dark | `#1A1A1A` | Dark elements | `--color-dark` |
| Text | `#3E4C59` | Body text | `--color-text` |
| Text Dark | `#1A1A1A` | Headings | `--color-text-dark` |
| Text Light | `#6B7280` | Captions, meta | `--color-text-light` |

### Dark Theme Color Palette

| Color Name | Hex Value | Usage | CSS Variable |
|------------|-----------|-------|--------------|
| Primary | `#F9FAFB` | Brand color, CTAs | `--color-darkmode-primary` |
| Body | `#1E1F22` | Background | `--color-darkmode-body` |
| Border | `#3B3F46` | Borders, dividers | `--color-darkmode-border` |
| Light | `#2A2C2F` | Light backgrounds | `--color-darkmode-light` |
| Dark | `#1E1F22` | Dark elements | `--color-darkmode-dark` |
| Text | `#D1D5DB` | Body text | `--color-darkmode-text` |
| Text Dark | `#F9FAFB` | Headings | `--color-darkmode-text-dark` |
| Text Light | `#9CA3AF` | Captions, meta | `--color-darkmode-text-light` |

### Data Visualization Colors

| Color Name | Hex Value | Usage | CSS Variable |
|------------|-----------|-------|--------------|
| Primary Data | `#00BCD4` | Main data series | `--color-primary-data` |
| Secondary Data | `#9575CD` | Secondary data series | `--color-secondary-data` |
| Tertiary Data | `#4285F4` | Additional data | `--color-tertiary-data` |
| Quaternary | `#FF7043` | Warning/alert data | `--color-quaternary` |
| Neutral Data | `#90A4AE` | Reference data | `--color-neutral-data` |

### Color Usage Examples

**Theme-Aware Background**:
```html
<div class="bg-body dark:bg-darkmode-body">
  Content with theme-aware background
</div>
```

**Text Color Hierarchy**:
```html
<h1 class="text-text-dark dark:text-darkmode-text-dark">Main Heading</h1>
<p class="text-text dark:text-darkmode-text">Body text content</p>
<span class="text-text-light dark:text-darkmode-text-light">Caption text</span>
```

**Data Visualization**:
```html
<div class="bg-primary-data">Chart element</div>
<div class="border-secondary-data">Data border</div>
```

---

## Component Styling Architecture

### CSS Layer Organization

**File Structure** (`src/styles/`):
```
styles/
├── main.css          # Central import and layer definition
├── base.css          # Typography, resets, base styles
├── components.css    # Reusable component styles
├── buttons.css       # Button variants and states
├── navigation.css    # Navigation-specific styling
├── search.css        # Search component styles
├── utilities.css     # Custom utility classes
└── safe.css         # Critical CSS for above-the-fold
```

**Layer Definition** (`src/styles/main.css`):
```css
@import "tailwindcss";
@plugin "../tailwind-plugin/tw-theme";
@plugin "../tailwind-plugin/tw-bs-grid";
@plugin "@tailwindcss/forms";
@plugin "@tailwindcss/typography";

@custom-variant dark (&:where(.dark, .dark *));

@import "./safe.css";
@import "./utilities.css";

@layer base {
  @import "./base.css";
}

@layer components {
  @import "./components.css";
  @import "./navigation.css";
  @import "./buttons.css";
  @import "./search.css";
}
```

### Component Style Patterns

**Section Components**:
```css
.section {
  @apply pb-24 xl:pb-28;
}

.section-sm {
  @apply pb-16 xl:pb-20;
}
```

**Container System**:
```css
.container {
  @apply mx-auto px-4 xl:!max-w-[1320px] 2xl:!max-w-[1600px];
}
```

**Button Variants** (`src/styles/buttons.css`):
```css
.btn {
  @apply inline-block rounded border border-transparent px-5 py-2 font-semibold capitalize transition;
}

.btn-sm {
  @apply rounded-sm px-4 py-1.5 text-sm;
}

.btn-primary {
  @apply border-primary bg-primary dark:border-darkmode-primary dark:text-text-dark dark:bg-darkmode-primary text-white;
}

.btn-outline-primary {
  @apply border-dark text-text-dark hover:bg-dark dark:hover:text-text-dark dark:border-darkmode-primary dark:hover:bg-darkmode-primary bg-transparent hover:text-white dark:text-white;
}
```

**Navigation Components** (`src/styles/navigation.css`):
```css
.navbar {
  @apply relative flex flex-wrap items-center justify-between;
}

.navbar-brand {
  @apply text-text-dark dark:text-darkmode-text-dark text-xl font-semibold;
}

.nav-link {
  @apply text-text-dark dark:text-darkmode-text-dark block origin-center transform-gpu cursor-pointer p-3 font-semibold transition-transform duration-200 hover:[transform:scale(1.08)] lg:px-2 lg:py-3;
  white-space: nowrap;
}
```

**Theme Switcher** (`src/styles/navigation.css`):
```css
.theme-switcher {
  @apply inline-flex;

  label {
    @apply bg-border relative inline-block h-4 w-6 cursor-pointer rounded-2xl lg:w-10;
  }

  input {
    @apply absolute opacity-0;
  }

  span {
    @apply bg-dark absolute -top-1 left-0 flex h-6 w-6 items-center justify-center rounded-full transition-all duration-300 dark:bg-white;
  }

  input:checked + label span {
    @apply lg:left-4;
  }
}
```

### Interactive Component Patterns

**Social Icons**:
```css
.social-icons {
  @apply space-x-4;
}

.social-icons li a {
  @apply bg-primary dark:bg-darkmode-primary dark:text-text-dark flex h-9 w-9 items-center justify-center rounded-sm text-center leading-9 text-white transition-colors duration-200;
}
```

**Notice Components**:
```css
.notice {
  @apply mb-6 rounded-lg border px-8 py-6;
}

.notice.note {
  @apply text-tertiary-data border-current;
}

.notice.tip {
  @apply text-primary-data border-current;
}

.notice.warning {
  @apply text-quaternary border-current;
}
```

**Tab Components**:
```css
.tab {
  @apply border-border dark:border-darkmode-border overflow-hidden rounded-lg border;
}

.tab-nav {
  @apply border-border bg-light dark:border-darkmode-border dark:bg-darkmode-light !m-0 flex !list-none border-b;
}

.tab-nav-item {
  @apply border-border text-text-dark dark:border-light !my-0 cursor-pointer border-b-[3px] !px-8 py-2 text-lg opacity-80;
}
```

---

## Utility Classes & Custom CSS

### Custom Utility Classes

**Background Gradients** (`src/styles/utilities.css`):
```css
@utility bg-gradient {
  @apply dark:from-darkmode-light dark:to-darkmode-body bg-linear-to-b from-[rgba(249,249,249,1)] from-[0.53%] to-white to-[83.28%];
}
```

**Form Elements**:
```css
@utility form-input {
  @apply bg-light text-text-dark placeholder:text-text-light focus:border-primary dark:focus:border-darkmode-primary dark:border-darkmode-border dark:bg-darkmode-light dark:text-darkmode-text-light w-full rounded border-transparent px-6 py-4 focus:ring-transparent;
}

@utility form-label {
  @apply font-secondary text-text-dark dark:text-darkmode-text-light mb-4 block text-xl font-normal;
}
```

**Hero Components**:
```css
@utility hero-image-container {
  @apply max-h-[45vh] overflow-hidden object-cover object-center md:max-h-[60vh];
}
```

### Search Modal Styling

**Modal Structure** (`src/styles/search.css`):
```css
.search-modal {
  @apply invisible fixed top-0 left-0 z-50 flex h-full w-full items-start justify-center opacity-0;
}

.search-modal.show {
  @apply visible opacity-100;
}

.search-wrapper {
  @apply dark:bg-darkmode-body relative z-10 mt-24 w-[660px] max-w-[96%] rounded bg-white shadow-lg;
}

.search-wrapper-header-input {
  @apply focus:border-dark border-border dark:bg-darkmode-light dark:text-darkmode-text dark:border-darkmode-border dark:focus:border-darkmode-primary h-12 w-full rounded-[4px] border border-solid pr-4 pl-10 transition duration-200 outline-none focus:ring-0;
}
```

**Search Results**:
```css
.search-result-item {
  @apply dark:bg-darkmode-body dark:border-darkmode-border border-border relative mb-1 flex scroll-my-[30px] items-start rounded border border-solid bg-white p-4;
}

.search-result-item:hover {
  @apply bg-dark dark:bg-dark;
}

.search-result-item:hover .search-result-item-title {
  @apply text-white;
}
```

---

## Chart & Data Visualization Theming

### Chart Theme Integration

**Theme Context Hook** (`src/utils/chartTheme.ts`):
```typescript
export function getThemeColors(isDarkMode: boolean): ThemeColors {
  const theme = isDarkMode
    ? themeConfig.colors.darkmode
    : themeConfig.colors.default;
  const dataColors = themeConfig.colors.data;

  return {
    primary: theme.theme_color.primary,
    body: theme.theme_color.body,
    border: theme.theme_color.border,
    light: theme.theme_color.light,
    dark: theme.theme_color.dark,
    text: theme.text_color.text,
    textDark: theme.text_color["text-dark"],
    textLight: theme.text_color["text-light"],
    primaryData: dataColors.primary_data,
    secondaryData: dataColors.secondary_data,
    tertiaryData: dataColors.tertiary_data,
    quaternary: dataColors.quaternary,
    neutralData: dataColors.neutral_data,
  };
}
```

**Chart Color Mapping**:
```typescript
export function getChartColors(isDarkMode: boolean) {
  const colors = getThemeColors(isDarkMode);

  return {
    multiStrategy: colors.primaryData,    // #00BCD4 - Cyan for multi-strategy
    buyHold: colors.secondaryData,        // #9575CD - Purple for buy-and-hold
    drawdown: colors.quaternary,          // #FF7043 - Orange for drawdowns/risk
    tertiary: colors.tertiaryData,        // #4285F4 - Blue for additional data
    neutral: colors.neutralData,          // #90A4AE - Gray for neutral/reference
    text: colors.text,
    textDark: colors.textDark,
    textLight: colors.textLight,
    grid: isDarkMode ? "rgba(156, 163, 175, 0.2)" : "rgba(0, 0, 0, 0.1)",
    tick: isDarkMode ? "#9CA3AF" : "#6B7280",
  };
}
```

**Plotly.js Theme Integration**:
```typescript
export function getPlotlyThemeColors(isDarkMode: boolean) {
  const colors = getThemeColors(isDarkMode);

  return {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    font: {
      family: '"Inter", ui-sans-serif, system-ui, -apple-system, sans-serif',
      size: 12,
      color: colors.text,
    },
    titleFont: {
      size: 16,
      color: colors.textDark,
    },
    legendBgColor: isDarkMode
      ? "rgba(31, 41, 55, 0.8)"
      : "rgba(255, 255, 255, 0.8)",
    gridColor: isDarkMode 
      ? "rgba(156, 163, 175, 0.2)" 
      : "rgba(0, 0, 0, 0.1)",
    tickColor: isDarkMode ? "#9CA3AF" : "#6B7280",
  };
}
```

### Chart Type Definitions

**Chart Types** (`src/types/ChartTypes.ts`):
```typescript
export type ChartType =
  | "apple-price"
  | "portfolio-value-comparison"
  | "returns-comparison"
  | "portfolio-drawdowns"
  | "live-signals-equity-curve"
  | "live-signals-benchmark-comparison"
  | "fundamental-revenue-fcf"
  | "fundamental-key-metrics"
  | "fundamental-valuation"
  | "multi-stock-price";

export interface ThemeColors {
  primary: string;
  body: string;
  border: string;
  light: string;
  dark: string;
  text: string;
  textDark: string;
  textLight: string;
  primaryData: string;
  secondaryData: string;
  tertiaryData: string;
  quaternary: string;
  neutralData: string;
}
```

---

## Build System Integration

### Vite Configuration

**TailwindCSS Plugin Setup** (`astro.config.mjs`):
```javascript
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        '@/components': path.resolve('./src/layouts/components'),
        '@/config': path.resolve('./src/config'),
        '@/layouts': path.resolve('./src/layouts'),
        '@/hooks': path.resolve('./src/hooks'),
        '@/types': path.resolve('./src/types'),
        '@': path.resolve('./src')
      }
    }
  }
});
```

**Feature Flag Integration**:
```javascript
const buildTimeFlags = getFeatureFlags();

// Build-time feature flags for dead code elimination
define: {
  ...Object.fromEntries(
    FEATURE_FLAGS
      .filter(flag => flag.buildTimeOptimization)
      .map(flag => {
        const defineName = getBuildDefineName(flag.name);
        const defineValue = buildTimeFlags[flag.name];
        return [defineName, defineValue];
      })
  ),
}
```

### Asset Optimization

**Font Loading Strategy**:
- Self-hosted TTF files in `public/fonts/heebo/`
- Font-display: swap for optimal loading performance
- Preload critical font weights

**CSS Optimization**:
- Layer-based architecture for optimal cascade
- Build-time CSS custom property generation
- Dead code elimination via feature flags

**Bundle Optimization**:
```javascript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'vendor': ['react', 'react-dom'],
        'plotly': ['plotly.js-dist', 'react-plotly.js']
      }
    }
  },
  chunkSizeWarningLimit: 2000,
  minify: 'esbuild'
}
```

---

## Development Guidelines

### Naming Conventions

**CSS Classes**:
- Use semantic naming: `.hero-section`, `.card-content`, `.nav-item`
- Follow BEM methodology for complex components
- Prefix custom utilities with descriptive names

**CSS Variables**:
- Theme colors: `--color-{theme-name}`
- Font properties: `--font-{property}`
- Spacing: `--space-{size}`

**Component Files**:
- Use PascalCase for component files: `ThemeSwitcher.astro`
- Use kebab-case for style files: `theme-switcher.css`

### Best Practices

**Theme Usage**:
```html
<!-- ✅ Good: Use semantic theme colors -->
<div class="bg-body dark:bg-darkmode-body text-text dark:text-darkmode-text">

<!-- ❌ Bad: Use hard-coded colors -->
<div class="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200">
```

**Responsive Design**:
```html
<!-- ✅ Good: Mobile-first responsive -->
<h1 class="text-h1 md:text-h1 font-bold">

<!-- ❌ Bad: Desktop-first -->
<h1 class="lg:text-4xl text-2xl font-bold">
```

**Component Styling**:
```html
<!-- ✅ Good: Use component classes -->
<button class="btn btn-primary">

<!-- ❌ Bad: Inline utility overload -->
<button class="inline-block rounded border border-transparent px-5 py-2 font-semibold">
```

### Performance Considerations

**Font Loading**:
- Use `font-display: swap` for all font faces
- Preload critical font weights
- Minimize font variation usage

**CSS Optimization**:
- Use CSS custom properties for theme values
- Leverage Tailwind's purge functionality
- Group related styles in component classes

**JavaScript Integration**:
- Minimize runtime theme calculations
- Use CSS custom properties for dynamic theming
- Implement efficient theme switching

### Accessibility Guidelines

**Color Contrast**:
- Maintain WCAG AA compliance (4.5:1 ratio)
- Test both light and dark theme variants
- Use theme-aware focus indicators

**Typography**:
- Maintain readable line heights (1.5+ for body text)
- Use appropriate heading hierarchy
- Ensure sufficient font sizes (16px minimum)

**Interactive Elements**:
```html
<!-- ✅ Good: Accessible theme switcher -->
<label for="theme-switcher">
  <span class="sr-only">Toggle dark mode</span>
  <input id="theme-switcher" type="checkbox" data-theme-switcher />
</label>
```

---

## Technical Reference

### Complete CSS Custom Properties

**Theme Colors** (Generated from theme.json):
```css
:root {
  /* Light theme colors */
  --color-primary: #1A1A1A;
  --color-body: #FFFFFF;
  --color-border: #DDE2E6;
  --color-light: #F5F7FA;
  --color-dark: #1A1A1A;
  --color-text: #3E4C59;
  --color-text-dark: #1A1A1A;
  --color-text-light: #6B7280;
  
  /* Data colors */
  --color-primary-data: #00BCD4;
  --color-secondary-data: #9575CD;
  --color-tertiary-data: #4285F4;
  --color-quaternary: #FF7043;
  --color-neutral-data: #90A4AE;
  
  /* Font properties */
  --font-primary: "Heebo", sans-serif;
  --font-secondary: "Heebo", sans-serif;
  --font-brand: "Paytone One", sans-serif;
  --text-base: 16px;
  --text-base-sm: 12.8px;
  --text-h1: 2.6873856rem;
  --text-h2: 2.239488rem;
  --text-h3: 1.86624rem;
  --text-h4: 1.5552rem;
  --text-h5: 1.296rem;
  --text-h6: 1.08rem;
}

.dark {
  /* Dark theme color overrides */
  --color-primary: #F9FAFB;
  --color-body: #1E1F22;
  --color-border: #3B3F46;
  --color-light: #2A2C2F;
  --color-dark: #1E1F22;
  --color-text: #D1D5DB;
  --color-text-dark: #F9FAFB;
  --color-text-light: #9CA3AF;
}
```

### Available Utility Classes

**Theme-Aware Background**:
- `bg-primary` / `bg-darkmode-primary`
- `bg-body` / `bg-darkmode-body`
- `bg-light` / `bg-darkmode-light`
- `bg-dark` / `bg-darkmode-dark`

**Theme-Aware Text**:
- `text-text` / `text-darkmode-text`
- `text-text-dark` / `text-darkmode-text-dark`
- `text-text-light` / `text-darkmode-text-light`

**Data Visualization Colors**:
- `bg-primary-data`, `text-primary-data`, `border-primary-data`
- `bg-secondary-data`, `text-secondary-data`, `border-secondary-data`
- `bg-tertiary-data`, `text-tertiary-data`, `border-tertiary-data`
- `bg-quaternary`, `text-quaternary`, `border-quaternary`
- `bg-neutral-data`, `text-neutral-data`, `border-neutral-data`

**Typography Utilities**:
- `font-primary`, `font-secondary`, `font-brand`
- `text-base`, `text-base-sm`
- `text-h1`, `text-h2`, `text-h3`, `text-h4`, `text-h5`, `text-h6`

**Custom Utilities**:
- `bg-gradient` - Theme-aware gradient background
- `form-input` - Styled form input with theme support
- `form-label` - Styled form label with theme support
- `hero-image-container` - Responsive hero image container

**Brand Typography**:
- `brand-text` - Brand font styling with visual alignment optimization

### Component Class Reference

**Layout Components**:
```css
.section        /* Section spacing */
.section-sm     /* Smaller section spacing */
.container      /* Main container with max-width */
```

**Navigation Components**:
```css
.navbar         /* Main navigation bar */
.navbar-brand   /* Brand/logo area */
.navbar-nav     /* Navigation list */
.nav-item       /* Individual nav item */
.nav-link       /* Navigation link */
.nav-dropdown   /* Dropdown container */
```

**Button Components**:
```css
.btn            /* Base button */
.btn-sm         /* Small button */
.btn-primary    /* Primary button variant */
.btn-outline-primary /* Outlined primary button */
```

**Theme Components**:
```css
.theme-switcher /* Theme switcher container */
```

**Notice Components**:
```css
.notice         /* Base notice */
.notice.note    /* Note variant */
.notice.tip     /* Tip variant */
.notice.info    /* Info variant */
.notice.warning /* Warning variant */
```

**Tab Components**:
```css
.tab            /* Tab container */
.tab-nav        /* Tab navigation */
.tab-nav-item   /* Individual tab */
.tab-content    /* Tab content area */
```

### Integration Examples

**React Component with Theme**:
```tsx
import { getThemeColors } from '@/utils/chartTheme';
import { useTheme } from '@/hooks/useTheme';

function ThemedComponent() {
  const theme = useTheme();
  const colors = getThemeColors(theme === 'dark');
  
  return (
    <div className="bg-body dark:bg-darkmode-body">
      <h1 className="text-text-dark dark:text-darkmode-text-dark">
        Themed Content
      </h1>
    </div>
  );
}
```

**Astro Component with Theme Classes**:
```astro
---
// Component logic
---
<section class="section bg-body dark:bg-darkmode-body">
  <div class="container">
    <h2 class="text-text-dark dark:text-darkmode-text-dark font-secondary">
      Section Title
    </h2>
    <p class="text-text dark:text-darkmode-text">
      Section content with theme-aware styling.
    </p>
  </div>
</section>
```

**Brand Font Usage Examples**:
```astro
<!-- Navigation Logo (Logo.astro) -->
<a href="/" class="navbar-brand inline-block">
  <h1 class="brand-text m-0 font-semibold">Cole Morton</h1>
</a>
```

```tsx
// LogoDisplay React Component with size variants
<div className="logo-display-container">
  <h1 className={`brand-text m-0 font-semibold text-text-dark dark:text-darkmode-text-dark ${sizeClasses}`}>
    Cole Morton
  </h1>
</div>
```

```css
/* Custom brand styling */
.custom-brand-element {
  font-family: var(--font-brand), sans-serif;
  @apply text-text-dark dark:text-darkmode-text-dark;
  transform: translateY(-5px); /* Optical alignment */
}
```

**CSS Custom Component**:
```css
.custom-card {
  @apply bg-light dark:bg-darkmode-light border border-border dark:border-darkmode-border rounded-lg p-6;
}

.custom-card-title {
  @apply text-text-dark dark:text-darkmode-text-dark font-secondary text-xl font-semibold mb-4;
}

.custom-card-content {
  @apply text-text dark:text-darkmode-text leading-relaxed;
}
```

---

## Conclusion

This style guide provides comprehensive documentation for the Cole Morton frontend styling system. The architecture emphasizes:

- **Performance**: Self-hosted fonts, optimized CSS delivery, build-time optimizations
- **Maintainability**: Centralized theme configuration, systematic naming conventions
- **Scalability**: Plugin-based architecture, component-focused styling patterns
- **User Experience**: Smooth theme transitions, accessible design patterns
- **Developer Experience**: TypeScript integration, clear documentation, consistent patterns

For updates or questions about the styling system, refer to the source files mentioned throughout this guide or consult the development team.

---

**Document Version**: 1.0.0  
**Last Updated**: September 2025  
**Next Review**: December 2025