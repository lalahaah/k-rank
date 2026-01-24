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
                <div className="absolute top-1/2 -right-20 -translate-y-1/2 text-[20rem] font-black text-gray-50 select-none -z-0">
                    FOOD
                </div>
            </section>

            {/* Filters & Control Bar */}
            <div className="max-w-6xl mx-auto px-4 -mt-8 relative z-20">
                <div className="bg-white rounded-2xl shadow-xl shadow-food-500/5 p-2 flex flex-wrap gap-2 border border-gray-100">
                    {/* View Toggle */}
                    <div className="flex gap-1 bg-gray-100 rounded-xl p-1 mr-2">
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
                    {AREAS.map((area) => (
                        <button
                            key={area}
                            onClick={() => setActiveArea(area)}
                            className={`px-6 py-3 rounded-xl text-sm font-bold transition-all ${activeArea === area
                                    ? 'bg-food-500 text-white shadow-lg shadow-food-500/30'
                                    : 'text-gray-400 hover:bg-gray-50'
                                }`}
                        >
                            {area}
                        </button>
                    ))}
                    <div className="ml-auto hidden md:flex items-center gap-4 px-4 text-[10px] font-black text-gray-300 uppercase tracking-widest">
                        Last Updated: Just Now
                    </div>
                </div>

                {/* Search Bar */}
                <div className="mt-4 relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search restaurants, locations, or tags..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-12 pr-4 py-4 rounded-2xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-food-500 focus:border-transparent font-medium text-gray-900 placeholder-gray-400"
                    />
                </div>
            </div>

            {/* Main Grid */}
            <main className="max-w-6xl mx-auto px-4 py-12">
                {loading ? (
                    <div className="text-center py-12">
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
                )}
            </main>

            {/* Waitlist Section (PRD 5.3) */}
            <section className="bg-food-500 py-20 relative overflow-hidden">
                <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
                    <Bell className="w-12 h-12 text-white/50 mx-auto mb-6" />
                    <h2 className="text-3xl md:text-5xl font-black text-white tracking-tighter mb-4">
                        GET EARLY ACCESS TO <br /> NEW HOTSPOTS.
                    </h2>
                    <p className="text-orange-100 mb-10 max-w-lg mx-auto font-medium">
                        Be the first to know when a new restaurant hits the Top 10. Subscribe to our Weekly Seoul Pulse.
                    </p>
                    <form
                        onSubmit={handleWaitlistSubmit}
                        className="flex flex-col md:flex-row gap-3 max-w-md mx-auto"
                    >
                        <input
                            type="email"
                            placeholder="Your Email Address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="flex-1 px-6 py-4 rounded-2xl bg-white focus:outline-none font-bold text-gray-900"
                        />
                        <button
                            type="submit"
                            className="bg-gray-900 text-white px-8 py-4 rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-black transition-colors"
                        >
                            Join Waitlist
                        </button>
                    </form>
                </div>
            </section>

            <Footer />
        </div>
    );
}
