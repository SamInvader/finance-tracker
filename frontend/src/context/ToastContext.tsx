import { createContext, useCallback, useContext, useState, type ReactNode } from "react";

type Toast = { id: number; title: string; tone?: "ok" | "err" };

const ToastContext = createContext<{ push: (title: string, tone?: "ok" | "err") => void }>({ push: () => {} });

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<Toast[]>([]);
  const push = useCallback((title: string, tone: "ok" | "err" = "ok") => {
    const id = Date.now() + Math.random();
    setItems((xs) => [...xs, { id, title, tone }]);
    setTimeout(() => setItems((xs) => xs.filter((t) => t.id !== id)), 3500);
  }, []);
  return (
    <ToastContext.Provider value={{ push }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-[min(100%-2rem,22rem)] flex-col gap-2">
        {items.map((t) => (
          <div
            key={t.id}
            role="status"
            className={`pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow-card ${
              t.tone === "err"
                ? "border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-100"
                : "border-slate-200 bg-white text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
            }`}
          >
            {t.title}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
