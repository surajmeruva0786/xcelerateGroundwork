import { PlotLatestAnalysis } from "../App";

interface Props {
  plots: PlotLatestAnalysis[];
}

export const PlotTable: React.FC<Props> = ({ plots }) => {
  return (
    <div className="card">
      <h2>Plot-Level Details</h2>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Plot No.</th>
              <th>Risk</th>
              <th>Risk score</th>
              <th>Encroachment</th>
              <th>Vacant</th>
              <th>Partial</th>
              <th>Closed</th>
            </tr>
          </thead>
          <tbody>
            {plots.map((p) => (
              <tr key={p.plot.id}>
                <td>{p.plot.plot_number}</td>
                <td>{p.risk_level ?? "-"}</td>
                <td>{p.risk_score?.toFixed(2) ?? "-"}</td>
                <td>{p.has_encroachment ? "Yes" : "No"}</td>
                <td>{p.is_vacant ? "Yes" : "No"}</td>
                <td>{p.is_partial_construction ? "Yes" : "No"}</td>
                <td>{p.is_closed ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


