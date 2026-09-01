import { useEffect, useState } from "react";
import { Card, EmptyState, LoadingState } from "../components/ui";
import { financeApi } from "../services/finance";

export default function Insights() {
  const [items, setItems] = useState<any[] | null>(null);
  useEffect(() => { financeApi.insights().then(setItems as any); }, []);
  if (!items) return <LoadingState />;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Insights</h1>
      <p className="text-sm text-slate-500">Observations calculated from your stored transactions. Nothing here is invented.</p>
      {items.length === 0 ? <EmptyState title="No insights" body="Add more history." /> : items.map((i, n) => (
        <Card key={n} title={i.title}><p className="text-sm">{i.body}</p></Card>
      ))}
    </div>
  );
}
