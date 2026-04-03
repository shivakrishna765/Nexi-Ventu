import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api } from "../utils/api";
import { getSession, setSession, clearSession, getToken } from "../utils/session";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount: if a token exists, validate it by fetching /profile
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    api.getProfile()
      .then((profile) => {
        // Merge fresh profile with stored token
        setUser({ ...profile, token });
        // Refresh stored user data in case profile changed
        setSession({ token, ...profile });
      })
      .catch(() => {
        // Token expired or invalid — clear everything
        clearSession();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  // ── login ──────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const data = await api.login(email, password);
    // data = { access_token, token_type, user }
    const { access_token, user: userData } = data;

    setSession({ token: access_token, ...userData });
    setUser({ ...userData, token: access_token });

    return userData; // caller uses userData.role for redirect
  }, []);

  // ── signup ─────────────────────────────────────────────────────────────────
  const signup = useCallback(async (name, email, password, role) => {
    const data = await api.signup(name, email, password, role);
    const { access_token, user: userData } = data;

    setSession({ token: access_token, ...userData });
    setUser({ ...userData, token: access_token });

    return userData;
  }, []);

  // ── logout ─────────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
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
