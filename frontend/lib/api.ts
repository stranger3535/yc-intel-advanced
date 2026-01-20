// frontend/lib/api.ts

const RAW_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

// ✅ ensure /api is added ONCE
export const API_BASE = RAW_API_BASE.endsWith("/api")
  ? RAW_API_BASE
  : `${RAW_API_BASE}/api`;

console.log("✅ API BASE:", API_BASE);

/* =========================
   SEARCH
========================= */
export async function searchCompany(query: string) {
  if (!query.trim()) return [];

  try {
    const res = await fetch(
      `${API_BASE}/search/search?query=${encodeURIComponent(query)}`,
      { cache: "no-store" }
    );

    if (!res.ok) {
      console.error("❌ Search API error:", res.status);
      return [];
    }

    return await res.json();
  } catch (err) {
    console.error("❌ Search API failed:", err);
    return [];
  }
}

/* =========================
   CHAT
========================= */
export async function chat(question: string) {
  const res = await fetch(`${API_BASE}/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error("Chat API failed");
  }

  return await res.json();
}

/* =========================
   TRENDS
========================= */
export async function getTrends() {
  try {
    const res = await fetch(`${API_BASE}/trends`, {
      cache: "no-store",
    });

    if (!res.ok) {
      console.error("❌ Trends API error:", res.status);
      return { trends: [] };
    }

    return await res.json(); // { trends: [...] }
  } catch (err) {
    console.error("❌ Trends API failed:", err);
    return { trends: [] };
  }
}

/* =========================
   COMPANIES
========================= */
export async function getCompanies() {
  try {
    const res = await fetch(`${API_BASE}/companies`, {
      cache: "no-store",
    });

    if (!res.ok) {
      console.error("❌ Companies API error:", res.status);
      return [];
    }

    return await res.json(); // array
  } catch (err) {
    console.error("❌ Companies fetch failed:", err);
    return [];
  }
}

/* =========================
   LEADERBOARD
========================= */
export async function getLeaderboard() {
  try {
    const res = await fetch(`${API_BASE}/leaderboard/`, {
      cache: "no-store",
    });

    if (!res.ok) {
      console.error("❌ Leaderboard API error:", res.status);
      return {
        top_momentum: [],
        top_stable: [],
        recent_changes: [],
      };
    }

    return await res.json(); // object with 3 arrays
  } catch (err) {
    console.error("❌ Leaderboard API failed:", err);
    return {
      top_momentum: [],
      top_stable: [],
      recent_changes: [],
    };
  }
}