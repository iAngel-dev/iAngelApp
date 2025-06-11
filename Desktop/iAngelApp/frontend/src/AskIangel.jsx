// AskIangel.jsx
import React, { useState } from "react";

export default function AskIangel() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);
  const [audio, setAudio] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!message.trim()) return;
    setLoading(true);
    try {
      const user_id = "felix";
      const res = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id, prompt: message })
      });
      const data = await res.json();
      setResponse(data.response);
      setAudio(data.audio_path);

      await fetch("http://localhost:5002/log_conversation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id,
          prompt: message,
          response: data.response,
          anxiety_score: data.anxiety_score || null
        })
      });
    } catch (err) {
      setResponse("Erreur: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h2>💬 Parlez à iAngel</h2>
      <input
        type="text"
        value={message}
        onChange={e => setMessage(e.target.value)}
        placeholder="Posez votre question à iAngel"
        style={{ width: "80%", padding: "0.5rem" }}
      />
      <button onClick={handleAsk} style={{ marginLeft: "1rem", padding: "0.5rem 1rem" }}>
        Envoyer
      </button>
      {loading && <p>⏳ Chargement...</p>}
      {response && <p><strong>Réponse :</strong> {response}</p>}
      {audio && (
        <audio controls src={audio} style={{ marginTop: "1rem" }}>
          Votre navigateur ne supporte pas l'audio.
        </audio>
      )}
    </div>
  );
}
