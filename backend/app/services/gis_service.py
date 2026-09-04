"""
gis_service.py
----------------
Spec section 28 is explicit: don't fabricate official parcel boundaries.
There is no real cadastral survey data available in this project (the seed
records are themselves fictional, per ai/generate_samples.py's own
comment), so this module only ever produces clearly-labelled prototype
demonstration points -- a small set of real place-name anchors in the
Kamrup/Guwahati area (where the seed villages are set) plus a deterministic
jitter so repeat runs are stable, never a claim of surveyed parcel geometry.
The API response and the frontend both carry an explicit "prototype_data"
flag so this is never presented as authoritative.
"""
import hashlib

# Approximate town/locality centres in and around Kamrup / Kamrup Metro,
# Assam -- real place names, deliberately coarse (locality-level, not
# parcel-level) since no real survey data backs this.
ANCHORS = {
    "rangapara": (26.2006, 92.1633),
    "beltola": (26.1240, 91.7898),
    "chandrapur": (26.0730, 91.8460),
    "sonapur": (26.0300, 91.9450),
    "guwahati": (26.1445, 91.7362),
    "rangia": (26.4419, 91.6208),
}
DEFAULT_CENTER = ANCHORS["guwahati"]


def assign_coordinates(village: str | None, district: str | None, record_code: str) -> tuple[float, float]:
    key = (village or "").strip().lower()
    base = ANCHORS.get(key, DEFAULT_CENTER)

    # Deterministic small jitter (~< 2km) so records in the same village
    # don't all render on one exact point, without implying real
    # parcel-level precision.
    digest = hashlib.sha256(record_code.encode("utf-8")).hexdigest()
    jitter_lat = (int(digest[:8], 16) / 0xFFFFFFFF - 0.5) * 0.02
    jitter_lng = (int(digest[8:16], 16) / 0xFFFFFFFF - 0.5) * 0.02
    return round(base[0] + jitter_lat, 6), round(base[1] + jitter_lng, 6)
