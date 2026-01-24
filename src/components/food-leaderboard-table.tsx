"use client";

import { TrendingUp, TrendingDown, Minus, ShoppingCart } from "lucide-react";
import Image from "next/image";
import { useState, useEffect } from "react";
import { FirebaseRankingRepository } from "@/infrastructure/repositories/firebase-ranking-repository";
import type { FoodRankingItem } from "@/domain/entities/ranking";

interface FoodLeaderboardTableProps {
    rankings: FoodRankingItem[];
}

const categories = [
    { id: "all", label: "All" },
    { id: "ramen", label: "Ramen" },
    { id: "snacks", label: "Snacks" },
    { id: "beverages", label: "Beverages" },
];

export function FoodLeaderboardTable({ rankings: initialRankings }: FoodLeaderboardTableProps) {
    const [rankings, setRankings] = useState<FoodRankingItem[]>(initialRankings);
    const [activeCategory, setActiveCategory] = useState("all");
    const [loading, setLoading] = useState(false);

    // 카테고리 필터링된 랭킹
    const filteredRankings = activeCategory === "all"
        ? rankings
        : rankings.filter(item => {
            const category = item.category.toLowerCase();
            if (activeCategory === "ramen") return category === "ramen";
            if (activeCategory === "snacks") return category === "snack";
            if (activeCategory === "beverages") return category === "beverage";
            return true;
        });

    // 랭크 재계산 (필터링 후)
    const displayRankings = filteredRankings.map((item, index) => ({
        ...item,
        displayRank: index + 1
    }));

    // Spicy Level 렌더링 (🌶️ 아이콘)
    const renderSpicyLevel = (level?: number) => {
        if (!level || level === 1) return null;

        return (
            <div className="flex items-center gap-1">
                {Array.from({ length: level }).map((_, i) => (
                    <span key={i} className="text-red-500">🌶️</span>
                ))}
            </div>
        );
    };

    // 트렌드 아이콘 렌더링
    const renderTrend = (trend: number) => {
        if (trend > 0) {
            return (
                <div className="flex items-center text-red-500 font-bold">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    <span>+{trend}</span>
                </div>
            );
        } else if (trend < 0) {
            return (
                <div className="flex items-center text-blue-500 font-bold">
                    <TrendingDown className="w-4 h-4 mr-1" />
                    <span>{trend}</span>
                </div>
            );
        } else {
            return (
                <div className="flex items-center text-gray-400">
                    <Minus className="w-4 h-4" />
                </div>
            );
        }
    };

    return (
        <div className="space-y-6">
            {/* 카테고리 필터 */}
            <div className="flex flex-wrap gap-2 justify-center">
                {categories.map((cat) => (
                    <button
                        key={cat.id}
                        onClick={() => setActiveCategory(cat.id)}
                        className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${activeCategory === cat.id
                                ? "bg-food-500 text-white shadow-md"
                                : "bg-white text-gray-700 hover:bg-gray-100 border border-gray-200"
                            }`}
                    >
                        {cat.label}
                    </button>
                ))}
            </div>

            {/* 로딩 상태 */}
            {loading ? (
                <div className="text-center py-12">
                    <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-food-500 border-r-transparent"></div>
                    <p className="mt-4 text-gray-500">Loading rankings...</p>
                </div>
            ) : displayRankings.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-gray-500">No products found in this category.</p>
                </div>
            ) : (
                <>
                    {/* Desktop Table */}
                    <div className="hidden md:block overflow-hidden rounded-lg border border-gray-200 bg-white">
                        <table className="w-full">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Rank
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Product
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Category
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Price
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Tags
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Trend
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Action
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {displayRankings.map((item) => (
                                    <tr key={item.rank} className="hover:bg-gray-50 transition-colors">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <span className={`text-2xl font-black ${item.displayRank === 1 ? "text-yellow-500" :
                                                        item.displayRank === 2 ? "text-gray-400" :
                                                            item.displayRank === 3 ? "text-amber-600" :
                                                                "text-gray-600"
                                                    }`}>
                                                    {item.displayRank}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-4">
                                                <div className="relative h-16 w-16 flex-shrink-0 rounded-md overflow-hidden bg-gray-100">
                                                    <Image
                                                        src={item.imageUrl}
                                                        alt={item.productName}
                                                        fill
                                                        className="object-cover"
                                                        sizes="64px"
                                                    />
                                                </div>
                                                <div>
                                                    <div className="font-semibold text-gray-900 mb-1">
                                                        {item.productName}
                                                    </div>
                                                    <div className="text-sm text-gray-500">
                                                        {item.brand}
                                                    </div>
                                                    {renderSpicyLevel(item.spicyLevel)}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="px-3 py-1 text-xs font-medium rounded-full bg-food-100 text-food-700">
                                                {item.category}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                                            {item.price}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-wrap gap-1">
                                                {item.isVegan && (
                                                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                                                        🌱 Vegan
                                                    </span>
                                                )}
                                                {item.tags.slice(0, 2).map((tag, idx) => (
                                                    <span
                                                        key={idx}
                                                        className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700"
                                                    >
                                                        {tag}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {renderTrend(item.trend)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right">
                                            {item.buyUrl && (
                                                <a
                                                    href={item.buyUrl}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center gap-2 px-4 py-2 bg-food-500 hover:bg-food-600 text-white text-sm font-medium rounded-md transition-colors"
                                                >
                                                    <ShoppingCart className="w-4 h-4" />
                                                    Buy
                                                </a>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Mobile Cards */}
                    <div className="md:hidden space-y-4">
                        {displayRankings.map((item) => (
                            <div
                                key={item.rank}
                                className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                            >
                                <div className="flex gap-4">
                                    {/* Rank Badge */}
                                    <div className="flex-shrink-0">
                                        <span className={`text-3xl font-black ${item.displayRank === 1 ? "text-yellow-500" :
                                                item.displayRank === 2 ? "text-gray-400" :
                                                    item.displayRank === 3 ? "text-amber-600" :
                                                        "text-gray-600"
                                            }`}>
                                            {item.displayRank}
                                        </span>
                                    </div>

                                    {/* Image */}
                                    <div className="relative h-20 w-20 flex-shrink-0 rounded-md overflow-hidden bg-gray-100">
                                        <Image
                                            src={item.imageUrl}
                                            alt={item.productName}
                                            fill
                                            className="object-cover"
                                            sizes="80px"
                                        />
                                    </div>

                                    {/* Content */}
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-semibold text-gray-900 mb-1 truncate">
                                            {item.productName}
                                        </h3>
                                        <p className="text-sm text-gray-500 mb-2">{item.brand}</p>

                                        <div className="flex items-center gap-2 mb-2">
                                            <span className="px-2 py-1 text-xs font-medium rounded-full bg-food-100 text-food-700">
                                                {item.category}
                                            </span>
                                            <span className="text-sm font-medium text-gray-900">
                                                {item.price}
                                            </span>
                                        </div>

                                        {renderSpicyLevel(item.spicyLevel)}

                                        {/* Tags */}
                                        <div className="flex flex-wrap gap-1 mt-2">
                                            {item.isVegan && (
                                                <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                                                    🌱 Vegan
                                                </span>
                                            )}
                                            {item.tags.slice(0, 2).map((tag, idx) => (
                                                <span
                                                    key={idx}
                                                    className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700"
                                                >
                                                    {tag}
                                                </span>
                                            ))}
                                        </div>

                                        {/* Trend & Buy Button */}
                                        <div className="flex items-center justify-between mt-3">
                                            <div>{renderTrend(item.trend)}</div>
                                            {item.buyUrl && (
                                                <a
                                                    href={item.buyUrl}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-food-500 hover:bg-food-600 text-white text-sm font-medium rounded-md transition-colors"
                                                >
                                                    <ShoppingCart className="w-4 h-4" />
                                                    Buy
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
