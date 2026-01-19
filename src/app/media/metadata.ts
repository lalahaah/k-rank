import { Metadata } from 'next';

/**
 * K-Media Leaderboard 페이지 메타데이터
 * Netflix Korea 드라마 및 콘텐츠 랭킹을 위한 SEO 최적화
 */
export const mediaMetadata: Metadata = {
    title: 'K-Media Leaderboard - Netflix Korea Top 10 Rankings',
    description: 'Discover the top trending K-Dramas and Korean shows on Netflix. Real-time rankings of Korean movies, dramas, and entertainment content updated daily.',
    keywords: [
        'K-Drama',
        'Netflix Korea',
        'Korean Shows',
        'Korean Movies',
        'K-Drama Rankings',
        'Korean Entertainment',
        'Netflix Top 10 Korea',
        'Squid Game',
        'Korean Series',
        'K-Content',
        'Korean TV Shows'
    ],
    openGraph: {
        title: 'K-Media Leaderboard - Netflix Korea Top 10 Rankings',
        description: 'Discover the top trending K-Dramas and Korean shows on Netflix. Real-time rankings updated daily.',
        url: 'https://k-rank.vercel.app/media',
        images: [
            {
                url: '/og-media.png',
                width: 1200,
                height: 630,
                alt: 'K-Media Leaderboard - Netflix Korea Rankings',
            },
        ],
        type: 'website',
    },
    twitter: {
        card: 'summary_large_image',
        title: 'K-Media Leaderboard - Netflix Korea Top 10 Rankings',
        description: 'Discover the top trending K-Dramas and Korean shows on Netflix. Real-time rankings updated daily.',
        images: ['/twitter-media.png'],
    },
    alternates: {
        canonical: 'https://k-rank.vercel.app/media',
    },
};
