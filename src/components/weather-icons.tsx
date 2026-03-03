"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface WeatherIconProps {
    size?: number;
    className?: string;
}

/* ─── HEAVY RAIN ─── */
export function HeavyRainIcon({ size = 48, className }: WeatherIconProps) {
    const drops = [
        { x: 14, d: 0 }, { x: 19, d: 0.15 }, { x: 24, d: 0.3 },
        { x: 29, d: 0.1 }, { x: 34, d: 0.4 }, { x: 37, d: 0.25 },
    ];
    return (
        <svg viewBox="-2 -2 52 52" fill="none" className={cn("text-current", className)} style={{ width: size, height: size }}>
            <path d="M36 20H14a7 7 0 01-.5-14A9 9 0 0134 8a6 6 0 012 12z" fill="currentColor" opacity={0.15} />
            <path d="M36 20H14a7 7 0 01-.5-14A9 9 0 0134 8a6 6 0 012 12z" stroke="currentColor" strokeWidth={2} strokeLinecap="round" />
            {drops.map((drop) => (
                <motion.line key={drop.x} x1={drop.x} y1={24} x2={drop.x - 2} y2={30} stroke="currentColor" strokeWidth={1.5} strokeLinecap="round"
                    animate={{ y: [0, 16], opacity: [1, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: drop.d, ease: "easeIn" }} />
            ))}
        </svg>
    );
}
