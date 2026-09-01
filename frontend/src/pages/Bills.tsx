import { useEffect, useState } from "react";
import { Card, EmptyState, Field, Modal } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useToast } from "../context/ToastContext";

export default function Bills() {
  const { push } = useToast();
  const [items, setItems] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", amount: "", due_date: "", frequency: "monthly" });
  async function load() { setItems(await financeApi.bills() as any); }
  useEffect(() => { load(); }, []);
  return (
    <div className="space-y-4">
      <div className="flex justify-between"><h1 className="text-2xl font-bold">Bills</h1><button className="btn-primary" onClick={() => setOpen(true)}>Add bill</button></div>
      {items.length === 0 ? <EmptyState title="No bills" body="Track rent, electricity, and other due dates." /> : (
        <div className="grid gap-3 md:grid-cols-2">
          {items.map((b) => (
            <Card key={b.id}>
              <div className="flex justify-between"><h2 className="font-semibold">{b.name}</h2><span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs capitalize dark:bg-slate-800">{b.status.replace("_", " ")}</span></div>
              <p className="mt-1 tabular-nums">{formatMoney(b.amount)} due {b.due_date}</p>
              <div className="mt-3 flex gap-2">
                <button className="btn-secondary text-xs" onClick={async () => { await financeApi.updateBill(b.id, { status: "paid" }); push("Marked paid"); load(); }}>Mark paid</button>
                <button className="text-xs text-rose-700" onClick={async () => { await financeApi.deleteBill(b.id); load(); }}>Delete</button>
              </div>
            </Card>
          ))}
        </div>
      )}
      <Modal open={open} onClose={() => setOpen(false)} title="New bill">
        <form className="space-y-3" onSubmit={async (e) => { e.preventDefault(); await financeApi.createBill({ ...form, amount: Number(form.amount) }); setOpen(false); push("Bill added"); load(); }}>
          <Field label="Name"><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></Field>
          <Field label="Amount"><input className="input" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required /></Field>
          <Field label="Due date"><input className="input" type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} required /></Field>
          <Field label="Frequency"><select className="input" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })}><option>monthly</option><option>weekly</option><option>yearly</option></select></Field>
          <button className="btn-primary w-full">Save</button>
        </form>
      </Modal>
    </div>
  );
}
