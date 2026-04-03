/**
 * api.js — Centralised API client for Nexus Venture
 *
 * All requests go directly to http://127.0.0.1:8000.
 * CORS is configured on the backend to allow http://localhost:5173.
 *
 * For production: set VITE_API_URL=https://your-api.com in .env.production
 */
const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function getToken() {
  try { return localStorage.getItem("token") || null; }
  catch { return null; }
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  } catch (networkErr) {
    console.error(`[API] Network error on ${path}:`, networkErr);
    throw new Error("Cannot reach the server. Is the backend running on http://127.0.0.1:8000?");
  }

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch { /* non-JSON error body */ }
    console.error(`[API] ${path} → ${res.status}:`, detail);
    throw new Error(detail);
  }

  return res.json();
}

export const api = {
  /**
   * POST /login
   * FastAPI requires application/x-www-form-urlencoded with field "username".
   */
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    let res;
    try {
      res = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData,
      });
    } catch (networkErr) {
      console.error("[API] Network error on /login:", networkErr);
      throw new Error("Cannot reach the server. Is the backend running on http://127.0.0.1:8000?");
    }

    if (!res.ok) {
      let detail = "Login failed";
      try { detail = (await res.json()).detail || detail; } catch { /* ignore */ }
      console.error("[API] /login →", res.status, detail);
      throw new Error(detail);
    }

    const data = await res.json();
    console.log("[API] LOGIN RESPONSE:", { token: data.access_token?.slice(0, 20) + "...", user: data.user });
    return data;
  },

  /**
   * POST /signup — JSON body
   */
  signup: async (name, email, password, role) => {
    const data = await request("/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password, role }),
    });
    console.log("[API] SIGNUP RESPONSE:", { token: data.access_token?.slice(0, 20) + "...", user: data.user });
    return data;
  },

  getProfile:    ()     => request("/profile"),
  updateProfile: (data) => request("/profile", { method: "PUT", body: JSON.stringify(data) }),
  test:          ()     => request("/test"),

  chat:        (payload) => request("/nexus-chat",      { method: "POST", body: JSON.stringify(payload) }),
  chatDemo:    (payload) => request("/nexus-chat/demo", { method: "POST", body: JSON.stringify(payload) }),
  getStartups: ()        => request("/get-startups"),
  adminStats:  ()        => request("/admin/stats"),
};
