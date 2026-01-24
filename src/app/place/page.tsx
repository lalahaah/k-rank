"use client";

import React from 'react';
import {
    Search,
    TrendingUp,
    MapPin as MapIcon,
    ChevronRight
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { PlaceCard } from '@/components/place-card';
import type { PlaceRankingItem } from '@/domain/entities/ranking';
import { FirebaseRankingRepository } from '@/infrastructure/repositories/firebase-ranking-repository';

const CATEGORIES = ['All', 'Culture', 'Nature', 'Modern'];

export default function PlacePage() {
    const [activeTab, setActiveTab] = useState('All');
    const [searchQuery, setSearchQuery] = useState('');
    const [rankings, setRankings] = useState<PlaceRankingItem[]>([]);
    const [loading, setLoading] = useState(true);

    // 데이터 fetch
    useEffect(() => {
        async function fetchData() {
            try {
                const repository = new FirebaseRankingRepository();
                const data = await repository.getPlaceRankings();
                setRankings(data);
            } catch (error) {
                console.error('Error fetching place rankings:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    // 필터링된 여행지
    const filteredRankings = rankings.filter((item) => {
        // 카테고리 필터
        if (activeTab !== 'All' && item.category !== activeTab) {
            return false;
        }
        // 검색 필터
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            return (
                item.name.toLowerCase().includes(query) ||
                item.nameKo.toLowerCase().includes(query) ||
                item.location.toLowerCase().includes(query) ||
                item.tags.some(tag => tag.toLowerCase().includes(query))
            );
        }
        return true;
    });

    return (
        <div className="min-h-screen bg-[#F8FAFC] font-sans selection:bg-place-500 selection:text-white pb-20">
            <Navbar />

            {/* Header Section - Place Theme (Aligned with Food Style) */}
            <section className="bg-white py-16 md:py-24 overflow-hidden relative">
                <div className="max-w-6xl mx-auto px-4 relative z-10">
                    <div className="max-w-2xl">
                        <div className="inline-flex items-center gap-2 bg-place-50 text-place-500 px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest mb-6">
                            <span className="flex h-2 w-2 rounded-full bg-place-500 animate-pulse"></span>
                            Verified Data from VisitKorea
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black text-gray-900 tracking-tighter leading-[0.9] mb-6">
                            EXPLORE KOREA <br />
                            <span className="text-place-500">LIKE A LOCAL.</span>
                        </h1>
                        <p className="text-lg text-gray-500 font-medium leading-relaxed">
                            Stop visiting tourist traps. We use local visitation data to show you where Koreans actually spend their weekends.
                        </p>
                    </div>
                </div>
                <div className="absolute top-1/2 -right-20 -translate-y-1/2 text-[20rem] font-black text-gray-50 select-none -z-0">
                    PLACE
                </div>
            </section>

            {/* Navigation & Search */}
            <div className="sticky top-16 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
                <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-2">
                        {CATEGORIES.map(cat => (
                            <button
                                key={cat}
                                onClick={() => setActiveTab(cat)}
                                className={`px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all whitespace-nowrap ${activeTab === cat
                                    ? 'bg-place-500 text-white shadow-lg shadow-place-500/30'
                                    : 'text-gray-400 hover:text-gray-900'
                                    }`}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>
                    <div className="hidden md:flex relative w-64">
                        <input
                            type="text"
                            placeholder="Search destinations..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-gray-50 border-none rounded-2xl py-3 pl-10 pr-4 text-xs font-bold focus:ring-2 focus:ring-place-500/20"
                        />
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
                    </div>
                </div>
            </div>

            {/* Main Ranking Grid */}
            <main className="max-w-6xl mx-auto px-6 py-12">
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-2xl font-black text-gray-900 flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-place-500" /> Monthly Local Choice
                    </h2>
                    <div className="flex items-center gap-4 text-[10px] font-black text-gray-300 uppercase tracking-widest">
                        <span className="flex items-center gap-1"><MapIcon className="w-3 h-3" /> National</span>
                        <span>Updated Jan 24</span>
                    </div>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-place-500 border-r-transparent"></div>
                        <p className="mt-4 text-gray-500">Loading places...</p>
                    </div>
                ) : filteredRankings.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-gray-500 text-lg">
                            {searchQuery || activeTab !== 'All'
                                ? 'No places found. Try adjusting your filters.'
                                : 'No place data available yet. Coming soon!'}
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="space-y-4">
                            {filteredRankings.map(item => (
                                <PlaceCard key={item.rank} item={item} />
                            ))}
                        </div>

                        {/* Explore More CTA */}
                        {filteredRankings.length >= 10 && (
                            <div className="mt-12 text-center">
                                <button className="px-12 py-5 bg-white border-2 border-gray-100 rounded-3xl font-black text-xs uppercase tracking-[0.2em] text-gray-400 hover:border-place-500 hover:text-place-500 transition-all group">
                                    Explore 50+ More Places <ChevronRight className="inline-block w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                                </button>
                            </div>
                        )}
                    </>
                )}
            </main>

            {/* Travel Essentials Banner */}
            <section className="max-w-6xl mx-auto px-6 mb-20">
                <div className="bg-gray-900 rounded-[3rem] p-10 md:p-16 relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-place-500 rounded-full blur-[120px] opacity-20 -translate-y-1/2 translate-x-1/2"></div>
                    <div className="relative z-10">
                        <h3 className="text-3xl md:text-5xl font-black text-white tracking-tighter mb-4">
                            READY FOR <br /> <span className="text-place-500">THE JOURNEY?</span>
                        </h3>
                        <p className="text-gray-400 font-medium text-sm md:text-base">
                            Grab your eSIM, T-money, and Travel Passes at the best price.
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-3 relative z-10">
                        <a
                            href="https://www.klook.com/en-US/search?query=korea%20esim"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-place-500 hover:text-white transition-all"
                        >
                            Get eSIM
                        </a>
                        <a
                            href="https://www.klook.com/en-US/search?query=t-money"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-place-500 hover:text-white transition-all"
                        >
                            T-money Card
                        </a>
                        <a
                            href="https://www.klook.com/en-US/search?query=korea%20pass"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-place-500 text-white px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-white hover:text-gray-900 transition-all font-sans"
                        >
                            All Passes
                        </a>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <Footer />
        </div>
    );
}
