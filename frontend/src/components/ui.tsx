import { type ReactNode } from "react";
import { classNames } from "../utils/format";

export function Card({ children, className, title, action }: { children: ReactNode; className?: string; title?: string; action?: ReactNode }) {
  return (
    <section className={classNames("card", className)}>
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between gap-3">
          {title && <h2 className="text-base font-semibold tracking-tight">{title}</h2>}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function EmptyState({ title, body, action }: { title: string; body: string; action?: ReactNode }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-300 px-6 py-12 text-center dark:border-slate-700">
      <p className="text-base font-semibold">{title}</p>
      <p className="mx-auto mt-1 max-w-md text-sm text-slate-500">{body}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="animate-pulse space-y-3" role="status" aria-live="polite" aria-label={label}>
      <div className="h-24 rounded-2xl bg-slate-200 dark:bg-slate-800" />
      <div className="h-24 rounded-2xl bg-slate-200 dark:bg-slate-800" />
      <span className="sr-only">{label}</span>
    </div>
  );
}

export function Field({ label, children, hint, error }: { label: string; children: ReactNode; hint?: string; error?: string }) {
  return (
    <label className="block">
      <span className="label">{label}</span>
      {children}
      {hint && !error && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
      {error && <span className="mt-1 block text-xs text-rose-600">{error}</span>}
    </label>
  );
}

export function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center sm:items-center" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <button className="absolute inset-0 bg-slate-950/50" aria-label="Close dialog" onClick={onClose} />
      <div className="relative z-10 max-h-[90vh] w-full overflow-y-auto rounded-t-2xl bg-white p-5 shadow-xl dark:bg-slate-900 sm:max-w-lg sm:rounded-2xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 id="modal-title" className="text-lg font-semibold">
            {title}
          </h2>
          <button className="btn-secondary px-3 py-1 text-sm" onClick={onClose}>
            Close
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function Confirm({
  open,
  title,
  body,
  onCancel,
  onConfirm,
}: {
  open: boolean;
  title: string;
  body: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  return (
    <Modal open={open} onClose={onCancel} title={title}>
      <p className="text-sm text-slate-600 dark:text-slate-300">{body}</p>
      <div className="mt-4 flex justify-end gap-2">
        <button className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button className="btn-primary bg-rose-700 hover:bg-rose-800" onClick={onConfirm}>
          Confirm
        </button>
      </div>
    </Modal>
  );
}
