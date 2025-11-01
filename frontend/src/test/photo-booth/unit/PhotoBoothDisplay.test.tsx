import React from "react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";

// Mock photo-booth config BEFORE importing the component
vi.mock("@/config/photo-booth.json", () => ({
  default: {
    default_dashboard: "portfolio_history_portrait",
    performance: {
      render_timeout: 100, // Faster for testing
    },
    export_options: {
      aspect_ratios: {
        available: [
          {
            id: "16:9",
            name: "Widescreen (16:9)",
            dimensions: { width: 1920, height: 1080 },
          },
          {
            id: "4:3",
            name: "Traditional (4:3)",
            dimensions: { width: 1440, height: 1080 },
          },
          {
            id: "3:4",
            name: "Portrait (3:4)",
            dimensions: { width: 1080, height: 1440 },
          },
        ],
      },
    },
  },
}));

// Mock dashboard loader BEFORE importing the component
vi.mock("@/services/dashboardLoader", () => ({
  DashboardLoader: {
    getAllDashboards: vi.fn(() =>
      Promise.resolve([
        {
          id: "trading_performance",
          title: "Trading Performance Dashboard",
          description: "Comprehensive trading strategy performance overview",
          layout: "2x2_grid",
          mode: "both",
          enabled: true,
          charts: [
            {
              title: "Bitcoin Portfolio Value Comparison",
              category: "Bitcoin Performance",
              description:
                "Multi-strategy Bitcoin trading vs buy-and-hold approach from 2014-2025",
              chartType: "portfolio-value-comparison",
            },
            {
              title: "Trade PnL Distribution",
              category: "Trading Performance",
              description: "Distribution of profit/loss across all trades",
              chartType: "trade-pnl-distribution",
            },
          ],
        },
        {
          id: "portfolio_history_portrait",
          title: "Portfolio History Portrait",
          description:
            "Portfolio trading history with waterfall and time series analysis",
          layout: "2x1_stack",
          mode: "both",
          enabled: true,
          charts: [
            {
              title: "Closed Position PnL Waterfall",
              category: "Trading Performance",
              description:
                "Waterfall chart showing individual trade profits and losses from closed positions, sorted from highest to lowest PnL. Visualizes contribution of each trade to overall portfolio performance.",
              chartType: "trade-pnl-waterfall",
            },
            {
              title: "Closed Position PnL Performance",
              category: "Trading Performance",
              description:
                "Multi-line time series showing cumulative PnL for each closed position, indexed to $0 at entry date. Track performance progression across the closed portfolio with individual lines for each ticker.",
              chartType: "closed-positions-pnl-timeseries",
            },
          ],
        },
      ]),
    ),
    getDashboard: vi.fn((id: string) => {
      const dashboards = [
        { id: "trading_performance", title: "Trading Performance Dashboard" },
        {
          id: "portfolio_history_portrait",
          title: "Portfolio History Portrait",
        },
      ];
      return Promise.resolve(dashboards.find((d) => d.id === id) || null);
    }),
    getLayoutClasses: vi.fn((layout: string) => {
      const layoutMappings: Record<string, string> = {
        "2x2_grid": "grid grid-cols-1 gap-6 lg:grid-cols-2 h-full",
        "2x1_stack": "flex flex-col h-full",
      };
      return layoutMappings[layout] || "flex flex-col h-full";
    }),
  },
}));

// Mock chart display component
vi.mock("@/shortcodes/ChartDisplay", () => ({
  default: ({ title, chartType, titleOnly, className }: any) => (
    <div data-testid={`mock-chart-${chartType}`} className={className || ""}>
      <div data-testid="chart-title">{title}</div>
      <div data-testid="chart-title-only">{titleOnly ? "true" : "false"}</div>
    </div>
  ),
}));

import PhotoBoothDisplay from "@/shortcodes/PhotoBoothDisplay";
import { DashboardLoader } from "@/services/dashboardLoader";
import {
  setupPhotoBoothMocks,
  mockFetchError,
  mockNetworkError,
} from "../__mocks__/setup.tsx";
import { testURLParams } from "../__mocks__/test-data.mock";
import { mockURLSearchParams, mockWindowHistory } from "../utils/test-helpers";

// Get the mocked DashboardLoader for per-test overrides
const mockDashboardLoader = vi.mocked(DashboardLoader);

describe("PhotoBoothDisplay Component", () => {
  beforeEach(() => {
    setupPhotoBoothMocks();
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  describe("Component Initialization", () => {
    it("renders loading state initially", () => {
      render(<PhotoBoothDisplay />);

      expect(screen.getByText("Loading dashboards...")).toBeInTheDocument();
    });

    it("renders dashboard after successful loading", async () => {
      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });
    });

    it("displays error when dashboard loading fails", async () => {
      mockDashboardLoader.getAllDashboards.mockRejectedValue(
        new Error("Network error"),
      );

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(
          screen.getByText("Failed to Load Dashboards"),
        ).toBeInTheDocument();
      });
    });
  });

  describe("URL Parameter Parsing", () => {
    it("parses dashboard parameter from URL", async () => {
      mockURLSearchParams(testURLParams.portraitMode);

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const select = screen.getByDisplayValue("Portfolio History Portrait");
        expect(select).toBeInTheDocument();
      });
    });

    it("parses mode parameter and sets theme", async () => {
      mockURLSearchParams({ mode: "dark" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const darkButton = screen.getByRole("button", { name: /dark/i });
        expect(darkButton).toHaveClass("bg-blue-500");
      });
    });

    it("parses aspect ratio parameter", async () => {
      mockURLSearchParams({ aspect_ratio: "3:4" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const aspectSelect = screen.getByDisplayValue("3:4 Portrait");
        expect(aspectSelect).toBeInTheDocument();
      });
    });

    it("parses format parameter", async () => {
      mockURLSearchParams({ format: "svg" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const formatSelect = screen.getByDisplayValue("SVG");
        expect(formatSelect).toBeInTheDocument();
      });
    });

    it("parses DPI parameter", async () => {
      mockURLSearchParams({ dpi: "600" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const dpiSelect = screen.getByDisplayValue("600 (Ultra)");
        expect(dpiSelect).toBeInTheDocument();
      });
    });

    it("parses scale factor parameter", async () => {
      mockURLSearchParams({ scale: "4" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const scaleSelect = screen.getByDisplayValue("4x");
        expect(scaleSelect).toBeInTheDocument();
      });
    });
  });

  describe("State Management", () => {
    it("updates URL when dashboard changes", async () => {
      const { mockReplaceState } = mockWindowHistory();

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const select = screen.getByLabelText(/dashboard/i);
        fireEvent.change(select, {
          target: { value: "portfolio_history_portrait" },
        });
      });

      expect(mockReplaceState).toHaveBeenCalledWith(
        {},
        "",
        expect.stringContaining("dashboard=portfolio_history_portrait"),
      );
    });

    it("updates URL when mode changes", async () => {
      const { mockReplaceState } = mockWindowHistory();

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const darkButton = screen.getByRole("button", { name: /dark/i });
        fireEvent.click(darkButton);
      });

      expect(mockReplaceState).toHaveBeenCalledWith(
        {},
        "",
        expect.stringContaining("mode=dark"),
      );
    });

    it("updates URL when aspect ratio changes", async () => {
      const { mockReplaceState } = mockWindowHistory();

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const aspectSelect = screen.getByLabelText(/ratio/i);
        fireEvent.change(aspectSelect, { target: { value: "3:4" } });
      });

      expect(mockReplaceState).toHaveBeenCalled();

      // Get the actual URL that was passed
      const actualURL = mockReplaceState.mock.calls[0][2];
      expect(actualURL).toMatch(/aspect_ratio=3(%3A|:)4/); // Handle URL encoding of ':'
    });
  });

  describe("CSS Custom Properties", () => {
    it("sets CSS custom properties based on aspect ratio", async () => {
      mockURLSearchParams({ aspect_ratio: "3:4" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Find the dashboard element with the actual CSS custom properties
      const dashboardElement = document.querySelector(".photo-booth-dashboard");
      expect(dashboardElement).toHaveStyle("--photo-booth-width: 1080px");
      expect(dashboardElement).toHaveStyle("--photo-booth-height: 1440px");
    });
  });

  describe("Export Functionality", () => {
    it("shows export button when dashboard is ready", async () => {
      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Wait for ready state timeout to complete (100ms from mock config)
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 1000 },
      );

      await waitFor(() => {
        const exportButton = screen.getByRole("button", {
          name: /export dashboard/i,
        });
        expect(exportButton).toBeInTheDocument();
        expect(exportButton).not.toBeDisabled();
      });
    });

    it("disables export button when dashboard is loading", async () => {
      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // During ready state loading, button should be disabled
      const exportButton = screen.getByRole("button", {
        name: /export dashboard/i,
      });
      expect(exportButton).toBeDisabled();

      // Should show loading state
      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });

    it("calls export API with correct parameters", async () => {
      mockURLSearchParams(testURLParams.portraitMode);

      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Wait for ready state timeout to complete (100ms from mock config)
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 1000 },
      );

      await waitFor(async () => {
        const exportButton = screen.getByRole("button", {
          name: /export dashboard/i,
        });
        fireEvent.click(exportButton);

        expect(global.fetch).toHaveBeenCalledWith("/api/export-dashboard", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            dashboard_id: "portfolio_history_portrait",
            mode: "light",
            aspect_ratio: "3:4",
            format: "png",
            dpi: 300,
            scale_factor: 3,
          }),
        });
      });
    });

    it("shows success message after successful export", async () => {
      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Wait for ready state timeout to complete (100ms from mock config)
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 1000 },
      );

      await waitFor(async () => {
        const exportButton = screen.getByRole("button", {
          name: /export dashboard/i,
        });
        fireEvent.click(exportButton);

        await waitFor(() => {
          expect(
            screen.getByText(/successfully exported/i),
          ).toBeInTheDocument();
        });
      });
    });

    it("shows error message after failed export", async () => {
      global.fetch = mockFetchError(500, "Export failed") as any;

      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Wait for ready state timeout to complete (100ms from mock config)
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 1000 },
      );

      await waitFor(async () => {
        const exportButton = screen.getByRole("button", {
          name: /export dashboard/i,
        });
        fireEvent.click(exportButton);

        await waitFor(() => {
          expect(screen.getByText(/export failed/i)).toBeInTheDocument();
        });
      });
    });

    it("handles network errors gracefully", async () => {
      global.fetch = mockNetworkError() as any;

      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Wait for ready state timeout to complete (100ms from mock config)
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 1000 },
      );

      await waitFor(async () => {
        const exportButton = screen.getByRole("button", {
          name: /export dashboard/i,
        });
        fireEvent.click(exportButton);

        await waitFor(() => {
          expect(screen.getByText(/export failed/i)).toBeInTheDocument();
        });
      });
    });
  });

  describe("Dashboard Content Rendering", () => {
    it("renders portfolio history portrait with header and footer", async () => {
      mockURLSearchParams({ dashboard: "portfolio_history_portrait" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Twitter Live Signals")).toBeInTheDocument();
        expect(screen.getByText("colemorton.com")).toBeInTheDocument();
      });
    });

    it("passes titleOnly=true to charts in portfolio history portrait", async () => {
      mockURLSearchParams({ dashboard: "portfolio_history_portrait" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const titleOnlyElements = screen.getAllByTestId("chart-title-only");
        titleOnlyElements.forEach((element) => {
          expect(element).toHaveTextContent("true");
        });
      });
    });

    it("applies correct theme class to dashboard", async () => {
      mockURLSearchParams({ mode: "dark" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Test that the dashboard wrapper has the dark class
      const dashboardWrapper = document.querySelector(".photo-booth-dashboard");
      expect(dashboardWrapper).toHaveClass("dark");

      // Test that the dashboard content has the dark-mode class
      const dashboardContent = document.querySelector(".dashboard-content");
      expect(dashboardContent).toHaveClass("dark-mode");
    });
  });

  describe("Ready State Management", () => {
    it("marks component as ready after timeout", async () => {
      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Initially should show loading (ready state loading)
      expect(screen.getByText("Loading...")).toBeInTheDocument();

      // Wait for ready state timeout to complete (100ms from mock config)
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 1000 },
      );
    });

    it("resets ready state when parameters change", async () => {
      render(<PhotoBoothDisplay />);

      // Wait for dashboard loading to complete first
      await waitFor(() => {
        expect(
          screen.getByRole("heading", { name: "Portfolio History Portrait" }),
        ).toBeInTheDocument();
      });

      // Wait for ready state timeout to complete (100ms from mock config)
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 1000 },
      );

      // Change a parameter (mode button)
      const modeButton = screen.getByRole("button", { name: /dark/i });
      fireEvent.click(modeButton);

      // Should reset to loading
      expect(screen.getByText("Loading...")).toBeInTheDocument();
    });
  });

  describe("Error Handling", () => {
    it("shows retry button when dashboard loading fails", async () => {
      mockDashboardLoader.getAllDashboards.mockRejectedValue(
        new Error("Network error"),
      );

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const retryButton = screen.getByRole("button", { name: /retry/i });
        expect(retryButton).toBeInTheDocument();
      });
    });

    it("handles invalid dashboard ID gracefully", async () => {
      mockURLSearchParams({ dashboard: "invalid_dashboard" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Dashboard Not Found")).toBeInTheDocument();
      });
    });

    it("falls back to defaults for invalid parameters", async () => {
      mockURLSearchParams(testURLParams.invalidFormatParams);

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        // Should fall back to default values
        expect(screen.getByDisplayValue("16:9 Wide")).toBeInTheDocument();
        expect(screen.getByDisplayValue("PNG")).toBeInTheDocument();
      });
    });
  });
});
