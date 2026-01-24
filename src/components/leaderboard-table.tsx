"use client";

import { TrendingUp, TrendingDown, Minus, ShoppingCart } from "lucide-react";
import Image from "next/image";
import { useState, useEffect } from "react";
import { FirebaseRankingRepository } from "@/infrastructure/repositories/firebase-ranking-repository";
import type { RankingItem } from "@/domain/entities/ranking";

interface LeaderboardTableProps {
    rankings: RankingItem[];
    searchQuery?: string;
    isCategoryHidden?: boolean;
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

export function LeaderboardTable({ rankings: initialRankings, isCategoryHidden = false }: LeaderboardTableProps) {
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
                const repository = new FirebaseRankingRepository();
                const data = await repository.getLatestRankings(selectedCategory);
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
            {!isCategoryHidden && (
                <div className="mb-4 overflow-x-auto">
                    <div className="flex gap-2 min-w-max pb-2">
                        {categories.map((cat) => (
                            <button
                                key={cat.id}
                                onClick={() => setSelectedCategory(cat.id)}
                                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap ${selectedCategory === cat.id
                                    ? "bg-beauty-500 text-white shadow-md"
                                    : "bg-white text-gray-500 border border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                                    }`}
                            >
                                {cat.label}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Table */}
            {loading ? (
                <div className="bg-bg-surface rounded-lg shadow-lg overflow-hidden">
                    <div className="py-20 text-center">
                        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-beauty-500 border-r-transparent"></div>
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
                    {/* Desktop Header Row - 태블릿 이상에서만 표시 */}
                    <div className="hidden md:grid grid-cols-12 gap-4 px-6 py-4 bg-gray-50 border-b border-gray-100">
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
                                /* 모바일: 카드 레이아웃, 태블릿 이상: 그리드 레이아웃 */
                                className="flex flex-col gap-3 p-4 md:grid md:grid-cols-12 md:gap-4 md:px-6 md:py-4 md:items-center hover:bg-brand-50 transition-colors group"
                            >
                                {/* 모바일 헤더 행: Rank + Product + Image */}
                                <div className="flex items-start gap-3 md:col-span-6">
                                    {/* Rank */}
                                    <div className="flex-shrink-0 md:col-span-1 md:text-center pt-1 md:pt-0">
                                        <span className="text-2xl md:text-base font-bold text-text-heading font-mono">
                                            {item.rank}
                                        </span>
                                    </div>

                                    {/* Image + Product Info */}
                                    <div className="flex items-start gap-3 flex-1 min-w-0 md:col-span-5">
                                        <div className="relative w-20 h-20 md:w-12 md:h-12 rounded-md overflow-hidden border border-gray-200 flex-shrink-0 bg-gray-100">
                                            <Image
                                                src={item.imageUrl}
                                                alt={item.productName}
                                                fill
                                                className="object-cover"
                                                sizes="(max-width: 768px) 80px, 48px"
                                                unoptimized
                                                onError={(e) => {
                                                    const target = e.target as HTMLImageElement;
                                                    target.src = "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=48&h=48&fit=crop";
                                                }}
                                            />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <div className="font-bold text-base md:text-sm text-text-heading line-clamp-2 md:truncate">
                                                {item.productName}
                                            </div>
                                            <div className="text-sm md:text-xs text-text-muted truncate mt-0.5">
                                                {item.brand}
                                            </div>
                                            <div className="text-sm md:text-xs font-medium text-heading mt-1">
                                                ₩{item.price.replace('원', '')}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* 모바일 메타 정보: Trend + Tags */}
                                <div className="flex flex-col gap-2 md:contents">
                                    {/* Trend */}
                                    <div className="md:col-span-2 md:flex md:justify-center">
                                        {item.trend > 0 ? (
                                            <span className="inline-flex items-center gap-1 text-xs font-bold text-trend-up bg-red-50 px-2 py-1 rounded w-fit">
                                                <TrendingUp size={14} />
                                                {item.trend}
                                            </span>
                                        ) : item.trend < 0 ? (
                                            <span className="inline-flex items-center gap-1 text-xs font-bold text-trend-down bg-blue-50 px-2 py-1 rounded w-fit">
                                                <TrendingDown size={14} />
                                                {Math.abs(item.trend)}
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center gap-1 text-xs font-bold text-trend-stable bg-gray-50 px-2 py-1 rounded w-fit">
                                                <Minus size={14} />
                                                0
                                            </span>
                                        )}
                                    </div>

                                    {/* Tags */}
                                    <div className="md:col-span-3 flex flex-wrap gap-1.5 md:gap-1">
                                        {item.tags.map((tag, idx) => (
                                            <span
                                                key={idx}
                                                className="bg-gray-100 text-gray-600 text-xs md:text-[10px] px-2.5 md:px-2 py-1 rounded-full"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Action Button */}
                                <div className="md:col-span-1 md:flex md:justify-center">
                                    <a
                                        href={
                                            item.buyUrl ||
                                            `https://www.amazon.com/s?k=${encodeURIComponent(item.productName)}`
                                        }
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block md:inline-block"
                                    >
                                        <button
                                            className="w-full md:w-auto bg-beauty-500 hover:bg-beauty-600 text-white px-4 py-2 md:px-3 md:py-1.5 rounded-md text-sm md:text-xs font-medium flex items-center justify-center gap-1.5 md:gap-1 transition-transform active:scale-95"
                                            title="Buy on Amazon"
                                        >
                                            <ShoppingCart size={14} className="md:w-3 md:h-3" />
                                            Buy
                                        </button>
                                    </a>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
