import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import * as api from "../services/api";
import { Card } from "../components/Badges";
import { actionLabel, formatDate } from "../utils/format";
import { FIELD_LABELS, type FieldName } from "../types";

const ENTITY_FILTERS = [
  { value: "", label: "All" },
  { value: "document", label: "Documents" },
  { value: "land_record", label: "Records" },
  { value: "user", label: "Users" },
];

export default function AuditTrail() {
  const [entityType, setEntityType] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["audit-log", entityType],
    queryFn: () => api.listAuditLog({ entity_type: entityType || undefined, limit: 200 }),
  });

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="font-serif text-2xl font-semibold text-primary mb-1">Audit Trails</h1>
      <p className="text-sm text-text-muted mb-6">Every mutating action in the system, in order &mdash; who did what, and when.</p>

      <div className="flex gap-1.5 mb-5">
        {ENTITY_FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setEntityType(f.value)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              entityType === f.value ? "bg-primary text-white" : "bg-surface border border-border text-text-muted hover:text-text-main"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-text-muted">Loading…</p>}

      <Card className="divide-y divide-border">
        {data?.length === 0 && <p className="p-6 text-sm text-text-muted">No audit entries match this filter.</p>}
        {data?.map((a) => (
          <div key={a.id} className="p-4 flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-info-bg text-primary flex items-center justify-center shrink-0 mt-0.5">
              <iconify-icon icon="lucide:activity" width="13"></iconify-icon>
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm text-text-main flex items-center gap-2 flex-wrap">
                <span className="font-medium">{actionLabel(a.action)}</span>
                {a.entity_type === "land_record" && a.entity_id && (
                  <Link to={`/records/${a.entity_id}`} className="text-xs text-primary hover:underline font-mono">
                    #{a.entity_id}
                  </Link>
                )}
                {a.field_name && <span className="text-xs text-text-muted">on {FIELD_LABELS[a.field_name as FieldName] ?? a.field_name}</span>}
              </div>
              {(a.old_value || a.new_value) && (
                <div className="text-xs font-mono text-text-muted mt-0.5">{a.old_value ?? "∅"} &rarr; {a.new_value ?? "∅"}</div>
              )}
              {a.notes && <div className="text-xs text-text-muted mt-0.5 italic">{a.notes}</div>}
              <div className="text-xs text-text-muted mt-1">{a.actor_name_snapshot} &middot; {formatDate(a.created_at)}</div>
            </div>
          </div>
        ))}
      </Card>
    </div>
  );
}
