"use client";

import React from 'react';
import { GoogleMap, useLoadScript, MarkerF, InfoWindowF } from '@react-google-maps/api';
import type { RestaurantRankingItem } from '@/domain/entities/ranking';
import Image from 'next/image';
import { Star, MapPin, Loader2 } from 'lucide-react';
import Link from 'next/link';

interface MapViewProps {
    restaurants: RestaurantRankingItem[];
}

// 서울 중심 좌표
const CENTER = {
    lat: 37.5665,
    lng: 127.0020
};

const mapContainerStyle = {
    width: '100%',
    height: '600px'
};

const mapOptions = {
    disableDefaultUI: false,
    zoomControl: true,
    styles: [
        {
            featureType: "poi",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
        }
    ]
};

export function MapView({ restaurants }: MapViewProps) {
    const [selectedRestaurant, setSelectedRestaurant] = React.useState<RestaurantRankingItem | null>(null);
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

    const { isLoaded, loadError } = useLoadScript({
        googleMapsApiKey: apiKey || '',
    });

    // API 키가 없는 경우
    if (!apiKey) {
        return (
            <div className="bg-white rounded-3xl p-12 text-center shadow-lg border border-gray-100">
                <div className="max-w-2xl mx-auto">
                    <MapPin className="w-16 h-16 text-food-500 mx-auto mb-4" />
                    <h3 className="text-2xl font-black text-gray-900 mb-4">
                        Google Maps API Key Required
                    </h3>
                    <p className="text-gray-600 mb-6">
                        지도 기능을 사용하려면 Google Maps API 키가 필요합니다.
                    </p>

                    <div className="bg-gray-50 rounded-xl p-6 text-left space-y-4">
                        <h4 className="font-bold text-gray-900">설정 방법:</h4>
                        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-700">
                            <li>
                                <a
                                    href="https://console.cloud.google.com/google/maps-apis"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-food-500 hover:underline"
                                >
                                    Google Cloud Console
                                </a>에서 Maps JavaScript API 활성화
                            </li>
                            <li>API 키 생성</li>
                            <li>프로젝트 루트에 <code className="bg-gray-200 px-2 py-1 rounded">.env.local</code> 파일 생성</li>
                            <li>
                                다음 내용 추가:<br />
                                <code className="bg-gray-200 px-2 py-1 rounded block mt-2">
                                    NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_api_key_here
                                </code>
                            </li>
                            <li>개발 서버 재시작</li>
                        </ol>
                    </div>

                    {/* 레스토랑 리스트 미리보기 */}
                    <div className="mt-8">
                        <h4 className="font-bold text-gray-900 mb-4">레스토랑 위치 (리스트)</h4>
                        <div className="grid gap-3">
                            {restaurants.slice(0, 5).map((restaurant) => (
                                <Link
                                    key={restaurant.rank}
                                    href={`/food/${restaurant.rank}`}
                                    className="flex items-center gap-4 bg-gray-50 rounded-xl p-4 hover:bg-food-50 transition-colors"
                                >
                                    <div className="w-16 h-16 relative rounded-lg overflow-hidden flex-shrink-0">
                                        <Image
                                            src={restaurant.imageUrl}
                                            alt={restaurant.name}
                                            fill
                                            className="object-cover"
                                            sizes="64px"
                                        />
                                    </div>
                                    <div className="flex-1 text-left">
                                        <h5 className="font-bold text-gray-900">{restaurant.name}</h5>
                                        <p className="text-sm text-gray-500 flex items-center gap-1">
                                            <MapPin className="w-3 h-3" />
                                            {restaurant.location}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs text-gray-400">Hype Score</div>
                                        <div className="font-black text-food-600">{restaurant.hypeScore}%</div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (loadError) {
        return (
            <div className="bg-white rounded-3xl p-12 text-center shadow-lg border border-gray-100">
                <p className="text-red-500">Error loading Google Maps</p>
            </div>
        );
    }

    if (!isLoaded) {
        return (
            <div className="bg-white rounded-3xl p-12 flex items-center justify-center shadow-lg border border-gray-100">
                <Loader2 className="w-8 h-8 text-food-500 animate-spin" />
                <span className="ml-3 text-gray-600">Loading map...</span>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-3xl overflow-hidden shadow-lg border border-gray-100">
            <GoogleMap
                mapContainerStyle={mapContainerStyle}
                center={CENTER}
                zoom={12}
                options={mapOptions}
            >
                {restaurants.map((restaurant) => {
                    // 실제 위도/경도 사용 (스크래퍼에서 저장한 값)
                    const position = {
                        lat: restaurant.latitude || CENTER.lat,
                        lng: restaurant.longitude || CENTER.lng
                    };

                    // Custom SVG marker with rank number
                    const markerIcon = {
                        url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg width="40" height="50" viewBox="0 0 40 50" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20 0C10.611 0 3 7.611 3 17c0 12.5 17 33 17 33s17-20.5 17-33c0-9.389-7.611-17-17-17z" fill="#F97316"/>
                      <circle cx="20" cy="17" r="8" fill="white"/>
                      <text x="20" y="22" font-family="Arial Black" font-size="12" font-weight="bold" fill="#F97316" text-anchor="middle">${restaurant.rank}</text>
                    </svg>
                  `),
                        scaledSize: new window.google.maps.Size(40, 50),
                        anchor: new window.google.maps.Point(20, 50)
                    };

                    return (
                        <MarkerF
                            key={restaurant.rank}
                            position={position}
                            onClick={() => setSelectedRestaurant(restaurant)}
                            icon={markerIcon}
                        />
                    );
                })}

                {selectedRestaurant && (
                    <InfoWindowF
                        position={{
                            lat: selectedRestaurant.latitude || CENTER.lat,
                            lng: selectedRestaurant.longitude || CENTER.lng
                        }}
                        onCloseClick={() => setSelectedRestaurant(null)}
                    >
                        <Link href={`/food/${selectedRestaurant.rank}`} className="block w-80">
                            <div className="p-2">
                                <div className="relative w-full h-40 mb-3 rounded-lg overflow-hidden">
                                    <Image
                                        src={selectedRestaurant.imageUrl}
                                        alt={selectedRestaurant.name}
                                        fill
                                        className="object-cover"
                                        sizes="320px"
                                    />
                                    <div className="absolute top-2 left-2 bg-black text-white px-3 py-1 rounded-lg font-black">
                                        #{selectedRestaurant.rank}
                                    </div>
                                </div>

                                <span className="text-food-500 font-bold text-xs uppercase">
                                    {selectedRestaurant.category}
                                </span>
                                <h3 className="text-lg font-black text-gray-900 mt-1">
                                    {selectedRestaurant.name}
                                </h3>
                                {selectedRestaurant.nameKo && (
                                    <p className="text-sm text-gray-600">{selectedRestaurant.nameKo}</p>
                                )}

                                <div className="flex items-center gap-3 mt-3">
                                    <div className="flex items-center gap-1">
                                        <MapPin className="w-3 h-3 text-gray-400" />
                                        <span className="text-xs text-gray-600">{selectedRestaurant.location}</span>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <Star className="w-3 h-3 text-food-500 fill-current" />
                                        <span className="text-xs text-gray-900 font-bold">{selectedRestaurant.hypeScore}%</span>
                                    </div>
                                </div>

                                <div className="mt-3 text-xs text-food-500 font-bold hover:underline">
                                    View Details →
                                </div>
                            </div>
                        </Link>
                    </InfoWindowF>
                )}
            </GoogleMap>
        </div>
    );
}
