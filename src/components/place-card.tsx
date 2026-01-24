import React, { useState } from 'react';
import {
    MapPin,
    Camera,
    Info,
    Calendar,
    Copy,
    TrendingUp,
    CheckCircle2,
    ExternalLink
} from 'lucide-react';
import type { PlaceRankingItem } from '@/domain/entities/ranking';
import Image from 'next/image';

interface PlaceCardProps {
    item: PlaceRankingItem;
}

export function PlaceCard({ item }: PlaceCardProps) {
    const [copied, setCopied] = useState(false);

    const handleCopyAddress = () => {
        const el = document.createElement('textarea');
        el.value = item.address;
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);

        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const getCategoryIcon = () => {
        switch (item.category) {
            case 'Culture':
                return '🏛️';
            case 'Nature':
                return '🏔️';
            case 'Modern':
                return '✨';
            default:
                return '📍';
        }
    };

    return (
        <div className="bg-white rounded-[2.5rem] border border-gray-100 overflow-hidden shadow-sm hover:shadow-xl transition-all group">
            <div className="flex flex-col lg:flex-row h-full">
                {/* Image Section */}
                <div className="relative w-full lg:w-2/5 h-72 lg:h-auto overflow-hidden">
                    <Image
                        src={item.imageUrl}
                        alt={item.name}
                        fill
                        className="object-cover transition-transform duration-700 group-hover:scale-110"
                        sizes="(max-width: 1024px) 100vw, 40vw"
                    />
                    <div className="absolute top-6 left-6 bg-black/80 backdrop-blur-md text-white px-5 py-2 rounded-2xl font-black text-xl shadow-lg">
                        #{item.rank}
                    </div>
                    <div className="absolute bottom-6 left-6 flex gap-2 flex-wrap">
                        {item.tags.map(tag => (
                            <span key={tag} className="bg-white/90 backdrop-blur-md text-gray-800 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight shadow-sm">
                                #{tag}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Content Section */}
                <div className="p-8 lg:p-10 flex-1 flex flex-col">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <div className="flex items-center gap-2 text-place-500 font-black text-[10px] uppercase tracking-widest mb-2">
                                <span>{getCategoryIcon()}</span>
                                {item.category}
                            </div>
                            <h3 className="text-3xl font-black text-gray-900 group-hover:text-place-500 transition-colors tracking-tighter">
                                {item.name}
                            </h3>
                            <p className="text-gray-400 font-medium text-sm mt-1">{item.nameKo} • {item.location}</p>
                        </div>
                        <div className="text-right">
                            <div className="bg-place-50 text-place-600 px-3 py-2 rounded-2xl flex items-center gap-2 border border-place-200">
                                <TrendingUp className="w-4 h-4" />
                                <div className="text-left">
                                    <p className="text-[10px] font-black uppercase leading-none mb-0.5">Local Rank</p>
                                    <p className="text-xs font-bold leading-none">{item.views} Views</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* AI Storyteller & Photo Spot */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                        <div className="bg-gray-50 border border-gray-100 p-5 rounded-3xl relative overflow-hidden group/box">
                            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover/box:opacity-20 transition-opacity">
                                <Info className="w-12 h-12" />
                            </div>
                            <h4 className="text-[10px] font-black text-place-600 uppercase tracking-widest mb-2">AI Cultural Guide</h4>
                            <p className="text-sm text-gray-600 leading-relaxed italic">&ldquo;{item.aiStory}&rdquo;</p>
                        </div>
                        <div className="bg-place-50 border border-place-100 p-5 rounded-3xl relative overflow-hidden group/box">
                            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover/box:opacity-20 transition-opacity">
                                <Camera className="w-12 h-12 text-place-600" />
                            </div>
                            <h4 className="text-[10px] font-black text-place-600 uppercase tracking-widest mb-2">Pro Photo Spot</h4>
                            <p className="text-sm text-gray-600 leading-relaxed font-medium italic">&ldquo;{item.photoSpot}&rdquo;</p>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-auto flex flex-col sm:flex-row gap-3">
                        <a
                            href={item.bookingUrl || 'https://www.klook.com/en-US/'}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 bg-gray-900 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 hover:bg-place-500 transition-all shadow-xl shadow-gray-200"
                        >
                            <Calendar className="w-4 h-4" /> Book a Tour
                        </a>
                        <button
                            onClick={handleCopyAddress}
                            className={`flex-1 py-4 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 border-2 transition-all ${copied
                                    ? 'bg-place-50 border-place-500 text-place-600'
                                    : 'bg-white border-gray-100 text-gray-400 hover:border-place-500 hover:text-place-500'
                                }`}
                        >
                            {copied ? <CheckCircle2 className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            {copied ? "Address Copied!" : "Address for Taxi"}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
