export interface RankingItem {
    rank: number;
    productName: string;
    brand: string;
    imageUrl: string;
    price: string;
    tags: string[];
    subcategory: string;
    trend: number;
    buyUrl?: string;
}

export interface MediaRankingItem {
    rank: number;
    titleEn: string;
    titleKo?: string;
    imageUrl: string;
    weeksInTop10: string;
    type: 'TV Show' | 'Film';
    trailerLink: string;
    vpnLink?: string;
    tags: string[];
    trend: number;
}

export interface DailyRanking {
    date: string;
    category: string;
    items: RankingItem[];
    updatedAt: any;
}

export interface MediaDailyRanking {
    date: string;
    category: string;
    items: MediaRankingItem[];
    updatedAt: any;
}
