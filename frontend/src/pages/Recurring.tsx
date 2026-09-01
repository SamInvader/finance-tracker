import { useEffect, useState } from "react";
import { Card, EmptyState, Field, Modal } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useToast } from "../context/ToastContext";

export default function Recurring() {
  const { push } = useToast();
  const [items, setItems] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ description: "", amount: "", type: "expense", frequency: "monthly", account_id: "", category_id: "", start_date: new Date().toISOString().slice(0, 10) });
  async function load() {
    const [r, a, c] = await Promise.all([financeApi.recurring(), financeApi.accounts(), financeApi.categories()]);
    setItems(r as any);
    setAccounts((a as any).accounts);
    setCategories(c as any);
  }
  useEffect(() => { load(); }, []);
  return (
    <div className="space-y-4">
      <div className="flex justify-between"><h1 className="text-2xl font-bold">Recurring transactions</h1><button className="btn-primary" onClick={() => setOpen(true)}>Add</button></div>
      {items.length === 0 ? <EmptyState title="None yet" body="Salary, rent, and data subscriptions can be generated automatically without duplicates." /> : items.map((r) => (
        <Card key={r.id}>
          <div className="flex justify-between gap-2">
            <div>
              <h2 className="font-semibold">{r.description}</h2>
              <p className="text-sm text-slate-500">{formatMoney(r.amount)} · {r.type} · {r.frequency} · next {r.next_occurrence} · {r.account_name}</p>
            </div>
            <div className="flex gap-2">
              <button className="btn-secondary text-xs" onClick={async () => { await financeApi.updateRecurring(r.id, { is_active: !r.is_active }); load(); }}>{r.is_active ? "Pause" : "Resume"}</button>
              <button className="text-xs text-rose-700" onClick={async () => { await financeApi.deleteRecurring(r.id); load(); }}>Delete</button>
            </div>
          </div>
        </Card>
      ))}
      <Modal open={open} onClose={() => setOpen(false)} title="New recurring item">
        <form className="space-y-3" onSubmit={async (e) => { e.preventDefault(); await financeApi.createRecurring({ ...form, amount: Number(form.amount), account_id: Number(form.account_id), category_id: form.category_id ? Number(form.category_id) : null }); setOpen(false); push("Created"); load(); }}>
          <Field label="Description"><input className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required /></Field>
          <Field label="Amount"><input className="input" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></Field>
          <Field label="Type"><select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}><option>expense</option><option>income</option></select></Field>
          <Field label="Frequency"><select className="input" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}><option>daily</option><option>weekly</option><option>monthly</option><option>yearly</option></select></Field>
          <Field label="Account"><select className="input" value={form.account_id} onChange={(e) => setForm({ ...form, account_id: e.target.value })} required><option value="">Select</option>{accounts.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</select></Field>
          <Field label="Category"><select className="input" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })}><option value="">None</option>{categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></Field>
          <Field label="Start date"><input className="input" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} /></Field>
          <button className="btn-primary w-full">Save</button>
        </form>
      </Modal>
    </div>
  );
}
