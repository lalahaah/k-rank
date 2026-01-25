"use client";

import React from 'react';
import {
    Search,
    Bell,
    List,
    Map
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { RestaurantCard } from '@/components/restaurant-card';
import { MapView } from '@/components/map-view';
import type { RestaurantRankingItem } from '@/domain/entities/ranking';
import { FirebaseRankingRepository } from '@/infrastructure/repositories/firebase-ranking-repository';

const AREAS = ['All', 'Seongsu', 'Dosan', 'Hannam', 'Hongdae'];

export default function FoodPage() {
    const [activeArea, setActiveArea] = useState('All');
    const [searchQuery, setSearchQuery] = useState('');
    const [rankings, setRankings] = useState<RestaurantRankingItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [email, setEmail] = useState('');
    const [viewMode, setViewMode] = useState<'list' | 'map'>('list');

    // 데이터 fetch
    useEffect(() => {
        async function fetchData() {
            try {
                const repository = new FirebaseRankingRepository();
                const data = await repository.getRestaurantRankings();
                setRankings(data);
            } catch (error) {
                console.error('Error fetching restaurant rankings:', error);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, []);

    // 필터링된 레스토랑
    const filteredRankings = rankings.filter((item) => {
        // 지역 필터
        if (activeArea !== 'All' && !item.location.includes(activeArea)) {
            return false;
        }
        // 검색 필터
        if (searchQuery.trim()) {
            const query = searchQuery.toLowerCase();
            return (
                item.name.toLowerCase().includes(query) ||
                item.nameKo?.toLowerCase().includes(query) ||
                item.category.toLowerCase().includes(query) ||
                item.location.toLowerCase().includes(query) ||
                item.aiInsight?.tags.some(tag => tag.toLowerCase().includes(query))
            );
        }
        return true;
    });

    const handleWaitlistSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        alert(`Thanks for joining! We'll send updates to ${email}`);
        setEmail('');
    };

    return (
        <div className="min-h-screen bg-[#F5F7FA] font-sans text-gray-900">
            <Navbar />

            {/* Hero Content */}
            <section className="bg-white py-16 md:py-24 overflow-hidden relative">
                <div className="max-w-6xl mx-auto px-4 relative z-10">
                    <div className="max-w-2xl">
                        <div className="inline-flex items-center gap-2 bg-food-50 text-food-600 px-3 py-1 rounded-full text-xs font-black uppercase tracking-widest mb-6">
                            <span className="flex h-2 w-2 rounded-full bg-food-500 animate-pulse"></span>
                            Live Social Signal from Seoul
                        </div>
                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-gray-900 leading-[0.9] mb-6">
                            WHERE SEOUL <br />
                            <span className="text-food-500">EATS NOW.</span>
                        </h1>
                        <p className="text-lg text-gray-500 font-medium leading-relaxed">
                            Don't just eat, experience the hype. We analyze real-time queue data and social signals to find your next favorite table.
                        </p>
                    </div>
                </div>
            </section>

            {/* Navigation & Search Bar */}
            <div className="sticky top-16 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-100">
                <div className="max-w-6xl mx-auto px-4 h-20 flex items-center gap-4">
                    {/* View Toggle */}
                    <div className="flex gap-1 bg-gray-100 rounded-xl p-1 shrink-0">
                        <button
                            onClick={() => setViewMode('list')}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${viewMode === 'list'
                                ? 'bg-white text-food-600 shadow-sm'
                                : 'text-gray-400 hover:text-gray-600'
                                }`}
                        >
                            <List className="w-4 h-4" />
                            <span className="hidden sm:inline">List</span>
                        </button>
                        <button
                            onClick={() => setViewMode('map')}
                            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${viewMode === 'map'
                                ? 'bg-white text-food-600 shadow-sm'
                                : 'text-gray-400 hover:text-gray-600'
                                }`}
                        >
                            <Map className="w-4 h-4" />
                            <span className="hidden sm:inline">Map</span>
                        </button>
                    </div>

                    {/* Area Filters */}
                    <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-2">
                        {AREAS.map((area) => (
                            <button
                                key={area}
                                onClick={() => setActiveArea(area)}
                                className={`px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all whitespace-nowrap ${activeArea === area
                                    ? 'bg-food-500 text-white shadow-lg shadow-food-500/30'
                                    : 'text-gray-400 hover:text-gray-900'
                                    }`}
                            >
                                {area}
                            </button>
                        ))}
                    </div>

                    {/* Search Bar */}
                    <div className="flex-1 hidden md:flex relative max-w-sm ml-auto">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-300" />
                        <input
                            type="text"
                            placeholder="Search restaurants..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-gray-50 border-none rounded-2xl py-3 pl-12 pr-4 text-xs font-bold focus:ring-2 focus:ring-food-500/20"
                        />
                    </div>
                </div>
            </div >

            {/* Main Grid */}
            < main className="max-w-6xl mx-auto px-4 py-12" >
                {
                    loading ? (
                        <div className="text-center py-12" >
                            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-food-500 border-r-transparent"></div>
                            <p className="mt-4 text-gray-500">Loading restaurants...</p>
                        </div>
                    ) : filteredRankings.length === 0 ? (
                        <div className="text-center py-12">
                            <p className="text-gray-500 text-lg">
                                {searchQuery || activeArea !== 'All'
                                    ? 'No restaurants found. Try adjusting your filters.'
                                    : 'No restaurant data available yet.'}
                            </p>
                        </div>
                    ) : (
                        <>
                            {/* Map or List View */}
                            {viewMode === 'map' ? (
                                <MapView restaurants={filteredRankings} />
                            ) : (
                                <>
                                    <div className="grid grid-cols-1 gap-8">
                                        {filteredRankings.map((item) => (
                                            <RestaurantCard key={item.rank} item={item} />
                                        ))}
                                    </div>

                                    {/* Explore More */}
                                    {filteredRankings.length >= 10 && (
                                        <div className="mt-16 text-center">
                                            <button className="px-10 py-5 bg-white border-2 border-gray-100 rounded-2xl font-bold text-gray-900 hover:border-food-500 hover:text-food-500 transition-all shadow-sm">
                                                Load Top 50 Restaurants
                                            </button>
                                        </div>
                                    )}
                                </>
                            )}
                        </>
                    )
                }
            </main >

            {/* Gourmet Booking Essentials */}
            < section className="max-w-6xl mx-auto px-6 mb-20" >
                <div className="bg-gray-900 rounded-[3rem] p-10 md:p-16 relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-8">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-food-500 rounded-full blur-[120px] opacity-20 -translate-y-1/2 translate-x-1/2"></div>
                    <div className="relative z-10">
                        <h3 className="text-3xl md:text-5xl font-black text-white tracking-tighter mb-4">
                            HUNGRY FOR <br /> <span className="text-food-500">THE BEST?</span>
                        </h3>
                        <p className="text-gray-400 font-medium text-sm md:text-base">
                            Book your table at Korea's most hyped restaurants.
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-3 relative z-10">
                        <a
                            href="https://www.catchtable.net/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-food-500 hover:text-white transition-all shadow-xl"
                        >
                            CatchTable Global
                        </a>
                        <a
                            href="https://www.creatrip.com/en/blog/614"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-white text-gray-900 px-6 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-food-500 hover:text-white transition-all shadow-xl"
                        >
                            Dining Guide
                        </a>
                    </div>
                </div>
            </section >

            <Footer />
        </div >
    );
}
