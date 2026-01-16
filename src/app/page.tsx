import { Search } from "lucide-react";
import { Navbar } from "@/components/navbar";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { getLatestRankings } from "@/lib/data";

export default async function Home() {
  // Fetch real data from Firebase
  const rankings = await getLatestRankings('beauty');

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
          <div className="relative max-w-2xl">
            <input
              type="text"
              placeholder="Search brands, spots, or dramas..."
              className="w-full px-6 py-4 pr-14 rounded-full text-lg border-none focus:outline-none focus:ring-2 focus:ring-white/50"
            />
            <button className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700">
              <Search className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-[1020px] px-4 py-8">
        <LeaderboardTable rankings={rankings} />
      </div>
    </div>
  );
}
