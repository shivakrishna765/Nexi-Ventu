import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api } from "../utils/api";
import { getSession, setSession, clearSession } from "../utils/session";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  // Rehydrate from localStorage on mount
  useEffect(() => {
    const session = getSession();
    if (session?.token) {
      api.getProfile()
        .then((profile) => {
          setUser({ ...profile, token: session.token });
        })
        .catch(() => {
          clearSession();
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await api.login(email, password);
    const session = { token: data.access_token, ...data.user };
    setSession(session);
    setUser(session);
    return data.user;
  }, []);

  const signup = useCallback(async (name, email, password, role) => {
    const data = await api.signup(name, email, password, role);
    const session = { token: data.access_token, ...data.user };
    setSession(session);
    setUser(session);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const updateUser = useCallback(async (updates) => {
    const updated = await api.updateProfile(updates);
    const session = { ...getSession(), ...updated };
    setSession(session);
    setUser(session);
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
