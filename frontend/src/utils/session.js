/**
 * session.js — localStorage helpers for Nexus Venture auth state.
 *
 * Storage layout:
 *   "token"        → JWT access token string
 *   "user"         → JSON-stringified user object
 *   "nexus_session"→ combined { token, ...user } for legacy compat
 */

// ── Write ─────────────────────────────────────────────────────────────────────

export function setSession({ token, ...user }) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
  // keep combined key for any code that still reads it
  localStorage.setItem("nexus_session", JSON.stringify({ token, ...user }));
}

// ── Read ──────────────────────────────────────────────────────────────────────

export function getToken() {
  return localStorage.getItem("token") || null;
}

export function getUser() {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/** Returns the combined session object { token, ...user } or null */
export function getSession() {
  const token = getToken();
  const user  = getUser();
  if (!token || !user) return null;
  return { token, ...user };
}

// ── Clear ─────────────────────────────────────────────────────────────────────

export function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("nexus_session");
}

// ── Role → route map ──────────────────────────────────────────────────────────

export function roleToRoute(role) {
  const map = {
    investor:      "/investor-dashboard",
    founder:       "/founder-dashboard",
    seeker:        "/team-dashboard",
    "team seeker": "/team-dashboard",
    collaborator:  "/collaborator-dashboard",
    member:        "/team-dashboard",
  };
  return map[(role || "").toLowerCase()] || "/team-dashboard";
}
