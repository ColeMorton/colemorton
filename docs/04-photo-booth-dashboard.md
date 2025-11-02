# Photo Booth & Dashboard System

**Version**: 2.1 | **Last Updated**: 2024-08-27 | **Status**: Production Ready
**Authority**: Product Team | **Audience**: Developers & System Architects

Technical reference for photo booth, dashboard, chart and export systems.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Photo Booth System](#2-photo-booth-system)
3. [Dashboard Architecture](#3-dashboard-architecture)
4. [Chart Data Solutions](#4-chart-data-solutions)
5. [Chart Components](#5-chart-components)
6. [Image Export System](#6-image-export-system)
7. [APIs](#7-apis)
8. [File Structure](#8-file-structure)

---

## 1. System Overview

**Technology Stack**:
- Frontend: Astro 5.7+ with React islands, TailwindCSS 4+
- Charts: Plotly.js for interactive visualizations
- Export: Puppeteer + Sharp.js for image generation
- Backend: Python scripts with pandas, matplotlib, plotly
- Data: CSV files with dedicated service layer

**Architecture**:
```
Python Scripts → CSV Data → Frontend → Photo Booth Export
     ↓              ↓          ↓           ↓
Dashboard Gen  → API Layer → Chart Display → PNG/SVG Output
```

---

## 2. Photo Booth System

### PhotoBoothDisplay Component
**File**: `frontend/src/layouts/shortcodes/PhotoBoothDisplay.tsx`

React component providing dashboard preview and export functionality.

**State Management**:
```typescript
interface PhotoBoothState {
  selectedDashboard: string;
  currentMode: "light" | "dark";
  selectedFormat: "png" | "svg" | "both";
  selectedAspectRatio: "16:9" | "4:3" | "3:4";
  selectedDPI: 150 | 300 | 600;
  selectedScaleFactor: 2 | 3 | 4;
  isReady: boolean;
  isExporting: boolean;
}
```

#### ConditionalPhotoBoothDisplay Component
**Location**: `frontend/src/layouts/shortcodes/ConditionalPhotoBoothDisplay.tsx`
**Type**: Conditional wrapper component
**Purpose**: Feature flag integration for photo booth visibility

#### PhotoBoothBase Component
**Location**: `frontend/src/layouts/PhotoBoothBase.astro`
**Type**: Astro layout component
**Purpose**: Base layout with SEO meta tags and styling

### 2.2 Configuration System

#### Photo Booth Configuration
**File**: `frontend/src/config/photo-booth.json`
**Structure**:

```json
{
  "default_dashboard": "trading_performance",
  "active_dashboards": [
    {
      "id": "trading_performance",
      "name": "Trading Performance Dashboard",
      "file": "trading-performance.mdx",
      "description": "Comprehensive trading strategy performance overview",
      "layout": "2x2_grid",
      "enabled": true
    },
    {
      "id": "portfolio_analysis",
      "name": "Portfolio Analysis Dashboard",
      "file": "portfolio-analysis.mdx",
      "description": "Portfolio composition and risk analysis",
      "layout": "1x3_stack",
      "enabled": true
    },
    {
      "id": "portfolio_history_portrait",
      "name": "Portfolio History Portrait",
      "file": "portfolio-history-portrait.mdx",
      "description": "Portfolio trading history with waterfall and time series analysis",
      "layout": "2x1_stack",
      "enabled": true
    },
    {
      "id": "market_overview",
      "name": "Market Overview Dashboard",
      "file": "market-overview.mdx",
      "description": "Market trends and sector analysis",
      "layout": "2x2_grid",
      "enabled": false
    }
  ],
  "screenshot_settings": {
    "viewport": { "width": 1920, "height": 1080 },
    "device_scale_factor": 2,
    "format": "png",
    "quality": 95,
    "full_page": false,
    "timeout": 30000,
    "wait_for_selector": ".photo-booth-ready"
  },
  "export_options": {
    "formats": {
      "available": ["png", "svg", "both"],
      "default": "png",
      "descriptions": {
        "png": "High-resolution raster image, perfect for presentations and print",
        "svg": "Vector-based image with infinite scalability and small file size",
        "both": "Generate both PNG and SVG formats simultaneously"
      }
    },
    "aspect_ratios": {
      "available": [
        {
          "id": "16:9",
          "name": "Widescreen (16:9)",
          "dimensions": { "width": 1920, "height": 1080 },
          "description": "Standard widescreen format, ideal for monitors and web"
        },
        {
          "id": "4:3",
          "name": "Traditional (4:3)",
          "dimensions": { "width": 1440, "height": 1080 },
          "description": "Classic presentation format, ideal for projectors"
        },
        {
          "id": "3:4",
          "name": "Portrait (3:4)",
          "dimensions": { "width": 1080, "height": 1440 },
          "description": "Portrait orientation, ideal for social media and mobile"
        }
      ],
      "default": "16:9"
    },
    "dpi_settings": {
      "available": [150, 300, 600],
      "default": 300,
      "descriptions": {
        "150": "Web/Digital - Standard screen resolution",
        "300": "Print/Professional - High-quality printing standard",
        "600": "Ultra-High - Professional publishing and large format"
      }
    },
    "scale_factors": {
      "available": [2, 3, 4],
      "default": 3,
      "descriptions": {
        "2": "Standard high-DPI (2x resolution)",
        "3": "Enhanced high-DPI (3x resolution)",
        "4": "Ultra high-DPI (4x resolution)"
      }
    }
  },
  "output": {
    "directory": "data/outputs/photo-booth",
    "filename_template": "{dashboard_id}_{mode}_{aspect_ratio}_{format}_{dpi}dpi_{timestamp}.{extension}",
    "legacy_filename_template": "{dashboard_id}_{mode}_{timestamp}.png",
    "modes": ["light", "dark"],
    "auto_cleanup": {
      "enabled": true,
      "keep_latest": 10,
      "older_than_days": 30
    }
  },
  "performance": {
    "preload_charts": true,
    "render_timeout": 15000,
    "retry_attempts": 3,
    "cache_bust": false
  },
  "data_dependencies": {
    "enabled": true,
    "config_path": "./chart-data-dependencies.json",
    "show_status_indicators": true,
    "allow_manual_refresh": true,
    "refresh_policies": {
      "auto_refresh_on_stale": false,
      "refresh_on_dashboard_load": true,
      "background_monitoring": true,
      "file_watching": true
    },
    "status_display": {
      "show_compact_indicators": true,
      "show_detailed_dashboard": false,
      "alert_on_stale_data": true,
      "alert_threshold_hours": 12
    },
    "integration": {
      "cli_services_enabled": true,
      "cli_rate_limiting": true,
      "file_monitoring": true,
      "cache_coordination": true
    }
  },
  "dashboard_data_mapping": {
    "trading_performance": {
      "primary_charts": [
        "portfolio-value-comparison",
        "returns-comparison",
        "live-signals-equity-curve",
        "trade-pnl-waterfall"
      ],
      "data_freshness_requirements": {
        "warning_threshold_hours": 6,
        "error_threshold_hours": 24
      },
      "refresh_priority": "high"
    },
    "portfolio_analysis": {
      "primary_charts": ["portfolio-drawdowns", "open-positions-pnl-timeseries", "closed-positions-pnl-timeseries"],
      "data_freshness_requirements": {
        "warning_threshold_hours": 12,
        "error_threshold_hours": 48
      },
      "refresh_priority": "medium"
    },
    "portfolio_history_portrait": {
      "primary_charts": ["trade-pnl-waterfall", "closed-positions-pnl-timeseries", "live-signals-weekly-candlestick"],
      "data_freshness_requirements": {
        "warning_threshold_hours": 24,
        "error_threshold_hours": 72
      },
      "refresh_priority": "low"
    },
    "market_overview": {
      "primary_charts": ["live-signals-benchmark-comparison", "apple-stock"],
      "data_freshness_requirements": {
        "warning_threshold_hours": 2,
        "error_threshold_hours": 8
      },
      "refresh_priority": "high"
    }
  }
}
```

#### Configuration Sections Explained

**Data Dependencies Configuration**:
- **File Watching**: Monitors data file changes for automatic invalidation
- **Refresh Policies**: Controls when and how data refreshes occur
- **Status Display**: Configures visual indicators for data freshness
- **CLI Integration**: Enables coordination with backend data pipeline

**Dashboard Data Mapping**:
- **Primary Charts**: Lists core chart types for each dashboard
- **Freshness Requirements**: Time-based thresholds for data staleness warnings
- **Refresh Priority**: Determines update priority during bulk operations

**Performance Configuration**:
- **Chart Preloading**: Enables background chart rendering for faster display
- **Render Timeout**: Maximum wait time for chart initialization (15 seconds)
- **Retry Logic**: Automatic retry attempts for failed operations
- **Cache Busting**: Controls cache invalidation strategies

### 2.3 URL Parameter System

**Supported Parameters**:
- `dashboard`: Dashboard ID to display
- `mode`: Theme mode (`light` | `dark`)
- `format`: Export format (`png` | `svg` | `both`)
- `aspect_ratio`: Aspect ratio (`16:9` | `4:3` | `3:4`)
- `dpi`: DPI setting (150 | 300 | 600)
- `scale`: Scale factor (2 | 3 | 4)

**Example URL**:
```
/photo-booth?dashboard=trading_performance&mode=dark&format=png&aspect_ratio=16:9&dpi=300&scale=3
```

### 2.4 Feature Flag Integration

**Config Location**: `frontend/src/lib/config.ts`
**Feature Flag**: `features.photoBooth`
**Behavior**: Redirects to 404 when disabled

---

## 3. Dashboard Architecture

### Configuration
**Files**:
- `frontend/src/config/photo-booth.json` - Primary configuration
- `frontend/src/pages/api/dashboards.json.ts` - API endpoint
- `frontend/src/content/dashboards/*.mdx` - Dashboard content

### Available Dashboards
1. **trading_performance** - File: `trading-performance.mdx`, Layout: 2x2_grid
2. **portfolio_analysis** - File: `portfolio-analysis.mdx`, Layout: 1x3_stack
3. **portfolio_history_portrait** - File: `portfolio-history-portrait.mdx`, Layout: 2x1_stack
4. **market_overview** - Disabled (enabled: false)

### Layout System
**File**: `frontend/src/services/dashboardLoader.ts`

```typescript
const layoutMappings: Record<string, string> = {
  "2x2_grid": "grid grid-cols-1 gap-6 lg:grid-cols-2 h-full",
  "1x3_stack": "flex flex-col gap-6 h-full",
  "2x1_stack": "flex flex-col h-full",
  "3x1_row": "grid grid-cols-1 gap-6 lg:grid-cols-3 h-full",
  "1x2_column": "grid grid-cols-1 gap-6 lg:grid-cols-2 h-full"
}
```

#### Responsive Design
- **Mobile**: Single column stack layout
- **Desktop**: Multi-column grid layouts based on configuration
- **Breakpoints**: Tailwind `lg:` breakpoint (1024px+)

### 3.2 Dashboard Renderer Component

**Location**: PhotoBoothDisplay.tsx (lines 575-634)
**Purpose**: Renders actual dashboard content with theme and layout support

**Key Features**:
- Dynamic layout class application
- Special handling for portrait dashboards
- Header/footer sections for branded dashboards
- Theme-aware styling

---

## 4. Chart Data Solutions

### 4.1 Data Service Architecture

#### ChartDataService Class
**Location**: `frontend/src/services/ChartDataService.ts`
**Purpose**: Centralized data fetching, caching, and CSV parsing

**Cache Management**:
- **Portfolio Data**: 5-minute cache duration
- **Live Signals**: Dedicated cache with timestamp validation
- **Trade History**: Separate cache for waterfall and position data
- **Benchmark Data**: SPY, QQQ, BTC-USD data caching

**CSV Parsing Methods**:
```typescript
class ChartDataService {
  private parseCSV(csvText: string): StockDataRow[]
  private parsePortfolioCSV(csvText: string): PortfolioDataRow[]
  private parseLiveSignalsCSV(csvText: string): LiveSignalsDataRow[]
  private parseTradeHistoryCSV(csvText: string): TradeHistoryDataRow[]
  private parseOpenPositionsPnLCSV(csvText: string): OpenPositionPnLDataRow[]
  private parseLiveSignalsBenchmarkCSV(csvText: string): LiveSignalsBenchmarkDataRow[]
}
```

### 4.2 Data Hook System

#### Portfolio Data Hooks
**Location**: `frontend/src/hooks/usePortfolioData.ts`

**Available Hooks**:
- `useAppleStockData()`: Legacy stock data for reference charts
- `usePortfolioData(chartType)`: Smart hook that switches data based on chart type
- `useLiveSignalsData()`: Live trading signals with MFE/MAE analysis
- `useTradeHistoryData()`: Closed trade history for waterfall charts
- `useOpenPositionsPnLData()`: Open position performance tracking
- `useClosedPositionsPnLData()`: Closed position historical performance
- `useLiveSignalsBenchmarkData()`: Portfolio vs. market benchmark comparison
- `useWaterfallTradeData()`: Pre-sorted trade data for waterfall visualization

**Hook Pattern**:
```typescript
interface DataServiceResponse<T> {
  data: T;
  loading: boolean;
  error: string | null;
}
```

### 4.3 Data Types & Structures

#### Core Data Interfaces
**Location**: `frontend/src/types/ChartTypes.ts`

**Portfolio Data Structure**:
```typescript
interface PortfolioDataRow {
  Date: string;
  Portfolio_Value?: string;
  Normalized_Value?: string;
  Cumulative_Returns?: string;
  Cumulative_Returns_Pct?: string;
  Drawdown?: string;
  Drawdown_Pct?: string;
  // Additional fields...
}
```

**Live Signals Structure**:
```typescript
interface LiveSignalsDataRow {
  timestamp: string;
  equity: string;
  equity_pct: string;
  drawdown: string;
  mfe: string; // Maximum Favorable Excursion
  mae: string; // Maximum Adverse Excursion
}
```

**Trade History Structure**:
```typescript
interface TradeHistoryDataRow {
  Position_UUID: string;
  Ticker: string;
  Entry_Timestamp: string;
  Exit_Timestamp: string;
  PnL: string;
  Direction: string;
  // Additional trade metadata...
}
```

### 4.4 Data Quality & Validation

#### Enhanced Data Validation
**ChartDataService** now includes comprehensive data quality monitoring:

```typescript
// Data validation with quality assessment
validateCSVData(data: any[], dataType: string): {
  isValid: boolean;
  issues: string[];
  recordCount: number;
}

// Data freshness monitoring
checkDataFreshness(endpoint: string): Promise<{
  isFresh: boolean;
  ageHours: number;
  lastModified?: string;
}>

// Comprehensive quality reporting
getDataQualityReport(): Promise<{
  overall: "healthy" | "warning" | "error";
  categories: {
    [key: string]: {
      status: "healthy" | "warning" | "error";
      recordCount: number;
      issues: string[];
      freshness: { isFresh: boolean; ageHours: number; };
    };
  };
  generatedAt: string;
}>
```

#### Data Validation Methods
**Enhanced validation features**:
- **Schema Validation**: Required field presence and type checking
- **Freshness Monitoring**: HTTP header-based age detection with 24-hour thresholds
- **Data Completeness**: Row count validation and missing data detection
- **Cross-Category Validation**: Live signals, trade history, and portfolio data consistency

#### Cache Management Enhancements
**Advanced caching system**:
- **Multi-level Caching**: Portfolio, live signals, trade history, benchmark, and open positions
- **Cache Status Reporting**: Validity, freshness, and data quality indicators
- **Intelligent Invalidation**: Time-based and event-driven cache clearing
- **Memory Optimization**: Automatic cleanup and resource management

#### Enhanced Data Methods
**Validation-enabled data fetching**:
```typescript
// Enhanced data fetching with validation
fetchLiveSignalsDataWithValidation(): Promise<{
  data: LiveSignalsDataRow[];
  validation: { isValid: boolean; issues: string[]; recordCount: number; };
  freshness: { isFresh: boolean; ageHours: number; lastModified?: string; };
}>

fetchTradeHistoryDataWithValidation(): Promise<{
  data: TradeHistoryDataRow[];
  validation: { isValid: boolean; issues: string[]; recordCount: number; };
  freshness: { isFresh: boolean; ageHours: number; lastModified?: string; };
}>

// Cache status monitoring
getCacheStatus(): {
  isValid: boolean;
  lastFetched?: number;
  hasData: boolean;
  dataQuality?: "unknown" | "healthy" | "warning" | "error";
}

// Manual cache management
clearCache(): void
```

### 4.5 Data Flow Pipeline

1. **Backend Generation**: Python scripts generate CSV files in `data/outputs/`
2. **Frontend Request**: React hooks trigger data fetching via ChartDataService
3. **CSV Processing**: Service parses CSV text into typed interfaces
4. **Data Validation**: Quality assessment and freshness checking
5. **Cache Management**: Data stored with timestamp-based invalidation and quality metrics
6. **Component Consumption**: Chart components receive typed, validated data with quality indicators

---

## 5. Chart Components

### ChartDisplay Component
**File**: `frontend/src/layouts/shortcodes/ChartDisplay.tsx`

**Supported Chart Types**:
```typescript
type ChartType =
  | "apple-stock"
  | "portfolio-value-comparison"
  | "returns-comparison"
  | "portfolio-drawdowns"
  | "live-signals-equity-curve"
  | "live-signals-benchmark-comparison"
  | "live-signals-drawdowns"
  | "live-signals-weekly-candlestick"
  | "trade-pnl-waterfall"
  | "open-positions-pnl-timeseries"
  | "closed-positions-pnl-timeseries"
```

**Props Interface**:
```typescript
interface ChartDisplayProps {
  title: string;
  category?: string;
  description?: string;
  chartType?: ChartType;
  timeframe?: "daily" | "weekly";
  indexed?: boolean;
  positionType?: "open" | "closed" | "auto";
  className?: string;
  titleOnly?: boolean;
}
```

### 5.3 Portfolio Chart Component

**Location**: `frontend/src/layouts/components/charts/PortfolioChart.tsx`
**Purpose**: Core chart data processing and Plotly.js integration

**Key Features**:
- **Dark Mode Detection**: Automatic theme switching with DOM observation
- **Data Transformation**: Convert raw CSV data to Plotly.js format
- **Smart Position Handling**: Auto-switch between open/closed position data
- **Weekly Aggregation**: Convert daily data to weekly OHLC for candlestick charts
- **Indexed Data Creation**: Generate synthetic entry points for position tracking
- **Legend Management**: Dynamic legend visibility based on data volume

**Chart-Specific Processing**:

1. **Portfolio Value Comparison**: Multi-strategy vs. buy-and-hold visualization
2. **Returns Comparison**: Daily percentage returns overlay
3. **Drawdown Analysis**: Filled area charts with risk visualization
4. **Live Signals MFE/MAE**: Maximum favorable/adverse excursion tracking
5. **Waterfall Charts**: Trade-by-trade PnL contribution analysis
6. **Position Time Series**: Individual position performance tracking
7. **Weekly Candlesticks**: OHLC aggregation from daily equity data

### 5.4 Chart Container Component

**Location**: `frontend/src/layouts/components/charts/ChartContainer.tsx`
**Purpose**: Consistent layout, styling, and metadata display

**Layout Features**:
- **Responsive Design**: Mobile-first layout with desktop enhancements
- **Theme Integration**: Dark/light mode support
- **Title-Only Mode**: Special mode for branded photo booth exports
- **Category Labels**: Uppercase tracking for chart organization
- **Description Support**: Rich text descriptions with theme-aware styling

### 5.5 Theme Integration

**Location**: `frontend/src/utils/chartTheme.ts`
**Purpose**: Centralized theme management for charts

**Color Palette**:
```typescript
const chartColors = {
  multiStrategy: "#00BCD4", // Cyan for active strategies
  buyHold: "#9575CD",       // Purple for buy-and-hold
  drawdown: "#FF7043",      // Orange for risk/drawdowns
  tertiary: "#4285F4",      // Blue for additional data
  neutral: "#90A4AE",       // Gray for neutral/reference
}
```

**Plotly Theme Integration**:
- **Transparent Backgrounds**: Paper and plot backgrounds set to transparent
- **Font Integration**: Inter font family with system fallbacks
- **Grid Styling**: Theme-aware grid colors and tick formatting
- **Legend Styling**: Positioned legends with theme-appropriate backgrounds

---

## 6. Image Export System

### 6.1 Export Pipeline Architecture

```
Frontend Request → API Endpoint → Python Script → Puppeteer → Sharp Processing → File Output
     │                 │              │             │            │               │
     ▼                 ▼              ▼             ▼            ▼               ▼
Export Controls  /api/export-    photo_booth_   Screenshot   Image Processing  Final Files
& Parameters     dashboard.ts    generator.py   Capture      & Optimization   in data/outputs/
```

### 6.2 Frontend Export Controls

**Location**: PhotoBoothDisplay component (lines 208-571)

**Export Options**:
- **Format Selection**: PNG, SVG, or both formats simultaneously
- **Aspect Ratio**: 16:9 (1920×1080), 4:3 (1440×1080), 3:4 (1080×1440)
- **DPI Settings**: 150 (web), 300 (print), 600 (ultra)
- **Scale Factors**: 2x, 3x, 4x for high-DPI displays
- **Mode Selection**: Light or dark theme export

**Export Process**:
1. User configures export parameters
2. Frontend validates ready state (charts loaded, no errors)
3. POST request to `/api/export-dashboard` with parameters
4. Real-time status updates and progress indication
5. Success confirmation with generated file paths

### 6.3 API Endpoint Implementation

**Location**: `frontend/src/pages/api/export-dashboard.ts`
**Method**: POST with JSON payload
**Purpose**: Bridge between frontend controls and Python export script

**Request Interface**:
```typescript
interface ExportRequest {
  dashboard_id: string;
  mode: "light" | "dark";
  aspect_ratio: "16:9" | "4:3" | "3:4";
  format: "png" | "svg" | "both";
  dpi: 150 | 300 | 600;
  scale_factor: 2 | 3 | 4;
}
```

**Process Flow**:
1. Validate required export parameters
2. Build Python script arguments array
3. Spawn `photo_booth_generator.py` process
4. Capture stdout/stderr for progress tracking
5. Parse generated file paths from output
6. Return success/error response with file list

### 6.4 Python Export Script

**Location**: `scripts/photo_booth_generator.py`
**Purpose**: High-resolution dashboard screenshot generation

**Key Features**:
- **Server Status Check**: Validates Astro dev server accessibility
- **Puppeteer Integration**: Headless Chrome screenshot capture
- **Sharp Processing**: PNG optimization and DPI setting
- **SVG Export**: Vector format generation for scalable graphics
- **Multi-format Support**: Simultaneous PNG and SVG generation

**Export Process**:
1. **Server Validation**: Check if localhost:4321 is accessible
2. **URL Construction**: Build photo booth URL with parameters
3. **Puppeteer Script Generation**: Create temporary Node.js script
4. **Screenshot Capture**: Wait for `.photo-booth-ready` selector
5. **UI Element Hiding**: Remove controls, dev toolbar, navigation
6. **Image Processing**: Apply DPI settings and optimization
7. **File Management**: Save to `data/outputs/photo-booth/`

**Filename Template**:
```
{dashboard_id}_{mode}_{aspect_ratio}_{format}_{dpi}dpi_{timestamp}.{extension}
```

Example: `trading_performance_dark_16x9_png_300dpi_20250810_143052.png`

### 6.5 Quality Standards

**PNG Export**:
- **Quality**: 95% JPEG quality for PNG-compatible compression
- **Color Depth**: 24-bit color with alpha channel support
- **DPI Metadata**: Embedded DPI information for print applications
- **Optimization**: Sharp.js processing for file size optimization

**SVG Export**:
- **Vector Accuracy**: Precise mathematical representation
- **Font Embedding**: System font fallbacks with web font references
- **Scalability**: Infinite resolution scaling capability
- **File Size**: Optimized SVG markup with minimal redundancy

**Screenshot Process**:
- **Wait Strategy**: Selector-based ready state detection
- **Viewport Accuracy**: Exact pixel dimensions per aspect ratio
- **Element Hiding**: Clean removal of UI controls and dev tools
- **Rendering Timeout**: 30-second maximum wait for chart completion

### 6.6 Enhanced Export Features

#### Auto-Cleanup and File Management
**Configuration**: `output.auto_cleanup` in photo-booth.json
- **Automatic Cleanup**: Removes old export files based on retention policies
- **Keep Latest**: Maintains 10 most recent exports per dashboard
- **Age-based Removal**: Deletes files older than 30 days
- **Smart Organization**: Organized file structure with descriptive filenames

#### Advanced Error Handling
**Export Pipeline Resilience**:
- **Parameter Validation**: Comprehensive input validation with detailed error messages
- **Process Monitoring**: Real-time Python script execution monitoring
- **Timeout Management**: Configurable timeout limits with graceful degradation
- **Error Context**: Detailed error reporting with troubleshooting guidance
- **Retry Logic**: Automatic retry attempts for transient failures

```typescript
// Enhanced error response structure
interface ExportErrorResponse {
  success: false;
  error: string;
  error_code: "VALIDATION_ERROR" | "PROCESS_TIMEOUT" | "SCRIPT_ERROR" | "NETWORK_ERROR";
  details: {
    dashboard_id?: string;
    parameters?: ExportRequest;
    python_output?: string;
    execution_time?: number;
  };
  retry_suggested: boolean;
  troubleshooting_steps: string[];
}
```

#### Export Status Tracking
**Real-time Progress Monitoring**:
- **Status Updates**: Live progress indication during export operations
- **Processing Time**: Accurate execution time reporting
- **File Generation**: Real-time file path reporting as files are created
- **Success Confirmation**: Detailed success reporting with generated file list

#### Enhanced Filename Templates
**Flexible Naming System**:
- **Standard Template**: `{dashboard_id}_{mode}_{aspect_ratio}_{format}_{dpi}dpi_{timestamp}.{extension}`
- **Legacy Support**: Backward compatibility with simple naming convention
- **Timestamp Precision**: Accurate timestamp formatting for unique file identification
- **Format Indicators**: Clear format and quality indicators in filenames

Example Filenames:
```
trading_performance_dark_16x9_png_300dpi_20250820_143052.png
portfolio_analysis_light_4x3_svg_600dpi_20250820_143127.svg
portfolio_history_portrait_dark_3x4_both_150dpi_20250820_143201.png
portfolio_history_portrait_dark_3x4_both_150dpi_20250820_143201.svg
```

---

## 7. APIs

### `/api/dashboards.json`
GET endpoint returning dashboard configurations.

**Response Structure**:
```typescript
interface DashboardResponse {
  success: boolean;
  dashboards: DashboardConfig[];
  timestamp: string;
  source: "static_config" | "content_collection";
}
```

#### Export API
**Endpoint**: `/api/export-dashboard`
**Method**: POST
**Purpose**: Generate high-resolution dashboard exports
**Timeout**: 2-minute process timeout with progress tracking

**Error Handling**:
- Parameter validation with detailed error messages
- Python script execution monitoring
- Graceful failure with cleanup and retry guidance
- File path parsing and verification

### 7.2 Backend Integration

#### Python Script Integration
**Scripts Location**: `scripts/`

**Key Scripts**:
1. **`photo_booth_generator.py`**: Primary export script
2. **`dashboard_generator.py`**: Static dashboard image generation
3. **`plotly_dashboard_generator.py`**: Plotly-specific dashboard rendering

**Integration Pattern**:
```typescript
const pythonProcess = spawn("python3", args, {
  cwd: path.resolve(process.cwd(), ".."),
  stdio: ["pipe", "pipe", "pipe"],
});
```

#### Data Pipeline Integration
**CSV Data Sources**: `data/outputs/` directory structure
**Processing Scripts**: Python data generation scripts
**File Watching**: Manual refresh or scheduled regeneration

### 7.3 Configuration Management

#### Feature Flags
**Location**: `frontend/src/lib/config.ts`
**Integration**: Astro environment variables and build-time configuration

#### Theme Configuration
**Location**: `frontend/src/config/theme.json`
**Integration**: Chart theming and color palette management

#### Photo Booth Configuration
**Location**: `frontend/src/config/photo-booth.json`
**Integration**: Export settings and dashboard metadata

---

## 8. File Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── photo-booth.astro                    # Photo booth page entry
│   │   └── api/
│   │       ├── dashboards.json.ts               # Dashboard config API
│   │       └── export-dashboard.ts              # Export API endpoint
│   ├── layouts/
│   │   ├── PhotoBoothBase.astro                 # Base photo booth layout
│   │   ├── shortcodes/
│   │   │   ├── PhotoBoothDisplay.tsx            # Main photo booth component
│   │   │   ├── ConditionalPhotoBoothDisplay.tsx # Feature flag wrapper
│   │   │   └── ChartDisplay.tsx                 # Chart entry point
│   │   └── components/
│   │       └── charts/
│   │           ├── ChartContainer.tsx           # Chart layout wrapper
│   │           ├── PortfolioChart.tsx           # Core chart processing
│   │           └── ChartRenderer.tsx            # Plotly integration
│   ├── services/
│   │   ├── dashboardLoader.ts                   # Dashboard loading service
│   │   └── ChartDataService.ts                  # Data fetching and caching
│   ├── hooks/
│   │   └── usePortfolioData.ts                  # Data hooks collection
│   ├── types/
│   │   └── ChartTypes.ts                        # TypeScript definitions
│   ├── utils/
│   │   └── chartTheme.ts                        # Theme management
│   ├── config/
│   │   ├── photo-booth.json                     # Photo booth configuration
│   │   └── theme.json                           # Theme configuration
│   └── test/                                    # Complete testing infrastructure
│       └── photo-booth/                         # Photo booth specific tests
│           ├── README.md                        # Test module documentation
│           ├── photo-booth-test-suite.ts        # Unified test runner
│           ├── __mocks__/                       # Shared mock system
│           │   ├── setup.tsx                    # Main mock configuration
│           │   ├── photo-booth-config.mock.ts   # Config mocks
│           │   ├── dashboard-loader.mock.ts     # Service mocks
│           │   └── test-data.mock.ts            # Centralized test data
│           ├── unit/                            # Component unit tests
│           │   ├── PhotoBoothDisplay.test.tsx   # Main component testing
│           │   └── DashboardRenderer.test.tsx   # Dashboard rendering tests
│           ├── integration/                     # Integration workflow tests
│           │   └── workflow.test.tsx            # Complete user workflows
│           ├── e2e/                             # End-to-end browser tests
│           │   ├── photo-booth-e2e-export.test.ts        # Phase 1: Export integration
│           │   ├── image-validation.test.ts               # Phase 2: Quality validation
│           │   ├── real-data-integration.test.ts          # Phase 3: Real data integration
│           │   ├── python-integration.test.ts             # Phase 4: Python process management
│           │   ├── filesystem-integration.test.ts         # Phase 5: File system management
│           │   ├── config-hotreload.test.ts               # Phase 6: Configuration testing
│           │   ├── performance-benchmarks.test.ts         # Phase 6: Performance testing
│           │   ├── advanced-error-scenarios.test.ts       # Phase 7: Error scenario coverage
│           │   ├── visual-regression.test.ts              # Visual consistency testing
│           │   ├── browser-specific.test.ts               # Cross-browser compatibility
│           │   ├── globalSetup.ts                         # E2E global configuration
│           │   └── screenshots/                           # Visual regression artifacts
│           ├── fixtures/                        # Test fixture data
│           └── utils/                           # Testing utilities
│               ├── e2e-setup.ts                 # E2E setup and browser management
│               └── test-helpers.ts              # Unit/integration test helpers

scripts/
├── photo_booth_generator.py                     # Primary export script
├── dashboard_generator.py                       # Dashboard generation
├── plotly_dashboard_generator.py               # Plotly dashboard rendering
└── utils/
    ├── svg_exporter.js                         # SVG export utility
    └── sharp_processor.js                      # PNG processing utility
```

### Testing

**Commands**:
```bash
# Frontend tests
cd frontend && yarn test

# Python script test
python scripts/photo_booth_generator.py --help
```

---
## Summary

Photo booth system providing dashboard export in PNG/SVG formats using Python integration with Puppeteer and Sharp.js processing.
