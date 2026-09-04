import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { apiErrorMessage } from "../services/api";

const DEMO_ACCOUNTS = [
  { role: "Verification Officer", icon: "lucide:shield-check", code: "OFC-KAM-1102", password: "Officer@123",
    desc: "Upload, process, review &amp; verify records" },
  { role: "System Administrator", icon: "lucide:settings", code: "ADM-0001", password: "Admin@123",
    desc: "Manage users, analytics &amp; audit trail" },
  { role: "Record Officer", icon: "lucide:folder-search", code: "REC-0007", password: "Record@123",
    desc: "Search records &amp; generate reports" },
];

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [employeeCode, setEmployeeCode] = useState("");
  const [password, setPassword] = useState("");
  const [staySignedIn, setStaySignedIn] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(employeeCode, password, staySignedIn);
      navigate("/dashboard");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen cadastral-grid flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-4xl grid md:grid-cols-2 gap-8 items-start">
        {/* Left: form */}
        <div className="bg-surface border border-border rounded-2xl shadow-sm p-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-11 h-11 rounded bg-primary rotate-45 flex items-center justify-center shrink-0">
              <div className="-rotate-45">
                <iconify-icon icon="lucide:compass" width="22" style={{ color: "#d4a574" }}></iconify-icon>
              </div>
            </div>
            <div>
              <div className="font-serif font-semibold text-xl text-primary leading-tight">Bhumi Praman</div>
              <div className="text-xs text-text-muted">Secure Gateway &middot; Land Record Platform</div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-main mb-1.5">Employee Code</label>
              <input
                type="text"
                required
                value={employeeCode}
                onChange={(e) => setEmployeeCode(e.target.value)}
                placeholder="e.g. OFC-KAM-1102"
                className="w-full px-3.5 py-2.5 border border-border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-main mb-1.5">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;"
                className="w-full px-3.5 py-2.5 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
            </div>
            <label className="flex items-center gap-2 text-sm text-text-muted">
              <input type="checkbox" checked={staySignedIn} onChange={(e) => setStaySignedIn(e.target.checked)} className="rounded border-border" />
              Stay signed in for 8 hours
            </label>

            {error && (
              <div className="flex items-start gap-2 px-3 py-2.5 rounded-lg bg-error-bg text-error text-sm">
                <iconify-icon icon="lucide:alert-circle" width="16" style={{ marginTop: 2 }}></iconify-icon>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white font-medium py-2.5 rounded-lg text-sm hover:bg-primary-dark transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {loading ? <iconify-icon icon="lucide:loader-2" className="animate-spin" width="16"></iconify-icon> : <iconify-icon icon="lucide:log-in" width="16"></iconify-icon>}
              Sign in
            </button>
          </form>

          <div className="mt-6 flex items-center gap-2 text-[11px] text-text-muted flex-wrap">
            <span className="px-2 py-0.5 rounded border border-border">SIH 2026 &middot; PS 26018</span>
            <span className="px-2 py-0.5 rounded border border-border">Prototype Build</span>
            <span className="px-2 py-0.5 rounded border border-border">Human-Verified AI</span>
          </div>
        </div>

        {/* Right: demo account shortcuts */}
        <div className="space-y-3 pt-2">
          <div className="text-gray-800 text-sm font-medium mb-1 px-1">Quick demo sign-in</div>
          <p className="text-xs text-text-muted px-1 mb-3 leading-relaxed">
            For evaluators: these fill in a real demo account's credentials below &mdash; the platform still
            authenticates normally and assigns permissions from the account record, not from which card you pick.
          </p>
          {DEMO_ACCOUNTS.map((acc) => (
            <button
              key={acc.code}
              type="button"
              onClick={() => {
                setEmployeeCode(acc.code);
                setPassword(acc.password);
                setError(null);
              }}
              className="w-full text-left bg-surface/95 border border-border rounded-xl p-4 flex items-start gap-3 hover:border-primary/50 hover:shadow-sm transition-all"
            >
              <div className="w-9 h-9 rounded-lg bg-info-bg text-info flex items-center justify-center shrink-0">
                <iconify-icon icon={acc.icon} width="18"></iconify-icon>
              </div>
              <div className="min-w-0">
                <div className="text-sm font-semibold text-text-main">{acc.role}</div>
                <div className="text-xs text-text-muted mt-0.5">{acc.desc}</div>
                <div className="text-[11px] font-mono text-text-muted mt-1">{acc.code}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
