// Utilise import.meta.env.VITE_API_URL pour les appels API
import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import DashboardIangel from "./DashboardIangel";
import SelfReflectionDashboard from "./SelfReflectionDashboard";
import AskIangel from "./AskIangel";

function ProtectedRoute({ children }) {
  const [accessGranted, setAccessGranted] = useState(localStorage.getItem("access_pass") === "2580");
  if (!accessGranted) {
    const input = prompt("Mot de passe requis pour accéder aux réflexions :");
    if (input === "2580") {
      localStorage.setItem("access_pass", "2580");
      setAccessGranted(true);
      return children;
    } else {
      alert("Accès refusé.");
      return <Navigate to="/ask" replace />;
    }
  }
  return children;
}

function PasswordReset() {
  const clearAccess = () => {
    localStorage.removeItem("access_pass");
    alert("Mot de passe réinitialisé. Rechargez la page pour ré-entrer le mot de passe.");
  };
  return (
    <div style={{ padding: "2rem" }}>
      <h2>🔐 Réinitialiser le mot de passe d'accès</h2>
      <button onClick={clearAccess}>Réinitialiser l'accès aux réflexions</button>
    </div>
  );
}

function ThemeToggle() {
  const [dark, toggleDark] = useThemeToggle();
  return (
    <div style={{ padding: "0.5rem 1rem", textAlign: "right" }}>
      <button onClick={toggleDark}>{dark ? "☀️ Mode clair" : "🌙 Mode sombre"}</button>
    </div>
  );
}

function NavMenu() {
  const logoStyle = { height: "40px", marginRight: "1rem" };
  const barStyle = {
    display: "flex",
    alignItems: "center",
    background: "#f8f9fa",
    padding: "1rem",
    gap: "1.5rem"
  };
  return (
    <div style={barStyle}>
      <img src="/App logo.png" alt="iAngel Logo" style={logoStyle} />
      <h1 style={{ fontSize: "1.5rem", margin: 0, fontWeight: 600 }}>iAngel</h1>
      <a href="/">📈 Dashboard</a>
      <a href="/ask">💬 Parler à iAngel</a>
      <a href="/reflexions">🧠 Réflexions</a>
      <a href="/reset-pass">🔐 Réinitialiser</a>
      <a href="/conversations">🗂️ Historique</a>
    </div>
  );
}

function ConversationsLog() {
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    fetch("http://localhost:5002/iangel_live_conversations.json")
      .then(res => res.json())
      .then(setLogs)
      .catch(err => console.error("Erreur récupération logs:", err));
  }, []);
  return (
    <div style={{ padding: "2rem" }}>
      <h2>🗂️ Historique des conversations</h2>
      {logs.length === 0 && <p>Aucun échange trouvé.</p>}
      {logs.map((entry, idx) => (
        <div key={idx} style={{ marginBottom: "1rem", padding: "1rem", border: "1px solid #ccc", borderRadius: "8px" }}>
          <div><strong>{new Date(entry.timestamp * 1000).toLocaleString()}</strong></div>
          <div><em>Utilisateur :</em> {entry.user_id}</div>
          <div><strong>Question :</strong> {entry.prompt}</div>
          <div><strong>Réponse :</strong> {entry.response}</div>
          <div><strong>Anxiété :</strong> {entry.anxiety_score ?? "N/A"}</div>
        </div>
      ))}
    </div>
  );
}

function useThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    document.body.style.background = dark ? "#111" : "#fff";
    document.body.style.color = dark ? "#f1f1f1" : "#000";
  }, [dark]);
  return [dark, () => setDark(!dark)];
}

export default function App() {
  return (
    <Router>
      <NavMenu />
      <ThemeToggle />
      <Routes>
        <Route path="/" element={<DashboardIangel />} />
        <Route path="/ask" element={<AskIangel />} />
        <Route path="/reflexions" element={<ProtectedRoute><SelfReflectionDashboard /></ProtectedRoute>} />
        <Route path="/reset-pass" element={<PasswordReset />} />
        <Route path="/conversations" element={<ConversationsLog />} />
        <Route path="*" element={<Navigate to="/ask" />} />
      </Routes>
    </Router>
  );
}
