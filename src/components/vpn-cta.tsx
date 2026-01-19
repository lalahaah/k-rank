export function VpnCta() {
    return (
        <div className="w-full bg-gradient-to-r from-media-500 to-media-600 py-16">
            <div className="mx-auto max-w-[1020px] px-4">
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-white mb-4">
                        Not Available in Your Country?
                    </h2>
                    <p className="text-white/90 text-lg mb-6">
                        Access Korean Netflix content from anywhere in the world with a premium VPN service.
                    </p>
                    <a
                        href="https://nordvpn.com/ko/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block"
                    >
                        <button className="bg-white text-media-600 px-8 py-4 rounded-lg text-lg font-bold hover:bg-blue-50 transition-all transform hover:scale-105 active:scale-95 shadow-xl">
                            🔓 Unlock with NordVPN
                        </button>
                    </a>
                    <p className="text-white/70 text-sm mt-4">
                        Fast, secure, and reliable VPN for streaming Korean content
                    </p>
                </div>
            </div>
        </div>
    );
}
