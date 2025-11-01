# Chart Data Dependency Management System

## Overview

The Chart Data Dependency Management System provides intelligent data refresh capabilities for Cole Morton's mixed data ecosystem. It handles manual data sources (unpredictable timing), CLI API services (automatic refresh), static data (never updates), and hybrid sources seamlessly.

## Quick Start

### 1. Using Enhanced Data Hooks

Replace existing hooks with enhanced versions that include dependency management:

```tsx
// OLD: Basic hook without dependency management
import { useLiveSignalsData } from "@/hooks/usePortfolioData";

// NEW: Enhanced hook with dependency management
import { useEnhancedLiveSignalsData } from "@/hooks/useEnhancedPortfolioData";

function MyChart() {
  const {
    data,
    loading,
    error,
    dataStatus, // NEW: Data freshness info
    refresh, // NEW: Manual refresh function
    canRefresh, // NEW: Whether refresh is available
    isRefreshing, // NEW: Refresh status
  } = useEnhancedLiveSignalsData();

  return (
    <div>
      {/* Your chart component */}

      {/* NEW: Data status indicator */}
      <DataStatusIndicator
        chartType="live-signals-equity-curve"
        compact={true}
        showRefreshButton={true}
      />
    </div>
  );
}
```

### 2. Adding Data Status Indicators

Show data freshness and refresh controls:

```tsx
import { DataStatusIndicator } from "@/layouts/components/charts/DataStatusIndicator";

// Compact indicator (for individual charts)
<DataStatusIndicator
  chartType="live-signals-equity-curve"
  compact={true}
  showRefreshButton={true}
/>

// Full indicator (for detailed status)
<DataStatusIndicator
  chartType="trade-pnl-waterfall"
  compact={false}
  showRefreshButton={true}
/>
```

### 3. Using the Data Status Dashboard

Monitor all chart dependencies in one place:

```tsx
import { DataStatusDashboard } from "@/layouts/components/charts/DataStatusDashboard";

// Compact dashboard (for overview)
<DataStatusDashboard showCompact={true} />

// Full dashboard (for detailed management)
<DataStatusDashboard showCompact={false} />
```

## Architecture Components

### 1. Data Source Classification

Four types of data sources are supported:

- **`manual`**: Files updated manually/externally (unpredictable timing)
- **`cli-api`**: Data available via CLI services (can auto-refresh)
- **`static`**: Historical data that never changes
- **`hybrid`**: Combination of manual + API data

### 2. Chart-Specific Configurations

Each chart type has specific data dependency requirements defined in `chart-data-dependencies.json`:

```json
{
  "live-signals-equity-curve": {
    "primarySource": {
      "type": "manual",
      "location": "/data/portfolio/live-signals/live_signals_equity.csv",
      "refreshMethod": "file-watch"
    },
    "freshness": {
      "warningThreshold": 4, // Hours before showing warning
      "errorThreshold": 12 // Hours before showing error
    },
    "refreshPolicy": {
      "allowManualRefresh": true,
      "autoRefresh": false
    }
  }
}
```

### 3. Service Integration Layer

The system integrates with existing CLI services for automatic data refresh:

- **Yahoo Finance**: Real-time market data
- **Financial Modeling Prep**: Advanced financial data
- **Alpha Vantage**: Technical indicators
- **CoinGecko**: Cryptocurrency data

Rate limiting and authentication are handled automatically.

### 4. File System Monitoring

Monitors manual data files for changes and triggers appropriate updates:

```typescript
// Files are automatically monitored based on chart configurations
// No manual setup required - the system handles it all
```

## Key Features

### ✅ **Intelligent Refresh Policies**

- Only refreshes data that can actually be refreshed
- Respects rate limits and API constraints
- Prioritizes critical vs. non-critical data

### ✅ **User-Friendly Status Indicators**

- Visual indicators show data age and freshness
- Clear messaging about refresh capabilities
- Manual refresh buttons where applicable

### ✅ **Mixed Data Source Support**

- Manual files (trade history from external systems)
- API data (real-time market prices)
- Static data (historical datasets)
- Hybrid combinations

### ✅ **Graceful Error Handling**

- Fails fast with meaningful error messages
- No fallback mechanisms that hide problems
- Clear indication when data is stale or missing

### ✅ **Performance Optimized**

- Intelligent caching with chart-specific policies
- Background monitoring without blocking UI
- Queue-based refresh system prevents overload

## Configuration Files

### Primary Configuration

- `chart-data-dependencies.json`: Chart-specific data source configurations
- `photo-booth.json`: Integration settings for photo booth system

### Type Definitions

- `DataDependencyTypes.ts`: Core interfaces and types
- `ChartTypes.ts`: Extended with dependency information

### Service Classes

- `DataDependencyManager.ts`: Central orchestration service
- `EnhancedChartDataService.ts`: Extended data service with dependency awareness
- `CLIServiceIntegration.ts`: CLI service coordination layer
- `FileSystemMonitor.ts`: File change detection service

### React Components

- `DataStatusIndicator.tsx`: Individual chart status display
- `DataStatusDashboard.tsx`: System-wide status management
- `useEnhancedPortfolioData.ts`: React hooks with dependency features

## Migration Guide

### Step 1: Update Imports

```tsx
// Replace existing hooks
import { useEnhancedLiveSignalsData } from "@/hooks/useEnhancedPortfolioData";
```

### Step 2: Add Status Indicators

```tsx
// Add to chart components
<DataStatusIndicator chartType="your-chart-type" compact={true} />
```

### Step 3: Configure Dependencies

```json
// Update chart-data-dependencies.json with your specific requirements
```

### Step 4: Enable Integration

```json
// In photo-booth.json
"data_dependencies": {
  "enabled": true,
  "show_status_indicators": true,
  "allow_manual_refresh": true
}
```

## Best Practices

### ✅ **For Live Signals Data**

- Use manual data source type
- Set short warning thresholds (4-6 hours)
- Enable file watching
- Allow manual refresh

### ✅ **For Market Data**

- Use CLI API source type
- Enable automatic refresh during market hours
- Respect rate limits
- Configure fallback sources

### ✅ **For Historical Data**

- Use static data source type
- Disable refresh capabilities
- Set long staleness thresholds
- No monitoring required

### ✅ **For Portfolio Data**

- Use hybrid source type when combining manual positions with API pricing
- Coordinate refresh schedules
- Prioritize manual data over API data for conflicts

## Error Handling

The system follows a **fail-fast approach**:

- ❌ **No fallback mechanisms** that hide data issues
- ✅ **Clear error messages** explaining what went wrong
- ✅ **User-friendly indicators** showing data status
- ✅ **Actionable controls** for refresh when possible

This ensures data quality issues are immediately visible rather than silently degrading functionality.
