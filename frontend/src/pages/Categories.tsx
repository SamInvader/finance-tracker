import { useEffect, useState } from "react";
import { Card, Field, Modal } from "../components/ui";
import { financeApi } from "../services/finance";
import { useToast } from "../context/ToastContext";

const ICONS = ["circle", "utensils", "bus", "smartphone", "home", "heart-pulse", "film", "gift", "briefcase"];

export default function Categories() {
  const { push } = useToast();
  const [items, setItems] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", kind: "expense", color: "#0f766e", icon: "circle", parent_id: "" });
  async function load() { setItems(await financeApi.categories() as any); }
  useEffect(() => { load(); }, []);
  return (
    <div className="space-y-4">
      <div className="flex justify-between"><h1 className="text-2xl font-bold">Categories</h1><button className="btn-primary" onClick={() => setOpen(true)}>Add</button></div>
      <div className="grid gap-2 md:grid-cols-2">
        {items.map((c) => (
          <Card key={c.id}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full" style={{ background: c.color }} aria-hidden />
                <div>
                  <p className="font-medium">{c.name}</p>
                  <p className="text-xs capitalize text-slate-500">{c.kind}{c.parent_id ? " · subcategory" : ""}</p>
                </div>
              </div>
              <button className="text-xs text-rose-700" onClick={async () => { try { await financeApi.deleteCategory(c.id); load(); } catch (e: any) { push(e.message, "err"); } }}>Delete</button>
            </div>
          </Card>
        ))}
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title="New category">
        <form className="space-y-3" onSubmit={async (e) => { e.preventDefault(); await financeApi.createCategory({ ...form, parent_id: form.parent_id ? Number(form.parent_id) : null }); setOpen(false); load(); }}>
          <Field label="Name"><input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></Field>
          <Field label="Kind"><select className="input" value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}><option value="expense">Expense</option><option value="income">Income</option></select></Field>
          <Field label="Color"><input className="input" type="color" value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} /></Field>
          <Field label="Icon"><select className="input" value={form.icon} onChange={(e) => setForm({ ...form, icon: e.target.value })}>{ICONS.map((i) => <option key={i}>{i}</option>)}</select></Field>
          <Field label="Parent"><select className="input" value={form.parent_id} onChange={(e) => setForm({ ...form, parent_id: e.target.value })}><option value="">None</option>{items.filter((c) => c.kind === form.kind).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select></Field>
          <button className="btn-primary w-full">Save</button>
        </form>
      </Modal>
    </div>
  );
}
