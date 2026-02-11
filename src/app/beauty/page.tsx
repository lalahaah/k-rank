"use client";

import { useState, useEffect, useMemo } from "react";
import Script from "next/script";
import { Navbar } from "@/components/navbar";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { FirebaseRankingRepository } from "@/infrastructure/repositories/firebase-ranking-repository";
import type { RankingItem } from "@/domain/entities/ranking";
import { Footer } from "@/components/footer";
import { BillboardAd, SidebarAd } from "@/components/ads";

export default function BeautyPage() {
    const [rankings, setRankings] = useState<RankingItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedCategory, setSelectedCategory] = useState<string>("all");

    // Initial and Category data fetch
    useEffect(() => {
        async function fetchRankingData() {
            setLoading(true);
            try {
                const repository = new FirebaseRankingRepository();
                const data = await repository.getLatestRankings(selectedCategory);
                setRankings(data);
            } catch (error) {
                console.error('Error fetching rankings:', error);
            } finally {
                setLoading(false);
            }
        }

        fetchRankingData();
    }, [selectedCategory]);

    // Filter rankings based on search query
    const filteredRankings = searchQuery.trim()
        ? rankings.filter((item) =>
            item.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
            item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
        )
        : rankings;

    // JSON-LD 구조화된 데이터 생성 (SEO)
    const jsonLdItemList = useMemo(() => {
        if (!rankings.length) return null;

        return {
            '@context': 'https://schema.org',
            '@type': 'ItemList',
            name: 'K-Beauty Product Rankings',
            description: 'AI-curated K-Beauty rankings from Olive Young, Hwahae, and Glowpick',
            numberOfItems: rankings.length,
            itemListElement: rankings.slice(0, 10).map((item, index) => ({
                '@type': 'ListItem',
                position: index + 1,
                item: {
                    '@type': 'Product',
                    name: item.productName,
                    brand: {
                        '@type': 'Brand',
                        name: item.brand,
                    },
                    image: item.imageUrl,
                    offers: {
                        '@type': 'Offer',
                        price: String(item.price || '0').replace(/[^0-9]/g, ''),
                        priceCurrency: 'KRW',
                        availability: 'https://schema.org/InStock',
                    },
                    aggregateRating: item.rank <= 3 ? {
                        '@type': 'AggregateRating',
                        ratingValue: '5',
                        reviewCount: '100',
                    } : undefined,
                },
            })),
        };
    }, [rankings]);

    return (
        <div className="min-h-screen bg-canvas">
            {/* JSON-LD for SEO */}
            {jsonLdItemList && (
                <Script
                    id="jsonld-beauty-products"
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdItemList) }}
                />
            )}

            <Navbar />

            {/* Billboard Ad (Header Bottom) */}
            <BillboardAd />

            {/* Hero Section - Beauty Theme (Aligned with Food Style) */}
            <section className="bg-white py-16 md:py-24 overflow-hidden relative">
                <div className="max-w-6xl mx-auto px-4 relative z-10">
                    <div className="max-w-2xl">
                        <div className="inline-flex items-center gap-2 bg-beauty-50 text-beauty-600 px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest mb-6">
                            <span className="flex h-2 w-2 rounded-full bg-beauty-500 animate-pulse"></span>
                            AI-Curated from Top K-Beauty Platforms
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black text-gray-900 tracking-tighter leading-[0.9] mb-6">
                            DECODE K-BEAUTY <br />
                            <span className="text-beauty-500">TRENDS NOW.</span>
                        </h1>
                        <p className="text-lg text-gray-500 font-medium leading-relaxed">
                            The definitive guide to what's actually trending in Korea's beauty scene. Our AI editor analyzes daily rankings from <strong className="text-gray-900">Olive Young</strong>, <strong className="text-gray-900">Hwahae</strong>, and <strong className="text-gray-900">Glowpick</strong> to show you the real winners.
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
                            { id: "all", label: "All" },
                            { id: "skincare", label: "Skincare" },
                            { id: "suncare", label: "Suncare" },
                            { id: "masks", label: "Masks" },
                            { id: "makeup", label: "Makeup" },
                            { id: "haircare", label: "Haircare" },
                            { id: "bodycare", label: "Bodycare" }
                        ].map((cat) => (
                            <button
                                key={cat.id}
                                onClick={() => setSelectedCategory(cat.id)}
                                className={`px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all whitespace-nowrap ${selectedCategory === cat.id
                                    ? 'bg-beauty-500 text-white shadow-lg shadow-beauty-500/30'
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
                            placeholder="Search beauty..."
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-gray-50 border-none rounded-2xl py-3 pl-12 pr-4 text-xs font-bold focus:ring-2 focus:ring-beauty-500/20"
                        />
                        <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                    </div>
                </div>
            </div >

            {/* Main Content */}
            < div className="mx-auto max-w-6xl px-4 py-12" >
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2">
                        {loading ? (
                            <div className="text-center py-12">
                                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-beauty-500 border-r-transparent"></div>
                                <p className="mt-4 text-gray-500">Loading rankings...</p>
                            </div>
                        ) : (
                            <LeaderboardTable rankings={filteredRankings} isCategoryHidden={true} />
                        )}
                    </div>

                    {/* Sidebar Sticky Ad */}
                    <div className="hidden lg:block">
                        <SidebarAd />
                    </div>
                </div>
            </div >

            {/* Beauty Shopping Essentials */}
            < section className="max-w-6xl mx-auto px-6 mb-20" >
                <div className="bg-gray-900 rounded-[3rem] p-10 md:p-16 relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-beauty-500 rounded-full blur-[120px] opacity-20 -translate-y-1/2 translate-x-1/2"></div>
                    <div className="relative z-10">
                        <h3 className="text-3xl md:text-5xl font-black text-white tracking-tighter mb-4">
                            WANT THESE <br /> <span className="text-beauty-500">GLOW GEMS?</span>
                        </h3>
                        <p className="text-gray-400 font-medium text-sm md:text-base">
                            Shop the latest K-Beauty trends with international shipping.
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-3 relative z-10">
                        <a
                            href="https://global.oliveyoung.com/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-beauty-500 hover:text-white transition-all shadow-xl"
                        >
                            Olive Young Global
                        </a>
                        <a
                            href="https://www.hwahae.com/en"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-beauty-500 hover:text-white transition-all shadow-xl"
                        >
                            Hwahae Global
                        </a>
                        <a
                            href="https://www.glowpick.com/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-beauty-500 hover:text-white transition-all shadow-xl"
                        >
                            Glowpick
                        </a>
                        <a
                            href="https://www.yesstyle.com/en/beauty.html"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-beauty-500 hover:text-white transition-all shadow-xl"
                        >
                            YesStyle Beauty
                        </a>
                    </div>
                </div>
            </section >


            {/* Footer */}
            < Footer />
        </div >
    );
}
