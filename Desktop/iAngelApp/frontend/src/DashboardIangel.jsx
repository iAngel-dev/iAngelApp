// DashboardIangel.jsx
import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Scatter
} from "recharts";

export default function DashboardIangel() {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    fetch("import.meta.env.VITE_API_URL0.158:8080/stress_records?user_id=felix")
      .then(res => res.json())
      .then(data => setRecords(data))
      .catch(err => console.error(err));
  }, []);

  const getColor = (val) => {
    if (val >= 0.7) return "red";
    if (val >= 0.4) return "orange";
    return "green";
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>📈 Dashboard émotionnel</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={records}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" tickFormatter={t => new Date(t * 1000).toLocaleDateString()} />
          <YAxis domain={[0, 1]} />
          <Tooltip labelFormatter={t => new Date(t * 1000).toLocaleString()} />
          <Line dataKey="anxiety_score" stroke="#8884d8" />
          <Scatter
            data={records.map(r => ({ ...r, color: getColor(r.anxiety_score) }))}
            fill="#8884d8"
            shape={({ cx, cy, payload }) => (
              <circle cx={cx} cy={cy} r={4} fill={getColor(payload.anxiety_score)} />
            )}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
