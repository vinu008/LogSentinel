import { useEffect, useState, useRef } from "react";
import { fetchLogs, connectAnomalySocket } from "./api";

const LEVEL_COLORS = {
  DEBUG: "#888",
  INFO: "#2196F3",
  WARN: "#FF9800",
  ERROR: "#f44336",
  FATAL: "#9C27B0",
};

export default function App() {
  const [logs, setLogs] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [serviceFilter, setServiceFilter] = useState("");
  const [levelFilter, setLevelFilter] = useState("");
  const wsRef = useRef(null);

  // poll logs every 3 seconds
  useEffect(() => {
    const poll = async () => {
      try {
        const data = await fetchLogs({ service: serviceFilter, level: levelFilter });
        setLogs(data);
      } catch (e) {
        console.error("Failed to fetch logs", e);
      }
    };
    poll();
    const interval = setInterval(poll, 3000);
    return () => clearInterval(interval);
  }, [serviceFilter, levelFilter]);

  // connect anomaly websocket once
  useEffect(() => {
    wsRef.current = connectAnomalySocket((anomaly) => {
      setAnomalies((prev) => [anomaly, ...prev].slice(0, 20));
    });
    return () => wsRef.current?.close();
  }, []);

  return (
    <div style={{ fontFamily: "monospace", padding: 24, background: "#0f0f0f", minHeight: "100vh", color: "#eee" }}>
      <h1 style={{ color: "#4fc3f7" }}>LogSentinel</h1>

      {/* Anomaly Panel */}
      {anomalies.length > 0 && (
        <div style={{ marginBottom: 24, background: "#1a1a1a", borderRadius: 8, padding: 16, borderLeft: "4px solid #f44336" }}>
          <h3 style={{ color: "#f44336", margin: "0 0 12px" }}>⚠ Recent Anomalies</h3>
          {anomalies.map((a, i) => (
            <div key={i} style={{ marginBottom: 6, fontSize: 13 }}>
              <strong>{a.service}</strong> — error rate {(a.error_rate * 100).toFixed(1)}%
              (Z-score: {a.zscore}) at {new Date(a.detected_at * 1000).toLocaleTimeString()}
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div style={{ marginBottom: 16, display: "flex", gap: 12 }}>
        <input
          placeholder="Filter by service..."
          value={serviceFilter}
          onChange={(e) => setServiceFilter(e.target.value)}
          style={{ padding: "6px 12px", background: "#1a1a1a", border: "1px solid #333", color: "#eee", borderRadius: 4 }}
        />
        <select
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
          style={{ padding: "6px 12px", background: "#1a1a1a", border: "1px solid #333", color: "#eee", borderRadius: 4 }}
        >
          <option value="">All levels</option>
          {["DEBUG","INFO","WARN","ERROR","FATAL"].map(l => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>
      </div>

      {/* Log Table */}
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ background: "#1a1a1a", textAlign: "left" }}>
            <th style={{ padding: "8px 12px", color: "#888" }}>Timestamp</th>
            <th style={{ padding: "8px 12px", color: "#888" }}>Service</th>
            <th style={{ padding: "8px 12px", color: "#888" }}>Level</th>
            <th style={{ padding: "8px 12px", color: "#888" }}>Message</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #1a1a1a" }}>
              <td style={{ padding: "6px 12px", color: "#888" }}>{log.timestamp}</td>
              <td style={{ padding: "6px 12px" }}>{log.service}</td>
              <td style={{ padding: "6px 12px", color: LEVEL_COLORS[log.level] ?? "#eee", fontWeight: "bold" }}>
                {log.level}
              </td>
              <td style={{ padding: "6px 12px" }}>{log.message}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
