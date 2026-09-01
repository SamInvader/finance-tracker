import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { authService } from "../services/auth";
import type { Preferences, User } from "../types";
import { useTheme } from "./ThemeContext";

interface AuthState {
  user: User | null;
  preferences: Preferences | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, confirm: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
  setPreferences: (p: Preferences) => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [preferences, setPreferences] = useState<Preferences | null>(null);
  const [loading, setLoading] = useState(true);
  const { setTheme } = useTheme();

  const apply = (u: User, p: Preferences, token?: string) => {
    if (token) localStorage.setItem("ledgerly_token", token);
    setUser(u);
    setPreferences(p);
    if (p?.theme) setTheme(p.theme);
  };

  const refresh = async () => {
    const token = localStorage.getItem("ledgerly_token");
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const data = await authService.me();
      apply(data.user, data.preferences);
    } catch {
      localStorage.removeItem("ledgerly_token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      user,
      preferences,
      loading,
      async login(email, password) {
        const data = await authService.login({ email, password });
        apply(data.user, data.preferences, data.token);
      },
      async register(name, email, password, confirm) {
        const data = await authService.register({ name, email, password, confirm_password: confirm });
        apply(data.user, data.preferences, data.token);
      },
      logout() {
        localStorage.removeItem("ledgerly_token");
        setUser(null);
        setPreferences(null);
      },
      refresh,
      setPreferences,
    }),
    [user, preferences, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("AuthProvider required");
  return ctx;
}
