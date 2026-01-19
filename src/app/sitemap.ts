import { MetadataRoute } from 'next';

/**
 * 동적 사이트맵 생성
 * Next.js가 자동으로 /sitemap.xml 경로에 제공
 */
export default function sitemap(): MetadataRoute.Sitemap {
    const baseUrl = 'https://k-rank.vercel.app';
    const currentDate = new Date();

    return [
        {
            url: baseUrl,
            lastModified: currentDate,
            changeFrequency: 'daily',
            priority: 1,
        },
        {
            url: `${baseUrl}/beauty`,
            lastModified: currentDate,
            changeFrequency: 'daily',
            priority: 0.9,
        },
        {
            url: `${baseUrl}/media`,
            lastModified: currentDate,
            changeFrequency: 'daily',
            priority: 0.9,
        },
        {
            url: `${baseUrl}/food`,
            lastModified: currentDate,
            changeFrequency: 'weekly',
            priority: 0.7,
        },
        {
            url: `${baseUrl}/place`,
            lastModified: currentDate,
            changeFrequency: 'weekly',
            priority: 0.7,
        },
        {
            url: `${baseUrl}/privacy`,
            lastModified: new Date('2026-01-19'),
            changeFrequency: 'monthly',
            priority: 0.5,
        },
    ];
}
