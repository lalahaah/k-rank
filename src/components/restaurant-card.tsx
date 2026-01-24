import React from 'react';
import { Clock, MapPin, Star, Calendar, Navigation, Info, Flame } from 'lucide-react';
import type { RestaurantRankingItem } from '@/domain/entities/ranking';
import Image from 'next/image';
import Link from 'next/link';

interface RestaurantCardProps {
    item: RestaurantRankingItem;
}

export function RestaurantCard({ item }: RestaurantCardProps) {
    return (
        <Link href={`/food/${item.rank}`} className="block">
            <div className="bg-white rounded-3xl overflow-hidden border border-gray-100 shadow-sm hover:shadow-xl transition-all group flex flex-col md:flex-row h-full cursor-pointer">
                {/* 이미지 섹션 */}
                <div className="relative w-full md:w-2/5 h-64 md:h-auto overflow-hidden">
                    <Image
                        src={item.imageUrl}
                        alt={item.name}
                        fill
                        className="object-cover transition-transform duration-700 group-hover:scale-110"
                        sizes="(max-width: 768px) 100vw, 40vw"
                    />
                    <div className="absolute top-4 left-4 bg-black text-white px-4 py-2 rounded-xl font-black text-xl shadow-lg">
                        #{item.rank}
                    </div>
                    {item.rank === 1 && (
                        <div className="absolute top-4 right-4 bg-food-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-lg">
                            <Flame className="w-3 h-3 fill-current" /> TRENDING #1
                        </div>
                    )}
                </div>

                {/* 정보 섹션 */}
                <div className="p-6 md:p-8 flex-1 flex flex-col">
                    <div className="flex justify-between items-start mb-2">
                        <div>
                            <span className="text-food-500 font-bold text-xs uppercase tracking-widest">
                                {item.category}
                            </span>
                            <h3 className="text-2xl md:text-3xl font-black text-gray-900 mt-1 group-hover:text-food-600 transition-colors">
                                {item.name}
                            </h3>
                            {item.nameKo && (
                                <p className="text-sm text-gray-500 font-medium mt-1">{item.nameKo}</p>
                            )}
                        </div>
                        <div className="flex flex-col items-end">
                            <div className="flex items-center gap-1 text-gray-400 text-xs font-medium">
                                <MapPin className="w-3 h-3" /> {item.location}
                            </div>
                        </div>
                    </div>

                    {/* 핵심 수치 (Social Signals) */}
                    <div className="flex items-center gap-4 my-4 flex-wrap">
                        <div className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded-xl border border-gray-100">
                            <Star className="w-4 h-4 text-food-500 fill-current" />
                            <div>
                                <p className="text-[10px] text-gray-400 font-bold uppercase leading-none">
                                    Hype Score
                                </p>
                                <p className="text-sm font-black text-gray-800">{item.hypeScore}%</p>
                            </div>
                        </div>
                        <div
                            className={`ml-auto px-3 py-1 rounded-full text-[10px] font-bold uppercase border ${item.status === 'Available'
                                ? 'bg-green-50 text-green-600 border-green-100'
                                : 'bg-red-50 text-red-600 border-red-100'
                                }`}
                        >
                            {item.status}
                        </div>
                    </div>

                    {/* AI Insight Box */}
                    {item.aiInsight && (
                        <div className="bg-food-50/50 rounded-2xl p-4 border border-food-100 mb-6 flex gap-3">
                            <div className="bg-white p-1.5 rounded-lg h-fit shadow-sm">
                                <Info className="w-4 h-4 text-food-500" />
                            </div>
                            <div className="flex-1">
                                <span className="font-bold text-food-600 block mb-0.5 text-xs">
                                    AI Insight
                                </span>
                                <p className="text-sm text-gray-700 leading-relaxed italic">
                                    "{item.aiInsight.summary}"
                                </p>
                                {item.aiInsight.tips && (
                                    <p className="text-xs text-gray-600 mt-2 font-medium">
                                        💡 {item.aiInsight.tips}
                                    </p>
                                )}
                                {item.aiInsight.tags && item.aiInsight.tags.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-3">
                                        {item.aiInsight.tags.map((tag, idx) => (
                                            <span
                                                key={idx}
                                                className="px-2 py-1 bg-white text-food-600 rounded-full text-[10px] font-bold border border-food-100"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* 액션 버튼 */}
                    <div className="mt-auto flex gap-3">
                        <button
                            className="flex-1 bg-gray-900 text-white py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 hover:bg-food-600 transition-colors shadow-lg shadow-gray-200"
                            onClick={(e) => {
                                e.preventDefault();
                                if (item.links?.reservation) {
                                    window.open(item.links.reservation, '_blank');
                                }
                            }}
                        >
                            <Calendar className="w-4 h-4" /> Reserve via CatchTable
                        </button>
                        <button
                            className="w-14 bg-white border border-gray-200 text-gray-400 py-3.5 rounded-xl flex items-center justify-center hover:text-food-500 hover:border-food-500 transition-all"
                            onClick={(e) => {
                                e.preventDefault();
                                if (item.links?.map) {
                                    window.open(item.links.map, '_blank');
                                }
                            }}
                        >
                            <Navigation className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </Link>
    );
}
