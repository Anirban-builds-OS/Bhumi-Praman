import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import * as api from "../services/api";
import { Card, ConfidenceBadge } from "../components/Badges";
import { confidencePct } from "../utils/format";

export default function VerificationQueue() {
  const { data, isLoading } = useQuery({
    queryKey: ["records", { status: "pending_review" }],
    queryFn: () => api.listRecords({ status: "pending_review", page_size: 50 }),
  });

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="font-serif text-2xl font-semibold text-primary mb-1">Verification Queue</h1>
      <p className="text-sm text-text-muted mb-8">Records awaiting officer review, ordered by most recently processed.</p>

      {isLoading && <p className="text-sm text-text-muted">Loading…</p>}
      {data?.items.length === 0 && (
        <Card className="p-10 text-center">
          <iconify-icon icon="lucide:inbox" width="28" style={{ color: "#6b6560" }}></iconify-icon>
          <p className="text-sm text-text-muted mt-3">No records pending verification. Upload and process a document to get started.</p>
          <Link to="/ingest" className="inline-flex items-center gap-1.5 mt-4 text-sm font-medium text-primary hover:underline">
            Go to Bulk Ingestion <iconify-icon icon="lucide:arrow-right" width="13"></iconify-icon>
          </Link>
        </Card>
      )}

      <div className="space-y-2">
        {data?.items.map((r) => (
          <Link key={r.id} to={`/verify/${r.id}`} className="block">
            <Card className="p-4 flex items-center gap-4 hover:border-primary/50 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-warning-bg text-warning flex items-center justify-center shrink-0">
                <iconify-icon icon="lucide:clipboard-check" width="18"></iconify-icon>
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-mono font-medium text-text-main">{r.record_code}</div>
                <div className="text-xs text-text-muted truncate">
                  {r.owner_name ?? "Owner not yet extracted"} &middot; {r.village ?? "village n/a"}, {r.district ?? "district n/a"}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {r.has_duplicates && <span title="Possible duplicate" className="text-warning"><iconify-icon icon="lucide:copy-warning" width="15"></iconify-icon></span>}
                {r.has_conflicts && <span title="Possible ownership conflict" className="text-error"><iconify-icon icon="lucide:git-compare" width="15"></iconify-icon></span>}
                <ConfidenceBadge value={r.record_confidence} bucket={r.record_confidence >= 0.85 ? "high" : r.record_confidence >= 0.6 ? "medium" : "low"} />
              </div>
              <iconify-icon icon="lucide:chevron-right" width="16" style={{ color: "#6b6560" }}></iconify-icon>
            </Card>
          </Link>
        ))}
      </div>
      {data && data.items.length > 0 && (
        <p className="text-xs text-text-muted mt-3">
          Showing {data.items.length} of {data.total} pending record{data.total !== 1 ? "s" : ""}. Record confidence shown is {confidencePct(0)} &ndash; 100% as measured at extraction time.
        </p>
      )}
    </div>
  );
}
