import React from "react";
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PhotoBoothDisplay from "@/shortcodes/PhotoBoothDisplay";
import {
  mockPhotoBoothConfig,
  mockURLSearchParams,
  mockWindowHistory,
  testScenarios,
} from "../mocks/photo-booth.mock";
import {
  mockAllDashboards,
  mockDashboardLoader,
  mockFetchSuccess,
  mockExportSuccess,
  mockExportError,
} from "../mocks/dashboard.mock";

// Mock the photo booth config
vi.mock("@/config/photo-booth.json", () => ({
  default: mockPhotoBoothConfig,
}));

// Mock the dashboard loader
vi.mock("@/services/dashboardLoader", () => ({
  DashboardLoader: mockDashboardLoader,
}));

// Mock ChartDisplay component
vi.mock("@/shortcodes/ChartDisplay", () => ({
  default: ({ title, chartType, titleOnly }: any) => (
    <div data-testid={`mock-chart-${chartType}`}>
      <div data-testid="chart-title">{title}</div>
      <div data-testid="chart-title-only">{titleOnly ? "true" : "false"}</div>
    </div>
  ),
}));

describe("Photo Booth Workflow Integration", () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    vi.clearAllMocks();

    // Mock successful dashboard loading
    mockDashboardLoader.getAllDashboards.mockResolvedValue(mockAllDashboards);

    // Mock successful export by default
    global.fetch = mockFetchSuccess(mockExportSuccess) as any;
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  describe("Complete Dashboard Loading Flow", () => {
    it("loads dashboard, shows loading state, then renders content", async () => {
      render(<PhotoBoothDisplay />);

      // Initially shows loading
      expect(screen.getByText("Loading dashboards...")).toBeInTheDocument();

      // Dashboard loads and content appears
      await waitFor(() => {
        expect(
          screen.getByText("Portfolio History Portrait"),
        ).toBeInTheDocument();
      });

      // Charts are rendered
      expect(
        screen.getByTestId("mock-chart-trade-pnl-waterfall"),
      ).toBeInTheDocument();
      expect(
        screen.getByTestId("mock-chart-closed-positions-pnl-timeseries"),
      ).toBeInTheDocument();

      // Ready state is achieved
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 16000 },
      );
    });

    it("handles dashboard loading failure and retry", async () => {
      // Mock initial failure
      mockDashboardLoader.getAllDashboards.mockRejectedValueOnce(
        new Error("Network error"),
      );

      render(<PhotoBoothDisplay />);

      // Shows error state
      await waitFor(() => {
        expect(
          screen.getByText("Failed to Load Dashboards"),
        ).toBeInTheDocument();
      });

      // Retry button appears
      const retryButton = screen.getByRole("button", { name: /retry/i });
      expect(retryButton).toBeInTheDocument();

      // Mock successful retry
      mockDashboardLoader.getAllDashboards.mockResolvedValue(mockAllDashboards);

      // Click retry
      await user.click(retryButton);

      // Should reload and show dashboard
      await waitFor(() => {
        expect(
          screen.getByText("Portfolio History Portrait"),
        ).toBeInTheDocument();
      });
    });
  });

  describe("Parameter Synchronization Workflow", () => {
    it("synchronizes all parameters between URL, state, and UI", async () => {
      const { mockReplaceState } = mockWindowHistory();

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      // Change dashboard
      const dashboardSelect = screen.getByLabelText(/dashboard/i);
      await user.selectOptions(dashboardSelect, "portfolio_history_portrait");

      // Change mode
      const darkButton = screen.getByRole("button", { name: /dark/i });
      await user.click(darkButton);

      // Change aspect ratio
      const aspectSelect = screen.getByLabelText(/ratio/i);
      await user.selectOptions(aspectSelect, "3:4");

      // Change format
      const formatSelect = screen.getByLabelText(/format/i);
      await user.selectOptions(formatSelect, "svg");

      // Change DPI
      const dpiSelect = screen.getByLabelText(/dpi/i);
      await user.selectOptions(dpiSelect, "600");

      // Change scale
      const scaleSelect = screen.getByLabelText(/scale/i);
      await user.selectOptions(scaleSelect, "4");

      // Verify URL updates were called
      expect(mockReplaceState).toHaveBeenCalledWith(
        {},
        "",
        expect.stringContaining("dashboard=portfolio_history_portrait"),
      );
      expect(mockReplaceState).toHaveBeenCalledWith(
        {},
        "",
        expect.stringContaining("mode=dark"),
      );
      expect(mockReplaceState).toHaveBeenCalledWith(
        {},
        "",
        expect.stringContaining("aspect_ratio=3:4"),
      );
    });

    it("maintains parameter consistency across state changes", async () => {
      mockURLSearchParams(testScenarios.portraitMode);

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        // Verify all parameters are reflected in UI
        expect(
          screen.getByDisplayValue("Portfolio History Portrait"),
        ).toBeInTheDocument();
        expect(screen.getByDisplayValue("3:4 Portrait")).toBeInTheDocument();
        expect(screen.getByDisplayValue("PNG")).toBeInTheDocument();
        expect(screen.getByDisplayValue("300 (Print)")).toBeInTheDocument();
        expect(screen.getByDisplayValue("3x")).toBeInTheDocument();

        const lightButton = screen.getByRole("button", { name: /light/i });
        expect(lightButton).toHaveClass("bg-blue-500");
      });
    });
  });

  describe("Aspect Ratio Workflow", () => {
    it("changes aspect ratio and updates dimensions", async () => {
      const mockSetProperty = vi.fn();
      const mockRef = {
        current: {
          style: {
            setProperty: mockSetProperty,
          },
        },
      };

      vi.spyOn(React, "useRef").mockReturnValue(mockRef);

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      // Change to 3:4 portrait
      const aspectSelect = screen.getByLabelText(/ratio/i);
      await user.selectOptions(aspectSelect, "3:4");

      // Verify CSS custom properties are set
      await waitFor(() => {
        expect(mockSetProperty).toHaveBeenCalledWith(
          "--photo-booth-width",
          "1080px",
        );
        expect(mockSetProperty).toHaveBeenCalledWith(
          "--photo-booth-height",
          "1440px",
        );
      });

      // Change to 4:3
      await user.selectOptions(aspectSelect, "4:3");

      await waitFor(() => {
        expect(mockSetProperty).toHaveBeenCalledWith(
          "--photo-booth-width",
          "1440px",
        );
        expect(mockSetProperty).toHaveBeenCalledWith(
          "--photo-booth-height",
          "1080px",
        );
      });

      // Change to 16:9
      await user.selectOptions(aspectSelect, "16:9");

      await waitFor(() => {
        expect(mockSetProperty).toHaveBeenCalledWith(
          "--photo-booth-width",
          "1920px",
        );
        expect(mockSetProperty).toHaveBeenCalledWith(
          "--photo-booth-height",
          "1080px",
        );
      });
    });

    it("resets ready state when aspect ratio changes", async () => {
      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      // Change aspect ratio
      const aspectSelect = screen.getByLabelText(/ratio/i);
      await user.selectOptions(aspectSelect, "3:4");

      // Should reset to loading state
      expect(screen.getByText("Loading...")).toBeInTheDocument();

      // Should eventually become ready again
      await waitFor(
        () => {
          expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
        },
        { timeout: 16000 },
      );
    });
  });

  describe("Theme Switching Workflow", () => {
    it("switches themes and applies correct classes", async () => {
      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      // Initially light mode
      const lightButton = screen.getByRole("button", { name: /light/i });
      const darkButton = screen.getByRole("button", { name: /dark/i });

      expect(lightButton).toHaveClass("bg-blue-500");
      expect(darkButton).not.toHaveClass("bg-blue-500");

      // Switch to dark mode
      await user.click(darkButton);

      await waitFor(() => {
        expect(darkButton).toHaveClass("bg-blue-500");
        expect(lightButton).not.toHaveClass("bg-blue-500");

        // Dashboard should have dark class
        const dashboard = document.querySelector(".photo-booth-dashboard");
        expect(dashboard).toHaveClass("dark");
      });

      // Switch back to light mode
      await user.click(lightButton);

      await waitFor(() => {
        expect(lightButton).toHaveClass("bg-blue-500");
        expect(darkButton).not.toHaveClass("bg-blue-500");

        // Dashboard should not have dark class
        const dashboard = document.querySelector(".photo-booth-dashboard");
        expect(dashboard).not.toHaveClass("dark");
      });
    });
  });

  describe("Export Workflow", () => {
    it("completes full export workflow successfully", async () => {
      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      // Set up specific parameters
      const aspectSelect = screen.getByLabelText(/ratio/i);
      await user.selectOptions(aspectSelect, "3:4");

      const darkButton = screen.getByRole("button", { name: /dark/i });
      await user.click(darkButton);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      // Start export
      const exportButton = screen.getByRole("button", {
        name: /export dashboard/i,
      });
      await user.click(exportButton);

      // Should show exporting state
      expect(screen.getByText("Exporting...")).toBeInTheDocument();
      expect(exportButton).toBeDisabled();

      // Verify API call was made with correct parameters
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith("/api/export-dashboard", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            dashboard_id: "portfolio_history_portrait",
            mode: "dark",
            aspect_ratio: "3:4",
            format: "png",
            dpi: 300,
            scale_factor: 3,
          }),
        });
      });

      // Should show success message
      await waitFor(() => {
        expect(screen.getByText(/successfully exported/i)).toBeInTheDocument();
      });

      // Export button should be enabled again
      expect(exportButton).not.toBeDisabled();
      expect(screen.getByText("Export Dashboard")).toBeInTheDocument();
    });

    it("handles export failure gracefully", async () => {
      global.fetch = mockFetchSuccess(mockExportError) as any;

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      const exportButton = screen.getByRole("button", {
        name: /export dashboard/i,
      });
      await user.click(exportButton);

      // Should show error message
      await waitFor(() => {
        expect(
          screen.getByText(/export generation failed/i),
        ).toBeInTheDocument();
      });

      // Export button should be enabled again
      expect(exportButton).not.toBeDisabled();
    });

    it("prevents multiple simultaneous exports", async () => {
      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      const exportButton = screen.getByRole("button", {
        name: /export dashboard/i,
      });

      // Start first export
      await user.click(exportButton);
      expect(exportButton).toBeDisabled();

      // Try to start second export
      await user.click(exportButton);

      // Fetch should only be called once
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe("Portfolio History Portrait Specific Workflow", () => {
    it("renders portfolio history portrait with correct elements", async () => {
      mockURLSearchParams({ dashboard: "portfolio_history_portrait" });

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        // Header should appear
        expect(screen.getByText("Twitter Live Signals")).toBeInTheDocument();

        // Footer should appear
        expect(screen.getByText("colemorton.com")).toBeInTheDocument();

        // Charts should have titleOnly=true
        const titleOnlyElements = screen.getAllByTestId("chart-title-only");
        titleOnlyElements.forEach((element) => {
          expect(element).toHaveTextContent("true");
        });

        // Both charts should be present
        expect(
          screen.getByTestId("mock-chart-trade-pnl-waterfall"),
        ).toBeInTheDocument();
        expect(
          screen.getByTestId("mock-chart-closed-positions-pnl-timeseries"),
        ).toBeInTheDocument();
      });
    });

    it("applies correct layout classes for 2x1_stack", async () => {
      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        const chartsContainer = document.querySelector(".flex.flex-col.h-full");
        expect(chartsContainer).toBeInTheDocument();
      });

      expect(mockDashboardLoader.getLayoutClasses).toHaveBeenCalledWith(
        "2x1_stack",
      );
    });
  });

  describe("Advanced Parameter Combinations", () => {
    it("handles all parameter combinations correctly", async () => {
      const { mockReplaceState } = mockWindowHistory();

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      // Test multiple parameter changes in sequence
      const changes = [
        { element: "aspect_ratio", value: "3:4", selector: /ratio/i },
        { element: "format", value: "svg", selector: /format/i },
        { element: "dpi", value: "600", selector: /dpi/i },
        { element: "scale", value: "4", selector: /scale/i },
      ];

      for (const change of changes) {
        const select = screen.getByLabelText(change.selector);
        await user.selectOptions(select, change.value);

        // Wait for ready state after each change
        await waitFor(
          () => {
            expect(
              screen.getByText("Ready for screenshot"),
            ).toBeInTheDocument();
          },
          { timeout: 16000 },
        );
      }

      // Verify final state
      expect(screen.getByDisplayValue("3:4 Portrait")).toBeInTheDocument();
      expect(screen.getByDisplayValue("SVG")).toBeInTheDocument();
      expect(screen.getByDisplayValue("600 (Ultra)")).toBeInTheDocument();
      expect(screen.getByDisplayValue("4x")).toBeInTheDocument();

      // Verify multiple URL updates occurred
      expect(mockReplaceState).toHaveBeenCalledTimes(4);
    });
  });

  describe("Error Recovery Workflow", () => {
    it("recovers from temporary network failures", async () => {
      // Start with network error
      global.fetch = vi.fn(() =>
        Promise.reject(new Error("Network error")),
      ) as any;

      render(<PhotoBoothDisplay />);

      await waitFor(() => {
        expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
      });

      const exportButton = screen.getByRole("button", {
        name: /export dashboard/i,
      });
      await user.click(exportButton);

      // Should show error
      await waitFor(() => {
        expect(screen.getByText(/export failed/i)).toBeInTheDocument();
      });

      // Fix network and try again
      global.fetch = mockFetchSuccess(mockExportSuccess) as any;

      // Dismiss error
      const dismissButton = screen.getByText("×");
      await user.click(dismissButton);

      // Try export again
      await user.click(exportButton);

      // Should succeed this time
      await waitFor(() => {
        expect(screen.getByText(/successfully exported/i)).toBeInTheDocument();
      });
    });
  });
});
