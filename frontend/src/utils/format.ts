import type { ConfidenceBucket, RecordStatus } from "../types";

export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso.endsWith("Z") ? iso : iso + "Z");
  return d.toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

export function formatDateShort(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso.endsWith("Z") ? iso : iso + "Z");
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

export function confidencePct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export const bucketStyles: Record<ConfidenceBucket, { bg: string; text: string; label: string }> = {
  high: { bg: "bg-success-bg", text: "text-success", label: "High Confidence" },
  medium: { bg: "bg-warning-bg", text: "text-warning", label: "Review Recommended" },
  low: { bg: "bg-error-bg", text: "text-error", label: "Manual Verification Required" },
  missing: { bg: "bg-error-bg", text: "text-error", label: "Not Extracted" },
};

export const statusStyles: Record<RecordStatus, { bg: string; text: string; label: string }> = {
  verified: { bg: "bg-success-bg", text: "text-success", label: "Verified" },
  pending_review: { bg: "bg-warning-bg", text: "text-warning", label: "Pending Review" },
  rejected: { bg: "bg-error-bg", text: "text-error", label: "Rejected" },
};

export function bytesToSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function actionLabel(action: string): string {
  const map: Record<string, string> = {
    "auth.login": "Signed in",
    "document.uploaded": "Document uploaded",
    "document.page_processed": "Page processed by AI",
    "document.processing_failed": "Processing failed",
    "record.created": "Record created from AI extraction",
    "record.field_edit": "Field edited",
    "record.field_accept": "Field accepted",
    "record.field_reject": "Field rejected",
    "record.verified": "Record verified",
    "record.rejected": "Record rejected",
    "report.generated": "Report generated",
    "user.created": "User account created",
  };
  return map[action] ?? action;
}
