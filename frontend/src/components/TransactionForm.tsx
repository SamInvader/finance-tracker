import { useEffect, useMemo, useState } from "react";
import { Field } from "./ui";
import { parseQuick } from "../utils/format";
import type { Account, Category } from "../types";

export function TransactionForm({
  accounts,
  categories,
  initial,
  onSubmit,
  submitting,
}: {
  accounts: Account[];
  categories: Category[];
  initial?: Partial<{
    type: string;
    amount: number;
    account_id: number;
    destination_account_id: number;
    category_id: number;
    date: string;
    description: string;
    notes: string;
    tags: string;
  }>;
  onSubmit: (payload: object) => Promise<void>;
  submitting?: boolean;
}) {
  const [quick, setQuick] = useState("");
  const [type, setType] = useState(initial?.type || "expense");
  const [amount, setAmount] = useState(String(initial?.amount ?? ""));
  const [accountId, setAccountId] = useState(String(initial?.account_id ?? accounts[0]?.id ?? ""));
  const [destId, setDestId] = useState(String(initial?.destination_account_id ?? ""));
  const [categoryId, setCategoryId] = useState(String(initial?.category_id ?? ""));
  const [date, setDate] = useState(initial?.date || new Date().toISOString().slice(0, 10));
  const [description, setDescription] = useState(initial?.description || "");
  const [notes, setNotes] = useState(initial?.notes || "");
  const [tags, setTags] = useState(initial?.tags || "");
  const [error, setError] = useState("");

  useEffect(() => {
    if (accounts[0] && !accountId) setAccountId(String(accounts[0].id));
  }, [accounts, accountId]);

  const filteredCats = useMemo(
    () => categories.filter((c) => (type === "transfer" ? true : c.kind === type)),
    [categories, type]
  );

  function applyQuick() {
    const parsed = parseQuick(quick);
    if (parsed.amount) setAmount(String(parsed.amount));
    if (parsed.description) setDescription(parsed.description);
    setType(parsed.type);
    const match = categories.find((c) => c.name.toLowerCase().includes(parsed.description.toLowerCase().split(" ")[0] || "xxx"));
    if (match) {
      setType(match.kind);
      setCategoryId(String(match.id));
    }
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!amount || Number(amount) <= 0) {
      setError("Enter a valid amount");
      return;
    }
    if (!accountId) {
      setError("Select an account");
      return;
    }
    if (type === "transfer" && (!destId || destId === accountId)) {
      setError("Choose a different destination account");
      return;
    }
    try {
      await onSubmit({
        type,
        amount: Number(amount),
        account_id: Number(accountId),
        destination_account_id: destId ? Number(destId) : null,
        category_id: categoryId ? Number(categoryId) : null,
        date,
        description,
        notes,
        tags,
      });
    } catch (err: any) {
      setError(err.message || "Could not save");
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <Field label="Quick add" hint="Example: Food 3500">
        <div className="flex gap-2">
          <input className="input" value={quick} onChange={(e) => setQuick(e.target.value)} placeholder="Food ₦3500" />
          <button type="button" className="btn-secondary" onClick={applyQuick}>
            Parse
          </button>
        </div>
      </Field>
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="Type">
          <select className="input" value={type} onChange={(e) => setType(e.target.value)}>
            <option value="expense">Expense</option>
            <option value="income">Income</option>
            <option value="transfer">Transfer</option>
          </select>
        </Field>
        <Field label="Amount (₦)">
          <input className="input" inputMode="decimal" value={amount} onChange={(e) => setAmount(e.target.value)} required />
        </Field>
        <Field label="Account">
          <select className="input" value={accountId} onChange={(e) => setAccountId(e.target.value)}>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name}
              </option>
            ))}
          </select>
        </Field>
        {type === "transfer" ? (
          <Field label="To account">
            <select className="input" value={destId} onChange={(e) => setDestId(e.target.value)}>
              <option value="">Select destination</option>
              {accounts
                .filter((a) => String(a.id) !== accountId)
                .map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
            </select>
          </Field>
        ) : (
          <Field label="Category">
            <select className="input" value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">Uncategorized</option>
              {filteredCats.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </Field>
        )}
        <Field label="Date">
          <input className="input" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
        </Field>
        <Field label="Description">
          <input className="input" value={description} onChange={(e) => setDescription(e.target.value)} />
        </Field>
      </div>
      <Field label="Notes">
        <textarea className="input min-h-[72px]" value={notes} onChange={(e) => setNotes(e.target.value)} />
      </Field>
      <Field label="Tags" hint="Comma-separated">
        <input className="input" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="food, campus" />
      </Field>
      {error && <p className="text-sm text-rose-600">{error}</p>}
      <button className="btn-primary w-full" disabled={submitting}>
        {submitting ? "Saving…" : "Save transaction"}
      </button>
    </form>
  );
}
