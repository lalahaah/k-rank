import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Analytics } from "@vercel/analytics/react";
import Script from "next/script";
import { ScrollToTop } from "@/components/scroll-to-top";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL('https://k-rank.vercel.app'),
  title: {
    default: "K-Rank Leaderboard | Real-time Korean Trends Rankings",
    template: "%s | K-Rank"
  },
  description: "The OP.GG for K-Trends - Discover real-time rankings of K-Beauty, K-Media, K-Food, and K-Places. Track trending Korean products and content updated daily from Seoul.",
  keywords: [
    "K-Beauty Rankings",
    "Korean Beauty Products",
    "K-Drama Rankings",
    "Netflix Korea",
    "Korean Trends",
    "Hwahae Global Rankings",
    "K-Pop",
    "Korean Culture",
    "Seoul Trends",
    "K-Rank"
  ],
  authors: [{ name: "K-Rank Team" }],
  creator: "K-Rank",
  publisher: "K-Rank",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    alternateLocale: ['en_US'],
    url: 'https://k-rank.vercel.app',
    siteName: 'K-Rank Leaderboard',
    title: 'K-Rank Leaderboard | Real-time Korean Trends Rankings',
    description: 'The OP.GG for K-Trends - Discover real-time rankings of K-Beauty, K-Media, K-Food, and K-Places.',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'K-Rank Leaderboard - Real-time Korean Trends',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'K-Rank Leaderboard | Real-time Korean Trends Rankings',
    description: 'The OP.GG for K-Trends - Track trending Korean products and content updated daily from Seoul.',
    images: ['/twitter-image.png'],
    creator: '@krank',
  },
  verification: {
    google: 'your-google-verification-code',
    other: {
      'impact-site-verification': '9840cd48-4996-4dce-970b-b6035e2229a5',
    },
    // yandex: 'your-yandex-verification-code',
    // bing: 'your-bing-verification-code',
  },
  alternates: {
    canonical: 'https://k-rank.vercel.app',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const gaId = process.env.NEXT_PUBLIC_GA_ID;

  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={`${inter.variable} antialiased`}>
        {/* Google Analytics */}
        {gaId && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${gaId}`}
              strategy="afterInteractive"
            />
            <Script id="google-analytics" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${gaId}');
              `}
            </Script>
          </>
        )}

        {children}
        <ScrollToTop />

        {/* Vercel Analytics */}
        <Analytics />
      </body>
    </html>
  );
}
