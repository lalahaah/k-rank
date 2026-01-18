import React from 'react';

interface LogoProps {
    className?: string;
    iconOnly?: boolean;
    variant?: 'white' | 'brand';
}

export function Logo({ className = "", iconOnly = false, variant = 'brand' }: LogoProps) {
    const isBrand = variant === 'brand';

    return (
        <div className={`flex items-center gap-2.5 ${className}`}>
            <div className={`${isBrand ? 'bg-brand-500 text-white' : 'bg-white text-brand-500'} p-1.5 rounded-lg shadow-sm flex-shrink-0`}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                    {/* Vertical Line (Y-axis / Stem) */}
                    <path d="M6 20V4"></path>
                    {/* K Chevron (Data Points) */}
                    <path d="M18 4L10 12L18 20"></path>
                    {/* Dots for Data feel */}
                    <circle cx="6" cy="4" r="1.5" fill="currentColor" stroke="none"></circle>
                    <circle cx="18" cy="4" r="1.5" fill="currentColor" stroke="none"></circle>
                    <circle cx="18" cy="20" r="1.5" fill="currentColor" stroke="none"></circle>
                </svg>
            </div>
            {!iconOnly && (
                <div className="flex flex-col leading-none">
                    <span className={`text-xl font-black tracking-tighter ${isBrand ? 'text-slate-900' : 'text-white'}`}>K-RANK</span>
                    <span className={`${isBrand ? 'text-brand-500' : 'text-white/80'} text-[7px] font-bold tracking-[0.2em] uppercase mt-0.5`}>Leaderboard</span>
                </div>
            )}
        </div>
    );
}
