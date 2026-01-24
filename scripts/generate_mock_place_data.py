#!/usr/bin/env python3
"""
K-Rank Place Mock Data Generator
Frontend 테스트를 위한 Mock 여행지 데이터 생성
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# 환경변수 로드
load_dotenv()

# Firebase 초기화
def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    if not firebase_admin._apps:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        key_path = os.path.join(project_root, 'serviceAccountKey.json')
        
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()


# Mock 데이터
MOCK_PLACES = [
    {
        'rank': 1,
        'name': 'Gyeongbokgung Palace',
        'nameKo': '경복궁',
        'location': 'Seoul',
        'category': 'Culture',
        'imageUrl': 'https://images.unsplash.com/photo-1541432923778-36bc64949430?q=80&w=1200&auto=format&fit=crop',
        'views': '1.2M',
        'likes': '85k',
        'aiStory': 'This was the main royal palace of the Joseon Dynasty. Visiting at 10 AM or 2 PM allows you to see the Changing of the Guard ceremony.',
        'photoSpot': 'Stand at the center of Gwanghwamun Gate for a perfectly symmetrical shot of the palace against Bugaksan Mountain.',
        'tags': ['Royal Heritage', 'Must Visit', 'Hanbok Friendly'],
        'address': '서울특별시 종로구 사직로 161',
        'bookingUrl': 'https://www.klook.com/en-US/activity/1362-gyeongbokgung-palace-admission-seoul/',
        'latitude': 37.5796,
        'longitude': 126.977,
        'trend': 0
    },
    {
        'rank': 2,
        'name': 'Haeundae Blue Line Park',
        'nameKo': '해운대 블루라인파크',
        'location': 'Busan',
        'category': 'Modern',
        'imageUrl': 'https://images.unsplash.com/photo-1590604166539-ec965a9478f7?q=80&w=1200&auto=format&fit=crop',
        'views': '890k',
        'likes': '62k',
        'aiStory': 'A stunning coastal railway transformed into a tourist attraction. The colorful Beach Train offers the most romantic view of the East Sea.',
        'photoSpot': 'Inside the Sky Capsule, time your shutter as another capsule passes by with the ocean in the background.',
        'tags': ['Ocean View', 'Romantic', 'Busan Hotspot'],
        'address': '부산광역시 해운대구 청사포로 116',
        'bookingUrl': 'https://www.klook.com/en-US/activity/51898-haeundae-blue-line-park/',
        'latitude': 35.1585,
        'longitude': 129.1805,
        'trend': 2
    },
    {
        'rank': 3,
        'name': 'Hallasan National Park',
        'nameKo': '한라산국립공원',
        'location': 'Jeju',
        'category': 'Nature',
        'imageUrl': 'https://images.unsplash.com/photo-1621516104847-786d79e8e53d?q=80&w=1200&auto=format&fit=crop',
        'views': '750k',
        'likes': '58k',
        'aiStory': "South Korea's highest peak and a UNESCO World Heritage site. The Baekrokdam crater lake at the summit is a spiritual symbol of Jeju.",
        'photoSpot': "The Yeongsil Trail's 'Byeongpung Rocks' offer a majestic view of the clouds below your feet.",
        'tags': ['Hiking', 'UNESCO', 'Nature Lover'],
        'address': '제주특별자치도 제주시 1100로 2070-61',
        'bookingUrl': 'https://www.klook.com/en-US/activity/2746-hallasan-national-park-jeju/',
        'latitude': 33.3617,
        'longitude': 126.5292,
        'trend': -1
    },
    {
        'rank': 4,
        'name': 'Bukchon Hanok Village',
        'nameKo': '북촌한옥마을',
        'location': 'Seoul',
        'category': 'Culture',
        'imageUrl': 'https://images.unsplash.com/photo-1583492547988-cf2c4cb54c16?q=80&w=1200&auto=format&fit=crop',
        'views': '680k',
        'likes': '51k',
        'aiStory': 'A traditional Korean village with over 600 years of history. Walk through alleys lined with hanok houses to experience old Seoul.',
        'photoSpot': 'The viewpoint at the top of the hill offers a stunning view of hanok rooftops with Namsan Tower in the background.',
        'tags': ['Traditional Village', 'Hanbok Zone', 'Photo Hotspot'],
        'address': '서울특별시 종로구 계동길 37',
        'bookingUrl': 'https://www.klook.com/en-US/activity/bukchon-hanok-village-seoul/',
        'latitude': 37.5826,
        'longitude': 126.9834,
        'trend': 1
    },
    {
        'rank': 5,
        'name': 'Nami Island',
        'nameKo': '남이섬',
        'location': 'Gangwon',
        'category': 'Nature',
        'imageUrl': 'https://images.unsplash.com/photo-1583424113672-ea9c98d76c94?q=80&w=1200&auto=format&fit=crop',
        'views': '620k',
        'likes': '47k',
        'aiStory': 'Famous for its beautiful tree-lined roads, especially stunning in autumn. It became a global attraction after the K-drama Winter Sonata was filmed here.',
        'photoSpot': 'The metasequoia tree lane creates a natural tunnel perfect for romantic photos, best during golden hour.',
        'tags': ['K-Drama Location', 'Autumn Colors', 'Romantic'],
        'address': '강원도 춘천시 남산면 남이섬길 1',
        'bookingUrl': 'https://www.klook.com/en-US/activity/1368-nami-island-rail-bike-seoul/',
        'latitude': 37.7911,
        'longitude': 127.5267,
        'trend': 0
    }
]


def save_mock_data():
    """Mock 데이터를 Firestore에 저장"""
    db = initialize_firebase()
    
    try:
        # 현재 날짜 (UTC)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        doc_id = f"{today}_place"
        
        print(f"\n💾 Mock 데이터 Firestore 저장 중... (문서 ID: {doc_id})")
        
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc_ref.set({
            'date': today,
            'category': 'place',
            'items': MOCK_PLACES,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        print(f"✅ Mock 데이터 저장 완료! ({len(MOCK_PLACES)}개 여행지)")
        print(f"📄 문서 경로: daily_rankings/{doc_id}")
        
        print("\n📋 저장된 여행지:")
        for place in MOCK_PLACES:
            print(f"  {place['rank']}. {place['name']} ({place['nameKo']}) - {place['category']}")
        
    except Exception as e:
        print(f"❌ Firestore 저장 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🗺️ K-RANK PLACE MOCK DATA GENERATOR")
    print("=" * 60)
    save_mock_data()
    print("\n✅ 완료! http://localhost:3000/place 에서 확인하세요.")
    print("=" * 60)
