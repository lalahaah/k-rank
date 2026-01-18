"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/navbar";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { SearchBar } from "@/components/search-bar";
import { FirebaseRankingRepository } from "@/infrastructure/repositories/firebase-ranking-repository";
import type { RankingItem } from "@/domain/entities/ranking";
import { CtaSection } from "@/components/cta-section";
import { Footer } from "@/components/footer";

export default function BeautyPage() {
    const [rankings, setRankings] = useState<RankingItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const category: string = "all"; // Default category for beauty page

    // Initial data fetch
    useEffect(() => {
        async function fetchInitialData() {
            try {
                const repository = new FirebaseRankingRepository();
                const data = await repository.getLatestRankings('all');
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
            <div className={`w-full ${category === 'media' ? 'bg-slate-900' : 'bg-brand-500'}`}>
                <div className="mx-auto max-w-[1020px] px-4 py-16">
                    <h1 className="text-4xl font-bold text-white mb-3">
                        Real-time K-Beauty Leaderboard
                    </h1>
                    <p className="text-white/90 text-lg mb-8">
                        Track the top performing beauty products in Korea. Updated daily.
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
