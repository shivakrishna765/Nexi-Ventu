const KEY = "nexus_session";

export function getSession() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setSession(payload) {
  localStorage.setItem(KEY, JSON.stringify(payload));
}

export function clearSession() {
  localStorage.removeItem(KEY);
}

export function roleToRoute(role) {
  const map = {
    investor:     "/investor-dashboard",
    founder:      "/founder-dashboard",
    seeker:       "/team-dashboard",
    "team seeker": "/team-dashboard",
    collaborator: "/collaborator-dashboard",
    member:       "/team-dashboard",
  };
  return map[(role || "").toLowerCase()] || "/team-dashboard";
}
