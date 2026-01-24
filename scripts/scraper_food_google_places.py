#!/usr/bin/env python3
"""
K-Rank Food Scraper (Google Places API New)
Google Places API (New)를 사용하여 서울의 트렌딩 레스토랑을 수집하고 Firebase에 저장합니다.
"""

import os
import sys
import math
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

import requests
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai

# 환경변수 로드
load_dotenv()

# 서울 핫플레이스 좌표
HOT_AREAS = [
    {"name": "Gangnam", "location": {"latitude": 37.4979, "longitude": 127.0276}, "displayName": "Gangnam, Seoul"},
    {"name": "Seongsu", "location": {"latitude": 37.5444, "longitude": 127.0557}, "displayName": "Seongsu, Seoul"},
    {"name": "Hannam", "location": {"latitude": 37.5340, "longitude": 127.0030}, "displayName": "Hannam, Seoul"},
    {"name": "Hongdae", "location": {"latitude": 37.5563, "longitude": 126.9240}, "displayName": "Hongdae, Seoul"},
    {"name": "Dosan", "location": {"latitude": 37.5220, "longitude": 127.0390}, "displayName": "Dosan, Seoul"},
    {"name": "Itaewon", "location": {"latitude": 37.5345, "longitude": 126.9945}, "displayName": "Itaewon, Seoul"},
]

def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    if not firebase_admin._apps:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        key_path = os.path.join(project_root, 'serviceAccountKey.json')
        
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()


def initialize_gemini():
    """Gemini API 초기화"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-2.0-flash')


def calculate_hype_score(rating: float, user_ratings_total: int, recency_boost: float = 1.0) -> int:
    """Hype Score 계산"""
    if user_ratings_total == 0 or rating == 0:
        return 0
    
    rating_factor = rating / 5.0
    review_factor = min(10, math.log10(user_ratings_total + 1) * 2)
    score = int(rating_factor * review_factor * 10 * recency_boost)
    
    return min(100, score)


# estimate_wait_time 함수 제거 (불확실한 추정치 방지)


def get_status(hype_score: int) -> str:
    """Hype Score 기반 상태 추정"""
    if hype_score >= 95:
        return "Hard to Book"
    elif hype_score >= 85:
        return "Queueing"
    else:
        return "Available"


def search_nearby_places(api_key: str, location: Dict, radius: int = 1000) -> List[Dict]:
    """
    Places API (New) - Nearby Search
    https://developers.google.com/maps/documentation/places/web-service/search-nearby
    """
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.userRatingCount,places.types,places.formattedAddress,places.location,places.photos,places.internationalPhoneNumber,places.priceLevel,places.googleMapsUri"
    }
    
    data = {
        "includedTypes": ["restaurant"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": location,
                "radius": radius
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result.get("places", [])
    else:
        print(f"   ❌ API 오류: {response.status_code} - {response.text}")
        return []


def scrape_google_places_new(api_key: str, max_per_area: int = 3) -> List[Dict[str, Any]]:
    """Google Places API (New)로 트렌딩 레스토랑 수집"""
    print("🍽️  Google Places API (New)로 레스토랑 수집 시작...")
    
    all_restaurants = []
    seen_place_ids = set()
    
    for area in HOT_AREAS:
        print(f"\n📍 {area['name']} 지역 검색 중...")
        
        try:
            places = search_nearby_places(api_key, area['location'])
            print(f"   {len(places)}개 장소 발견")
            
            # 평점과 리뷰 수로 정렬
            places.sort(
                key=lambda p: (p.get('rating', 0) * math.log10(p.get('userRatingCount', 0) + 1)),
                reverse=True
            )
            
            count = 0
            for place in places[:max_per_area * 2]:
                place_id = place.get('id', '')
                
                if place_id in seen_place_ids:
                    continue
                
                seen_place_ids.add(place_id)
                
                # 기본 정보
                name = place.get('displayName', {}).get('text', 'Unknown')
                rating = place.get('rating', 0)
                reviews = place.get('userRatingCount', 0)
                
                # 리뷰가 너무 적으면 스킵
                if reviews < 50:
                    continue
                
                # Hype Score 계산
                hype_score = calculate_hype_score(rating, reviews)
                
                # 이미지 URL
                photos = place.get('photos', [])
                if photos:
                    # Photos API (New) 사용
                    photo_name = photos[0].get('name', '')
                    image_url = f"https://places.googleapis.com/v1/{photo_name}/media?maxWidthPx=1920&maxHeightPx=1080&key={api_key}"
                else:
                    image_url = "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1920&h=1080&auto=format&fit=crop"
                
                # 카테고리 추론
                types = place.get('types', [])
                if 'cafe' in types or 'bakery' in types:
                    category = 'Bakery / Cafe'
                elif 'bar' in types:
                    category = 'Bar'
                else:
                    category = 'Restaurant'
                
                # priceLevel을 priceRange로 변환
                price_level_map = {
                    'PRICE_LEVEL_FREE': '₩',
                    'PRICE_LEVEL_INEXPENSIVE': '₩',
                    'PRICE_LEVEL_MODERATE': '₩₩',
                    'PRICE_LEVEL_EXPENSIVE': '₩₩₩',
                    'PRICE_LEVEL_VERY_EXPENSIVE': '₩₩₩₩'
                }
                price_range = price_level_map.get(place.get('priceLevel', 'PRICE_LEVEL_MODERATE'), '₩₩')
                
                # 위도/경도 추출
                location_data = place.get('location', {})
                latitude = location_data.get('latitude', 0)
                longitude = location_data.get('longitude', 0)
                
                restaurant = {
                    'name': name,
                    'nameKo': name,
                    'location': area['displayName'],
                    'category': category,
                    'imageUrl': image_url,
                    'rating': rating,
                    'reviews': reviews,
                    'hypeScore': hype_score,
                    'status': get_status(hype_score),
                    'latitude': latitude,
                    'longitude': longitude,
                    'aiInsight': {
                        'summary': '',  # Gemini AI가 채움
                        'tips': '',
                        'tags': []
                    },
                    'details': {
                        'address': place.get('formattedAddress', ''),
                        'phone': place.get('internationalPhoneNumber', ''),
                        'hours': '',  # 영업시간 정보가 없으므로 빈 문자열
                        'priceRange': price_range,
                        'mustTry': []  # Gemini AI가 채울 수도 있음
                    },
                    'links': {
                        'reservation': '',  # CatchTable 링크는 별도로 설정 필요
                        'map': place.get('googleMapsUri', '')
                    },
                    'trend': 0
                }
                
                all_restaurants.append(restaurant)
                count += 1
                print(f"   ✓ {name} (Rating: {rating}, Reviews: {reviews}, Hype: {hype_score})")
                
                if count >= max_per_area:
                    break
                    
        except Exception as e:
            print(f"   ❌ {area['name']} 검색 오류: {e}")
            continue
    
    # Hype Score로 정렬 후 Top 10
    all_restaurants.sort(key=lambda x: x['hypeScore'], reverse=True)
    top_restaurants = all_restaurants[:10]
    
    # 순위 부여
    for idx, restaurant in enumerate(top_restaurants, 1):
        restaurant['rank'] = idx
    
    print(f"\n✅ 총 {len(top_restaurants)}개 레스토랑 선정 완료")
    
    return top_restaurants


async def translate_korean_names(model, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gemini AI로 레스토랑 이름을 한국어로 번역"""
    print("\n🌐 레스토랑 이름 한국어 번역 중...")
    
    names = [f"{r['rank']}. {r['name']}" for r in restaurants]
    
    prompt = f"""
Translate the following restaurant names into Korean if they are Korean restaurants.
If the restaurant is already a Korean name or a well-known Korean brand, provide the original Korean name.
If it's a foreign restaurant, keep it as is or provide a commonly used Korean transliteration.

Restaurant Names:
{chr(10).join(names)}

Response format (JSON):
{{
  "translations": [
    {{"rank": 1, "nameKo": "한국어 이름"}},
    ...
  ]
}}

JSON only.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        translations = json.loads(result_text)
        
        for trans in translations.get('translations', []):
            rank = trans.get('rank')
            name_ko = trans.get('nameKo')
            
            for restaurant in restaurants:
                if restaurant['rank'] == rank:
                    restaurant['nameKo'] = name_ko
                    break
        
        print("✅ 한국어 번역 완료")
        
    except Exception as e:
        print(f"⚠️  번역 오류: {e}")
        for restaurant in restaurants:
            restaurant['nameKo'] = restaurant['name']
    
    return restaurants


async def generate_ai_insights(model, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gemini AI로 레스토랑 태그, 설명, 팁, 추천 메뉴 생성"""
    print("\n🤖 Gemini AI로 AI Insight 생성 중...")
    
    restaurant_info = [
        f"{r['rank']}. {r['name']} - {r['category']} in {r['location']} (Rating: {r.get('rating', 0)}, Reviews: {r.get('reviews', 0)})"
        for r in restaurants
    ]
    
    prompt = f"""
Analyze each restaurant and generate comprehensive AI insights.

For each restaurant, provide:
1. 2-3 unique tags that describe its characteristics (e.g., ["Viral", "Aesthetic", "Must Visit"])
2. A brief, enticing summary (1-2 sentences) highlighting what makes it special
3. Practical tips for visiting (e.g., best time to visit, reservation tips)
4. 2-3 must-try menu items if you can infer from the restaurant type

Restaurants:
{chr(10).join(restaurant_info)}

Response format (JSON):
{{
  "insights": [
    {{
      "rank": 1,
      "tags": ["Korean BBQ", "Premium", "Date Night"],
      "summary": "Known for premium cuts and intimate atmosphere.",
      "tips": "Reservations required on weekends. Try the lunch set menu for better value.",
      "mustTry": ["Beef Short Ribs", "Marinated Pork Belly", "Cold Noodles"]
    }},
    ...
  ]
}}

JSON only.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        insights_data = json.loads(result_text)
        
        for insight in insights_data.get('insights', []):
            rank = insight.get('rank')
            tags = insight.get('tags', [])
            summary = insight.get('summary', '')
            tips = insight.get('tips', '')
            must_try = insight.get('mustTry', [])
            
            for restaurant in restaurants:
                if restaurant['rank'] == rank:
                    restaurant['aiInsight'] = {
                        'summary': summary,
                        'tips': tips,
                        'tags': tags
                    }
                    if must_try:
                        restaurant['details']['mustTry'] = must_try
                    break
        
        print("✅ AI Insight 생성 완료")
        
    except Exception as e:
        print(f"⚠️  AI Insight 생성 오류: {e}")
        for restaurant in restaurants:
            restaurant['aiInsight'] = {
                'summary': f"Popular {restaurant['category'].lower()} in {restaurant['location'].replace(', Seoul', '')}.",
                'tips': 'Visit during off-peak hours to avoid long waits.',
                'tags': ['Korean Food', 'Trending', restaurant['category']]
            }
    
    return restaurants


def save_to_firebase(db, restaurants: List[Dict[str, Any]]):
    """Firebase에 레스토랑 데이터 저장"""
    print("\n💾 Firebase에 저장 중...")
    
    today = datetime.utcnow().strftime('%Y-%m-%d')
    doc_id = f"{today}_restaurants"
    
    data = {
        'category': 'restaurants',
        'date': today,
        'lastUpdated': datetime.utcnow(),
        'items': restaurants
    }
    
    doc_ref = db.collection('daily_rankings').document(doc_id)
    doc_ref.set(data)
    
    print(f"✅ {len(restaurants)}개 레스토랑 저장 완료 (문서 ID: {doc_id})")


async def main():
    """메인 함수"""
    print("🍜 K-Rank Food Scraper (Google Places API New)")
    print("=" * 60)
    
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("❌ GOOGLE_PLACES_API_KEY not found in environment")
        sys.exit(1)
    
    db = initialize_firebase()
    print("✅ Firebase 초기화 완료")
    
    try:
        model = initialize_gemini()
        print("✅ Gemini AI 초기화 완료")
    except Exception as e:
        print(f"⚠️  Gemini 초기화 실패: {e}")
        model = None
    
    # 1. Google Places에서 레스토랑 수집
    restaurants = scrape_google_places_new(api_key, max_per_area=3)
    
    if len(restaurants) == 0:
        print("❌ 레스토랑을 찾지 못했습니다")
        sys.exit(1)
    
    # 2. Gemini AI로 한국어 이름 번역
    if model:
        restaurants = await translate_korean_names(model, restaurants)
    
    # 3. Gemini AI로 AI Insight 생성
    if model:
        restaurants = await generate_ai_insights(model, restaurants)
    
    # 4. Firebase에 저장
    save_to_firebase(db, restaurants)
    
    print("\n✅ Food 스크래퍼 완료!")
    print(f"총 {len(restaurants)}개 레스토랑 업데이트")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
