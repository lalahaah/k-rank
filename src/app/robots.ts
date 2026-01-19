import { MetadataRoute } from 'next';

/**
 * robots.txt 설정
 * 검색엔진 크롤러에게 크롤링 규칙을 알려줌
 */
export default function robots(): MetadataRoute.Robots {
    const baseUrl = 'https://k-rank.vercel.app';

    return {
        rules: [
            {
                userAgent: '*',
                allow: '/',
                disallow: [
                    '/api/',
                    '/admin/',
                    '/_next/',
                    '/private/',
                ],
            },
            {
                userAgent: 'Googlebot',
                allow: '/',
                disallow: ['/api/', '/admin/'],
            },
            {
                userAgent: 'Bingbot',
                allow: '/',
                disallow: ['/api/', '/admin/'],
            },
        ],
        sitemap: `${baseUrl}/sitemap.xml`,
    };
}
