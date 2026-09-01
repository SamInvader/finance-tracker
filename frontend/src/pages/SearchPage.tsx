import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Card } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";

export default function SearchPage() {
  const [params] = useSearchParams();
  const q = params.get("q") || "";
  const [data, setData] = useState<any>(null);
  useEffect(() => { if (q) financeApi.search(q).then(setData); }, [q]);
  if (!q) return <p>Type a search in the header.</p>;
  if (!data) return <p>Searching…</p>;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Search “{q}”</h1>
      {["transactions", "accounts", "categories", "bills", "subscriptions", "goals", "debts"].map((key) => (
        <Card key={key} title={key}>
          {(data[key] || []).length === 0 ? <p className="text-sm text-slate-500">No matches.</p> : (
            <ul className="text-sm">
              {data[key].map((row: any) => (
                <li key={row.id} className="flex justify-between py-1">
                  <span>{row.name || row.description || row.title}</span>
                  {row.amount != null && <span>{formatMoney(row.amount)}</span>}
                </li>
              ))}
            </ul>
          )}
        </Card>
      ))}
      <Link className="text-sm text-teal-700" to="/transactions">Open transactions</Link>
    </div>
  );
}
