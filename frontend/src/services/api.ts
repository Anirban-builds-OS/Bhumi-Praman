import axios from "axios";
import type {
  AuditLogOut, DashboardStats, DocumentOut, EvaluationReport, ExtractionOut,
  FieldName, GisRecord, LandRecordOut, PaginatedRecords, User,
} from "../types";

const client = axios.create({ baseURL: "/api" });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("bp_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("bp_token");
      localStorage.removeItem("bp_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export function apiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (err.request && !err.response) return "Can't reach the server. Is the backend running?";
  }
  return "Something went wrong. Please try again.";
}

// --- Auth ---
export async function login(employee_code: string, password: string, stay_signed_in: boolean) {
  const { data } = await client.post("/auth/login", { employee_code, password, stay_signed_in });
  return data as { access_token: string; user: User; expires_in_minutes: number };
}
export async function me() {
  const { data } = await client.get("/auth/me");
  return data as User;
}

// --- Documents ---
export async function uploadDocument(file: File, onProgress?: (pct: number) => void) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await client.post("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (evt) => {
      if (onProgress && evt.total) onProgress(Math.round((evt.loaded / evt.total) * 100));
    },
  });
  return data as DocumentOut;
}
export async function listDocuments() {
  const { data } = await client.get("/documents");
  return data as DocumentOut[];
}
export async function getDocument(id: number) {
  const { data } = await client.get(`/documents/${id}`);
  return data as DocumentOut;
}
export async function processDocument(id: number) {
  const { data } = await client.post(`/documents/${id}/process`);
  return data as { document: DocumentOut; extractions: ExtractionOut[]; land_record_ids: number[] };
}
// export function pageImageUrl(documentId: number, pageId: number) {
//   const token = localStorage.getItem("bp_token");
//   return `/api/documents/${documentId}/pages/${pageId}/image?t=${token ? token.slice(-8) : ""}`;
// }
export function pageImageUrl(documentId: number, pageId: number) {
  return `/api/documents/${documentId}/pages/${pageId}/image`;
}

// --- Records ---
export interface RecordSearchQuery {
  query?: string; status?: string; district?: string; tehsil?: string; village?: string;
  needs_review_only?: boolean; page?: number; page_size?: number;
}
export async function listRecords(params: RecordSearchQuery) {
  const { data } = await client.get("/records", { params });
  return data as PaginatedRecords;
}
export async function getRecord(id: number) {
  const { data } = await client.get(`/records/${id}`);
  return data as LandRecordOut;
}
export async function editField(recordId: number, field: FieldName, value: string | null, action: "edit" | "accept" | "reject") {
  const { data } = await client.post(`/records/${recordId}/fields`, { field, value, action });
  return data as LandRecordOut;
}
export async function revalidateRecord(recordId: number) {
  const { data } = await client.post(`/records/${recordId}/validate`);
  return data as LandRecordOut;
}
export async function verifyRecord(recordId: number, notes?: string) {
  const { data } = await client.post(`/records/${recordId}/verify`, { notes });
  return data as LandRecordOut;
}
export async function rejectRecord(recordId: number, reason: string) {
  const { data } = await client.post(`/records/${recordId}/reject`, { reason });
  return data as LandRecordOut;
}

// --- Analytics ---
export async function getDashboardStats() {
  const { data } = await client.get("/dashboard/statistics");
  return data as DashboardStats;
}
export async function runEvaluation() {
  const { data } = await client.post("/evaluation/run");
  return data as EvaluationReport;
}

// --- GIS ---
export async function getGisRecords(params?: { district?: string; status_filter?: string }) {
  const { data } = await client.get("/gis/records", { params });
  return data as GisRecord[];
}

// --- Reports ---
export async function generateReport(recordId: number) {
  const res = await client.post(`/reports/${recordId}`, null, { responseType: "blob" });
  return res.data as Blob;
}

// --- Audit ---
export async function listAuditLog(params?: { entity_type?: string; action?: string; limit?: number }) {
  const { data } = await client.get("/audit", { params });
  return data as AuditLogOut[];
}
export async function getRecordAuditTrail(recordId: number) {
  const { data } = await client.get(`/audit/records/${recordId}`);
  return data as AuditLogOut[];
}

export default client;
