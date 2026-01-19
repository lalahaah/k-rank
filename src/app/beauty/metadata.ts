import { Metadata } from 'next';

/**
 * K-Beauty Leaderboard 페이지 메타데이터
 * SEO 최적화를 위한 Open Graph, Twitter Cards 포함
 */
export const beautyMetadata: Metadata = {
    title: 'K-Beauty Leaderboard - Real-time Olive Young Rankings',
    description: 'Track the top trending K-Beauty products from Olive Young. Real-time rankings of Korean skincare, makeup, and beauty products updated daily from Seoul.',
    keywords: [
        'K-Beauty',
        'Olive Young',
        'Korean Skincare',
        'Korean Makeup',
        'Beauty Rankings',
        'Korean Beauty Products',
        'Torriden',
        'COSRX',
        'Innisfree',
        'Seoul Beauty',
        'K-Beauty Trends'
    ],
    openGraph: {
        title: 'K-Beauty Leaderboard - Real-time Olive Young Rankings',
        description: 'Track the top trending K-Beauty products from Olive Young. Real-time rankings updated daily from Seoul.',
        url: 'https://k-rank.vercel.app/beauty',
        images: [
            {
                url: '/og-beauty.png',
                width: 1200,
                height: 630,
                alt: 'K-Beauty Leaderboard from Olive Young',
            },
        ],
        type: 'website',
    },
    twitter: {
        card: 'summary_large_image',
        title: 'K-Beauty Leaderboard - Real-time Olive Young Rankings',
        description: 'Track the top trending K-Beauty products from Olive Young. Real-time rankings updated daily.',
        images: ['/twitter-beauty.png'],
    },
    alternates: {
        canonical: 'https://k-rank.vercel.app/beauty',
    },
};
