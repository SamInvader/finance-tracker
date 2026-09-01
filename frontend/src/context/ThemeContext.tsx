import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

type Theme = "light" | "dark" | "system";

const ThemeContext = createContext<{
  theme: Theme;
  setTheme: (t: Theme) => void;
  resolved: "light" | "dark";
}>({ theme: "system", setTheme: () => {}, resolved: "light" });

function resolve(theme: Theme): "light" | "dark" {
  if (theme === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return theme;
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => (localStorage.getItem("ledgerly_theme") as Theme) || "system");
  const [resolved, setResolved] = useState<"light" | "dark">(() => (typeof window === "undefined" ? "light" : resolve(theme)));

  useEffect(() => {
    const apply = () => {
      const next = resolve(theme);
      setResolved(next);
      document.documentElement.classList.toggle("dark", next === "dark");
    };
    apply();
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = () => theme === "system" && apply();
    mq.addEventListener("change", listener);
    return () => mq.removeEventListener("change", listener);
  }, [theme]);

  const setTheme = (t: Theme) => {
    localStorage.setItem("ledgerly_theme", t);
    setThemeState(t);
  };

  const value = useMemo(() => ({ theme, setTheme, resolved }), [theme, resolved]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
