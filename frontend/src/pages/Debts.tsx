import { useEffect, useState } from "react";
import { Card, EmptyState, Field, Modal } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useToast } from "../context/ToastContext";

export default function Debts() {
  const { push } = useToast();
  const [data, setData] = useState<any>(null);
  const [plan, setPlan] = useState<any>(null);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", lender: "", original: "", remaining: "", interest_rate: "0", minimum_payment: "", due_date: "" });
  async function load() {
    setData(await financeApi.debts());
    setPlan(await financeApi.payoff("snowball"));
  }
  useEffect(() => { load(); }, []);
  if (!data) return null;
  return (
    <div className="space-y-4">
      <div className="flex justify-between"><h1 className="text-2xl font-bold">Debts</h1><button className="btn-primary" onClick={() => setOpen(true)}>Add debt</button></div>
      <div className="grid gap-3 sm:grid-cols-2">
        <Card><p className="text-sm text-slate-500">Remaining</p><p className="text-2xl font-semibold">{formatMoney(data.total_remaining)}</p></Card>
        <Card><p className="text-sm text-slate-500">Paid</p><p className="text-2xl font-semibold">{formatMoney(data.total_paid)}</p></Card>
      </div>
      {data.items.length === 0 ? <EmptyState title="No debts tracked" body="Loans and hire-purchase balances live here." /> : data.items.map((d: any) => (
        <Card key={d.id}>
          <h2 className="font-semibold">{d.name} {d.lender && <span className="font-normal text-slate-500">· {d.lender}</span>}</h2>
          <p className="text-sm">{formatMoney(d.remaining)} remaining of {formatMoney(d.original)} · {d.percent}% paid · {d.interest_rate}% interest</p>
          <div className="my-2 h-2 rounded-full bg-slate-200 dark:bg-slate-800"><div className="h-full rounded-full bg-teal-700" style={{ width: `${d.percent}%` }} /></div>
          <button className="btn-secondary mt-2 text-xs" onClick={async () => { const amt = prompt("Payment amount"); if (!amt) return; await financeApi.payDebt(d.id, { amount: Number(amt) }); push("Payment recorded"); load(); }}>Record payment</button>
        </Card>
      ))}
      {plan && (
        <Card title="Payoff estimate">
          <div className="mb-2 flex gap-2">
            <button className="btn-secondary text-xs" onClick={async () => setPlan(await financeApi.payoff("snowball"))}>Snowball</button>
            <button className="btn-secondary text-xs" onClick={async () => setPlan(await financeApi.payoff("avalanche"))}>Avalanche</button>
          </div>
          <p className="text-sm">Method: {plan.method}. {plan.months ? `About ${plan.months} months.` : "Not enough payment data."} Estimated interest {formatMoney(plan.total_interest_estimate)}.</p>
          <p className="mt-2 text-xs text-slate-500">{plan.disclaimer}</p>
        </Card>
      )}
      <Modal open={open} onClose={() => setOpen(false)} title="New debt">
        <form className="space-y-3" onSubmit={async (e) => { e.preventDefault(); await financeApi.createDebt({ ...form, original: Number(form.original), remaining: Number(form.remaining || form.original), interest_rate: Number(form.interest_rate), minimum_payment: Number(form.minimum_payment || 0) }); setOpen(false); load(); }}>
          <Field label="Name"><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></Field>
          <Field label="Lender"><input className="input" value={form.lender} onChange={(e) => setForm({ ...form, lender: e.target.value })} /></Field>
          <Field label="Original"><input className="input" value={form.original} onChange={(e) => setForm({ ...form, original: e.target.value })} required /></Field>
          <Field label="Remaining"><input className="input" value={form.remaining} onChange={(e) => setForm({ ...form, remaining: e.target.value })} /></Field>
          <Field label="Interest rate %"><input className="input" value={form.interest_rate} onChange={(e) => setForm({ ...form, interest_rate: e.target.value })} /></Field>
          <Field label="Minimum payment"><input className="input" value={form.minimum_payment} onChange={(e) => setForm({ ...form, minimum_payment: e.target.value })} /></Field>
          <Field label="Due date"><input className="input" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></Field>
          <button className="btn-primary w-full">Save</button>
        </form>
      </Modal>
    </div>
  );
}
