#!/usr/bin/env python3
"""
K-Rank Food Scraper (Google Places API New)
Google Places API (New)를 사용하여 서울의 트렌딩 레스토랑을 수집하고 Firebase에 저장합니다.
"""

import os
import sys
import math
import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

import requests
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai

# 환경변수 로드
load_dotenv()

# 개발 모드 설정
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'
WRITE_TO_FIRESTORE = os.getenv('WRITE_TO_FIRESTORE', 'false').lower() == 'true'
DEV_LIMIT = int(os.getenv('DEV_LIMIT', '5'))

# 서울 핫플레이스 좌표
HOT_AREAS = [
    {"name": "Gangnam", "location": {"latitude": 37.4979, "longitude": 127.0276}, "displayName": "Gangnam, Seoul"},
    {"name": "Seongsu", "location": {"latitude": 37.5444, "longitude": 127.0557}, "displayName": "Seongsu, Seoul"},
    {"name": "Hannam", "location": {"latitude": 37.5340, "longitude": 127.0030}, "displayName": "Hannam, Seoul"},
    {"name": "Hongdae", "location": {"latitude": 37.5563, "longitude": 126.9240}, "displayName": "Hongdae, Seoul"},
    {"name": "Dosan", "location": {"latitude": 37.5220, "longitude": 127.0390}, "displayName": "Dosan, Seoul"},
    {"name": "Itaewon", "location": {"latitude": 37.5345, "longitude": 126.9945}, "displayName": "Itaewon, Seoul"},
]

CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_cache.json')

def load_cache() -> Dict[str, Any]:
    """로컬 캐시 파일 로드"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  캐시 로드 오류: {e}")
    return {}

def save_cache(cache: Dict[str, Any]):
    """로컬 캐시 파일 저장"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  캐시 저장 오류: {e}")

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

def get_status(hype_score: int) -> str:
    """Hype Score 기반 상태 추정"""
    if hype_score >= 95:
        return "Hard to Book"
    elif hype_score >= 85:
        return "Queueing"
    else:
        return "Available"

def search_nearby_places(api_key: str, location: Dict, radius: int = 1000) -> List[Dict]:
    """Places API (New) - Nearby Search"""
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
        print(f"   ❌ API 오류: {response.status_code}")
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
            for place in places[:max_per_area * 3]: # 여유 있게 수집
                place_id = place.get('id', '')
                
                if place_id in seen_place_ids:
                    continue
                
                seen_place_ids.add(place_id)
                
                # 기본 정보
                name = place.get('displayName', {}).get('text', 'Unknown')
                rating = place.get('rating', 0)
                reviews = place.get('userRatingCount', 0)
                
                # 리뷰가 너무 적으면 스킵 (검증 강화)
                if reviews < 50:
                    continue
                
                # Hype Score 계산
                hype_score = calculate_hype_score(rating, reviews)
                
                # 이미지 URL
                photos = place.get('photos', [])
                if photos:
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
                
                price_level_map = {
                    'PRICE_LEVEL_FREE': '₩',
                    'PRICE_LEVEL_INEXPENSIVE': '₩',
                    'PRICE_LEVEL_MODERATE': '₩₩',
                    'PRICE_LEVEL_EXPENSIVE': '₩₩₩',
                    'PRICE_LEVEL_VERY_EXPENSIVE': '₩₩₩₩'
                }
                price_range = price_level_map.get(place.get('priceLevel', 'PRICE_LEVEL_MODERATE'), '₩₩')
                
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
                        'summary': '',
                        'tips': '',
                        'tags': []
                    },
                    'details': {
                        'address': place.get('formattedAddress', ''),
                        'phone': place.get('internationalPhoneNumber', ''),
                        'hours': '',
                        'priceRange': price_range,
                        'mustTry': []
                    },
                    'links': {
                        'reservation': '',
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
    
    # Hype Score로 정렬 후 Top 30
    all_restaurants.sort(key=lambda x: x['hypeScore'], reverse=True)
    limit = 30
    if DEV_MODE:
        limit = DEV_LIMIT * 5 # 지역별 수집량을 고려하여 여유 있게
        
    top_restaurants = all_restaurants[:limit]
    
    # 순위 부여
    for idx, restaurant in enumerate(top_restaurants, 1):
        restaurant['rank'] = idx
    
    print(f"\n✅ 총 {len(top_restaurants)}개 레스토랑 선정 완료")
    
    return top_restaurants

async def analyze_restaurants_batch(model: genai.GenerativeModel, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gemini AI로 레스토랑 이름 번역 및 인사이트 통합 생성"""
    print("\n🌐 Gemini AI로 이름 번역 및 인사이트 생성 중 (Batch Processing)...")
    
    cache = load_cache()
    to_process = []
    
    for r in restaurants:
        cache_key = f"restaurant_{r['name']}"
        if cache_key in cache:
            cached_data = cache[cache_key]
            r['nameKo'] = cached_data.get('nameKo', r['name'])
            r['aiInsight'] = cached_data.get('aiInsight', r['aiInsight'])
            r['details']['mustTry'] = cached_data.get('mustTry', [])
            print(f"  ⚡ 캐시 사용")
        else:
            to_process.append(r)
            
    if not to_process:
        print("✅ 모든 레스토랑이 캐시되어 있습니다.")
        return restaurants

    print(f"  🤖 {len(to_process)}개 레스토랑 AI 분석 요청 중...")
    
    # 10개씩 배치 처리
    batch_size = 10
    for i in range(0, len(to_process), batch_size):
        batch = to_process[i:i+batch_size]
        
        info_list = [
            f"Rank {r['rank']}: {r['name']} ({r['category']} in {r['location']})"
            for r in batch
        ]
        
        prompt = f"""
Analyze the following restaurants in Seoul and provide translations and insights.

RESTAURANTS:
{chr(10).join(info_list)}

FOR EACH RESTAURANT, PROVIDE:
1. nameKo: The common Korean name of the restaurant.
2. summary: A 1-2 sentence enticing description in English.
3. tips: Practical visiting tip in English.
4. tags: 2-3 short hashtags (e.g., ["Viral", "Aesthetic"]).
5. mustTry: 2-3 recommended menu items in English.

RESPONSE FORMAT (JSON):
{{
  "results": [
    {{
      "rank": 1,
      "nameKo": "한국어 이름",
      "summary": "...",
      "tips": "...",
      "tags": ["...", "..."],
      "mustTry": ["...", "..."]
    }},
    ...
  ]
}}

JSON ONLY.
        """
        
        try:
            response = await model.generate_content_async(prompt)
            result_text = response.text.strip()
            
            # JSON 클렌징
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(result_text)
            results = data.get('results', [])
            
            for res in results:
                rank = res.get('rank')
                for r in batch:
                    if r['rank'] == rank:
                        r['nameKo'] = res.get('nameKo', r['name'])
                        r['aiInsight'] = {
                            'summary': res.get('summary', ''),
                            'tips': res.get('tips', ''),
                            'tags': res.get('tags', [])
                        }
                        r['details']['mustTry'] = res.get('mustTry', [])
                        
                        # 캐시 저장
                        cache_key = f"restaurant_{r['name']}"
                        cache[cache_key] = {
                            'nameKo': r['nameKo'],
                            'aiInsight': r['aiInsight'],
                            'mustTry': r['details']['mustTry'],
                            'updatedAt': datetime.now(timezone.utc).isoformat()
                        }
                        break
            
            print(f"  ✅ 배치 {i//batch_size + 1} 완료")
            save_cache(cache)
            
        except Exception as e:
            print(f"  ❌ 배치 {i//batch_size + 1} 오류: {e}")
            # 폴백
            for r in batch:
                r['nameKo'] = r['name']
                r['aiInsight'] = {
                    'summary': f"Popular {r['category'].lower()} in {r['location']}.",
                    'tips': "Check maps for busy hours.",
                    'tags': ["Seoul", r['category']]
                }

    return restaurants

async def calculate_restaurant_trends(db: firestore.client, current_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """레스토랑 순위 변동(Trend) 계산"""
    print("\n📈 순위 변동 계산 중...")
    
    # 어제 날짜 확인
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
    doc_id = f"{yesterday}_restaurants"
    
    try:
        prev_doc = db.collection('daily_rankings').document(doc_id).get()
        if not prev_doc.exists:
            print(f"  ℹ️ 어제 데이터({yesterday})가 없어 변동을 0으로 설정합니다.")
            return current_items
            
        prev_data = prev_doc.to_dict()
        prev_items = prev_data.get('items', [])
        
        # 이전 순위 매핑
        prev_rank_map = {item['name']: item['rank'] for item in prev_items}
        
        for item in current_items:
            prev_rank = prev_rank_map.get(item['name'])
            if prev_rank:
                item['trend'] = prev_rank - item['rank']
            else:
                item['trend'] = 0 # 신규 진입은 0으로 표시 (또는 다른 로직)
                
        print("  ✅ 변동 계산 완료")
    except Exception as e:
        print(f"  ⚠️  변동 계산 오류: {e}")
        
    return current_items

def save_to_firebase(db, restaurants: List[Dict[str, Any]]):
    """Firebase에 레스토랑 데이터 저장"""
    print("\n💾 Firebase에 저장 중...")
    
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    doc_id = f"{today}_restaurants"
    
    data = {
        'category': 'restaurants',
        'date': today,
        'lastUpdated': datetime.now(timezone.utc),
        'items': restaurants
    }
    
    if DEV_MODE and not WRITE_TO_FIRESTORE:
        print(f"🧪  [DEV_MODE] Firebase 저장을 건너뜁니다.")
        print(f"  📊 {len(data['items'])}개 레스토랑 준비됨")
        return

    doc_ref = db.collection('daily_rankings').document(doc_id)
    doc_ref.set(data)
    
    print(f"✅ {len(restaurants)}개 레스토랑 저장 완료 (문서 ID: {doc_id})")

async def main():
    """메인 함수"""
    print("\n" + "=" * 60)
    print("🍜 K-Rank Food Scraper (Google Places API New)")
    print(f"MODE: {'DEVELOPMENT' if DEV_MODE else 'PRODUCTION'}")
    print("=" * 60)
    
    api_key = os.getenv('GOOGLE_PLACES_API_KEY') or os.getenv('GOOGLE_MAPS_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GOOGLE_PLACES_API_KEY, GOOGLE_MAPS_API_KEY 또는 GEMINI_API_KEY를 찾을 수 없습니다.")
        sys.exit(1)
    
    db = initialize_firebase()
    
    try:
        model = initialize_gemini()
    except Exception as e:
        print(f"⚠️  Gemini 초기화 실패: {e}")
        model = None
    
    # 1. Google Places에서 레스토랑 수집
    max_per_area = 2 if DEV_MODE else 7
    restaurants = scrape_google_places_new(api_key, max_per_area=max_per_area)
    
    if not restaurants:
        print("\n❌ [CRITICAL] 수집된 레스토랑 데이터가 0개입니다.")
        sys.exit(1)
    
    # 2. Gemini AI 분석 (번역 + 인사이트)
    if model:
        restaurants = await analyze_restaurants_batch(model, restaurants)
    
    # 3. 트렌드 계산
    restaurants = await calculate_restaurant_trends(db, restaurants)
    
    # 4. Firebase에 저장
    save_to_firebase(db, restaurants)
    
    print("\n✅ Food 스크래퍼 완료!")
    print(f"총 {len(restaurants)}개 레스토랑 처리 완료")

if __name__ == '__main__':
    asyncio.run(main())
