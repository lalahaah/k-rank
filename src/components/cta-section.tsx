"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bell } from "lucide-react";

export function CtaSection() {
    return (
        <section className="bg-white border-t border-gray-100 py-16">
            <div className="max-w-4xl mx-auto px-4 text-center">
                <div className="inline-flex items-center justify-center p-3 bg-brand-50 rounded-full mb-6">
                    <Bell className="w-6 h-6 text-brand-500" />
                </div>

                <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
                    Don't Miss the Next K-Trend
                </h2>

                <p className="text-gray-500 mb-8 max-w-lg mx-auto">
                    We are currently curating data for <strong>K-Food</strong> and <strong>K-Place</strong>.
                    Join the waitlist to get notified when we launch new categories.
                </p>

                <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto" onSubmit={(e) => e.preventDefault()}>
                    <Input
                        type="email"
                        placeholder="Enter your email"
                        className="h-12 border-gray-200 focus:border-brand-500"
                    />
                    <Button type="submit" className="h-12 px-8 bg-brand-500 hover:bg-brand-600 text-white font-bold text-sm uppercase tracking-wide">
                        Notify Me
                    </Button>
                </form>

                <p className="text-xs text-gray-400 mt-4">
                    No spam. Unsubscribe anytime.
                </p>
            </div>
        </section>
    );
}
