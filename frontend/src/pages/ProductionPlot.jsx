import { ArrowLeft, ChartNoAxesCombined } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import Plot from "react-plotly.js";

import { fetchWellProductionDaily } from "../api/client.js";

const COLORS = { oil: "#0a8062", water: "#2e7bcf", gas: "#c47a16" };

function formatNumber(value, maximumFractionDigits = 0) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "-";
  return number.toLocaleString(undefined, { maximumFractionDigits });
}

function parseRows(rows) {
  return (rows || []).map((row) => ({
    ...row,
    timestamp: new Date(row.date).getTime(),
    daily_oil: Number(row.daily_oil || 0),
    daily_water: Number(row.daily_water || 0),
    daily_gas: Number(row.daily_gas || 0),
  })).filter((row) => Number.isFinite(row.timestamp)).sort((a, b) => a.timestamp - b.timestamp);
}

function ProductionChart({ rows, chartMode }) {
  const mode = chartMode === "scatter" ? "markers" : "lines+markers";
  const markerSize = chartMode === "scatter" ? 7 : 4;
  const dates = rows.map((row) => row.date);
  const trace = (key, name, color, unit, yaxis) => ({
    x: dates, y: rows.map((row) => row[key]), type: "scatter", mode, name, yaxis,
    line: { color, width: 2 }, marker: { color, size: markerSize },
    hovertemplate: `%{y:,.2f} ${unit}<extra>${name}</extra>`,
  });

  return (
    <Plot
      className="production-plotly-chart"
      data={[
        trace("daily_oil", "Oil Production", COLORS.oil, "bbls"),
        trace("daily_water", "Water Production", COLORS.water, "bbls"),
        trace("daily_gas", "Gas Production", COLORS.gas, "MCF", "y2"),
      ]}
      layout={{
        autosize: true, margin: { l: 78, r: 82, t: 64, b: 72 },
        paper_bgcolor: "#ffffff", plot_bgcolor: "#ffffff",
        font: { family: "Inter, system-ui, sans-serif", color: "#263942", size: 12 },
        hovermode: "x unified", legend: { orientation: "h", x: 0, y: 1.15 },
        xaxis: {
          title: { text: "Date", standoff: 14 }, type: "date", showgrid: false,
          rangeslider: { visible: true, thickness: 0.08 },
          rangeselector: {
            buttons: [
              { count: 1, label: "1y", step: "year", stepmode: "backward" },
              { count: 5, label: "5y", step: "year", stepmode: "backward" },
              { step: "all", label: "All" },
            ], x: 0, y: 1.04,
          },
        },
        yaxis: {
          title: { text: "Oil / Water Production (bbls)", standoff: 10 },
          rangemode: "tozero", gridcolor: "#e4ece9", zerolinecolor: "#c7d5d0",
        },
        yaxis2: {
          title: { text: "Gas Production (MCF)", standoff: 10 },
          overlaying: "y", side: "right", rangemode: "tozero", showgrid: false, zeroline: false,
        },
      }}
      config={{
        responsive: true, displaylogo: false, scrollZoom: true,
        modeBarButtonsToRemove: ["lasso2d", "select2d"],
      }}
      useResizeHandler
      style={{ width: "100%", height: "100%" }}
    />
  );
}

export default function ProductionPlot({ wellId }) {
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [chartMode, setChartMode] = useState("lines");

  useEffect(() => {
    let active = true;
    setLoading(true);
    fetchWellProductionDaily(wellId)
      .then((data) => {
        if (!active) return;
        setPayload(data);
        setError("");
      })
      .catch((err) => {
        if (active) setError(err.message || "Unable to load production data.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [wellId]);

  const rows = useMemo(() => parseRows(payload?.rows), [payload]);
  const well = payload?.well || {};
  const totals = useMemo(() => rows.reduce((acc, row) => ({
    oil: acc.oil + row.daily_oil,
    water: acc.water + row.daily_water,
    gas: acc.gas + row.daily_gas,
  }), { oil: 0, water: 0, gas: 0 }), [rows]);

  return (
    <main className="production-plot-shell">
      <header className="production-plot-header">
        <button type="button" className="secondary-action" onClick={() => { window.location.hash = "production"; }}>
          <ArrowLeft size={16} /> Back to Production Modules
        </button>
        <div>
          <p className="eyebrow">Daily Production Plot</p>
          <h1 className="production-plot-well-title">
            <span>Well Name: {well.name || "-"}</span>
            <span>Base_UWI: {well.uwi || wellId}</span>
          </h1>
        </div>
        <div className="segmented-control" aria-label="Chart mode">
          <button type="button" className={chartMode === "lines" ? "selected" : ""} onClick={() => setChartMode("lines")}>Line</button>
          <button type="button" className={chartMode === "scatter" ? "selected" : ""} onClick={() => setChartMode("scatter")}>Scatter</button>
        </div>
      </header>

      {error && <div className="notice">{error}</div>}
      {loading && <div className="map-message"><span className="spinner" /><span>Loading production plot</span></div>}
      {!loading && !error && rows.length === 0 && (
        <div className="empty production-plot-empty">
          <ChartNoAxesCombined size={28} />
          <span>No daily production rows are available for this well.</span>
        </div>
      )}
      {!loading && !error && rows.length > 0 && (
        <>
          <section className="production-plot-stats">
            <div><span>Daily rows</span><strong>{rows.length.toLocaleString()}</strong></div>
            <div><span>Total oil</span><strong>{formatNumber(totals.oil)} bbls</strong></div>
            <div><span>Total water</span><strong>{formatNumber(totals.water)} bbls</strong></div>
            <div><span>Total gas</span><strong>{formatNumber(totals.gas)} MCF</strong></div>
          </section>
          <section className="production-plot-card">

            <ProductionChart rows={rows} chartMode={chartMode} />
          </section>
        </>
      )}
    </main>
  );
}

