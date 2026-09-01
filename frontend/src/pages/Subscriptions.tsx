import { useEffect, useState } from "react";
import { Card, EmptyState, Field, Modal } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useToast } from "../context/ToastContext";

export default function Subscriptions() {
  const { push } = useToast();
  const [data, setData] = useState<any>(null);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", amount: "", billing_cycle: "monthly", next_billing_date: "", status: "active" });
  async function load() { setData(await financeApi.subscriptions()); }
  useEffect(() => { load(); }, []);
  if (!data) return null;
  return (
    <div className="space-y-4">
      <div className="flex justify-between"><h1 className="text-2xl font-bold">Subscriptions</h1><button className="btn-primary" onClick={() => setOpen(true)}>Add</button></div>
      <div className="grid gap-3 sm:grid-cols-2">
        <Card><p className="text-sm text-slate-500">Monthly cost</p><p className="text-2xl font-semibold">{formatMoney(data.monthly_total)}</p></Card>
        <Card><p className="text-sm text-slate-500">Annual cost</p><p className="text-2xl font-semibold">{formatMoney(data.annual_total)}</p></Card>
      </div>
      {data.items.length === 0 ? <EmptyState title="No subscriptions" body="Track Spotify, iCloud, and other recurring services." /> : data.items.map((s: any) => (
        <Card key={s.id}>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div><h2 className="font-semibold">{s.name}</h2><p className="text-sm text-slate-500">{formatMoney(s.amount)} / {s.billing_cycle} · next {s.next_billing_date} · {s.status}</p></div>
            <div className="flex gap-2">
              {["active", "paused", "cancelled"].map((st) => (
                <button key={st} className="btn-secondary text-xs" onClick={async () => { await financeApi.updateSub(s.id, { status: st }); load(); }}>{st}</button>
              ))}
              <button className="text-xs text-rose-700" onClick={async () => { await financeApi.deleteSub(s.id); load(); }}>Delete</button>
            </div>
          </div>
        </Card>
      ))}
      <Modal open={open} onClose={() => setOpen(false)} title="New subscription">
        <form className="space-y-3" onSubmit={async (e) => { e.preventDefault(); await financeApi.createSub({ ...form, amount: Number(form.amount) }); setOpen(false); push("Added"); load(); }}>
          <Field label="Service"><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></Field>
          <Field label="Cost"><input className="input" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></Field>
          <Field label="Cycle"><select className="input" value={form.billing_cycle} onChange={(e) => setForm({ ...form, billing_cycle: e.target.value })}><option>monthly</option><option>weekly</option><option>yearly</option></select></Field>
          <Field label="Next billing"><input className="input" type="date" value={form.next_billing_date} onChange={(e) => setForm({ ...form, next_billing_date: e.target.value })} required /></Field>
          <button className="btn-primary w-full">Save</button>
        </form>
      </Modal>
    </div>
  );
}
