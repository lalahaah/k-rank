#!/usr/bin/env python3
"""
K-Rank Beauty Scraper
올리브영 베스트 제품 랭킹을 크롤링하고 Firebase에 저장합니다.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import json

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 카테고리 매핑 정의
CATEGORY_MAPPING = {
    'all': {'url_param': None, 'firestore_category': 'beauty'},
    'skincare': {'url_param': '10000010001', 'firestore_category': 'beauty-skincare'},
    'suncare': {'url_param': '10000010011', 'firestore_category': 'beauty-suncare'},
    'masks': {'url_param': '10000010009', 'firestore_category': 'beauty-masks'},
    'makeup': {'url_param': '10000010002', 'firestore_category': 'beauty-makeup'},
    'haircare': {'url_param': '10000010004', 'firestore_category': 'beauty-haircare'},
    'bodycare': {'url_param': '10000010003', 'firestore_category': 'beauty-bodycare'},
}


# Firebase 초기화
def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Gemini API 초기화
def initialize_gemini():
    """Gemini API 초기화"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-2.5-flash')

async def scrape_olive_young_by_category(category_code: str = None, max_items: int = 20, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    올리브영 카테고리별 베스트 제품 크롤링
    
    Args:
        category_code: 카테고리 코드 (예: '10000010001' for Skincare, None for All)
        max_items: 크롤링할 최대 아이템 수
        max_retries: Cloudflare 우회 실패 시 최대 재시도 횟수
        
    Returns:
        제품 데이터 리스트
    """
    products = []
    
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                print(f"🌐 브라우저 시작 중... (시도 {attempt + 1}/{max_retries})")
                
                # 브라우저 설정: headless=False로 변경하여 더 실제 브라우저처럼 보이게
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                # 브라우저 컨텍스트 생성 with User-Agent 설정
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='ko-KR',
                    timezone_id='Asia/Seoul'
                )
                
                # JavaScript로 webdriver 감지 우회
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
                page = await context.new_page()
                
                # 올리브영 베스트 랭킹 페이지 - 카테고리별 URL 생성
                if category_code:
                    url = f"https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo={category_code}&rowsPerPage=100"
                else:
                    url = "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&rowsPerPage=100"
                
                print(f"📄 페이지 로딩 중: {url}")
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                
                # Cloudflare 챌린지 대기 및 통과 확인
                print("⏳ Cloudflare 챌린지 통과 대기 중...")
                await page.wait_for_timeout(15000)  # 15초 대기
                
                # 추가 네트워크 안정화 대기
                try:
                    await page.wait_for_load_state('networkidle', timeout=10000)
                except:
                    print("⚠️  네트워크 idle 상태 대기 타임아웃 (계속 진행)")
                
                # 페이지 제목으로 Cloudflare 페이지인지 확인
                page_title = await page.title()
                if "Just a moment" in page_title or "잠시만 기다려" in page_title:
                    print(f"⚠️  Cloudflare 챌린지 페이지 감지됨 (시도 {attempt + 1}/{max_retries})")
                    await browser.close()
                    if attempt < max_retries - 1:
                        print("🔄 재시도 중...")
                        await asyncio.sleep(5)  # 재시도 전 5초 대기
                        continue
                    else:
                        print("❌ 최대 재시도 횟수 초과")
                        return products
                
                print(f"✅ 페이지 로드 완료: {page_title}")
                
                # HTML 가져오기
                content = await page.content()
                
                # 디버깅: HTML 저장
                with open('oliveyoung_debug.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("💾 HTML 저장: oliveyoung_debug.html")
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # 제품 아이템 찾기 - 올리브영 실제 구조
                items = soup.select('ul.common_prd_list li')[:max_items]
                
                # 디버깅: 다른 셀렉터도 시도
                if len(items) == 0:
                    print("⚠️  'ul.common_prd_list li' 로 제품을 찾지 못함")
                    items = soup.select('.prd_info')[:max_items]
                    print(f"   '.prd_info' 시도: {len(items)}개 발견")
                
                if len(items) == 0:
                    items = soup.select('li.flag')[:max_items]
                    print(f"   'li.flag' 시도: {len(items)}개 발견")
                
                print(f"✅ {len(items)}개 제품 발견")
                
                # 제품을 찾지 못한 경우 재시도
                if len(items) == 0:
                    print(f"⚠️  제품을 찾지 못함 (시도 {attempt + 1}/{max_retries})")
                    await browser.close()
                    if attempt < max_retries - 1:
                        print("🔄 재시도 중...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        print("❌ 최대 재시도 횟수 초과")
                        return products
                
                for idx, item in enumerate(items, 1):
                    try:
                        # 제품명 (.prd_name 안의 .tx_name에서 추출)
                        name_elem = item.select_one('.prd_name .tx_name')
                        name = name_elem.get_text(strip=True) if name_elem else f"Product {idx}"
                        
                        # 브랜드
                        brand_elem = item.select_one('.tx_brand')
                        brand = brand_elem.get_text(strip=True) if brand_elem else "Unknown"
                        
                        # 이미지 (src와 data-original 둘 다 확인)
                        img_elem = item.select_one('.prd_thumb img')
                        image_url = ''
                        if img_elem:
                            image_url = img_elem.get('data-original', '') or img_elem.get('src', '')
                        if image_url and not image_url.startswith('http'):
                            image_url = 'https:' + image_url
                        
                        # 가격 (현재가)
                        price_elem = item.select_one('.tx_cur .tx_num')
                        price = price_elem.get_text(strip=True) if price_elem else "0"
                        if price:
                            price = price + "원"
                        
                        # 구매 링크 (상세 페이지 URL)
                        link_elem = item.select_one('.prd_thumb a')
                        buy_url = link_elem.get('href', '') if link_elem else ''
                        if buy_url and not buy_url.startswith('http'):
                            buy_url = 'https://www.oliveyoung.co.kr' + buy_url
                        
                        product = {
                            'rank': idx,
                            'productName': name,
                            'brand': brand,
                            'imageUrl': image_url or f"https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=100&h=100&fit=crop",
                            'price': price,
                            'buyUrl': buy_url,
                            'tags': [],
                            'subcategory': 'skincare',  # 기본값, Gemini로 분류 예정
                            'trend': 0,  # 추후 계산
                        }
                        
                        products.append(product)
                        print(f"  {idx}. {brand} - {name} ({price})")
                        
                    except Exception as e:
                        print(f"⚠️  제품 {idx} 파싱 오류: {e}")
                        continue
                
                await browser.close()
                
                # 성공적으로 제품을 수집한 경우 루프 종료
                print("✅ 제품 크롤링 성공!")
                break
                
        except Exception as e:
            print(f"❌ 크롤링 오류 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print("🔄 재시도 중...")
                await asyncio.sleep(5)
                continue
            else:
                print("❌ 최대 재시도 횟수 초과")
                import traceback
                traceback.print_exc()
    
    return products

async def calculate_trends(db, category_key: str, current_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    이전 날짜 랭킹과 비교하여 트렌드 계산
    
    Args:
        db: Firestore 클라이언트
        category_key: 카테고리 키
        current_products: 현재 제품 리스트
        
    Returns:
        트렌드가 추가된 제품 리스트
    """
    from datetime import timedelta
    
    try:
        # 어제 날짜 (UTC)
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        firestore_category = CATEGORY_MAPPING[category_key]['firestore_category']
        doc_id = f"{yesterday}_{firestore_category}"
        
        # 어제 데이터 가져오기
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            # 어제 데이터 없으면 트렌드 0
            for product in current_products:
                product['trend'] = 0
            return current_products
        
        yesterday_items = doc.to_dict().get('items', [])
        
        # 제품명으로 매칭하여 순위 변동 계산
        for current_item in current_products:
            current_rank = current_item['rank']
            product_name = current_item['productName']
            
            # 어제 순위 찾기
            yesterday_rank = None
            for old_item in yesterday_items:
                if old_item['productName'] == product_name:
                    yesterday_rank = old_item['rank']
                    break
            
            if yesterday_rank:
                # 트렌드 = 어제 순위 - 오늘 순위 (양수면 상승)
                current_item['trend'] = yesterday_rank - current_rank
            else:
                # 신규 진입
                current_item['trend'] = 0
        
        return current_products
        
    except Exception as e:
        print(f"⚠️  트렌드 계산 오류: {e}")
        # 오류 발생 시 트렌드 0으로 설정
        for product in current_products:
            product['trend'] = 0
        return current_products

async def translate_to_english(model, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 제품명과 브랜드명을 영어로 번역
    
    Args:
        model: Gemini 모델
        products: 제품 리스트
        
    Returns:
        영어로 번역된 제품 리스트
    """
    print("\n🌐 Gemini AI로 제품명 및 브랜드명 영어 번역 중...")
    
    # 제품 이름 리스트 생성
    product_names = [f"{p['rank']}. {p['brand']} - {p['productName']}" for p in products]
    
    prompt = f"""
Translate the following Korean beauty product brands and names to English.
Romanize Korean brand names (e.g., 메디힐 → Mediheal, 어노브 → UNOVE).
Remove special characters like [], 기획, 단품, etc.
Make the names concise and clear.

Products:
{chr(10).join(product_names)}

Response format (JSON):
{{
  "translations": [
    {{"rank": 1, "brand": "English Brand Name", "product_name": "English Product Name"}},
    {{"rank": 2, "brand": "English Brand Name", "product_name": "English Product Name"}},
    ...
  ]
}}

JSON only.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱
        # 마크다운 코드 블록 제거
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        translations = json.loads(result_text)
        
        # 제품에 영어 이름 및 브랜드 적용
        for item in translations.get('translations', []):
            rank = item.get('rank')
            english_brand = item.get('brand', '')
            english_name = item.get('product_name', '')
            
            for product in products:
                if product['rank'] == rank:
                    # 한글 브랜드와 제품명을 영어로 완전히 교체
                    if english_brand:
                        product['brand'] = english_brand
                    if english_name:
                        product['productName'] = english_name
                    break
        
        print("✅ 영어 번역 완료 (브랜드 + 제품명)")
        
    except Exception as e:
        print(f"⚠️  Gemini 번역 오류: {e}")
        print("한글 제품명 유지")
    
    return products

async def generate_tags(model, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 제품별 태그 자동 생성
    
    Args:
        model: Gemini 모델
        products: 제품 리스트
        
    Returns:
        태그가 추가된 제품 리스트
    """
    print("\n🏷️  Gemini AI로 제품 태그 자동 생성 중...")
    
    # 제품 이름 리스트 생성 (영어 번역된 이름 사용)
    product_info = [f"{p['rank']}. {p['brand']} - {p['productName']}" for p in products]
    
    prompt = f"""
Generate 2-3 relevant tags for each beauty product.
Tags should describe product benefits, type, or main features.
Use English tags only. Keep them short and concise.

Examples:
- Mask Pack → ["Hydrating", "Soothing", "Sheet Mask"]
- Hair Treatment → ["Damage Repair", "Moisturizing"]
- Sunscreen → ["UV Protection", "Tone Up"]

Products:
{chr(10).join(product_info)}

Response format (JSON):
{{
  "tags": [
    {{"rank": 1, "tags": ["Hydrating", "Soothing", "Sheet Mask"]}},
    {{"rank": 2, "tags": ["Damage Repair", "Moisturizing"]}},
    ...
  ]
}}

JSON only.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱
        # 마크다운 코드 블록 제거
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        tag_data = json.loads(result_text)
        
        # 제품에 태그 적용
        for item in tag_data.get('tags', []):
            rank = item.get('rank')
            tags = item.get('tags', [])
            
            for product in products:
                if product['rank'] == rank:
                    product['tags'] = tags
                    break
        
        print("✅ 태그 생성 완료")
        
    except Exception as e:
        print(f"⚠️  Gemini 태그 생성 오류: {e}")
        print("빈 태그 배열 유지")
    
    return products

def save_to_firebase(db, category_key: str, products: List[Dict[str, Any]]):
    """
    Firebase Firestore에 카테고리별 데이터 저장
    
    Args:
        db: Firestore 클라이언트
        category_key: 카테고리 키 (예: 'all', 'skincare', 'suncare')
        products: 제품 리스트
    """
    print(f"\n💾 Firebase에 {category_key} 카테고리 저장 중...")
    
    # 오늘 날짜 (UTC)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Firestore 카테고리 가져오기
    firestore_category = CATEGORY_MAPPING[category_key]['firestore_category']
    
    # 문서 ID: {날짜}_{카테고리}
    doc_id = f"{today}_{firestore_category}"
    doc_ref = db.collection('daily_rankings').document(doc_id)
    
    # 데이터 구조
    data = {
        'date': today,
        'category': firestore_category,
        'items': products,
        'updatedAt': firestore.SERVER_TIMESTAMP
    }
    
    # 저장
    doc_ref.set(data)
    
    print(f"✅ {len(products)}개 제품을 {doc_id} 문서에 저장 완료")
    print(f"📁 컬렉션: daily_rankings")
    print(f"📄 문서 ID: {doc_id}")

async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🇰🇷 K-Rank Beauty Scraper - 카테고리별 크롤링")
    print("=" * 60)
    
    try:
        # 1. Firebase 초기화
        print("\n📱 Firebase 초기화 중...")
        db = initialize_firebase()
        print("✅ Firebase 연결 완료")
        
        # 2. Gemini 초기화
        print("\n🤖 Gemini AI 초기화 중...")
        model = initialize_gemini()
        print("✅ Gemini AI 연결 완료")
        
        total_products = 0
        
        # 3. 각 카테고리별로 크롤링
        for category_key, config in CATEGORY_MAPPING.items():
            print("\n" + "=" * 60)
            print(f"📦 {category_key.upper()} 카테고리 크롤링 시작")
            print("=" * 60)
            
            # 카테고리별 크롤링
            products = await scrape_olive_young_by_category(
                category_code=config['url_param'],
                max_items=20
            )
            
            if not products:
                print(f"⚠️  {category_key} 카테고리에서 제품을 찾지 못했습니다.")
                continue
            
            # 트렌드 계산 (이전 날짜 데이터와 비교)
            products = await calculate_trends(db, category_key, products)
            
            # 영어 번역 (브랜드 + 제품명)
            products = await translate_to_english(model, products)
            
            # 태그 자동 생성
            products = await generate_tags(model, products)
            
            # Firebase에 저장
            save_to_firebase(db, category_key, products)
            total_products += len(products)
        
        print("\n" + "=" * 60)
        print("✅ 모든 카테고리 크롤링 완료!")
        print("=" * 60)
        
        # 결과 요약
        print(f"\n📊 크롤링 결과:")
        print(f"  - 총 제품 수: {total_products}개")
        print(f"  - 크롤링된 카테고리: All, Skincare, Suncare, Masks, Makeup, Haircare, Bodycare")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())


