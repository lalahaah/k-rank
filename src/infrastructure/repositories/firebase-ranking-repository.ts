import { collection, query, where, getDocs } from 'firebase/firestore';
import { db } from '../firebase/client';
import { IRankingRepository } from '../../domain/repositories/ranking-repository';
import { RankingItem, MediaRankingItem, DailyRanking, MediaDailyRanking } from '../../domain/entities/ranking';

export class FirebaseRankingRepository implements IRankingRepository {
    async getLatestRankings(category: string): Promise<RankingItem[]> {
        try {
            const today = new Date().toISOString().split('T')[0];
            let firestoreCategory = 'beauty';
            if (category !== 'all') {
                firestoreCategory = `beauty-${category}`;
            }

            const rankingsRef = collection(db, 'daily_rankings');
            const q = query(
                rankingsRef,
                where('category', '==', firestoreCategory),
                where('date', '==', today)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                const fallbackQ = query(
                    rankingsRef,
                    where('category', '==', firestoreCategory)
                );
                const fallbackSnapshot = await getDocs(fallbackQ);

                if (fallbackSnapshot.empty) return [];

                const doc = fallbackSnapshot.docs[0];
                const data = doc.data() as DailyRanking;
                return data.items || [];
            }

            const doc = querySnapshot.docs[0];
            const data = doc.data() as DailyRanking;
            return data.items || [];
        } catch (error) {
            console.error('Error fetching rankings from Firebase:', error);
            return [];
        }
    }

    async getMediaRankings(): Promise<MediaRankingItem[]> {
        try {
            const today = new Date().toISOString().split('T')[0];
            const rankingsRef = collection(db, 'daily_rankings');
            const q = query(
                rankingsRef,
                where('category', '==', 'media'),
                where('date', '==', today)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                const fallbackQ = query(
                    rankingsRef,
                    where('category', '==', 'media')
                );
                const fallbackSnapshot = await getDocs(fallbackQ);

                if (fallbackSnapshot.empty) return [];

                const doc = fallbackSnapshot.docs[0];
                const data = doc.data() as MediaDailyRanking;
                return data.items || [];
            }

            const doc = querySnapshot.docs[0];
            const data = doc.data() as MediaDailyRanking;
            return data.items || [];
        } catch (error) {
            console.error('Error fetching media rankings from Firebase:', error);
            return [];
        }
    }

    async getRankingsByDate(date: string, category: string): Promise<RankingItem[]> {
        try {
            const rankingsRef = collection(db, 'daily_rankings');
            const q = query(
                rankingsRef,
                where('date', '==', date),
                where('category', '==', category)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) return [];

            const doc = querySnapshot.docs[0];
            const data = doc.data() as DailyRanking;
            return data.items || [];
        } catch (error) {
            console.error('Error fetching rankings by date from Firebase:', error);
            return [];
        }
    }
}
