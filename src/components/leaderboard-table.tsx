"use client";

import { TrendingUp, TrendingDown, Minus, ShoppingCart } from "lucide-react";
import Image from "next/image";
import { useState, useEffect } from "react";
import { getLatestRankings } from "@/lib/data";

export interface RankingItem {
    rank: number;
    productName: string;
    brand: string;
    imageUrl: string;
    price: string;
    trend: number; // 양수=상승, 음수=하락, 0=유지
    tags: string[];
    buyUrl?: string;
    subcategory: string; // 서브 카테고리 필터용
}

interface LeaderboardTableProps {
    rankings: RankingItem[];
}

const categories = [
    { id: "all", label: "All" },
    { id: "skincare", label: "Skincare" },
    { id: "suncare", label: "Suncare" },
    { id: "masks", label: "Masks" },
    { id: "makeup", label: "Makeup" },
    { id: "haircare", label: "Haircare" },
    { id: "bodycare", label: "Bodycare" },
];

export function LeaderboardTable({ rankings: initialRankings }: LeaderboardTableProps) {
    const [selectedCategory, setSelectedCategory] = useState<string>("all");
    const [rankings, setRankings] = useState<RankingItem[]>(initialRankings);
    const [loading, setLoading] = useState(false);

    // 카테고리 변경 시 서버에서 새 데이터 가져오기
    useEffect(() => {
        async function fetchCategoryData() {
            if (selectedCategory === 'all') {
                // 'all'은 초기 데이터 사용
                setRankings(initialRankings);
                return;
            }

            setLoading(true);
            try {
                const data = await getLatestRankings(selectedCategory);
                setRankings(data);
            } catch (error) {
                console.error('Error fetching category data:', error);
            } finally {
                setLoading(false);
            }
        }

        fetchCategoryData();
    }, [selectedCategory, initialRankings]);

    return (
        <div>
            {/* Filter Bar */}
            <div className="mb-4 overflow-x-auto">
                <div className="flex gap-2 min-w-max pb-2">
                    {categories.map((cat) => (
                        <button
                            key={cat.id}
                            onClick={() => setSelectedCategory(cat.id)}
                            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${selectedCategory === cat.id
                                ? "bg-brand-500 text-white shadow-md"
                                : "bg-white text-gray-500 border border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                                }`}
                        >
                            {cat.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            {loading ? (
                <div className="bg-bg-surface rounded-lg shadow-lg overflow-hidden">
                    <div className="py-20 text-center">
                        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-brand-500 border-r-transparent"></div>
                        <p className="mt-4 text-gray-500">카테고리 데이터 로딩 중...</p>
                    </div>
                </div>
            ) : rankings.length === 0 ? (
                <div className="bg-bg-surface rounded-lg shadow-lg overflow-hidden">
                    <div className="py-20 text-center text-gray-500">
                        <p>랭킹 데이터가 없습니다.</p>
                        <p className="text-sm mt-2">스크립트를 실행하여 데이터를 생성해주세요.</p>
                    </div>
                </div>
            ) : (
                <div className="bg-bg-surface rounded-lg shadow-lg overflow-hidden">
                    {/* Header Row */}
                    <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-gray-50 border-b border-gray-100">
                        <div className="col-span-1 text-center">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Rank
                            </span>
                        </div>
                        <div className="col-span-5">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Product
                            </span>
                        </div>
                        <div className="col-span-2 text-center">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Trend
                            </span>
                        </div>
                        <div className="col-span-3">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Tags
                            </span>
                        </div>
                        <div className="col-span-1 text-center">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Action
                            </span>
                        </div>
                    </div>

                    {/* Data Rows */}
                    <div className="divide-y divide-gray-100">
                        {rankings.map((item) => (
                            <div
                                key={item.rank}
                                className="grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-brand-50 transition-colors group"
                            >
                                {/* Rank */}
                                <div className="col-span-1 text-center">
                                    <span className="text-base font-bold text-text-heading font-mono">
                                        {item.rank}
                                    </span>
                                </div>

                                {/* Product */}
                                <div className="col-span-5 flex items-center gap-3">
                                    <div className="relative w-12 h-12 rounded-md overflow-hidden border border-gray-200 flex-shrink-0 bg-gray-100">
                                        <Image
                                            src={item.imageUrl}
                                            alt={item.productName}
                                            fill
                                            className="object-cover"
                                            sizes="48px"
                                        />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <div className="font-bold text-sm text-text-heading truncate">
                                            {item.productName}
                                        </div>
                                        <div className="text-xs text-text-muted truncate">
                                            {item.brand}
                                        </div>
                                        <div className="text-xs font-medium text-heading">
                                            {item.price}
                                        </div>
                                    </div>
                                </div>

                                {/* Trend */}
                                <div className="col-span-2 flex justify-center">
                                    {item.trend > 0 ? (
                                        <span className="flex items-center gap-1 text-xs font-bold text-trend-up bg-red-50 px-2 py-1 rounded">
                                            <TrendingUp size={14} />
                                            {item.trend}
                                        </span>
                                    ) : item.trend < 0 ? (
                                        <span className="flex items-center gap-1 text-xs font-bold text-trend-down bg-blue-50 px-2 py-1 rounded">
                                            <TrendingDown size={14} />
                                            {Math.abs(item.trend)}
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-1 text-xs font-bold text-trend-stable bg-gray-50 px-2 py-1 rounded">
                                            <Minus size={14} />
                                            0
                                        </span>
                                    )}
                                </div>

                                {/* Tags */}
                                <div className="col-span-3 flex flex-wrap gap-1">
                                    {item.tags.map((tag, idx) => (
                                        <span
                                            key={idx}
                                            className="bg-gray-100 text-gray-600 text-[10px] px-2 py-1 rounded-full"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>

                                {/* Action */}
                                <div className="col-span-1 flex justify-center">
                                    <button
                                        className="bg-brand-500 hover:bg-brand-600 text-white px-3 py-1.5 rounded-md text-xs font-medium flex items-center gap-1"
                                        onClick={() => {
                                            if (item.buyUrl) {
                                                window.open(item.buyUrl, "_blank");
                                            }
                                        }}
                                    >
                                        <ShoppingCart size={12} />
                                        Buy
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
