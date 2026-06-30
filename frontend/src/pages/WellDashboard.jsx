import { Filter, MapPin, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  fetchActualWellStatuses,
  fetchCurrentOperators,
  fetchAllWells,
  fetchProductionInjectionFormations,
  fetchWellStatuses,
  fetchWellTypes,
} from "../api/client.js";

import WellMap from "../components/WellMap.jsx";
import MultiSelectDropdown, { selectedLabel } from "../components/MultiSelectDropdown.jsx";

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


export default function WellDashboard() {
  const [wells, setWells] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [actualStatuses, setActualStatuses] = useState([]);
  const [types, setTypes] = useState([]);
  const [operators, setOperators] = useState([]);
  const [formations, setFormations] = useState([]);
  const [filters, setFilters] = useState({
    search: "",
    status: [],
    actual_status: [],
    well_type: [],
    cur_operator_name: [],
    prod_inject_frmtn: [],
  });
  const [topN, setTopN] = useState(25);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [totalCount, setTotalCount] = useState(0);
  const [operatorSearch, setOperatorSearch] = useState("");
  const [formationSearch, setFormationSearch] = useState("");

  useEffect(() => {
    Promise.all([
      fetchWellStatuses(),
      fetchWellTypes(),
      fetchCurrentOperators(),
      fetchProductionInjectionFormations(),
    ])
      .then(([statusOptions, typeOptions, operatorOptions, formationOptions]) => {
        setStatuses(statusOptions);
        setTypes(typeOptions);
        setOperators(operatorOptions);
        const uniqueFormations = Array.from(
          new Map(formationOptions.map((formation) => [formation.value, formation])).values(),
        );
        setFormations(uniqueFormations);
      })
      .catch(() => setError("Unable to load filter options."));
  }, []);

  useEffect(() => {
    fetchActualWellStatuses(filters.status)
      .then((statusOptions) => {
        setActualStatuses(statusOptions);
        setFilters((current) => ({
          ...current,
          actual_status: current.actual_status.filter((value) => statusOptions.some((option) => option.value === value)),
        }));
      })
      .catch(() => setError("Unable to load detailed status options."));
  }, [filters.status]);

  useEffect(() => {
    let isCurrentRequest = true;
    setLoading(true);
    fetchAllWells(filters)
      .then((data) => {
        if (!isCurrentRequest) return;
        setWells(Array.isArray(data) ? data : data.results || []);
        setTotalCount(Array.isArray(data) ? data.length : data.count ?? data.results?.length ?? 0);
        setError("");
      })
      .catch(() => {
        if (isCurrentRequest) setError("Unable to load all wells from the API.");
      })
      .finally(() => {
        if (isCurrentRequest) setLoading(false);
      });

    return () => {
      isCurrentRequest = false;
    };
  }, [filters]);

  const metrics = useMemo(() => {
    const mapped = wells.filter((well) => well.latitude && well.longitude).length;
    const active = wells.filter((well) => well.status === "OPEN" || well.status === "Active").length;
    return { total: totalCount, mapped, active };
  }, [wells, totalCount]);

  const tableWells = useMemo(() => wells.slice(0, topN), [wells, topN]);
  const visibleOperators = useMemo(() => {
    const search = operatorSearch.trim().toLowerCase();
    if (!search) return operators;

    const matches = operators.filter((operator) => operator.label.toLowerCase().includes(search));
    const selected = operators.filter((operator) => filters.cur_operator_name.includes(operator.value));
    return Array.from(new Map([...selected, ...matches].map((operator) => [operator.value, operator])).values());
  }, [operators, operatorSearch, filters.cur_operator_name]);
  const visibleFormations = useMemo(() => {
    const search = formationSearch.trim().toLowerCase();
    if (!search) return formations;
    const matches = formations.filter((formation) => formation.label.toLowerCase().includes(search));
    const selected = formations.filter((formation) => filters.prod_inject_frmtn.includes(formation.value));
    return Array.from(new Map([...selected, ...matches].map((formation) => [formation.value, formation])).values());
  }, [formations, formationSearch, filters.prod_inject_frmtn]);

  function updateFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  function toggleArrayFilter(key, value) {
    setFilters((current) => {
      const currentValues = current[key] || [];
      const selected = currentValues.includes(value)
        ? currentValues.filter((item) => item !== value)
        : [...currentValues, value];
      return { ...current, [key]: selected };
    });
  }

  function clearArrayFilter(key) {
    setFilters((current) => ({ ...current, [key]: [] }));
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Saguaro Petroleum</p>
          <h1>Well Production</h1>
        </div>

        <label className="field">
          <span>Search UWI or name</span>
          <div className="input-with-icon">
            <Search size={16} />
            <input
              value={filters.search}
              onChange={(event) => updateFilter("search", event.target.value)}
              placeholder="100-06-10..."
            />
          </div>
        </label>

        <MultiSelectDropdown
          title="Well status"
          options={statuses}
          selected={filters.status}
          onToggle={(value) => toggleArrayFilter("status", value)}
          onClear={() => clearArrayFilter("status")}
        />

        <MultiSelectDropdown
          title="Status detail"
          options={actualStatuses}
          selected={filters.actual_status}
          onToggle={(value) => toggleArrayFilter("actual_status", value)}
          onClear={() => clearArrayFilter("actual_status")}
        />

        <MultiSelectDropdown
          title="Well type"
          options={types}
          selected={filters.well_type}
          onToggle={(value) => toggleArrayFilter("well_type", value)}
          onClear={() => clearArrayFilter("well_type")}
        />

        <div className="field">
          <span>Current operator ({selectedLabel(filters.cur_operator_name.length)})</span>
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
            onToggle={(value) => toggleArrayFilter("cur_operator_name", value)}
            onClear={() => clearArrayFilter("cur_operator_name")}
            emptyText="No matching operators"
          />
        </div>

        <div className="field">
          <span>Production/injection formation ({selectedLabel(filters.prod_inject_frmtn.length)})</span>
          <div className="input-with-icon">
            <Search size={16} />
            <input
              value={formationSearch}
              onChange={(event) => setFormationSearch(event.target.value)}
              placeholder="Search formations..."
            />
          </div>
          <MultiSelectDropdown
            title="Formations"
            options={visibleFormations}
            selected={filters.prod_inject_frmtn}
            onToggle={(value) => toggleArrayFilter("prod_inject_frmtn", value)}
            onClear={() => clearArrayFilter("prod_inject_frmtn")}
            emptyText="No matching formations"
          />
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
          <div><strong>{metrics.total}</strong><span>Total</span></div>
          <div><strong>{metrics.active}</strong><span>Open</span></div>
          <div><strong>{metrics.mapped}</strong><span>Mapped</span></div>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Django REST + PostGIS</p>
            <h2>Well Production Management</h2>
          </div>
          <div className="status-pill">
            <Filter size={16} />
            {loading ? "Loading" : `${totalCount.toLocaleString()} wells`}
          </div>
        </header>

        {error && <div className="notice">{error}</div>}

        <div className="map-panel">
          <WellMap wells={wells} loading={loading} />
        </div>

        <section className="table-section">
          <div className="section-title">
            <MapPin size={18} />
            <h3>Well Register: Top {Math.min(topN, wells.length)}</h3>
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
                    <td colSpan="9" className="empty">No wells match the current filters.</td>
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
