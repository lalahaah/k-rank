"use client";

import { useState, useEffect } from "react";
import { ChevronUp } from "lucide-react";

export function ScrollToTop() {
    const [isVisible, setIsVisible] = useState(false);

    // 스크롤 위치에 따라 버튼 표시 여부 결정
    useEffect(() => {
        const toggleVisibility = () => {
            if (window.scrollY > 300) {
                setIsVisible(true);
            } else {
                setIsVisible(false);
            }
        };

        window.addEventListener("scroll", toggleVisibility);
        return () => window.removeEventListener("scroll", toggleVisibility);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    };

    return (
        <div className="fixed bottom-8 right-8 z-[100] transition-all duration-500">
            <button
                onClick={scrollToTop}
                className={`
          group flex h-14 w-14 items-center justify-center rounded-full shadow-2xl transition-all duration-500
          ${isVisible
                        ? "translate-y-0 opacity-100 scale-100"
                        : "translate-y-10 opacity-0 scale-50 pointer-events-none"}
          bg-white/80 backdrop-blur-xl border border-gray-100 text-gray-900 
          hover:bg-gray-900 hover:text-white hover:scale-110 active:scale-95
        `}
                aria-label="Scroll to top"
            >
                <ChevronUp className="h-6 w-6 transition-transform group-hover:-translate-y-1" />
            </button>
        </div>
    );
}
