import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Field } from "../components/ui";

export default function Login() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || "Could not sign in");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <form onSubmit={onSubmit} className="card w-full max-w-md space-y-4">
        <div>
          <p className="text-sm font-semibold text-teal-700">Ledgerly</p>
          <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
          <p className="text-sm text-slate-500">Sign in to your personal finance workspace.</p>
        </div>
        <Field label="Email">
          <input className="input" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </Field>
        <Field label="Password">
          <input className="input" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </Field>
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className="text-center text-sm text-slate-500">
          No account? <Link className="font-semibold text-teal-700" to="/register">Create one</Link>
        </p>
        <p className="text-center text-xs text-slate-400">Demo: demo@ledgerly.local / DemoPass123! (after seeding)</p>
      </form>
    </div>
  );
}
