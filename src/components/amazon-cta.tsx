"use client";

import { Button } from "@/components/ui/button";
import { ExternalLink } from "lucide-react";

export function AmazonCta() {
    const handleClick = () => {
        // Amazon.com 한국 스낵 검색 페이지로 리다이렉트
        const affiliateId = process.env.NEXT_PUBLIC_AMAZON_AFFILIATE_ID || 'krank-20';
        const searchUrl = `https://www.amazon.com/s?k=korean+snacks+ramen&tag=${affiliateId}`;
        window.open(searchUrl, '_blank', 'noopener,noreferrer');
    };

    return (
        <section className="bg-gradient-to-r from-food-500 to-food-600 py-16">
            <div className="max-w-4xl mx-auto px-4 text-center">
                <div className="inline-flex items-center justify-center p-3 bg-white/20 rounded-full mb-6">
                    <span className="text-5xl">🛒</span>
                </div>

                <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                    Want to Try These Korean Snacks?
                </h2>

                <p className="text-white/90 text-lg mb-8 max-w-2xl mx-auto">
                    Shop authentic Korean ramen, snacks, and beverages on Amazon with fast shipping to your doorstep!
                </p>

                <Button
                    onClick={handleClick}
                    className="h-14 px-8 bg-white text-food-600 hover:bg-gray-100 text-lg font-bold rounded-full shadow-xl transition-all hover:scale-105"
                >
                    <ExternalLink className="w-5 h-5 mr-2" />
                    Shop on Amazon
                </Button>

                <p className="text-white/70 text-sm mt-6">
                    As an Amazon Associate, we earn from qualifying purchases.
                </p>
            </div>
        </section>
    );
}
