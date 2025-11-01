import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";

// Helper to mock URL search params
export const mockURLSearchParams = (params: Record<string, string>) => {
  const searchParams = new URLSearchParams(params);

  Object.defineProperty(window, "location", {
    value: {
      search: searchParams.toString(),
      href: `http://localhost:4321/photo-booth?${searchParams.toString()}`,
      origin: "http://localhost:4321",
      pathname: "/photo-booth",
    },
    writable: true,
    configurable: true,
  });

  return searchParams;
};

// Helper to mock window.history
export const mockWindowHistory = () => {
  const mockReplaceState = vi.fn();
  const mockPushState = vi.fn();

  Object.defineProperty(window, "history", {
    value: {
      replaceState: mockReplaceState,
      pushState: mockPushState,
    },
    writable: true,
    configurable: true,
  });

  return { mockReplaceState, mockPushState };
};

// Helper to wait for photo booth to be ready
export const waitForPhotoBoothReady = async (timeout = 20000) => {
  await waitFor(
    () => {
      expect(screen.getByText("Ready for screenshot")).toBeInTheDocument();
    },
    { timeout },
  );
};

// Helper to wait for dashboard to load
export const waitForDashboardLoad = async () => {
  await waitFor(() => {
    expect(screen.queryByText("Loading dashboards...")).not.toBeInTheDocument();
  });
};

// Helper to simulate export process
export const simulateExport = async (
  user: ReturnType<typeof userEvent.setup>,
) => {
  const exportButton = screen.getByRole("button", {
    name: /export dashboard/i,
  });
  await user.click(exportButton);

  // Wait for export to complete
  await waitFor(() => {
    expect(screen.queryByText("Exporting...")).not.toBeInTheDocument();
  });
};

// Helper to check if element has expected CSS custom properties
export const expectCSSCustomProperties = (
  element: HTMLElement,
  properties: Record<string, string>,
) => {
  const style = getComputedStyle(element);

  Object.entries(properties).forEach(([property, value]) => {
    expect(style.getPropertyValue(property)).toBe(value);
  });
};

// Helper to simulate parameter changes
export const changePhotoBoothParams = async (
  user: ReturnType<typeof userEvent.setup>,
  params: {
    aspectRatio?: string;
    mode?: "light" | "dark";
    format?: string;
    dpi?: string;
    scale?: string;
    dashboard?: string;
  },
) => {
  if (params.aspectRatio) {
    const aspectSelect = screen.getByLabelText(/ratio/i);
    await user.selectOptions(aspectSelect, params.aspectRatio);
  }

  if (params.mode) {
    const modeButton = screen.getByRole("button", {
      name: new RegExp(params.mode, "i"),
    });
    await user.click(modeButton);
  }

  if (params.format) {
    const formatSelect = screen.getByLabelText(/format/i);
    await user.selectOptions(formatSelect, params.format);
  }

  if (params.dpi) {
    const dpiSelect = screen.getByLabelText(/dpi/i);
    await user.selectOptions(dpiSelect, params.dpi);
  }

  if (params.scale) {
    const scaleSelect = screen.getByLabelText(/scale/i);
    await user.selectOptions(scaleSelect, params.scale);
  }

  if (params.dashboard) {
    const dashboardSelect = screen.getByLabelText(/dashboard/i);
    await user.selectOptions(dashboardSelect, params.dashboard);
  }
};

// Helper to verify dashboard content structure
export const verifyDashboardStructure = (dashboardId: string) => {
  const isPortfolioHistory = dashboardId === "portfolio_history_portrait";

  if (isPortfolioHistory) {
    // Should have header and footer
    expect(screen.getByText("Twitter Live Signals")).toBeInTheDocument();
    expect(screen.getByText("colemorton.com")).toBeInTheDocument();
  }

  // Should have charts
  const charts = screen.getAllByTestId(/^mock-chart-/);
  expect(charts.length).toBeGreaterThan(0);
};
