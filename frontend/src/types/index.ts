export type UserRole = "administrator" | "verification_officer" | "record_officer";

export interface User {
  id: number;
  employee_code: string;
  full_name: string;
  role: UserRole;
  jurisdiction: string | null;
  is_active: boolean;
  created_at: string;
}

export interface FieldLocation {
  left: number;
  top: number;
  width: number;
  height: number;
  match_score: number;
}

export type ConfidenceBucket = "high" | "medium" | "low" | "missing";

export interface FieldState {
  value: string | null;
  pattern_confidence: number;
  ocr_confidence: number;
  confidence: number;
  confidence_bucket: ConfidenceBucket;
  needs_human_review: boolean;
  source: "ai" | "officer";
  field_verified: boolean;
  location: FieldLocation | null;
}

export const FIELD_NAMES = [
  "owner_name", "father_name", "survey_number", "khasra_number", "khata_number",
  "plot_area", "village", "tehsil", "district", "land_classification",
  "mutation_number", "registration_number",
] as const;
export type FieldName = (typeof FIELD_NAMES)[number];

export const FIELD_LABELS: Record<FieldName, string> = {
  owner_name: "Owner Name",
  father_name: "Father's / Guardian's Name",
  survey_number: "Survey Number",
  khasra_number: "Khasra Number",
  khata_number: "Khata Number",
  plot_area: "Plot Area",
  village: "Village",
  tehsil: "Tehsil",
  district: "District",
  land_classification: "Land Classification",
  mutation_number: "Mutation Number",
  registration_number: "Registration Number",
};

export interface DocumentPage {
  id: number;
  page_number: number;
  image_path: string;
  image_width: number | null;
  image_height: number | null;
  status: "pending" | "processing" | "processed" | "failed";
  error_message: string | null;
}

export interface DocumentOut {
  id: number;
  original_filename: string;
  content_type: string;
  file_size_bytes: number;
  page_count: number;
  status: "uploaded" | "processing" | "processed" | "failed";
  error_message: string | null;
  batch_label: string | null;
  uploaded_at: string;
  pages: DocumentPage[];
}

export interface OcrWord {
  text: string;
  conf: number;
  left: number;
  top: number;
  width: number;
  height: number;
  line_num: number;
  block_num: number;
}

export interface ExtractionOut {
  id: number;
  document_page_id: number;
  ocr_full_text: string;
  ocr_mean_word_confidence: number;
  deskew_angle_deg: number;
  record_confidence: number;
  auto_approvable: boolean;
  fields: Record<FieldName, FieldState>;
  ocr_words: OcrWord[];
  validation_issues: string[];
  created_at: string;
}

export type RecordStatus = "pending_review" | "verified" | "rejected";

export interface ConflictEntry {
  conflicting_doc_id: string;
  shared_field: string;
  shared_value: string;
}

export interface LandRecordSummary {
  id: number;
  record_code: string;
  status: RecordStatus;
  owner_name: string | null;
  survey_number: string | null;
  khasra_number: string | null;
  khata_number: string | null;
  village: string | null;
  tehsil: string | null;
  district: string | null;
  record_confidence: number;
  has_validation_issues: boolean;
  has_duplicates: boolean;
  has_conflicts: boolean;
  updated_at: string;
}

export interface LandRecordOut {
  id: number;
  record_code: string;
  document_page_id: number | null;
  document_id: number | null;
  extraction_id: number | null;
  status: RecordStatus;
  page_image_width: number | null;
  page_image_height: number | null;
  owner_name: string | null;
  father_name: string | null;
  survey_number: string | null;
  khasra_number: string | null;
  khata_number: string | null;
  plot_area: string | null;
  village: string | null;
  tehsil: string | null;
  district: string | null;
  land_classification: string | null;
  mutation_number: string | null;
  registration_number: string | null;
  latitude: number | null;
  longitude: number | null;
  fields: Record<FieldName, FieldState>;
  validation_issues: string[];
  duplicate_of: string[];
  conflicts: ConflictEntry[];
  record_confidence: number;
  verification_hash: string | null;
  rejection_reason: string | null;
  created_by_id: number | null;
  verified_by_id: number | null;
  verified_by_name: string | null;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedRecords {
  items: LandRecordSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface AuditLogOut {
  id: number;
  actor_name_snapshot: string;
  action: string;
  entity_type: string;
  entity_id: number | null;
  field_name: string | null;
  old_value: string | null;
  new_value: string | null;
  notes: string | null;
  created_at: string;
}

export interface DashboardStats {
  total_documents: number;
  total_pages_processed: number;
  total_records: number;
  verified_records: number;
  pending_review_records: number;
  rejected_records: number;
  low_confidence_records: number;
  validation_conflicts: number;
  duplicate_flags: number;
  pipeline_flow: Record<string, number>;
  district_coverage: { district: string; total: number; verified: number; pct: number }[];
  recent_activity: AuditLogOut[];
}

export interface GisRecord {
  id: number;
  record_code: string;
  status: RecordStatus;
  owner_name: string | null;
  khasra_number: string | null;
  survey_number: string | null;
  village: string | null;
  tehsil: string | null;
  district: string | null;
  plot_area: string | null;
  latitude: number;
  longitude: number;
}

export interface EvaluationReport {
  documents_evaluated: number;
  mean_cer: number;
  macro_average_f1: number;
  field_metrics: Record<string, { precision: number; recall: number; f1: number; support: number }>;
  confidence_calibration: Record<string, { count: number; accuracy_when_bucket_used: number }>;
  per_document: Record<string, unknown>[];
}
