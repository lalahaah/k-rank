"use client";

import React from 'react';
import {
    ExternalLink,
    Sparkles,
    Gift,
    Bell,
    ShoppingBag,
    X,
    Plane,
    ArrowRight as ArrowRightIcon
} from 'lucide-react';

/**
 * 📢 광고 설정 (AD_CONFIG)
 * 여기서 내용만 수정하시면 사이트의 광고 내용이 바로 바뀝니다!
 */
export const AD_CONFIG = {
    // 1번: 상단 빌보드 광고 설정
    billboard: {
        badge: "Exclusive Deal",
        text: "Get up to 20% off on Korean sunscreens at Amazon today!",
        linkText: "Shop Now",
        linkUrl: "https://www.amazon.com/s?k=korean+sunscreen&tag=nextidealab-20", // 대표님의 아마존 태그 포함 링크
    },
    // 2번: 리스트 중간 광고 (인피드)
    inFeed: {
        badge: "Sponsored Insight",
        title: "Still haven't found your Holy Grail?",
        description: "Check out the 'All-Time Best Sellers' chosen by 10 million global K-Beauty fans on YesStyle.",
        linkText: "Explore YesStyle Best Sellers",
        buttonText: "Shop Top Selection",
        linkUrl: "https://www.yesstyle.com/en/home.html?rco=NOWINKOREA", // 예스스타일 제휴 링크
    },
    // 3번: 사이드바 광고 설정
    sidebar: {
        badge: "BEST SELLER",
        title: "medicube Toner Pads Zero Pore Pad",
        description: "The viral sensation with over 20k+ reviews on Amazon. Get yours today at the best price.",
        buttonText: "Check Amazon Price",
        linkUrl: "https://www.amazon.com/Medicube-Zero-Pore-Pads-Dual-Textured/dp/B09V7Z4TJG?ref_=ast_sto_dp&th=1?tag=nextidealab-20",
        image: "https://m.media-amazon.com/images/I/618ang-TWOL._AC_SL1500_.jpg" // 나중에 이미지 주소가 생기면 여기에 넣으세요.
    }
};

/**
 * 🗺️ K-Place 전용 광고 설정
 */
export const PLACE_AD_CONFIG = {
    billboard: {
        badge: "Travel Essential",
        text: "Don't get lost! Get your unlimited 5G eSIM & T-Money card at 15% off.",
        linkUrl: "https://www.klook.com/en-US/search?query=korea+esim",
    },
    inFeed: {
        title: "Planning a trip beyond Seoul?",
        description: "Discover the hidden gems of Jeju Island and Gyeongju with our verified local guides.",
        buttonText: "Explore Day Tours",
        linkUrl: "https://www.klook.com/en-US/search?query=jeju+tour",
    }
};

// 1. Top Billboard Ad (헤더 하단 배치용)
export const BillboardAd = () => {
    const { billboard: data } = AD_CONFIG;
    return (
        <div className="w-full bg-orange-50 border-y border-orange-100 py-3 px-4 mb-6">
            <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                    <div className="bg-orange-500 text-white p-1.5 rounded-lg shadow-sm">
                        <Gift size={16} />
                    </div>
                    <p className="text-sm font-medium text-orange-900">
                        <span className="font-bold">{data.badge}:</span> {data.text}
                    </p>
                </div>
                <a
                    href={data.linkUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-xs font-black text-orange-600 uppercase tracking-widest hover:underline decoration-2 underline-offset-4"
                >
                    {data.linkText} <ExternalLink size={14} />
                </a>
            </div>
        </div>
    );
};

// 2. In-Feed Native Ad (리스트 중간 삽입용)
export const InFeedAd = () => {
    const { inFeed: data } = AD_CONFIG;
    return (
        <div className="my-6 p-1 bg-gradient-to-r from-orange-500 via-amber-400 to-orange-600 rounded-2xl shadow-lg">
            <div className="bg-white rounded-xl p-6 md:p-8 flex flex-col md:flex-row items-center gap-6">
                <div className="flex-1 text-center md:text-left">
                    <div className="inline-flex items-center gap-2 px-2 py-1 bg-orange-50 text-orange-600 text-[10px] font-black uppercase tracking-wider rounded border border-orange-100 mb-3">
                        <Sparkles size={10} /> {data.badge}
                    </div>
                    <h3 className="text-xl md:text-2xl font-black text-gray-900 mb-2 leading-tight">
                        {data.title.split(' ').map((word, i) =>
                            word === 'Holy' || word === 'Grail?' ? <span key={i} className="text-orange-500 italic"> {word}</span> : ` ${word}`
                        )}
                    </h3>
                    <p className="text-sm text-gray-500 font-medium mb-4 max-w-md">
                        {data.description}
                    </p>
                    <div className="flex flex-wrap justify-center md:justify-start gap-4">
                        <a href={data.linkUrl} target="_blank" rel="noopener noreferrer" className="text-xs font-bold text-gray-900 border-b-2 border-orange-500 pb-1 hover:text-orange-500 transition-colors">
                            {data.linkText}
                        </a>
                    </div>
                </div>

                <div className="flex-shrink-0 w-full md:w-auto">
                    <a href={data.linkUrl} target="_blank" rel="noopener noreferrer">
                        <button className="w-full md:w-auto bg-gray-900 hover:bg-orange-600 text-white px-8 py-4 rounded-xl font-black text-xs uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-xl shadow-gray-200">
                            {data.buttonText} <ArrowRightIcon size={14} />
                        </button>
                    </a>
                </div>
            </div>
        </div>
    );
};

// 3. Sidebar / Sticky Ad (상세 페이지 사이드바용)
export const SidebarAd = () => {
    const { sidebar: data } = AD_CONFIG;
    return (
        <div className="bg-white border border-gray-100 rounded-2xl p-6 sticky top-24 shadow-sm">
            <div className="flex items-center justify-between mb-4">
                <span className="text-[10px] font-bold text-gray-300 uppercase tracking-widest tracking-tighter">Sponsored</span>
                <button className="text-gray-300 hover:text-gray-500 transition-colors text-xs font-medium">
                    <X size={14} />
                </button>
            </div>

            <div className="aspect-square bg-gray-100 rounded-xl mb-4 overflow-hidden relative group">
                <div className="absolute inset-0 flex items-center justify-center text-gray-300 group-hover:scale-110 transition-transform duration-500">
                    {data.image ? (
                        <img src={data.image} alt={data.title} className="w-full h-full object-cover" />
                    ) : (
                        <ShoppingBag size={48} />
                    )}
                </div>
                <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur px-2 py-1 rounded text-[10px] font-black text-gray-800 border border-gray-100">
                    {data.badge}
                </div>
            </div>

            <h4 className="font-bold text-gray-900 mb-2 leading-snug">
                {data.title}
            </h4>
            <p className="text-xs text-gray-500 mb-6 leading-relaxed">
                {data.description}
            </p>

            <a href={data.linkUrl} target="_blank" rel="noopener noreferrer" className="block w-full bg-orange-500 text-white text-center py-3 rounded-xl font-bold text-xs uppercase tracking-widest hover:bg-orange-600 transition-colors">
                {data.buttonText}
            </a>
        </div>
    );
};

// 4. Newsletter Footer Ad (푸터 직전 배치용)
export const FooterAd = () => {
    return (
        <div className="max-w-6xl mx-auto px-4 mb-20">
            <div className="bg-gray-900 rounded-[2.5rem] py-16 px-8 text-center relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-orange-500 rounded-full blur-[120px] opacity-20 -translate-y-1/2 translate-x-1/2"></div>
                <div className="relative z-10">
                    <div className="inline-flex p-3 bg-white/5 rounded-2xl mb-6">
                        <Bell className="text-orange-500 w-8 h-8" />
                    </div>
                    <h2 className="text-3xl font-black text-white mb-4 tracking-tighter">
                        Don't Miss the Next K-Trend.
                    </h2>
                    <p className="text-gray-400 mb-8 max-w-md mx-auto text-sm font-medium">
                        Get weekly reports on trending beauty products and exclusive affiliate coupons delivered to your inbox.
                    </p>
                    <div className="flex flex-col sm:flex-row gap-2 max-w-sm mx-auto">
                        <input
                            type="email"
                            placeholder="your-email@example.com"
                            className="flex-1 px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-white focus:outline-none focus:border-orange-500 transition-colors text-sm"
                        />
                        <button className="bg-orange-500 text-white px-6 py-3 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-white hover:text-gray-900 transition-all">
                            Join Now
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
// 5. Place Billboard Ad (여행 섹션 상단용)
export const PlaceBillboardAd = () => (
    <div className="w-full bg-emerald-50 border-y border-emerald-100 py-4 px-6 mb-10 rounded-3xl">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
                <div className="bg-[#10B981] text-white p-2 rounded-xl shadow-lg shadow-emerald-200">
                    <Plane size={20} />
                </div>
                <p className="text-sm font-bold text-emerald-900 leading-tight">
                    <span className="bg-white px-2 py-0.5 rounded text-[10px] font-black uppercase text-[#10B981] mr-2 border border-emerald-100">
                        {PLACE_AD_CONFIG.billboard.badge}
                    </span>
                    {PLACE_AD_CONFIG.billboard.text}
                </p>
            </div>
            <a href={PLACE_AD_CONFIG.billboard.linkUrl} target="_blank" className="flex items-center gap-2 text-xs font-black text-[#10B981] uppercase tracking-widest hover:underline whitespace-nowrap">
                Book Now <ExternalLink size={14} />
            </a>
        </div>
    </div>
);

// 6. Place In-Feed Ad (여행 리스트 중간용)
export const PlaceInFeedAd = () => (
    <div className="my-12 p-1 bg-gradient-to-r from-[#10B981] via-teal-400 to-emerald-600 rounded-[3rem] shadow-xl shadow-emerald-100">
        <div className="bg-white rounded-[2.5rem] p-8 md:p-12 flex flex-col md:flex-row items-center gap-8 shadow-inner">
            <div className="flex-1 text-center md:text-left">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-50 text-[#10B981] text-[10px] font-black uppercase tracking-widest rounded-full border border-emerald-100 mb-4">
                    <Gift size={12} /> Special Experience
                </div>
                <h3 className="text-3xl md:text-4xl font-black text-gray-900 mb-3 tracking-tighter leading-none">
                    {PLACE_AD_CONFIG.inFeed.title}
                </h3>
                <p className="text-gray-500 font-medium mb-6 max-w-md italic">
                    "{PLACE_AD_CONFIG.inFeed.description}"
                </p>
                <div className="flex justify-center md:justify-start">
                    <a href={PLACE_AD_CONFIG.inFeed.linkUrl} target="_blank" className="text-xs font-black text-gray-900 border-b-2 border-[#10B981] pb-1 hover:text-[#10B981] transition-all">
                        View All Recommendations
                    </a>
                </div>
            </div>
            <div className="flex-shrink-0 w-full md:w-auto">
                <a href={PLACE_AD_CONFIG.inFeed.linkUrl} target="_blank">
                    <button className="w-full md:w-auto bg-gray-900 hover:bg-[#10B981] text-white px-10 py-5 rounded-2xl font-black text-xs uppercase tracking-widest transition-all flex items-center justify-center gap-3 shadow-2xl shadow-gray-200 active:scale-95">
                        {PLACE_AD_CONFIG.inFeed.buttonText} <ArrowRightIcon size={16} />
                    </button>
                </a>
            </div>
        </div>
    </div>
);
