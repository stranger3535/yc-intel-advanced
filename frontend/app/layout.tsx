import "./globals.css";
import Link from "next/link";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <nav style={{ padding: "16px 32px" }}>
          <Link href="/">Chat</Link>
          <Link href="/companies">Companies</Link>
          <Link href="/trends">Trends</Link>
          <Link href="/leaderboard">Leaderboard</Link>
        </nav>

        <main>
          <div className="container">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}