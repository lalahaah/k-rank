import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { Utensils } from "lucide-react";

export default function FoodPage() {
    return (
        <div className="min-h-screen bg-canvas flex flex-col">
            <Navbar />
            <main className="flex-1">
                {/* Hero Section - Food Theme */}
                <div className="w-full bg-food-500 py-24 text-center">
                    <div className="max-w-4xl mx-auto px-4">
                        <h1 className="text-5xl md:text-6xl font-black text-white mb-6 uppercase tracking-tighter drop-shadow-lg">
                            K-Food Leaderboard
                        </h1>
                        <div className="inline-block bg-white text-food-500 px-6 py-2 rounded-full text-sm font-black uppercase tracking-widest shadow-xl animate-bounce mb-8">
                            Coming Soon
                        </div>
                        <p className="text-xl text-white/90 max-w-2xl mx-auto leading-relaxed font-medium drop-shadow-md">
                            We are currently cooking up the real-time rankings for the best Korean restaurants and dishes. Stay tuned!
                        </p>
                    </div>
                </div>

                <div className="py-24 text-center opacity-20">
                    <Utensils className="w-24 h-24 mx-auto text-slate-300" />
                </div>
            </main>
            <Footer />
        </div>
    );
}
