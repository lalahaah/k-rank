"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/navbar";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { SearchBar } from "@/components/search-bar";
import { getLatestRankings } from "@/lib/data";
import type { RankingItem } from "@/components/leaderboard-table";
import { CtaSection } from "@/components/cta-section";
import { Footer } from "@/components/footer";

export default function Home() {
  const [rankings, setRankings] = useState<RankingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  // Initial data fetch
  useEffect(() => {
    async function fetchInitialData() {
      try {
        const data = await getLatestRankings('all');
        setRankings(data);
      } catch (error) {
        console.error('Error fetching rankings:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchInitialData();
  }, []);

  // Filter rankings based on search query
  const filteredRankings = searchQuery.trim()
    ? rankings.filter((item) =>
      item.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.brand.toLowerCase().includes(searchQuery.toLowerCase())
    )
    : rankings;

  return (
    <div className="min-h-screen bg-canvas">
      <Navbar />

      {/* Hero Section */}
      <div className="w-full bg-brand-500">
        <div className="mx-auto max-w-[1020px] px-4 py-16">
          <h1 className="text-4xl font-bold text-white mb-3">
            Real-time K-Trend Leaderboard
          </h1>
          <p className="text-white/90 text-lg mb-8">
            Track the top performing products, places, and media in Korea. Updated daily.
          </p>

          {/* Search Bar */}
          <SearchBar onSearch={setSearchQuery} />
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-[1020px] px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-brand-500 border-r-transparent"></div>
            <p className="mt-4 text-gray-500">Loading rankings...</p>
          </div>
        ) : (
          <LeaderboardTable rankings={filteredRankings} />
        )}
      </div>

      {/* CTA Section */}
      <CtaSection />

      {/* Footer */}
      <Footer />
    </div>
  );
}
