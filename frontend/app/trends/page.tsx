import { getTrends } from "@/lib/api";

export default async function TrendsPage() {
  const raw = await getTrends();

  // normalize backend response
  const trends = Array.isArray(raw)
    ? raw
    : Array.isArray(raw?.trends)
    ? raw.trends
    : Array.isArray(raw?.data)
    ? raw.data
    : [];

  return (
    <div style={{ padding: 24, color: "#e5e7eb" }}>
      <h1 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>
        Trends
      </h1>

      {trends.length === 0 ? (
        <p>No trends data available</p>
      ) : (
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            background: "#020617",
          }}
        >
          <thead>
            <tr>
              <th style={th}>Category</th>
              <th style={th}>Count</th>
            </tr>
          </thead>
          <tbody>
            {trends.map((t: any, i: number) => (
              <tr key={i}>
                <td style={td}>{t.category ?? t.tag ?? "—"}</td>
                <td style={td}>{t.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

const th = {
  border: "1px solid #334155",
  padding: "8px",
  textAlign: "left" as const,
};

const td = {
  border: "1px solid #334155",
  padding: "8px",
};