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
 * @param category - The category to fetch (e.g., 'beauty')
 * @returns Array of ranking items, or empty array if no data found
 */
export async function getLatestRankings(category: string): Promise<RankingItem[]> {
    try {
        // Get today's date in YYYY-MM-DD format (UTC)
        const today = new Date().toISOString().split('T')[0];

        // Query using today's date as document ID
        const rankingsRef = collection(db, 'daily_rankings');
        const q = query(
            rankingsRef,
            where('category', '==', category),
            where('date', '==', today)
        );

        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            console.warn(`No rankings found for category: ${category} on date: ${today}`);

            // Fallback: Try to get any document for this category (without date filter)
            const fallbackQ = query(
                rankingsRef,
                where('category', '==', category)
            );

            const fallbackSnapshot = await getDocs(fallbackQ);

            if (fallbackSnapshot.empty) {
                console.warn(`No rankings found for category: ${category} at all`);
                return [];
            }

            // Get the first document found
            const doc = fallbackSnapshot.docs[0];
            const data = doc.data() as DailyRanking;
            console.log(`Loaded rankings from date: ${data.date}`);

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
