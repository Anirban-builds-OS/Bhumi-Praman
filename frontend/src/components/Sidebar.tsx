import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/dashboard", icon: "lucide:layout-dashboard", label: "Dashboard" },
  { to: "/verify", icon: "lucide:clipboard-check", label: "Verification Queue" },
  { to: "/ingest", icon: "lucide:upload-cloud", label: "Bulk Ingestion" },
  { to: "/records", icon: "lucide:archive", label: "Archive Registry" },
  { to: "/gis", icon: "lucide:map", label: "GIS Explorer" },
  { to: "/analytics", icon: "lucide:bar-chart-3", label: "State Reports" },
  { to: "/audit", icon: "lucide:history", label: "Audit Trails" },
];

const ROLE_LABEL: Record<string, string> = {
  administrator: "System Administrator",
  verification_officer: "Verification Officer",
  record_officer: "Record Officer",
};

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 bg-primary text-white flex flex-col">
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/10">
        <div className="w-9 h-9 rounded bg-accent/90 rotate-45 flex items-center justify-center shrink-0">
          <div className="-rotate-45">
            <iconify-icon icon="lucide:compass" width="18" style={{ color: "#1e3a5f" }}></iconify-icon>
          </div>
        </div>
        <div>
          <div className="font-serif font-semibold text-[15px] leading-tight tracking-wide">BHUMI PRAMAN</div>
          <div className="text-[10px] uppercase tracking-wider text-white/50">SIH 2026 &middot; PS 26018</div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5 hover:text-white"
              }`
            }
          >
            <iconify-icon icon={item.icon} width="18"></iconify-icon>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-3 py-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="w-8 h-8 rounded-full bg-accent/90 flex items-center justify-center text-primary font-semibold text-sm shrink-0">
            {user?.full_name?.charAt(0) ?? "?"}
          </div>
          <div className="min-w-0">
            <div className="text-sm font-medium truncate">{user?.full_name}</div>
            <div className="text-[11px] text-white/50 truncate">{user ? ROLE_LABEL[user.role] : ""}</div>
          </div>
        </div>
        <button
          onClick={() => {
            logout();
            navigate("/login");
          }}
          className="mt-2 w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-white/60 hover:bg-white/5 hover:text-white transition-colors"
        >
          <iconify-icon icon="lucide:log-out" width="16"></iconify-icon>
          Sign out
        </button>
      </div>
    </aside>
  );
}
