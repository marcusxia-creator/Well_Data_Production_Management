import { ArrowLeft, ArrowRight, Check, Database, FileSpreadsheet, Save, Search, Upload } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { applyMappingTemplate, createRawImportTable, executeImportSplit, fetchMappedPreview, fetchMappingTemplates, inspectProductionData, previewProductionData, saveImportMappings, saveMappingTemplate, uploadProductionData, uploadRawWorkbook } from "../api/client.js";

function targetColumnLabel(mapping) {
  return mapping.target_column === "md_all_wells_m" ? "measured_depth_m" : mapping.target_column;
}


function productionFieldLabel(field) {
  return ({
    base_uwi: "base_uwi",
    production_date: "date",
    daily_oil: "oil",
    daily_water: "water",
    daily_gas: "gas",
    fluid: "fluid",
  })[field.target] || field.label || field.target;
}

function ProductionPreviewTable({ rows = [] }) {
  return (
    <div className="mapped-preview-wrap production-preview-wrap">
      <table>
        <thead><tr><th>base_uwi</th><th>date</th><th>oil</th><th>water</th><th>gas</th><th>fluid</th></tr></thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={`${row.base_uwi}-${row.production_date}-${index}`}><td>{row.base_uwi}</td><td>{row.production_date}</td><td>{row.daily_oil}</td><td>{row.daily_water}</td><td>{row.daily_gas}</td><td>{row.fluid}</td></tr>
          ))}
          {rows.length === 0 && <tr><td colSpan={6} className="empty">No mapped production rows to preview.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

function ProductionImportTab({
  productionFile,
  setProductionFile,
  productionStep,
  setProductionStep,
  productionInspect,
  setProductionInspect,
  productionMappings,
  setProductionMappings,
  productionPreview,
  setProductionPreview,
  productionSummary,
  setProductionSummary,
  productionReplaceExisting,
  setProductionReplaceExisting,
  productionBusy,
  handleProductionInspect,
  handleProductionPreview,
  handleProductionComplete,
}) {
  const requiredFields = (productionInspect?.fields || []).filter((field) => field.required);
  const unresolvedRequired = requiredFields.filter((field) => !productionMappings[field.target]).length;

  return (
    <>
      <ol className="stepper production-stepper">
        <li className={productionStep >= 1 ? "active" : ""}><span>1</span><div><strong>Daily File Import</strong><small>Read source headers</small></div></li>
        <li className={productionStep >= 2 ? "active" : ""}><span>2</span><div><strong>Column Mapping</strong><small>Map database fields</small></div></li>
        <li className={productionStep >= 3 ? "active" : ""}><span>3</span><div><strong>Mapped Data Review</strong><small>Review production rows</small></div></li>
        <li className={productionStep >= 4 ? "active" : ""}><span>4</span><div><strong>Complete</strong><small>Generate monthly data</small></div></li>
      </ol>

      {productionStep === 1 && (
        <section className="sequential-page">
          <section className="import-workspace upload-workspace">
            <div className="upload-panel">
              <FileSpreadsheet size={34} />
              <h2>Step 1: Import daily production file</h2>
              <p>CSV or Excel headings are inspected first so daily production database fields can be mapped before import.</p>
              <form onSubmit={handleProductionInspect}>
                <label className="file-picker">
                  <Upload size={18} />
                  <span>{productionFile ? productionFile.name : "Select .csv, .xlsx, or .xlsm production file"}</span>
                  <input type="file" accept=".csv,.xlsx,.xlsm" onChange={(event) => { setProductionFile(event.target.files?.[0] || null); setProductionInspect(null); setProductionPreview(null); setProductionSummary(null); }} />
                </label>
                <button className="primary-command" disabled={!productionFile || productionBusy}>{productionBusy ? "Inspecting file..." : "Inspect File"}<Upload size={17} /></button>
              </form>
            </div>
            <aside className="import-notes">
              <Database size={22} />
              <h3>Production storage</h3>
              <p>Daily rows are written to <code>production_daily</code>. Monthly totals and cumulative production are generated in <code>production_monthly</code>.</p>
            </aside>
          </section>
          {productionInspect && (
            <div className="step-one-results">
              <div className="batch-summary">
                <div><span>File</span><strong>{productionInspect.file_name}</strong></div>
                <div><span>Worksheet</span><strong>{productionInspect.sheet_name}</strong></div>
                <div><span>Rows</span><strong>{productionInspect.row_count.toLocaleString()}</strong></div>
                <div><span>Source columns</span><strong>{productionInspect.headers.length}</strong></div>
              </div>
              <section className="cleaned-header-section">
                <div className="section-heading"><div><h2>Source column names</h2><p>These names will be available for production field mapping.</p></div></div>
                <div className="header-chip-list">{productionInspect.headers.map((header, index) => <span key={`${header}-${index}`}><small>{index + 1}</small>{header || `column_${index + 1}`}</span>)}</div>
              </section>
            </div>
          )}
          <footer className="sequential-page-actions">
            <span>{productionInspect ? "File inspected. Continue to map production database fields." : "Inspect a production file to enable mapping."}</span>
            <button className="primary-command" disabled={!productionInspect || productionBusy} onClick={() => setProductionStep(2)}>Next: Column Mapping <ArrowRight size={17} /></button>
          </footer>
        </section>
      )}

      {productionStep === 2 && productionInspect && (
        <section className="sequential-page mapping-workspace">
          <div className="batch-summary">
            <div><span>File</span><strong>{productionInspect.file_name}</strong></div>
            <div><span>Target daily table</span><strong>production_daily</strong></div>
            <div><span>Required mapped</span><strong>{requiredFields.length - unresolvedRequired} / {requiredFields.length}</strong></div>
            <div><span>Monthly output</span><strong>production_monthly</strong></div>
          </div>
          <section className="mapping-section">
            <div className="mapping-toolbar">
              <div><h2>Step 2: Production column mapping</h2><p>Map source columns to daily production database fields.</p></div>
              <div className="mapping-metrics"><span className={unresolvedRequired ? "warning-count" : "ok-count"}>{unresolvedRequired} required unresolved</span></div>
            </div>
            <div className="mapping-table-wrap">
              <table className="mapping-table production-mapping-table">
                <thead><tr><th>Target table</th><th>Database field</th><th>Source column</th><th>Type</th><th>Rule</th></tr></thead>
                <tbody>{productionInspect.fields.map((field) => (
                  <tr key={field.target} className={field.required && !productionMappings[field.target] ? "mapping-required" : ""}>
                    <td><strong>production_daily</strong></td>
                    <td>{productionFieldLabel(field)}{field.target !== productionFieldLabel(field) && <small>Stored as {field.target}</small>}{field.required && <span className="required-mark">Required</span>}</td>
                    <td><select value={productionMappings[field.target] || ""} onChange={(event) => setProductionMappings((current) => ({ ...current, [field.target]: event.target.value }))}><option value="">Not mapped</option>{productionInspect.headers.map((header, index) => <option key={`${header}-${index}`} value={header}>{header || `column_${index + 1}`}</option>)}</select></td>
                    <td>{field.type}</td><td>{field.rule}</td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          </section>
          <footer className="sequential-page-actions">
            <button className="secondary-command" disabled={productionBusy} onClick={() => setProductionStep(1)}><ArrowLeft size={17} /> Back to File Import</button>
            <button className="primary-command" disabled={productionBusy || unresolvedRequired > 0} onClick={handleProductionPreview}>{productionBusy ? "Generating preview..." : "Next: Review Mapped Data"}<ArrowRight size={17} /></button>
          </footer>
        </section>
      )}

      {productionStep === 3 && productionPreview && (
        <section className="sequential-page mapped-review-workspace">
          <section className="mapped-review-section">
            <div className="mapping-toolbar"><div><h2>Step 3: Review mapped production data</h2><p>Review transformed daily rows before writing production tables.</p></div></div>
            <div className="mapped-header-list production-mapping-list">{Object.entries(productionPreview.mapped_columns).map(([target, source]) => <span key={target}><small>{target}</small>{source}</span>)}</div>
            <ProductionPreviewTable rows={productionPreview.preview} />
          </section>
          <footer className="sequential-page-actions mapping-complete-actions">
            <button className="secondary-command" disabled={productionBusy} onClick={() => setProductionStep(2)}><ArrowLeft size={17} /> Back to Column Mapping</button>
            <label><input type="checkbox" checked={productionReplaceExisting} onChange={(event) => setProductionReplaceExisting(event.target.checked)} /> Replace existing production data</label>
            <button className="primary-command" disabled={productionBusy} onClick={handleProductionComplete}>{productionBusy ? "Completing import..." : "Complete Process"}<Check size={17} /></button>
          </footer>
        </section>
      )}

      {productionStep === 4 && productionSummary && (
        <section className="sequential-page completion-workspace import-complete-page">
          <div className="completion-icon"><Check size={28} /></div>
          <h2>Production import is complete</h2>
          <p>Daily production rows were imported and monthly cumulative production was generated.</p>
          <div className="result-grid">
            <div><span>Daily table</span><strong>{productionSummary.daily_table_name}</strong></div>
            <div><span>Daily rows</span><strong>{productionSummary.daily_row_count.toLocaleString()}</strong></div>
            <div><span>Monthly table</span><strong>{productionSummary.monthly_table_name}</strong></div>
            <div><span>Monthly rows</span><strong>{productionSummary.monthly_row_count.toLocaleString()}</strong></div>
            <div><span>Wells</span><strong>{productionSummary.well_count.toLocaleString()}</strong></div>
            <div><span>Skipped rows</span><strong>{productionSummary.skipped_row_count.toLocaleString()}</strong></div>
          </div>
          <ProductionPreviewTable rows={productionSummary.preview} />
        </section>
      )}
    </>
  );
}

export default function RawDataImport({ onDone }) {
  const [activeImportTab, setActiveImportTab] = useState("raw");
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
  const [productionFile, setProductionFile] = useState(null);
  const [productionReplaceExisting, setProductionReplaceExisting] = useState(true);
  const [productionStep, setProductionStep] = useState(1);
  const [productionInspect, setProductionInspect] = useState(null);
  const [productionMappings, setProductionMappings] = useState({});
  const [productionPreview, setProductionPreview] = useState(null);
  const [productionSummary, setProductionSummary] = useState(null);
  const [productionBusy, setProductionBusy] = useState(false);

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

  async function handleProductionInspect(event) {
    event.preventDefault();
    if (!productionFile) return;
    setProductionBusy(true);
    setError("");
    setProductionInspect(null);
    setProductionPreview(null);
    setProductionSummary(null);
    try {
      const inspected = await inspectProductionData(productionFile);
      setProductionInspect(inspected);
      setProductionMappings(inspected.suggested_mappings || {});
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setProductionBusy(false);
    }
  }

  async function handleProductionPreview() {
    if (!productionFile) return;
    setProductionBusy(true);
    setError("");
    setProductionSummary(null);
    try {
      const preview = await previewProductionData(productionFile, productionMappings);
      setProductionPreview(preview);
      setProductionStep(3);
    } catch (previewError) {
      setError(previewError.message);
    } finally {
      setProductionBusy(false);
    }
  }

  async function handleProductionComplete() {
    if (!productionFile) return;
    setProductionBusy(true);
    setError("");
    try {
      const imported = await uploadProductionData(productionFile, productionReplaceExisting, productionMappings);
      setProductionSummary(imported);
      setProductionStep(4);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setProductionBusy(false);
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

      <nav className="import-subtabs" aria-label="Data import sections">
        <button className={activeImportTab === "raw" ? "selected" : ""} type="button" onClick={() => { setActiveImportTab("raw"); setError(""); }}>
          <FileSpreadsheet size={17} />
          <span><strong>Raw Data Import & Mapping</strong><small>Upload, map, and split source tables</small></span>
        </button>
        <button className={activeImportTab === "production" ? "selected" : ""} type="button" onClick={() => { setActiveImportTab("production"); setError(""); }}>
          <Database size={17} />
          <span><strong>Daily Production File Import</strong><small>Map daily volumes to production tables</small></span>
        </button>
      </nav>

      {activeImportTab === "raw" && importMetrics && (
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

      {activeImportTab === "production" && (
        <ProductionImportTab
          productionFile={productionFile}
          setProductionFile={setProductionFile}
          productionStep={productionStep}
          setProductionStep={setProductionStep}
          productionInspect={productionInspect}
          setProductionInspect={setProductionInspect}
          productionMappings={productionMappings}
          setProductionMappings={setProductionMappings}
          productionPreview={productionPreview}
          setProductionPreview={setProductionPreview}
          productionSummary={productionSummary}
          setProductionSummary={setProductionSummary}
          productionReplaceExisting={productionReplaceExisting}
          setProductionReplaceExisting={setProductionReplaceExisting}
          productionBusy={productionBusy}
          handleProductionInspect={handleProductionInspect}
          handleProductionPreview={handleProductionPreview}
          handleProductionComplete={handleProductionComplete}
        />
      )}

      {activeImportTab === "raw" && (
        <>
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
      )}
        </>
      )}
    </main>
  );
}










