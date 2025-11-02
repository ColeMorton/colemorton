import React from "react";
import FundamentalChart from "../charts/FundamentalCharts";
import type { FundamentalAnalysisData } from "@/types/ChartTypes";

interface FundamentalAnalysisDashboardProps {
  data: FundamentalAnalysisData;
  ticker: string;
  exportMode?: boolean;
  className?: string;
}

const FundamentalAnalysisDashboard: React.FC<
  FundamentalAnalysisDashboardProps
> = ({ data, ticker, exportMode = false, className = "" }) => {
  console.log("FundamentalAnalysisDashboard rendering:", {
    ticker,
    data: !!data,
    exportMode,
  });

  return (
    <div className={`fundamental-dashboard ${className}`} data-ticker={ticker}>
      {/* Header Section with Company Info and Key Metrics */}
      <div className="fundamental-header">
        <div className="company-info">
          <h1
            className="company-name"
            style={{ color: data.company.brandColor }}
          >
            {data.company.name}
          </h1>
        </div>

        <div className="key-metrics-row">
          <FundamentalChart chartType="fundamental-key-metrics" data={data} />
        </div>
      </div>

      {/* Main Content Grid - 3x3 Layout */}
      <div className="fundamental-dashboard-grid">
        {/* Row 1 */}
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-revenue-fcf"
            data={data}
            title="Revenue & FCF"
          />
        </div>
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-revenue-source"
            data={data}
            title="Revenue source"
          />
        </div>
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-geography"
            data={data}
            title="Geography"
          />
        </div>

        {/* Row 2 */}
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-key-metrics-expanded"
            data={data}
            title="Key metrics"
          />
        </div>
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-quality-rating"
            data={data}
            title="Quality"
          />
        </div>
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-financial-health"
            data={data}
            title="Financials"
          />
        </div>

        {/* Row 3 */}
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-pros-cons"
            data={data}
            title="Pros & Cons"
          />
        </div>
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-valuation-a"
            data={data}
            title="Valuation A"
          />
        </div>
        <div className="fundamental-chart-cell">
          <FundamentalChart
            chartType="fundamental-valuation-b"
            data={data}
            title="Valuation B"
          />
        </div>
      </div>

      {/* Footer */}
      <div className="fundamental-footer">
        <div className="footer-content">
          <div className="footer-section">
            <span className="footer-logo">⚡ Investing Visuals</span>
          </div>
          <div className="footer-section">
            <span className="footer-center">@INVESTINGVISUALS</span>
          </div>
          <div className="footer-section">
            <span className="footer-disclaimer">Not financial advice</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FundamentalAnalysisDashboard;
