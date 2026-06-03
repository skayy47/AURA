import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getMessages } from "next-intl/server";
import { Providers } from "./providers";
import { TopBar } from "@/components/layout/TopBar";
import { DatasetPill } from "@/components/layout/DatasetPill";
import { BotOrb } from "@/components/layout/BotOrb";
import { IntelligenceField } from "@/components/background/IntelligenceField";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "AURA — Data Engine",
  description: "Universal data ingestion, cleaning, and AI insights",
};

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const { locale } = params;
  const messages = await getMessages();

  return (
    <html
      lang={locale}
      dir={locale === "ar" ? "rtl" : "ltr"}
      suppressHydrationWarning
    >
      <body className="text-text">
        <NextIntlClientProvider messages={messages}>
          <IntelligenceField />
          <Providers>
            <TopBar />
            <DatasetPill />
            <BotOrb />
            <main className="min-h-screen pt-14 px-8 pb-8 relative max-w-[1280px] mx-auto">
              {children}
            </main>
          </Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
