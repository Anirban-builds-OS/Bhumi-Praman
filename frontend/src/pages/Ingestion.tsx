import { useCallback, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import * as api from "../services/api";
import { apiErrorMessage } from "../services/api";
import { Card } from "../components/Badges";
import { bytesToSize, formatDate } from "../utils/format";
import type { DocumentOut } from "../types";

const ACCEPTED_TYPES = ["application/pdf", "image/jpeg", "image/png"];
const ACCEPTED_EXT = ".pdf,.jpg,.jpeg,.png";

const STATUS_META: Record<DocumentOut["status"], { icon: string; label: string; tone: string }> = {
  uploaded: { icon: "lucide:upload", label: "Uploaded &mdash; awaiting processing", tone: "text-info" },
  processing: { icon: "lucide:loader-2", label: "AI processing…", tone: "text-warning" },
  processed: { icon: "lucide:check-circle-2", label: "Processed", tone: "text-success" },
  failed: { icon: "lucide:x-circle", label: "Processing failed", tone: "text-error" },
};

export default function Ingestion() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const qc = useQueryClient();
  const navigate = useNavigate();

  const { data: documents } = useQuery({ queryKey: ["documents"], queryFn: api.listDocuments, refetchInterval: 5000 });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadDocument(file, setUploadProgress),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      setUploadProgress(null);
    },
    onError: (err) => {
      setUploadError(apiErrorMessage(err));
      setUploadProgress(null);
    },
  });

  const processMutation = useMutation({
    mutationFn: (id: number) => api.processDocument(id),
    onSuccess: (result) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["dashboard-stats"] });
      if (result.land_record_ids.length === 1) {
        navigate(`/verify/${result.land_record_ids[0]}`);
      }
    },
  });

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    setUploadError(null);
    if (!ACCEPTED_TYPES.includes(file.type)) {
      setUploadError("Unsupported file type. Please upload a PDF, JPG, or PNG.");
      return;
    }
    if (file.size > 50 * 1024 * 1024) {
      setUploadError("File exceeds the 50MB limit.");
      return;
    }
    uploadMutation.mutate(file);
  }, [uploadMutation]);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="font-serif text-2xl font-semibold text-primary mb-1">Bulk Ingestion</h1>
      <p className="text-sm text-text-muted mb-8">Upload scanned land records for AI-assisted digitization. PDF, JPG, or PNG &middot; min. 200 DPI recommended.</p>

      <Card
        className={`drop-zone ${dragActive ? "drop-zone-active" : ""} p-12 text-center cursor-pointer mb-8`}
        onDragOver={(e: React.DragEvent) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e: React.DragEvent) => { e.preventDefault(); setDragActive(false); handleFiles(e.dataTransfer.files); }}
        onClick={() => inputRef.current?.click()}
      >
        <input ref={inputRef} type="file" accept={ACCEPTED_EXT} className="hidden" onChange={(e) => handleFiles(e.target.files)} />
        <div className="w-14 h-14 rounded-full bg-info-bg text-primary flex items-center justify-center mx-auto mb-4">
          <iconify-icon icon="lucide:upload-cloud" width="26"></iconify-icon>
        </div>
        <p className="text-sm font-medium text-text-main">Drag &amp; drop a document, or click to browse</p>
        <p className="text-xs text-text-muted mt-1">Accepted: PDF, JPG, PNG &middot; up to 50MB</p>

        {uploadProgress !== null && (
          <div className="mt-6 max-w-xs mx-auto">
            <div className="h-1.5 bg-bg-alt rounded-full overflow-hidden">
              <div className="h-full bg-primary transition-all" style={{ width: `${uploadProgress}%` }} />
            </div>
            <p className="text-xs text-text-muted mt-1.5">Uploading… {uploadProgress}%</p>
          </div>
        )}
        {uploadError && (
          <p className="mt-4 text-sm text-error flex items-center justify-center gap-1.5">
            <iconify-icon icon="lucide:alert-circle" width="14"></iconify-icon>{uploadError}
          </p>
        )}
      </Card>

      <h2 className="text-sm font-semibold text-text-main mb-3">Recent Uploads</h2>
      <div className="space-y-2">
        {documents?.length === 0 && <p className="text-sm text-text-muted">No documents uploaded yet.</p>}
        {documents?.map((doc) => {
          const meta = STATUS_META[doc.status];
          return (
            <Card key={doc.id} className="p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-bg-alt flex items-center justify-center shrink-0">
                <iconify-icon icon={doc.content_type === "application/pdf" ? "lucide:file-text" : "lucide:image"} width="18" style={{ color: "#6b6560" }}></iconify-icon>
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium text-text-main truncate">{doc.original_filename}</div>
                <div className="text-xs text-text-muted">
                  {bytesToSize(doc.file_size_bytes)} &middot; {doc.page_count} page{doc.page_count !== 1 ? "s" : ""} &middot; {formatDate(doc.uploaded_at)}
                </div>
                {doc.error_message && <div className="text-xs text-error mt-1">{doc.error_message}</div>}
              </div>
              <div className={`flex items-center gap-1.5 text-xs font-medium shrink-0 ${meta.tone}`}>
                <iconify-icon icon={meta.icon} className={doc.status === "processing" ? "animate-spin" : ""} width="14"></iconify-icon>
                <span dangerouslySetInnerHTML={{ __html: meta.label }} />
              </div>
              {doc.status === "uploaded" && (
                <button
                  onClick={() => processMutation.mutate(doc.id)}
                  disabled={processMutation.isPending}
                  className="shrink-0 flex items-center gap-1.5 bg-primary text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-60"
                >
                  <iconify-icon icon="lucide:play" width="13"></iconify-icon>
                  Process
                </button>
              )}
              {doc.status === "processed" && doc.pages[0] && (
                <button
                  onClick={() => navigate(`/records?document=${doc.id}`)}
                  className="shrink-0 flex items-center gap-1.5 border border-border text-text-main text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-bg-alt transition-colors"
                >
                  View Records
                </button>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
