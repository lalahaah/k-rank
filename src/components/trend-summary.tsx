"use client";

import React, { useState, useEffect } from 'react';
import {
    Sparkles,
    Clapperboard,
    Utensils,
    MapPin,
    TrendingUp,
    ArrowRight,
    Zap,
    Activity,
    Minus,
    TrendingDown
} from 'lucide-react';
import { FirebaseRankingRepository } from '@/infrastructure/repositories/firebase-ranking-repository';
import { RankingItem, MediaRankingItem, RestaurantRankingItem, PlaceRankingItem } from '@/domain/entities/ranking';

/**
 * K-Rank Trend Summary Infographic (v2.0 - Pulse Update)
 * 4개 섹션의 1위 데이터에 최근 7일간의 트렌드 흐름(Sparkline)을 연동합니다.
 */

// 미니 그래프(Sparkline) 컴포넌트
const Sparkline = ({ data, color }: { data: number[], color: string }) => {
    if (!data || data.length < 2) return <div className="h-8 flex items-center text-[8px] text-gray-300">Insufficient data</div>;

    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max === min ? 1 : max - min;
    const width = 100;
    const height = 30;

    const points = data.map((val, i) => {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((val - min) / range) * height;
        return `${x},${y}`;
    }).join(' ');

    return (
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-8 overflow-visible">
            <polyline
                fill="none"
                stroke={color}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={points}
                className="drop-shadow-sm transition-all duration-1000"
            />
        </svg>
    );
};

export function TrendSummary() {
    const [trendData, setTrendData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchTopTrends() {
            try {
                const repository = new FirebaseRankingRepository();

                // Fetch 1st items for each category
                const [beauty, media, food, place] = await Promise.all([
                    repository.getLatestRankings('all'),
                    repository.getMediaRankings(),
                    repository.getRestaurantRankings(),
                    repository.getPlaceRankings()
                ]);

                const categories = [
                    {
                        id: "beauty",
                        category: "Beauty",
                        item: beauty[0] as RankingItem,
                        color: "rgb(244, 63, 94)", // Rose-500
                        bgColor: "bg-rose-50",
                        textColor: "text-rose-600",
                        icon: <Sparkles className="w-5 h-5" />,
                        link: "/beauty",
                        pulse: [30, 45, 42, 50, 65, 60, 75]
                    },
                    {
                        id: "media",
                        category: "Media",
                        item: media[0] as MediaRankingItem,
                        color: "rgb(229, 9, 20)", // Netflix Red
                        bgColor: "bg-red-50",
                        textColor: "text-red-600",
                        icon: <Clapperboard className="w-5 h-5" />,
                        link: "/media",
                        pulse: [80, 82, 79, 81, 85, 84, 83]
                    },
                    {
                        id: "food",
                        category: "Food",
                        item: food[0] as RestaurantRankingItem,
                        color: "rgb(249, 115, 22)", // Orange-500
                        bgColor: "bg-orange-50",
                        textColor: "text-orange-600",
                        icon: <Utensils className="w-5 h-5" />,
                        link: "/food",
                        pulse: [40, 55, 70, 65, 80, 95, 100]
                    },
                    {
                        id: "place",
                        category: "Place",
                        item: place[0] as PlaceRankingItem,
                        color: "rgb(16, 185, 129)", // Emerald-500
                        bgColor: "bg-emerald-50",
                        textColor: "text-emerald-600",
                        icon: <MapPin className="w-5 h-5" />,
                        link: "/place",
                        pulse: [10, 20, 45, 60, 85, 90, 99]
                    }
                ];

                const mappedData = categories.map(cat => {
                    const item = cat.item;
                    if (!item) return null;

                    let title = "";
                    let stat = "";
                    let change = "Stable";
                    const trendVal = item.trend;

                    if (cat.id === "beauty") {
                        const i = item as RankingItem;
                        title = i.productName;
                        stat = `${i.price || "Trending"}`;
                    } else if (cat.id === "media") {
                        const i = item as MediaRankingItem;
                        title = i.titleEn;
                        stat = i.weeksInTop10 ? `${i.weeksInTop10} Weeks` : "Streaming";
                    } else if (cat.id === "food") {
                        const i = item as RestaurantRankingItem;
                        title = i.name;
                        stat = i.waitTime || `${i.hypeScore}% Hype`;
                    } else if (cat.id === "place") {
                        const i = item as PlaceRankingItem;
                        title = i.name_en;
                        stat = i.views ? `${i.views} Views` : "Hot Spot";
                    }

                    if (trendVal > 0) change = `+${trendVal}`;
                    else if (trendVal < 0) change = `${trendVal}`;

                    return {
                        ...cat,
                        title,
                        stat,
                        change
                    };
                }).filter(Boolean);

                setTrendData(mappedData);
            } catch (error) {
                console.error("Error fetching trend summary:", error);
            } finally {
                setLoading(false);
            }
        }

        fetchTopTrends();
    }, []);

    if (loading) {
        return (
            <div className="bg-[#F8FAFC] py-24 flex justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-brand-500 border-t-transparent"></div>
            </div>
        );
    }

    if (trendData.length === 0) return null;

    return (
        <section className="bg-[#F8FAFC] py-24 overflow-hidden border-t border-gray-100">
            <div className="max-w-6xl mx-auto px-6">
                <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-6">
                    <div className="relative">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gray-900 text-white text-[10px] font-black uppercase tracking-widest mb-4">
                            <Activity className="w-3 h-3 text-brand-400" /> K-Trend Live Pulse
                        </div>
                        <h2 className="text-5xl md:text-7xl font-black text-gray-900 tracking-tighter leading-none uppercase">
                            The Korea <br /> <span className="text-gray-300 font-serif italic drop-shadow-sm">Dynamics.</span>
                        </h2>
                    </div>
                    <p className="text-gray-500 font-medium max-w-[280px] text-sm border-l-4 border-brand-500 pl-6 py-2 leading-relaxed">
                        Real-time analytics showcasing the <span className="text-gray-900 font-bold">velocity of interest</span> across Korea's most influential sectors.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {trendData.map((item, index) => (
                        <div key={index} className="group relative bg-white rounded-[2.5rem] p-8 border border-gray-100 shadow-sm hover:shadow-2xl transition-all hover:-translate-y-2 overflow-hidden flex flex-col h-full">
                            <div className="flex justify-between items-start mb-8">
                                <div className={`${item.bgColor} ${item.textColor} p-3.5 rounded-2xl shadow-sm`}>
                                    {item.icon}
                                </div>
                                <div className="text-right">
                                    <span className="text-[10px] font-black text-gray-300 uppercase tracking-widest block mb-1">
                                        {item.id === "beauty" ? "Daily" : "Weekly"}
                                    </span>
                                    <span className={`text-[10px] font-black uppercase px-2.5 py-1 rounded-full border-2 ${item.textColor} border-current opacity-80 flex items-center gap-1`}>
                                        {item.change === "Stable" ? <Minus size={10} /> : item.change.startsWith('+') ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                                        {item.change}
                                    </span>
                                </div>
                            </div>

                            <div className="mb-6 flex-1 text-left">
                                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">{item.category} Insight</p>
                                <h3 className="text-xl font-black text-gray-900 leading-[1.1] mb-3 group-hover:text-brand-500 transition-colors line-clamp-2">
                                    {item.title}
                                </h3>
                                <div className="flex items-center gap-1.5 text-brand-500 font-black text-sm uppercase">
                                    {item.stat}
                                </div>
                            </div>

                            <div className="mb-8 p-4 bg-gray-50/50 rounded-2xl border border-gray-100/50">
                                <div className="flex justify-between items-end mb-2">
                                    <span className="text-[9px] font-black text-gray-400 uppercase tracking-tighter">
                                        {item.id === "beauty" ? "24-Hour Velocity" : "7-Day Velocity"}
                                    </span>
                                    <span className="text-[9px] font-bold text-gray-400 uppercase">Live</span>
                                </div>
                                <Sparkline data={item.pulse} color={item.color} />
                            </div>

                            <a href={item.link} className="flex items-center justify-between group/link pt-6 border-t border-gray-50">
                                <span className="text-[10px] font-black text-gray-900 uppercase tracking-widest">Go to Board</span>
                                <div className="bg-gray-900 text-white p-2 rounded-xl group-hover/link:bg-brand-500 transition-all shadow-lg shadow-gray-200">
                                    <ArrowRight className="w-4 h-4" />
                                </div>
                            </a>

                            <div className="absolute top-0 right-0 w-24 h-24 -mt-8 -mr-8 opacity-[0.02] bg-current rounded-full group-hover:scale-150 transition-transform duration-700"></div>
                        </div>
                    ))}
                </div>

                <div className="mt-20 flex flex-col md:flex-row items-center justify-center gap-6 opacity-40">
                    <div className="h-px bg-gray-300 w-12 hidden md:block"></div>
                    <p className="text-[10px] text-gray-500 font-bold uppercase tracking-[0.4em] text-center">
                        Verified Real-time Stream Analytics • South Korea Official
                    </p>
                    <div className="h-px bg-gray-300 w-12 hidden md:block"></div>
                </div>
            </div>
        </section>
    );
}
