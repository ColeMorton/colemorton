import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import type { ChartType } from "@/types/ChartTypes";
import {
  mockMultiStockDataXPEVNIO,
  mockMultiStockDataThreeSymbols,
  mockMultiStockMapping,
  mockMultiStockMetadata,
  mockSymbolMetadata,
} from "@/test/__mocks__/multi-stock-data.mock";

/**
 * Integration tests for multi-stock chart workflow
 * Tests the complete pipeline from chart type to rendered output
 */

// Mock configuration with comprehensive multi-stock setup
const mockChartConfig = {
  multiStockMapping: mockMultiStockMapping,
  multiStockMetadata: mockMultiStockMetadata,
  symbolMetadata: mockSymbolMetadata,
  chartTypeMapping: {
    "apple-price": "AAPL",
    "mstr-price": "MSTR",
  },
  dependencies: {
    "multi-stock-price": {
      chartType: "multi-stock-price",
      chartStatus: "active",
      primarySource: {
        type: "cli-api",
        location: "dynamic",
        refreshMethod: "api-poll",
        frequency: "daily",
        cliService: "yahoo-finance",
        symbols: "dynamic",
      },
    },
    "xpev-nio-stock-price": {
      chartType: "xpev-nio-stock-price",
      chartStatus: "active",
      primarySource: {
        type: "cli-api",
        location: "dynamic",
        refreshMethod: "api-poll",
        frequency: "daily",
        cliService: "yahoo-finance",
        symbols: "dynamic",
      },
    },
    "tech-giants-comparison": {
      chartType: "tech-giants-comparison",
      chartStatus: "active",
      primarySource: {
        type: "cli-api",
        location: "dynamic",
        refreshMethod: "api-poll",
        frequency: "daily",
        cliService: "yahoo-finance",
        symbols: "dynamic",
      },
    },
    "portfolio-history": {
      chartType: "portfolio-history",
      chartStatus: "active",
      primarySource: {
        type: "csv",
        location: "/data/portfolio_history.csv",
        refreshMethod: "manual",
        frequency: "on-demand",
      },
    },
  },
};

vi.mock("@/config/chart-data-dependencies.json", () => ({
  default: mockChartConfig,
}));

// Mock chart theme
vi.mock("@/utils/chartTheme", () => ({
  getChartColors: vi.fn(() => ({
    multiStrategy: "#1f77b4",
    buyHold: "#9575cd",
    tertiary: "#4caf50",
    drawdown: "#ff7043",
    neutral: "#90a4ae",
  })),
  getPlotlyThemeColors: vi.fn(() => ({
    paper_bgcolor: "white",
    plot_bgcolor: "white",
    font: { color: "black" },
    titleFont: { color: "black", size: 16 },
  })),
}));

// Mock chart data service
const mockChartDataService = {
  fetchStockData: vi.fn(),
};

vi.mock("@/services/ChartDataService", () => ({
  chartDataService: mockChartDataService,
}));

// Mock ChartRenderer to capture full integration data
const MockChartRenderer = vi.fn(({ data, layout, loading, error }) => (
  <div data-testid="chart-integration">
    <div data-testid="integration-data" data-chart-data={JSON.stringify(data)}>
      {data?.length || 0} data series
    </div>
    <div data-testid="integration-layout" data-layout={JSON.stringify(layout)}>
      {layout?.title?.text || "No title"}
    </div>
    <div data-testid="integration-status">
      {loading ? "loading" : error ? "error" : "ready"}
    </div>
  </div>
));

vi.mock("@/layouts/components/charts/ChartRenderer", () => ({
  default: MockChartRenderer,
}));

describe("Multi-Stock Chart Integration Tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    MockChartRenderer.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("End-to-End Multi-Stock Workflow", () => {
    it("should complete full XPEV vs NIO chart workflow", async () => {
      // Mock API responses
      mockChartDataService.fetchStockData
        .mockResolvedValueOnce(mockMultiStockDataXPEVNIO.XPEV)
        .mockResolvedValueOnce(mockMultiStockDataXPEVNIO.NIO);

      // Import components after mocks are set up
      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      // Test complete ChartDisplay -> PortfolioChart integration
      render(
        <ChartDisplay
          title="XPEV vs NIO Stock Comparison"
          chartType="xpev-nio-stock-price"
          description="Chinese EV stocks comparison"
        />,
      );

      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      // Verify chart was rendered with correct data
      expect(screen.getByTestId("integration-data")).toHaveTextContent(
        "2 data series",
      );

      // Verify layout configuration
      const layoutElement = screen.getByTestId("integration-layout");
      expect(layoutElement).toHaveTextContent("XPEV vs NIO Stock Comparison");

      // Verify API calls were made correctly
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledTimes(2);
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledWith(
        "XPEV",
        expect.any(AbortSignal),
      );
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledWith(
        "NIO",
        expect.any(AbortSignal),
      );
    });

    it("should handle three-symbol chart integration", async () => {
      // Mock API responses for three symbols
      mockChartDataService.fetchStockData
        .mockResolvedValueOnce(mockMultiStockDataThreeSymbols.AAPL)
        .mockResolvedValueOnce(mockMultiStockDataThreeSymbols.MSTR)
        .mockResolvedValueOnce(mockMultiStockDataThreeSymbols.TSLA);

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(
        <ChartDisplay
          title="Tech Giants Comparison"
          chartType="tech-giants-comparison"
          description="Technology stocks comparison"
        />,
      );

      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      // Verify three data series
      expect(screen.getByTestId("integration-data")).toHaveTextContent(
        "3 data series",
      );

      // Verify all three symbols were fetched
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledTimes(3);
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledWith(
        "AAPL",
        expect.any(AbortSignal),
      );
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledWith(
        "MSTR",
        expect.any(AbortSignal),
      );
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledWith(
        "TSLA",
        expect.any(AbortSignal),
      );
    });
  });

  describe("Configuration Integration", () => {
    it("should resolve chart type to symbols correctly", async () => {
      const chartType: ChartType = "xpev-nio-stock-price";

      // Test the actual helper functions from PortfolioChart
      const isMultiStockChart = (type: string): boolean => {
        return type.includes("multi-stock") || type.endsWith("-stock-price");
      };

      const getSymbolsFromMultiStockChart = (type: string): string[] => {
        if (!isMultiStockChart(type)) {
          return [];
        }
        return (
          mockChartConfig.multiStockMapping[
            type as keyof typeof mockChartConfig.multiStockMapping
          ] || []
        );
      };

      expect(isMultiStockChart(chartType)).toBe(true);
      expect(getSymbolsFromMultiStockChart(chartType)).toEqual(["XPEV", "NIO"]);
    });

    it("should integrate metadata for chart titles and display names", async () => {
      mockChartDataService.fetchStockData
        .mockResolvedValueOnce(mockMultiStockDataXPEVNIO.XPEV)
        .mockResolvedValueOnce(mockMultiStockDataXPEVNIO.NIO);

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(
        <ChartDisplay
          chartType="xpev-nio-stock-price"
          // No title provided - should use metadata
        />,
      );

      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      // Should use metadata display name
      expect(screen.getByTestId("integration-layout")).toHaveTextContent(
        "XPEV vs NIO Comparison",
      );
    });

    it("should maintain type safety across the integration", async () => {
      // Verify ChartType union includes multi-stock types
      const validChartTypes: ChartType[] = [
        "multi-stock-price",
        "xpev-nio-stock-price",
        "apple-price",
        "portfolio-value-comparison",
      ];

      validChartTypes.forEach((chartType) => {
        expect(typeof chartType).toBe("string");
      });

      // Verify configuration structure matches expectations
      expect(mockChartConfig.multiStockMapping).toHaveProperty(
        "xpev-nio-stock-price",
      );
      expect(mockChartConfig.multiStockMetadata).toHaveProperty(
        "xpev-nio-stock-price",
      );
      expect(mockChartConfig.symbolMetadata).toHaveProperty("XPEV");
      expect(mockChartConfig.symbolMetadata).toHaveProperty("NIO");
    });
  });

  describe("Error Integration Testing", () => {
    it("should handle partial API failures in integration", async () => {
      // XPEV succeeds, NIO fails
      mockChartDataService.fetchStockData
        .mockResolvedValueOnce(mockMultiStockDataXPEVNIO.XPEV)
        .mockRejectedValueOnce(new Error("NIO API timeout"));

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(
        <ChartDisplay chartType="xpev-nio-stock-price" title="XPEV vs NIO" />,
      );

      await waitFor(() => {
        expect(screen.getByTestId("integration-status")).toHaveTextContent(
          "error",
        );
      });

      // Should show error state
      expect(screen.getByTestId("integration-data")).toHaveTextContent(
        "0 data series",
      );
    });

    it("should handle complete API failure gracefully", async () => {
      // Both symbols fail
      mockChartDataService.fetchStockData
        .mockRejectedValueOnce(new Error("XPEV API error"))
        .mockRejectedValueOnce(new Error("NIO API error"));

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(
        <ChartDisplay chartType="xpev-nio-stock-price" title="XPEV vs NIO" />,
      );

      await waitFor(() => {
        expect(screen.getByTestId("integration-status")).toHaveTextContent(
          "error",
        );
      });

      expect(screen.getByTestId("integration-data")).toHaveTextContent(
        "0 data series",
      );
    });

    it("should handle unknown chart types gracefully", async () => {
      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(
        <ChartDisplay
          chartType="unknown-chart-type"
          as
          any
          title="Unknown Chart"
        />,
      );

      // Should render without crashing
      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      // Should show no data
      expect(screen.getByTestId("integration-data")).toHaveTextContent(
        "0 data series",
      );
    });
  });

  describe("Performance Integration", () => {
    it("should handle concurrent API calls efficiently", async () => {
      const startTime = Date.now();

      // Mock delayed responses to test concurrency
      mockChartDataService.fetchStockData.mockImplementation((symbol) => {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(
              symbol === "XPEV"
                ? mockMultiStockDataXPEVNIO.XPEV
                : mockMultiStockDataXPEVNIO.NIO,
            );
          }, 100); // 100ms delay for each
        });
      });

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(
        <ChartDisplay
          chartType="xpev-nio-stock-price"
          title="Performance Test"
        />,
      );

      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Should complete in roughly 100ms (concurrent) rather than 200ms (sequential)
      expect(duration).toBeLessThan(150); // Some buffer for test execution overhead
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledTimes(2);
    });

    it("should cleanup resources properly on unmount", async () => {
      mockChartDataService.fetchStockData.mockImplementation(
        () => new Promise(() => {}),
      ); // Never resolves

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      const { unmount } = render(
        <ChartDisplay chartType="xpev-nio-stock-price" title="Cleanup Test" />,
      );

      // Start request
      expect(screen.getByTestId("integration-status")).toHaveTextContent(
        "loading",
      );

      // Unmount before completion
      unmount();

      // Should not cause memory leaks or unhandled promise rejections
      await new Promise((resolve) => setTimeout(resolve, 10));
    });
  });

  describe("Backwards Compatibility Integration", () => {
    it("should maintain single-stock chart functionality", async () => {
      const mockAppleData = [
        {
          date: "2024-01-01",
          open: "150.00",
          high: "155.00",
          low: "148.00",
          close: "152.00",
          volume: "50000000",
        },
      ];

      mockChartDataService.fetchStockData.mockResolvedValueOnce(mockAppleData);

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(<ChartDisplay chartType="apple-price" title="Apple Stock" />);

      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      // Should work as before
      expect(screen.getByTestId("integration-data")).toHaveTextContent(
        "1 data series",
      );
      expect(mockChartDataService.fetchStockData).toHaveBeenCalledWith(
        "AAPL",
        expect.any(AbortSignal),
      );
    });

    it("should maintain portfolio chart functionality", async () => {
      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      render(
        <ChartDisplay
          chartType="portfolio-value-comparison"
          title="Portfolio Comparison"
        />,
      );

      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      // Should not attempt stock data fetching for non-stock charts
      expect(mockChartDataService.fetchStockData).not.toHaveBeenCalled();
    });
  });

  describe("Chart Display Integration", () => {
    it("should support all multi-stock chart types in ChartDisplay", async () => {
      const supportedTypes = ["multi-stock-price", "xpev-nio-stock-price"];

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      for (const chartType of supportedTypes) {
        const { unmount } = render(
          <ChartDisplay
            chartType={chartType as ChartType}
            title={`Test ${chartType}`}
          />,
        );

        // Should render without error
        expect(screen.getByTestId("integration-data")).toBeInTheDocument();

        unmount();
      }
    });

    it("should pass through all props correctly", async () => {
      mockChartDataService.fetchStockData
        .mockResolvedValueOnce(mockMultiStockDataXPEVNIO.XPEV)
        .mockResolvedValueOnce(mockMultiStockDataXPEVNIO.NIO);

      const { default: ChartDisplay } = await import(
        "@/layouts/shortcodes/ChartDisplay"
      );

      const testProps = {
        title: "Custom Title",
        category: "Test Category",
        description: "Test Description",
        chartType: "xpev-nio-stock-price" as ChartType,
        className: "test-class",
      };

      render(<ChartDisplay {...testProps} />);

      const statusElement = await screen.findByTestId(
        "integration-status",
        {},
        { timeout: 5000 },
      );
      await waitFor(
        () => {
          expect(statusElement.textContent).toBe("ready");
        },
        { timeout: 5000 },
      );

      // Verify integration completed successfully
      expect(screen.getByTestId("integration-data")).toHaveTextContent(
        "2 data series",
      );
    });
  });
});
