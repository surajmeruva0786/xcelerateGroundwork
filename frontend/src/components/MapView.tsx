import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import { Feature, Geometry } from "geojson";
import { PlotLatestAnalysis, PlotFeature } from "../App";

interface Props {
  features: PlotFeature[];
  plots: PlotLatestAnalysis[];
}

function getRiskColor(riskLevel: string | null | undefined): string {
  switch (riskLevel) {
    case "HIGH":
      return "#e53935";
    case "MEDIUM":
      return "#fb8c00";
    case "LOW":
      return "#43a047";
    default:
      return "#607d8b";
  }
}

export const MapView: React.FC<Props> = ({ features, plots }) => {
  const plotById = new Map(plots.map((p) => [p.plot.id, p]));

  const style = (feature: Feature<Geometry, any>) => {
    const id = feature.id as string;
    const plot = plotById.get(id);
    const riskLevel = plot?.risk_level ?? null;
    return {
      color: "#333",
      weight: 1,
      fillOpacity: 0.6,
      fillColor: getRiskColor(riskLevel),
    };
  };

  const defaultCenter: [number, number] = [21.25, 81.63]; // Chhattisgarh approx

  return (
    <div className="map-container">
      <MapContainer center={defaultCenter} zoom={12} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {features.length > 0 && (
          <GeoJSON
            key="plots-geojson"
            data={{
              type: "FeatureCollection",
              features: features as any,
            }}
            style={style}
          />
        )}
      </MapContainer>
      <div className="map-legend">
        <span className="legend-item">
          <span className="legend-color" style={{ backgroundColor: getRiskColor("HIGH") }} />
          HIGH risk
        </span>
        <span className="legend-item">
          <span className="legend-color" style={{ backgroundColor: getRiskColor("MEDIUM") }} />
          MEDIUM risk
        </span>
        <span className="legend-item">
          <span className="legend-color" style={{ backgroundColor: getRiskColor("LOW") }} />
          LOW risk
        </span>
      </div>
    </div>
  );
};


