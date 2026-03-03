"use client";

import React from 'react';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { HeavyRainIcon } from '@/components/weather-icons';

export default function PlacePage() {
    return (
        <div className="min-h-screen bg-[#F5F7FA] font-sans text-gray-900 flex flex-col">
            <Navbar />

            <main className="flex-1 flex flex-col items-center justify-center p-8 text-center">
                <div className="bg-white p-12 md:p-16 rounded-[3rem] shadow-sm border border-gray-100 max-w-2xl w-full">
                    <div className="flex justify-center mb-8">
                        <HeavyRainIcon size={96} className="text-place-500" />
                    </div>
                    <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-gray-900 mb-4">
                        COMING SOON
                    </h1>
                    <p className="text-lg text-gray-500 font-medium">
                        플레이스 랭킹 서비스는 현재 새단장 중입니다.<br />
                        더 나은 서비스로 곧 찾아뵙겠습니다.
                    </p>
                </div>

            </main>

            <Footer />
        </div>
    );
}
