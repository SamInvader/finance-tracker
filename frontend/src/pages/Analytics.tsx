import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis, Pie, PieChart, Cell } from "recharts";
import { Card } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useTheme } from "../context/ThemeContext";

export default function Analytics() {
  const [period, setPeriod] = useState("30d");
  const [data, setData] = useState<any>(null);
  const { resolved } = useTheme();
  useEffect(() => { financeApi.analytics(period).then(setData); }, [period]);
  if (!data) return null;
  const axis = resolved === "dark" ? "#94a3b8" : "#64748b";
  const cmp = data.comparison;
  return (
    <div className="space-y-4">
      <div className="flex justify-between"><h1 className="text-2xl font-bold">Analytics</h1>
        <select className="input max-w-[10rem]" value={period} onChange={(e) => setPeriod(e.target.value)}>
          <option value="7d">7 days</option><option value="30d">30 days</option><option value="3m">3 months</option><option value="6m">6 months</option><option value="1y">1 year</option>
        </select>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Card><p className="text-sm text-slate-500">Income</p><p className="text-xl font-semibold">{formatMoney(data.this_month.income)}</p></Card>
        <Card><p className="text-sm text-slate-500">Expenses</p><p className="text-xl font-semibold">{formatMoney(data.this_month.expense)}</p></Card>
        <Card><p className="text-sm text-slate-500">Net</p><p className="text-xl font-semibold">{formatMoney(data.this_month.net)}</p></Card>
        <Card><p className="text-sm text-slate-500">Savings rate</p><p className="text-xl font-semibold">{data.this_month.savings_rate}%</p></Card>
      </div>
      <Card title="This month vs last month">
        <p className="text-sm">Income {formatMoney(cmp.current.income)} vs {formatMoney(cmp.previous.income)}. Expenses {formatMoney(cmp.current.expense)} vs {formatMoney(cmp.previous.expense)}.</p>
      </Card>
      <Card title="Cash flow">
        <div className="h-64">
          <ResponsiveContainer>
            <BarChart data={data.cashflow}>
              <CartesianGrid strokeDasharray="3 3" stroke={axis} opacity={0.2} />
              <XAxis dataKey="date" tick={{ fill: axis, fontSize: 10 }} hide={data.cashflow.length > 40} />
              <YAxis tick={{ fill: axis, fontSize: 11 }} />
              <Tooltip /><Legend />
              <Bar dataKey="income" fill="#0f766e" /><Bar dataKey="expense" fill="#be123c" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="By category">
          <div className="h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={data.spending_by_category} dataKey="value" nameKey="name" innerRadius={40} outerRadius={80}>
                  {data.spending_by_category.map((c: any) => <Cell key={c.name} fill={c.color} />)}
                </Pie>
                <Tooltip formatter={(v: number) => formatMoney(v)} /><Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card title="By account">
          <ul className="text-sm">{data.spending_by_account.map((a: any) => <li key={a.name} className="flex justify-between py-1"><span>{a.name}</span><span>{formatMoney(a.value)}</span></li>)}</ul>
        </Card>
      </div>
      <Card title="Income sources">
        <ul className="text-sm">{data.income_by_source.map((a: any) => <li key={a.name} className="flex justify-between py-1"><span>{a.name}</span><span>{formatMoney(a.value)}</span></li>)}</ul>
      </Card>
    </div>
  );
}
