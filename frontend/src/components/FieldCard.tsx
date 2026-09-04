import { useState } from "react";
import type { FieldName, FieldState } from "../types";
import { FIELD_LABELS } from "../types";
import { ConfidenceBadge, ReviewFlag } from "./Badges";

interface Props {
  field: FieldName;
  state: FieldState;
  variant: "priority" | "condensed";
  isActive: boolean;
  onFocus: () => void;
  onAccept: () => void;
  onEdit: (value: string) => void;
  onReject: () => void;
  busy?: boolean;
}

export default function FieldCard({ field, state, variant, isActive, onFocus, onAccept, onEdit, onReject, busy }: Props) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(state.value ?? "");

  function submitEdit() {
    onEdit(draft);
    setEditing(false);
  }

  const containerClasses = variant === "priority"
    ? `border rounded-xl p-5 mb-4 transition-colors ${isActive ? "border-primary bg-info-bg/40" : "border-warning/40 bg-warning-bg/30"}`
    : `border rounded-lg p-3 transition-colors cursor-pointer ${isActive ? "border-primary bg-info-bg/40" : "border-border bg-surface hover:border-primary/40"}`;

  return (
    <div className={containerClasses} onMouseEnter={onFocus} onClick={variant === "condensed" ? onFocus : undefined}>
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <span className={`font-medium text-text-main ${variant === "priority" ? "text-sm" : "text-xs"}`}>{FIELD_LABELS[field]}</span>
        <ConfidenceBadge value={state.confidence} bucket={state.confidence_bucket} />
      </div>

      {editing ? (
        <div className="flex items-center gap-2 mt-2" onClick={(e) => e.stopPropagation()}>
          <input
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submitEdit()}
            className="flex-1 px-2.5 py-1.5 border border-primary rounded-md text-sm font-mono focus:outline-none"
          />
          <button onClick={submitEdit} className="p-1.5 rounded-md bg-primary text-white"><iconify-icon icon="lucide:check" width="14"></iconify-icon></button>
          <button onClick={() => setEditing(false)} className="p-1.5 rounded-md border border-border"><iconify-icon icon="lucide:x" width="14"></iconify-icon></button>
        </div>
      ) : (
        <div className={`font-mono text-text-main ${variant === "priority" ? "text-base mb-3" : "text-sm mb-2 truncate"}`}>
          {state.value ?? <span className="text-text-muted italic font-sans">Not extracted</span>}
        </div>
      )}

      {!editing && (
        <div className="flex items-center justify-between">
          {state.needs_human_review ? <ReviewFlag bucket={state.confidence_bucket} /> : (
            <span className="text-xs text-text-muted flex items-center gap-1">
              <iconify-icon icon={state.source === "officer" ? "lucide:user-check" : "lucide:check"} width="12"></iconify-icon>
              {state.source === "officer" ? "Officer corrected" : "Accepted"}
            </span>
          )}
          <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
            {!state.field_verified && state.value && (
              <button disabled={busy} onClick={onAccept} title="Accept AI value" className="p-1.5 rounded-md hover:bg-success-bg text-success">
                <iconify-icon icon="lucide:check" width="14"></iconify-icon>
              </button>
            )}
            <button disabled={busy} onClick={() => { setDraft(state.value ?? ""); setEditing(true); }} title="Edit" className="p-1.5 rounded-md hover:bg-info-bg text-info">
              <iconify-icon icon="lucide:pencil" width="14"></iconify-icon>
            </button>
            <button disabled={busy} onClick={onReject} title="Clear value" className="p-1.5 rounded-md hover:bg-error-bg text-error">
              <iconify-icon icon="lucide:x" width="14"></iconify-icon>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
