import { FirebaseRankingRepository } from '@/infrastructure/repositories/firebase-ranking-repository';
import { PlaceRankingItem } from '@/domain/entities/ranking';

const repository = new FirebaseRankingRepository();

export async function getLatestRankings(category: 'place'): Promise<PlaceRankingItem[]>;
export async function getLatestRankings(category: string): Promise<any[]> {
    if (category === 'place') {
        return repository.getPlaceRankings();
    }
    return repository.getLatestRankings(category);
}
