import axios from "axios";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (err) => {
    const isLogin = err.config?.url === "/auth/login";
    if (err.response?.status === 401 && !isLogin) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") window.location.assign("/login");
    }
    return Promise.reject(err);
  }
);

export function errorMessage(err) {
  const detail = err.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => `${e.loc.slice(1).join(".")}: ${e.msg}`).join(" | ");
  }
  if (typeof detail === "string") return detail;
  return err.message;
}

export default api;