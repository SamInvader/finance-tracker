import { useEffect, useState } from "react";
import { Card, EmptyState, Field, LoadingState, Modal } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useToast } from "../context/ToastContext";

export default function Goals() {
  const { push } = useToast();
  const [goals, setGoals] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState<any>(null);
  const [hist, setHist] = useState<any[]>([]);
  const [form, setForm] = useState({ name: "", target: "", deadline: "", description: "", priority: "3", account_id: "" });

  async function load() {
    const [g, a] = await Promise.all([financeApi.goals(), financeApi.accounts()]);
    setGoals(g as any);
    setAccounts((a as any).accounts);
  }
  useEffect(() => { load(); }, []);

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h1 className="text-2xl font-bold">Savings goals</h1>
        <button className="btn-primary" onClick={() => setOpen(true)}>New goal</button>
      </div>
      {goals.length === 0 ? <EmptyState title="No goals yet" body="Track an emergency fund, laptop, or school expenses." /> : (
        <div className="grid gap-3 md:grid-cols-2">
          {goals.map((g) => (
            <Card key={g.id}>
              <h2 className="font-semibold">{g.name}</h2>
              <p className="text-sm text-slate-500">{formatMoney(g.current)} of {formatMoney(g.target)} · {g.percent}%</p>
              <div className="my-2 h-2 rounded-full bg-slate-200 dark:bg-slate-800"><div className="h-full rounded-full bg-teal-600" style={{ width: `${Math.min(g.percent, 100)}%` }} /></div>
              <p className="text-xs text-slate-500">Remaining {formatMoney(g.remaining)} {g.deadline && `· due ${g.deadline}`}</p>
              {g.required_monthly != null && <p className="text-xs">Need about {formatMoney(g.required_monthly)} / month or {formatMoney(g.required_weekly)} / week.</p>}
              <div className="mt-3 flex gap-2">
                <button className="btn-secondary text-xs" onClick={async () => { const amt = prompt("Deposit amount"); if (!amt) return; await financeApi.depositGoal(g.id, { amount: Number(amt) }); push("Deposited"); load(); }}>Deposit</button>
                <button className="btn-secondary text-xs" onClick={async () => { const amt = prompt("Withdraw amount"); if (!amt) return; await financeApi.withdrawGoal(g.id, { amount: Number(amt) }); push("Withdrawn"); load(); }}>Withdraw</button>
                <button className="btn-secondary text-xs" onClick={async () => { setActive(g); setHist(await financeApi.goalHistory(g.id) as any); }}>History</button>
                <button className="text-xs text-rose-700" onClick={async () => { await financeApi.deleteGoal(g.id); load(); }}>Delete</button>
              </div>
            </Card>
          ))}
        </div>
      )}
      <Modal open={open} onClose={() => setOpen(false)} title="New goal">
        <form className="space-y-3" onSubmit={async (e) => { e.preventDefault(); await financeApi.createGoal({ ...form, target: Number(form.target), account_id: form.account_id || null, priority: Number(form.priority) }); push("Goal created"); setOpen(false); load(); }}>
          <Field label="Name"><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></Field>
          <Field label="Target"><input className="input" value={form.target} onChange={(e) => setForm({ ...form, target: e.target.value })} required /></Field>
          <Field label="Deadline"><input className="input" type="date" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} /></Field>
          <Field label="Account"><select className="input" value={form.account_id} onChange={(e) => setForm({ ...form, account_id: e.target.value })}><option value="">None</option>{accounts.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}</select></Field>
          <Field label="Description"><textarea className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></Field>
          <button className="btn-primary w-full">Save</button>
        </form>
      </Modal>
      <Modal open={!!active} onClose={() => setActive(null)} title={active?.name || "History"}>
        <ul className="text-sm">{hist.map((h) => <li key={h.id} className="flex justify-between py-1"><span>{h.date} · {h.kind}</span><span>{formatMoney(h.amount)}</span></li>)}</ul>
      </Modal>
    </div>
  );
}
