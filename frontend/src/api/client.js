const API_BASE_URL = window.location.protocol + "//" + window.location.hostname + ":" + (import.meta.env.VITE_API_PORT || "8001") + "/api";

const AUTH_TOKEN_KEY = "sp_auth_token";
localStorage.removeItem(AUTH_TOKEN_KEY);
let authToken = sessionStorage.getItem(AUTH_TOKEN_KEY);

function authHeaders(headers = {}) {
  return authToken ? { ...headers, Authorization: "Token " + authToken } : headers;
}

async function request(path) {
  const response = await fetch(API_BASE_URL + path, { headers: authHeaders() });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "API request failed: " + response.status);
  return data;
}

export async function fetchAuthStatus() {
  try {
    return await request("/auth/status/");
  } catch {
    authToken = null;
    sessionStorage.removeItem(AUTH_TOKEN_KEY);
    return request("/auth/status/");
  }
}

export async function loginUser(username, password) {
  authToken = null;
  sessionStorage.removeItem(AUTH_TOKEN_KEY);
  const data = await jsonRequest("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  authToken = data.token;
  sessionStorage.setItem(AUTH_TOKEN_KEY, data.token);
  return data.user;
}

export async function setupUser(username, email, password) {
  authToken = null;
  sessionStorage.removeItem(AUTH_TOKEN_KEY);
  const data = await jsonRequest("/auth/setup/", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
  authToken = data.token;
  sessionStorage.setItem(AUTH_TOKEN_KEY, data.token);
  return data.user;
}

export async function logoutUser() {
  try {
    await jsonRequest("/auth/logout/", { method: "POST", body: JSON.stringify({}) });
  } finally {
    authToken = null;
    sessionStorage.removeItem(AUTH_TOKEN_KEY);
  }
}

function wellFilterParams(filters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item) params.append(key, item);
      });
    } else if (value) {
      params.set(key, value);
    }
  });
  return params;
}

export async function fetchWells(filters = {}) {
  const params = wellFilterParams(filters);
  const query = params.toString();
  return request(`/wells/${query ? `?${query}` : ""}`);
}

export async function fetchAllWells(filters = {}) {
  const params = wellFilterParams(filters);
  let page = 1;
  let count = 0;
  const results = [];

  while (page) {
    params.set("page", String(page));
    const data = await request(`/wells/?${params.toString()}`);
    const pageResults = Array.isArray(data) ? data : data.results || [];
    results.push(...pageResults);
    count = Array.isArray(data) ? results.length : data.count ?? results.length;
    if (Array.isArray(data) || !data.next) {
      page = null;
    } else if (typeof data.next === "number") {
      page = data.next;
    } else if (/^\d+$/.test(String(data.next))) {
      page = String(data.next);
    } else {
      const nextUrl = new URL(data.next, window.location.origin);
      page = nextUrl.searchParams.get("page");
    }
  }

  return { count, next: null, previous: null, results };
}

export async function fetchWellProductionDaily(wellId) {
  return request(`/wells/${encodeURIComponent(wellId)}/production-daily/`);
}
export async function fetchWellStatuses() {
  return request("/well-statuses/");
}

export async function fetchActualWellStatuses(status = []) {
  const params = new URLSearchParams();
  const statuses = Array.isArray(status) ? status : [status];
  statuses.forEach((item) => {
    if (item) params.append("status", item);
  });
  const query = params.toString();
  return request(`/actual-well-statuses/${query ? `?${query}` : ""}`);
}

export async function fetchWellTypes() {
  return request("/well-types/");
}

export async function fetchCurrentOperators() {
  return request("/current-operators/");
}

export async function fetchProductionInjectionFormations() {
  return request("/production-injection-formations/");
}


export async function fetchDataBrowserDatabases() {
  return request("/data-browser/databases/");
}

export async function deleteDataBrowserTable(database, table, confirmation) {
  return jsonRequest("/data-browser/tables/", {
    method: "DELETE",
    body: JSON.stringify({ database, table, confirmation }),
  });
}
export async function fetchDataBrowserRows({ database, table, columns = [], search = "", page = 1, pageSize = 100 }) {
  const params = new URLSearchParams();
  if (database) params.set("database", database);
  if (table) params.set("table", table);
  if (search) params.set("search", search);
  params.set("page", page);
  params.set("page_size", pageSize);
  columns.forEach((column) => params.append("columns", column));
  return request(`/data-browser/query/?${params.toString()}`);
}
async function jsonRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: authHeaders({ "Content-Type": "application/json", ...(options.headers || {}) }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `API request failed: ${response.status}`);
  return data;
}

export async function uploadRawWorkbook(file) {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE_URL}/imports/upload/`, { method: "POST", headers: authHeaders(), body: form });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Upload failed: ${response.status}`);
  return data;
}

async function productionFileRequest(path, file, payload = {}) {
  const form = new FormData();
  form.append("file", file);
  Object.entries(payload).forEach(([key, value]) => {
    form.append(key, typeof value === "object" ? JSON.stringify(value) : String(value));
  });
  const response = await fetch(`${API_BASE_URL}${path}`, { method: "POST", headers: authHeaders(), body: form });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Upload failed: ${response.status}`);
  return data;
}

export async function inspectProductionData(file) {
  return productionFileRequest("/imports/production/inspect/", file);
}

export async function previewProductionData(file, mappings) {
  return productionFileRequest("/imports/production/preview/", file, { mappings });
}

export async function uploadProductionData(file, replaceExisting = true, mappings = {}) {
  return productionFileRequest("/imports/production/upload/", file, {
    replace_existing: replaceExisting ? "true" : "false",
    mappings,
  });
}

export async function fetchImportBatch(batchId) {
  return request(`/imports/batches/${batchId}/`);
}

export async function createRawImportTable(batchId) {
  return jsonRequest(`/imports/batches/${batchId}/raw-table/`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}
export async function fetchMappingTemplates() {
  return request("/imports/mapping-templates/");
}

export async function saveMappingTemplate(batchId, name) {
  return jsonRequest(`/imports/batches/${batchId}/mapping-templates/`, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function applyMappingTemplate(batchId, templateId) {
  return jsonRequest(`/imports/batches/${batchId}/apply-mapping-template/`, {
    method: "POST",
    body: JSON.stringify({ template_id: templateId }),
  });
}
export async function saveImportMappings(batchId, mappings) {
  return jsonRequest(`/imports/batches/${batchId}/mappings/`, {
    method: "PUT",
    body: JSON.stringify({ mappings }),
  });
}

export async function fetchMappedPreview(batchId) {
  return request(`/imports/batches/${batchId}/mapped-preview/`);
}
export async function executeImportSplit(batchId, replaceExisting = true) {
  return jsonRequest(`/imports/batches/${batchId}/execute/`, {
    method: "POST",
    body: JSON.stringify({ replace_existing: replaceExisting }),
  });
}

