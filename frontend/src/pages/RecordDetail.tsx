import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import * as api from "../services/api";
import { Card, StatusBadge } from "../components/Badges";
import { FIELD_LABELS, type FieldName } from "../types";
import { actionLabel, formatDate } from "../utils/format";

const SECTIONS: { title: string; fields: FieldName[] }[] = [
  { title: "Ownership", fields: ["owner_name", "father_name"] },
  { title: "Land Identification", fields: ["survey_number", "khasra_number", "khata_number"] },
  { title: "Location", fields: ["village", "tehsil", "district"] },
  { title: "Area & Classification", fields: ["plot_area", "land_classification"] },
  { title: "Mutation & Registration", fields: ["mutation_number", "registration_number"] },
];

export default function RecordDetail() {
  const { recordId } = useParams();
  const id = Number(recordId);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const { data: record, isLoading } = useQuery({ queryKey: ["record", id], queryFn: () => api.getRecord(id), enabled: !!id });
  const { data: auditTrail } = useQuery({ queryKey: ["record-audit", id], queryFn: () => api.getRecordAuditTrail(id), enabled: !!id });

  const reportMutation = useMutation({
    mutationFn: () => api.generateReport(id),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${record?.record_code ?? "record"}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    },
    onError: () => setDownloadError("Couldn't generate the report. Please try again."),
  });

  if (isLoading) return <div className="p-8 text-sm text-text-muted">Loading record…</div>;
  if (!record) return <div className="p-8 text-sm text-error">Record not found.</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-start justify-between mb-6 flex-wrap gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="font-mono text-xl font-semibold text-text-main">{record.record_code}</h1>
            <StatusBadge status={record.status} />
          </div>
          <p className="text-sm text-text-muted">{record.owner_name ?? "Owner not extracted"} &middot; {record.village ?? "—"}, {record.tehsil ?? "—"}, {record.district ?? "—"}</p>
        </div>
        <div className="flex items-center gap-2">
          {record.latitude && record.longitude && (
            <Link to={`/gis?record=${record.id}`} className="flex items-center gap-1.5 border border-border text-text-main text-sm font-medium px-4 py-2 rounded-lg hover:bg-bg-alt transition-colors">
              <iconify-icon icon="lucide:map-pin" width="15"></iconify-icon> View on Map
            </Link>
          )}
          {record.status === "pending_review" && (
            <Link to={`/verify/${record.id}`} className="flex items-center gap-1.5 bg-primary text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors">
              <iconify-icon icon="lucide:clipboard-check" width="15"></iconify-icon> Open in Workspace
            </Link>
          )}
          <button
            onClick={() => reportMutation.mutate()}
            disabled={reportMutation.isPending}
            className="flex items-center gap-1.5 bg-secondary text-white text-sm font-medium px-4 py-2 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-60"
          >
            <iconify-icon icon={reportMutation.isPending ? "lucide:loader-2" : "lucide:file-down"} className={reportMutation.isPending ? "animate-spin" : ""} width="15"></iconify-icon>
            Export PDF
          </button>
        </div>
      </div>
      {downloadError && <div className="mb-4 px-4 py-2.5 rounded-lg bg-error-bg text-error text-sm">{downloadError}</div>}

      {record.status === "rejected" && record.rejection_reason && (
        <div className="mb-6 px-4 py-3 rounded-lg bg-error-bg text-error text-sm">
          <span className="font-medium">Rejected:</span> {record.rejection_reason}
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-5">
          {SECTIONS.map((section) => (
            <Card key={section.title} className="p-5">
              <h2 className="text-sm font-semibold text-primary mb-3">{section.title}</h2>
              <dl className="grid grid-cols-2 gap-x-4 gap-y-3">
                {section.fields.map((f) => (
                  <div key={f}>
                    <dt className="text-xs text-text-muted mb-0.5">{FIELD_LABELS[f]}</dt>
                    <dd className="text-sm font-mono text-text-main">{record[f] ?? "—"}</dd>
                  </div>
                ))}
              </dl>
            </Card>
          ))}

          <Card className="p-5">
            <h2 className="text-sm font-semibold text-primary mb-3">Audit History</h2>
            <div className="space-y-3">
              {(auditTrail ?? []).length === 0 && <p className="text-sm text-text-muted">No audit entries yet.</p>}
              {auditTrail?.map((a) => (
                <div key={a.id} className="flex gap-3 text-sm border-b border-border last:border-0 pb-3 last:pb-0">
                  <div className="w-6 h-6 rounded-full bg-info-bg text-primary flex items-center justify-center shrink-0 mt-0.5">
                    <iconify-icon icon="lucide:history" width="12"></iconify-icon>
                  </div>
                  <div className="min-w-0">
                    <div className="text-text-main">
                      {actionLabel(a.action)}
                      {a.field_name && <span className="text-text-muted"> &middot; {FIELD_LABELS[a.field_name as FieldName] ?? a.field_name}</span>}
                    </div>
                    {(a.old_value || a.new_value) && (
                      <div className="text-xs font-mono text-text-muted mt-0.5">
                        {a.old_value ?? "∅"} &rarr; {a.new_value ?? "∅"}
                      </div>
                    )}
                    <div className="text-xs text-text-muted mt-0.5">{a.actor_name_snapshot} &middot; {formatDate(a.created_at)}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="space-y-5">
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-primary mb-3">Validation</h2>
            {record.validation_issues.length === 0 ? (
              <p className="text-sm text-success flex items-center gap-1.5"><iconify-icon icon="lucide:check-circle-2" width="15"></iconify-icon>No open issues</p>
            ) : (
              <ul className="text-sm text-error space-y-1 list-disc list-inside">
                {record.validation_issues.map((i) => <li key={i}>{i}</li>)}
              </ul>
            )}
            {record.duplicate_of.length > 0 && (
              <p className="text-sm text-warning mt-2 flex items-center gap-1.5"><iconify-icon icon="lucide:copy-warning" width="14"></iconify-icon>Possible duplicate of {record.duplicate_of.join(", ")}</p>
            )}
            {record.conflicts.length > 0 && (
              <p className="text-sm text-error mt-2 flex items-center gap-1.5"><iconify-icon icon="lucide:git-compare" width="14"></iconify-icon>{record.conflicts.length} possible ownership conflict(s)</p>
            )}
          </Card>

          <Card className="p-5">
            <h2 className="text-sm font-semibold text-primary mb-3">Verification</h2>
            <dl className="space-y-2.5 text-sm">
              <div className="flex justify-between"><dt className="text-text-muted">Verified by</dt><dd className="text-text-main">{record.verified_by_name ?? "—"}</dd></div>
              <div className="flex justify-between"><dt className="text-text-muted">Verified at</dt><dd className="text-text-main">{formatDate(record.verified_at)}</dd></div>
              <div>
                <dt className="text-text-muted mb-1">Record integrity hash (SHA-256)</dt>
                <dd className="font-mono text-xs text-text-main break-all bg-bg-alt rounded px-2 py-1.5">{record.verification_hash ?? "Assigned once verified"}</dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </div>
  );
}
