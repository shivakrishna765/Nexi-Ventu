/**
 * api.js — Centralised API client for Nexus Venture
 *
 * Calls go directly to http://127.0.0.1:8000 in development.
 * Backend has CORS configured to allow http://localhost:5173.
 *
 * For production deploy, set VITE_API_URL in your .env.production file.
 */
const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// ── Token helpers ─────────────────────────────────────────────────────────────

function getToken() {
  try {
    return localStorage.getItem("token") || null;
  } catch {
    return null;
  }
}

// ── Generic authenticated JSON request ───────────────────────────────────────

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  } catch (networkErr) {
    console.error("Network error:", networkErr);
    throw new Error(
      "Cannot reach the server. Make sure the backend is running on http://127.0.0.1:8000"
    );
  }

  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch { /* response wasn't JSON */ }
    throw new Error(detail);
  }

  return res.json();
}

// ── API methods ───────────────────────────────────────────────────────────────

export const api = {

  /**
   * POST /login
   * FastAPI's OAuth2PasswordRequestForm requires application/x-www-form-urlencoded.
   * The field MUST be "username" (not "email") — FastAPI standard.
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
      console.error("Network error on login:", networkErr);
      throw new Error(
        "Cannot reach the server. Make sure the backend is running on http://127.0.0.1:8000"
      );
    }

    if (!res.ok) {
      let detail = "Login failed";
      try { detail = (await res.json()).detail || detail; } catch { /* ignore */ }
      throw new Error(detail);
    }

    return res.json(); // { access_token, token_type, user }
  },

  /**
   * POST /signup
   * JSON body: { name, email, password, role }
   * Returns: { access_token, token_type, user }
   */
  signup: (name, email, password, role) =>
    request("/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password, role }),
    }),

  /** GET /profile — requires Bearer token */
  getProfile: () => request("/profile"),

  /** PUT /profile — update user fields */
  updateProfile: (data) =>
    request("/profile", { method: "PUT", body: JSON.stringify(data) }),

  /** GET /test — quick connectivity check */
  test: () => request("/test"),

  // ── Chatbot ────────────────────────────────────────────────────────────────
  chat:     (payload) => request("/nexus-chat",      { method: "POST", body: JSON.stringify(payload) }),
  chatDemo: (payload) => request("/nexus-chat/demo", { method: "POST", body: JSON.stringify(payload) }),

  // ── Startups ───────────────────────────────────────────────────────────────
  getStartups: () => request("/get-startups"),

  // ── Admin ──────────────────────────────────────────────────────────────────
  adminStats: () => request("/admin/stats"),
};
