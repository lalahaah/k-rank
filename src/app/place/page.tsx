import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";

export default function PlacePage() {
    return (
        <div className="min-h-screen bg-canvas flex flex-col">
            <Navbar />
            <main className="flex-1 flex flex-col items-center justify-center p-4">
                <div className="text-center">
                    <h1 className="text-5xl font-black text-slate-900 mb-4 tracking-tighter uppercase">
                        K-Place
                    </h1>
                    <div className="inline-block bg-brand-500 text-white px-4 py-1 rounded-full text-sm font-bold uppercase tracking-widest animate-pulse mb-8">
                        Coming Soon
                    </div>
                    <p className="text-lg text-slate-600 max-w-md mx-auto leading-relaxed">
                        Discovering the most trending spots in Korea. Real-time place rankings are arriving soon.
                    </p>
                </div>
            </main>
            <Footer />
        </div>
    );
}
