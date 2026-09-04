import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams, Link } from "react-router-dom";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import * as api from "../services/api";
import { Card, StatusBadge } from "../components/Badges";
import type { GisRecord } from "../types";

const STATUS_COLOR: Record<GisRecord["status"], string> = {
  verified: "#15803d",
  pending_review: "#d97706",
  rejected: "#b91c1c",
};

function FlyToRecord({ record }: { record: GisRecord | null }) {
  const map = useMap();
  useEffect(() => {
    if (record) map.flyTo([record.latitude, record.longitude], 14, { duration: 0.6 });
  }, [record, map]);
  return null;
}

export default function GisExplorer() {
  const [searchParams] = useSearchParams();
  const focusId = searchParams.get("record");
  const { data: records, isLoading } = useQuery({ queryKey: ["gis-records"], queryFn: () => api.getGisRecords() });
  const [selected, setSelected] = useState<GisRecord | null>(null);

  useEffect(() => {
    if (focusId && records) {
      const match = records.find((r) => r.id === Number(focusId));
      if (match) setSelected(match);
    }
  }, [focusId, records]);

  const center: [number, number] = [26.1445, 91.7362]; // Guwahati

  return (
    <div className="flex h-screen">
      <div className="flex-1 relative">
        <div className="absolute top-4 left-4 z-[1000] bg-surface/95 backdrop-blur border border-border rounded-lg px-3 py-2 text-xs text-text-muted shadow-sm max-w-xs">
          <div className="flex items-center gap-1.5 font-medium text-text-main mb-0.5">
            <iconify-icon icon="lucide:info" width="13"></iconify-icon> Prototype / Demonstration Data
          </div>
          Map positions are locality-level approximations for demo purposes, not surveyed cadastral parcel boundaries.
        </div>
        {isLoading && <div className="absolute inset-0 flex items-center justify-center text-sm text-text-muted bg-bg-page/60 z-[1000]">Loading map…</div>}
        <MapContainer center={center} zoom={11} style={{ height: "100%", width: "100%" }} className="z-0">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <FlyToRecord record={selected} />
          {records?.map((r) => (
            <CircleMarker
              key={r.id}
              center={[r.latitude, r.longitude]}
              radius={selected?.id === r.id ? 10 : 7}
              pathOptions={{ color: STATUS_COLOR[r.status], fillColor: STATUS_COLOR[r.status], fillOpacity: 0.7, weight: 2 }}
              eventHandlers={{ click: () => setSelected(r) }}
            >
              <Popup>
                <div className="text-xs font-mono">{r.record_code}</div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="w-80 shrink-0 border-l border-border bg-surface overflow-y-auto">
        <div className="p-5 border-b border-border">
          <h1 className="font-serif text-lg font-semibold text-primary">GIS Explorer</h1>
          <p className="text-xs text-text-muted mt-1">{records?.length ?? 0} records plotted</p>
        </div>

        {selected ? (
          <div className="p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-sm font-semibold text-text-main">{selected.record_code}</span>
              <StatusBadge status={selected.status} />
            </div>
            <dl className="space-y-2.5 text-sm">
              <div><dt className="text-xs text-text-muted">Owner</dt><dd className="text-text-main">{selected.owner_name ?? "—"}</dd></div>
              <div><dt className="text-xs text-text-muted">Khasra / Survey No.</dt><dd className="font-mono text-text-main">{selected.khasra_number ?? "—"} / {selected.survey_number ?? "—"}</dd></div>
              <div><dt className="text-xs text-text-muted">Village</dt><dd className="text-text-main">{selected.village ?? "—"}</dd></div>
              <div><dt className="text-xs text-text-muted">Tehsil, District</dt><dd className="text-text-main">{selected.tehsil ?? "—"}, {selected.district ?? "—"}</dd></div>
              <div><dt className="text-xs text-text-muted">Plot Area</dt><dd className="text-text-main">{selected.plot_area ?? "—"}</dd></div>
              <div><dt className="text-xs text-text-muted">Coordinates (demo)</dt><dd className="font-mono text-xs text-text-main">{selected.latitude.toFixed(5)}, {selected.longitude.toFixed(5)}</dd></div>
            </dl>
            <Link to={`/records/${selected.id}`} className="mt-4 flex items-center justify-center gap-1.5 w-full bg-primary text-white text-sm font-medium py-2 rounded-lg hover:bg-primary-dark transition-colors">
              Open Full Record <iconify-icon icon="lucide:arrow-right" width="13"></iconify-icon>
            </Link>
          </div>
        ) : (
          <div className="p-5 space-y-2">
            {records?.map((r) => (
              <Card key={r.id} className="p-3 cursor-pointer hover:border-primary/50" onClick={() => setSelected(r)}>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-medium text-text-main">{r.record_code}</span>
                  <span className="w-2 h-2 rounded-full" style={{ background: STATUS_COLOR[r.status] }} />
                </div>
                <div className="text-xs text-text-muted mt-1 truncate">{r.village ?? "—"}, {r.district ?? "—"}</div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
