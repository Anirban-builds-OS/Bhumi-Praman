import { useMemo, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "../services/api";
import { apiErrorMessage } from "../services/api";
import DocumentCanvas from "../components/DocumentCanvas";
import FieldCard from "../components/FieldCard";
import { Card, StatusBadge } from "../components/Badges";
import { FIELD_NAMES, type FieldName } from "../types";
import { confidencePct } from "../utils/format";

export default function VerificationWorkspace() {
  const { recordId } = useParams();
  const id = Number(recordId);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [activeField, setActiveField] = useState<FieldName | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [showReject, setShowReject] = useState(false);

  const { data: record, isLoading } = useQuery({ queryKey: ["record", id], queryFn: () => api.getRecord(id), enabled: !!id });

  const fieldMutation = useMutation({
    mutationFn: ({ field, value, action }: { field: FieldName; value: string | null; action: "edit" | "accept" | "reject" }) =>
      api.editField(id, field, value, action),
    onSuccess: (updated) => {
      qc.setQueryData(["record", id], updated);
      setActionError(null);
    },
    onError: (err) => setActionError(apiErrorMessage(err)),
  });

  const verifyMutation = useMutation({
    mutationFn: () => api.verifyRecord(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["records"] });
      qc.invalidateQueries({ queryKey: ["dashboard-stats"] });
      navigate(`/records/${id}`);
    },
    onError: (err) => setActionError(apiErrorMessage(err)),
  });

  const rejectMutation = useMutation({
    mutationFn: () => api.rejectRecord(id, rejectReason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["records"] });
      qc.invalidateQueries({ queryKey: ["dashboard-stats"] });
      navigate("/verify");
    },
  });

  const { priorityFields, condensedFields } = useMemo(() => {
    if (!record) return { priorityFields: [], condensedFields: [] };
    const priority: FieldName[] = [];
    const condensed: FieldName[] = [];
    for (const f of FIELD_NAMES) {
      (record.fields[f]?.needs_human_review ? priority : condensed).push(f);
    }
    return { priorityFields: priority, condensedFields: condensed };
  }, [record]);

  const highlights = useMemo(() => {
    if (!record) return [];
    return FIELD_NAMES
      .filter((f) => record.fields[f]?.location)
      .map((f) => ({ field: f, location: record.fields[f].location!, active: f === activeField }));
  }, [record, activeField]);

  if (isLoading) return <div className="p-8 text-sm text-text-muted">Loading record…</div>;
  if (!record) return <div className="p-8 text-sm text-error">Record not found.</div>;

  const canVerify = record.validation_issues.length === 0 && priorityFields.length === 0;

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <Link to="/verify" className="text-text-muted hover:text-text-main"><iconify-icon icon="lucide:arrow-left" width="18"></iconify-icon></Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-mono text-lg font-semibold text-text-main">{record.record_code}</h1>
              <StatusBadge status={record.status} />
            </div>
            <p className="text-xs text-text-muted mt-0.5">
              AI record confidence at extraction: {confidencePct(record.record_confidence)}
            </p>
          </div>
        </div>
        {record.status === "pending_review" && (
          <div className="flex items-center gap-2">
            <button onClick={() => setShowReject(true)} className="flex items-center gap-1.5 border border-error/40 text-error text-sm font-medium px-4 py-2 rounded-lg hover:bg-error-bg transition-colors">
              <iconify-icon icon="lucide:x" width="15"></iconify-icon> Reject
            </button>
            <button
              onClick={() => verifyMutation.mutate()}
              disabled={!canVerify || verifyMutation.isPending}
              title={!canVerify ? "Resolve validation issues and review flagged fields first" : undefined}
              className="flex items-center gap-1.5 bg-secondary text-white text-sm font-medium px-4 py-2 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              <iconify-icon icon="lucide:badge-check" width="15"></iconify-icon> Verify Record
            </button>
          </div>
        )}
      </div>

      {(record.duplicate_of.length > 0 || record.conflicts.length > 0) && (
        <div className="mb-4 space-y-2">
          {record.duplicate_of.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-warning-bg text-warning text-sm">
              <iconify-icon icon="lucide:copy-warning" width="16"></iconify-icon>
              Possible duplicate of: {record.duplicate_of.join(", ")} &mdash; requires review, not an automatic determination.
            </div>
          )}
          {record.conflicts.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-error-bg text-error text-sm">
              <iconify-icon icon="lucide:git-compare" width="16"></iconify-icon>
              Possible ownership conflict on {record.conflicts[0].shared_field.replace("_", " ")} &ldquo;{record.conflicts[0].shared_value}&rdquo; with {record.conflicts.map((c) => c.conflicting_doc_id).join(", ")}.
            </div>
          )}
        </div>
      )}
      {actionError && (
        <div className="mb-4 px-4 py-2.5 rounded-lg bg-error-bg text-error text-sm flex items-center gap-2">
          <iconify-icon icon="lucide:alert-circle" width="16"></iconify-icon>{actionError}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[42%_6%_1fr] gap-4">
        {/* Document canvas */}
        <div>
          {record.document_id && record.document_page_id ? (
            <DocumentCanvas
              imageUrl={api.pageImageUrl(record.document_id, record.document_page_id)}
              imageWidth={record.page_image_width}
              imageHeight={record.page_image_height}
              highlights={highlights}
            />
          ) : (
            <Card className="p-10 text-center text-sm text-text-muted">No source image available for this record.</Card>
          )}
        </div>

        {/* Flow indicator */}
        <div className="hidden lg:flex flex-col items-center justify-center gap-3 text-text-muted">
          <iconify-icon icon="lucide:file-text" width="18"></iconify-icon>
          <div className="w-px h-16 bg-border" />
          <iconify-icon icon="lucide:sparkles" width="18" style={{ color: "#d4a574" }}></iconify-icon>
          <div className="w-px h-16 bg-border" />
          <iconify-icon icon="lucide:user-check" width="18"></iconify-icon>
        </div>

        {/* Extraction panel */}
        <div>
          {priorityFields.length > 0 && (
            <>
              <h2 className="text-sm font-semibold text-warning mb-3 flex items-center gap-1.5">
                <iconify-icon icon="lucide:alert-triangle" width="15"></iconify-icon>
                Needs your review ({priorityFields.length})
              </h2>
              {priorityFields.map((f) => (
                <FieldCard
                  key={f}
                  field={f}
                  state={record.fields[f]}
                  variant="priority"
                  isActive={activeField === f}
                  onFocus={() => setActiveField(f)}
                  busy={fieldMutation.isPending}
                  onAccept={() => fieldMutation.mutate({ field: f, value: record.fields[f].value, action: "accept" })}
                  onEdit={(v) => fieldMutation.mutate({ field: f, value: v, action: "edit" })}
                  onReject={() => fieldMutation.mutate({ field: f, value: null, action: "reject" })}
                />
              ))}
            </>
          )}

          {condensedFields.length > 0 && (
            <>
              <h2 className="text-sm font-semibold text-text-main mt-2 mb-3">Extracted fields</h2>
              <div className="grid grid-cols-2 gap-2.5">
                {condensedFields.map((f) => (
                  <FieldCard
                    key={f}
                    field={f}
                    state={record.fields[f]}
                    variant="condensed"
                    isActive={activeField === f}
                    onFocus={() => setActiveField(f)}
                    busy={fieldMutation.isPending}
                    onAccept={() => fieldMutation.mutate({ field: f, value: record.fields[f].value, action: "accept" })}
                    onEdit={(v) => fieldMutation.mutate({ field: f, value: v, action: "edit" })}
                    onReject={() => fieldMutation.mutate({ field: f, value: null, action: "reject" })}
                  />
                ))}
              </div>
            </>
          )}

          {record.validation_issues.length > 0 && (
            <div className="mt-5 px-4 py-3 rounded-lg bg-error-bg text-error text-sm">
              <div className="font-medium mb-1 flex items-center gap-1.5"><iconify-icon icon="lucide:shield-alert" width="15"></iconify-icon>Validation issues</div>
              <ul className="list-disc list-inside space-y-0.5">
                {record.validation_issues.map((issue) => <li key={issue}>{issue}</li>)}
              </ul>
            </div>
          )}
        </div>
      </div>

      {showReject && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50" onClick={() => setShowReject(false)}>
          <div className="bg-surface rounded-xl p-6 max-w-md w-full" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-serif text-lg font-semibold text-text-main mb-2">Reject this record</h3>
            <p className="text-sm text-text-muted mb-3">This record won't be countable toward verified totals. Explain why for the audit trail.</p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={3}
              placeholder="e.g. Illegible scan, re-upload requested from field office."
              className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
            <div className="flex justify-end gap-2 mt-4">
              <button onClick={() => setShowReject(false)} className="px-4 py-2 text-sm rounded-lg border border-border">Cancel</button>
              <button
                onClick={() => rejectMutation.mutate()}
                disabled={!rejectReason.trim() || rejectMutation.isPending}
                className="px-4 py-2 text-sm rounded-lg bg-error text-white disabled:opacity-50"
              >
                Confirm Reject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
