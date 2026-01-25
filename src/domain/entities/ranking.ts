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
    // Fields for Travel
    name_ko?: string;
    name_en?: string;
    ai_story?: string;
    photo_spot?: string;
    address_ko?: string;
    booking_url?: string;
    views?: string;
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

export interface FoodRankingItem {
    rank: number;
    productName: string;
    brand: string;
    imageUrl: string;
    price: string;
    category: 'Ramen' | 'Snack' | 'Beverage';
    tags: string[];
    spicyLevel?: number; // 1-5
    isVegan?: boolean;
    trend: number;
    buyUrl?: string; // Amazon affiliate link
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

export interface FoodDailyRanking {
    date: string;
    category: string;
    items: FoodRankingItem[];
    updatedAt: any;
}

export interface RestaurantRankingItem {
    rank: number;
    name: string;                    // 레스토랑명 (영문)
    nameKo?: string;                 // 레스토랑명 (한글)
    location: string;                // 지역 (예: "Dosan, Seoul")
    category: string;                // 카테고리 (예: "Bakery / Cafe", "K-BBQ (Pork)")
    imageUrl: string;                // 대표 이미지 URL
    images?: string[];               // 추가 이미지 URL 배열
    waitTime?: string;               // 평균 대기 시간 (예: "120 min")
    hypeScore: number;               // NIK Index (0-100)
    status: 'Available' | 'Queueing' | 'Hard to Book' | 'Reservations Only';
    latitude?: number;               // 위도 (지도 표시용)
    longitude?: number;              // 경도 (지도 표시용)
    rating?: number;                 // 평점 (0-5)
    reviews?: number;                // 리뷰 수
    aiInsight?: {
        summary: string;             // AI가 생성한 인사이트
        tips?: string;               // 주문 팁
        tags: string[];              // 해시태그 (예: ["Aesthetic", "Viral", "Must Visit"])
    };
    details?: {
        address?: string;            // 상세 주소
        phone?: string;              // 전화번호
        hours?: string;              // 영업 시간
        priceRange?: string;         // 가격대 (예: "₩₩")
        mustTry?: string[];          // 추천 메뉴
    };
    links?: {
        reservation?: string;        // 캐치테이블 예약 링크
        map?: string;                // 구글 맵 링크
    };
    trend: number;                   // 순위 변동 (-N: 하락, +N: 상승, 0: 유지)
}


export interface RestaurantDailyRanking {
    date: string;
    category: string;                // 'restaurants'
    items: RestaurantRankingItem[];
    updatedAt: any;
}

export interface PlaceRankingItem {
    rank: number;
    name_en: string;                 // 여행지명 (영문)
    name_ko: string;                 // 여행지명 (한글)
    location: string;                // 지역 (예: "Jongno, Seoul")
    category: string;                // 카테고리
    imageUrl: string;                // 대표 이미지 URL
    views: string;                   // 조회수 (예: "1.2M")
    likes?: string;                   // 좋아요 수 (예: "85k")
    ai_story: string;                // AI Cultural Guide (역사적 맥락, 방문 시간대)
    photo_spot: string;              // Pro Photo Spot (사진 촬영 팁)
    tags: string[];                  // 해시태그 (예: ["Royal Heritage", "Must Visit"])
    address_ko: string;              // 한국어 주소 (택시용)
    booking_url?: string;            // 우선순위 예약 링크
    klook_url?: string;              // Klook 예약 링크
    creatrip_url?: string;            // Creatrip 예약 링크
    priority_platform?: string;       // 우선순위 플랫폼 (Klook/Creatrip)
    hype_score?: number;             // AI Hype Score (1-100)
    verified_by_mix?: boolean;       // 3-Source 혼합 검증 여부
    mapx?: string;
    mapy?: string;
    content_id?: string;
    trend: number;                   // 순위 변동 (-N: 하락, +N: 상승, 0: 유지)
}

export interface PlaceDailyRanking {
    date: string;
    category: string;                // 'place'
    items: PlaceRankingItem[];
    updatedAt: any;
}
