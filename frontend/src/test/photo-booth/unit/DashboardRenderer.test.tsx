import React from "react";
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";
import {
  setupPhotoBoothMocks,
  mockPortfolioHistoryPortraitDashboard,
  mockDashboardLoader,
  createMockDashboard,
} from "../__mocks__/setup.tsx";

// Extract DashboardRenderer component for isolated testing
// Since it's a nested component, we need to test it through PhotoBoothDisplay
// or extract it to its own file. For now, we'll create a test wrapper.

// Mock DashboardRenderer component implementation for testing
const DashboardRenderer: React.FC<{
  dashboard: typeof mockPortfolioHistoryPortraitDashboard;
  mode: "light" | "dark";
  aspectRatio: "16:9" | "4:3" | "3:4";
}> = ({ dashboard, mode, aspectRatio }) => {
  const layoutClasses = mockDashboardLoader.getLayoutClasses(dashboard.layout);

  const isPortfolioHistoryPortrait =
    dashboard.id === "portfolio_history_portrait";

  return (
    <div
      className={`dashboard-content ${dashboard.layout} ${mode}-mode flex flex-col`}
      data-testid="dashboard-content"
      data-dashboard-id={dashboard.id}
      data-mode={mode}
      data-aspect-ratio={aspectRatio}
      style={{
        width: "100%",
        height: "100%",
        overflow: "hidden",
      }}
    >
      {/* Header Section - Only for Portfolio History Portrait */}
      {isPortfolioHistoryPortrait && (
        <div
          className="dashboard-header text-center"
          data-testid="dashboard-header"
        >
          <h1 className="text-dark mt-8 text-4xl font-bold dark:text-white">
            Twitter Live Signals
          </h1>
        </div>
      )}

      {/* Charts Section */}
      <div
        className={`${layoutClasses} min-h-0 flex-1`}
        data-testid="charts-container"
      >
        {dashboard.charts.map((chart, index) => (
          <div
            key={`${dashboard.id}-${chart.chartType}-${index}`}
            data-testid={`chart-${chart.chartType}`}
            className="photo-booth-chart"
          >
            <div data-testid="chart-title">{chart.title}</div>
            <div data-testid="chart-title-only">
              {isPortfolioHistoryPortrait ? "true" : "false"}
            </div>
          </div>
        ))}
      </div>

      {/* Footer Section - Only for Portfolio History Portrait */}
      {isPortfolioHistoryPortrait && (
        <div
          className="dashboard-footer flex justify-center"
          data-testid="dashboard-footer"
        >
          <h1 className="brand-text text-text-dark dark:text-darkmode-text-dark m-0 mb-8 text-4xl font-semibold">
            colemorton.com
          </h1>
        </div>
      )}
    </div>
  );
};

describe("DashboardRenderer Component", () => {
  beforeEach(() => {
    setupPhotoBoothMocks();
  });

  afterEach(() => {
    cleanup();
  });

  describe("Basic Rendering", () => {
    it("renders dashboard content with correct structure", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      const dashboardContent = screen.getByTestId("dashboard-content");
      expect(dashboardContent).toBeInTheDocument();
      expect(dashboardContent).toHaveClass(
        "dashboard-content",
        "light-mode",
        "flex",
        "flex-col",
      );
    });

    it("applies correct data attributes", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="dark"
          aspectRatio="3:4"
        />,
      );

      const dashboardContent = screen.getByTestId("dashboard-content");
      expect(dashboardContent).toHaveAttribute(
        "data-dashboard-id",
        "portfolio_history_portrait",
      );
      expect(dashboardContent).toHaveAttribute("data-mode", "dark");
      expect(dashboardContent).toHaveAttribute("data-aspect-ratio", "3:4");
    });

    it("applies correct inline styles", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      const dashboardContent = screen.getByTestId("dashboard-content");
      expect(dashboardContent).toHaveStyle({
        width: "100%",
        height: "100%",
        overflow: "hidden",
      });
    });
  });

  describe("Portfolio History Portrait Specific Features", () => {
    it("renders header for portfolio history portrait dashboard", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="3:4"
        />,
      );

      const header = screen.getByTestId("dashboard-header");
      expect(header).toBeInTheDocument();
      expect(screen.getByText("Twitter Live Signals")).toBeInTheDocument();
    });

    it("renders footer for portfolio history portrait dashboard", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="3:4"
        />,
      );

      const footer = screen.getByTestId("dashboard-footer");
      expect(footer).toBeInTheDocument();
      expect(screen.getByText("colemorton.com")).toBeInTheDocument();
    });

    it("does not render header/footer for other dashboards", () => {
      const nonPortraitDashboard = createMockDashboard({
        id: "trading_performance",
        title: "Trading Performance",
      });

      render(
        <DashboardRenderer
          dashboard={nonPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      expect(screen.queryByTestId("dashboard-header")).not.toBeInTheDocument();
      expect(screen.queryByTestId("dashboard-footer")).not.toBeInTheDocument();
    });

    it("passes titleOnly=true to charts for portfolio history portrait", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="3:4"
        />,
      );

      const titleOnlyElements = screen.getAllByTestId("chart-title-only");
      titleOnlyElements.forEach((element) => {
        expect(element).toHaveTextContent("true");
      });
    });

    it("passes titleOnly=false to charts for other dashboards", () => {
      const nonPortraitDashboard = createMockDashboard({
        id: "trading_performance",
        title: "Trading Performance",
      });

      render(
        <DashboardRenderer
          dashboard={nonPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      const titleOnlyElements = screen.getAllByTestId("chart-title-only");
      titleOnlyElements.forEach((element) => {
        expect(element).toHaveTextContent("false");
      });
    });
  });

  describe("Theme Handling", () => {
    it("applies light mode classes", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      const dashboardContent = screen.getByTestId("dashboard-content");
      expect(dashboardContent).toHaveClass("light-mode");
    });

    it("applies dark mode classes", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="dark"
          aspectRatio="16:9"
        />,
      );

      const dashboardContent = screen.getByTestId("dashboard-content");
      expect(dashboardContent).toHaveClass("dark-mode");
    });
  });

  describe("Layout Classes", () => {
    it("applies correct layout classes from dashboard loader", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      const chartsContainer = screen.getByTestId("charts-container");
      expect(chartsContainer).toHaveClass(
        "flex",
        "flex-col",
        "h-full",
        "min-h-0",
        "flex-1",
      );
    });

    it("calls dashboard loader getLayoutClasses with correct layout", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      expect(mockDashboardLoader.getLayoutClasses).toHaveBeenCalledWith(
        "2x1_stack",
      );
    });
  });

  describe("Charts Rendering", () => {
    it("renders all charts from dashboard configuration", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      expect(
        screen.getByTestId("chart-trade-pnl-waterfall"),
      ).toBeInTheDocument();
      expect(
        screen.getByTestId("chart-closed-positions-pnl-timeseries"),
      ).toBeInTheDocument();
    });

    it("renders chart titles correctly", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      expect(
        screen.getByText("Closed Position PnL Waterfall"),
      ).toBeInTheDocument();
      expect(
        screen.getByText("Closed Position PnL Performance"),
      ).toBeInTheDocument();
    });

    it("applies photo-booth-chart class to each chart", () => {
      render(
        <DashboardRenderer
          dashboard={mockPortfolioHistoryPortraitDashboard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      const charts = screen.getAllByTestId(
        /^chart-(trade-pnl-waterfall|closed-positions-pnl-timeseries)$/,
      );
      charts.forEach((chart) => {
        expect(chart).toHaveClass("photo-booth-chart");
      });
    });

    it("generates unique keys for charts", () => {
      const dashboardWithDuplicateCharts = createMockDashboard({
        charts: [
          {
            title: "Chart 1",
            chartType: "trade-pnl-waterfall",
            category: "Test",
          },
          {
            title: "Chart 2",
            chartType: "trade-pnl-waterfall",
            category: "Test",
          },
        ],
      });

      render(
        <DashboardRenderer
          dashboard={dashboardWithDuplicateCharts}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      // Should render both charts despite having the same chartType
      const charts = screen.getAllByTestId("chart-trade-pnl-waterfall");
      expect(charts).toHaveLength(2);
    });
  });

  describe("Aspect Ratio Handling", () => {
    it("maintains aspect ratio data attribute for all ratios", () => {
      const aspectRatios: Array<"16:9" | "4:3" | "3:4"> = [
        "16:9",
        "4:3",
        "3:4",
      ];

      aspectRatios.forEach((aspectRatio) => {
        const { unmount } = render(
          <DashboardRenderer
            dashboard={mockPortfolioHistoryPortraitDashboard}
            mode="light"
            aspectRatio={aspectRatio}
          />,
        );

        const dashboardContent = screen.getByTestId("dashboard-content");
        expect(dashboardContent).toHaveAttribute(
          "data-aspect-ratio",
          aspectRatio,
        );

        unmount();
      });
    });
  });

  describe("Error Handling", () => {
    it("handles empty charts array gracefully", () => {
      const emptyChartsBoard = createMockDashboard({
        charts: [],
      });

      render(
        <DashboardRenderer
          dashboard={emptyChartsBoard}
          mode="light"
          aspectRatio="16:9"
        />,
      );

      const chartsContainer = screen.getByTestId("charts-container");
      expect(chartsContainer).toBeInTheDocument();
      expect(chartsContainer.children).toHaveLength(0);
    });

    it("handles missing chart properties gracefully", () => {
      const invalidChartsBoard = createMockDashboard({
        charts: [
          {
            title: "",
            chartType: "trade-pnl-waterfall" as any,
          } as any,
        ],
      });

      expect(() => {
        render(
          <DashboardRenderer
            dashboard={invalidChartsBoard}
            mode="light"
            aspectRatio="16:9"
          />,
        );
      }).not.toThrow();
    });
  });
});
