#!/usr/bin/env python3
"""
K-Rank Place Scraper
한국관광공사 TourAPI를 활용하여 여행지 랭킹을 크롤링하고 Firebase에 저장합니다.
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
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

# Gemini API 초기화
def initialize_gemini():
    """Gemini API 초기화"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-2.0-flash')


def fetch_tour_places(api_key: str, max_items: int = 100) -> List[Dict[str, Any]]:
    """
    TourAPI에서 여행지 데이터 수집
    
    Args:
        api_key: TourAPI 키
        max_items: 수집할 최대 아이템 수
        
    Returns:
        여행지 데이터 리스트
    """
    print("\n🗺️ TourAPI에서 여행지 데이터 수집 중...")
    
    places = []
    
    # TourAPI 지역 기반 관광정보 조회 API (KorService2)
    # API 이름: areaBasedList2 (숫자 2 필수!)
    # contentTypeId=12: 관광지
    base_url = "https://apis.data.go.kr/B551011/KorService2/areaBasedList2"
    
    try:
        # serviceKey를 직접 URL에 포함
        # arrange=Q: 수정일순 정렬 (이미지 우선) - 최근 업데이트된 인기 장소 우선
        # listYN 파라미터 제거 (areaBasedList2에서는 지원하지 않음)
        url = f"{base_url}?serviceKey={api_key}&numOfRows={min(max_items, 100)}&pageNo=1&MobileOS=ETC&MobileApp=K-Rank&contentTypeId=12&arrange=Q&_type=json"
        
        print(f"📡 TourAPI (areaBasedList2) 호출 중... (최대 {max_items}개)")
        print(f"🔑 API Key: {api_key[:10]}...{api_key[-10:]}")
        print(f"🌐 Endpoint: {base_url}")
        
        response = requests.get(url, timeout=30)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ TourAPI 요청 실패: HTTP {response.status_code}")
            print(f"📄 응답 내용:\n{response.text[:1000]}")
            
            # 일반적인 TourAPI 오류 해결 팁
            if response.status_code == 500:
                print("\n💡 TourAPI HTTP 500 오류 해결 방법:")
                print("1. API 키 형식 확인:")
                print("   - 디코딩된 키를 사용하세요 (URL 인코딩 X)")
                print("   - 공백이나 개행문자 포함 여부 확인")
                print("2. 공공데이터포털에서 활용신청 승인 확인")
                print("3. API 트래픽 제한 확인 (일일 1000건)")
                print("4. contentTypeId=12가 지원되는지 확인")
            
            return places
            
        data = response.json()
        
        # 응답 구조 확인
        if 'response' not in data:
            print("❌ TourAPI 응답 형식 오류: 'response' 키 없음")
            print(f"📄 전체 응답:\n{json.dumps(data, indent=2, ensure_ascii=False)[:1000]}")
            return places
            
        response_data = data['response']
        
        result_code = response_data.get('header', {}).get('resultCode')
        result_msg = response_data.get('header', {}).get('resultMsg', 'Unknown error')
        
        print(f"📋 API 응답 코드: {result_code}")
        print(f"📋 API 응답 메시지: {result_msg}")
        
        if result_code != '0000':
            print(f"❌ TourAPI 오류: {result_msg}")
            
            # 오류 코드별 가이드
            error_guides = {
                '00': '정상 처리',
                '01': 'APPLICATION_ERROR',
                '02': 'DB_ERROR',
                '03': 'NODATA_ERROR',
                '04': 'HTTP_ERROR',
                '05': 'SERVICETIMEOUT_ERROR',
                '10': 'INVALID_REQUEST_PARAMETER_ERROR',
                '11': 'NO_MANDATORY_REQUEST_PARAMETERS_ERROR',
                '12': 'NO_OPENAPI_SERVICE_ERROR',
                '20': 'SERVICE_ACCESS_DENIED_ERROR',
                '22': 'LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR',
                '30': 'SERVICE_KEY_IS_NOT_REGISTERED_ERROR',
                '31': 'DEADLINE_HAS_EXPIRED_ERROR',
                '32': 'UNREGISTERED_IP_ERROR',
                '33': 'UNSIGNED_CALL_ERROR'
            }
            
            if result_code in error_guides:
                print(f"\n💡 오류 해설: {error_guides[result_code]}")
                
                if result_code == '30':
                    print("→ API 키가 등록되지 않았습니다. .env 파일의 TOUR_API_KEY를 확인하세요.")
                elif result_code == '31':
                    print("→ API 사용 기한이 만료되었습니다. 공공데이터포털에서 재신청하세요.")
                elif result_code in ['20', '22']:
                    print("→ API 사용 권한 또는 트래픽 제한 문제입니다.")
            
            return places
        
        items = response_data.get('body', {}).get('items', {}).get('item', [])
        
        if not items:
            print("⚠️ 데이터 없음")
            total_count = response_data.get('body', {}).get('totalCount', 0)
            print(f"📊 전체 데이터 수: {total_count}")
            return places
        
        print(f"✅ {len(items)}개 여행지 발견")
        
        for idx, item in enumerate(items[:max_items], 1):
            try:
                # 기본 정보 추출
                title = item.get('title', f'Place {idx}')
                addr1 = item.get('addr1', '')
                addr2 = item.get('addr2', '')
                address = f"{addr1} {addr2}".strip()
                
                # 이미지 URL (firstimage 우선, 없으면 firstimage2)
                image_url = item.get('firstimage', '') or item.get('firstimage2', '')
                if not image_url:
                    image_url = 'https://images.unsplash.com/photo-1583492547988-cf2c4cb54c16?w=1200'
                
                # 위치 정보
                latitude = float(item.get('mapy', 0)) if item.get('mapy') else None
                longitude = float(item.get('mapx', 0)) if item.get('mapx') else None
                
                # 지역 파싱 (서울, 부산, 제주 등)
                location = ''
                if '서울' in addr1:
                    location = 'Seoul'
                elif '부산' in addr1:
                    location = 'Busan'
                elif '제주' in addr1:
                    location = 'Jeju'
                elif '경기' in addr1:
                    location = 'Gyeonggi'
                elif '인천' in addr1:
                    location = 'Incheon'
                elif '강원' in addr1:
                    location = 'Gangwon'
                elif '경주' in addr1 or '경북' in addr1:
                    location = 'Gyeongju'
                else:
                    location = 'Korea'
                
                place = {
                    'rank': idx,
                    'name': title,  # 한글 이름 (추후 영문 변환)
                    'nameKo': title,
                    'location': location,
                    'category': 'Culture',  # 기본값, 추후 AI 분류
                    'imageUrl': image_url,
                    'views': '0',  # TourAPI에는 조회수 없음, 추후 처리
                    'likes': '0',
                    'aiStory': '',  # Gemini AI로 생성
                    'photoSpot': '',  # Gemini AI로 생성
                    'tags': [],
                    'address': address,
                    'bookingUrl': f'https://www.klook.com/en-US/search/?query={title}',
                    'latitude': latitude,
                    'longitude': longitude,
                    'trend': 0
                }
                
                places.append(place)
                print(f"  {idx}. {title} ({location})")
                
            except Exception as e:
                print(f"⚠️ 아이템 {idx} 파싱 오류: {e}")
                continue
        
        print(f"✅ 여행지 데이터 수집 완료: {len(places)}개")
        
    except Exception as e:
        print(f"❌ TourAPI 호출 오류: {e}")
        import traceback
        traceback.print_exc()
    
    return places


def translate_place_names(model, places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 여행지 이름을 영문으로 번역
    
    Args:
        model: Gemini 모델
        places: 여행지 리스트
        
    Returns:
        영문 이름이 추가된 여행지 리스트
    """
    print("\n🌐 Gemini AI로 여행지 이름 영문 번역 중...")
    
    # 장소 이름 리스트 생성
    place_names = [f"{p['rank']}. {p['nameKo']}" for p in places]
    
    prompt = f"""
Translate the following Korean place names into official English names.
Use the proper English names commonly used in tourism (e.g., "경복궁" -> "Gyeongbokgung Palace").
Keep location names, mountain names, and temple names in romanized Korean with proper suffixes.

Place Names:
{chr(10).join(place_names)}

Response format (JSON):
{{
  "translations": [
    {{"rank": 1, "name": "English Place Name"}},
    {{"rank": 2, "name": "English Place Name"}},
    ...
  ]
}}

JSON only.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        translations = json.loads(result_text)
        
        # 번역 적용
        for trans in translations.get('translations', []):
            rank = trans.get('rank')
            name = trans.get('name')
            
            for place in places:
                if place['rank'] == rank:
                    place['name'] = name
                    break
        
        print(f"✅ 영문 번역 완료 ({len(translations.get('translations', []))}/{len(places)}개)")
        
    except Exception as e:
        print(f"⚠️ Gemini 번역 오류: {e}")
        # 실패 시 기존 이름 유지
    
    return places


def categorize_places(model, places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 여행지 카테고리 자동 분류 (Culture, Nature, Modern)
    
    Args:
        model: Gemini 모델
        places: 여행지 리스트
        
    Returns:
        카테고리가 분류된 여행지 리스트
    """
    print("\n🏷️ Gemini AI로 여행지 카테고리 자동 분류 중...")
    
    place_info = [f"{p['rank']}. {p['nameKo']} ({p['name']})" for p in places]
    
    prompt = f"""
Categorize each Korean place into one of three categories based on its characteristics:
- **Culture**: Palaces, temples, museums, historical sites, traditional markets
- **Nature**: Mountains, beaches, islands, parks, natural landmarks
- **Modern**: Shopping districts, cafes, pop-up stores, modern attractions, urban areas

Places:
{chr(10).join(place_info)}

Response format (JSON):
{{
  "categories": [
    {{"rank": 1, "category": "Culture"}},
    {{"rank": 2, "category": "Nature"}},
    {{"rank": 3, "category": "Modern"}},
    ...
  ]
}}

JSON only. Use only "Culture", "Nature", or "Modern".
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        categories = json.loads(result_text)
        
        # 카테고리 적용
        for cat in categories.get('categories', []):
            rank = cat.get('rank')
            category = cat.get('category', 'Culture')
            
            # 유효성 검사
            if category not in ['Culture', 'Nature', 'Modern']:
                category = 'Culture'
            
            for place in places:
                if place['rank'] == rank:
                    place['category'] = category
                    break
        
        print(f"✅ 카테고리 분류 완료")
        
    except Exception as e:
        print(f"⚠️ Gemini 카테고리 분류 오류: {e}")
        # 실패 시 기본 "Culture" 유지
    
    return places


def generate_place_insights(model, places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 AI Cultural Guide와 Photo Spot 생성
    
    Args:
        model: Gemini 모델
        places: 여행지 리스트
        
    Returns:
        AI 정보가 추가된 여행지 리스트
    """
    print("\n✨ Gemini AI로 Cultural Guide & Photo Spot 생성 중...")
    
    place_info = [f"{p['rank']}. {p['name']} ({p['nameKo']}) - {p['category']}, {p['location']}" for p in places]
    
    prompt = f"""
For each Korean travel destination, generate TWO things in English:

1. **AI Cultural Guide** (aiStory): 2-3 sentences explaining the historical context, cultural significance, or best visiting time. Make it informative and engaging.

2. **Pro Photo Spot** (photoSpot): 1-2 sentences describing the exact spot and angle for Instagram-worthy photos used by locals.

Places:
{chr(10).join(place_info)}

Response format (JSON):
{{
  "insights": [
    {{
      "rank": 1,
      "aiStory": "This was the main royal palace of the Joseon Dynasty...",
      "photoSpot": "Stand at the center of Gwanghwamun Gate for a perfectly symmetrical shot...",
      "tags": ["Royal Heritage", "Must Visit", "Hanbok Friendly"]
    }},
    ...
  ]
}}

JSON only. Each place must have unique, specific insights and tags.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        insights = json.loads(result_text)
        
        # 인사이트 적용
        for ins in insights.get('insights', []):
            rank = ins.get('rank')
            ai_story = ins.get('aiStory', '')
            photo_spot = ins.get('photoSpot', '')
            tags = ins.get('tags', [])
            
            for place in places:
                if place['rank'] == rank:
                    place['aiStory'] = ai_story
                    place['photoSpot'] = photo_spot
                    place['tags'] = tags
                    break
        
        print(f"✅ AI Guide 생성 완료")
        
    except Exception as e:
        print(f"⚠️ Gemini AI Guide 생성 오류: {e}")
        # 실패 시 기본 메시지 설정
        for place in places:
            if not place.get('aiStory'):
                place['aiStory'] = f"A must-visit destination in {place['location']}."
            if not place.get('photoSpot'):
                place['photoSpot'] = "Capture the stunning view from the main entrance."
            if not place.get('tags'):
                place['tags'] = ['Must Visit', 'Local Favorite']
    
    return places


def save_to_firestore(db, places: List[Dict[str, Any]]):
    """
    여행지 데이터를 Firestore에 저장
    
    Args:
        db: Firestore 클라이언트
        places: 여행지 리스트
    """
    try:
        # 현재 날짜 (UTC)
        today = datetime.utcnow().strftime('%Y-%m-%d')
        doc_id = f"{today}_place"
        
        print(f"\n💾 Firestore에 저장 중... (문서 ID: {doc_id})")
        
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc_ref.set({
            'date': today,
            'category': 'place',
            'items': places,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        print(f"✅ Firestore 저장 완료! ({len(places)}개 여행지)")
        print(f"📄 문서 경로: daily_rankings/{doc_id}")
        
    except Exception as e:
        print(f"❌ Firestore 저장 오류: {e}")
        import traceback
        traceback.print_exc()


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🗺️ K-RANK PLACE SCRAPER")
    print("=" * 60)
    
    # API 키 확인
    tour_api_key = os.getenv('TOUR_API_KEY')
    if not tour_api_key or tour_api_key == 'YOUR_TOUR_API_KEY_HERE':
        print("❌ TOUR_API_KEY가 설정되지 않았습니다!")
        print("💡 .env 파일에 TOUR_API_KEY를 추가하세요.")
        print("📌 발급: https://www.data.go.kr/data/15101578/openapi.do")
        sys.exit(1)
    
    # Firebase 및 Gemini 초기화
    db = initialize_firebase()
    model = initialize_gemini()
    
    # 1. TourAPI에서 여행지 데이터 수집
    places = fetch_tour_places(tour_api_key, max_items=30)
    
    if not places:
        print("❌ 여행지 데이터 수집 실패")
        sys.exit(1)
    
    # 2. 여행지 이름 영문 번역
    places = translate_place_names(model, places)
    
    # 3. 카테고리 자동 분류
    places = categorize_places(model, places)
    
    # 4. AI Cultural Guide & Photo Spot 생성
    places = generate_place_insights(model, places)
    
    # 5. Firestore에 저장
    save_to_firestore(db, places)
    
    print("\n✅ 모든 작업 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
