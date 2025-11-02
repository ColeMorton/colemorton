import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import type { StockDataRow } from "@/types/ChartTypes";

// Mock chart data dependencies
const mockChartConfig = {
  multiStockMapping: {
    "xpev-nio-stock-price": ["XPEV", "NIO"],
    "test-three-stock": ["AAPL", "MSTR", "TSLA"],
  },
  multiStockMetadata: {
    "xpev-nio-stock-price": {
      displayName: "XPEV vs NIO Comparison",
      description: "Chinese EV stocks price comparison",
      sector: "Electric Vehicles",
    },
    "test-three-stock": {
      displayName: "Tech Giants Comparison",
      description: "Technology stocks comparison",
      sector: "Technology",
    },
  },
  chartTypeMapping: {
    "apple-price": "AAPL",
    "mstr-price": "MSTR",
  },
  symbolMetadata: {
    XPEV: {
      name: "XPeng Inc.",
      displayName: "XPeng Price",
      sector: "Electric Vehicles",
    },
    NIO: {
      name: "NIO Inc.",
      displayName: "NIO Price",
      sector: "Electric Vehicles",
    },
    AAPL: {
      name: "Apple Inc.",
      displayName: "Apple Price",
      sector: "Technology",
    },
    MSTR: {
      name: "MicroStrategy Inc.",
      displayName: "Strategy Price",
      sector: "Technology",
    },
    TSLA: {
      name: "Tesla Inc.",
      displayName: "Tesla Price",
      sector: "Electric Vehicles",
    },
  },
};

vi.mock("@/config/chart-data-dependencies.json", () => ({
  default: mockChartConfig,
}));

// Mock chart theme utilities
const mockColors = {
  multiStrategy: "#1f77b4",
  buyHold: "#9575cd",
  tertiary: "#4caf50",
  drawdown: "#ff7043",
  neutral: "#90a4ae",
};

vi.mock("@/utils/chartTheme", () => ({
  getChartColors: vi.fn(() => mockColors),
  getPlotlyThemeColors: vi.fn(() => ({
    paper_bgcolor: "white",
    plot_bgcolor: "white",
    font: { color: "black" },
    titleFont: { color: "black", size: 16 },
    gridColor: "#e0e0e0",
    tickColor: "#666",
    legendBgColor: "rgba(255,255,255,0.8)",
    legendBorderColor: "#ccc",
  })),
}));

// Mock hooks
const mockUseMultiStockData = vi.fn();
const mockUseStockData = vi.fn();
const mockUsePortfolioData = vi.fn();

vi.mock("@/hooks/usePortfolioData", () => ({
  useMultiStockData: mockUseMultiStockData,
  useStockData: mockUseStockData,
  usePortfolioData: mockUsePortfolioData,
  useLiveSignalsData: vi.fn(() => ({ data: [], loading: false, error: null })),
  useWaterfallTradeData: vi.fn(() => ({
    data: [],
    loading: false,
    error: null,
  })),
  useClosedPositionsPnLData: vi.fn(() => ({
    data: [],
    loading: false,
    error: null,
  })),
  useOpenPositionsPnLData: vi.fn(() => ({
    data: [],
    loading: false,
    error: null,
  })),
  useLiveSignalsBenchmarkData: vi.fn(() => ({
    data: [],
    loading: false,
    error: null,
  })),
}));

// Mock ChartRenderer to capture chart data
const MockChartRenderer = vi.fn(({ data, layout, loading, error }) => (
  <div data-testid="chart-renderer">
    <div data-testid="chart-data">{JSON.stringify(data)}</div>
    <div data-testid="chart-layout">{JSON.stringify(layout)}</div>
    <div data-testid="chart-loading">{loading ? "loading" : "ready"}</div>
    <div data-testid="chart-error">{error || "no-error"}</div>
  </div>
));

vi.mock("@/layouts/components/charts/ChartRenderer", () => ({
  default: MockChartRenderer,
}));

describe("PortfolioChart Multi-Stock Component Tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    MockChartRenderer.mockClear();

    // Default mock implementations
    mockUsePortfolioData.mockReturnValue({
      data: {},
      loading: false,
      error: null,
    });

    mockUseStockData.mockReturnValue({
      data: [],
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Multi-Stock Chart Rendering", () => {
    it("should render XPEV vs NIO chart with correct data structure", async () => {
      const mockXPEVData: StockDataRow[] = [
        {
          date: "2024-01-01",
          open: "10.00",
          high: "12.00",
          low: "9.50",
          close: "11.50",
          volume: "1000000",
        },
        {
          date: "2024-01-02",
          open: "11.50",
          high: "13.00",
          low: "11.00",
          close: "12.75",
          volume: "1200000",
        },
      ];

      const mockNIOData: StockDataRow[] = [
        {
          date: "2024-01-01",
          open: "8.00",
          high: "9.00",
          low: "7.50",
          close: "8.75",
          volume: "800000",
        },
        {
          date: "2024-01-02",
          open: "8.75",
          high: "10.00",
          low: "8.50",
          close: "9.50",
          volume: "950000",
        },
      ];

      mockUseMultiStockData.mockReturnValue({
        data: {
          XPEV: mockXPEVData,
          NIO: mockNIOData,
        },
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(
        <PortfolioChart chartType="xpev-nio-stock-price" title="XPEV vs NIO" />,
      );

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      // Verify chart data structure
      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      expect(chartData).toHaveLength(2); // Two stock lines

      // Verify XPEV data
      const xpevLine = chartData.find((line: any) =>
        line.name.includes("XPeng"),
      );
      expect(xpevLine).toBeDefined();
      expect(xpevLine.type).toBe("scatter");
      expect(xpevLine.mode).toBe("lines");
      expect(xpevLine.x).toEqual(["2024-01-01", "2024-01-02"]);
      expect(xpevLine.y).toEqual([11.5, 12.75]);

      // Verify NIO data
      const nioLine = chartData.find((line: any) => line.name.includes("NIO"));
      expect(nioLine).toBeDefined();
      expect(nioLine.type).toBe("scatter");
      expect(nioLine.mode).toBe("lines");
      expect(nioLine.x).toEqual(["2024-01-01", "2024-01-02"]);
      expect(nioLine.y).toEqual([8.75, 9.5]);
    });

    it("should assign dynamic colors for multi-stock charts", async () => {
      const mockMultiStockData = {
        AAPL: [
          {
            date: "2024-01-01",
            open: "150.00",
            high: "155.00",
            low: "148.00",
            close: "152.00",
            volume: "50000000",
          },
        ],
        MSTR: [
          {
            date: "2024-01-01",
            open: "300.00",
            high: "320.00",
            low: "295.00",
            close: "315.00",
            volume: "2000000",
          },
        ],
        TSLA: [
          {
            date: "2024-01-01",
            open: "200.00",
            high: "210.00",
            low: "195.00",
            close: "205.00",
            volume: "30000000",
          },
        ],
      };

      mockUseMultiStockData.mockReturnValue({
        data: mockMultiStockData,
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(
        <PortfolioChart
          chartType="test-three-stock"
          title="Three Stock Test"
        />,
      );

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      expect(chartData).toHaveLength(3);

      // Verify different colors are assigned
      const colors = chartData.map((line: any) => line.line.color);
      const uniqueColors = new Set(colors);
      expect(uniqueColors.size).toBe(3); // All different colors

      // Verify colors cycle through available palette
      expect(colors[0]).toBe(mockColors.multiStrategy);
      expect(colors[1]).toBe(mockColors.buyHold);
      expect(colors[2]).toBe(mockColors.tertiary);
    });

    it("should generate proper display names from symbol metadata", async () => {
      const mockData = {
        XPEV: [
          {
            date: "2024-01-01",
            open: "10.00",
            high: "12.00",
            low: "9.50",
            close: "11.50",
            volume: "1000000",
          },
        ],
        NIO: [
          {
            date: "2024-01-01",
            open: "8.00",
            high: "9.00",
            low: "7.50",
            close: "8.75",
            volume: "800000",
          },
        ],
      };

      mockUseMultiStockData.mockReturnValue({
        data: mockData,
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(
        <PortfolioChart chartType="xpev-nio-stock-price" title="XPEV vs NIO" />,
      );

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      // Verify display names use metadata
      const xpevLine = chartData.find((line: any) =>
        line.name.includes("XPeng"),
      );
      expect(xpevLine.name).toBe("XPeng Inc. (XPEV)");

      const nioLine = chartData.find((line: any) => line.name.includes("NIO"));
      expect(nioLine.name).toBe("NIO Inc. (NIO)");
    });

    it("should fallback to basic display names for unknown symbols", async () => {
      const mockData = {
        UNKNOWN: [
          {
            date: "2024-01-01",
            open: "10.00",
            high: "12.00",
            low: "9.50",
            close: "11.50",
            volume: "1000000",
          },
        ],
      };

      mockUseMultiStockData.mockReturnValue({
        data: mockData,
        loading: false,
        error: null,
      });

      // Mock unknown chart type not in config
      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(
        <PortfolioChart
          chartType="unknown-multi-stock"
          title="Unknown Chart"
        />,
      );

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      // Should fallback to basic name format
      expect(chartData[0]?.name).toBe("UNKNOWN Price");
    });
  });

  describe("Chart Layout and Configuration", () => {
    it("should generate correct chart title for multi-stock charts", async () => {
      mockUseMultiStockData.mockReturnValue({
        data: { XPEV: [], NIO: [] },
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(
        <PortfolioChart
          chartType="xpev-nio-stock-price"
          title="Custom Title"
        />,
      );

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartLayoutElement = screen.getByTestId("chart-layout");
      const chartLayout = JSON.parse(chartLayoutElement.textContent || "{}");

      // Should use multiStockMetadata display name when no custom title
      expect(chartLayout.title.text).toContain("XPEV vs NIO Comparison");
    });

    it("should set correct Y-axis title for multi-stock charts", async () => {
      mockUseMultiStockData.mockReturnValue({
        data: { XPEV: [], NIO: [] },
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="xpev-nio-stock-price" />);

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartLayoutElement = screen.getByTestId("chart-layout");
      const chartLayout = JSON.parse(chartLayoutElement.textContent || "{}");

      expect(chartLayout.yaxis.title.text).toBe("Price ($)");
    });

    it("should configure proper hover templates", async () => {
      const mockData = {
        XPEV: [
          {
            date: "2024-01-01",
            open: "10.00",
            high: "12.00",
            low: "9.50",
            close: "11.50",
            volume: "1000000",
          },
        ],
      };

      mockUseMultiStockData.mockReturnValue({
        data: mockData,
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="xpev-nio-stock-price" />);

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      const hoverTemplate = chartData[0]?.hovertemplate;
      expect(hoverTemplate).toContain("<b>%{fullData.name}</b>");
      expect(hoverTemplate).toContain("Date: %{x}");
      expect(hoverTemplate).toContain("Price: $%{y:.2f}");
      expect(hoverTemplate).toContain("<extra></extra>");
    });
  });

  describe("Error Handling and Edge Cases", () => {
    it("should handle loading state correctly", async () => {
      mockUseMultiStockData.mockReturnValue({
        data: {},
        loading: true,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="xpev-nio-stock-price" />);

      expect(screen.getByTestId("chart-loading")).toHaveTextContent("loading");
      expect(screen.getByTestId("chart-data")).toHaveTextContent("[]");
    });

    it("should handle error state correctly", async () => {
      mockUseMultiStockData.mockReturnValue({
        data: {},
        loading: false,
        error: "Failed to fetch stock data",
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="xpev-nio-stock-price" />);

      expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      expect(screen.getByTestId("chart-error")).toHaveTextContent(
        "Failed to fetch stock data",
      );
      expect(screen.getByTestId("chart-data")).toHaveTextContent("[]");
    });

    it("should handle empty data gracefully", async () => {
      mockUseMultiStockData.mockReturnValue({
        data: {},
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="xpev-nio-stock-price" />);

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      expect(screen.getByTestId("chart-data")).toHaveTextContent("[]");
      expect(screen.getByTestId("chart-error")).toHaveTextContent("no-error");
    });

    it("should handle partial data (some symbols missing)", async () => {
      mockUseMultiStockData.mockReturnValue({
        data: {
          XPEV: [
            {
              date: "2024-01-01",
              open: "10.00",
              high: "12.00",
              low: "9.50",
              close: "11.50",
              volume: "1000000",
            },
          ],
          // NIO data missing
        },
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="xpev-nio-stock-price" />);

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      // Should only render available data
      expect(chartData).toHaveLength(1);
      expect(chartData[0].name).toContain("XPeng");
    });

    it("should handle malformed stock data", async () => {
      mockUseMultiStockData.mockReturnValue({
        data: {
          XPEV: [
            {
              date: "2024-01-01",
              open: "10.00",
              high: "12.00",
              low: "9.50",
              close: "invalid",
              volume: "1000000",
            },
          ],
        },
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="xpev-nio-stock-price" />);

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      // Should handle NaN gracefully
      expect(chartData[0]?.y).toEqual([NaN]);
    });
  });

  describe("Single Stock Chart Compatibility", () => {
    it("should still handle single stock charts correctly", async () => {
      const mockAppleData: StockDataRow[] = [
        {
          date: "2024-01-01",
          open: "150.00",
          high: "155.00",
          low: "148.00",
          close: "152.00",
          volume: "50000000",
        },
      ];

      mockUseStockData.mockReturnValue({
        data: mockAppleData,
        loading: false,
        error: null,
      });

      const { default: PortfolioChart } = await import(
        "@/layouts/components/charts/PortfolioChart"
      );

      render(<PortfolioChart chartType="apple-price" title="Apple Stock" />);

      await waitFor(() => {
        expect(screen.getByTestId("chart-loading")).toHaveTextContent("ready");
      });

      const chartDataElement = screen.getByTestId("chart-data");
      const chartData = JSON.parse(chartDataElement.textContent || "[]");

      expect(chartData).toHaveLength(1);
      expect(chartData[0].y).toEqual([152.0]);
    });
  });
});
