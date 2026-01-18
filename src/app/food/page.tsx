import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";

export default function FoodPage() {
    return (
        <div className="min-h-screen bg-canvas flex flex-col">
            <Navbar />
            <main className="flex-1 flex flex-col items-center justify-center p-4">
                <div className="text-center">
                    <h1 className="text-5xl font-black text-slate-900 mb-4 tracking-tighter uppercase">
                        K-Food
                    </h1>
                    <div className="inline-block bg-brand-500 text-white px-4 py-1 rounded-full text-sm font-bold uppercase tracking-widest animate-pulse mb-8">
                        Coming Soon
                    </div>
                    <p className="text-lg text-slate-600 max-w-md mx-auto leading-relaxed">
                        We are currently cooking up the real-time rankings for the best Korean restaurants and dishes. Stay tuned!
                    </p>
                </div>
            </main>
            <Footer />
        </div>
    );
}
