"""
validator.py
-------------
Implements PS requirement #10 ("Automated validation using business rules,
cross-database verification, and duplicate detection").

Two layers:
 1. record-level rule checks (does this one record make internal sense?)
 2. batch-level duplicate detection (does this record collide with another
    already-processed record on the identifiers that should be unique?)

In production, layer (1) would also cross-check against external systems
(DILRMP/NGDRS/state LRMS master data for valid village/tehsil/district
names, ULPIN registry for parcel identity) -- those calls are stubbed here
as `# TODO: external cross-check` so the integration points are explicit.
"""
import re
import hashlib

NUMERIC_ID_PATTERN = re.compile(r"^[A-Za-z0-9\-\/]{1,20}$")
AREA_PATTERN = re.compile(r"^([0-9]+\.?[0-9]*)\s*(acres?|hectares?|sq\.?\s?m|bigha|katha)$", re.IGNORECASE)


def validate_record(scored_fields: dict) -> list[str]:
    """Returns a list of human-readable validation issues. An empty list
    means the record passed every automated rule check (it can still fail
    human review on content grounds -- rules only catch structural/logical
    problems)."""
    issues = []

    def val(field):
        return scored_fields.get(field, {}).get("value")

    # Completeness
    required = ["owner_name", "khasra_number", "khata_number", "village", "district"]
    for field in required:
        if not val(field):
            issues.append(f"Missing required field: {field}")

    # Numeric/ID format checks
    for field in ["survey_number", "khasra_number", "khata_number", "mutation_number", "registration_number"]:
        v = val(field)
        if v and not NUMERIC_ID_PATTERN.match(v):
            issues.append(f"{field} has an unexpected format: '{v}'")

    # Plot area sanity check (must parse as a positive number + unit)
    area = val("plot_area")
    if area:
        m = AREA_PATTERN.match(area)
        if not m:
            issues.append(f"plot_area could not be parsed as '<number> <unit>': '{area}'")
        elif float(m.group(1)) <= 0:
            issues.append(f"plot_area is not a positive value: '{area}'")

    # TODO: external cross-check -- village/tehsil/district against state
    # LRMS master list; khasra/khata against DILRMP MIS; owner identity
    # against consent-based Aadhaar-linked RoR per DILRMP guidelines.

    return issues


def _record_fingerprint(scored_fields: dict) -> str | None:
    """A record is considered a potential duplicate of another if it shares
    the same (village, khasra_number, khata_number) triple -- the same
    logical parcel should not appear twice as a distinct entry. Returns
    None when none of the three key fields were extracted: matching two
    records purely on "we couldn't read either of them" is not a duplicate
    signal, it's an extraction-quality signal, and flagging it as a
    possible duplicate would mislead the reviewing officer.
    (None-guard added during integration -- found via testing two real,
    heavily-degraded sample scans that both extracted blank on all three
    key fields and were incorrectly flagged as duplicates of each other.)
    """
    key_fields = ["village", "khasra_number", "khata_number"]
    values = [(scored_fields.get(f, {}).get("value") or "").strip().lower() for f in key_fields]
    if not any(values):
        return None
    raw = "|".join(values)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def find_duplicates(all_records: dict[str, dict]) -> dict[str, list[str]]:
    """all_records: {doc_id: scored_fields}
    Returns {doc_id: [other doc_ids it collides with]} for any record that
    shares a fingerprint with at least one other record."""
    fingerprints: dict[str, list[str]] = {}
    for doc_id, fields in all_records.items():
        fp = _record_fingerprint(fields)
        if fp is None:
            continue
        fingerprints.setdefault(fp, []).append(doc_id)

    duplicates: dict[str, list[str]] = {}
    for doc_ids in fingerprints.values():
        if len(doc_ids) > 1:
            for doc_id in doc_ids:
                duplicates[doc_id] = [d for d in doc_ids if d != doc_id]
    return duplicates


# ---------------------------------------------------------------------------
# ADDED during web integration (not part of the original Crystal prototype):
# find_duplicates() above answers "does this parcel already exist as a
# distinct entry?" (same village/khasra/khata). Conflict detection answers a
# different question -- "do two records disagree about who owns the same
# identified parcel?" -- which the PS26018 brief calls out separately
# (automated validation using business rules *and* duplicate detection are
# both named requirements). Kept in this file since it shares find_duplicates'
# batch-scan shape and the same "flag for human review, never auto-adjudicate"
# posture as the rest of this module.
# ---------------------------------------------------------------------------
def find_conflicts(all_records: dict[str, dict]) -> dict[str, list[dict]]:
    """all_records: {doc_id: scored_fields}
    A conflict is two records that share the same (survey_number OR
    khasra_number) but disagree on owner_name. Returns
    {doc_id: [{"conflicting_doc_id", "shared_field", "shared_value"}, ...]}
    for any record involved in at least one such disagreement. Structural
    only -- like validate_record, this never adjudicates who is "right";
    it only ever routes the pair to a human for review.
    """
    def val(fields, name):
        return (fields.get(name, {}).get("value") or "").strip().lower()

    conflicts: dict[str, list[dict]] = {}
    doc_ids = list(all_records.keys())
    for i, doc_a in enumerate(doc_ids):
        for doc_b in doc_ids[i + 1:]:
            fields_a, fields_b = all_records[doc_a], all_records[doc_b]
            owner_a, owner_b = val(fields_a, "owner_name"), val(fields_b, "owner_name")
            if not owner_a or not owner_b or owner_a == owner_b:
                continue
            for id_field in ("survey_number", "khasra_number"):
                shared = val(fields_a, id_field)
                if shared and shared == val(fields_b, id_field):
                    entry_a = {"conflicting_doc_id": doc_b, "shared_field": id_field, "shared_value": shared}
                    entry_b = {"conflicting_doc_id": doc_a, "shared_field": id_field, "shared_value": shared}
                    conflicts.setdefault(doc_a, []).append(entry_a)
                    conflicts.setdefault(doc_b, []).append(entry_b)
    return conflicts
