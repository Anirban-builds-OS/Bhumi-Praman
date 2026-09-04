import type { ConfidenceBucket, RecordStatus } from "../types";
import { bucketStyles, confidencePct, statusStyles } from "../utils/format";

export function StatusBadge({ status }: { status: RecordStatus }) {
  const s = statusStyles[status];
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${s.bg} ${s.text}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {s.label}
    </span>
  );
}

export function ConfidenceBadge({ value, bucket }: { value: number; bucket: ConfidenceBucket }) {
  const s = bucketStyles[bucket];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold ${s.bg} ${s.text}`}>
      {confidencePct(value)}
    </span>
  );
}

export function ReviewFlag({ bucket }: { bucket: ConfidenceBucket }) {
  const s = bucketStyles[bucket];
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium ${s.text}`}>
      <iconify-icon icon="lucide:alert-triangle" width="13"></iconify-icon>
      {s.label}
    </span>
  );
}

export function Card({ className = "", children, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`bg-surface border border-border rounded-xl ${className}`} {...rest}>
      {children}
    </div>
  );
}
