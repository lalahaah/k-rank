export function VpnCta() {
    return (
        <section className="max-w-6xl mx-auto px-6 mb-20">
            <div className="bg-gray-900 rounded-[3rem] p-10 md:p-16 relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="absolute top-0 right-0 w-64 h-64 bg-media-500 rounded-full blur-[120px] opacity-20 -translate-y-1/2 translate-x-1/2"></div>
                <div className="relative z-10">
                    <h3 className="text-3xl md:text-5xl font-black text-white tracking-tighter mb-4">
                        GLOBAL <br /> <span className="text-media-500">STREAMING.</span>
                    </h3>
                    <p className="text-gray-400 font-medium text-sm md:text-base">
                        Access original K-content from anywhere in the world.
                    </p>
                </div>
                <div className="flex flex-wrap gap-3 relative z-10">
                    <a
                        href="https://nordvpn.com/ko/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="bg-media-500 text-white px-8 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-white hover:text-gray-900 transition-all shadow-xl"
                    >
                        🔓 Unlock with NordVPN
                    </a>
                </div>
            </div>
        </section>
    );
}
