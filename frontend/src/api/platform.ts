import { api } from "./client";

export type Dataset = { id: string; filename: string; rows: number; columns: number; created_at: string };
export type DocumentItem = { id: string; filename: string; path: string; file_type: string; size_bytes: number; checksum?: string; indexed_at?: string; created_at: string };
export type UploadResult = { dataset_id?: string; document_id?: string; filename: string; row_count?: number; column_count?: number; columns?: string[]; data_types?: Record<string, string>; missing_values?: Record<string, number>; quality_score?: number; chunks?: number; status?: string };
export const platformApi = {
  dashboard: () => api.get("/dashboard").then(r => r.data),
  datasets: () => api.get<Dataset[]>("/datasets").then(r => r.data),
  documents: () => api.get<DocumentItem[]>("/documents").then(r => r.data),
  document: (id: string) => api.get(`/documents/${id}`).then(r => r.data),
  dataset: (id: string) => api.get(`/datasets/${id}`).then(r => r.data),
  datasetPreview: (id: string, offset = 0, q = "") => api.get(`/datasets/${id}/preview`, { params: { offset, q } }).then(r => r.data),
  datasetColumns: (id: string) => api.get(`/datasets/${id}/columns`).then(r => r.data),
  customers: (q = "") => api.get("/customers", { params: { q } }).then(r => r.data),
  customer: (id: string) => api.get(`/customers/${encodeURIComponent(id)}`).then(r => r.data),
  analytics: (dataset_id?: string) => api.get("/analytics", { params: { dataset_id } }).then(r => r.data),
  predictionHistory: () => api.get("/predictions/history").then(r => r.data),
  predict: (customer_id: string, features: Record<string, unknown> = {}) => api.post("/predict", { customer_id, features }).then(r => r.data),
  search: (q: string) => api.get("/search", { params: { q } }).then(r => r.data),
  reportsDashboard: () => api.get("/reports/dashboard").then(r => r.data),
  copilot: (question: string) => api.post("/rag/query", { question }).then(r => r.data),
  me: () => api.get("/auth/me").then(r => r.data),
  insights: () => api.get("/insights").then(r => r.data),
  notifications: () => api.get("/notifications").then(r => r.data),
  activity: () => api.get("/activity").then(r => r.data),
  upload: (file: File, onUploadProgress?: (pct: number) => void) => {
    const form = new FormData(); form.append("file", file);
    const extension = file.name.split(".").pop()?.toLowerCase();
    const endpoint = ["csv", "xlsx", "xls", "json"].includes(extension ?? "") ? "/datasets" : "/documents";
    return api.post<UploadResult>(endpoint, form, { onUploadProgress: e => onUploadProgress?.(e.total ? Math.round(e.loaded * 100 / e.total) : 0) }).then(r => r.data);
  },
  login: (email: string, password: string) => api.post("/auth/login", { email, password }).then(r => r.data),
  register: (name: string, email: string, password: string, role: string) => api.post("/auth/register", { name, email, password, role }).then(r => r.data),
  chat: (question: string) => api.post("/rag/query", { question }).then(r => r.data),
};
