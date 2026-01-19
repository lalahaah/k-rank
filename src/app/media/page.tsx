"use client";

import { useState, useEffect, useMemo } from "react";
import Script from "next/script";
import { Navbar } from "@/components/navbar";
import { MediaLeaderboardTable } from "@/components/media-leaderboard-table";
import { SearchBar } from "@/components/search-bar";
import { FirebaseRankingRepository } from "@/infrastructure/repositories/firebase-ranking-repository";
import type { MediaRankingItem } from "@/domain/entities/ranking";
import { Footer } from "@/components/footer";
import { VpnCta } from "@/components/vpn-cta";

export default function MediaPage() {
    const [rankings, setRankings] = useState<MediaRankingItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");

    // Initial data fetch
    useEffect(() => {
        async function fetchInitialData() {
            try {
                const repository = new FirebaseRankingRepository();
                const data = await repository.getMediaRankings();
                setRankings(data);
            } catch (error) {
                console.error('Error fetching media rankings:', error);
            } finally {
                setLoading(false);
            }
        }

        fetchInitialData();
    }, []);

    // Filter rankings based on search query
    const filteredRankings = searchQuery.trim()
        ? rankings.filter((item) =>
            item.titleEn.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (item.titleKo && item.titleKo.toLowerCase().includes(searchQuery.toLowerCase())) ||
            item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
        )
        : rankings;

    // JSON-LD 구조화된 데이터 생성 (SEO)
    const jsonLdItemList = useMemo(() => {
        if (!rankings.length) return null;

        return {
            '@context': 'https://schema.org',
            '@type': 'ItemList',
            name: 'Netflix Korea Top 10 Rankings',
            description: 'Real-time top trending K-Dramas and Korean shows on Netflix',
            numberOfItems: rankings.length,
            itemListElement: rankings.slice(0, 10).map((item, index) => ({
                '@type': 'ListItem',
                position: index + 1,
                item: {
                    '@type': 'Movie',
                    name: item.titleEn,
                    alternateName: item.titleKo,
                    image: item.imageUrl,
                    genre: item.tags,
                    aggregateRating: {
                        '@type': 'AggregateRating',
                        ratingValue: item.rank <= 3 ? '9' : '8',
                        bestRating: '10',
                        ratingCount: '1000',
                    },
                    contentRating: item.tags.includes('Family') ? 'G' : item.tags.includes('Romance') ? 'PG-13' : 'TV-MA',
                },
            })),
        };
    }, [rankings]);


    return (
        <div className="min-h-screen bg-canvas">
            {/* JSON-LD for SEO */}
            {jsonLdItemList && (
                <Script
                    id="jsonld-media-rankings"
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdItemList) }}
                />
            )}

            <Navbar />

            {/* Hero Section - Media Theme */}
            <div className="w-full bg-media-500">
                <div className="mx-auto max-w-[1020px] px-4 py-16">
                    <h1 className="text-4xl font-bold text-white mb-3">
                        🎬 K-Media Leaderboard
                    </h1>
                    <p className="text-white/90 text-lg mb-8">
                        Track the top trending Korean dramas and shows on Netflix. Updated daily.
                    </p>

                    {/* Search Bar */}
                    <SearchBar onSearch={setSearchQuery} placeholder="Search titles, tags..." />
                </div>
            </div>

            {/* Main Content */}
            <div className="mx-auto max-w-[1020px] px-4 py-8">
                {loading ? (
                    <div className="text-center py-12">
                        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-media-500 border-r-transparent"></div>
                        <p className="mt-4 text-gray-500">Loading rankings...</p>
                    </div>
                ) : (
                    <MediaLeaderboardTable rankings={filteredRankings} />
                )}
            </div>

            {/* VPN CTA */}
            <VpnCta />

            {/* Footer */}
            <Footer />
        </div>
    );
}
