import { useState } from "react";
import { Card, Field } from "../components/ui";
import { api } from "../services/api";
import { financeApi } from "../services/finance";
import { useToast } from "../context/ToastContext";

export default function ImportExport() {
  const { push } = useToast();
  const [csv, setCsv] = useState("");
  const [mapping, setMapping] = useState({ date: "date", amount: "amount", description: "description", category: "category", account: "account", type: "type" });
  const [preview, setPreview] = useState<any>(null);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [accountId, setAccountId] = useState("");
  useState(() => { financeApi.accounts().then((d: any) => { setAccounts(d.accounts); setAccountId(String(d.accounts[0]?.id || "")); }); });

  async function download(kind: string) {
    const res = await api.get(`/api/export/${kind}`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${kind}.csv`;
    a.click();
  }

  async function downloadBackup() {
    const data = await financeApi.backup();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "ledgerly-backup.json";
    a.click();
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Import & export</h1>
      <Card title="CSV export">
        <div className="flex flex-wrap gap-2">
          {["transactions", "accounts", "budgets", "goals", "debts"].map((k) => (
            <button key={k} className="btn-secondary capitalize" onClick={() => download(k)}>{k}</button>
          ))}
        </div>
      </Card>
      <Card title="CSV import">
        <Field label="Paste CSV"><textarea className="input min-h-[120px] font-mono text-xs" value={csv} onChange={(e) => setCsv(e.target.value)} /></Field>
        <div className="mt-2 grid gap-2 sm:grid-cols-3">
          {Object.keys(mapping).map((k) => (
            <Field key={k} label={`${k} column`}>
              <input className="input" value={(mapping as any)[k]} onChange={(e) => setMapping({ ...mapping, [k]: e.target.value })} />
            </Field>
          ))}
        </div>
        <button className="btn-secondary mt-3" onClick={async () => setPreview(await financeApi.importPreview({ csv, mapping }))}>Preview</button>
        {preview && (
          <div className="mt-3 text-sm">
            <p>{preview.valid_count} valid · {preview.invalid_count} invalid</p>
            {preview.invalid?.slice(0, 5).map((e: any) => <p key={e.row} className="text-rose-600">Row {e.row}: {e.error}</p>)}
            <Field label="Default account">
              <select className="input" value={accountId} onChange={(e) => setAccountId(e.target.value)}>
                {accounts.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </Field>
            <button className="btn-primary mt-2" onClick={async () => { await financeApi.importCommit({ rows: preview.valid, account_id: Number(accountId) }); push("Imported"); }}>Confirm import</button>
          </div>
        )}
      </Card>
      <Card title="Full JSON backup">
        <div className="flex gap-2">
          <button className="btn-secondary" onClick={downloadBackup}>Download backup</button>
          <label className="btn-secondary cursor-pointer">
            Restore…
            <input type="file" accept="application/json" className="hidden" onChange={async (e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              const text = await file.text();
              try {
                const backup = JSON.parse(text);
                await financeApi.restore(backup, true);
                push("Restore complete");
              } catch (err: any) {
                push(err.message || "Invalid backup", "err");
              }
            }} />
          </label>
        </div>
        <p className="mt-2 text-xs text-slate-500">Restore replaces this user's financial data after validating the file version and required collections.</p>
      </Card>
    </div>
  );
}
