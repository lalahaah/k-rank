import { collection, query, where, getDocs, orderBy, limit } from 'firebase/firestore';
import { db } from '../firebase/client';
import { IRankingRepository } from '../../domain/repositories/ranking-repository';
import { RankingItem, MediaRankingItem, FoodRankingItem, DailyRanking, MediaDailyRanking, FoodDailyRanking, RestaurantRankingItem, RestaurantDailyRanking, PlaceRankingItem, PlaceDailyRanking } from '../../domain/entities/ranking';


export class FirebaseRankingRepository implements IRankingRepository {
    async getLatestRankings(category: string): Promise<RankingItem[]> {
        try {
            let firestoreCategory = 'beauty';
            if (category !== 'all') {
                firestoreCategory = `beauty-${category}`;
            }

            const rankingsRef = collection(db, 'daily_rankings');
            // 날짜 내림차순으로 정렬하여 가장 최신 데이터 1개를 가져옴
            const q = query(
                rankingsRef,
                where('category', '==', firestoreCategory),
                orderBy('date', 'desc'),
                limit(1)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                return [];
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
            const rankingsRef = collection(db, 'daily_rankings');
            const q = query(
                rankingsRef,
                where('category', '==', 'media'),
                orderBy('date', 'desc'),
                limit(1)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                return [];
            }

            const doc = querySnapshot.docs[0];
            const data = doc.data() as MediaDailyRanking;
            return data.items || [];
        } catch (error) {
            console.error('Error fetching media rankings from Firebase:', error);
            return [];
        }
    }

    async getFoodRankings(): Promise<FoodRankingItem[]> {
        try {
            const rankingsRef = collection(db, 'daily_rankings');
            const q = query(
                rankingsRef,
                where('category', '==', 'food'),
                orderBy('date', 'desc'),
                limit(1)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                return [];
            }

            const doc = querySnapshot.docs[0];
            const data = doc.data() as FoodDailyRanking;
            return data.items || [];
        } catch (error) {
            console.error('Error fetching food rankings from Firebase:', error);
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

    async getRestaurantRankings(): Promise<RestaurantRankingItem[]> {
        try {
            const rankingsRef = collection(db, 'daily_rankings');
            const q = query(
                rankingsRef,
                where('category', '==', 'restaurants'),
                orderBy('date', 'desc'),
                limit(1)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                return [];
            }

            const doc = querySnapshot.docs[0];
            const data = doc.data() as RestaurantDailyRanking;
            return data.items || [];
        } catch (error) {
            console.error('Error fetching restaurant rankings from Firebase:', error);
            return [];
        }
    }

    async getPlaceRankings(): Promise<PlaceRankingItem[]> {
        try {
            const rankingsRef = collection(db, 'daily_rankings');
            const q = query(
                rankingsRef,
                where('category', '==', 'place'),
                orderBy('date', 'desc'),
                limit(1)
            );

            const querySnapshot = await getDocs(q);

            if (querySnapshot.empty) {
                return [];
            }

            const doc = querySnapshot.docs[0];
            const data = doc.data() as PlaceDailyRanking;
            return data.items || [];
        } catch (error) {
            console.error('Error fetching place rankings from Firebase:', error);
            return [];
        }
    }
}
