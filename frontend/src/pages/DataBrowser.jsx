import { ChevronLeft, ChevronRight, Columns3, Database, Search, TableProperties, Trash2, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { deleteDataBrowserTable, fetchDataBrowserDatabases, fetchDataBrowserRows } from "../api/client.js";

export default function DataBrowser() {
  const [catalog, setCatalog] = useState([]);
  const [database, setDatabase] = useState("");
  const [table, setTable] = useState("");
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [search, setSearch] = useState("");
  const [submittedSearch, setSubmittedSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(100);
  const [rows, setRows] = useState([]);
  const [resultColumns, setResultColumns] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [loadingRows, setLoadingRows] = useState(false);
  const [error, setError] = useState("");
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState("");
  const [deletingTable, setDeletingTable] = useState(false);

  useEffect(() => {
    fetchDataBrowserDatabases()
      .then((data) => {
        const databases = data.databases || [];
        setCatalog(databases);
        const preferred = databases.find((item) => item.name === data.current_database) || databases[0];
        if (preferred) {
          setDatabase(preferred.name);
          setTable(preferred.tables?.[0]?.name || "");
        }
        setError("");
      })
      .catch((exc) => setError(exc.message || "Unable to load backend data catalog."))
      .finally(() => setLoadingCatalog(false));
  }, []);

  const activeDatabase = useMemo(
    () => catalog.find((item) => item.name === database),
    [catalog, database],
  );

  const tables = activeDatabase?.tables || [];
  const activeTable = useMemo(
    () => tables.find((item) => item.name === table),
    [tables, table],
  );
  const columns = activeTable?.columns || [];
  const canDeleteTable = table.startsWith("raw_excel_batch_") || table.startsWith("unique_raw_excel_batch_");

  useEffect(() => {
    if (!activeTable) {
      setSelectedColumns([]);
      return;
    }
    setSelectedColumns(activeTable.columns.slice(0, 24).map((column) => column.name));
    setPage(1);
    setSubmittedSearch("");
    setSearch("");
  }, [activeTable]);

  useEffect(() => {
    if (!database || !table || selectedColumns.length === 0) {
      setRows([]);
      setResultColumns([]);
      setTotalCount(0);
      return;
    }
    setLoadingRows(true);
    fetchDataBrowserRows({ database, table, columns: selectedColumns, search: submittedSearch, page, pageSize })
      .then((data) => {
        setRows(data.results || []);
        setResultColumns(data.columns || []);
        setTotalCount(data.count || 0);
        setError("");
      })
      .catch((exc) => setError(exc.message || "Unable to query selected table."))
      .finally(() => setLoadingRows(false));
  }, [database, table, selectedColumns, submittedSearch, page, pageSize]);

  function chooseDatabase(value) {
    const nextDatabase = catalog.find((item) => item.name === value);
    setDatabase(value);
    setTable(nextDatabase?.tables?.[0]?.name || "");
  }

  function toggleColumn(columnName) {
    setSelectedColumns((current) => {
      if (current.includes(columnName)) {
        return current.length === 1 ? current : current.filter((column) => column !== columnName);
      }
      return [...current, columnName];
    });
    setPage(1);
  }

  function submitSearch(event) {
    event.preventDefault();
    setPage(1);
    setSubmittedSearch(search.trim());
  }

  async function confirmDeleteTable() {
    if (!database || !table || deleteConfirmation !== table) return;
    setDeletingTable(true);
    setError("");
    try {
      await deleteDataBrowserTable(database, table, deleteConfirmation);
      const remainingTables = tables.filter((item) => item.name !== table);
      setCatalog((current) => current.map((item) => (
        item.name === database ? { ...item, tables: remainingTables } : item
      )));
      setTable(remainingTables[0]?.name || "");
      setShowDeleteDialog(false);
      setDeleteConfirmation("");
    } catch (exc) {
      setError(exc.message || "Unable to delete the selected table.");
    } finally {
      setDeletingTable(false);
    }
  }
  const firstRow = totalCount === 0 ? 0 : (page - 1) * pageSize + 1;
  const lastRow = Math.min(page * pageSize, totalCount);

  return (
    <main className="data-browser-page">
      <aside className="data-browser-sidebar">
        <div>
          <p className="eyebrow">Backend data</p>
          <h1>Data Browser</h1>
        </div>

        <label className="field">
          <span>Database</span>
          <select value={database} onChange={(event) => chooseDatabase(event.target.value)} disabled={loadingCatalog}>
            {catalog.map((item) => (
              <option key={item.name} value={item.name}>{item.name}</option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Table</span>
          <select value={table} onChange={(event) => setTable(event.target.value)} disabled={!tables.length}>
            {tables.map((item) => (
              <option key={item.name} value={item.name}>{item.name}</option>
            ))}
          </select>
        </label>

        <form className="field" onSubmit={submitSearch}>
          <span>Search values</span>
          <div className="input-with-icon">
            <Search size={16} />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Find any value..." />
          </div>
          <button className="primary-command" type="submit"><Search size={16} />Query table</button>
        </form>

        <label className="field">
          <span>Rows per page</span>
          <select value={pageSize} onChange={(event) => { setPageSize(Number(event.target.value)); setPage(1); }}>
            <option value={25}>25 rows</option>
            <option value={50}>50 rows</option>
            <option value={100}>100 rows</option>
            <option value={250}>250 rows</option>
            <option value={500}>500 rows</option>
          </select>
        </label>

        <div className="browser-stat-grid">
          <div><strong>{tables.length}</strong><span>Tables</span></div>
          <div><strong>{columns.length}</strong><span>Columns</span></div>
          <div><strong>{totalCount.toLocaleString()}</strong><span>Rows</span></div>
        </div>
      </aside>

      <section className="data-browser-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Read-only table query</p>
            <h2>{table || "Select a table"}</h2>
          </div>
          <div className="status-pill">
            <Database size={16} />
            {loadingRows ? "Loading" : `${firstRow.toLocaleString()}-${lastRow.toLocaleString()} of ${totalCount.toLocaleString()}`}
          </div>
          <button
            className="danger-icon-button"
            type="button"
            title={canDeleteTable ? "Delete selected table" : "Only raw import tables can be deleted"}
            aria-label="Delete selected table"
            disabled={!table}
            onClick={() => { setDeleteConfirmation(""); setShowDeleteDialog(true); }}
          >
            <Trash2 size={17} />
          </button>
        </header>

        {error && <div className="notice">{error}</div>}

        <section className="column-browser">
          <div className="section-title">
            <Columns3 size={18} />
            <h3>Columns with values</h3>
          </div>
          <div className="column-chip-list">
            {columns.map((column) => (
              <button
                type="button"
                key={column.name}
                className={`column-chip ${selectedColumns.includes(column.name) ? "selected" : ""}`}
                onClick={() => toggleColumn(column.name)}
                title={`${column.name} (${column.type})`}
              >
                <strong>{column.name}</strong>
                <small>{column.type}</small>
              </button>
            ))}
          </div>
        </section>

        <section className="data-table-section">
          <div className="section-title table-control-title">
            <span><TableProperties size={18} /><h3>Data table</h3></span>
            <div className="pager-controls">
              <button className="secondary-command" type="button" onClick={() => setPage((current) => Math.max(current - 1, 1))} disabled={page <= 1 || loadingRows}>
                <ChevronLeft size={16} />Previous
              </button>
              <span>Page {page}</span>
              <button className="secondary-command" type="button" onClick={() => setPage((current) => current + 1)} disabled={lastRow >= totalCount || loadingRows}>
                Next<ChevronRight size={16} />
              </button>
            </div>
          </div>

          <div className="browser-table-wrap">
            <table>
              <thead>
                <tr>
                  {resultColumns.map((column) => (
                    <th key={column.name}>{column.name}<small>{column.type}</small></th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, rowIndex) => (
                  <tr key={`${page}-${rowIndex}`}>
                    {resultColumns.map((column) => (
                      <td key={column.name} title={row[column.name] ?? ""}>{row[column.name] || "-"}</td>
                    ))}
                  </tr>
                ))}
                {!loadingRows && rows.length === 0 && (
                  <tr><td className="empty" colSpan={Math.max(resultColumns.length, 1)}>No rows match the current query.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </section>
      {showDeleteDialog && (
        <div className="dialog-backdrop" role="presentation" onMouseDown={() => !deletingTable && setShowDeleteDialog(false)}>
          <section className="confirmation-dialog" role="dialog" aria-modal="true" aria-labelledby="delete-table-title" onMouseDown={(event) => event.stopPropagation()}>
            <header>
              <div><h2 id="delete-table-title">Delete table</h2><p>This permanently removes the table and all of its data.</p></div>
              <button className="icon-button" type="button" title="Close" aria-label="Close" disabled={deletingTable} onClick={() => setShowDeleteDialog(false)}><X size={18} /></button>
            </header>
            <dl>
              <div><dt>Database</dt><dd>{database}</dd></div>
              <div><dt>Table</dt><dd>{table}</dd></div>
            </dl>
            <label className="field">
              <span>Enter <strong>{table}</strong> to confirm</span>
              <input autoFocus value={deleteConfirmation} onChange={(event) => setDeleteConfirmation(event.target.value)} />
            </label>
            <footer>
              <button className="secondary-command" type="button" disabled={deletingTable} onClick={() => setShowDeleteDialog(false)}>Cancel</button>
              <button className="danger-command" type="button" disabled={deletingTable || deleteConfirmation !== table} onClick={confirmDeleteTable}>
                <Trash2 size={16} />{deletingTable ? "Deleting..." : "Delete table"}
              </button>
            </footer>
          </section>
        </div>
      )}    </main>
  );
}
