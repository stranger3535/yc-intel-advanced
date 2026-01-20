import { getLeaderboard } from "@/lib/api";

export default async function LeaderboardPage() {
  const raw = await getLeaderboard();

  const data =
    raw && typeof raw === "object"
      ? raw
      : {
          top_momentum: [],
          top_stable: [],
          recent_changes: [],
        };

  const topMomentum = Array.isArray(data.top_momentum)
    ? data.top_momentum
    : [];
  const topStable = Array.isArray(data.top_stable)
    ? data.top_stable
    : [];
  const recentChanges = Array.isArray(data.recent_changes)
    ? data.recent_changes
    : [];

  return (
    <main>
      <div className="page">
        <h1>Leaderboard</h1>

        {/* TOP MOMENTUM */}
        <h2>Top Momentum</h2>
        {topMomentum.length === 0 ? (
          <p>No data</p>
        ) : (
          <table>
            <tbody>
              {topMomentum.map((c: any, i: number) => (
                <tr key={i}>
                  <td>{c.name}</td>
                  <td>{c.momentum_score ?? c.score ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <br />

        {/* MOST STABLE */}
        <h2>Most Stable</h2>
        {topStable.length === 0 ? (
          <p>No data</p>
        ) : (
          <table>
            <tbody>
              {topStable.map((c: any, i: number) => (
                <tr key={i}>
                  <td>{c.name}</td>
                  <td>{c.stability_score ?? c.score ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <br />

        {/* RECENT CHANGES */}
        <h2>Recent Changes</h2>
        {recentChanges.length === 0 ? (
          <p>No data</p>
        ) : (
          <table>
            <tbody>
              {recentChanges.map((c: any, i: number) => (
                <tr key={i}>
                  <td>{c.name}</td>
                  <td>{c.last_change ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}