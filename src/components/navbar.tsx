"use client";

import { Search } from "lucide-react";
import { useState, useEffect } from "react";
import { Logo } from "./logo";
import Link from "next/link";
import { usePathname } from "next/navigation";

export function Navbar() {
    const pathname = usePathname();
    const [activeTab, setActiveTab] = useState("beauty");

    // Set active tab based on current pathname
    useEffect(() => {
        if (pathname === "/media") {
            setActiveTab("media");
        } else if (pathname === "/beauty") {
            setActiveTab("beauty");
        } else if (pathname === "/food") {
            setActiveTab("food");
        } else if (pathname === "/place") {
            setActiveTab("place");
        } else {
            setActiveTab("home");
        }
    }, [pathname]);

    // Theme color based on active tab
    const getThemeColor = (tab: string) => {
        switch (tab) {
            case "beauty": return "bg-beauty-600";
            case "media": return "bg-media-600";
            case "food": return "bg-food-600";
            case "place": return "bg-place-600";
            default: return "bg-white/20";
        }
    };

    const getMobileThemeColor = (tab: string) => {
        switch (tab) {
            case "beauty": return "bg-beauty-600 text-white";
            case "media": return "bg-media-600 text-white";
            case "food": return "bg-food-600 text-white";
            case "place": return "bg-place-600 text-white";
            default: return "text-white/80";
        }
    };

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
                        <Link href="/beauty">
                            <button
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "beauty"
                                    ? `${getThemeColor("beauty")} text-white shadow-sm`
                                    : "text-white/80 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                Beauty
                            </button>
                        </Link>
                        <Link href="/food">
                            <button
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "food"
                                    ? `${getThemeColor("food")} text-white shadow-sm`
                                    : "text-white/80 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                Food
                            </button>
                        </Link>
                        <Link href="/place">
                            <button
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "place"
                                    ? `${getThemeColor("place")} text-white shadow-sm`
                                    : "text-white/80 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                Place
                            </button>
                        </Link>
                        <Link href="/media">
                            <button
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "media"
                                    ? `${getThemeColor("media")} text-white shadow-sm`
                                    : "text-white/80 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                Media
                            </button>
                        </Link>
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
                <Link href="/beauty">
                    <button
                        className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${activeTab === "beauty"
                            ? getMobileThemeColor("beauty")
                            : "text-white/80"
                            }`}
                    >
                        Beauty
                    </button>
                </Link>
                <Link href="/food">
                    <button
                        className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${activeTab === "food"
                            ? getMobileThemeColor("food")
                            : "text-white/80"
                            }`}
                    >
                        Food
                    </button>
                </Link>
                <Link href="/place">
                    <button
                        className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${activeTab === "place"
                            ? getMobileThemeColor("place")
                            : "text-white/80"
                            }`}
                    >
                        Place
                    </button>
                </Link>
                <Link href="/media">
                    <button
                        className={`px-3 py-1.5 rounded text-sm font-medium transition-all ${activeTab === "media"
                            ? getMobileThemeColor("media")
                            : "text-white/80"
                            }`}
                    >
                        Media
                    </button>
                </Link>
            </div>
        </nav>
    );
}
