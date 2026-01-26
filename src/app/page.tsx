"use client";

import { Sparkles, ArrowRight, PlayCircle, Utensils, MapPin } from "lucide-react";
import Link from "next/link";
import Script from "next/script";
import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";
import { SeoContent } from "@/components/seo-content";
import { TrendSummary } from "@/components/trend-summary";


export default function LandingPage() {
  // JSON-LD 구조화된 데이터 (SEO)
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'K-Rank Leaderboard',
    description: 'Real-time Korean trends rankings for Beauty, Media, Food, and Places',
    url: 'https://k-rank.vercel.app',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: 'https://k-rank.vercel.app/search?q={search_term_string}'
      },
      'query-input': 'required name=search_term_string'
    },
    publisher: {
      '@type': 'Organization',
      name: 'K-Rank',
      logo: {
        '@type': 'ImageObject',
        url: 'https://k-rank.vercel.app/logo.png'
      }
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F7FA] font-sans">
      {/* JSON-LD for SEO */}
      <Script
        id="jsonld-website"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <Navbar />


      {/* Hero Section with Background Image */}
      <section className="relative flex-1 flex flex-col items-center justify-center px-4 py-24 text-center overflow-hidden">

        {/* Background Image (Seoul Night View) */}
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1538485399081-7191377e8241?q=80&w=2000&auto=format&fit=crop"
            alt="Korea Cityscape"
            className="w-full h-full object-cover"
          />
          {/* Dark Overlay for Readability */}
          <div className="absolute inset-0 bg-slate-900/70 backdrop-blur-[2px]"></div>
        </div>

        <div className="relative z-10 w-full max-w-5xl mx-auto flex flex-col items-center">

          {/* Brand Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/20 text-white text-xs font-bold uppercase tracking-wider mb-8 backdrop-blur-md shadow-lg">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            Live Data from Korea
          </div>

          {/* Main Typography */}
          <h1 className="text-5xl md:text-7xl font-black text-white tracking-tighter mb-6 leading-tight drop-shadow-xl">
            K-RANK <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#5383E8] to-blue-300">LEADERBOARD</span>
          </h1>

          <p className="text-lg md:text-xl text-gray-200 max-w-2xl mx-auto mb-16 leading-relaxed font-light drop-shadow-md">
            Don't guess what's trending. <strong className="text-white font-bold">Know it.</strong> <br className="hidden md:block" />
            Real-time rankings for Beauty, Media, Food and Places straight from Korea.
          </p>

          {/* Bento Grid Navigation */}
          <div className="grid grid-cols-1 md:grid-cols-4 md:grid-rows-2 gap-4 w-full h-auto md:h-[420px]">

            {/* Card 1: Beauty (Left Big Column) */}
            <Link href="/beauty" className="group col-span-1 md:col-span-2 md:row-span-2 relative h-64 md:h-auto rounded-3xl overflow-hidden bg-beauty-500/50 hover:bg-beauty-600 transition-all shadow-2xl hover:-translate-y-1 block border border-white/10">
              <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1612817288484-96639d073114?q=80&w=1000&auto=format&fit=crop')] bg-cover bg-center opacity-30 group-hover:opacity-20 transition-opacity"></div>

              <div className="absolute inset-0 p-8 flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <div className="bg-white/20 backdrop-blur-md p-3 rounded-2xl text-white">
                    <Sparkles className="w-8 h-8" />
                  </div>
                  <span className="bg-white text-beauty-500 px-3 py-1 rounded-full text-xs font-bold uppercase shadow-sm">#1 Traffic</span>
                </div>
                <div className="text-left relative z-10">
                  <h3 className="text-4xl font-black text-white mb-2 tracking-tight">K-BEAUTY</h3>
                  <p className="text-rose-100 text-sm mb-6 font-medium">Olive Young Real-time Rankings.</p>
                  <div className="inline-flex items-center gap-3 bg-white text-beauty-500 px-5 py-2.5 rounded-full font-bold text-sm hover:bg-rose-50 transition-colors shadow-lg">
                    View Ranking <ArrowRight className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </Link>

            {/* Card 2: Media (Top Right Wide) */}
            <Link href="/media" className="group col-span-1 md:col-span-2 md:row-span-1 relative h-48 md:h-auto rounded-3xl overflow-hidden bg-media-500/50 hover:bg-media-600 transition-all shadow-2xl hover:-translate-y-1 border border-white/10 block">
              <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?q=80&w=1000&auto=format&fit=crop')] bg-cover bg-center opacity-40 group-hover:opacity-30 transition-opacity"></div>

              <div className="absolute inset-0 p-6 flex justify-between items-center">
                <div className="text-left relative z-10">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-white text-media-500 px-2 py-0.5 rounded text-[10px] font-bold uppercase">Netflix Top 10</span>
                  </div>
                  <h3 className="text-2xl font-black text-white mb-1">K-MEDIA</h3>
                  <p className="text-red-100 text-xs font-medium">Dramas & Movies.</p>
                </div>
                <div className="bg-white/10 backdrop-blur-md p-3 rounded-full text-white border border-white/10">
                  <PlayCircle className="w-8 h-8 fill-current" />
                </div>
              </div>
            </Link>

            {/* Card 3: Food (Bottom Right 1) */}
            <Link href="/food" className="group col-span-1 md:row-span-1 relative h-40 md:h-auto rounded-3xl overflow-hidden bg-food-500/50 hover:bg-food-600 transition-all shadow-2xl hover:-translate-y-1 border border-white/10 block">
              <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1585478259715-876a6a81fc08?q=80&w=1000&auto=format&fit=crop')] bg-cover bg-center opacity-40 group-hover:opacity-30 transition-opacity"></div>

              <div className="absolute inset-0 p-6 flex justify-between items-center">
                <div className="text-left relative z-10">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-white text-food-500 px-2 py-0.5 rounded text-[10px] font-bold uppercase">Seoul Eats</span>
                  </div>
                  <h3 className="text-2xl font-black text-white mb-1">K-FOOD</h3>
                  <p className="text-orange-100 text-xs font-medium">Hot Restaurants.</p>
                </div>
                <div className="bg-white/10 backdrop-blur-md p-3 rounded-full text-white border border-white/10">
                  <Utensils className="w-8 h-8" />
                </div>
              </div>
            </Link>

            {/* Card 4: Place (Bottom Right 2) */}
            <Link href="/place" className="group col-span-1 md:row-span-1 relative h-40 md:h-auto rounded-3xl overflow-hidden bg-place-500/50 hover:bg-place-600 border border-white/20 transition-all shadow-2xl hover:-translate-y-1 block">
              <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1517154421773-0529f29ea451?q=80&w=1000&auto=format&fit=crop')] bg-cover bg-center opacity-40 group-hover:opacity-30 transition-opacity"></div>

              <div className="absolute inset-0 p-6 flex justify-between items-center">
                <div className="text-left relative z-10">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-white text-place-500 px-2 py-0.5 rounded text-[10px] font-bold uppercase">Travel Guide</span>
                  </div>
                  <h3 className="text-2xl font-black text-white mb-1">K-PLACE</h3>
                  <p className="text-emerald-100 text-xs font-medium">Local Favorites.</p>
                </div>
                <div className="bg-white/10 backdrop-blur-md p-3 rounded-full text-white border border-white/10">
                  <MapPin className="w-8 h-8" />
                </div>
              </div>
            </Link>

          </div>
        </div>
      </section>

      <TrendSummary />
      <SeoContent />
      <Footer />
    </div>
  );
}
