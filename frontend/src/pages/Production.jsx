import { Filter, MapPin, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  fetchCurrentOperators,
  fetchAllWells,
} from "../api/client.js";

import WellMap from "../components/WellMap.jsx";
import MultiSelectDropdown from "../components/MultiSelectDropdown.jsx";

function formatDepth(value) {
  if (value == null || value === "") return "-";
  const depth = Number(value);
  return Number.isFinite(depth) ? depth.toLocaleString() + " m" : "-";
}

function formatProduction(well) {
  const sample = (well.production_samples || []).find(
    (item) =>
      item.oil_m3 != null ||
      item.gas_e3m3 != null ||
      item.water_m3 != null
  );

  if (!sample) return "No production data";

  const values = [];

  if (sample.oil_m3 != null) {
    values.push("Oil " + Number(sample.oil_m3).toLocaleString() + " m3");
  }

  if (sample.gas_e3m3 != null) {
    values.push("Gas " + Number(sample.gas_e3m3).toLocaleString() + " e3m3");
  }

  if (sample.water_m3 != null) {
    values.push("Water " + Number(sample.water_m3).toLocaleString() + " m3");
  }

  return values.join(" | ");
}

export default function Production() {
  const [wells, setWells] = useState([]);
  const [operators, setOperators] = useState([]);
  const [filters, setFilters] = useState({
    cur_operator_name: [],
  });
  const [selectedUwis, setSelectedUwis] = useState([]);
  const [topN, setTopN] = useState(25);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [totalCount, setTotalCount] = useState(0);
  const [operatorSearch, setOperatorSearch] = useState("");
  const [wellSearch, setWellSearch] = useState("");

  // Load operator list only.
  useEffect(() => {
    fetchCurrentOperators()
      .then((operatorOptions) => {
        setOperators(operatorOptions);
        setError("");
      })
      .catch(() => setError("Unable to load operator options."));
  }, []);

  // Load wells only after operator selection changes.
  useEffect(() => {
    let isCurrentRequest = true;

    if (filters.cur_operator_name.length === 0) {
      setWells([]);
      setSelectedUwis([]);
      setTotalCount(0);
      setLoading(false);
      return undefined;
    }

    setLoading(true);
    fetchAllWells(filters)
      .then((data) => {
        if (!isCurrentRequest) return;

        const results = Array.isArray(data) ? data : data.results || [];
        setWells(results);
        setTotalCount(Array.isArray(data) ? data.length : data.count ?? results.length);
        setSelectedUwis([]); // reset well selection when operator changes
        setError("");
      })
      .catch(() => {
        if (isCurrentRequest) setError("Unable to load wells for the selected operator.");
      })
      .finally(() => {
        if (isCurrentRequest) setLoading(false);
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [filters]);

  const visibleOperators = useMemo(() => {
    const search = operatorSearch.trim().toLowerCase();
    if (!search) return operators;

    const matches = operators.filter((operator) =>
      operator.label.toLowerCase().includes(search),
    );
    const selected = operators.filter((operator) =>
      filters.cur_operator_name.includes(operator.value),
    );

    return Array.from(
      new Map([...selected, ...matches].map((operator) => [operator.value, operator])).values(),
    );
  }, [operators, operatorSearch, filters.cur_operator_name]);

  const visibleWellOptions = useMemo(() => {
    const search = wellSearch.trim().toLowerCase();

    return wells
      .filter((well) => {
        if (!search) return true;
        return [well.uwi, well.name, well.operator]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(search));
      })
      .map((well) => ({
        value: well.uwi,
        label: `${well.uwi}${well.name ? ` — ${well.name}` : ""}`,
      }));
  }, [wells, wellSearch]);

  const selectedWells = useMemo(() => {
    if (selectedUwis.length === 0) return wells;
    const selectedSet = new Set(selectedUwis);
    return wells.filter((well) => selectedSet.has(well.uwi));
  }, [wells, selectedUwis]);

  const tableWells = useMemo(() => selectedWells.slice(0, topN), [selectedWells, topN]);

  const metrics = useMemo(() => {
    const mapped = selectedWells.filter((well) => well.latitude && well.longitude).length;
    const active = selectedWells.filter((well) => well.status === "OPEN" || well.status === "Active").length;
    return {
      total: totalCount,
      shown: selectedWells.length,
      mapped,
      active,
    };
  }, [selectedWells, totalCount]);

  function toggleOperator(value) {
    setFilters((current) => {
      const currentValues = current.cur_operator_name || [];
      const selected = currentValues.includes(value)
        ? currentValues.filter((item) => item !== value)
        : [...currentValues, value];
      return { ...current, cur_operator_name: selected };
    });
  }

  function clearOperators() {
    setFilters((current) => ({ ...current, cur_operator_name: [] }));
  }

  function toggleWell(uwi) {
    setSelectedUwis((current) =>
      current.includes(uwi)
        ? current.filter((item) => item !== uwi)
        : [...current, uwi],
    );
  }

  function clearWells() {
    setSelectedUwis([]);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">SP Petroleum</p>
          <h1>Well Production</h1>
        </div>

        <label className="field">
          <span>Select operator</span>
          <div className="input-with-icon">
            <Search size={16} />
            <input
              value={operatorSearch}
              onChange={(event) => setOperatorSearch(event.target.value)}
              placeholder="Search operators..."
            />
          </div>
          <MultiSelectDropdown
            title="Operators"
            options={visibleOperators}
            selected={filters.cur_operator_name}
            onToggle={toggleOperator}
            onClear={clearOperators}
            emptyText="No matching operators"
          />
        </label>

        <div className="field">
          <div className="filter-title-row">
            <span>Select wells ({selectedUwis.length === 0 ? "all" : selectedUwis.length})</span>
            {selectedUwis.length > 0 && (
              <button type="button" className="link-button" onClick={clearWells}>
                Show all
              </button>
            )}
          </div>

          <div className="input-with-icon">
            <Search size={16} />
            <input
              value={wellSearch}
              onChange={(event) => setWellSearch(event.target.value)}
              placeholder="Search UWI or well name..."
              disabled={wells.length === 0}
            />
          </div>

          <div className="choice-list well-choice-list">
            {visibleWellOptions.map((well) => (
              <label key={well.value} className="choice-item">
                <input
                  type="checkbox"
                  checked={selectedUwis.includes(well.value)}
                  onChange={() => toggleWell(well.value)}
                />
                <span>{well.label}</span>
              </label>
            ))}

            {!loading && filters.cur_operator_name.length > 0 && visibleWellOptions.length === 0 && (
              <p className="empty small">No wells found for this operator.</p>
            )}

            {filters.cur_operator_name.length === 0 && (
              <p className="empty small">Select an operator to load wells.</p>
            )}
          </div>
        </div>

        <label className="field">
          <span>Table rows</span>
          <select value={topN} onChange={(event) => setTopN(Number(event.target.value))}>
            <option value={10}>Top 10</option>
            <option value={25}>Top 25</option>
            <option value={50}>Top 50</option>
            <option value={100}>Top 100</option>
          </select>
        </label>

        <div className="stat-grid">
          <div><strong>{metrics.total}</strong><span>Loaded</span></div>
          <div><strong>{metrics.shown}</strong><span>Shown</span></div>
          <div><strong>{metrics.mapped}</strong><span>Mapped</span></div>
          <div><strong>{metrics.active}</strong><span>Open</span></div>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Django REST + PostGIS</p>
            <h2>Operator Well Map</h2>
          </div>
          <div className="status-pill">
            <Filter size={16} />
            {loading ? "Loading" : `${selectedWells.length.toLocaleString()} wells shown`}
          </div>
        </header>

        {error && <div className="notice">{error}</div>}

        <div className="map-panel">
          <WellMap wells={selectedWells} loading={loading} />
        </div>

        <section className="table-section">
          <div className="section-title">
            <MapPin size={18} />
            <h3>Selected Well Register: Top {Math.min(topN, selectedWells.length)}</h3>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>UWI</th>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Status Detail</th>
                  <th>Type</th>
                  <th>Operator</th>
                  <th>Total Depth</th>
                  <th>Production Summary</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                {tableWells.map((well) => (
                  <tr key={well.uwi}>
                    <td>{well.uwi}</td>
                    <td>{well.name}</td>
                    <td><span className={`tag ${well.status}`}>{well.status}</span></td>
                    <td>{well.actual_status_text || "-"}</td>
                    <td>{well.well_type}</td>
                    <td>{well.operator || "-"}</td>
                    <td>{formatDepth(well.measured_depth_m)}</td>
                    <td>{formatProduction(well)}</td>
                    <td>{well.latitude && well.longitude ? `${well.latitude}, ${well.longitude}` : "-"}</td>
                  </tr>
                ))}
                {!loading && tableWells.length === 0 && (
                  <tr>
                    <td colSpan="9" className="empty">
                      Select an operator and wells to display the map and table.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </section>
    </main>
  );
}
