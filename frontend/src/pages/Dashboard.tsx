import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getDashboardStats } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { actionLabel, formatDate } from "../utils/format";
import { Card } from "../components/Badges";

const KPI_DEFS = [
  { key: "total_documents", label: "Total Documents", icon: "lucide:file-stack", tone: "text-primary" },
  { key: "total_records", label: "Records Extracted", icon: "lucide:layers", tone: "text-primary" },
  { key: "verified_records", label: "Verified Records", icon: "lucide:badge-check", tone: "text-success" },
  { key: "pending_review_records", label: "Pending Verification", icon: "lucide:clock", tone: "text-warning" },
  { key: "low_confidence_records", label: "Low-Confidence Records", icon: "lucide:alert-triangle", tone: "text-error" },
  { key: "validation_conflicts", label: "Ownership Conflicts", icon: "lucide:git-compare", tone: "text-error" },
  { key: "duplicate_flags", label: "Possible Duplicates", icon: "lucide:copy-warning", tone: "text-warning" },
  { key: "rejected_records", label: "Rejected Records", icon: "lucide:x-circle", tone: "text-text-muted" },
] as const;

const FLOW_STEPS = [
  { key: "uploaded", label: "Uploaded" },
  { key: "ai_parsed", label: "AI Parsed" },
  { key: "reviewing", label: "Reviewing" },
  { key: "verified", label: "Verified" },
  { key: "rejected", label: "Rejected" },
];

export default function Dashboard() {
  const { user } = useAuth();
  const { data, isLoading, error } = useQuery({ queryKey: ["dashboard-stats"], queryFn: getDashboardStats, refetchInterval: 15000 });

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-serif text-2xl font-semibold text-primary">Welcome back, {user?.full_name?.split(" ")[0]}</h1>
          <p className="text-sm text-text-muted mt-1">Digitization &amp; validation overview across your jurisdiction.</p>
        </div>
        <Link to="/ingest" className="flex items-center gap-2 bg-primary text-white text-sm font-medium px-4 py-2.5 rounded-lg hover:bg-primary-dark transition-colors">
          <iconify-icon icon="lucide:upload-cloud" width="16"></iconify-icon>
          Upload Document
        </Link>
      </div>

      {isLoading && <div className="text-text-muted text-sm">Loading statistics…</div>}
      {error && <div className="text-error text-sm">Couldn't load dashboard statistics. Is the backend running?</div>}

      {data && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {KPI_DEFS.map((k) => (
              <Card key={k.key} className="p-4">
                <div className={`flex items-center gap-2 ${k.tone} mb-2`}>
                  <iconify-icon icon={k.icon} width="16"></iconify-icon>
                  <span className="text-xs font-medium uppercase tracking-wide text-text-muted">{k.label}</span>
                </div>
                <div className="text-2xl font-serif font-semibold text-text-main">{data[k.key]}</div>
              </Card>
            ))}
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <Card className="md:col-span-2 p-6">
              <h2 className="text-sm font-semibold text-text-main mb-5">Digitization Pipeline</h2>
              <div className="flex items-center">
                {FLOW_STEPS.map((step, i) => (
                  <div key={step.key} className="flex items-center flex-1 last:flex-none">
                    <div className="flex flex-col items-center gap-2 shrink-0">
                      <div className="w-12 h-12 rounded-full bg-info-bg text-primary flex items-center justify-center font-serif font-semibold">
                        {data.pipeline_flow[step.key] ?? 0}
                      </div>
                      <span className="text-xs text-text-muted whitespace-nowrap">{step.label}</span>
                    </div>
                    {i < FLOW_STEPS.length - 1 && <div className="flex-1 h-px bg-border mx-2" />}
                  </div>
                ))}
              </div>

              <h2 className="text-sm font-semibold text-text-main mt-8 mb-4">District Coverage</h2>
              {data.district_coverage.length === 0 ? (
                <p className="text-sm text-text-muted">No district data yet &mdash; process a document to see coverage here.</p>
              ) : (
                <div className="space-y-3">
                  {data.district_coverage.map((d) => (
                    <div key={d.district}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="font-medium text-text-main">{d.district}</span>
                        <span className="text-text-muted">{d.verified} / {d.total} verified ({d.pct}%)</span>
                      </div>
                      <div className="h-2 bg-bg-alt rounded-full overflow-hidden">
                        <div className="h-full bg-secondary rounded-full" style={{ width: `${d.pct}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            <Card className="p-6">
              <h2 className="text-sm font-semibold text-text-main mb-4">Recent Activity</h2>
              <div className="space-y-4">
                {data.recent_activity.length === 0 && <p className="text-sm text-text-muted">No activity yet.</p>}
                {data.recent_activity.map((a) => (
                  <div key={a.id} className="flex gap-3 text-sm">
                    <div className="w-6 h-6 rounded-full bg-info-bg text-primary flex items-center justify-center shrink-0 mt-0.5">
                      <iconify-icon icon="lucide:activity" width="12"></iconify-icon>
                    </div>
                    <div className="min-w-0">
                      <div className="text-text-main">{actionLabel(a.action)}</div>
                      <div className="text-xs text-text-muted">{a.actor_name_snapshot} &middot; {formatDate(a.created_at)}</div>
                    </div>
                  </div>
                ))}
              </div>
              <Link to="/audit" className="mt-4 flex items-center gap-1 text-xs font-medium text-primary hover:underline">
                View full audit trail <iconify-icon icon="lucide:arrow-right" width="12"></iconify-icon>
              </Link>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
