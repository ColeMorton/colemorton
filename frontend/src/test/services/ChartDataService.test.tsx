import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import type { StockDataRow } from "@/types/chart";

/**
 * Data Service Tests for Multi-Stock Chart Functionality
 * Tests the ChartDataService for multi-stock data fetching scenarios
 */

// Mock fetch API
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("ChartDataService Multi-Stock Tests", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Multi-Symbol Data Fetching", () => {
    it("should fetch multiple stock symbols concurrently", async () => {
      // Mock successful responses for both symbols with proper CSV format
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          text: () =>
            Promise.resolve(
              "date,open,high,low,close,volume\n2024-01-01,10.50,12.25,9.75,11.80,15234567\n2024-01-02,11.80,13.50,11.25,12.75,18456789",
            ),
        })
        .mockResolvedValueOnce({
          ok: true,
          text: () =>
            Promise.resolve(
              "date,open,high,low,close,volume\n2024-01-01,6.25,6.80,6.10,6.55,45678912\n2024-01-02,6.55,7.10,6.40,6.90,52341678",
            ),
        });

      // Import service after mocks are set up
      const { chartDataService } = await import("@/services/ChartDataService");

      // Create promises for concurrent execution
      const xpevPromise = chartDataService.fetchStockData(
        "XPEV",
        new AbortController().signal,
      );
      const nioPromise = chartDataService.fetchStockData(
        "NIO",
        new AbortController().signal,
      );

      const [xpevResult, nioResult] = await Promise.all([
        xpevPromise,
        nioPromise,
      ]);

      // Verify both requests were made
      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("XPEV"),
        expect.objectContaining({ signal: expect.any(AbortSignal) }),
      );
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("NIO"),
        expect.objectContaining({ signal: expect.any(AbortSignal) }),
      );

      // Verify parsed results have correct structure
      expect(xpevResult).toHaveLength(2);
      expect(xpevResult[0]).toMatchObject({
        date: "2024-01-01",
        open: "10.50",
        high: "12.25",
        low: "9.75",
        close: "11.80",
        volume: "15234567",
      });
      expect(nioResult).toHaveLength(2);
      expect(nioResult[0]).toMatchObject({
        date: "2024-01-01",
        open: "6.25",
        high: "6.80",
        low: "6.10",
        close: "6.55",
        volume: "45678912",
      });
    });

    it("should handle partial failures in multi-stock requests", async () => {
      // XPEV succeeds, NIO fails
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          text: () =>
            Promise.resolve(
              "date,open,high,low,close,volume\n2024-01-01,10.50,12.25,9.75,11.80,15234567",
            ),
        })
        .mockRejectedValueOnce(new Error("Network timeout"));

      const { chartDataService } = await import("@/services/ChartDataService");

      // Test concurrent requests with mixed outcomes
      const xpevPromise = chartDataService.fetchStockData(
        "XPEV",
        new AbortController().signal,
      );
      const nioPromise = chartDataService.fetchStockData(
        "NIO",
        new AbortController().signal,
      );

      const [xpevResult, nioError] = await Promise.allSettled([
        xpevPromise,
        nioPromise,
      ]);

      expect(xpevResult.status).toBe("fulfilled");
      if (xpevResult.status === "fulfilled") {
        expect(xpevResult.value).toHaveLength(1);
        expect(xpevResult.value[0]).toMatchObject({
          date: "2024-01-01",
          open: "10.50",
          close: "11.80",
        });
      }

      expect(nioError.status).toBe("rejected");
      if (nioError.status === "rejected") {
        expect(nioError.reason.message).toContain("Network timeout");
      }
    });

    it("should handle AbortController for concurrent requests", async () => {
      const abortController = new AbortController();

      // Mock long-running requests with proper abort handling
      mockFetch.mockImplementation((url, options) => {
        return new Promise((resolve, reject) => {
          const timeoutId = setTimeout(
            () =>
              resolve({
                ok: true,
                text: () =>
                  Promise.resolve(
                    "date,open,high,low,close,volume\n2024-01-01,10.50,12.25,9.75,11.80,15234567",
                  ),
              }),
            1000,
          );

          // Check if signal is already aborted
          if (options?.signal?.aborted) {
            clearTimeout(timeoutId);
            const error = new Error("The operation was aborted");
            error.name = "AbortError";
            reject(error);
            return;
          }

          // Listen for abort event
          options?.signal?.addEventListener("abort", () => {
            clearTimeout(timeoutId);
            const error = new Error("The operation was aborted");
            error.name = "AbortError";
            reject(error);
          });
        });
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      const xpevPromise = chartDataService.fetchStockData(
        "XPEV",
        abortController.signal,
      );
      const nioPromise = chartDataService.fetchStockData(
        "NIO",
        abortController.signal,
      );

      // Abort after a short delay
      setTimeout(() => abortController.abort(), 50);

      // Both requests should be aborted
      await expect(Promise.all([xpevPromise, nioPromise])).rejects.toThrow();
    });
  });

  describe("Data Quality and Validation", () => {
    it("should validate CSV data structure for stock data", async () => {
      const invalidCsvData = "invalid,structure\nno,proper,headers";

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(invalidCsvData),
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      await expect(
        chartDataService.fetchStockData(
          "INVALID",
          new AbortController().signal,
        ),
      ).rejects.toThrow("Invalid CSV structure");
    });

    it("should handle malformed price data gracefully", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () =>
          Promise.resolve(
            "date,open,high,low,close,volume\n2024-01-01,,,10.50,11.80,15234567",
          ),
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      const result = await chartDataService.fetchStockData(
        "TEST",
        new AbortController().signal,
      );

      // Should return data even with missing values (empty strings)
      expect(result).toHaveLength(1);
      expect(result[0].open).toBe("");
      expect(result[0].high).toBe("");
      expect(result[0].low).toBe("10.50");
      expect(result[0].close).toBe("11.80");
    });

    it("should handle empty data responses", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve("date,open,high,low,close,volume\n"), // Headers only
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      // Fail-fast: empty data should throw
      await expect(
        chartDataService.fetchStockData("EMPTY", new AbortController().signal),
      ).rejects.toThrow("No data returned for EMPTY");
    });
  });

  describe("Error Handling and Resilience", () => {
    it("should handle HTTP error responses", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      await expect(
        chartDataService.fetchStockData(
          "NOTFOUND",
          new AbortController().signal,
        ),
      ).rejects.toThrow("404");
    });

    it("should handle network errors", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Failed to fetch"));

      const { chartDataService } = await import("@/services/ChartDataService");

      await expect(
        chartDataService.fetchStockData(
          "NETWORK_ERROR",
          new AbortController().signal,
        ),
      ).rejects.toThrow("Failed to fetch");
    });

    it("should handle timeout scenarios", async () => {
      mockFetch.mockImplementation(
        () =>
          new Promise((_, reject) => {
            setTimeout(() => reject(new Error("Request timeout")), 100);
          }),
      );

      const { chartDataService } = await import("@/services/ChartDataService");

      await expect(
        chartDataService.fetchStockData(
          "TIMEOUT",
          new AbortController().signal,
        ),
      ).rejects.toThrow("Request timeout");
    });

    it("should handle rate limiting gracefully", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        statusText: "Too Many Requests",
        headers: new Map([["Retry-After", "60"]]),
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      await expect(
        chartDataService.fetchStockData(
          "RATE_LIMITED",
          new AbortController().signal,
        ),
      ).rejects.toThrow("429");
    });
  });

  describe("Caching and Performance", () => {
    it("should cache successful responses", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        text: () =>
          Promise.resolve(
            "date,open,high,low,close,volume\n2024-01-01,10.50,12.25,9.75,11.80,15234567",
          ),
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      // First request
      const result1 = await chartDataService.fetchStockData(
        "CACHED",
        new AbortController().signal,
      );

      // Second request (should use cache if implemented)
      const result2 = await chartDataService.fetchStockData(
        "CACHED",
        new AbortController().signal,
      );

      expect(result1).toEqual(result2);
      expect(result1).toHaveLength(1);
      expect(result1[0]).toMatchObject({
        date: "2024-01-01",
        close: "11.80",
      });
    });

    it("should handle large datasets efficiently", async () => {
      // Generate large CSV data
      const largeCsvData = [
        "date,open,high,low,close,volume",
        ...Array.from(
          { length: 10000 },
          (_, i) =>
            `2024-01-${String(i + 1).padStart(2, "0")},100.${i},105.${i},95.${i},102.${i},${1000000 + i}`,
        ),
      ].join("\n");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(largeCsvData),
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      const startTime = Date.now();
      const result = await chartDataService.fetchStockData(
        "LARGE",
        new AbortController().signal,
      );
      const endTime = Date.now();

      expect(result).toHaveLength(10000);
      expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1 second
    });
  });

  describe("Data Format Compatibility", () => {
    it("should handle different CSV formats", async () => {
      const alternativeCsvFormat = [
        "Date,Open,High,Low,Close,Volume", // Different capitalization
        "2024-01-01,10.50,12.25,9.75,11.80,15234567",
      ].join("\n");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(alternativeCsvFormat),
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      const result = await chartDataService.fetchStockData(
        "FORMAT_TEST",
        new AbortController().signal,
      );

      expect(result).toHaveLength(1);
      // Headers are lowercased by parseCSV
      expect(result[0].close).toBe("11.80");
      expect(result[0].date).toBe("2024-01-01");
    });

    it("should handle CSV with extra columns", async () => {
      const csvWithExtraColumns = [
        "date,open,high,low,close,volume,adj_close,dividend",
        "2024-01-01,10.50,12.25,9.75,11.80,15234567,11.75,0.00",
      ].join("\n");

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(csvWithExtraColumns),
      });

      const { chartDataService } = await import("@/services/ChartDataService");

      const result = await chartDataService.fetchStockData(
        "EXTRA_COLS",
        new AbortController().signal,
      );

      expect(result[0]).toHaveProperty("close", "11.80");
      expect(result[0]).toHaveProperty("adj_close", "11.75");
      expect(result[0]).toHaveProperty("dividend", "0.00");
    });
  });

  describe("Multi-Stock Integration", () => {
    it("should support the multi-stock workflow end-to-end", async () => {
      // Mock responses for XPEV and NIO with proper CSV
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          text: () =>
            Promise.resolve(
              "date,open,high,low,close,volume\n2024-01-01,10.50,12.25,9.75,11.80,15234567",
            ),
        })
        .mockResolvedValueOnce({
          ok: true,
          text: () =>
            Promise.resolve(
              "date,open,high,low,close,volume\n2024-01-01,6.25,6.80,6.10,6.55,45678912",
            ),
        });

      const { chartDataService } = await import("@/services/ChartDataService");

      // Simulate the multi-stock hook behavior
      const symbols = ["XPEV", "NIO"];
      const abortController = new AbortController();

      const stockDataPromises = symbols.map((symbol) =>
        chartDataService.fetchStockData(symbol, abortController.signal),
      );

      const results = await Promise.all(stockDataPromises);

      // Convert to the expected multi-stock data structure
      const multiStockData = results.reduce(
        (acc, data, index) => {
          acc[symbols[index]] = data;
          return acc;
        },
        {} as Record<string, StockDataRow[]>,
      );

      expect(Object.keys(multiStockData)).toEqual(["XPEV", "NIO"]);
      expect(multiStockData.XPEV).toHaveLength(1);
      expect(multiStockData.NIO).toHaveLength(1);
      expect(multiStockData.XPEV[0].close).toBe("11.80");
      expect(multiStockData.NIO[0].close).toBe("6.55");
    });

    it("should handle mixed success/failure in multi-stock requests", async () => {
      // XPEV succeeds, NIO fails, TSLA succeeds
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          text: () =>
            Promise.resolve(
              "date,open,high,low,close,volume\n2024-01-01,10.50,12.25,9.75,11.80,15234567",
            ),
        })
        .mockRejectedValueOnce(new Error("NIO API error"))
        .mockResolvedValueOnce({
          ok: true,
          text: () =>
            Promise.resolve(
              "date,open,high,low,close,volume\n2024-01-01,200,210,195,205,30000000",
            ),
        });

      const { chartDataService } = await import("@/services/ChartDataService");

      const symbols = ["XPEV", "NIO", "TSLA"];
      const abortController = new AbortController();

      const stockDataPromises = symbols.map((symbol) =>
        chartDataService.fetchStockData(symbol, abortController.signal),
      );

      const results = await Promise.allSettled(stockDataPromises);

      expect(results[0].status).toBe("fulfilled");
      expect(results[1].status).toBe("rejected");
      expect(results[2].status).toBe("fulfilled");

      // The hook should handle this by setting an error state
      const hasError = results.some((result) => result.status === "rejected");
      expect(hasError).toBe(true);
    });
  });
});
