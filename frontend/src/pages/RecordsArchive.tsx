import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import * as api from "../services/api";
import { Card, StatusBadge, ConfidenceBadge } from "../components/Badges";
import type { RecordStatus } from "../types";

const STATUS_TABS: { value: RecordStatus | ""; label: string }[] = [
  { value: "", label: "All" },
  { value: "pending_review", label: "Pending Review" },
  { value: "verified", label: "Verified" },
  { value: "rejected", label: "Rejected" },
];

export default function RecordsArchive() {
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<RecordStatus | "">("");
  const [page, setPage] = useState(1);
  const pageSize = 15;

  const { data, isLoading } = useQuery({
    queryKey: ["records", { query, status, page }],
    queryFn: () => api.listRecords({ query: query || undefined, status: status || undefined, page, page_size: pageSize }),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="font-serif text-2xl font-semibold text-primary mb-1">Archive Registry</h1>
      <p className="text-sm text-text-muted mb-6">Search and browse every digitized land record.</p>

      <div className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1">
          <iconify-icon icon="lucide:search" width="16" style={{ position: "absolute", left: 12, top: 12, color: "#6b6560" }}></iconify-icon>
          <input
            value={query}
            onChange={(e) => { setQuery(e.target.value); setPage(1); }}
            placeholder="Search by owner, survey no., khasra, khata, village, or record ID…"
            className="w-full pl-9 pr-3 py-2.5 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
        </div>
      </div>

      <div className="flex gap-1.5 mb-5">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            onClick={() => { setStatus(tab.value); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              status === tab.value ? "bg-primary text-white" : "bg-surface border border-border text-text-muted hover:text-text-main"
            }`}
          >
            {tab.label}
          </button>
        ))}
        {searchParams.get("document") && (
          <span className="px-3 py-1.5 rounded-lg text-xs font-medium bg-info-bg text-info flex items-center gap-1">
            <iconify-icon icon="lucide:filter" width="12"></iconify-icon> From document #{searchParams.get("document")}
          </span>
        )}
      </div>

      {isLoading && <p className="text-sm text-text-muted">Loading…</p>}
      {data?.items.length === 0 && (
        <Card className="p-10 text-center text-sm text-text-muted">No records match this search.</Card>
      )}

      <div className="space-y-2">
        {data?.items.map((r) => (
          <Link key={r.id} to={`/records/${r.id}`}>
            <Card className="p-4 flex items-center gap-4 hover:border-primary/50 transition-colors">
              <div className="min-w-0 flex-1 grid grid-cols-2 md:grid-cols-4 gap-3 items-center">
                <div>
                  <div className="text-sm font-mono font-medium text-text-main">{r.record_code}</div>
                  <div className="text-xs text-text-muted truncate">{r.owner_name ?? "Owner not extracted"}</div>
                </div>
                <div className="text-xs text-text-muted">
                  <div>Khasra: <span className="font-mono text-text-main">{r.khasra_number ?? "—"}</span></div>
                  <div>Khata: <span className="font-mono text-text-main">{r.khata_number ?? "—"}</span></div>
                </div>
                <div className="text-xs text-text-muted truncate">{r.village ?? "—"}, {r.district ?? "—"}</div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={r.status} />
                  {(r.has_duplicates || r.has_conflicts) && (
                    <iconify-icon icon="lucide:alert-triangle" width="14" style={{ color: "#d97706" }}></iconify-icon>
                  )}
                </div>
              </div>
              <ConfidenceBadge value={r.record_confidence} bucket={r.record_confidence >= 0.85 ? "high" : r.record_confidence >= 0.6 ? "medium" : "low"} />
            </Card>
          </Link>
        ))}
      </div>

      {data && data.total > pageSize && (
        <div className="flex items-center justify-between mt-5 text-sm">
          <span className="text-text-muted">Page {page} of {totalPages} &middot; {data.total} records</span>
          <div className="flex gap-2">
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="px-3 py-1.5 rounded-lg border border-border disabled:opacity-40">Previous</button>
            <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)} className="px-3 py-1.5 rounded-lg border border-border disabled:opacity-40">Next</button>
          </div>
        </div>
      )}
    </div>
  );
}
