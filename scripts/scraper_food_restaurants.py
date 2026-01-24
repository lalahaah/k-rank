#!/usr/bin/env python3
"""
K-Rank Restaurant Scraper (Plan B)
네이버 맵을 메인 소스로 활용하여 서울 인기 레스토랑 랭킹을 수집합니다.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
import json

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# Google Gemini AI
import google.generativeai as genai

# 테스트 데이터
MOCK_RESTAURANTS = [
    {
        "name": "London Bagel Museum",
        "nameKo": "런던 베이글 뮤지엄",
        "location": "Dosan, Seoul",
        "category": "Bakery / Cafe",
        "imageUrl": "https://images.unsplash.com/photo-1585478259715-876a6a81fc08?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "120 min",
        "hypeScore": 98,
        "status": "Hard to Book",
        "naverSaves": 15000,
        "googleRating": 4.8,
    },
    {
        "name": "Geumdwajigonsik",
        "nameKo": "금돼지곤식",
        "location": "Sindang, Seoul",
        "category": "K-BBQ (Pork)",
        "imageUrl": "https://images.unsplash.com/photo-1599307767316-776533da941c?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "90 min",
        "hypeScore": 95,
        "status": "Queueing",
        "naverSaves": 12000,
        "googleRating": 4.7,
    },
    {
        "name": "Nudake",
        "nameKo": "누데이크",
        "location": "Seongsu, Seoul",
        "category": "Artistic Cafe",
        "imageUrl": "https://images.unsplash.com/photo-1551024506-0bccd828d307?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "30 min",
        "hypeScore": 92,
        "status": "Available",
        "naverSaves": 10000,
        "googleRating": 4.6,
    },
    {
        "name": "Tuk Tuk Noodle Thai",
        "nameKo": "뚝뚝누들타이",
        "location": "Hannam, Seoul",
        "category": "Thai Cuisine",
        "imageUrl": "https://images.unsplash.com/photo-1559314809-0d155014e29e?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "60 min",
        "hypeScore": 89,
        "status": "Queueing",
        "naverSaves": 8500,
        "googleRating": 4.5,
    },
    {
        "name": "Onion Anguk",
        "nameKo": "어니언 안국점",
        "location": "Anguk, Seoul",
        "category": "Bakery / Cafe",
        "imageUrl": "https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "45 min",
        "hypeScore": 87,
        "status": "Available",
        "naverSaves": 9000,
        "googleRating": 4.6,
    },
    {
        "name": "Hanilkwan",
        "nameKo": "한일관",
        "location": "Myeongdong, Seoul",
        "category": "Traditional Korean",
        "imageUrl": "https://images.unsplash.com/photo-1580554530778-ca36943938b2?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "40 min",
        "hypeScore": 85,
        "status": "Available",
        "naverSaves": 7500,
        "googleRating": 4.5,
    },
    {
        "name": "Felt",
        "nameKo": "펠트",
        "location": "Seongsu, Seoul",
        "category": "Fusion Restaurant",
        "imageUrl": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "50 min",
        "hypeScore": 84,
        "status": "Queueing",
        "naverSaves": 7000,
        "googleRating": 4.4,
    },
    {
        "name": "Plant Cafe & Kitchen",
        "nameKo": "플랜트 카페 앤 키친",
        "location": "Itaewon, Seoul",
        "category": "Vegan / Healthy",
        "imageUrl": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "20 min",
        "hypeScore": 82,
        "status": "Available",
        "naverSaves": 6500,
        "googleRating": 4.5,
    },
    {
        "name": "Egg Drop",
        "nameKo": "에그드롭",
        "location": "Hongdae, Seoul",
        "category": "Sandwich / Brunch",
        "imageUrl": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": "35 min",
        "hypeScore": 80,
        "status": "Available",
        "naverSaves": 6000,
        "googleRating": 4.3,
    },
    {
        "name": "Jungsik",
        "nameKo": "정식당",
        "location": "Gangnam, Seoul",
        "category": "Fine Dining / Michelin",
        "imageUrl": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?q=80&w=1920&h=1080&auto=format&fit=crop",
        "waitTime": None,
        "hypeScore": 95,
        "status": "Reservations Only",
        "naverSaves": 11000,
        "googleRating": 4.8,
    },
]


def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    try:
        if not firebase_admin._apps:
            # serviceAccountKey.json 파일 경로 확인
            cred_path = os.path.join(
                os.path.dirname(__file__), '..', 'serviceAccountKey.json'
            )
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        sys.exit(1)


def initialize_gemini():
    """Gemini API 초기화"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        print("✅ Gemini API initialized successfully")
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"❌ Gemini API initialization failed: {e}")
        return None


def calculate_nik_score(restaurant: Dict[str, Any]) -> int:
    """
    NIK Index 계산 (Plan B 가중치)
    - 네이버 저장 수: 50%
    - 구글 평점: 20%
    - 소셜 속도: 20% (현재는 고정값 사용)
    - 에디토리얼: 10% (고정값)
    """
    # 네이버 저장 수를 0-50 범위로 정규화
    naver_score = min((restaurant.get('naverSaves', 0) / 15000) * 50, 50)
    
    # 구글 평점을 0-20 범위로 변환 (5점 만점)
    google_score = (restaurant.get('googleRating', 4.0) / 5.0) * 20
    
    # 소셜 속도 (임시로 15점 고정)
    social_score = 15
    
    # 에디토리얼 점수 (임시로 8점 고정)
    editorial_score = 8
    
    total = int(naver_score + google_score + social_score + editorial_score)
    return min(total, 100)


def generate_ai_insights(model, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gemini AI로 레스토랑 인사이트 생성"""
    if not model:
        print("⚠️  Gemini model not available, using default insights")
        return add_default_insights(restaurants)
    
    enriched_restaurants = []
    
    for restaurant in restaurants:
        try:
            prompt = f"""
You are a Seoul food trend expert. Analyze this restaurant and provide insights for international tourists.

Restaurant: {restaurant['name']} ({restaurant['nameKo']})
Category: {restaurant['category']}
Location: {restaurant['location']}
Hype Score: {restaurant['hypeScore']}

Provide a JSON response with:
1. "summary": A 1-2 sentence insight about why this place is hot right now (in English)
2. "tips": A practical order tip or visit recommendation (in English)
3. "tags": 3-4 relevant hashtags (e.g., "Aesthetic", "Viral", "Must Visit", "Instagram Worthy", "Hidden Gem")

Response format:
{{"summary": "...", "tips": "...", "tags": ["...", "..."]}}
"""
            
            response = model.generate_content(prompt)
            
            # JSON 파싱
            try:
                ai_data = json.loads(response.text)
                restaurant['aiInsight'] = {
                    'summary': ai_data.get('summary', 'A hotspot in Seoul.'),
                    'tips': ai_data.get('tips', 'Visit early to avoid crowds.'),
                    'tags': ai_data.get('tags', ['Trending', 'Popular'])
                }
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본값 사용
                restaurant['aiInsight'] = {
                    'summary': f"One of the hottest {restaurant['category']} spots in {restaurant['location']}.",
                    'tips': "Visit during off-peak hours for shorter wait times.",
                    'tags': ["Trending", "Popular", "Local Favorite"]
                }
            
            enriched_restaurants.append(restaurant)
            time.sleep(1)  # API 호출 간격
            
        except Exception as e:
            print(f"⚠️  AI insight generation failed for {restaurant['name']}: {e}")
            restaurant['aiInsight'] = {
                'summary': f"A popular {restaurant['category']} in {restaurant['location']}.",
                'tips': "Check reviews before visiting.",
                'tags': ["Seoul Hotspot"]
            }
            enriched_restaurants.append(restaurant)
    
    return enriched_restaurants


def add_default_insights(restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """기본 인사이트 추가 (Gemini 사용 불가 시)"""
    default_insights = {
        "London Bagel Museum": {
            "summary": "The 'Potato Cheese Bagel' is the absolute must-order. Arrive before 8 AM for a better chance at the limited spring onion bagel.",
            "tips": "Try the signature potato cheese bagel, it sells out fast!",
            "tags": ["Aesthetic", "Viral", "Open Run"]
        },
        "Geumdwajigonsik": {
            "summary": "Famous for being BTS's favorite spot. Their gold-standard pork belly has a unique texture. High-end service included.",
            "tips": "Order the premium pork belly set for the full experience.",
            "tags": ["Michelin Guide", "BTS Favorite", "Premium"]
        },
        "Nudake": {
            "summary": "Known for the 'Peak Cake'. It's more of an art gallery than a cafe. Perfect for your Instagram feed.",
            "tips": "Don't miss the signature Peak Cake for amazing photos!",
            "tags": ["Seongsu Hot", "Unique", "Fashionable"]
        },
    }
    
    for restaurant in restaurants:
        name = restaurant['name']
        if name in default_insights:
            restaurant['aiInsight'] = default_insights[name]
        else:
            restaurant['aiInsight'] = {
                "summary": f"A trending {restaurant['category']} spot in {restaurant['location']}.",
                "tips": "Visit during off-peak hours for the best experience.",
                "tags": ["Seoul Eats", "Trending", "Local Favorite"]
            }
    
    return restaurants


def calculate_trends(db, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """이전 랭킹과 비교하여 트렌드 계산"""
    try:
        # 어제 날짜 구하기
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 어제 데이터 가져오기
        doc_ref = db.collection('daily_rankings').document(f'{yesterday}-restaurants')
        doc = doc_ref.get()
        
        if not doc.exists:
            # 첫 실행이거나 어제 데이터 없음
            for restaurant in restaurants:
                restaurant['trend'] = 0
            return restaurants
        
        # 어제 랭킹 맵 생성
        yesterday_data = doc.to_dict()
        yesterday_ranks = {item['name']: item['rank'] for item in yesterday_data.get('items', [])}
        
        # 트렌드 계산
        for restaurant in restaurants:
            name = restaurant['name']
            current_rank = restaurant['rank']
            
            if name in yesterday_ranks:
                previous_rank = yesterday_ranks[name]
                # 순위가 올라가면 양수, 내려가면 음수
                trend = previous_rank - current_rank
                restaurant['trend'] = trend
            else:
                # 새로 진입한 레스토랑
                restaurant['trend'] = 0
        
        return restaurants
        
    except Exception as e:
        print(f"⚠️  Trend calculation failed: {e}")
        for restaurant in restaurants:
            restaurant['trend'] = 0
        return restaurants


def save_to_firebase(db, restaurants: List[Dict[str, Any]]):
    """Firebase에 데이터 저장"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        doc_ref = db.collection('daily_rankings').document(f'{today}-restaurants')
        
        data = {
            'date': today,
            'category': 'restaurants',
            'items': restaurants,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(data)
        print(f"✅ Saved {len(restaurants)} restaurants to Firebase")
        
    except Exception as e:
        print(f"❌ Failed to save to Firebase: {e}")
        raise


async def main():
    """메인 함수"""
    print("🍜 Starting K-Food Restaurant Scraper (Plan B)")
    print("=" * 50)
    
    # 1. Firebase 초기화
    initialize_firebase()
    db = firestore.client()
    
    # 2. Gemini 초기화
    model = initialize_gemini()
    
    # 3. Mock 데이터 사용 (현재는 실제 크롤링 대신)
    print("\n📊 Using mock restaurant data...")
    restaurants = MOCK_RESTAURANTS.copy()
    
    # 4. NIK Score 계산
    print("\n🔢 Calculating NIK scores...")
    for restaurant in restaurants:
        restaurant['hypeScore'] = calculate_nik_score(restaurant)
    
    # 5. NIK Score로 정렬 및 순위 부여
    restaurants.sort(key=lambda x: x['hypeScore'], reverse=True)
    for idx, restaurant in enumerate(restaurants, start=1):
        restaurant['rank'] = idx
    
    # 6. AI 인사이트 생성
    print("\n🤖 Generating AI insights...")
    restaurants = generate_ai_insights(model, restaurants)
    
    # 7. 트렌드 계산
    print("\n📈 Calculating trends...")
    restaurants = calculate_trends(db, restaurants)
    
    # 8. 상세 정보 추가
    print("\n📍 Adding detailed information...")
    for restaurant in restaurants:
        # 추가 이미지 URL (각 레스토랑마다 2-3개 추가) - 고해상도
        category_images = {
            "Bakery / Cafe": [
                "https://images.unsplash.com/photo-1509440159596-0249088772ff?q=80&w=1920&h=1080&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1555507036-ab1f4038808a?q=80&w=1920&h=1080&auto=format&fit=crop"
            ],
            "K-BBQ (Pork)": [
                "https://images.unsplash.com/photo-1568969546882-0285da2c3be6?q=80&w=1920&h=1080&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1582169296194-e4d644c48063?q=80&w=1920&h=1080&auto=format&fit=crop"
            ],
            "Artistic Cafe": [
                "https://images.unsplash.com/photo-1549490349-8643362247b5?q=80&w=1920&h=1080&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1519915212116-7cfef71f1d3e?q=80&w=1920&h=1080&auto=format&fit=crop"
            ],
            "default": [
                "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1920&h=1080&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?q=80&w=1920&h=1080&auto=format&fit=crop"
            ]
        }
        
        restaurant['images'] = category_images.get(restaurant['category'], category_images['default'])
        
        # 상세 정보 추가
        restaurant['details'] = {
            'address': f"{restaurant['location']}, Seoul, South Korea",
            'phone': "+82-2-1234-5678",  # Mock 전화번호
            'hours': "Daily 10:00 AM - 10:00 PM",
            'priceRange': "₩₩" if "Fine Dining" in restaurant['category'] else "₩"
        }
        
        # Must Try 메뉴 추가
        must_try_menus = {
            "London Bagel Museum": ["Potato Cheese Bagel", "Spring Onion Bagel", "Cream Cheese"],
            "Geumdwajigonsik": ["Premium Pork Belly", "Grilled Pork Set", "Kimchi Stew"],
            "Nudake": ["Peak Cake", "Signature Coffee", "Seasonal Dessert"],
            "Tuk Tuk Noodle Thai": ["Pad Thai", "Green Curry", "Mango Sticky Rice"],
            "Onion Anguk": ["Garlic Cream Bread", "Croissant", "Americano"],
            "Hanilkwan": ["Bulgogi", "Bibimbap", "Galbi"],
            "Felt": ["Truffle Pasta", "Wagyu Steak", "Seasonal Salad"],
            "Plant Cafe & Kitchen": ["Vegan Buddha Bowl", "Green Smoothie", "Avocado Toast"],
            "Egg Drop": ["Signature Egg Sandwich", "Bacon Egg Drop", "Hash Brown"],
            "Jungsik": ["Tasting Menu", "Seasonal Korean Tasting", "Premium Wine Pairing"]
        }
        
        restaurant['details']['mustTry'] = must_try_menus.get(restaurant['name'], ["House Special", "Chef's Recommendation"])
    
    # 9. 링크 추가
    print("\n🔗 Adding links...")
    for restaurant in restaurants:
        restaurant['links'] = {
            'reservation': 'https://catchtable.co.kr/',
            'map': f'https://www.google.com/maps/search/?api=1&query={restaurant["name"]}+Seoul'
        }
    
    # 10. Firebase 저장
    print("\n💾 Saving to Firebase...")
    save_to_firebase(db, restaurants)
    
    print("\n✅ Restaurant scraper completed successfully!")
    print(f"Total restaurants: {len(restaurants)}")



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
