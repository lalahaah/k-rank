import { RankingItem, MediaRankingItem } from '../entities/ranking';

export interface IRankingRepository {
    getLatestRankings(category: string): Promise<RankingItem[]>;
    getMediaRankings(): Promise<MediaRankingItem[]>;
    getRankingsByDate(date: string, category: string): Promise<RankingItem[]>;
}
