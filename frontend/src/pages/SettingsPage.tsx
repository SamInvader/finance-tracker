import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Card, Field } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { authService } from "../services/auth";
import { useToast } from "../context/ToastContext";

const WIDGETS = ["summary", "cashflow", "spending", "budgets", "recent", "upcoming", "health"];

export default function SettingsPage() {
  const { user, preferences, setPreferences } = useAuth();
  const { theme, setTheme } = useTheme();
  const { push } = useToast();
  const [name, setName] = useState(user?.name || "");
  const [widgets, setWidgets] = useState<string[]>(preferences?.dashboard_widgets || WIDGETS);
  const [range, setRange] = useState(preferences?.default_time_range || "30d");
  const [pw, setPw] = useState({ current_password: "", new_password: "", confirm_password: "" });

  async function save(e: FormEvent) {
    e.preventDefault();
    const data = await authService.updateMe({ name, theme, default_time_range: range, dashboard_widgets: widgets });
    setPreferences(data.preferences);
    push("Settings saved");
  }

  function toggle(id: string) {
    setWidgets((w) => (w.includes(id) ? w.filter((x) => x !== id) : [...w, id]));
  }
  function move(id: string, dir: number) {
    const i = widgets.indexOf(id);
    if (i < 0) return;
    const j = i + dir;
    if (j < 0 || j >= widgets.length) return;
    const next = [...widgets];
    [next[i], next[j]] = [next[j], next[i]];
    setWidgets(next);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Settings</h1>
      <Card title="Profile">
        <form className="space-y-3" onSubmit={save}>
          <Field label="Name"><input className="input" value={name} onChange={(e) => setName(e.target.value)} /></Field>
          <p className="text-sm text-slate-500">{user?.email}</p>
          <Field label="Theme">
            <select className="input" value={theme} onChange={(e) => setTheme(e.target.value as any)}>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
          </Field>
          <Field label="Default dashboard range">
            <select className="input" value={range} onChange={(e) => setRange(e.target.value)}>
              <option value="7d">7 days</option>
              <option value="30d">30 days</option>
              <option value="3m">3 months</option>
              <option value="6m">6 months</option>
              <option value="1y">1 year</option>
            </select>
          </Field>
          <fieldset>
            <legend className="label">Dashboard widgets</legend>
            {WIDGETS.map((id) => (
              <div key={id} className="mb-1 flex items-center gap-2 text-sm">
                <input type="checkbox" checked={widgets.includes(id)} onChange={() => toggle(id)} id={id} />
                <label htmlFor={id} className="capitalize">{id}</label>
                <button type="button" className="text-xs" onClick={() => move(id, -1)}>Up</button>
                <button type="button" className="text-xs" onClick={() => move(id, 1)}>Down</button>
              </div>
            ))}
          </fieldset>
          <button className="btn-primary">Save preferences</button>
        </form>
      </Card>
      <Card title="Password">
        <form className="space-y-3" onSubmit={async (e) => { e.preventDefault(); await authService.changePassword(pw); push("Password changed"); }}>
          <Field label="Current"><input className="input" type="password" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} /></Field>
          <Field label="New"><input className="input" type="password" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} /></Field>
          <Field label="Confirm"><input className="input" type="password" value={pw.confirm_password} onChange={(e) => setPw({ ...pw, confirm_password: e.target.value })} /></Field>
          <button className="btn-primary">Update password</button>
        </form>
      </Card>
      <Link className="text-sm font-semibold text-teal-700" to="/categories">Manage categories</Link>
    </div>
  );
}
