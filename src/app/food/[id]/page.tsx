"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import {
    ArrowLeft,
    MapPin,
    Clock,
    Star,
    Phone,
    Calendar,
    Navigation,
    Share2,
    Heart,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import type { RestaurantRankingItem } from '@/domain/entities/ranking';
import { FirebaseRankingRepository } from '@/infrastructure/repositories/firebase-ranking-repository';

export default function RestaurantDetailPage() {
    const params = useParams();
    const router = useRouter();
    const [restaurant, setRestaurant] = useState<RestaurantRankingItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    useEffect(() => {
        async function fetchRestaurant() {
            try {
                const repository = new FirebaseRankingRepository();
                const restaurants = await repository.getRestaurantRankings();

                // ID는 rank를 기준으로 함
                const id = parseInt(params.id as string);
                const found = restaurants.find(r => r.rank === id);

                if (found) {
                    setRestaurant(found);
                }
            } catch (error) {
                console.error('Error fetching restaurant:', error);
            } finally {
                setLoading(false);
            }
        }

        fetchRestaurant();
    }, [params.id]);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#F5F7FA]">
                <Navbar />
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-food-500 border-r-transparent"></div>
                </div>
            </div>
        );
    }

    if (!restaurant) {
        return (
            <div className="min-h-screen bg-[#F5F7FA]">
                <Navbar />
                <div className="max-w-4xl mx-auto px-4 py-20 text-center">
                    <h1 className="text-3xl font-black text-gray-900 mb-4">Restaurant Not Found</h1>
                    <p className="text-gray-500 mb-8">The restaurant you're looking for doesn't exist.</p>
                    <button
                        onClick={() => router.push('/food')}
                        className="px-6 py-3 bg-food-500 text-white rounded-xl font-bold hover:bg-food-600 transition-colors"
                    >
                        Back to All Restaurants
                    </button>
                </div>
            </div>
        );
    }

    const allImages = [restaurant.imageUrl, ...(restaurant.images || [])];

    const nextImage = () => {
        setCurrentImageIndex((prev) => (prev + 1) % allImages.length);
    };

    const prevImage = () => {
        setCurrentImageIndex((prev) => (prev - 1 + allImages.length) % allImages.length);
    };

    return (
        <div className="min-h-screen bg-[#F5F7FA]">
            <Navbar />

            {/* Back Button */}
            <div className="max-w-6xl mx-auto px-4 pt-6">
                <button
                    onClick={() => router.push('/food')}
                    className="flex items-center gap-2 text-gray-600 hover:text-food-500 transition-colors font-medium"
                >
                    <ArrowLeft className="w-5 h-5" />
                    Back to All Restaurants
                </button>
            </div>

            {/* Hero Section with Image Gallery */}
            <div className="max-w-6xl mx-auto px-4 py-8">
                <div className="bg-white rounded-3xl overflow-hidden shadow-xl">
                    {/* Image Gallery */}
                    <div className="relative h-96 md:h-[500px] bg-gray-100">
                        <Image
                            src={allImages[currentImageIndex]}
                            alt={restaurant.name}
                            fill
                            className="object-cover"
                            sizes="(max-width: 1200px) 100vw, 1200px"
                            priority
                        />

                        {/* Gallery Controls */}
                        {allImages.length > 1 && (
                            <>
                                <button
                                    onClick={prevImage}
                                    className="absolute left-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white p-2 rounded-full shadow-lg transition-all"
                                >
                                    <ChevronLeft className="w-6 h-6 text-gray-800" />
                                </button>
                                <button
                                    onClick={nextImage}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white p-2 rounded-full shadow-lg transition-all"
                                >
                                    <ChevronRight className="w-6 h-6 text-gray-800" />
                                </button>

                                {/* Image Indicators */}
                                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                                    {allImages.map((_, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setCurrentImageIndex(idx)}
                                            className={`w-2 h-2 rounded-full transition-all ${idx === currentImageIndex ? 'bg-white w-8' : 'bg-white/50'
                                                }`}
                                        />
                                    ))}
                                </div>
                            </>
                        )}

                        {/* Rank Badge */}
                        <div className="absolute top-4 left-4 bg-black text-white px-4 py-2 rounded-xl font-black text-xl shadow-lg">
                            #{restaurant.rank}
                        </div>
                    </div>

                    {/* Restaurant Info */}
                    <div className="p-8 md:p-12">
                        {/* Header */}
                        <div className="mb-8">
                            <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                                <div>
                                    <span className="text-food-500 font-bold text-sm uppercase tracking-widest">
                                        {restaurant.category}
                                    </span>
                                    <h1 className="text-4xl md:text-5xl font-black text-gray-900 mt-2">
                                        {restaurant.name}
                                    </h1>
                                    {restaurant.nameKo && (
                                        <p className="text-xl text-gray-600 font-medium mt-2">{restaurant.nameKo}</p>
                                    )}
                                </div>

                                {/* Action Buttons */}
                                <div className="flex gap-2">
                                    <button className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors">
                                        <Share2 className="w-5 h-5 text-gray-600" />
                                    </button>
                                    <button className="p-3 bg-gray-100 hover:bg-food-50 rounded-full transition-colors">
                                        <Heart className="w-5 h-5 text-gray-600 hover:text-food-500" />
                                    </button>
                                </div>
                            </div>

                            {/* Quick Stats */}
                            <div className="flex flex-wrap gap-6">
                                <div className="flex items-center gap-2">
                                    <MapPin className="w-5 h-5 text-food-500" />
                                    <span className="text-gray-700 font-medium">{restaurant.location}</span>
                                </div>
                                {restaurant.waitTime && (
                                    <div className="flex items-center gap-2">
                                        <Clock className="w-5 h-5 text-food-500" />
                                        <span className="text-gray-700 font-medium">Wait: {restaurant.waitTime}</span>
                                    </div>
                                )}
                                <div className="flex items-center gap-2">
                                    <Star className="w-5 h-5 text-food-500 fill-current" />
                                    <span className="text-gray-700 font-medium">Hype Score: {restaurant.hypeScore}%</span>
                                </div>
                            </div>

                            {/* Status Badge */}
                            <div className="mt-4">
                                <span
                                    className={`inline-block px-4 py-2 rounded-full text-sm font-bold ${restaurant.status === 'Available'
                                            ? 'bg-green-50 text-green-600'
                                            : 'bg-red-50 text-red-600'
                                        }`}
                                >
                                    {restaurant.status}
                                </span>
                            </div>
                        </div>

                        {/* AI Insight */}
                        {restaurant.aiInsight && (
                            <div className="bg-food-50 rounded-2xl p-6 mb-8 border border-food-100">
                                <h3 className="text-food-600 font-black text-sm uppercase tracking-widest mb-3">
                                    ✨ AI Insight
                                </h3>
                                <p className="text-gray-800 text-lg leading-relaxed italic mb-4">
                                    "{restaurant.aiInsight.summary}"
                                </p>
                                {restaurant.aiInsight.tips && (
                                    <p className="text-gray-700 font-medium">
                                        <span className="text-food-600">💡 </span>
                                        {restaurant.aiInsight.tips}
                                    </p>
                                )}
                                {restaurant.aiInsight.tags && restaurant.aiInsight.tags.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-4">
                                        {restaurant.aiInsight.tags.map((tag, idx) => (
                                            <span
                                                key={idx}
                                                className="px-3 py-1 bg-white text-food-600 rounded-full text-sm font-bold border border-food-200"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Details Section */}
                        {restaurant.details && (
                            <div className="grid md:grid-cols-2 gap-6 mb-8">
                                {restaurant.details.address && (
                                    <div className="bg-gray-50 rounded-xl p-4">
                                        <h4 className="font-bold text-gray-900 mb-2">Address</h4>
                                        <p className="text-gray-700">{restaurant.details.address}</p>
                                    </div>
                                )}
                                {restaurant.details.phone && (
                                    <div className="bg-gray-50 rounded-xl p-4">
                                        <h4 className="font-bold text-gray-900 mb-2">Phone</h4>
                                        <p className="text-gray-700">{restaurant.details.phone}</p>
                                    </div>
                                )}
                                {restaurant.details.hours && (
                                    <div className="bg-gray-50 rounded-xl p-4">
                                        <h4 className="font-bold text-gray-900 mb-2">Hours</h4>
                                        <p className="text-gray-700">{restaurant.details.hours}</p>
                                    </div>
                                )}
                                {restaurant.details.priceRange && (
                                    <div className="bg-gray-50 rounded-xl p-4">
                                        <h4 className="font-bold text-gray-900 mb-2">Price Range</h4>
                                        <p className="text-gray-700 text-2xl">{restaurant.details.priceRange}</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Must Try Section */}
                        {restaurant.details?.mustTry && restaurant.details.mustTry.length > 0 && (
                            <div className="mb-8">
                                <h3 className="text-2xl font-black text-gray-900 mb-4">Must Try</h3>
                                <div className="flex flex-wrap gap-3">
                                    {restaurant.details.mustTry.map((item, idx) => (
                                        <div
                                            key={idx}
                                            className="px-4 py-2 bg-gradient-to-r from-food-500 to-food-600 text-white rounded-full font-bold text-sm shadow-md"
                                        >
                                            {item}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* CTA Buttons */}
                        <div className="flex flex-col sm:flex-row gap-4">
                            <button
                                onClick={() => {
                                    if (restaurant.links?.reservation) {
                                        window.open(restaurant.links.reservation, '_blank');
                                    }
                                }}
                                className="flex-1 bg-gray-900 text-white py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 hover:bg-food-600 transition-colors shadow-lg"
                            >
                                <Calendar className="w-5 h-5" />
                                Reserve via CatchTable
                            </button>
                            <button
                                onClick={() => {
                                    if (restaurant.links?.map) {
                                        window.open(restaurant.links.map, '_blank');
                                    }
                                }}
                                className="sm:w-auto px-8 bg-white border-2 border-gray-200 text-gray-700 py-4 rounded-xl font-bold flex items-center justify-center gap-2 hover:border-food-500 hover:text-food-500 transition-all"
                            >
                                <Navigation className="w-5 h-5" />
                                Get Directions
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <Footer />
        </div>
    );
}
