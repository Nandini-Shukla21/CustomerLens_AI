import { api } from "./client";

// ============================================================
// TYPES
// ============================================================

export type Dataset = {
  id: string;
  filename: string;
  rows: number;
  columns: number;
  created_at: string;
};

export type DocumentItem = {
  id: string;
  filename: string;
  path: string;
  file_type: string;
  size_bytes: number;
  checksum?: string;
  indexed_at?: string;
  created_at: string;
};

export type UploadResult = {
  dataset_id?: string;
  document_id?: string;
  filename: string;
  row_count?: number;
  column_count?: number;
  columns?: string[];
  data_types?: Record<string, string>;
  missing_values?: Record<string, number>;
  quality_score?: number;
  chunks?: number;
  status?: string;
};

// ============================================================
// PLATFORM API
// ============================================================

export const platformApi = {
  // ==========================================================
  // DASHBOARD
  // ==========================================================

  dashboard: () =>
    api.get("/dashboard").then((r) => r.data),

  // ==========================================================
  // DATASETS
  // ==========================================================

  datasets: () =>
    api.get<Dataset[]>("/datasets").then((r) => r.data),

  dataset: (id: string) =>
    api
      .get(`/datasets/${encodeURIComponent(id)}`)
      .then((r) => r.data),

  datasetPreview: (
    id: string,
    offset = 0,
    q = "",
    limit = 200,
  ) =>
    api
      .get(`/datasets/${encodeURIComponent(id)}/preview`, {
        params: {
          offset,
          q,
          limit,
        },
      })
      .then((r) => r.data),

  datasetColumns: (id: string) =>
    api
      .get(`/datasets/${encodeURIComponent(id)}/columns`)
      .then((r) => r.data),

  // ==========================================================
  // DATASET DOWNLOAD
  // ==========================================================

  downloadDataset: async (id: string): Promise<Blob> => {
    const response = await api.get(
      `/datasets/${encodeURIComponent(id)}/download`,
      {
        responseType: "blob",
      },
    );

    return response.data;
  },

  // ==========================================================
  // DATASET DELETE
  // ==========================================================

  deleteDataset: (id: string) =>
    api
      .delete(`/datasets/${encodeURIComponent(id)}`)
      .then((r) => r.data),

  // ==========================================================
  // DOCUMENTS
  // ==========================================================

  documents: () =>
    api.get<DocumentItem[]>("/documents").then((r) => r.data),

  document: (id: string) =>
    api
      .get(`/documents/${encodeURIComponent(id)}`)
      .then((r) => r.data),

  // ==========================================================
  // DOCUMENT DOWNLOAD
  // ==========================================================

  downloadDocument: async (id: string): Promise<Blob> => {
    const response = await api.get(
      `/documents/${encodeURIComponent(id)}/download`,
      {
        responseType: "blob",
      },
    );

    return response.data;
  },

  // ==========================================================
  // DOCUMENT DELETE
  // ==========================================================

  deleteDocument: (id: string) =>
    api
      .delete(`/documents/${encodeURIComponent(id)}`)
      .then((r) => r.data),

  // ==========================================================
  // CUSTOMERS
  // ==========================================================

  customers: (q = "") =>
    api
      .get("/customers", {
        params: { q },
      })
      .then((r) => r.data),

  customer: (id: string) =>
    api
      .get(`/customers/${encodeURIComponent(id)}`)
      .then((r) => r.data),

  // ==========================================================
  // ANALYTICS
  // ==========================================================

  analytics: (dataset_id?: string) =>
    api
      .get("/analytics", {
        params: dataset_id ? { dataset_id } : {},
      })
      .then((r) => r.data),

  // ==========================================================
  // PREDICTIONS
  // ==========================================================

  predictionHistory: () =>
    api.get("/predictions/history").then((r) => r.data),

  predict: (
    customer_id: string,
    features: Record<string, unknown> = {},
  ) =>
    api
      .post("/predict", {
        customer_id,
        features,
      })
      .then((r) => r.data),

  // ==========================================================
  // SEARCH
  // ==========================================================

  search: (q: string) =>
    api
      .get("/search", {
        params: { q },
      })
      .then((r) => r.data),

  // ==========================================================
  // REPORTS
  // ==========================================================

  reportsDashboard: () =>
    api.get("/reports/dashboard").then((r) => r.data),

  // ==========================================================
  // RAG / COPILOT
  // ==========================================================

  copilot: (question: string) =>
    api
      .post("/rag/query", {
        question,
      })
      .then((r) => r.data),

  chat: (question: string) =>
    api
      .post("/rag/query", {
        question,
      })
      .then((r) => r.data),

  // ==========================================================
  // AUTH
  // ==========================================================

  me: () =>
    api.get("/auth/me").then((r) => r.data),

  login: (email: string, password: string) =>
    api
      .post("/auth/login", {
        email,
        password,
      })
      .then((r) => r.data),

  register: (
    name: string,
    email: string,
    password: string,
    role: string,
  ) =>
    api
      .post("/auth/register", {
        name,
        email,
        password,
        role,
      })
      .then((r) => r.data),

  // ==========================================================
  // INSIGHTS
  // ==========================================================

  insights: () =>
    api.get("/insights").then((r) => r.data),

  // ==========================================================
  // NOTIFICATIONS
  // ==========================================================

  notifications: () =>
    api.get("/notifications").then((r) => r.data),

  // ==========================================================
  // ACTIVITY
  // ==========================================================

  activity: () =>
    api.get("/activity").then((r) => r.data),

  // ==========================================================
  // UPLOAD
  // ==========================================================

  upload: (
    file: File,
    onUploadProgress?: (pct: number) => void,
  ) => {
    const form = new FormData();
    form.append("file", file);

    const extension = file.name
      .split(".")
      .pop()
      ?.toLowerCase();

    const endpoint = [
      "csv",
      "xlsx",
      "xls",
      "json",
    ].includes(extension ?? "")
      ? "/datasets"
      : "/documents";

    return api
      .post<UploadResult>(endpoint, form, {
        onUploadProgress: (e) => {
          onUploadProgress?.(
            e.total
              ? Math.round((e.loaded * 100) / e.total)
              : 0,
          );
        },
      })
      .then((r) => r.data);
  },
};