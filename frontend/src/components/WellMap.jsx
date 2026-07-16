import { GoogleMap, OverlayView, useJsApiLoader } from "@react-google-maps/api";
import L, { divIcon, latLngBounds } from "leaflet";
import "leaflet-draw";
import "leaflet-draw/dist/leaflet.draw.css";
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
  ["marker-saguaro-operator", "Saguaro Petroleum wells"],
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

const PRODUCTION_BUBBLE_MIN_SIZE = 18;
const PRODUCTION_BUBBLE_MAX_SIZE = 78;
const PRODUCTION_BUBBLE_METRICS = {
  oil: { field: "cumulative_oil_volume", label: "Cumulative oil", unit: "bbls" },
  gas: { field: "cumulative_gas_volume", label: "Cumulative gas", unit: "mcf" },
  fluid: { field: "cumulative_fluid_volume", label: "Cumulative fluid", unit: "bbls" },
};

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
  "marker-saguaro-operator": "Saguaro Petroleum well",
  "marker-default": "Other well",
};

function formatDepth(value) {
  if (value == null || value === "") return "-";
  const depth = Number(value);
  return Number.isFinite(depth) ? depth.toLocaleString() + " ft" : "-";
}

function formatVolume(value, maximumFractionDigits = 0) {
  const volume = Number(value);
  if (!Number.isFinite(volume)) return null;

  return volume.toLocaleString(undefined, {
    maximumFractionDigits,
  });
}

function formatProduction(well) {
  const cumulativeOil = formatVolume(well.cumulative_oil_volume);
  const cumulativeGas = formatVolume(well.cumulative_gas_volume);
  const cumulativeFluid = formatVolume(well.cumulative_fluid_volume);
  const cumulativeValues = [];

  if (cumulativeOil != null) cumulativeValues.push("Cumulative oil " + cumulativeOil + " bbls");
  if (cumulativeGas != null) cumulativeValues.push("Cumulative gas " + cumulativeGas + " mcf");
  if (cumulativeFluid != null) cumulativeValues.push("Cumulative fluid " + cumulativeFluid + " bbls");

  if (cumulativeValues.length > 0) {
    return cumulativeValues.join(" | ");
  }

  const sample = (well.production_samples || []).find((item) => (
    item.oil_m3 != null || item.gas_e3m3 != null || item.water_m3 != null
  ));
  if (!sample) return "No production data";
  const values = [];
  if (sample.oil_m3 != null) values.push("Oil " + Number(sample.oil_m3).toLocaleString() + " bbls");
  if (sample.gas_e3m3 != null) values.push("Gas " + Number(sample.gas_e3m3).toLocaleString() + " e3m3");
  if (sample.water_m3 != null) values.push("Water " + Number(sample.water_m3).toLocaleString() + " bbls");
  return values.join(" | ");
}

function wellStatusText(well) {
  return `${well.actual_status_text || ""} ${well.well_type || ""} ${well.status || ""}`.toLowerCase();
}

function isSaguaroOperator(well) {
  const operatorName = String(
    well.cur_operator_name ||
    well.current_operator ||
    well.operator ||
    ""
  )
    .trim()
    .toUpperCase();

  return operatorName.includes("SAGUARO PETROLEUM");
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

function bubbleMetricConfig(metricKey) {
  return PRODUCTION_BUBBLE_METRICS[metricKey] || PRODUCTION_BUBBLE_METRICS.fluid;
}

function cumulativeBubbleVolume(well, metricKey) {
  const { field } = bubbleMetricConfig(metricKey);
  const value = Number(well[field]);
  return Number.isFinite(value) && value > 0 ? value : 0;
}

function productionBubbleMetrics(wells, metricKey) {
  const values = wells.map((well) => cumulativeBubbleVolume(well, metricKey)).filter((value) => value > 0);
  return {
    maxVolume: values.length ? Math.max(...values) : 0,
    metricKey,
  };
}

function productionBubbleSize(well, metrics) {
  const volume = cumulativeBubbleVolume(well, metrics.metricKey);
  if (!volume || !metrics.maxVolume) return 0;
  const ratio = Math.sqrt(volume / metrics.maxVolume);
  return Math.round(PRODUCTION_BUBBLE_MIN_SIZE + ratio * (PRODUCTION_BUBBLE_MAX_SIZE - PRODUCTION_BUBBLE_MIN_SIZE));
}

function productionBubbleLabel(well, metricKey) {
  const metric = bubbleMetricConfig(metricKey);
  const volume = cumulativeBubbleVolume(well, metricKey);
  return volume ? metric.label + " " + Math.round(volume).toLocaleString() + " " + metric.unit : "";
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

function markerHtml(well, bubbleMetrics, showProductionBubbles = true) {
  const markerClass = markerClassForWell(well);
  const operatorClass = isSaguaroOperator(well) ? "marker-saguaro-operator" : "";
  const bubbleSize = showProductionBubbles ? productionBubbleSize(well, bubbleMetrics) : 0;
  const bubbleLabel = productionBubbleLabel(well, bubbleMetrics.metricKey);
  const plotHref = `#production-plot/${encodeURIComponent(well.uwi)}`;
  const bubble = bubbleSize
    ? `<a class="production-fluid-bubble production-plot-link" href="${plotHref}" style="width:${bubbleSize}px;height:${bubbleSize}px" title="${bubbleLabel}; open production plot for ${well.uwi}" aria-label="${bubbleLabel}; open production plot for ${well.uwi}"></a>`
    : "";
  return `<span class="well-marker-stack" title="${bubbleLabel}">${bubble}<span class="well-status-marker ${markerClass} ${operatorClass}" aria-hidden="true"></span></span>`;
}

function leafletIconForWell(well, bubbleMetrics, showProductionBubbles = true) {
  const bubbleSize = showProductionBubbles ? productionBubbleSize(well, bubbleMetrics) : 0;
  const iconSize = Math.max(22, bubbleSize || 18);
  return divIcon({
    className: "well-status-marker-icon",
    html: markerHtml(well, bubbleMetrics, showProductionBubbles),
    iconSize: [iconSize, iconSize],
    iconAnchor: [iconSize / 2, iconSize / 2],
    popupAnchor: [0, -(iconSize / 2)],
  });
}

function MapLegend({ showProductionBubbles, productionBubbleMetric }) {
  const bubbleMetric = bubbleMetricConfig(productionBubbleMetric);
  return (
    <div className="map-legend" aria-label="Well status legend">
      <strong>Legend</strong>
      {LEGEND_ITEMS.map(([markerClass, label]) => (
        <span key={markerClass}><i className={"well-status-marker " + markerClass} />{label}</span>
      ))}
      {showProductionBubbles && <span><i className="production-fluid-bubble" />{bubbleMetric.label} volume</span>}
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

function AnnotationDrawingTools() {
  const map = useMap();
  useEffect(() => {
    const annotationPane = map.createPane("annotationPane");
    annotationPane.style.zIndex = "650";
    annotationPane.style.pointerEvents = "auto";

    const annotations = new L.FeatureGroup();
    map.addLayer(annotations);
    const controls = new L.Control.Draw({
      position: "topleft",
      draw: {
        polyline: { shapeOptions: { pane: "annotationPane", color: "#d63b2f", weight: 4 } },
        circle: { shapeOptions: { pane: "annotationPane", color: "#d63b2f", fillColor: "#f26b5e", fillOpacity: 0.18, weight: 3 } },
        polygon: false, rectangle: false, marker: false, circlemarker: false,
      },
      edit: { featureGroup: annotations },
    });
    const handleCreated = (event) => annotations.addLayer(event.layer);
    map.addControl(controls);
    map.on(L.Draw.Event.CREATED, handleCreated);
    return () => {
      map.off(L.Draw.Event.CREATED, handleCreated);
      map.removeControl(controls);
      map.removeLayer(annotations);
      annotationPane.remove();
    };
  }, [map]);
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

function GoogleWellDot({ well, bubbleMetrics, showProductionBubbles }) {
  const markerClass = markerClassForWell(well);
  const operatorClass = isSaguaroOperator(well) ? "marker-saguaro-operator" : "";
  const bubbleSize = showProductionBubbles ? productionBubbleSize(well, bubbleMetrics) : 0;
  const bubbleLabel = productionBubbleLabel(well, bubbleMetrics.metricKey);
  return (
    <OverlayView
      position={{ lat: Number(well.latitude), lng: Number(well.longitude) }}
      mapPaneName={OverlayView.OVERLAY_MOUSE_TARGET}
    >
      <div className="google-marker-wrap" style={{ width: Math.max(18, bubbleSize), height: Math.max(18, bubbleSize) }} title={`${markerLabelForWell(well)}: ${well.uwi} ${well.name || ""}`}>
        {bubbleSize > 0 && <a className="production-fluid-bubble production-plot-link" href={`#production-plot/${encodeURIComponent(well.uwi)}`} style={{ width: bubbleSize, height: bubbleSize }} title={bubbleLabel + `; open production plot for ${well.uwi}`} aria-label={bubbleLabel + `; open production plot for ${well.uwi}`} onClick={(event) => event.stopPropagation()} />}
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

function GoogleWellMap({ wells, mapType, showProductionBubbles, productionBubbleMetric }) {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_API_KEY || "",
  });

  const mappedWells = wells.filter((well) => well.latitude && well.longitude);
  const positions = useMemo(() => mappedWellPositions(wells), [wells]);
  const bubbleMetrics = useMemo(
    () => showProductionBubbles ? productionBubbleMetrics(wells, productionBubbleMetric) : { maxVolume: 0, metricKey: productionBubbleMetric },
    [wells, showProductionBubbles, productionBubbleMetric],
  );
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
        <GoogleWellDot key={well.uwi} well={well} bubbleMetrics={bubbleMetrics} showProductionBubbles={showProductionBubbles} />
      ))}
    </GoogleMap>
  );
}

export default function WellMap({ wells, loading, showProductionBubbles = true, productionBubbleMetric = "fluid" }) {
  const [mapMode, setMapMode] = useState("leaflet");
  const activeBubbleMetric = PRODUCTION_BUBBLE_METRICS[productionBubbleMetric] ? productionBubbleMetric : "fluid";
  const mappedWells = wells.filter((well) => well.latitude && well.longitude);
  const positions = useMemo(() => mappedWellPositions(wells), [wells]);
  const bubbleMetrics = useMemo(
    () => showProductionBubbles ? productionBubbleMetrics(wells, activeBubbleMetric) : { maxVolume: 0, metricKey: activeBubbleMetric },
    [wells, showProductionBubbles, activeBubbleMetric],
  );
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
      <MapLegend showProductionBubbles={showProductionBubbles} productionBubbleMetric={activeBubbleMetric} />
      {loading && (
        <div className="map-loading" aria-live="polite">
          <span className="spinner" />
          <span>Loading wells</span>
        </div>
      )}
      {mapMode === "leaflet" && (
        <MapContainer center={center} zoom={positions.length ? 7 : 5} scrollWheelZoom className="well-map">
          <FitLeafletToWells positions={positions} />
          <AnnotationDrawingTools />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {mappedWells.map((well) => (
            <Marker
              key={well.uwi}
              position={[Number(well.latitude), Number(well.longitude)]}
              icon={leafletIconForWell(well, bubbleMetrics, showProductionBubbles)}
            >
              <Popup>
                <WellPopup well={well} />
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      )}
      {mapMode === "google-roadmap" && <GoogleWellMap wells={wells} mapType="roadmap" showProductionBubbles={showProductionBubbles} productionBubbleMetric={activeBubbleMetric} />}
      {mapMode === "google-satellite" && <GoogleWellMap wells={wells} mapType="satellite" showProductionBubbles={showProductionBubbles} productionBubbleMetric={activeBubbleMetric} />}
    </div>
  );
}

