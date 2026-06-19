import { create } from "zustand";
import api from "../services/api";

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem("access_token") || null,
  isAuthenticated: !!localStorage.getItem("access_token"),

  login: async (email, password) => {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);
    const res = await api.post("/auth/login", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    localStorage.setItem("access_token", res.data.access_token);
    set({ token: res.data.access_token, isAuthenticated: true, user: res.data });
    return res.data;
  },

  register: async (email, password, full_name) => {
    const res = await api.post("/auth/register", { email, password, full_name });
    localStorage.setItem("access_token", res.data.access_token);
    set({ token: res.data.access_token, isAuthenticated: true, user: res.data });
    return res.data;
  },

  logout: () => {
    localStorage.removeItem("access_token");
    set({ token: null, isAuthenticated: false, user: null });
    window.location.href = "/login";
  },
}));

export default useAuthStore;
