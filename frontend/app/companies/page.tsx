"use client";

import { useEffect, useState } from "react";
import { getCompanies } from "@/lib/api";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCompanies()
      .then((data) => {
        if (Array.isArray(data)) {
          setCompanies(data);
        } else {
          setCompanies([]);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <main style={styles.main}>
      <h1 style={styles.title}>YC Companies</h1>

      {loading ? (
        <p style={styles.info}>Loading companies…</p>
      ) : companies.length === 0 ? (
        <p style={styles.info}>No companies found</p>
      ) : (
        <div style={styles.tableWrapper}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Website</th>
                <th style={styles.th}>Founded</th>
                <th style={styles.th}>Active</th>
              </tr>
            </thead>

            <tbody>
              {companies.map((c, i) => {
                const website =
                  c.domain && c.domain.startsWith("http")
                    ? c.domain
                    : c.domain
                    ? `https://${c.domain}`
                    : null;

                return (
                  <tr key={i}>
                    <td style={styles.tdStrong}>{c.name}</td>

                    <td style={styles.td}>
                      {website ? (
                        <a
                          href={website}
                          target="_blank"
                          rel="noreferrer"
                          style={styles.link}
                        >
                          {website.replace(/^https?:\/\//, "")}
                        </a>
                      ) : (
                        "—"
                      )}
                    </td>

                    <td style={styles.td}>
                      {c.founded_year ?? "—"}
                    </td>

                    <td style={styles.td}>
                      {c.is_active ? "Yes" : "No"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}

/* =========================
   Styles (NO Tailwind)
========================= */

const styles: { [key: string]: React.CSSProperties } = {
  main: {
    maxWidth: "1100px",
    margin: "0 auto",
    padding: "32px 16px",
    color: "#e5e7eb",
  },

  title: {
    fontSize: "28px",
    fontWeight: 700,
    marginBottom: "24px",
  },

  info: {
    color: "#94a3b8",
  },

  tableWrapper: {
    overflowX: "auto",
    background: "#020617",
    borderRadius: "8px",
    border: "1px solid #1e293b",
  },

  table: {
    width: "100%",
    borderCollapse: "collapse",
  },

  th: {
    textAlign: "left",
    padding: "12px",
    fontSize: "13px",
    color: "#94a3b8",
    borderBottom: "1px solid #1e293b",
    background: "#020617",
  },

  td: {
    padding: "12px",
    borderBottom: "1px solid #1e293b",
    fontSize: "14px",
    color: "#cbd5f5",
    verticalAlign: "middle",
  },

  tdStrong: {
    padding: "12px",
    borderBottom: "1px solid #1e293b",
    fontSize: "14px",
    fontWeight: 600,
    color: "#e5e7eb",
  },

  link: {
    color: "#38bdf8",
    textDecoration: "none",
  },
};