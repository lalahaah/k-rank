"use client";

import { Search, X } from "lucide-react";
import { useState } from "react";

interface SearchBarProps {
    onSearch: (query: string) => void;
}

export function SearchBar({ onSearch }: SearchBarProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [isFocused, setIsFocused] = useState(false);

    const handleChange = (value: string) => {
        setSearchQuery(value);
        onSearch(value);
    };

    const handleClear = () => {
        setSearchQuery("");
        onSearch("");
    };

    return (
        <div className="relative max-w-2xl">
            <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleChange(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                placeholder="Search brands, spots, or dramas..."
                className="w-full px-6 py-4 pr-24 rounded-full text-lg bg-brand-500 border-2 border-white/80 text-white placeholder:text-white/60 focus:outline-none focus:ring-2 focus:ring-white focus:border-white"
            />

            {/* Clear button */}
            {searchQuery && (
                <button
                    onClick={handleClear}
                    className="absolute right-14 top-1/2 -translate-y-1/2 text-white/60 hover:text-white transition-colors"
                    aria-label="Clear search"
                >
                    <X className="w-5 h-5" />
                </button>
            )}

            {/* Search button */}
            <button
                className="absolute right-4 top-1/2 -translate-y-1/2 text-white/80 hover:text-white transition-colors"
                aria-label="Search"
            >
                <Search className="w-6 h-6" />
            </button>
        </div>
    );
}
