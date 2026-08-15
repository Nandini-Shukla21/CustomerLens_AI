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
  path?: string;
  file_type?: string;
  size_bytes?: number;
  checksum?: string;
  indexed_at?: string;
  created_at: string;
};

export type HomeDocument = {
  id: string;
  filename: string;
  checksum?: string;
  indexed_at?: string;
  created_at: string;
  status: string;
};

export type HomeActivity = {
  id: string;
  who: string;
  what: string;
  when: string;
  type: string;
};

export type RecentActivity = {
  id: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  entity_name: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type Insight = {
  id: string;
  dataset_id?: string;
  title: string;
  description: string;
  priority: string;
  confidence: number;
  action: string;
  created_at: string;
};

export type HomeOverview = {
  stats: {
    datasets: number;
    documents: number;
    customers: number;
    revenue: number;
    transactions: number;
    average_ltv: number;
    average_risk: number;
    average_churn: number;
    predictions: number;
    average_prediction_probability: number;
    average_prediction_confidence: number;
    total_uploads: number;
    total_size_bytes: number;
  };

  datasets: Dataset[];

  documents: HomeDocument[];

  /*
   * This is the format expected by _app.home.tsx.
   * It is created from the backend's recent_activity.
   */
  activity: HomeActivity[];

  /*
   * Raw activity returned by the backend.
   */
  recent_activity: RecentActivity[];

  insights: Insight[];

  charts: {
    uploads: {
      date: string;
      count: number;
    }[];

    datasets: {
      name: string;
      rows: number;
      columns: number;
    }[];
  };
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
    api
      .get("/dashboard")
      .then((r) => r.data),

  // ==========================================================
  // HOME OVERVIEW
  // ==========================================================

  home: async (): Promise<HomeOverview> => {
    const response = await api.get("/home/summary");

    const data = response.data;

    /*
     * Backend returns `recent_activity`.
     *
     * The current home page expects:
     *   who
     *   what
     *   when
     *   type
     *
     * Convert the backend format here so we don't have
     * to change the UI component.
     */
    const activity: HomeActivity[] = (
      data.recent_activity ?? []
    ).map((item: RecentActivity) => ({
      id: item.id,
      who: item.entity_name || "System",
      what: item.action || "performed an action",
      when: item.created_at,
      type: item.entity_type || "activity",
    }));

    return {
      ...data,
      activity,
    };
  },

  // ==========================================================
  // HOME SUMMARY
  // ==========================================================

  homeSummary: async (): Promise<HomeOverview> => {
    const response = await api.get("/home/summary");

    const data = response.data;

    const activity: HomeActivity[] = (
      data.recent_activity ?? []
    ).map((item: RecentActivity) => ({
      id: item.id,
      who: item.entity_name || "System",
      what: item.action || "performed an action",
      when: item.created_at,
      type: item.entity_type || "activity",
    }));

    return {
      ...data,
      activity,
    };
  },

  // ==========================================================
  // DATASETS
  // ==========================================================

  datasets: () =>
    api
      .get<Dataset[]>("/datasets")
      .then((r) => r.data),

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
      .get(
        `/datasets/${encodeURIComponent(id)}/preview`,
        {
          params: {
            offset,
            q,
            limit,
          },
        },
      )
      .then((r) => r.data),

  datasetColumns: (id: string) =>
    api
      .get(
        `/datasets/${encodeURIComponent(id)}/columns`,
      )
      .then((r) => r.data),

  // ==========================================================
  // DATASET DOWNLOAD
  // ==========================================================

  downloadDataset: async (
    id: string,
  ): Promise<Blob> => {
    const response = await api.get<Blob>(
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

  deleteDataset: async (
    id: string,
  ) => {
    const response = await api.delete(
      `/datasets/${encodeURIComponent(id)}`,
    );

    return response.data;
  },

  // ==========================================================
  // DOCUMENTS
  // ==========================================================

  documents: () =>
    api
      .get<DocumentItem[]>("/documents")
      .then((r) => r.data),

  document: (id: string) =>
    api
      .get(
        `/documents/${encodeURIComponent(id)}`,
      )
      .then((r) => r.data),

  // ==========================================================
  // DOCUMENT DOWNLOAD
  // ==========================================================

  downloadDocument: async (
    id: string,
  ): Promise<Blob> => {
    const response = await api.get<Blob>(
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

  deleteDocument: async (
    id: string,
  ) => {
    const response = await api.delete(
      `/documents/${encodeURIComponent(id)}`,
    );

    return response.data;
  },

  // ==========================================================
  // CUSTOMERS
  // ==========================================================

  customers: (q = "") =>
    api
      .get("/customers", {
        params: {
          q,
        },
      })
      .then((r) => r.data),

  customer: (id: string) =>
    api
      .get(
        `/customers/${encodeURIComponent(id)}`,
      )
      .then((r) => r.data),

  // ==========================================================
  // ANALYTICS
  // ==========================================================

  analytics: (dataset_id?: string) =>
    api
      .get("/analytics", {
        params: dataset_id
          ? { dataset_id }
          : {},
      })
      .then((r) => r.data),

  // ==========================================================
  // PREDICTIONS
  // ==========================================================

  predictionHistory: () =>
    api
      .get("/predictions/history")
      .then((r) => r.data),

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
        params: {
          q,
        },
      })
      .then((r) => r.data),

  // ==========================================================
  // REPORTS
  // ==========================================================

  reportsDashboard: (dataset_id?: string) =>
    api
      .get("/reports/dashboard", {
        params: dataset_id
          ? { dataset_id }
          : {},
      })
      .then((r) => r.data),

  // ==========================================================
  // RAG / COPILOT
  // ==========================================================

  copilot: (
    question: string,
    dataset_id?: string,
  ) =>
    api
      .post("/rag/query", {
        question,
        dataset_id,
      })
      .then((r) => r.data),

  chat: (
    question: string,
    dataset_id?: string,
  ) =>
    api
      .post("/rag/query", {
        question,
        dataset_id,
      })
      .then((r) => r.data),

  // ==========================================================
  // AUTH
  // ==========================================================

  me: () =>
    api
      .get("/auth/me")
      .then((r) => r.data),

  login: (
    email: string,
    password: string,
  ) =>
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

  insights: (dataset_id?: string) =>
    api
      .get("/insights", {
        params: dataset_id
          ? { dataset_id }
          : {},
      })
      .then((r) => r.data),

  // ==========================================================
  // NOTIFICATIONS
  // ==========================================================

  notifications: () =>
    api
      .get("/notifications")
      .then((r) => r.data),

  // ==========================================================
  // ACTIVITY
  // ==========================================================

  activity: () =>
    api
      .get("/activity")
      .then((r) => r.data),

  // ==========================================================
  // UPLOAD
  // ==========================================================

  upload: (
    file: File,
    onUploadProgress?: (
      pct: number,
    ) => void,
  ) => {
    const form = new FormData();

    form.append("file", file);

    const extension = file.name
      .split(".")
      .pop()
      ?.toLowerCase();

    const datasetExtensions = [
      "csv",
      "xlsx",
      "xls",
      "json",
    ];

    const endpoint =
      datasetExtensions.includes(
        extension ?? "",
      )
        ? "/datasets"
        : "/documents";

    return api
      .post<UploadResult>(
        endpoint,
        form,
        {
          onUploadProgress: (event) => {
            if (event.total) {
              const percentage =
                Math.round(
                  (event.loaded * 100) /
                    event.total,
                );

              onUploadProgress?.(
                percentage,
              );
            } else {
              onUploadProgress?.(0);
            }
          },
        },
      )
      .then((r) => r.data);
  },
};