"use client";

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Logo } from "./logo";

const DATA_SOURCES = [
    { name: "Olive Young Korea", category: "Beauty", link: "https://www.oliveyoung.co.kr" },
    // 추후 다른 소스 추가 예시:
    // { name: "Naver Shopping", category: "General", link: "https://shopping.naver.com" },
];

export function Footer() {
    return (
        <footer className="bg-gray-50 border-t border-gray-200 pt-12 pb-8">
            <div className="max-w-6xl mx-auto px-4">

                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
                    {/* Brand Info */}
                    <div className="col-span-1 md:col-span-1">
                        <Logo variant="brand" className="mb-4" />
                        <p className="text-sm text-gray-500 leading-relaxed">
                            Your data-driven guide to real-time Korean trends.
                            We track daily rankings to help you shop smart.
                        </p>
                    </div>

                    {/* Categories */}
                    <div>
                        <h4 className="font-bold text-gray-900 mb-4 text-sm uppercase tracking-wide">Explore</h4>
                        <ul className="space-y-2 text-sm text-gray-500">
                            <li><a href="#" className="hover:text-brand-500 transition-colors">K-Beauty</a></li>
                            <li><span className="opacity-50 cursor-not-allowed">K-Food (Soon)</span></li>
                            <li><span className="opacity-50 cursor-not-allowed">K-Place (Soon)</span></li>
                            <li><span className="opacity-50 cursor-not-allowed">K-Media (Soon)</span></li>
                        </ul>
                    </div>

                    {/* Company */}
                    <div>
                        <h4 className="font-bold text-gray-900 mb-4 text-sm uppercase tracking-wide">Company</h4>
                        <ul className="space-y-2 text-sm text-gray-500">
                            <li><a href="#" className="hover:text-brand-500 transition-colors">About Us</a></li>
                            <li><a href="#" className="hover:text-brand-500 transition-colors">Contact</a></li>
                            <li><a href="#" className="hover:text-brand-500 transition-colors">Privacy Policy</a></li>
                            <li>
                                <Dialog>
                                    <DialogTrigger asChild>
                                        <button className="hover:text-brand-500 transition-colors text-left outline-none">
                                            Data Source
                                        </button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-md">
                                        <DialogHeader>
                                            <DialogTitle>Data Sources</DialogTitle>
                                            <DialogDescription>
                                                We collect and analyze data from the following authoritative sources.
                                            </DialogDescription>
                                        </DialogHeader>
                                        <div className="mt-4 space-y-4">
                                            {DATA_SOURCES.map((source) => (
                                                <div key={source.name} className="flex items-center justify-between p-3 border rounded-lg bg-gray-50">
                                                    <div>
                                                        <div className="font-semibold text-gray-900">{source.name}</div>
                                                        <div className="text-xs text-gray-500">{source.category}</div>
                                                    </div>
                                                    <a
                                                        href={source.link}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-xs text-brand-500 hover:underline font-medium"
                                                    >
                                                        Visit Site
                                                    </a>
                                                </div>
                                            ))}
                                            <div className="p-3 border border-dashed rounded-lg bg-gray-50/50 flex items-center justify-center">
                                                <span className="text-xs text-gray-400 italic">More sources coming soon...</span>
                                            </div>
                                        </div>
                                    </DialogContent>
                                </Dialog>
                            </li>
                        </ul>
                    </div>

                    {/* Disclaimer (Legal) */}
                    <div className="col-span-1 md:col-span-1">
                        <h4 className="font-bold text-gray-900 mb-4 text-sm uppercase tracking-wide">Disclosure</h4>
                        <p className="text-xs text-gray-400 leading-relaxed">
                            K-RANK is a participant in the Amazon Services LLC Associates Program.
                            We may earn commissions on qualifying purchases made through our links at no extra cost to you.
                        </p>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-gray-200 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-xs text-gray-400">
                        &copy; {new Date().getFullYear()} K-Rank Leaderboards. All rights reserved.
                    </p>

                </div>
            </div>
        </footer>
    );
}
