"use client";

import { Play, TrendingUp, TrendingDown, Minus, Unlock } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import type { MediaRankingItem } from "@/domain/entities/ranking";

interface MediaLeaderboardTableProps {
    rankings: MediaRankingItem[];
}

const categories = [
    { id: "TV Show", label: "TV Shows" },
    { id: "Film", label: "Movies" },
];

export function MediaLeaderboardTable({ rankings }: MediaLeaderboardTableProps) {
    const [selectedCategory, setSelectedCategory] = useState<string>("TV Show");

    // Filter rankings based on selected category
    const filteredRankings = rankings.filter(item => item.type === selectedCategory);

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
                                ? "bg-media-500 text-white shadow-md"
                                : "bg-white text-gray-500 border border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                                }`}
                        >
                            {cat.label}
                        </button>
                    ))}
                </div>
            </div>
            {/* Table */}
            {filteredRankings.length === 0 ? (
                <div className="bg-bg-surface rounded-lg shadow-lg overflow-hidden">
                    <div className="py-20 text-center text-gray-500">
                        <p>미디어 랭킹 데이터가 없습니다.</p>
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
                                Title
                            </span>
                        </div>
                        <div className="col-span-2 text-center">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Trend
                            </span>
                        </div>
                        <div className="col-span-2">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Weeks in Top 10
                            </span>
                        </div>
                        <div className="col-span-2 text-center">
                            <span className="text-xs font-bold text-text-muted uppercase">
                                Action
                            </span>
                        </div>
                    </div>

                    {/* Data Rows */}
                    <div className="divide-y divide-gray-100">
                        {filteredRankings.map((item) => (
                            <div
                                key={item.rank}
                                /* 모바일: 카드 레이아웃, 태블릿 이상: 그리드 레이아웃 */
                                className="flex flex-col gap-3 p-4 md:grid md:grid-cols-12 md:gap-4 md:px-6 md:py-4 md:items-center hover:bg-red-50 transition-colors group"
                            >
                                {/* 모바일 헤더 행: Rank + Title + Image */}
                                <div className="flex items-center gap-3 md:col-span-6">
                                    {/* Rank */}
                                    <div className="flex-shrink-0 md:col-span-1 md:text-center">
                                        <span className="text-2xl md:text-base font-bold text-text-heading font-mono">
                                            {item.rank}
                                        </span>
                                    </div>

                                    {/* Image + Title */}
                                    <div className="flex items-center gap-3 flex-1 min-w-0 md:col-span-5">
                                        <div className="relative w-16 h-16 md:w-12 md:h-12 rounded-md overflow-hidden border border-gray-200 flex-shrink-0 bg-gray-100">
                                            <Image
                                                src={item.imageUrl}
                                                alt={item.titleEn}
                                                fill
                                                className="object-cover"
                                                sizes="(max-width: 768px) 64px, 48px"
                                            />
                                        </div>
                                        <div className="min-w-0 flex-1">
                                            <div className="font-bold text-base md:text-sm text-text-heading line-clamp-2 md:truncate">
                                                {item.titleEn}
                                            </div>
                                            {item.titleKo && item.titleKo !== item.titleEn && (
                                                <div className="text-sm md:text-xs text-text-muted line-clamp-1 md:truncate">
                                                    {item.titleKo}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* 모바일 메타 정보: Trend + Weeks */}
                                <div className="flex items-center justify-between md:contents">
                                    {/* Trend */}
                                    <div className="md:col-span-2 md:flex md:justify-center">
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
                                                
                                            </span>
                                        )}
                                    </div>

                                    {/* Weeks in Top 10 */}
                                    <div className="md:col-span-2 md:text-center">
                                        <span className="text-sm font-bold text-media-600">
                                            {item.weeksInTop10} {parseInt(item.weeksInTop10) === 1 ? 'week' : 'weeks'}
                                        </span>
                                    </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex gap-2 md:col-span-2 md:justify-center">
                                    <a
                                        href={item.trailerLink}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex-1 md:flex-initial inline-block"
                                    >
                                        <button
                                            className="w-full md:w-auto bg-media-500 hover:bg-media-600 text-white px-4 py-2 md:px-3 md:py-1.5 rounded-md text-sm md:text-xs font-medium flex items-center justify-center gap-1.5 md:gap-1 transition-transform active:scale-95"
                                            title="Watch Trailer"
                                        >
                                            <Play size={14} className="md:w-3 md:h-3" fill="currentColor" />
                                            Trailer
                                        </button>
                                    </a>
                                    {item.vpnLink && (
                                        <a
                                            href={item.vpnLink}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex-1 md:flex-initial inline-block"
                                        >
                                            <button
                                                className="w-full md:w-auto bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 md:px-3 md:py-1.5 rounded-md text-sm md:text-xs font-medium flex items-center justify-center gap-1.5 md:gap-1 transition-transform active:scale-95"
                                                title="Unlock with VPN"
                                            >
                                                <Unlock size={14} className="md:w-3 md:h-3" />
                                                VPN
                                            </button>
                                        </a>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
