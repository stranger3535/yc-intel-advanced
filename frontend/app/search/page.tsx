"use client";

import { useState } from "react";
import { searchCompany } from "lib/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);

  async function search() {
    const data = await searchCompany(query);
    setResults(data);
  }

  return (
    <div className="p-8 text-white">
      <h1 className="text-3xl font-bold mb-4">
        Search YC Company
      </h1>

      <div className="flex gap-2 mb-6">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1 px-3 py-2 bg-slate-800 rounded"
          placeholder="Company name…"
        />
        <button
          onClick={search}
          className="px-4 py-2 bg-green-500 text-black rounded"
        >
          Search
        </button>
      </div>

      {results.map((c, i) => (
        <div key={i} className="bg-slate-900 p-4 rounded mb-3">
          <h2>{c.name}</h2>
          <p className="text-sm text-slate-400">{c.description}</p>
        </div>
      ))}
    </div>
  );
}
