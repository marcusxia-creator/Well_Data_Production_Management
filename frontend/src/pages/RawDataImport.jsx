import { ArrowLeft, ArrowRight, Check, Database, FileSpreadsheet, Save, Search, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { applyMappingTemplate, createRawImportTable, executeImportSplit, fetchMappedPreview, fetchMappingTemplates, saveImportMappings, saveMappingTemplate, uploadRawWorkbook } from "../api/client.js";

function targetColumnLabel(mapping) {
  return mapping.target_column === "md_all_wells_m" ? "measured_depth_m" : mapping.target_column;
}

export default function RawDataImport({ onDone }) {
  const [file, setFile] = useState(null);
  const [batch, setBatch] = useState(null);
  const [step, setStep] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [creatingRawTable, setCreatingRawTable] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState("");
  const [targetFilter, setTargetFilter] = useState("all");
  const [mappingSearch, setMappingSearch] = useState("");
  const [replaceExisting, setReplaceExisting] = useState(true);
  const [summary, setSummary] = useState(null);
  const [mappedPreview, setMappedPreview] = useState(null);
  const [previewTableName, setPreviewTableName] = useState("");
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [mappingTemplates, setMappingTemplates] = useState([]);
  const [templateName, setTemplateName] = useState("");
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [templateBusy, setTemplateBusy] = useState(false);
  const [templateMessage, setTemplateMessage] = useState("");

  useEffect(() => {
    let active = true;
    fetchMappingTemplates()
      .then((templates) => {
        if (active) setMappingTemplates(templates);
      })
      .catch(() => {
        if (active) setMappingTemplates([]);
      });
    return () => {
      active = false;
    };
  }, []);
  const targetTables = useMemo(() => {
    if (!batch) return [];
    return Array.from(new Set((batch.mappings || []).map((mapping) => mapping.target_table)));
  }, [batch]);

  const visibleMappings = useMemo(() => {
    if (!batch) return [];
    const search = mappingSearch.trim().toLowerCase();
    return (batch.mappings || []).filter((mapping) => {
      const matchesTable = targetFilter === "all" || mapping.target_table === targetFilter;
      const searchable = `${mapping.target_table} ${targetColumnLabel(mapping)} ${mapping.target_column} ${mapping.source_column} ${mapping.notes}`.toLowerCase();
      return matchesTable && (!search || searchable.includes(search));
    });
  }, [batch, targetFilter, mappingSearch]);

  const importMetrics = useMemo(() => {
    if (!summary) return null;
    const counts = Object.values(summary).map(Number);
    return {
      dataPoints: counts.reduce((total, count) => total + count, 0),
      populatedTables: counts.filter((count) => count > 0).length,
    };
  }, [summary]);

  const mappingMetrics = useMemo(() => {
    if (!batch) return { mapped: 0, included: 0, unresolvedRequired: 0 };
    const included = (batch.mappings || []).filter((mapping) => mapping.include);
    return {
      included: included.length,
      mapped: included.filter((mapping) => mapping.source_column || mapping.default_value).length,
      unresolvedRequired: included.filter(
        (mapping) => mapping.required && !mapping.source_column && !mapping.default_value
          && !["raw_id", "source_file", "import_timestamp"].includes(mapping.target_column),
      ).length,
    };
  }, [batch]);

  async function handleUpload(event) {
    event.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");
    setSummary(null);
    try {
      const uploaded = await uploadRawWorkbook(file);
      setBatch(uploaded);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleNext() {
    if (!batch) return;
    setCreatingRawTable(true);
    setError("");
    try {
      const materialized = await createRawImportTable(batch.id);
      setBatch(materialized);
      setStep(2);
    } catch (tableError) {
      setError(tableError.message);
    } finally {
      setCreatingRawTable(false);
    }
  }
  function updateMapping(id, changes) {
    setBatch((current) => ({
      ...current,
      mappings: current.mappings.map((mapping) => (mapping.id === id ? { ...mapping, ...changes } : mapping)),
    }));
  }

  function mappingPayload() {
    return batch.mappings.map(({ id, source_column, include, default_value }) => ({
      id, source_column, include, default_value,
    }));
  }

  async function handleSaveTemplate() {
    if (!batch || !templateName.trim()) return;
    setTemplateBusy(true);
    setError("");
    setTemplateMessage("");
    try {
      const savedBatch = await saveImportMappings(batch.id, mappingPayload());
      setBatch(savedBatch);
      const template = await saveMappingTemplate(savedBatch.id, templateName.trim());
      const templates = await fetchMappingTemplates();
      setMappingTemplates(templates);
      setSelectedTemplateId(String(template.id));
      setTemplateMessage(`Saved template "${template.name}".`);
    } catch (templateError) {
      setError(templateError.message);
    } finally {
      setTemplateBusy(false);
    }
  }

  async function handleApplyTemplate() {
    if (!batch || !selectedTemplateId) return;
    setTemplateBusy(true);
    setError("");
    setTemplateMessage("");
    try {
      const result = await applyMappingTemplate(batch.id, Number(selectedTemplateId));
      setBatch(result.batch);
      const missingCount = result.summary.missing_source_columns.length;
      setTemplateMessage(
        missingCount
          ? `Applied ${result.summary.template.name}. ${missingCount} saved source column${missingCount === 1 ? "" : "s"} were not found in this file.`
          : `Applied ${result.summary.template.name}.`,
      );
    } catch (templateError) {
      setError(templateError.message);
    } finally {
      setTemplateBusy(false);
    }
  }
  async function handleMappingNext() {
    setLoadingPreview(true);
    setError("");
    setSummary(null);
    try {
      const saved = await saveImportMappings(
        batch.id,
        mappingPayload(),
      );
      setBatch(saved);
      const preview = await fetchMappedPreview(saved.id);
      setMappedPreview(preview);
      const firstPopulated = preview.tables.find((table) => table.rows.length > 0) || preview.tables[0];
      setPreviewTableName(firstPopulated?.table_name || "");
      setStep(3);
    } catch (previewError) {
      setError(previewError.message);
    } finally {
      setLoadingPreview(false);
    }
  }
  async function handleComplete() {
    setExecuting(true);
    setError("");
    setSummary(null);
    try {
      const result = await executeImportSplit(batch.id, replaceExisting);
      setBatch((current) => ({ ...current, ...result.batch, mappings: current?.mappings || [] }));
      setSummary(result.summary || {});
      setStep(4);
    } catch (processError) {
      setError(processError.message);
    } finally {
      setExecuting(false);
    }
  }

  return (
    <main className="import-page">
      <header className="import-header">
        <div>
          <p className="eyebrow">Data Management Module</p>
          <h1>Raw Data Import & Mapping</h1>
          <p>Complete the Excel import first, then continue to the separate column-mapping page.</p>
        </div>
        <button className="secondary-command" onClick={onDone}><ArrowLeft size={17} /> Production Dashboard</button>
      </header>

      {importMetrics && (
        <section className="import-success-banner" aria-live="polite">
          <div className="success-banner-icon"><Check size={22} /></div>
          <div className="success-banner-message">
            <span>Import completed</span>
            <strong>{importMetrics.dataPoints.toLocaleString()} data points imported</strong>
          </div>
          <div className="success-banner-stat">
            <span>Raw rows</span>
            <strong>{batch.row_count.toLocaleString()}</strong>
          </div>
          <div className="success-banner-stat">
            <span>Target tables populated</span>
            <strong>{importMetrics.populatedTables}</strong>
          </div>
        </section>
      )}

      <ol className="stepper">
        <li className={step >= 1 ? "active" : ""}><span>1</span><div><strong>Raw Excel Import</strong><small>Clean headers and store raw rows</small></div></li>
        <li className={step >= 2 ? "active" : ""}><span>2</span><div><strong>Column Mapping</strong><small>Link cleaned source columns</small></div></li>
        <li className={step >= 3 ? "active" : ""}><span>3</span><div><strong>Mapped Data Review</strong><small>Review rows and complete</small></div></li>
        <li className={step >= 4 ? "active" : ""}><span>4</span><div><strong>Complete</strong><small>Return to dashboard</small></div></li>
      </ol>

      {error && <div className="notice">{error}</div>}

      {step === 1 && (
        <section className="sequential-page">
          <section className="import-workspace upload-workspace">
            <div className="upload-panel">
              <FileSpreadsheet size={34} />
              <h2>Step 1: Import raw Excel data</h2>
              <p>Column names are cleaned to lowercase snake_case before the rows are stored.</p>
              <form onSubmit={handleUpload}>
                <label className="file-picker">
                  <Upload size={18} />
                  <span>{file ? file.name : "Select .xlsx or .xlsm workbook"}</span>
                  <input type="file" accept=".xlsx,.xlsm" onChange={(event) => setFile(event.target.files?.[0] || null)} />
                </label>
                <button className="primary-command" disabled={!file || uploading}>
                  {uploading ? "Importing raw rows..." : batch ? "Import another workbook" : "Import workbook"}
                  <Upload size={17} />
                </button>
              </form>
            </div>
            <aside className="import-notes">
              <Database size={22} />
              <h3>Raw database storage</h3>
              <p>Every non-empty Excel row is saved in <code>raw_import_row</code> before mapping.</p>
              <p>Cleaned headings become the JSON keys used on the next page.</p>
            </aside>
          </section>

          {batch && (
            <div className="step-one-results">
              <div className="batch-summary">
                <div><span>Workbook</span><strong>{batch.file_name}</strong></div>
                <div><span>Worksheet</span><strong>{batch.sheet_name}</strong></div>
                <div><span>Raw rows</span><strong>{batch.row_count.toLocaleString()}</strong></div>
                <div><span>Cleaned columns</span><strong>{batch.headers.length}</strong></div>
              </div>

              <section className="cleaned-header-section">
                <div className="section-heading"><div><h2>Cleaned column names</h2><p>These names will be available for manual mapping.</p></div></div>
                <div className="header-chip-list">
                  {batch.headers.map((header, index) => <span key={header}><small>{index + 1}</small>{header}</span>)}
                </div>
              </section>

              <section className="raw-preview-section">
                <div className="section-heading"><div><h2>Raw data table preview</h2><p>First {batch.preview.length} stored rows</p></div></div>
                <div className="raw-preview-wrap">
                  <table>
                    <thead><tr><th>Excel row</th>{batch.headers.map((header) => <th key={header}>{header}</th>)}</tr></thead>
                    <tbody>{batch.preview.map((row) => (
                      <tr key={row.row_number}><td>{row.row_number}</td>{batch.headers.map((header) => <td key={header}>{String(row.data[header] ?? "")}</td>)}</tr>
                    ))}</tbody>
                  </table>
                </div>
              </section>
            </div>
          )}

          <footer className="sequential-page-actions">
            <span>{batch ? "Raw data import completed. Continue to map the cleaned columns." : "Import a workbook to enable the next step."}</span>
            <button className="primary-command" disabled={!batch || uploading || creatingRawTable} onClick={handleNext}>
              {creatingRawTable ? "Creating raw database table..." : "Next: Column Mapping"} <ArrowRight size={17} />
            </button>
          </footer>
        </section>
      )}


      {step === 2 && batch && (
        <section className="sequential-page mapping-workspace">
          <div className="batch-summary">
            <div><span>Workbook</span><strong>{batch.file_name}</strong></div>
            <div><span>Worksheet</span><strong>{batch.sheet_name}</strong></div>
            <div><span>Raw rows</span><strong>{batch.row_count.toLocaleString()}</strong></div>
            <div><span>Source columns</span><strong>{batch.headers.length}</strong></div>
            <div><span>Raw database table</span><strong>{batch.raw_table_name || "Not created"}</strong></div>
          </div>

          <section className="mapping-section">
            <div className="mapping-toolbar">
              <div><h2>Step 2: Raw data table column mapping</h2><p>{mappingMetrics.mapped} of {mappingMetrics.included} included targets linked</p></div>
              <div className="mapping-metrics"><span className={mappingMetrics.unresolvedRequired ? "warning-count" : "ok-count"}>{mappingMetrics.unresolvedRequired} required unresolved</span></div>
            </div>
            <div className="mapping-filters">
              <div className="light-input"><Search size={16} /><input value={mappingSearch} onChange={(event) => setMappingSearch(event.target.value)} placeholder="Search target or source columns" /></div>
              <select value={targetFilter} onChange={(event) => setTargetFilter(event.target.value)}><option value="all">All target tables</option>{targetTables.map((table) => <option key={table} value={table}>{table}</option>)}</select>
            </div>
            <div className="mapping-template-tools">
              <div className="template-save-row">
                <input value={templateName} onChange={(event) => setTemplateName(event.target.value)} placeholder="Template name for this file format" />
                <button className="secondary-command" type="button" disabled={templateBusy || !templateName.trim()} onClick={handleSaveTemplate}><Save size={16} /> Save Mapping Template</button>
              </div>
              <div className="template-apply-row">
                <select value={selectedTemplateId} onChange={(event) => setSelectedTemplateId(event.target.value)}>
                  <option value="">Select saved mapping template</option>
                  {mappingTemplates.map((template) => <option key={template.id} value={template.id}>{template.name} ({template.column_count} columns)</option>)}
                </select>
                <button className="secondary-command" type="button" disabled={templateBusy || !selectedTemplateId} onClick={handleApplyTemplate}>Apply Template</button>
              </div>
              {templateMessage && <p className="template-message">{templateMessage}</p>}
            </div>
            <div className="mapping-table-wrap">
              <table className="mapping-table">
                <thead><tr><th>Use</th><th>Target table</th><th>Target column</th><th>Cleaned source column</th><th>Type</th><th>Rule</th></tr></thead>
                <tbody>{visibleMappings.map((mapping) => (
                  <tr key={mapping.id} className={!mapping.source_column && mapping.required && mapping.include ? "mapping-required" : ""}>
                    <td><input type="checkbox" checked={mapping.include} onChange={(event) => updateMapping(mapping.id, { include: event.target.checked })} /></td>
                    <td><strong>{mapping.target_table}</strong>{mapping.casing_type && <small>{mapping.casing_type}</small>}</td>
                    <td>{targetColumnLabel(mapping)}{mapping.target_column === "md_all_wells_m" && <small>Stored as md_all_wells_m</small>}{mapping.required && <span className="required-mark">Required</span>}</td>
                    <td><select disabled={!mapping.include} value={mapping.source_column} onChange={(event) => updateMapping(mapping.id, { source_column: event.target.value })}><option value="">Not mapped</option>{batch.headers.map((header) => <option key={header} value={header}>{header}</option>)}</select>{mapping.suggested_source_column && <small>Suggested: {mapping.suggested_source_column}</small>}</td>
                    <td>{mapping.target_type}</td><td title={mapping.transform_rule}>{mapping.transform_rule || "copy"}</td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          </section>

          {summary && (
            <section className="process-result">
              <div className="completion-icon"><Check size={24} /></div>
              <div><h2>Process completed</h2><p>Mapped raw values were written to the target tables.</p></div>
              <div className="result-grid">{Object.entries(summary).map(([table, count]) => <div key={table}><span>{table}</span><strong>{Number(count || 0).toLocaleString()} rows</strong></div>)}</div>
            </section>
          )}

          <footer className="sequential-page-actions">
            <button className="secondary-command" disabled={loadingPreview} onClick={() => { setError(""); setStep(1); }}><ArrowLeft size={17} /> Back to Raw Import</button>
            <button className="primary-command" disabled={loadingPreview || mappingMetrics.unresolvedRequired > 0} onClick={handleMappingNext}>
              {loadingPreview ? "Generating mapped preview..." : "Next: Review Mapped Data"}<ArrowRight size={17} />
            </button>
          </footer>
        </section>
      )}

      {step === 3 && mappedPreview && (
        <section className="sequential-page mapped-review-workspace">
          <section className="mapped-review-section">
            <div className="mapping-toolbar">
              <div><h2>Step 3: Review mapped data</h2><p>Select a target table and review its mapped headers and first 20 rows.</p></div>
              <select value={previewTableName} onChange={(event) => setPreviewTableName(event.target.value)}>
                {mappedPreview.tables.map((table) => (
                  <option key={table.table_name} value={table.table_name}>{table.table_name} ({table.rows.length} preview rows)</option>
                ))}
              </select>
            </div>
            {mappedPreview.tables.filter((table) => table.table_name === previewTableName).map((table) => (
              <div key={table.table_name}>
                <div className="mapped-header-list">
                  {table.headers.map((header, index) => <span key={header}><small>{index + 1}</small>{header}</span>)}
                </div>
                <div className="mapped-preview-wrap">
                  <table>
                    <thead><tr>{table.headers.map((header) => <th key={header}>{header}</th>)}</tr></thead>
                    <tbody>
                      {table.rows.map((row, rowIndex) => <tr key={rowIndex}>{table.headers.map((header) => <td key={header}>{String(row[header] ?? "")}</td>)}</tr>)}
                      {table.rows.length === 0 && <tr><td colSpan={table.headers.length || 1} className="empty">No mapped rows for this target table.</td></tr>}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </section>

          {summary && (
            <section className="process-result">
              <div className="completion-icon"><Check size={24} /></div>
              <div><h2>Process completed</h2><p>Mapped data was written to the target tables.</p></div>
              <div className="result-grid">{Object.entries(summary).map(([table, count]) => <div key={table}><span>{table}</span><strong>{Number(count || 0).toLocaleString()} rows</strong></div>)}</div>
            </section>
          )}

          <footer className="sequential-page-actions mapping-complete-actions">
            <button className="secondary-command" disabled={executing} onClick={() => { setError(""); setSummary(null); setStep(2); }}><ArrowLeft size={17} /> Back to Column Mapping</button>
            <label><input type="checkbox" checked={replaceExisting} onChange={(event) => setReplaceExisting(event.target.checked)} /> Replace existing target-table data</label>
            <button className="primary-command" disabled={executing} onClick={handleComplete}>
              {executing ? "Completing process..." : summary ? "Run Complete Process Again" : "Complete Process"}<Check size={17} />
            </button>
          </footer>
        </section>
      )}
      {step === 4 && summary && (
        <section className="sequential-page completion-workspace import-complete-page">
          <div className="completion-icon"><Check size={28} /></div>
          <h2>Import is complete</h2>
          <p>Mapped data was written to the target tables.</p>
          <div className="result-grid">
            {Object.entries(summary).map(([table, count]) => (
              <div key={table}><span>{table}</span><strong>{Number(count || 0).toLocaleString()} rows</strong></div>
            ))}
          </div>
          <button className="primary-command" type="button" onClick={onDone}>
            <ArrowLeft size={17} /> Go back to Dashboard
          </button>
        </section>
      )}    </main>
  );
}










