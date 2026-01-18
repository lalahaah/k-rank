export function Footer() {
    return (
        <footer className="bg-gray-50 border-t border-gray-200 pt-12 pb-8">
            <div className="max-w-6xl mx-auto px-4">

                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
                    {/* Brand Info */}
                    <div className="col-span-1 md:col-span-1">
                        <div className="font-black text-brand-500 text-xl mb-4 tracking-tighter">K-RANK</div>
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
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                        <span>Data Source:</span>
                        <span className="font-bold text-gray-600">Olive Young Korea</span>
                    </div>
                </div>
            </div>
        </footer>
    );
}
