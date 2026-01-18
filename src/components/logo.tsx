import React from 'react';

interface LogoProps {
    className?: string;
    iconOnly?: boolean;
    variant?: 'white' | 'brand';
    size?: 'sm' | 'md' | 'lg' | 'xl';
}

export function Logo({
    className = "",
    iconOnly = false,
    variant = 'brand',
    size = 'md'
}: LogoProps) {
    const isBrand = variant === 'brand';

    // Size mapping to maintain the "Perfect Balance" from the revised concept
    const sizeClasses = {
        sm: {
            container: "gap-2",
            iconBox: "p-1 rounded-lg",
            svg: "16",
            text: "text-xl",
            dots: "1"
        },
        md: {
            container: "gap-2.5",
            iconBox: "p-1.5 rounded-xl",
            svg: "20",
            text: "text-2xl",
            dots: "1.2"
        },
        lg: {
            container: "gap-3",
            iconBox: "p-2 rounded-xl",
            svg: "28",
            text: "text-4xl",
            dots: "1.5"
        },
        xl: { // This matches the user's snippet (approx 48px height)
            container: "gap-4",
            iconBox: "p-2 rounded-xl",
            svg: "32",
            text: "text-5xl",
            dots: "1.5"
        }
    };

    const s = sizeClasses[size];

    return (
        <div className={`flex items-center ${s.container} ${className}`}>
            {/* Icon Box */}
            <div className={`${isBrand ? 'bg-brand-500 text-white' : 'bg-white text-brand-500'} ${s.iconBox} shadow-md flex items-center justify-center flex-shrink-0`}>
                <svg width={s.svg} height={s.svg} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
                    {/* Vertical Line */}
                    <path d="M6 20V4"></path>
                    {/* K Chevron */}
                    <path d="M18 4L10 12L18 20"></path>
                    {/* Dots */}
                    <circle cx="6" cy="4" r={s.dots} fill="currentColor" stroke="none"></circle>
                    <circle cx="18" cy="4" r={s.dots} fill="currentColor" stroke="none"></circle>
                    <circle cx="18" cy="20" r={s.dots} fill="currentColor" stroke="none"></circle>
                </svg>
            </div>

            {/* Logo Text */}
            {!iconOnly && (
                <span className={`${s.text} font-black tracking-tighter leading-none ${isBrand ? 'text-slate-900' : 'text-white'}`}>
                    K-RANK
                </span>
            )}
        </div>
    );
}
