import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api } from "../utils/api";
import { getSession, setSession, clearSession, getToken, getUser } from "../utils/session";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Seed state from localStorage immediately — no flicker, no blank screen
  const [user, setUser]       = useState(() => {
    const token = getToken();
    const u     = getUser();
    return token && u ? { ...u, token } : null;
  });
  const [loading, setLoading] = useState(true);

  // On mount: validate the stored token against /profile
  // If backend is unreachable, keep the stored user (don't log them out)
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    api.getProfile()
      .then((profile) => {
        console.log("[Auth] Profile refreshed:", profile.email, "role:", profile.role);
        const updated = { ...profile, token };
        setSession({ token, ...profile });
        setUser(updated);
      })
      .catch((err) => {
        console.warn("[Auth] Profile fetch failed:", err.message);
        // Only clear session if it's a 401 (invalid token), not a network error
        if (err.message.includes("401") || err.message.includes("credentials")) {
          clearSession();
          setUser(null);
        }
        // Otherwise keep the stored user — backend may just be starting up
      })
      .finally(() => setLoading(false));
  }, []);

  // ── login ──────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const data = await api.login(email, password);
    const { access_token, user: userData } = data;

    console.log("[Auth] Login success:", userData.email, "role:", userData.role);

    setSession({ token: access_token, ...userData });
    setUser({ ...userData, token: access_token });

    return userData;
  }, []);

  // ── signup ─────────────────────────────────────────────────────────────────
  const signup = useCallback(async (name, email, password, role) => {
    const data = await api.signup(name, email, password, role);
    const { access_token, user: userData } = data;

    console.log("[Auth] Signup success:", userData.email, "role:", userData.role);

    setSession({ token: access_token, ...userData });
    setUser({ ...userData, token: access_token });

    return userData;
  }, []);

  // ── logout ─────────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    console.log("[Auth] Logged out");
    clearSession();
    setUser(null);
  }, []);

  // ── updateUser ─────────────────────────────────────────────────────────────
  const updateUser = useCallback(async (updates) => {
    const updated = await api.updateProfile(updates);
    const token   = getToken();
    setSession({ token, ...updated });
    setUser({ ...updated, token });
    return updated;
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
