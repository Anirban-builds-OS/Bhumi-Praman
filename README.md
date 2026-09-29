# Bhumi Praman

### Intelligent Land Record Digitization & Validation System

**Smart India Hackathon 2026 · Problem Statement 26018 · Ministry of Rural Development**

> **AI extracts. Rules validate. Evidence explains. Humans certify.**

Bhumi Praman is an AI-assisted platform for transforming scanned, handwritten, multilingual, and legacy land records into **structured, searchable, validated, traceable, and verifiable digital records**.

It is designed as an **intelligence and verification layer around existing land-record infrastructure**, not as a replacement for government LRMS/DILRMP systems.

**Bhumi** = land · **Praman** = proof / verification

---

## Why Bhumi Praman?

Land-record digitization is not just an OCR problem.

A production-oriented system must answer four questions for every important field:

1. **What did the document say?**
2. **How confidently was it extracted?**
3. **Does it agree with related land records and spatial evidence?**
4. **Who reviewed and certified the final value?**

Bhumi Praman therefore moves beyond:

```text
SCAN → OCR → DATABASE
```

towards:

```text
DOCUMENT
   ↓
UNDERSTAND
   ↓
EXTRACT
   ↓
SCORE
   ↓
VALIDATE
   ↓
RECONCILE
   ↓
VERIFY
   ↓
PROVENANCE
   ↓
TRUSTED RECORD
```

---

# 1. Problem Statement

**SIH 2026 — PS 26018: Intelligent Land Record Digitization and Validation System**

Legacy land records can exist as:

- scanned Record-of-Rights / Khatauni documents
- handwritten registers
- degraded images
- legacy PDFs
- multilingual records
- semi-structured forms
- mutation registers
- deeds and related supporting documents
- cadastral maps and spatial references

A digitization system must preserve the connection between the **source document**, **machine-extracted information**, **validation evidence**, and **human verification**.

Bhumi Praman is built around that principle.

---

# 2. Core Design Principle

> **AI is an assistant, not the authority.**

The platform separates machine inference from official verification:

```text
AI output
   ↓
"Probable value"
   ↓
Confidence + evidence + validation
   ↓
Human officer review
   ↓
Verified value
```

No machine-generated value should be treated as an official/legal determination merely because its confidence score is high.

---

# 3. Product Workflow

```mermaid
flowchart TD
    A[Document Upload] --> B[Preprocessing]
    B --> C[Document & Language Classification]
    C --> D[OCR / HTR]
    D --> E[Structured Field Extraction]
    E --> F[Field-Level Confidence]
    F --> G[Source Evidence Linking]
    G --> H[Validation & Anomaly Detection]
    H --> I[Cross-Record Reconciliation]
    I --> J[Cadastral / GIS Consistency]
    J --> K[Verification Priority Queue]
    K --> L[Human Verification]
    L --> M[Versioned Verified Record]
    M --> N[Audit Trail & Integrity]
    N --> O[Reports / Search / GIS]
    N --> P[Citizen Verification]
```

---

# 4. Current Prototype — Implemented

The current repository already provides the core end-to-end workflow.

| Capability | Current Status |
|---|---|
| Document upload: PDF / JPG / PNG | ✅ Implemented |
| OpenCV preprocessing | ✅ Implemented |
| Tesseract OCR | ✅ Implemented |
| OCR confidence + bounding boxes | ✅ Implemented |
| Structured field extraction | ✅ Implemented |
| 12 Record-of-Rights fields | ✅ Implemented |
| Field-level confidence | ✅ Implemented |
| Source-document field highlighting | ✅ Implemented |
| Required/format validation | ✅ Implemented |
| Duplicate / ownership-conflict flags | ✅ Implemented |
| Human verification workspace | ✅ Implemented |
| Server-side RBAC | ✅ Implemented |
| Audit logging | ✅ Implemented |
| Search / archive registry | ✅ Implemented |
| GIS prototype | ✅ Implemented |
| Live evaluation re-run | ✅ Implemented |
| PDF report generation | ✅ Implemented |
| SHA-256 record integrity fingerprint | ✅ Implemented |
| SQLite / PostgreSQL configuration | ✅ Implemented |
| Backend tests | ✅ Implemented |
| Docker deployment starting point | ✅ Present; validate locally |

---

# 5. Differentiated Intelligence Layer

The following capabilities form the **next intelligence layer** of Bhumi Praman. They are deliberately separated from the already-working prototype so the README never confuses a planned capability with a demonstrated one.

## 5.1 Document Intelligence & Quality Gate

Before OCR, classify the incoming document.

### Inputs

- document type
- page count
- language/script
- orientation
- scan quality
- layout
- table structure
- handwriting likelihood

### Proposed routing

```text
Incoming Document
      ↓
Quality Gate
      ↓
Document Type
      ↓
Language / Script
      ↓
Layout Detection
      ↓
OCR / HTR Route
```

Possible document classes:

- Record of Rights
- Khatauni / Jamabandi
- Mutation register
- Sale deed
- Patta / regional extract
- Cadastral map
- supporting document

This prevents every document from being forced through the same extraction schema.

---

# 6. Advanced Document Processing

## 6.1 Preprocessing Pipeline

The current pipeline already performs core preprocessing. The extensible pipeline can expand to:

```text
Input
 ↓
Orientation Detection
 ↓
Deskew
 ↓
Denoise
 ↓
Grayscale
 ↓
Contrast Enhancement / CLAHE
 ↓
Adaptive Thresholding
 ↓
Background Cleanup
 ↓
Border Removal
 ↓
Crop / Region Detection
 ↓
Resolution Enhancement
 ↓
Quality Score
```

A quality gate can route unreadable pages to manual inspection instead of producing misleading OCR.

### Proposed technical components

- OpenCV
- Pillow
- NumPy
- Hough/minAreaRect orientation detection
- Otsu / adaptive thresholding
- Laplacian-based blur measurement
- configurable preprocessing profiles

---

# 7. Multilingual OCR & Handwriting Recognition

## Current

- Tesseract / pytesseract
- multilingual language packs
- OCR bounding boxes
- OCR confidence

## Upgrade path

A provider-agnostic OCR adapter can support:

- Tesseract
- PaddleOCR
- RapidOCR / ONNX
- TrOCR / Indic HTR
- other approved Indic-language OCR services

```text
                 OCR Router
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Tesseract   PaddleOCR   Indic HTR
        │           │           │
        └───────────┼───────────┘
                    ▼
              Normalized OCR
```

Routing can use:

- language/script
- document type
- handwriting probability
- image quality
- model availability
- latency requirements

### Indic normalization

The extraction layer should also support:

- transliteration
- numeral normalization
- date normalization
- unit normalization
- Unicode normalization
- script variants

---

# 8. Structured Land-Record Extraction

The current schema supports 12 Record-of-Rights fields.

The extensible canonical schema can include:

| Category | Example fields |
|---|---|
| Identity | Owner name, guardian/father name |
| Parcel | Survey no., Khasra no., Khata no., plot no. |
| Area | Recorded area, unit, normalized area |
| Administrative | Village, tehsil, district, state |
| Classification | Agricultural / residential / other |
| Ownership | Ownership type, share |
| Mutation | Mutation number, mutation date |
| Registration | Registration reference, date |
| Temporal | Record date, effective-from, effective-to |
| Spatial | Parcel identifier, geometry reference |
| Provenance | Source document, page, evidence region |
| Verification | Status, verifier, verification time |

### Hybrid extraction architecture

Use deterministic extraction where rules are reliable and semantic extraction where context matters:

```text
OCR Output
   │
   ├── Deterministic fields
   │      ├── dates
   │      ├── survey IDs
   │      ├── mutation IDs
   │      ├── numbers
   │      └── units
   │
   └── Semantic fields
          ├── owner
          ├── guardian/father
          ├── classification
          └── ownership context
```

The two paths are merged through a field-ownership schema so that a semantic model cannot silently overwrite a deterministic value.

---

# 9. Field-Level Confidence Engine

The existing system already provides field-level confidence.

The upgraded design treats confidence as a **multi-signal explanation**, not a single black-box number.

Possible signals:

```text
OCR Confidence
      +
Extraction Confidence
      +
Pattern / Format Validity
      +
Context Agreement
      +
Cross-Record Agreement
      +
Evidence Quality
      +
Spatial Agreement
      ↓
Field Confidence
```

Every score should also expose a machine-readable explanation.

Example:

```json
{
  "field": "survey_number",
  "value": "124/3",
  "confidence": 0.94,
  "signals": {
    "ocr": 0.98,
    "pattern_match": 0.95,
    "cross_record": 0.91
  },
  "reason": "OCR and survey-number pattern agree; one related record differs."
}
```

> Confidence is decision support, not legal proof.

---

# 10. Evidence-Backed Extraction

One of Bhumi Praman's strongest existing capabilities is source highlighting.

The upgraded model makes this a formal provenance layer:

```text
Original Scan
     ↓
Page
     ↓
OCR Span
     ↓
Bounding Box
     ↓
Extracted Field
     ↓
Validation Result
     ↓
Officer Correction
     ↓
Verified Value
```

### Evidence object

Each important field can reference:

- source document ID
- page number
- bounding box
- OCR text span
- OCR model/run ID
- extraction run ID
- confidence
- validation findings
- reviewer action

This makes the question **"Why is this value in the database?"** answerable.

---

# 11. Validation & Anomaly Engine

Validation should operate at multiple levels.

## Field-level validation

- required fields
- field formats
- date validity
- numeric validity
- allowed classifications
- identifier patterns

## Record-level validation

- area > 0
- internal field consistency
- owner/share totals
- administrative hierarchy
- mutation/record-date consistency

## Cross-record validation

- duplicate record
- owner conflict
- survey/Khasra conflict
- area mismatch
- temporal inconsistency
- mutation discontinuity

## Spatial validation

- parcel identifier mismatch
- geometry overlap
- topology errors
- document/GIS area mismatch

### Example anomaly object

```json
{
  "type": "AREA_MISMATCH",
  "severity": "HIGH",
  "record_id": "REC-1024",
  "expected": 10.0,
  "observed": 10.5,
  "unit": "acre",
  "evidence": [
    "parent_record:REC-1001",
    "child_record:REC-1024"
  ],
  "requires_review": true
}
```

---

# 12. Regional Land-Unit Normalization

Land-area values must be normalized before mathematical comparison.

Examples:

```text
Bigha
Biswa
Acre
Hectare
Square metre
Square feet
```

The target normalization layer should:

1. identify source unit
2. identify jurisdiction/profile
3. convert to canonical unit
4. preserve original value
5. preserve conversion provenance

For mathematically sensitive operations, use decimal arithmetic rather than floating-point approximations.

```text
Original:
2.50 Bigha

       ↓

Jurisdiction-specific conversion

       ↓

Canonical:
Normalized Area

       ↓

Reconciliation Engine
```

No conversion should be assumed universally valid across jurisdictions where local definitions differ.

---

# 13. Cross-Document Reconciliation Engine

This is one of the main differentiators of the proposed Bhumi Praman architecture.

Instead of:

```text
Document A → Record A
Document B → Record B
```

the system creates relationships:

```text
Document A
    │
    ├── same parcel
    ├── same owner candidate
    ├── mutation relation
    ├── parent parcel
    └── supporting document
          │
          ▼
     Record Graph
```

### Reconciliation dimensions

- owner
- guardian/father
- village
- survey/Khasra
- Khata
- area
- mutation
- registration
- record dates
- parcel lineage

### Match types

```text
EXACT
NORMALIZED
FUZZY
PROBABLE
CONFLICT
UNKNOWN
```

Every relationship carries evidence and confidence.

---

# 14. Ownership & Parcel Timeline

A record should be able to explain its history.

Example:

```text
1998
Original Record
Owner: A
Area: 10.00 acres
      │
      ▼
2005
Mutation
Owner: B
      │
      ▼
2017
Subdivision
10.00 → 4.25 + 5.75
      │
      ▼
2024
Transfer
      │
      ▼
2026
Current Record
```

### Timeline events

- creation
- mutation
- sale/transfer
- subdivision
- amalgamation
- correction
- verification

Every event should point back to one or more source documents.

---

# 15. Area & Subdivision Reconciliation

For parcel hierarchies:

```text
Parent Parcel
      │
      ├── Child 1
      ├── Child 2
      └── Child 3
```

The reconciliation rule becomes:

```text
SUM(child areas) ≈ parent area
```

with configurable tolerance.

Example:

```text
Parent: 10.00 acres
Children: 3.25 + 2.75 + 4.50
Total: 10.50 acres

→ AREA RECONCILIATION FAILURE
→ HIGH PRIORITY REVIEW
```

The original area and normalized area must both remain available for auditability.

---

# 16. Entity Resolution

Names vary across legacy records.

Example:

```text
Ramesh Kumar
Ramesh Kr.
Ramesh Kumar S/O Mohan
रमेश कुमार
```

Entity resolution should compare multiple attributes instead of relying only on name similarity:

- normalized name
- transliteration
- guardian/father name
- village
- address
- parcel references
- historical relationships

### Result

```text
Candidate Entity Match
       ↓
Similarity: 0.91
       ↓
Supporting evidence:
✓ Same village
✓ Same father name
✓ Same Khasra
⚠ Name spelling variation
       ↓
Human confirmation required
```

This is **record linkage**, not automated identity proof.

---

# 17. Multi-Page Record Intelligence

Instead of processing every page as an unrelated record:

```text
12-page PDF
    ↓
Page Classification
    ↓
Page Ordering
    ↓
Record Grouping
    ↓
Cross-Page References
    ↓
Unified Record
```

Possible page classes:

- header/title page
- owner table
- mutation section
- parcel details
- continuation page
- annexure
- map page

This is particularly important for long revenue registers.

---

# 18. Cadastral & GIS Consistency

The GIS layer should not be only a visualization.

The target system uses spatial data as another validation signal.

```text
Land Record
Survey/Khasra + Area
       │
       ▼
Parcel Linker
       │
       ▼
GIS / PostGIS
       │
       ├── ID agreement
       ├── Area agreement
       ├── Spatial overlap
       └── Topology checks
```

### Spatial technology path

- Leaflet for web visualization
- GeoJSON for exchange
- PostgreSQL + PostGIS for spatial storage
- GeoServer for service publishing
- QGIS for administrative/spatial data preparation

> Current map coordinates are prototype/demo locations, not authoritative cadastral boundaries.

---

# 19. Anomaly Center

All validation signals should converge into one review-oriented view.

### Anomaly classes

| Category | Examples |
|---|---|
| Identity | entity mismatch / ambiguous name |
| Parcel | Khasra conflict / duplicate parcel |
| Area | unit or subdivision mismatch |
| Temporal | mutation/date discontinuity |
| Document | poor scan / missing page |
| Spatial | geometry overlap / parcel mismatch |
| Extraction | low OCR / low field confidence |

### Severity

```text
CRITICAL
HIGH
MEDIUM
LOW
INFO
```

Each anomaly should answer:

```text
What happened?
Why was it flagged?
What evidence supports it?
What should the officer inspect?
```

---

# 20. Verification Priority Queue

Manual review time is limited.

Instead of treating every record equally, the system can prioritize cases using:

```text
Low confidence
      +
High anomaly severity
      +
Cross-record conflicts
      +
Missing evidence
      +
Record importance
      ↓
Review Priority
```

This creates a practical human-in-the-loop workflow where officers see the most uncertain and inconsistent cases first.

---

# 21. Verification Workspace

The existing split-screen workspace can be expanded into a structured decision console.

```text
┌──────────────────────────┬─────────────────────────────┐
│                          │                             │
│     SOURCE DOCUMENT      │      STRUCTURED RECORD      │
│                          │                             │
│  Zoom / Rotate / Page    │  Owner       [96%]          │
│  OCR overlay             │  Khasra      [91%] ⚠        │
│  Evidence region         │  Area        [54%] ⚠        │
│                          │                             │
│                          │  Validation: 2 issues        │
│                          │                             │
│                          │  [Accept] [Edit] [Reject]   │
│                          │                             │
└──────────────────────────┴─────────────────────────────┘
```

### Review controls

- per-field accept/edit/reject
- source evidence jump
- validation explanation
- conflict explanation
- correction reason
- reviewer identity
- verification timestamp
- previous-value comparison

---

# 22. Maker–Checker Verification

For higher assurance workflows, use separation of responsibilities.

```text
Operator
   ↓
Digitization
   ↓
Verifier
   ↓
Review
   ↓
Supervisor
   ↓
Final Certification
```

The exact role hierarchy can be configured for the deployment.

This allows the same record to have:

- created by
- corrected by
- verified by
- approved by
- audited by

without collapsing every action into a single user.

---

# 23. Versioned Record History

A verified record should remain historically inspectable.

### Target version model

```text
Record v1
   ↓
Record v2
   ↓
Record v3
   ↓
Current
```

Each revision stores:

- valid-from
- valid-to
- is-current
- edited-by
- changed-fields
- reason
- supporting evidence

A temporal/SCD-Type-2 style model can retain historical versions without overwriting prior verified states.

---

# 24. Evidence Ledger & Provenance

The full evidence chain can be represented as:

```text
SOURCE FILE
    ↓
FILE HASH
    ↓
PROCESSING RUN
    ↓
OCR RESULT
    ↓
EXTRACTED FIELD
    ↓
CONFIDENCE
    ↓
VALIDATION
    ↓
OFFICER CORRECTION
    ↓
VERIFICATION
    ↓
FINAL RECORD
    ↓
REPORT / PUBLIC VERIFICATION
```

### Integrity model

Use:

- SHA-256 document hash
- record hash
- immutable-style append-only event history
- version identifiers
- timestamps
- actor IDs

A hash is an integrity fingerprint; it is **not automatically a legally valid digital signature**.

### Optional integrity extensions

For environments that require stronger tamper-evidence, the provenance layer can be extended with:

- hash chaining across audit events
- Merkle-style evidence aggregation
- signed verification manifests
- optional permissioned blockchain anchoring

Blockchain is an **optional integrity/distribution extension**, not a substitute for validation, source evidence, or human certification.

---

# 25. Fraud & Dispute Intelligence

The target anomaly layer can identify signals associated with:

- possible double entry
- duplicate parcel registration
- owner conflicts
- suspicious area inflation
- unexpected ownership transitions
- conflicting mutation histories
- cadastral overlap

The output should be a **risk flag for investigation**, not a legal finding.

### Example

```text
Parcel: 124/3

⚠ Possible Double Entry

Record A
Owner: X
Date: 2018

Record B
Owner: Y
Date: 2019

Related Khasra: 124/3
Overlap: High
```

---

# 26. Deed / Record Difference Viewer

For related versions of a document or record:

```text
Previous Version        Current Version

Owner: A                Owner: B
Area: 2.40 ha           Area: 3.10 ha
Khasra: 124/3            Khasra: 124/3
```

Highlight:

- changed owners
- changed areas
- changed parcel identifiers
- changed dates
- added/removed clauses
- suspicious numeric changes

This is especially useful when investigating historical changes.

---

# 27. AI-Assisted Correction & Continuous Learning

Officer corrections can become structured learning signals.

```text
AI Prediction
      ↓
Officer Correction
      ↓
Correction Reason
      ↓
Gold Label
      ↓
Evaluation Dataset
      ↓
Model Improvement
      ↓
New Model Version
```

The system should capture:

- original prediction
- corrected value
- field name
- source evidence
- correction reason
- document type
- language
- model version
- reviewer

Future models can then be evaluated against a stable golden set rather than being silently retrained.

---

# 28. AI Quality & Evaluation Dashboard

Accuracy should be measured, not claimed.

### Recommended metrics

| Metric | Purpose |
|---|---|
| CER | OCR character error |
| WER | OCR word error |
| Precision | Extraction correctness |
| Recall | Extraction coverage |
| F1 | Field extraction quality |
| Latency | Processing time |
| Confidence calibration | Whether confidence reflects reality |
| Review rate | Percentage requiring human review |
| Resolution rate | Percentage resolved without escalation |

### Evaluation dimensions

Measure separately by:

- language
- document type
- scan quality
- handwriting vs printed
- field
- model version

---

# 29. Current Evaluation Transparency

The present prototype evaluates a small labelled sample set.

| Metric | Current result |
|---|---:|
| Macro-average field F1 | **0.042** |
| Mean Character Error Rate | **62%** |

These numbers are not presented as production accuracy.

They demonstrate the current weakness of the off-the-shelf OCR/extraction pipeline and provide a baseline for improvement.

The evaluation should remain reproducible through the application's evaluation workflow.

---

# 30. Smart Search & Natural-Language Query Layer

The registry can evolve from field filters to semantic record search.

Examples:

```text
Show verified land owned by Ramesh Kumar in Village X.
```

```text
Find parcels where the current owner differs from the 1990 record.
```

```text
Show records with area mismatches above 5%.
```

```text
Find documents whose Khasra number conflicts with another record.
```

The query layer should translate natural-language requests into constrained database filters and validation predicates rather than allowing unrestricted database generation.

---

# 31. Citizen Verification Portal

A public verification layer can expose only safe, non-sensitive information.

### Flow

```text
Verified Record
      ↓
Verification ID
      ↓
QR Code
      ↓
Public Verification Page
      ↓
Status + Safe Record Metadata
      ↓
Integrity Check
```

The citizen portal should not expose:

- internal confidence diagnostics
- private staff notes
- credentials
- sensitive audit metadata
- protected personal information

---

# 32. Secure Public Certificate

A future certificate can contain:

- Verification ID
- Record reference
- Verification timestamp
- issuing authority metadata
- QR verification link
- SHA-256 integrity fingerprint

The QR endpoint verifies that the presented record corresponds to the stored verification state.

---

# 33. Offline / Low-Connectivity Field Workflow

For rural field environments, a future client can support:

```text
Offline Capture
      ↓
Local Queue
      ↓
Encrypted Local Store
      ↓
Connectivity Restored
      ↓
Sync Queue
      ↓
Server Reconciliation
```

Possible implementation:

- IndexedDB
- service worker
- sync queue
- idempotency keys
- conflict resolution
- resumable uploads

Offline mode should never bypass server-side authorization or verification rules.

---

# 34. Async Processing Architecture

Large multi-page documents should not block API requests.

### Target architecture

```text
Frontend
   ↓
FastAPI
   ↓
Transactional Outbox
   ↓
Redis / Queue
   ↓
Celery Worker
   ↓
AI Processing
   ↓
Database
   ↓
Frontend Status
```

A worker/sweeper can detect orphaned or stuck jobs.

This is preferable to running heavy OCR synchronously inside the request thread.

---

# 35. Integration Architecture

All external systems should sit behind explicit adapters.

```text
                Bhumi Praman Core
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
    LRMS Adapter   DILRMP Adapter   GIS Adapter
       │               │                │
       ▼               ▼                ▼
  State System     Government      Cadastral DB
                    System
```

Possible future integrations:

- DILRMP
- state LRMS
- registration systems
- cadastral GIS
- DigiLocker-style document exchange
- authorized identity/e-sign services
- government webhooks
- public verification APIs

> The current prototype is **integration-ready, not live-integrated** with government systems.

---

# 36. API Architecture

The FastAPI backend can expose:

### Authentication

```text
POST /api/auth/login
POST /api/auth/refresh
```

### Documents

```text
POST /api/documents/upload
POST /api/documents/{id}/process
GET  /api/documents/{id}
```

### Records

```text
GET  /api/records
GET  /api/records/{id}
PATCH /api/records/{id}
```

### Verification

```text
GET  /api/verification/queue
POST /api/records/{id}/verify
POST /api/records/{id}/reject
```

### Evidence / Audit

```text
GET /api/records/{id}/evidence
GET /api/records/{id}/history
GET /api/audit
```

### Evaluation

```text
POST /api/evaluation/run
GET  /api/evaluation/results
```

### Public verification

```text
GET /api/public/verify/{verification_id}
```

Exact endpoints remain implementation-dependent; FastAPI/OpenAPI provides the API contract.

---

# 37. Proposed Data Model

A scalable PostgreSQL/PostGIS deployment can use logical entities such as:

```text
users
documents
document_pages
processing_runs
ocr_spans
records
record_fields
field_evidence
validation_issues
record_relationships
ownership_events
parcel_events
parcel_geometries
entity_candidates
verification_tasks
record_versions
audit_events
model_versions
correction_labels
integration_outbox
public_verification_tokens
```

### Relationship model

```text
Document
  └── Pages
       └── OCR Spans
            └── Evidence
                 └── Record Fields
                      └── Validation
                           └── Verification
                                └── Versioned Record
```

---

# 38. Technology Architecture

## Current Core

| Layer | Current technology |
|---|---|
| Frontend | React 19, TypeScript, Vite |
| UI | Tailwind CSS v4 |
| Routing | React Router |
| Data fetching | TanStack Query / Axios |
| Analytics | Recharts |
| GIS UI | React Leaflet |
| Backend | Python, FastAPI, Uvicorn |
| ORM | SQLAlchemy 2 |
| Validation | Pydantic v2 |
| OCR | Tesseract / pytesseract |
| CV | OpenCV |
| PDF | PyMuPDF |
| Reports | ReportLab |
| Database | SQLite / PostgreSQL |
| Authentication | JWT |
| Password security | bcrypt |
| Testing | pytest, HTTPX, FastAPI TestClient |

## Extended Intelligence Stack

| Capability | Target technologies |
|---|---|
| OCR ensemble | Tesseract, PaddleOCR, RapidOCR / ONNX |
| Handwriting | TrOCR / Indic HTR / optional Sarvam-style provider adapter |
| Vision | OpenCV, YOLOv8 / Detectron2 |
| NLP / NER | spaCy, Hugging Face Transformers |
| Indic NLP | Indic NLP libraries, MuRIL-class models |
| Async processing | Celery + Redis |
| Object storage | S3-compatible / MinIO |
| Spatial DB | PostgreSQL + PostGIS |
| Map services | GeoServer |
| Desktop GIS | QGIS |
| 3D spatial visualization | CesiumJS (optional extension) |
| Search / analytics | PostgreSQL full-text + optional vector/search layer |
| Observability | Grafana + metrics/logging stack |
| Data evaluation | CER, WER, field precision/recall/F1, latency |
| Deployment | Docker / Docker Compose; Kubernetes for larger environments |

---

# 39. Repository Structure

```text
bhumi-praman/
│
├── frontend/
│   ├── src/
│   └── ...
│
├── backend/
│   └── app/
│       ├── api/
│       ├── auth/
│       ├── database/
│       ├── middleware/
│       ├── models/
│       ├── schemas/
│       └── services/
│
├── ai/
│   ├── preprocessing/
│   ├── ocr/
│   ├── extraction/
│   ├── confidence/
│   ├── validator.py
│   ├── generate_samples.py
│   └── tests/
│
├── data/
│   ├── sample_documents/
│   └── evaluation/
│
├── database/
│   └── seed/
│
├── gis/
│
├── storage/
│
├── scripts/
│
├── deployment/
│
├── docs/
│
├── tests/
│
└── README.md
```

---

# 40. Security Model

Current controls include:

- JWT bearer authentication
- bcrypt password hashing
- server-side RBAC
- content-type and size validation
- server-generated filenames
- environment-based secrets
- centralized exception handling
- append-only audit events
- SHA-256 record integrity fingerprints

### Planned production hardening

- HTTPS everywhere
- secret manager / KMS
- encrypted object storage
- database encryption strategy
- key rotation
- stronger session controls
- rate limiting
- security headers
- malware scanning on uploaded files
- immutable/WORM audit storage where required
- centralized logging and monitoring
- backup/restore testing
- formal penetration testing

---

# 41. Privacy & Governance

Land records can contain sensitive personal and administrative information.

The platform should therefore support:

- role-limited field visibility
- least-privilege access
- data minimization for public views
- auditability of every privileged action
- configurable retention policies
- secure document storage
- explicit public/private data boundaries

Citizen-facing verification should expose only the minimum information required for verification.

---

# 42. Current vs Planned vs Integration-Only

| Capability | Status |
|---|---|
| OCR + field extraction | ✅ Current |
| Source highlighting | ✅ Current |
| Human verification | ✅ Current |
| Audit trail | ✅ Current |
| GIS prototype | ✅ Current |
| PDF + SHA-256 | ✅ Current |
| Evaluation dashboard | ✅ Current |
| Advanced Indic HTR | 🔵 Planned |
| OCR ensemble routing | 🔵 Planned |
| Document classification | 🔵 Planned |
| Multi-page record merging | 🔵 Planned |
| Cross-document reconciliation | 🔵 Planned |
| Ownership genealogy | 🔵 Planned |
| Unit normalization | 🔵 Planned |
| Area/subdivision reconciliation | 🔵 Planned |
| Entity resolution | 🔵 Planned |
| Advanced cadastral topology | 🔵 Planned |
| Verification priority queue | 🔵 Planned |
| Active learning dataset loop | 🔵 Planned |
| Natural-language search | 🔵 Planned |
| Citizen QR verification | 🔵 Planned |
| Offline field sync | 🔵 Planned |
| Celery/Redis async workers | 🔵 Planned |
| S3/MinIO object storage | 🔵 Planned |
| PostGIS production deployment | 🔵 Planned |
| GeoServer integration | 🔵 Planned |
| DILRMP/LRMS live integration | 🟣 Integration-only / future |
| Government APIs | 🟣 Integration-only / future |
| Authoritative cadastral boundaries | 🟣 Requires authoritative data source |

**Legend**

- ✅ Implemented and demonstrated
- 🔵 Planned / architecture target
- 🟣 Requires external system/data/authority

---

# 43. Technical Differentiators

## 25.1 Evidence-First

Every important extracted field can point back to the source scan.

## 25.2 Cross-Record, Not Document-Only

Related documents are reconciled instead of being treated as independent OCR jobs.

## 25.3 Temporal Intelligence

Ownership and parcel changes are modeled as events and versions.

## 25.4 Spatial Consistency

GIS becomes a validation signal, not just a map.

## 25.5 Human Certification

AI generates candidates; authorized officers certify the final record.

## 25.6 Explainable Confidence

The system explains why a field received its confidence level.

## 25.7 Measurable Accuracy

CER, WER, field F1, latency, review rate, and error buckets can be tracked over time.

## 25.8 Model Agnostic

OCR/HTR providers are behind adapters, allowing replacement without rewriting the application.

## 25.9 Integration Ready

Existing government systems remain external authorities; Bhumi Praman provides the intelligence layer around them.

---

# 44. From Existing Prototype to Intelligence Platform

The upgrade path is intentionally incremental:

```text
PHASE 1 — CURRENT
OCR
Extraction
Confidence
Validation
Human Verification
Audit
GIS
Reports
      │
      ▼
PHASE 2 — INTELLIGENCE
Document Classification
Multi-page Grouping
Unit Normalization
Entity Resolution
Cross-record Reconciliation
Timeline
Area Reconciliation
      │
      ▼
PHASE 3 — SPATIAL + RISK
PostGIS
Parcel Linking
Topology Checks
Anomaly Center
Fraud/Conflict Signals
Priority Queue
      │
      ▼
PHASE 4 — LEARNING
Correction Dataset
Benchmarking
Model Registry
Retraining
Confidence Calibration
      │
      ▼
PHASE 5 — ECOSYSTEM
Public Verification
QR Certificates
Offline Sync
LRMS/DILRMP Adapters
Government APIs
```

---

# 45. Installation

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Git
- Tesseract OCR
- English + required Indic language packs

### Windows

Install Tesseract and ensure it is either on `PATH` or configured through:

```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Verify:

```powershell
tesseract --list-langs
```

---

# 46. Backend Setup

```powershell
git clone https://github.com/Anirban-builds-OS/Bhumi-Praman.git
cd Bhumi-Praman

copy .env.example .env

cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Seed the local environment:

```powershell
python ..\database\seed\seed.py
```

Start the backend:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

# 47. Frontend Setup

In a separate terminal:

```powershell
cd Bhumi-Praman\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 48. Database

Local development uses SQLite by default.

For PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://user:password@host:5432/bhumi_praman
```

All application access goes through SQLAlchemy, allowing the database backend to be changed without rewriting the API layer.

For production geospatial support:

```text
PostgreSQL
   +
PostGIS
```

---

# 49. API Documentation

FastAPI automatically exposes:

- Swagger UI — `/docs`
- ReDoc — `/redoc`
- OpenAPI schema

This provides an integration surface for future government systems and external clients.

---

# 50. Testing

Current backend tests cover:

- field extraction
- confidence scoring
- field → source matching
- duplicate/conflict detection
- upload → process → verify → report
- RBAC
- evaluation endpoint

Run:

```powershell
cd backend
.\venv\Scripts\Activate.ps1

pytest tests\test_api.py -v
pytest ..\ai\tests\test_pipeline_smoke.py -v
```

Frontend production build:

```bash
cd frontend
npm run build
```

---

# 51. Benchmarking Strategy

A stronger evaluation bench should maintain a versioned golden dataset.

```text
Golden Set
   ↓
Model Version N
   ↓
Evaluation
   ├── CER
   ├── WER
   ├── Field F1
   ├── Precision
   ├── Recall
   ├── Latency
   └── Review Rate
   ↓
Compare with Model Version N+1
```

Recommended evaluation buckets:

- clean scans
- low-resolution scans
- skewed scans
- noisy scans
- printed text
- handwriting
- Hindi
- Assamese
- Bengali
- other configured Indic languages
- different document layouts

---

# 52. Demo Walkthrough

### Existing prototype

1. Sign in using a demo role.
2. Open the dashboard.
3. Upload a PDF/JPG/PNG.
4. Process the document.
5. Inspect the source scan.
6. Inspect field-level OCR/extraction confidence.
7. Click evidence-linked fields.
8. Review validation findings.
9. Accept, edit, or reject fields.
10. Verify the record.
11. Open Archive Registry.
12. View the GIS representation.
13. Generate the PDF report.
14. Inspect the audit trail.
15. Re-run the evaluation dashboard.

### Intelligence-layer demo target

```text
Upload 2–4 related records
        ↓
Extract
        ↓
Link related parcel records
        ↓
Show owner / area / mutation timeline
        ↓
Detect an inconsistency
        ↓
Show source evidence
        ↓
Prioritize verification
        ↓
Officer resolves conflict
        ↓
Create verified version
        ↓
Generate QR verification
```

---

# 53. Limitations

Bhumi Praman is currently a **student prototype**, not a deployed government land-record system.

### Current limitations

- OCR accuracy is currently weak on degraded documents.
- The current OCR engine is based on off-the-shelf Tesseract.
- Handwriting recognition is not yet production-grade.
- The current labelled evaluation set is small.
- GIS positions are prototype/demo locations, not surveyed cadastral parcel boundaries.
- Sample/demo data is fictional/synthetic.
- Live DILRMP/LRMS integration is not implemented.
- Multi-page PDFs are not yet merged into unified cross-page records.
- Frontend automated tests are not yet comprehensive.
- SHA-256 provides integrity evidence, not PKI-based legal non-repudiation.
- Advanced capabilities in this README are explicitly marked as planned unless listed as current.

These limitations are intentional disclosures, not hidden behind marketing claims.

---

# 54. Roadmap

## Near Term

- [ ] OCR ensemble adapter
- [ ] Advanced Indic HTR
- [ ] Document type classifier
- [ ] Multi-page record grouping
- [ ] Unit normalization
- [ ] Cross-document reconciliation
- [ ] Ownership/parcel timeline
- [ ] Area/subdivision reconciliation
- [ ] Entity resolution
- [ ] Anomaly Center
- [ ] Verification priority queue

## Platform

- [ ] PostGIS parcel model
- [ ] GeoServer integration
- [ ] Optional CesiumJS 3D parcel visualization
- [ ] Celery + Redis workers
- [ ] Transactional outbox + job sweeper
- [ ] S3/MinIO document storage
- [ ] SCD-Type-2 record versioning
- [ ] Model registry
- [ ] Correction dataset pipeline
- [ ] Automated benchmark suite

## Citizen & Ecosystem

- [ ] Public verification portal
- [ ] QR-enabled certificate
- [ ] Notification adapters for approved citizen/officer events
- [ ] Public-safe record view
- [ ] Offline field workflow
- [ ] LRMS/DILRMP adapters
- [ ] Government API/webhook integration
- [ ] Optional signed/hash-chain or permissioned-ledger anchoring

---

# 55. Engineering Rules

Bhumi Praman follows these rules as the feature set grows:

### Rule 1 — Never hide evidence

Every important extracted value should remain traceable to its source.

### Rule 2 — Never turn confidence into authority

A high score means "more likely correct", not "legally verified".

### Rule 3 — Never overwrite history silently

Corrections should create versioned events and retain previous values.

### Rule 4 — Never treat GIS as a substitute for authoritative survey data

Spatial visualization and spatial validation depend on the quality and authority of the underlying dataset.

### Rule 5 — Never call an integration live when it is simulated

Adapters, mock services, and real government systems must be clearly distinguished.

### Rule 6 — Measure the model continuously

Every meaningful OCR/extraction upgrade should be evaluated against a fixed benchmark.

---

# 56. Final Positioning

Most digitization systems stop at:

> **"We converted the document into data."**

Bhumi Praman is designed to continue:

> **"We can show the evidence, measure confidence, compare related records, identify inconsistencies, trace historical changes, route uncertainty to a human, preserve the entire audit history, and expose a verifiable final record."**

### The intended transformation

```text
LEGACY DOCUMENT
       ↓
DIGITAL DATA
       ↓
VALIDATED DATA
       ↓
RECONCILED DATA
       ↓
VERIFIED DATA
       ↓
TRACEABLE DATA
       ↓
TRUSTED LAND RECORD
```

---

# 57. License

Add the project's applicable open-source license here.

---
