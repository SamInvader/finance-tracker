import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card, Field } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useTheme } from "../context/ThemeContext";

export default function NetWorth() {
  const [data, setData] = useState<any>(null);
  const { resolved } = useTheme();
  const [asset, setAsset] = useState({ name: "", value: "", kind: "investment" });
  const [liab, setLiab] = useState({ name: "", value: "", kind: "other" });
  async function load() { setData(await financeApi.netWorth()); }
  useEffect(() => { load(); }, []);
  if (!data) return null;
  const axis = resolved === "dark" ? "#94a3b8" : "#64748b";
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Net worth</h1>
      <p className="text-sm text-slate-500">Assets minus liabilities. Account balances, extra assets, debts, and other liabilities are included.</p>
      <div className="grid gap-3 sm:grid-cols-3">
        <Card><p className="text-sm text-slate-500">Current</p><p className="text-2xl font-semibold">{formatMoney(data.current)}</p></Card>
        <Card><p className="text-sm text-slate-500">Previous snapshot</p><p className="text-2xl font-semibold">{data.previous == null ? "—" : formatMoney(data.previous)}</p></Card>
        <Card><p className="text-sm text-slate-500">Change</p><p className="text-2xl font-semibold">{formatMoney(data.change)} {data.percent_change != null && `(${data.percent_change}%)`}</p></Card>
      </div>
      <Card title="History">
        <div className="h-64">
          <ResponsiveContainer>
            <LineChart data={data.history}>
              <CartesianGrid strokeDasharray="3 3" stroke={axis} opacity={0.2} />
              <XAxis dataKey="date" tick={{ fill: axis, fontSize: 11 }} />
              <YAxis tick={{ fill: axis, fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatMoney(v)} />
              <Line type="monotone" dataKey="net_worth" stroke="#0f766e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Add asset">
          <form className="space-y-2" onSubmit={async (e) => { e.preventDefault(); await financeApi.createAsset({ ...asset, value: Number(asset.value) }); load(); }}>
            <Field label="Name"><input className="input" value={asset.name} onChange={(e) => setAsset({ ...asset, name: e.target.value })} required /></Field>
            <Field label="Value"><input className="input" value={asset.value} onChange={(e) => setAsset({ ...asset, value: e.target.value })} required /></Field>
            <button className="btn-primary">Add</button>
          </form>
          <ul className="mt-3 text-sm">{data.assets_list.map((a: any) => <li key={a.id} className="flex justify-between py-1">{a.name}<span>{formatMoney(a.value)} <button className="text-rose-700" onClick={async () => { await financeApi.deleteAsset(a.id); load(); }}>×</button></span></li>)}</ul>
        </Card>
        <Card title="Add liability">
          <form className="space-y-2" onSubmit={async (e) => { e.preventDefault(); await financeApi.createLiability({ ...liab, value: Number(liab.value) }); load(); }}>
            <Field label="Name"><input className="input" value={liab.name} onChange={(e) => setLiab({ ...liab, name: e.target.value })} required /></Field>
            <Field label="Value"><input className="input" value={liab.value} onChange={(e) => setLiab({ ...liab, value: e.target.value })} required /></Field>
            <button className="btn-primary">Add</button>
          </form>
          <ul className="mt-3 text-sm">{data.liabilities_list.map((a: any) => <li key={a.id} className="flex justify-between py-1">{a.name}<span>{formatMoney(a.value)} <button className="text-rose-700" onClick={async () => { await financeApi.deleteLiability(a.id); load(); }}>×</button></span></li>)}</ul>
        </Card>
      </div>
    </div>
  );
}
