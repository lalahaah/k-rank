"use client";

import { useState, useEffect, useMemo } from "react";
import Script from "next/script";
import { Navbar } from "@/components/navbar";
import { MediaLeaderboardTable } from "@/components/media-leaderboard-table";
import { FirebaseRankingRepository } from "@/infrastructure/repositories/firebase-ranking-repository";
import type { MediaRankingItem } from "@/domain/entities/ranking";
import { Footer } from "@/components/footer";
import { VpnCta } from "@/components/vpn-cta";

export default function MediaPage() {
    const [rankings, setRankings] = useState<MediaRankingItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string>("TV Show");

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

    // Filter rankings based on category and search query
    const filteredRankings = rankings
        .filter(item => item.type === selectedCategory)
        .filter((item) => {
            if (!searchQuery.trim()) return true;
            return (
                item.titleEn.toLowerCase().includes(searchQuery.toLowerCase()) ||
                (item.titleKo && item.titleKo.toLowerCase().includes(searchQuery.toLowerCase())) ||
                item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
            );
        });

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

            {/* Hero Section - Media Theme (Aligned with Food Style) */}
            <section className="bg-white py-16 md:py-24 overflow-hidden relative">
                <div className="max-w-6xl mx-auto px-4 relative z-10">
                    <div className="max-w-2xl">
                        <div className="inline-flex items-center gap-2 bg-media-50 text-media-600 px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest mb-6">
                            <span className="flex h-2 w-2 rounded-full bg-media-500 animate-pulse"></span>
                            Real-time Data from Netflix
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black text-gray-900 tracking-tighter leading-[0.9] mb-6">
                            WATCH K-MEDIA <br />
                            <span className="text-media-500">THE HYPE.</span>
                        </h1>
                        <p className="text-lg text-gray-500 font-medium leading-relaxed">
                            Discover the shows and movies that are dominating Korean screens right now. Real-time insights from Netflix Top 10.
                        </p>
                    </div>
                </div>
            </section>

            {/* Navigation & Search Bar */}
            <div className="sticky top-16 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
                <div className="max-w-6xl mx-auto px-4 h-20 flex items-center gap-4">
                    {/* Category Filters */}
                    <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-2">
                        {[
                            { id: "TV Show", label: "TV Shows" },
                            { id: "Film", label: "Movies" },
                        ].map((cat) => (
                            <button
                                key={cat.id}
                                onClick={() => setSelectedCategory(cat.id)}
                                className={`px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all whitespace-nowrap ${selectedCategory === cat.id
                                    ? 'bg-media-500 text-white shadow-lg shadow-media-500/30'
                                    : 'text-gray-400 hover:text-gray-900'
                                    }`}
                            >
                                {cat.label}
                            </button>
                        ))}
                    </div>

                    {/* Search Bar */}
                    <div className="flex-1 hidden md:flex relative max-w-sm ml-auto">
                        <input
                            type="text"
                            placeholder="Search media..."
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-gray-50 border-none rounded-2xl py-3 pl-12 pr-4 text-xs font-bold focus:ring-2 focus:ring-media-500/20"
                        />
                        <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    </div>
                </div>
            </div >

            {/* Main Content */}
            < div className="mx-auto max-w-6xl px-6 py-12" >
                {
                    loading ? (
                        <div className="text-center py-12" >
                            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-media-500 border-r-transparent"></div>
                            <p className="mt-4 text-gray-500">Loading rankings...</p>
                        </div>
                    ) : (
                        <MediaLeaderboardTable rankings={filteredRankings} isCategoryHidden={true} />
                    )
                }
            </div >

            {/* VPN CTA */}
            < VpnCta />

            {/* Footer */}
            < Footer />
        </div >
    );
}
