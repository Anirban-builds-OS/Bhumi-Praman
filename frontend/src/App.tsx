import { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./hooks/useAuth";
import AppLayout from "./layouts/AppLayout";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Ingestion from "./pages/Ingestion";
import VerificationQueue from "./pages/VerificationQueue";
import VerificationWorkspace from "./pages/VerificationWorkspace";
import RecordsArchive from "./pages/RecordsArchive";
import RecordDetail from "./pages/RecordDetail";
import AuditTrail from "./pages/AuditTrail";

// Code-split the two heaviest pages (Leaflet and Recharts pull in a lot of
// weight neither page 1 nor most sessions need immediately).
const GisExplorer = lazy(() => import("./pages/GisExplorer"));
const Analytics = lazy(() => import("./pages/Analytics"));

function PageFallback() {
  return <div className="p-8 text-sm text-text-muted">Loading…</div>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />

          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/ingest" element={<Ingestion />} />
            <Route path="/verify" element={<VerificationQueue />} />
            <Route path="/verify/:recordId" element={<VerificationWorkspace />} />
            <Route path="/records" element={<RecordsArchive />} />
            <Route path="/records/:recordId" element={<RecordDetail />} />
            <Route path="/gis" element={<Suspense fallback={<PageFallback />}><GisExplorer /></Suspense>} />
            <Route path="/analytics" element={<Suspense fallback={<PageFallback />}><Analytics /></Suspense>} />
            <Route path="/audit" element={<AuditTrail />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
