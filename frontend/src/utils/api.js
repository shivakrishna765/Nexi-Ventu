/**
 * api.js — Centralised API client for Nexus Venture
 * All backend calls go through here so auth headers are always attached.
 */

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  try {
    const s = localStorage.getItem("nexus_session");
    return s ? JSON.parse(s).token : null;
  } catch {
    return null;
  }
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const api = {
  login: (email, password) => {
    const body = new URLSearchParams({ username: email, password });
    return fetch(`${BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    }).then(async (r) => {
      if (!r.ok) throw new Error((await r.json()).detail || "Login failed");
      return r.json();
    });
  },

  signup: (name, email, password, role) =>
    request("/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password, role }),
    }),

  getProfile: () => request("/profile"),

  updateProfile: (data) =>
    request("/profile", { method: "PUT", body: JSON.stringify(data) }),

  // ── Chatbot ────────────────────────────────────────────────────────────────
  chat: (payload) =>
    request("/nexus-chat", { method: "POST", body: JSON.stringify(payload) }),

  chatDemo: (payload) =>
    request("/nexus-chat/demo", { method: "POST", body: JSON.stringify(payload) }),

  // ── Startups ───────────────────────────────────────────────────────────────
  getStartups: () => request("/get-startups"),

  // ── Admin ──────────────────────────────────────────────────────────────────
  adminStats: () => request("/admin/stats"),
};
