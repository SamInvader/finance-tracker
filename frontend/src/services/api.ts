import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem("ledgerly_token", token);
  } else {
    localStorage.removeItem("ledgerly_token");
  }
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ledgerly_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.error || err.message || "Request failed";
    return Promise.reject({ ...err, message, details: err.response?.data?.details });
  }
);

export async function unwrap<T>(p: Promise<{ data: { ok: boolean; data: T; error?: string } }>): Promise<T> {
  const res = await p;
  return res.data.data;
}

export default api;
