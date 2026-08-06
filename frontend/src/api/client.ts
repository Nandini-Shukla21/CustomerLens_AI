import axios, { AxiosError } from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("customerlens_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: unknown }>) => {
    console.log("Axios error:", error.response?.data);

    const detail = error.response?.data?.detail;

    const message =
      typeof detail === "string"
        ? detail
        : detail
        ? JSON.stringify(detail)
        : error.code === "ECONNABORTED"
        ? "The request timed out."
        : "Unable to reach the server.";

    return Promise.reject(new Error(message));
  }
);