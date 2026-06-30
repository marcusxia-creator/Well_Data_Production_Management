import { GoogleMap, OverlayView, useJsApiLoader } from "@react-google-maps/api";
import { divIcon, latLngBounds } from "leaflet";
import { useEffect, useMemo, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";

const DEFAULT_CENTER = [54.5, -115.0];
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const GOOGLE_MAP_OPTIONS = {
  clickableIcons: false,
  fullscreenControl: false,
  mapTypeControl: false,
  streetViewControl: false,
};
const LEGEND_ITEMS = [
  ["marker-sp-operator", "SP current operator"],
  ["marker-oil", "Oil well"],
  ["marker-gas", "Gas well"],
  ["marker-oil-gas", "Oil/gas well"],
  ["marker-injection", "Injection well"],
  ["marker-plugged-oil-gas", "Plugged oil/gas"],
  ["marker-plugged-gas", "Plugged gas well"],
  ["marker-plugged-oil", "Plugged oil well"],
  ["marker-dry-hole", "Dry hole"],
  ["marker-abandoned", "Abandoned"],
];

const MARKER_LABELS = {
  "marker-oil": "Oil well",
  "marker-gas": "Gas well",
  "marker-oil-gas": "Oil/gas well",
  "marker-injection": "Injection well",
  "marker-plugged-oil-gas": "Plugged oil/gas well",
  "marker-plugged-gas": "Plugged gas well",
  "marker-plugged-oil": "Plugged oil well",
  "marker-dry-hole": "Dry hole",
  "marker-abandoned": "Abandoned well",
  "marker-sp-operator": "Saguaro wells",
  "marker-default": "Other well",
};

function formatDepth(value) {
  if (value == null || value === "") return "-";
  const depth = Number(value);
  return Number.isFinite(depth) ? depth.toLocaleString() + " m" : "-";
}

function formatProduction(well) {
  const sample = (well.production_samples || []).find((item) => (
    item.oil_m3 != null || item.gas_e3m3 != null || item.water_m3 != null
  ));
  if (!sample) return "No production data";
  const values = [];
  if (sample.oil_m3 != null) values.push("Oil " + Number(sample.oil_m3).toLocaleString() + " m3");
  if (sample.gas_e3m3 != null) values.push("Gas " + Number(sample.gas_e3m3).toLocaleString() + " e3m3");
  if (sample.water_m3 != null) values.push("Water " + Number(sample.water_m3).toLocaleString() + " m3");
  return values.join(" | ");
}
function wellStatusText(well) {
  return `${well.actual_status_text || ""} ${well.well_type || ""} ${well.status || ""}`.toLowerCase();
}

function isSpOperator(well) {
  const operatorName = String(
    well.cur_operator_name ||
    well.current_operator ||
    well.operator ||
    ""
  )
    .trim()
    .toUpperCase();

  return (
    operatorName === "SP" ||
    operatorName === "S.P." ||
    operatorName.includes("SAGUARO") ||
    operatorName.includes("SAGUARO PETROLEUM")
  );
}

function markerClassForWell(well) {
  const statusText = wellStatusText(well);
  const isPlugged = statusText.includes("plug");
  const isOil = statusText.includes("oil");
  const isGas = statusText.includes("gas");

  if (statusText.includes("dry hole") || statusText.includes("dry")) return "marker-dry-hole";
  if (statusText.includes("abandon") || statusText.includes("abd")) return "marker-abandoned";
  if (isPlugged && isOil && isGas) return "marker-plugged-oil-gas";
  if (isPlugged && isGas) return "marker-plugged-gas";
  if (isPlugged && isOil) return "marker-plugged-oil";
  if (statusText.includes("inject") || statusText.includes("disposal")) return "marker-injection";
  if (isOil && isGas) return "marker-oil-gas";
  if (isGas) return "marker-gas";
  if (isOil) return "marker-oil";
  return "marker-default";
}

function markerLabelForWell(well) {
  return MARKER_LABELS[markerClassForWell(well)] || MARKER_LABELS["marker-default"];
}

function mappedWellPositions(wells) {
  return wells
    .filter((well) => well.latitude && well.longitude)
    .map((well) => [Number(well.latitude), Number(well.longitude)]);
}

function googleBoundsForPositions(positions) {
  if (!window.google || positions.length === 0) return null;
  const bounds = new window.google.maps.LatLngBounds();
  positions.forEach(([latitude, longitude]) => bounds.extend({ lat: latitude, lng: longitude }));
  return bounds;
}

function markerHtml(well) {
  const markerClass = markerClassForWell(well);
  const operatorClass = isSpOperator(well) ? "marker-sp-operator" : "";
  return `<span class="well-status-marker ${markerClass} ${operatorClass}" aria-hidden="true"></span>`;
}

function leafletIconForWell(well) {
  return divIcon({
    className: "well-status-marker-icon",
    html: markerHtml(well),
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    popupAnchor: [0, -8],
  });
}

function MapLegend() {
  return (
    <div className="map-legend" aria-label="Well status legend">
      <strong>Legend</strong>
      {LEGEND_ITEMS.map(([markerClass, label]) => (
        <span key={markerClass}><i className={`well-status-marker ${markerClass}`} />{label}</span>
      ))}
    </div>
  );
}

function FitLeafletToWells({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (!positions.length) return;
    if (positions.length === 1) {
      map.setView(positions[0], 12);
      return;
    }
    map.fitBounds(latLngBounds(positions), { padding: [42, 42], maxZoom: 13 });
  }, [map, positions]);
  return null;
}

function WellPopup({ well }) {
  return (
    <div className="well-popup-details">
      <span><strong>Well Name:</strong> {well.name || "-"}</span>
      <span><strong>API:</strong> {well.uwi}</span>
      <span><strong>Status:</strong> {well.actual_status_text || well.status || "-"}</span>
      <span><strong>Operator:</strong> {well.operator || "-"}</span>
      <span><strong>Type:</strong> {well.well_type || "-"}</span>
      <span><strong>Total Depth:</strong> {formatDepth(well.measured_depth_m)}</span>
      <span><strong>Production:</strong> {formatProduction(well)}</span>
    </div>
  );
}

function GoogleWellDot({ well }) {
  const markerClass = markerClassForWell(well);
  const operatorClass = isSpOperator(well) ? "marker-sp-operator" : "";
  return (
    <OverlayView
      position={{ lat: Number(well.latitude), lng: Number(well.longitude) }}
      mapPaneName={OverlayView.OVERLAY_MOUSE_TARGET}
    >
      <div className="google-marker-wrap" title={`${markerLabelForWell(well)}: ${well.uwi} ${well.name || ""}`}>
        <span className={`well-status-marker ${markerClass} ${operatorClass}`} />
        <span className="google-dot-popup">
          <small><strong>Well Name:</strong> {well.name || "-"}</small>
          <small><strong>API:</strong> {well.uwi}</small>
          <small><strong>Status:</strong> {well.actual_status_text || well.status || "-"}</small>
          <small><strong>Operator:</strong> {well.operator || "-"}</small>
          <small><strong>Type:</strong> {well.well_type || "-"}</small>
          <small><strong>Total Depth:</strong> {formatDepth(well.measured_depth_m)}</small>
          <small><strong>Production:</strong> {formatProduction(well)}</small>
        </span>
      </div>
    </OverlayView>
  );
}

function GoogleWellMap({ wells, mapType }) {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_API_KEY || "",
  });

  const mappedWells = wells.filter((well) => well.latitude && well.longitude);
  const positions = useMemo(() => mappedWellPositions(wells), [wells]);
  const center = positions.length
    ? { lat: positions[0][0], lng: positions[0][1] }
    : { lat: DEFAULT_CENTER[0], lng: DEFAULT_CENTER[1] };
  const options = useMemo(() => ({ ...GOOGLE_MAP_OPTIONS, mapTypeId: mapType }), [mapType]);

  function fitGoogleMap(map) {
    const bounds = googleBoundsForPositions(positions);
    if (!bounds) return;
    if (positions.length === 1) {
      map.setCenter({ lat: positions[0][0], lng: positions[0][1] });
      map.setZoom(12);
      return;
    }
    map.fitBounds(bounds, 48);
  }

  if (!GOOGLE_API_KEY) {
    return (
      <div className="map-message">
        <strong>Google Maps API key required</strong>
        <span>Set VITE_GOOGLE_MAPS_API_KEY in the frontend environment to enable Google Map and Satellite modes.</span>
      </div>
    );
  }

  if (loadError) {
    return <div className="map-message">Unable to load Google Maps.</div>;
  }

  if (!isLoaded) {
    return (
      <div className="map-message">
        <span className="spinner" />
        <span>Loading Google Maps</span>
      </div>
    );
  }

  return (
    <GoogleMap
      center={center}
      zoom={positions.length ? 7 : 5}
      mapContainerClassName="well-map"
      options={options}
      onLoad={fitGoogleMap}
    >
      {mappedWells.map((well) => (
        <GoogleWellDot key={well.uwi} well={well} />
      ))}
    </GoogleMap>
  );
}

export default function WellMap({ wells, loading }) {
  const [mapMode, setMapMode] = useState("leaflet");
  const mappedWells = wells.filter((well) => well.latitude && well.longitude);
  const positions = useMemo(() => mappedWellPositions(wells), [wells]);
  const center = positions.length ? positions[0] : DEFAULT_CENTER;

  return (
    <div className="map-wrap">
      <div className="map-mode-control" aria-label="Map mode">
        <button
          type="button"
          className={mapMode === "leaflet" ? "selected" : ""}
          onClick={() => setMapMode("leaflet")}
        >
          Road
        </button>
        <button
          type="button"
          className={mapMode === "google-roadmap" ? "selected" : ""}
          onClick={() => setMapMode("google-roadmap")}
        >
          Google Map
        </button>
        <button
          type="button"
          className={mapMode === "google-satellite" ? "selected" : ""}
          onClick={() => setMapMode("google-satellite")}
        >
          Satellite
        </button>
      </div>
      <MapLegend />
      {loading && (
        <div className="map-loading" aria-live="polite">
          <span className="spinner" />
          <span>Loading wells</span>
        </div>
      )}
      {mapMode === "leaflet" && (
        <MapContainer center={center} zoom={positions.length ? 7 : 5} scrollWheelZoom className="well-map">
          <FitLeafletToWells positions={positions} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {mappedWells.map((well) => (
            <Marker
              key={well.uwi}
              position={[Number(well.latitude), Number(well.longitude)]}
              icon={leafletIconForWell(well)}
            >
              <Popup>
                <WellPopup well={well} />
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      )}
      {mapMode === "google-roadmap" && <GoogleWellMap wells={wells} mapType="roadmap" />}
      {mapMode === "google-satellite" && <GoogleWellMap wells={wells} mapType="satellite" />}
    </div>
  );
}

