import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "meme_maker",
  description: "Make memes by placing faces on popular templates",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <header className="header">
            <a href="/" className="brand">meme_maker</a>
            <nav className="nav">
              <a href="/admin/templates">Anchor templates</a>
            </nav>
          </header>
          {children}
          <footer className="footer">Built with Next.js + FastAPI</footer>
        </div>
      </body>
    </html>
  );
}
