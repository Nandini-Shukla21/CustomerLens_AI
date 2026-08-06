import axios, { AxiosError } from "axios";

export const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL, timeout: 30_000 });
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("customerlens_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use((response) => response, (error: AxiosError<{ detail?: string }>) => {
  const message = error.response?.data?.detail || (error.code === "ECONNABORTED" ? "The request timed out." : "Unable to reach the server.");
  return Promise.reject(new Error(message));
});
