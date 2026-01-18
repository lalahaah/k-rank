"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bell, CheckCircle2, AlertCircle } from "lucide-react";
import { useState } from "react";
import { db } from "@/infrastructure/firebase/client";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";

export function CtaSection() {
    const [email, setEmail] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
    const [message, setMessage] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        // 이메일 유효성 검사
        if (!email || !email.includes("@")) {
            setStatus("error");
            setMessage("Please enter a valid email address.");
            return;
        }

        setIsSubmitting(true);
        setStatus("idle");

        try {
            // Firestore에 이메일 저장
            await addDoc(collection(db, "waitlist"), {
                email: email.trim().toLowerCase(),
                subscribedAt: serverTimestamp(),
                category: "k-food-k-place",
            });

            setStatus("success");
            setMessage("Thanks for joining! We'll notify you when we launch.");
            setEmail(""); // 입력 필드 초기화
        } catch (error) {
            console.error("Error saving email:", error);
            setStatus("error");
            setMessage("Something went wrong. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };

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
                    We are currently curating data for <strong>K-Food</strong>, <strong>K-Place</strong> and <strong>K-Media</strong>.
                    Join the waitlist to get notified when we launch new categories.
                </p>

                <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto" onSubmit={handleSubmit}>
                    <Input
                        type="email"
                        placeholder="Enter your email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={isSubmitting}
                        className="h-12 border-gray-200 focus:border-brand-500"
                    />
                    <Button
                        type="submit"
                        disabled={isSubmitting}
                        className="h-12 px-8 bg-brand-500 hover:bg-brand-600 text-white font-bold text-sm uppercase tracking-wide disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSubmitting ? "Submitting..." : "Notify Me"}
                    </Button>
                </form>

                {/* 상태 메시지 */}
                {status !== "idle" && (
                    <div className={`mt-4 flex items-center justify-center gap-2 text-sm ${status === "success" ? "text-green-600" : "text-red-600"
                        }`}>
                        {status === "success" ? (
                            <CheckCircle2 className="w-4 h-4" />
                        ) : (
                            <AlertCircle className="w-4 h-4" />
                        )}
                        <span>{message}</span>
                    </div>
                )}

                <p className="text-xs text-gray-400 mt-4">
                    No spam. Unsubscribe anytime.
                </p>
            </div>
        </section>
    );
}
