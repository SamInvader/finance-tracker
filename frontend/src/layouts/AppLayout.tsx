import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  BarChart3,
  Bell,
  CalendarDays,
  CreditCard,
  Flag,
  LayoutDashboard,
  LogOut,
  PiggyBank,
  Repeat,
  Search,
  Settings,
  TrendingUp,
  Upload,
  Wallet,
  Menu,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { financeApi } from "../services/finance";
import { classNames } from "../utils/format";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/accounts", label: "Accounts", icon: Wallet },
  { to: "/transactions", label: "Transactions", icon: CreditCard },
  { to: "/budgets", label: "Budgets", icon: BarChart3 },
  { to: "/goals", label: "Goals", icon: Flag },
  { to: "/bills", label: "Bills", icon: CalendarDays },
  { to: "/subscriptions", label: "Subscriptions", icon: Repeat },
  { to: "/recurring", label: "Recurring", icon: Repeat },
  { to: "/debts", label: "Debts", icon: TrendingUp },
  { to: "/net-worth", label: "Net worth", icon: PiggyBank },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/forecast", label: "Forecast", icon: TrendingUp },
  { to: "/calendar", label: "Calendar", icon: CalendarDays },
  { to: "/insights", label: "Insights", icon: Search },
  { to: "/import-export", label: "Import / Export", icon: Upload },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [notifs, setNotifs] = useState<any[]>([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [q, setQ] = useState("");
  const navigate = useNavigate();
  const loc = useLocation();

  useEffect(() => {
    setOpen(false);
  }, [loc.pathname]);

  useEffect(() => {
    financeApi.notifications().then((d: any) => {
      setNotifs(d.items);
      setUnread(d.unread);
    }).catch(() => {});
  }, [loc.pathname]);

  const nav = (
    <nav className="flex flex-col gap-1 p-3" aria-label="Main">
      {NAV.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          className={({ isActive }) =>
            classNames(
              "flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium",
              isActive
                ? "bg-teal-700 text-white"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            )
          }
        >
          <item.icon size={18} aria-hidden />
          {item.label}
        </NavLink>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[16rem_1fr]">
      <aside className="hidden border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 lg:block">
        <div className="flex h-16 items-center px-5 text-lg font-bold tracking-tight">Ledgerly</div>
        {nav}
      </aside>
      {open && (
        <div className="fixed inset-0 z-30 lg:hidden">
          <button className="absolute inset-0 bg-slate-950/40" aria-label="Close menu" onClick={() => setOpen(false)} />
          <aside className="relative z-40 h-full w-72 bg-white dark:bg-slate-900">
            <div className="flex h-16 items-center justify-between px-4 font-bold">
              Ledgerly
              <button className="btn-secondary px-2" onClick={() => setOpen(false)} aria-label="Close">
                <X size={18} />
              </button>
            </div>
            {nav}
          </aside>
        </div>
      )}
      <div className="flex min-w-0 flex-col">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-slate-200 bg-white/90 px-4 backdrop-blur dark:border-slate-800 dark:bg-slate-950/90">
          <button className="btn-secondary px-2 lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu">
            <Menu size={18} />
          </button>
          <form
            className="flex min-w-0 flex-1 items-center gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              if (q.trim()) navigate(`/search?q=${encodeURIComponent(q.trim())}`);
            }}
          >
            <Search size={16} className="shrink-0 text-slate-400" aria-hidden />
            <input
              className="input border-0 bg-transparent px-0 shadow-none"
              placeholder="Search transactions, bills, goals…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              aria-label="Global search"
            />
          </form>
          <div className="relative">
            <button className="btn-secondary px-3" onClick={() => setShowNotifs((v) => !v)} aria-label="Notifications">
              <Bell size={18} />
              {unread > 0 && <span className="rounded-full bg-rose-600 px-1.5 text-[10px] text-white">{unread}</span>}
            </button>
            {showNotifs && (
              <div className="absolute right-0 mt-2 w-80 rounded-2xl border border-slate-200 bg-white p-2 shadow-card dark:border-slate-700 dark:bg-slate-900">
                <div className="mb-2 flex items-center justify-between px-2">
                  <p className="text-sm font-semibold">Notifications</p>
                  <button
                    className="text-xs text-teal-700"
                    onClick={async () => {
                      await financeApi.readAllNotifs();
                      setUnread(0);
                      setNotifs((xs) => xs.map((n) => ({ ...n, is_read: true })));
                    }}
                  >
                    Mark all read
                  </button>
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {notifs.length === 0 && <p className="px-2 py-6 text-center text-sm text-slate-500">No notifications yet.</p>}
                  {notifs.map((n) => (
                    <button
                      key={n.id}
                      className={classNames("mb-1 w-full rounded-xl px-3 py-2 text-left text-sm", !n.is_read && "bg-teal-50 dark:bg-teal-950/40")}
                      onClick={async () => {
                        await financeApi.readNotif(n.id);
                        setNotifs((xs) => xs.map((x) => (x.id === n.id ? { ...x, is_read: true } : x)));
                        setUnread((u) => Math.max(u - 1, 0));
                      }}
                    >
                      <p className="font-medium">{n.title}</p>
                      <p className="text-xs text-slate-500">{n.body}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          <span className="hidden text-sm text-slate-500 sm:inline">{user?.name}</span>
          <button className="btn-secondary px-3" onClick={logout} aria-label="Log out">
            <LogOut size={16} />
          </button>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 p-4 pb-24 lg:pb-8">
          <Outlet />
        </main>
        <nav className="fixed bottom-0 left-0 right-0 z-20 grid grid-cols-5 border-t border-slate-200 bg-white py-2 dark:border-slate-800 dark:bg-slate-900 lg:hidden" aria-label="Mobile">
          {[NAV[0], NAV[1], NAV[2], NAV[3], NAV[15]].map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"} className={({ isActive }) => classNames("flex flex-col items-center gap-1 text-[11px]", isActive ? "text-teal-700" : "text-slate-500")}>
              <item.icon size={18} />
              {item.label.split(" ")[0]}
            </NavLink>
          ))}
        </nav>
      </div>
    </div>
  );
}
