"use client";

import { Search } from "lucide-react";
import { useState } from "react";
import { Logo } from "./logo";
import Link from "next/link";

export function Navbar() {
    const [activeTab, setActiveTab] = useState("beauty");

    return (
        <nav className="sticky top-0 z-50 bg-brand-500 text-white shadow-md">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex-shrink-0">
                        <Logo variant="white" />
                    </Link>

                    {/* Navigation Tabs */}
                    <div className="hidden md:flex items-center space-x-1">
                        <button
                            onClick={() => setActiveTab("beauty")}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "beauty"
                                ? "bg-white/20 text-white"
                                : "text-white/80 hover:bg-white/10 hover:text-white"
                                }`}
                        >
                            Beauty
                        </button>
                        <div className="relative group">
                            <button
                                disabled
                                className="px-4 py-2 rounded-md text-sm font-medium text-white/50 cursor-not-allowed"
                            >
                                Food
                            </button>
                            <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap">
                                Coming Soon
                            </div>
                        </div>
                        <div className="relative group">
                            <button
                                disabled
                                className="px-4 py-2 rounded-md text-sm font-medium text-white/50 cursor-not-allowed"
                            >
                                Place
                            </button>
                            <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap">
                                Coming Soon
                            </div>
                        </div>
                        <div className="relative group">
                            <button
                                disabled
                                className="px-4 py-2 rounded-md text-sm font-medium text-white/50 cursor-not-allowed"
                            >
                                Media
                            </button>
                            <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap">
                                Coming Soon
                            </div>
                        </div>
                    </div>

                    {/* Login Button */}
                    <div className="flex items-center">
                        <button className="px-4 py-2 bg-white text-brand-500 rounded-md text-sm font-medium hover:bg-white/90 transition-colors">
                            Login
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Navigation */}
            <div className="md:hidden px-4 pb-3 space-x-2">
                <button
                    onClick={() => setActiveTab("beauty")}
                    className={`px-3 py-1.5 rounded text-sm font-medium ${activeTab === "beauty"
                        ? "bg-white/20 text-white"
                        : "text-white/80"
                        }`}
                >
                    Beauty
                </button>
                <button disabled className="px-3 py-1.5 rounded text-sm font-medium text-white/50 cursor-not-allowed">
                    Food
                </button>
                <button disabled className="px-3 py-1.5 rounded text-sm font-medium text-white/50 cursor-not-allowed">
                    Place
                </button>
                <button disabled className="px-3 py-1.5 rounded text-sm font-medium text-white/50 cursor-not-allowed">
                    Media
                </button>
            </div>
        </nav>
    );
}
