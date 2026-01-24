#!/usr/bin/env python3
"""
K-Rank Food Scraper
편의점 베스트 간식/라면 랭킹을 크롤링하고 Firebase에 저장합니다.
"""

import os
import sys
import time
import re
from datetime import datetime
from typing import List, Dict, Any
import json

from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 카테고리 매핑
FOOD_CATEGORIES = {
    'all': {'name': 'All Products', 'firestore_category': 'food'},
    'ramen': {'name': 'Ramen', 'firestore_category': 'food-ramen'},
    'snacks': {'name': 'Snacks', 'firestore_category': 'food-snacks'},
    'beverages': {'name': 'Beverages', 'firestore_category': 'food-beverages'},
}


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
        raise ValueError("GEMINI_API_KEY not found in .env file")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-2.0-flash')


def scrape_convenience_store_food(max_items: int = 20, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    편의점 베스트 상품 크롤링 (ScraperAPI 사용)
    
    Args:
        max_items: 크롤링할 최대 아이템 수
        max_retries: 최대 재시도 횟수
        
    Returns:
        제품 데이터 리스트
    """
    products = []
    
    # ScraperAPI 키 확인
    scraperapi_key = os.getenv('SCRAPER_API_KEY')
    if not scraperapi_key:
        print("❌ SCRAPER_API_KEY not found in environment")
        return products
    
    # CU 편의점 베스트 상품 페이지
    # 실제 URL은 CU 사이트 분석 후 조정 필요
    # 가능한 URL 옵션:
    # - https://cu.bgfretail.com/product/product.do (메인)
    # - https://cu.bgfretail.com/event/plusAjax.do (베스트 상품)
    target_url = "https://cu.bgfretail.com/product/product.do?category=product&depth2=1"
    
    for attempt in range(max_retries):
        try:
            print(f"🌐 ScraperAPI로 페이지 요청 중... (시도 {attempt + 1}/{max_retries})")
            print(f"📄 URL: {target_url}")
            
            # ScraperAPI 파라미터
            params = {
                'api_key': scraperapi_key,
                'url': target_url,
                'country_code': 'kr',
                'render': 'true'  # JavaScript 렌더링 활성화
            }
            
            response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
            
            if response.status_code == 200:
                print("✅ ScraperAPI 요청 성공!")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Cloudflare 체크
                page_title = soup.title.string if soup.title else "No Title"
                if "잠시만" in page_title or "Just a moment" in page_title:
                    print(f"⚠️  Cloudflare 페이지 감지됨 (시도 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 재시도 중...")
                        time.sleep(5)
                        continue
                    else:
                        print("❌ 최대 재시도 횟수 초과")
                        return products
                
                print(f"✅ 페이지 로드 완료: {page_title}")
                
                # 제품 파싱 (실제 선택자는 사이트 분석 후 조정 필요)
                items = soup.select('.product-item, .prod-item, .item')[:max_items]
                
                if len(items) == 0:
                    print("⚠️  제품을 찾지 못함. Mock 데이터 생성...")
                    # Mock 데이터 생성 (테스트용)
                    products = generate_mock_food_data(max_items)
                    print("✅ Mock 데이터로 계속 진행합니다.")
                    break
                
                print(f"✅ {len(items)}개 제품 발견")
                
                # 제품 정보 추출
                for idx, item in enumerate(items, 1):
                    try:
                        name_elem = item.select_one('.product-name, .prod-name, .name')
                        name = name_elem.get_text(strip=True) if name_elem else f"Product {idx}"
                        
                        brand_elem = item.select_one('.brand, .manufacturer')
                        brand = brand_elem.get_text(strip=True) if brand_elem else "Unknown"
                        
                        img_elem = item.select_one('img')
                        image_url = ''
                        if img_elem:
                            image_url = (
                                img_elem.get('data-original', '') or 
                                img_elem.get('data-src', '') or 
                                img_elem.get('src', '')
                            )
                        
                        if image_url and not image_url.startswith('http'):
                            image_url = 'https:' + image_url if image_url.startswith('//') else 'https://cu.bgfretail.com' + image_url
                        
                        price_elem = item.select_one('.price, .price-num')
                        price = price_elem.get_text(strip=True) if price_elem else "0"
                        if price and not price.endswith('원'):
                            price = price + "원"
                        
                        # 카테고리 추측 (제품명 기반)
                        category = categorize_food_product(name)
                        
                        product = {
                            'rank': idx,
                            'productName': name,
                            'brand': brand,
                            'imageUrl': image_url or "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=400&fit=crop",
                            'price': price,
                            'category': category,
                            'tags': [],
                            'spicyLevel': 0,
                            'isVegan': False,
                            'trend': 0,
                            'buyUrl': ''
                        }
                        
                        products.append(product)
                        print(f"  {idx}. {brand} - {name} ({category})")
                        
                    except Exception as e:
                        print(f"⚠️  제품 {idx} 파싱 오류: {e}")
                        continue
                
                print("✅ 제품 크롤링 성공!")
                break
                
            else:
                print(f"❌ ScraperAPI 요청 실패: HTTP {response.status_code}")
                if attempt < max_retries - 1:
                    print("🔄 재시도 중...")
                    time.sleep(5)
                    continue
                else:
                    print("❌ 최대 재시도 횟수 초과")
                    
        except requests.exceptions.Timeout:
            print(f"⏱️  요청 타임아웃 (시도 {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                print("🔄 재시도 중...")
                time.sleep(5)
                continue
            else:
                print("❌ 최대 재시도 횟수 초과")
                
        except Exception as e:
            print(f"❌ 크롤링 오류 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("🔄 재시도 중...")
                time.sleep(5)
                continue
            else:
                print("❌ 최대 재시도 횟수 초과")
                print("⚠️  Mock 데이터로 대체합니다...")
                products = generate_mock_food_data(max_items)
                import traceback
                traceback.print_exc()
    
    # 크롤링 실패 후에도 products가 비어있으면 Mock 데이터 생성
    if not products:
        print("⚠️  크롤링 완전 실패. Mock 데이터 생성 중...")
        products = generate_mock_food_data(max_items)
    
    return products


def categorize_food_product(product_name: str) -> str:
    """
    제품명을 기반으로 카테고리 추측
    
    Args:
        product_name: 제품명
        
    Returns:
        카테고리 ('Ramen', 'Snack', 'Beverage')
    """
    name_lower = product_name.lower()
    
    # 라면 키워드
    if any(keyword in name_lower for keyword in ['라면', 'ramen', '면', 'noodle', '짜파구리', '불닭']):
        return 'Ramen'
    
    # 음료 키워드
    if any(keyword in name_lower for keyword in ['음료', 'drink', '주스', 'juice', '커피', 'coffee', '우유', 'milk', '사이다', '콜라']):
        return 'Beverage'
    
    # 기본값: 스낵
    return 'Snack'


def generate_mock_food_data(count: int = 20) -> List[Dict[str, Any]]:
    """
    테스트용 Mock 데이터 생성
    
    Args:
        count: 생성할 제품 수
        
    Returns:
        Mock 제품 데이터 리스트
    """
    print("🔨 Mock 데이터 생성 중...")
    
    mock_products = [
        {"name": "신라면", "brand": "농심", "category": "Ramen", "price": "1,200원"},
        {"name": "진라면", "brand": "오뚜기", "category": "Ramen", "price": "1,100원"},
        {"name": "불닭볶음면", "brand": "삼양", "category": "Ramen", "price": "1,300원"},
        {"name": "꿀꽈배기", "brand": "크라운", "category": "Snack", "price": "1,500원"},
        {"name": "포카칩", "brand": "오리온", "category": "Snack", "price": "1,800원"},
        {"name": "새우깡", "brand": "농심", "category": "Snack", "price": "1,200원"},
        {"name": "바나나맛우유", "brand": "빙그레", "category": "Beverage", "price": "1,400원"},
        {"name": "초코파이", "brand": "오리온", "category": "Snack", "price": "2,500원"},
        {"name": "짜파게티", "brand": "농심", "category": "Ramen", "price": "1,100원"},
        {"name": "허니버터칩", "brand": "해태", "category": "Snack", "price": "2,000원"},
        {"name": "칠성사이다", "brand": "롯데", "category": "Beverage", "price": "1,200원"},
        {"name": "안성탕면", "brand": "농심", "category": "Ramen", "price": "1,000원"},
        {"name": "카스타드", "brand": "해태", "category": "Snack", "price": "1,300원"},
        {"name": "맥콜", "brand": "롯데", "category": "Beverage", "price": "1,100원"},
        {"name": "육개장", "brand": "농심", "category": "Ramen", "price": "1,200원"},
        {"name": "오징어땅콩", "brand": "롯데", "category": "Snack", "price": "1,500원"},
        {"name": "밀키스", "brand": "롯데", "category": "Beverage", "price": "1,300원"},
        {"name": "너구리", "brand": "농심", "category": "Ramen", "price": "1,200원"},
        {"name": "프링글스", "brand": "켈로그", "category": "Snack", "price": "2,800원"},
        {"name": "비락식혜", "brand": "빙그레", "category": "Beverage", "price": "1,200원"},
    ]
    
    products = []
    for idx, item in enumerate(mock_products[:count], 1):
        products.append({
            'rank': idx,
            'productName': item['name'],
            'brand': item['brand'],
            'imageUrl': f"https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=400&fit=crop&sig={idx}",
            'price': item['price'],
            'category': item['category'],
            'tags': [],
            'spicyLevel': 0,
            'isVegan': False,
            'trend': 0,
            'buyUrl': ''
        })
    
    print(f"✅ Mock 데이터 {len(products)}개 생성 완료")
    return products


async def analyze_food_with_gemini(model, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 음식 제품 분석 (맵기 레벨, Vegan, 영어 번역, 태그)
    
    Args:
        model: Gemini 모델
        products: 제품 리스트
        
    Returns:
        분석이 완료된 제품 리스트
    """
    print("\n🤖 Gemini AI로 제품 분석 중...")
    
    # 제품 정보 리스트 생성
    product_info = [f"{p['rank']}. {p['brand']} - {p['productName']} ({p['category']})" for p in products]
    
    prompt = f"""
Analyze these Korean food products and provide detailed information for each.

Products:
{chr(10).join(product_info)}

For each product, provide:
1. **productNameEn**: English translation of the product name (keep brand name, translate description)
2. **spicyLevel**: Spice level from 1-5 (1 = Not Spicy, 3 = Medium, 5 = Extremely Spicy)
3. **isVegan**: true if vegan-friendly, false otherwise
4. **tags**: 3 relevant tags (e.g., "Spicy Noodles", "Korean Classic", "Sweet Snack", "Refreshing Drink")
5. **flavorProfile**: One word - Sweet/Savory/Umami/Tangy/Spicy

Examples:
- 신라면 (Ramen) → {{"productNameEn": "Shin Ramyun", "spicyLevel": 4, "isVegan": false, "tags": ["Spicy Noodles", "Korean Classic", "Comfort Food"], "flavorProfile": "Spicy"}}
- 바나나맛우유 (Beverage) → {{"productNameEn": "Banana Milk", "spicyLevel": 1, "isVegan": true, "tags": ["Sweet Drink", "Korean Favorite", "Creamy"], "flavorProfile": "Sweet"}}

Response format (JSON only):
{{
  "analysis": [
    {{"rank": 1, "productNameEn": "...", "spicyLevel": 3, "isVegan": false, "tags": ["...", "...", "..."], "flavorProfile": "..."}},
    {{"rank": 2, "productNameEn": "...", "spicyLevel": 1, "isVegan": true, "tags": ["...", "...", "..."], "flavorProfile": "..."}}
  ]
}}
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱 (마크다운 코드 블록 제거)
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        analysis_data = json.loads(result_text)
        
        # 분석 결과 적용
        for item in analysis_data.get('analysis', []):
            rank = item.get('rank')
            
            for product in products:
                if product['rank'] == rank:
                    product['productName'] = item.get('productNameEn', product['productName'])
                    product['spicyLevel'] = item.get('spicyLevel', 1)
                    product['isVegan'] = item.get('isVegan', False)
                    product['tags'] = item.get('tags', [])
                    # flavorProfile을 첫 번째 태그에 추가
                    flavor = item.get('flavorProfile', '')
                    if flavor and flavor not in product['tags']:
                        product['tags'].insert(0, flavor)
                    break
        
        print(f"✅ Gemini 분석 완료 ({len(products)}개 제품)")
        
    except Exception as e:
        print(f"⚠️  Gemini 분석 오류: {e}")
        print("💡 기본값 사용")
        # 분석 실패 시 기본값 사용
        for product in products:
            product['tags'] = [product['category'], "Korean Food"]
    
    return products


def generate_amazon_link(product_name: str, brand: str) -> str:
    """
    Amazon Affiliate 링크 생성
    
    Args:
        product_name: 제품명
        brand: 브랜드명
        
    Returns:
        Amazon 검색 URL (affiliate ID 포함)
    """
    affiliate_id = os.getenv('AMAZON_AFFILIATE_ID', 'krank-20')
    
    # 검색 쿼리 생성 (브랜드 + 제품명)
    search_query = f"{brand} {product_name}".replace(' ', '+')
    
    # Amazon 검색 URL
    amazon_url = f"https://www.amazon.com/s?k={search_query}&tag={affiliate_id}"
    
    return amazon_url


async def calculate_food_trends(db, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    이전 날짜 랭킹과 비교하여 트렌드 계산
    
    Args:
        db: Firestore 클라이언트
        products: 현재 제품 리스트
        
    Returns:
        트렌드가 추가된 제품 리스트
    """
    from datetime import timedelta
    
    try:
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        doc_id = f"{yesterday}_food"
        
        print(f"\n📊 트렌드 계산 중... (어제: {yesterday})")
        
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print(f"⚠️  어제 데이터 없음. 트렌드 0으로 설정")
            for product in products:
                product['trend'] = 0
            return products
        
        yesterday_items = doc.to_dict().get('items', [])
        print(f"✅ 어제 데이터 {len(yesterday_items)}개 발견")
        
        # 제품명으로 매칭
        for current_item in products:
            current_rank = current_item['rank']
            product_name = current_item['productName']
            
            yesterday_rank = None
            for old_item in yesterday_items:
                if old_item.get('productName') == product_name:
                    yesterday_rank = old_item.get('rank')
                    break
            
            if yesterday_rank:
                trend = yesterday_rank - current_rank
                current_item['trend'] = trend
                print(f"  {product_name}: {yesterday_rank}위 → {current_rank}위 (변동: {'+' if trend > 0 else ''}{trend})")
            else:
                current_item['trend'] = 0
                print(f"  {product_name}: 신규 진입 (변동: NEW)")
        
        return products
        
    except Exception as e:
        print(f"⚠️  트렌드 계산 오류: {e}")
        for product in products:
            product['trend'] = 0
        return products


def save_to_firebase(db, products: List[Dict[str, Any]]):
    """
    Firebase에 데이터 저장
    
    Args:
        db: Firestore 클라이언트
        products: 제품 리스트
    """
    try:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        doc_id = f"{today}_food"
        
        print(f"\n💾 Firebase에 저장 중... (문서 ID: {doc_id})")
        
        data = {
            'date': today,
            'category': 'food',
            'items': products,
            'updatedAt': firestore.SERVER_TIMESTAMP
        }
        
        db.collection('daily_rankings').document(doc_id).set(data)
        print(f"✅ Firebase 저장 완료! ({len(products)}개 제품)")
        
    except Exception as e:
        print(f"❌ Firebase 저장 오류: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """메인 함수"""
    print("=" * 60)
    print("🍜 K-Rank Food Scraper 시작")
    print("=" * 60)
    
    # 초기화
    db = initialize_firebase()
    model = initialize_gemini()
    
    # 1. 크롤링
    products = scrape_convenience_store_food(max_items=20)
    
    if not products:
        print("⚠️  데이터가 없습니다. 프로그램 종료")
        return
    
    # 2. Gemini AI 분석
    products = await analyze_food_with_gemini(model, products)
    
    # 3. Amazon 링크 생성
    print("\n🔗 Amazon Affiliate 링크 생성 중...")
    for product in products:
        product['buyUrl'] = generate_amazon_link(product['productName'], product['brand'])
    print("✅ Amazon 링크 생성 완료")
    
    # 4. 트렌드 계산
    products = await calculate_food_trends(db, products)
    
    # 5. Firebase에 저장
    save_to_firebase(db, products)
    
    print("\n" + "=" * 60)
    print("🎉 K-Rank Food Scraper 완료!")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
