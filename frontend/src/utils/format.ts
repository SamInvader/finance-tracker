export function formatMoney(amount: number | null | undefined, currency = "NGN") {
  const value = Number(amount || 0);
  try {
    return new Intl.NumberFormat("en-NG", {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
    }).format(value);
  } catch {
    return `₦${value.toLocaleString("en-NG", { minimumFractionDigits: 2 })}`;
  }
}

export function classNames(...xs: Array<string | false | null | undefined>) {
  return xs.filter(Boolean).join(" ");
}

export function parseQuick(text: string) {
  const raw = text.trim();
  const match = raw.match(/(?:₦|NGN)?\s*([0-9]{1,3}(?:,[0-9]{3})*|[0-9]+)(?:\.[0-9]{1,2})?/i);
  let amount: number | undefined;
  let description = raw;
  if (match) {
    amount = Number(match[0].replace(/[₦,\s]|NGN/gi, ""));
    description = (raw.slice(0, match.index) + raw.slice((match.index || 0) + match[0].length)).trim();
  }
  let type: "income" | "expense" | "transfer" = "expense";
  const lower = raw.toLowerCase();
  if (["salary", "allowance", "freelance", "income", "gift"].some((w) => lower.includes(w))) type = "income";
  if (lower.includes("transfer") || raw.includes("->") || raw.includes("→")) type = "transfer";
  return { description: description || "Transaction", amount, type };
}
