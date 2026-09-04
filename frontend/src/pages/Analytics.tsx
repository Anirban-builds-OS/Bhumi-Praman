import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import * as api from "../services/api";
import { apiErrorMessage } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Card } from "../components/Badges";
import { FIELD_LABELS } from "../types";
import type { EvaluationReport } from "../types";

function f1Color(f1: number) {
  if (f1 >= 0.9) return "#15803d";
  if (f1 >= 0.7) return "#d97706";
  return "#b91c1c";
}

export default function Analytics() {
  const { user } = useAuth();
  const { data: stats } = useQuery({ queryKey: ["dashboard-stats"], queryFn: api.getDashboardStats });
  const [evalResult, setEvalResult] = useState<EvaluationReport | null>(null);
  const [evalError, setEvalError] = useState<string | null>(null);

  const evalMutation = useMutation({
    mutationFn: api.runEvaluation,
    onSuccess: (data) => { setEvalResult(data); setEvalError(null); },
    onError: (err) => setEvalError(apiErrorMessage(err)),
  });

  const districtChart = (stats?.district_coverage ?? []).map((d) => ({ name: d.district, total: d.total, verified: d.verified }));
  const fieldF1Chart = evalResult
    ? Object.entries(evalResult.field_metrics)
        .map(([field, m]) => ({ field: FIELD_LABELS[field as keyof typeof FIELD_LABELS] ?? field, f1: m.f1 }))
        .sort((a, b) => a.f1 - b.f1)
    : [];

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="font-serif text-2xl font-semibold text-primary mb-1">State Reports &amp; Analytics</h1>
      <p className="text-sm text-text-muted mb-8">Digitization coverage and AI pipeline accuracy, computed from real system data.</p>

      <Card className="p-6 mb-6">
        <h2 className="text-sm font-semibold text-text-main mb-4">Verified Coverage by District</h2>
        {districtChart.length === 0 ? (
          <p className="text-sm text-text-muted">No district data yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={districtChart}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d1ccc6" />
              <XAxis dataKey="name" fontSize={12} stroke="#6b6560" />
              <YAxis fontSize={12} stroke="#6b6560" allowDecimals={false} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #d1ccc6" }} />
              <Bar dataKey="total" fill="#d1ccc6" name="Total records" radius={[4, 4, 0, 0]} />
              <Bar dataKey="verified" fill="#4a7c59" name="Verified" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Card>

      <Card className="p-6">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-semibold text-text-main">AI Pipeline Accuracy</h2>
          {user?.role === "administrator" ? (
            <button
              onClick={() => evalMutation.mutate()}
              disabled={evalMutation.isPending}
              className="flex items-center gap-1.5 bg-primary text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-60"
            >
              <iconify-icon icon={evalMutation.isPending ? "lucide:loader-2" : "lucide:play"} className={evalMutation.isPending ? "animate-spin" : ""} width="13"></iconify-icon>
              Run Evaluation
            </button>
          ) : (
            <span className="text-xs text-text-muted">Administrator access required to run evaluation</span>
          )}
        </div>
        <p className="text-xs text-text-muted mb-4">
          Measured against the labelled sample set with known ground truth &mdash; this is never a hard-coded figure, it's recomputed live each time you run it.
        </p>

        {evalError && <p className="text-sm text-error mb-3">{evalError}</p>}

        {evalResult ? (
          <>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-3 rounded-lg bg-bg-alt">
                <div className="text-xl font-serif font-semibold text-text-main">{evalResult.documents_evaluated}</div>
                <div className="text-xs text-text-muted mt-0.5">Documents evaluated</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-bg-alt">
                <div className="text-xl font-serif font-semibold text-text-main">{(evalResult.mean_cer * 100).toFixed(1)}%</div>
                <div className="text-xs text-text-muted mt-0.5">Mean character error rate</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-bg-alt">
                <div className="text-xl font-serif font-semibold text-text-main">{(evalResult.macro_average_f1 * 100).toFixed(1)}%</div>
                <div className="text-xs text-text-muted mt-0.5">Macro-average field F1</div>
              </div>
            </div>

            <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wide mb-2">Per-field F1</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={fieldF1Chart} layout="vertical" margin={{ left: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d1ccc6" horizontal={false} />
                <XAxis type="number" domain={[0, 1]} fontSize={11} stroke="#6b6560" />
                <YAxis type="category" dataKey="field" fontSize={11} width={130} stroke="#6b6560" />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #d1ccc6" }} />
                <Bar dataKey="f1" radius={[0, 4, 4, 0]}>
                  {fieldF1Chart.map((entry) => <Cell key={entry.field} fill={f1Color(entry.f1)} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-text-muted mt-3">
              Low scores reflect the current off-the-shelf OCR engine on heavily degraded scans, not a data or logic error &mdash;
              see the README's Limitations section. This is exactly why the human verification workspace exists.
            </p>
          </>
        ) : (
          !evalMutation.isPending && <p className="text-sm text-text-muted">No evaluation run yet this session.</p>
        )}
      </Card>
    </div>
  );
}
