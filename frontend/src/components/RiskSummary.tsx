import { Pie, PieChart, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { PlotLatestAnalysis } from "../App";

interface Props {
  plots: PlotLatestAnalysis[];
}

const COLORS = ["#43a047", "#fb8c00", "#e53935"];

export const RiskSummary: React.FC<Props> = ({ plots }) => {
  const total = plots.length;
  const low = plots.filter((p) => p.risk_level === "LOW").length;
  const med = plots.filter((p) => p.risk_level === "MEDIUM").length;
  const high = plots.filter((p) => p.risk_level === "HIGH").length;

  const data = [
    { name: "Low", value: low },
    { name: "Medium", value: med },
    { name: "High", value: high },
  ];

  const encroached = plots.filter((p) => p.has_encroachment).length;
  const vacant = plots.filter((p) => p.is_vacant).length;
  const closed = plots.filter((p) => p.is_closed).length;

  return (
    <div className="card">
      <h2>Compliance Summary</h2>
      <div className="summary-grid">
        <div>
          <p className="summary-label">Total plots</p>
          <p className="summary-value">{total}</p>
        </div>
        <div>
          <p className="summary-label">Encroached</p>
          <p className="summary-value">{encroached}</p>
        </div>
        <div>
          <p className="summary-label">Vacant</p>
          <p className="summary-value">{vacant}</p>
        </div>
        <div>
          <p className="summary-label">Closed (approx.)</p>
          <p className="summary-value">{closed}</p>
        </div>
      </div>
      <div style={{ width: "100%", height: 220 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={70}
              label
            >
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};


