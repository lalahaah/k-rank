import React from 'react';
import { Sparkles, BarChart3, Globe, ShieldCheck } from 'lucide-react';

/**
 * K-Rank SEO Editorial Section
 * 푸터 직전에 배치하여 검색 엔진 최적화와 브랜드 신뢰도를 동시에 잡는 컴포넌트입니다.
 */

export function SeoContent() {
  return (
    <section className="bg-white py-24 border-t border-gray-100">
      <div className="max-w-5xl mx-auto px-6">

        {/* Section Header */}
        <div className="mb-16 text-center">
          <h2 className="text-3xl md:text-5xl font-black text-gray-900 tracking-tighter mb-6">
            DECODING THE <span className="text-orange-500">KOREA PULSE.</span>
          </h2>
          <div className="w-24 h-1.5 bg-orange-500 mx-auto rounded-full"></div>
        </div>

        {/* SEO-Rich Editorial Text */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-20 items-start">

          <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="text-orange-500 w-5 h-5" />
              Real-time Insights from Korea's Heart
            </h3>
            <p className="text-gray-600 leading-relaxed font-medium">
              In the fast-paced world of <strong>Korean trends</strong>, staying updated is no longer a luxury—it's a necessity.
              K-RANK acts as your digital bridge to Korea, aggregating real-time data from authoritative sources like
              <strong> Olive Young</strong> for beauty and <strong>Netflix Korea</strong> for media rankings.
              Unlike static blogs, our leaderboard updates daily to reflect what Koreans are actually buying and watching <em>right now</em>.
            </p>
            <p className="text-gray-600 leading-relaxed font-medium">
              Whether you are looking for the next <strong>K-Beauty holy grail</strong> or the most talked-about <strong>K-Drama</strong>,
              K-RANK provides the cultural context you need to understand the <em>why</em> behind the hype.
            </p>
          </div>

          <div className="space-y-6">
            <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <BarChart3 className="text-orange-500 w-5 h-5" />
              Data-Driven, Not Ad-Driven
            </h3>
            <p className="text-gray-600 leading-relaxed font-medium">
              Our mission is to eliminate information asymmetry. Most "Best K-Beauty" lists online are sponsored or outdated.
              At K-RANK, we prioritize <strong>raw data signals</strong>. We analyze sales volume, social media velocity, and
              search trends in South Korea to curate a list that represents the true local interest.
            </p>
            <ul className="space-y-4 pt-2">
              <li className="flex gap-3">
                <ShieldCheck className="text-green-500 w-5 h-5 shrink-0" />
                <span className="text-sm text-gray-500 font-bold uppercase tracking-tight">Verified Source: Official API & Public Data</span>
              </li>
              <li className="flex gap-3">
                <Globe className="text-blue-500 w-5 h-5 shrink-0" />
                <span className="text-sm text-gray-500 font-bold uppercase tracking-tight">Global Accessibility: English Context & Global Shop Links</span>
              </li>
            </ul>
          </div>

        </div>

        {/* SEO Keywords Footer (Hidden but Searchable or Subtle) */}
        <div className="mt-20 pt-12 border-t border-gray-50">
          <p className="text-[10px] text-gray-300 font-bold uppercase tracking-[0.2em] leading-loose text-center">
            Discover trending: Round Lab Sunscreen • Anua Heartleaf Toner • Torriden Serum • Squid Game Season 2 •
            Seongsu-dong Pop-ups • Hannam-dong Restaurants • Olive Young Rankings • Netflix Top 10 Korea •
            Best Korean Skincare 2026 • Real-time Korea Life.
          </p>
        </div>
      </div>
    </section>
  );
}
