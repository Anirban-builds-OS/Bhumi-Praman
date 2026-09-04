GIS logic lives in `backend/app/services/gis_service.py` (demo coordinate
assignment) and `frontend/src/pages/GisExplorer.tsx` (the Leaflet map) —
GIS wasn't broken out as a separate top-level module since it's not a
standalone system, just another backend service + frontend page. This
folder is kept per the project's directory-structure convention in case
you want to house standalone GIS assets (e.g. real cadastral boundary
files, once available) here later.
