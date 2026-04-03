/**
 * session.js — localStorage helpers for Nexus Venture auth state.
 *
 * Keys:
 *   "token"  → JWT string
 *   "user"   → JSON user object (without token)
 */

export function setSession({ token, ...user }) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

export function getToken() {
  try { return localStorage.getItem("token") || null; }
  catch { return null; }
}

export function getUser() {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch { return null; }
}

export function getSession() {
  const token = getToken();
  const user  = getUser();
  return token && user ? { token, ...user } : null;
}

export function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("nexus_session"); // legacy key cleanup
}

export function roleToRoute(role) {
  const map = {
    investor:      "/investor-dashboard",
    founder:       "/founder-dashboard",
    seeker:        "/team-dashboard",
    "team seeker": "/team-dashboard",
    member:        "/team-dashboard",
    collaborator:  "/collaborator-dashboard",
  };
  return map[(role || "").toLowerCase().trim()] || "/team-dashboard";
}
