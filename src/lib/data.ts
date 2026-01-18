import { collection, query, where, orderBy, limit, getDocs } from 'firebase/firestore';
import { db } from './firebase';

export interface RankingItem {
    rank: number;
    productName: string;
    brand: string;
    imageUrl: string;
    price: string;
    tags: string[];
    subcategory: string;
    trend: number;
}

export interface DailyRanking {
    date: string;
    category: string;
    items: RankingItem[];
    updatedAt: any;
}

/**
 * Fetch the latest ranking data for a specific category
 * @param category - The category to fetch (e.g., 'all', 'skincare', 'suncare', 'masks', 'makeup', 'hair-body')
 * @returns Array of ranking items, or empty array if no data found
 */
export async function getLatestRankings(category: string): Promise<RankingItem[]> {
    try {
        // Get today's date in YYYY-MM-DD format (UTC)
        const today = new Date().toISOString().split('T')[0];

        // 카테고리 매핑: 프론트엔드 카테고리 -> Firestore 카테고리
        let firestoreCategory = 'beauty'; // default for 'all'
        if (category !== 'all') {
            firestoreCategory = `beauty-${category}`;
        }

        // Query using today's date as document ID
        const rankingsRef = collection(db, 'daily_rankings');
        const q = query(
            rankingsRef,
            where('category', '==', firestoreCategory),
            where('date', '==', today)
        );

        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            console.warn(`No rankings found for category: ${firestoreCategory} on date: ${today}`);

            // Fallback: Try to get any document for this category (without date filter)
            const fallbackQ = query(
                rankingsRef,
                where('category', '==', firestoreCategory)
            );

            const fallbackSnapshot = await getDocs(fallbackQ);

            if (fallbackSnapshot.empty) {
                console.warn(`No rankings found for category: ${firestoreCategory} at all`);
                return [];
            }

            // Get the first document found
            const doc = fallbackSnapshot.docs[0];
            const data = doc.data() as DailyRanking;
            console.log(`Loaded rankings from date: ${data.date} for category: ${firestoreCategory}`);

            return data.items || [];
        }

        // Get the first (should be only one) document for today
        const doc = querySnapshot.docs[0];
        const data = doc.data() as DailyRanking;

        return data.items || [];
    } catch (error) {
        console.error('Error fetching rankings:', error);
        return [];
    }
}

// Media 관련 인터페이스
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

export interface MediaDailyRanking {
    date: string;
    category: string;
    items: MediaRankingItem[];
    updatedAt: any;
}

/**
 * Fetch the latest media rankings (Netflix Top 10)
 * @returns Array of media ranking items, or empty array if no data found
 */
export async function getMediaRankings(): Promise<MediaRankingItem[]> {
    try {
        // Get today's date in YYYY-MM-DD format (UTC)
        const today = new Date().toISOString().split('T')[0];

        // Query using today's date as document ID
        const rankingsRef = collection(db, 'daily_rankings');
        const q = query(
            rankingsRef,
            where('category', '==', 'media'),
            where('date', '==', today)
        );

        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            console.warn(`No media rankings found for date: ${today}`);

            // Fallback: Try to get any document for media category
            const fallbackQ = query(
                rankingsRef,
                where('category', '==', 'media')
            );

            const fallbackSnapshot = await getDocs(fallbackQ);

            if (fallbackSnapshot.empty) {
                console.warn('No media rankings found at all');
                return [];
            }

            // Get the first document found
            const doc = fallbackSnapshot.docs[0];
            const data = doc.data() as MediaDailyRanking;
            console.log(`Loaded media rankings from date: ${data.date}`);

            return data.items || [];
        }

        // Get the first (should be only one) document for today
        const doc = querySnapshot.docs[0];
        const data = doc.data() as MediaDailyRanking;

        return data.items || [];
    } catch (error) {
        console.error('Error fetching media rankings:', error);
        return [];
    }
}


/**
 * Fetch all rankings for a specific date
 * @param date - Date string in YYYY-MM-DD format
 * @param category - The category to fetch
 * @returns Array of ranking items, or empty array if no data found
 */
export async function getRankingsByDate(
    date: string,
    category: string
): Promise<RankingItem[]> {
    try {
        const rankingsRef = collection(db, 'daily_rankings');
        const q = query(
            rankingsRef,
            where('date', '==', date),
            where('category', '==', category)
        );

        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            console.warn(`No rankings found for date: ${date}, category: ${category}`);
            return [];
        }

        const doc = querySnapshot.docs[0];
        const data = doc.data() as DailyRanking;

        return data.items || [];
    } catch (error) {
        console.error('Error fetching rankings by date:', error);
        return [];
    }
}
