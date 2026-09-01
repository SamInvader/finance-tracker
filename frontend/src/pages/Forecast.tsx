import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { Card } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";
import { useTheme } from "../context/ThemeContext";

export default function Forecast() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<any>(null);
  const { resolved } = useTheme();
  useEffect(() => { financeApi.forecast(days).then(setData); }, [days]);
  if (!data) return null;
  const axis = resolved === "dark" ? "#94a3b8" : "#64748b";
  return (
    <div className="space-y-4">
      <div className="flex justify-between"><h1 className="text-2xl font-bold">Cash-flow forecast</h1>
        <div className="flex gap-2">{[7, 30, 90].map((d) => <button key={d} className={days === d ? "btn-primary text-xs" : "btn-secondary text-xs"} onClick={() => setDays(d)}>{d} days</button>)}</div>
      </div>
      <p className="text-sm text-slate-500">{data.disclaimer}</p>
      <div className="grid gap-3 sm:grid-cols-3">
        <Card><p className="text-sm text-slate-500">Opening</p><p className="text-xl font-semibold">{formatMoney(data.opening_balance)}</p></Card>
        <Card><p className="text-sm text-slate-500">Projected end</p><p className="text-xl font-semibold">{formatMoney(data.projected_end_balance)}</p></Card>
        <Card><p className="text-sm text-slate-500">Lowest projected</p><p className="text-xl font-semibold">{formatMoney(data.lowest_projected_balance)}</p></Card>
      </div>
      <Card>
        <div className="h-72">
          <ResponsiveContainer>
            <LineChart data={data.series}>
              <CartesianGrid strokeDasharray="3 3" stroke={axis} opacity={0.2} />
              <XAxis dataKey="date" tick={{ fill: axis, fontSize: 10 }} hide={days > 40} />
              <YAxis tick={{ fill: axis, fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatMoney(v)} />
              <Line type="monotone" dataKey="balance" stroke="#0f766e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
