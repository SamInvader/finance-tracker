import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Field } from "../components/ui";

export default function Register() {
  const { register } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(name, email, password, confirm);
    } catch (err: any) {
      setError(err.message || "Could not register");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <form onSubmit={onSubmit} className="card w-full max-w-md space-y-4">
        <div>
          <p className="text-sm font-semibold text-teal-700">Ledgerly</p>
          <h1 className="text-2xl font-bold">Create your account</h1>
        </div>
        <Field label="Name">
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} required />
        </Field>
        <Field label="Email">
          <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </Field>
        <Field label="Password">
          <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
        </Field>
        <Field label="Confirm password">
          <input className="input" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
        </Field>
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>
          {busy ? "Creating…" : "Create account"}
        </button>
        <p className="text-center text-sm text-slate-500">
          Already have an account? <Link className="font-semibold text-teal-700" to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
