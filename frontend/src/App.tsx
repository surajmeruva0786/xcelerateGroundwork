import { useEffect, useState } from "react";
import axios from "axios";
import { MapView } from "./components/MapView";
import { RiskSummary } from "./components/RiskSummary";
import { PlotTable } from "./components/PlotTable";

export interface PlotSummary {
  id: string;
  industrial_area_id: string;
  plot_number: string;
  approved_land_use: string | null;
}

export interface PlotLatestAnalysis {
  plot: PlotSummary;
  last_result_id: string | null;
  risk_level: string | null;
  risk_score: number | null;
  has_encroachment: boolean | null;
  is_vacant: boolean | null;
  is_partial_construction: boolean | null;
  is_closed: boolean | null;
}

export interface PlotFeature {
  id: string;
  geometry: GeoJSON.Geometry;
  properties: {
    plot_number: string;
    industrial_area_id: string;
  };
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

function App() {
  const [plots, setPlots] = useState<PlotLatestAnalysis[]>([]);
  const [features, setFeatures] = useState<PlotFeature[]>([]);
  const [selectedSatelliteRunId, setSelectedSatelliteRunId] = useState<string | null>(null);
  const [availableRuns, setAvailableRuns] = useState<
    { id: string; t1_date: string; t2_date: string; status: string }[]
  >([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [plotsResp, featuresResp, runsResp] = await Promise.all([
          axios.get<PlotLatestAnalysis[]>(`${API_BASE_URL}/plots/latest-analysis`),
          axios.get<{ type: string; features: PlotFeature[] }>(
            `${API_BASE_URL}/plots/geojson`
          ),
          axios.get<
            { id: string; t1_date: string; t2_date: string; status: string }[]
          >(`${API_BASE_URL}/analysis/runs`),
        ]);
        setPlots(plotsResp.data);
        setFeatures(featuresResp.data.features);
        setAvailableRuns(runsResp.data);
        if (runsResp.data.length > 0) {
          setSelectedSatelliteRunId(runsResp.data[0].id);
        }
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleDownloadReport = () => {
    if (!selectedSatelliteRunId) return;
    window.open(
      `${API_BASE_URL}/analysis/${selectedSatelliteRunId}/report.pdf`,
      "_blank"
    );
  };

  const handleRunChange = (runId: string) => {
    setSelectedSatelliteRunId(runId);
    // In a more advanced version, we would refetch per-run plot metrics here.
  };

  if (loading) {
    return <div className="app-root">Loading dashboard…</div>;
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div>
          <h1>CSIDC Industrial Land Compliance</h1>
          <p>Automated monitoring of industrial plots using Sentinel-2 & GIS</p>
        </div>
        <div className="header-controls">
          <label>
            Satellite run (T1 vs T2):
            <select
              value={selectedSatelliteRunId ?? ""}
              onChange={(e) => handleRunChange(e.target.value)}
            >
              {availableRuns.map((run) => (
                <option key={run.id} value={run.id}>
                  {new Date(run.t1_date).toISOString().slice(0, 10)} →{" "}
                  {new Date(run.t2_date).toISOString().slice(0, 10)} ({run.status})
                </option>
              ))}
            </select>
          </label>
          <button onClick={handleDownloadReport} disabled={!selectedSatelliteRunId}>
            Download PDF Report
          </button>
        </div>
      </header>
      <main className="app-main">
        <section className="map-panel">
          <MapView features={features} plots={plots} />
        </section>
        <section className="side-panel">
          <RiskSummary plots={plots} />
          <PlotTable plots={plots} />
        </section>
      </main>
    </div>
  );
}

export default App;


