import type { Metadata } from "next";
import { Providers } from "./providers";
import { Sidebar } from "@/components/layout/Sidebar";
import "@/styles/globals.css";

export const metadata: Metadata = { title: "AURA — Data Engine", description: "Universal data ingestion, cleaning, and AI insights" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-bg text-text">
        <Providers>
          <Sidebar />
          <main className="ml-[280px] min-h-screen px-8 py-8">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
