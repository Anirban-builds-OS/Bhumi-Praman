import { Link } from "react-router-dom";

const WORKFLOW_STEPS = [
  { icon: "lucide:upload-cloud", title: "Upload", desc: "Scanned records, PDFs, or photographs of Khatauni/Record-of-Rights documents." },
  { icon: "lucide:scan-line", title: "AI/OCR Pipeline", desc: "Preprocessing, multilingual OCR, and structured field extraction with per-field confidence." },
  { icon: "lucide:shield-check", title: "Validation", desc: "Format checks, duplicate detection, and possible ownership-conflict flags." },
  { icon: "lucide:user-check", title: "Human Verification", desc: "An officer reviews, corrects, and signs off on every low-confidence field before a record counts as official." },
  { icon: "lucide:database", title: "Searchable Record", desc: "Verified records are searchable, mapped, auditable, and exportable as an official PDF." },
];

const CAPABILITIES = [
  { icon: "lucide:languages", title: "Multilingual OCR", desc: "English, Hindi, and Assamese text recognition on printed documents, with confidence-scored, human-verified extraction." },
  { icon: "lucide:target", title: "Confidence-Scored Extraction", desc: "Every field carries a transparent confidence score blending pattern match and OCR quality \u2014 nothing is presented as certain when it isn't." },
  { icon: "lucide:copy-warning", title: "Duplicate & Conflict Detection", desc: "Flags possible duplicate parcels and possible ownership conflicts for human review \u2014 never an automatic determination." },
  { icon: "lucide:map", title: "GIS Visualization", desc: "Map verified records against their village/tehsil/district for coverage and spatial context." },
  { icon: "lucide:history", title: "Full Audit Trail", desc: "Every upload, edit, verification, and rejection is logged \u2014 who, what, and when." },
  { icon: "lucide:file-down", title: "Official Report Export", desc: "Generate a branded PDF summary of any verified record, including its integrity hash." },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-bg-page">
      <header className="border-b border-border bg-surface/90 backdrop-blur sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-primary rotate-45 flex items-center justify-center shrink-0">
              <div className="-rotate-45"><iconify-icon icon="lucide:compass" width="18" style={{ color: "#d4a574" }}></iconify-icon></div>
            </div>
            <span className="font-serif font-semibold text-lg text-primary">Bhumi Praman</span>
          </div>
          <Link to="/login" className="bg-primary text-white text-sm font-medium px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors">
            Access Platform
          </Link>
        </div>
      </header>

      <section className="cadastral-grid border-b border-border">
        <div className="max-w-4xl mx-auto px-6 py-20 text-center">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-info-bg text-info text-xs font-medium mb-6">
            <iconify-icon icon="lucide:sparkles" width="13"></iconify-icon> Smart India Hackathon 2026 &middot; Problem Statement 26018
          </div>
          <h1 className="font-serif text-4xl md:text-5xl font-semibold text-primary leading-tight mb-5">
            Intelligent Land Record<br />Digitization &amp; Validation
          </h1>
          <p className="text-text-muted text-lg max-w-2xl mx-auto mb-8 leading-relaxed">
            AI-assisted extraction turns scanned and legacy land records into structured, searchable, validated
            digital records &mdash; while keeping trained officers in control of every verification.
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link to="/login" className="bg-primary text-white text-sm font-medium px-6 py-3 rounded-lg hover:bg-primary-dark transition-colors flex items-center gap-2">
              Access Platform <iconify-icon icon="lucide:arrow-right" width="15"></iconify-icon>
            </Link>
          </div>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-6 py-16">
        <h2 className="font-serif text-2xl font-semibold text-primary text-center mb-2">How It Works</h2>
        <p className="text-text-muted text-center mb-10">From a scanned document to a verified, searchable record.</p>
        <div className="grid md:grid-cols-5 gap-4">
          {WORKFLOW_STEPS.map((step, i) => (
            <div key={step.title} className="text-center relative">
              <div className="w-12 h-12 rounded-full bg-info-bg text-primary flex items-center justify-center mx-auto mb-3">
                <iconify-icon icon={step.icon} width="20"></iconify-icon>
              </div>
              <div className="text-sm font-semibold text-text-main mb-1">{i + 1}. {step.title}</div>
              <p className="text-xs text-text-muted leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-surface border-y border-border">
        <div className="max-w-5xl mx-auto px-6 py-16">
          <h2 className="font-serif text-2xl font-semibold text-primary text-center mb-2">Platform Capabilities</h2>
          <p className="text-text-muted text-center mb-10">Built for real records offices, honest about current limitations.</p>
          <div className="grid md:grid-cols-3 gap-6">
            {CAPABILITIES.map((cap) => (
              <div key={cap.title} className="p-5 rounded-xl border border-border">
                <div className="w-10 h-10 rounded-lg bg-info-bg text-primary flex items-center justify-center mb-3">
                  <iconify-icon icon={cap.icon} width="18"></iconify-icon>
                </div>
                <h3 className="text-sm font-semibold text-text-main mb-1.5">{cap.title}</h3>
                <p className="text-xs text-text-muted leading-relaxed">{cap.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="max-w-3xl mx-auto px-6 py-16 text-center">
        <iconify-icon icon="lucide:shield-alert" width="28" style={{ color: "#d97706" }}></iconify-icon>
        <h2 className="font-serif text-xl font-semibold text-text-main mt-3 mb-2">AI-assisted, not AI-decided</h2>
        <p className="text-sm text-text-muted leading-relaxed">
          No field is treated as final until a human officer reviews it. Low-confidence extractions are routed for
          mandatory manual verification, and the platform never presents simulated or sample output as a measured result.
        </p>
      </section>

      <footer className="border-t border-border bg-surface">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs text-text-muted flex-wrap justify-center">
            <span className="px-2 py-1 rounded border border-border">SIH 2026 &middot; PS 26018</span>
            <span className="px-2 py-1 rounded border border-border">Student Prototype</span>
            <span className="px-2 py-1 rounded border border-border">Human-Verified AI</span>
          </div>
          <p className="text-xs text-text-muted">&copy; 2026 &middot; Built for Smart India Hackathon. Not an official government record system.</p>
        </div>
      </footer>
    </div>
  );
}
