import { useEffect, useMemo, useState } from "react";
import { Card, Modal } from "../components/ui";
import { financeApi } from "../services/finance";
import { formatMoney } from "../utils/format";

export default function CalendarPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [events, setEvents] = useState<any[]>([]);
  const [sel, setSel] = useState<any>(null);
  useEffect(() => { financeApi.calendar(year, month).then(setEvents as any); }, [year, month]);
  const first = new Date(year, month - 1, 1).getDay();
  const days = new Date(year, month, 0).getDate();
  const cells = useMemo(() => {
    const arr: { day?: number; date?: string }[] = [];
    for (let i = 0; i < first; i++) arr.push({});
    for (let d = 1; d <= days; d++) arr.push({ day: d, date: `${year}-${String(month).padStart(2, "0")}-${String(d).padStart(2, "0")}` });
    return arr;
  }, [first, days, year, month]);
  const byDate: Record<string, any[]> = {};
  events.forEach((e) => { (byDate[e.date] ||= []).push(e); });
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Calendar</h1>
        <div className="flex gap-2">
          <button className="btn-secondary" onClick={() => { if (month === 1) { setYear(year - 1); setMonth(12); } else setMonth(month - 1); }}>Prev</button>
          <span className="self-center text-sm">{year}-{String(month).padStart(2, "0")}</span>
          <button className="btn-secondary" onClick={() => { if (month === 12) { setYear(year + 1); setMonth(1); } else setMonth(month + 1); }}>Next</button>
        </div>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-500">{["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].map((d) => <div key={d}>{d}</div>)}</div>
      <div className="grid grid-cols-7 gap-1">
        {cells.map((c, i) => (
          <div key={i} className="min-h-[5.5rem] rounded-xl border border-slate-200 p-1 text-left text-xs dark:border-slate-800">
            <div className="font-semibold">{c.day}</div>
            {c.date && byDate[c.date]?.map((e, idx) => (
              <button key={idx} className="mt-0.5 block w-full truncate rounded bg-teal-50 px-1 text-left dark:bg-teal-950" onClick={() => setSel(e)}>{e.title}</button>
            ))}
          </div>
        ))}
      </div>
      <Modal open={!!sel} onClose={() => setSel(null)} title={sel?.title || ""}>
        {sel && <p className="text-sm">{sel.kind} on {sel.date} · {formatMoney(sel.amount)}</p>}
      </Modal>
    </div>
  );
}
