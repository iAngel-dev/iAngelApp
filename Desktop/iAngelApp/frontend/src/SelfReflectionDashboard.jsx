// SelfReflectionDashboard.jsx
import React, { useEffect, useState } from "react";

export default function SelfReflectionDashboard() {
  const [reflections, setReflections] = useState([]);

  useEffect(() => {
    fetch("import.meta.env.VITE_API_URL/self_reflections")
      .then(res => res.json())
      .then(data => setReflections(data.reverse()))
      .catch(err => console.error("Erreur récupération réflexions:", err));
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h2>🧠 Introspections d’iAngel</h2>
      {reflections.length === 0 && <p>Aucune introspection encore.</p>}
      <ul style={{ listStyle: "none", padding: 0 }}>
        {reflections.map((r, i) => (
          <li key={i} style={{ marginBottom: "1rem", background: "#f3f3f3", padding: "1rem", borderRadius: "8px" }}>
            <strong>{new Date(r.timestamp * 1000).toLocaleString()}</strong><br />
            <em>Utilisateur :</em> {r.user_id}<br />
            <div>{r.message}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
