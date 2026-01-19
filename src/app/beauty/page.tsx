"use client";

import { useState, useEffect, useMemo } from "react";
import Script from "next/script";
import { Navbar } from "@/components/navbar";
import { LeaderboardTable } from "@/components/leaderboard-table";
import { SearchBar } from "@/components/search-bar";
import { FirebaseRankingRepository } from "@/infrastructure/repositories/firebase-ranking-repository";
import type { RankingItem } from "@/domain/entities/ranking";
import { CtaSection } from "@/components/cta-section";
import { Footer } from "@/components/footer";

// 페이지 메타데이터는 layout.tsx 또는 별도의 metadata export로 처리
// "use client" 페이지에서는 직접 export 불가능하므로 별도 파일 필요


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
            description: 'Real-time top trending K-Beauty products from Olive Young',
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
                        price: item.price?.replace(/[^0-9]/g, '') || '0',
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

            {/* Hero Section */}
            <div className="w-full bg-beauty-500">
                <div className="mx-auto max-w-[1020px] px-4 py-16">
                    <h1 className="text-4xl font-bold text-white mb-3">
                        Real-time K-Beauty Leaderboard
                    </h1>
                    <p className="text-white/90 text-lg mb-8">
                        Track the top performing beauty products in Korea. Updated daily.
                    </p>

                    {/* Search Bar */}
                    <SearchBar onSearch={setSearchQuery} placeholder="Search brands, products, tags..." />
                </div>
            </div>

            {/* Main Content */}
            <div className="mx-auto max-w-[1020px] px-4 py-8">
                {loading ? (
                    <div className="text-center py-12">
                        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent opacity-50"></div>
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
