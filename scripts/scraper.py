#!/usr/bin/env python3
"""
K-Rank Beauty Scraper
올리브영 베스트 제품 랭킹을 크롤링하고 Firebase에 저장합니다.
"""

import asyncio
import os
import sys
import random
import time
from datetime import datetime
from typing import List, Dict, Any
import json

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
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

def scrape_olive_young_by_category(category_code: str = None, max_items: int = 20, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    올리브영 카테고리별 베스트 제품 크롤링 (ScraperAPI 사용)
    
    Args:
        category_code: 카테고리 코드 (예: '10000010001' for Skincare, None for All)
        max_items: 크롤링할 최대 아이템 수
        max_retries: 요청 실패 시 최대 재시도 횟수
        
    Returns:
        제품 데이터 리스트
    """
    products = []
    
    # ScraperAPI 키 확인
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    if not scraperapi_key:
        print("❌ SCRAPERAPI_KEY not found in environment")
        return products
    
    # URL 생성
    if category_code:
        target_url = f"https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&fltDispCatNo={category_code}&rowsPerPage=100"
    else:
        target_url = "https://www.oliveyoung.co.kr/store/main/getBestList.do?dispCatNo=900000100100001&rowsPerPage=100"
    
    for attempt in range(max_retries):
        try:
            print(f"🌐 ScraperAPI로 페이지 요청 중... (시도 {attempt + 1}/{max_retries})")
            print(f"📄 URL: {target_url}")
            
            # ScraperAPI 파라미터
            params = {
                'api_key': scraperapi_key,
                'url': target_url,
                'country_code': 'kr',  # 한국 IP 사용
                'render': 'true'  # JavaScript 렌더링
            }
            
            # 요청 전송
            response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
            
            if response.status_code == 200:
                print("✅ ScraperAPI 요청 성공!")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Cloudflare 체크
                page_title = soup.title.string if soup.title else "No Title"
                if "잠시만" in page_title or "Just a moment" in page_title:
                    print(f"⚠️  여전히 Cloudflare 페이지 감지됨 (시도 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 재시도 중...")
                        time.sleep(5)
                        continue
                    else:
                        print("❌ 최대 재시도 횟수 초과")
                        return products
                
                print(f"✅ 페이지 로드 완료: {page_title}")
                
                # 제품 파싱
                items = soup.select('div.prd_info')[:max_items]
                
                if len(items) == 0:
                    print("⚠️  'div.prd_info'로 제품을 찾지 못함")
                    items = soup.select('ul.common_prd_list li')[:max_items]
                
                print(f"✅ {len(items)}개 제품 발견")
                
                if len(items) == 0:
                    print(f"⚠️  제품을 찾지 못함 (시도 {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print("🔄 재시도 중...")
                        time.sleep(5)
                        continue
                    else:
                        print("❌ 최대 재시도 횟수 초과")
                        return products
                
                # 제품 정보 추출
                for idx, item in enumerate(items, 1):
                    try:
                        name_elem = item.select_one('.prd_name .tx_name') or item.select_one('p.tx_name')
                        name = name_elem.get_text(strip=True) if name_elem else f"Product {idx}"
                        
                        brand_elem = item.select_one('.tx_brand')
                        brand = brand_elem.get_text(strip=True) if brand_elem else "Unknown"
                        
                        img_elem = item.select_one('img')
                        image_url = ''
                        if img_elem:
                            image_url = img_elem.get('src', '') or img_elem.get('data-original', '')
                        if image_url and not image_url.startswith('http'):
                            image_url = 'https:' + image_url
                        
                        price_elem = item.select_one('.tx_cur .tx_num')
                        price = price_elem.get_text(strip=True) if price_elem else "0"
                        if price:
                            price = price + "원"
                        
                        link_elem = item.select_one('a')
                        buy_url = link_elem.get('href', '') if link_elem else ''
                        if buy_url and not buy_url.startswith('http'):
                            buy_url = 'https://www.oliveyoung.co.kr' + buy_url
                        
                        product = {
                            'rank': idx,
                            'productName': name,
                            'brand': brand,
                            'imageUrl': image_url or "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=100&h=100&fit=crop",
                            'price': price,
                            'buyUrl': buy_url,
                            'tags': [],
                            'subcategory': 'skincare',
                            'trend': 0
                        }
                        
                        products.append(product)
                        print(f"  {idx}. {brand} - {name} ({price})")
                        
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

async def scrape_netflix(media_type: str = 'tv', max_items: int = 10, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    Netflix Top 10 South Korea TV Shows/Films 크롤링
    
    Args:
        media_type: 'tv' 또는 'film'
        max_items: 크롤링할 최대 아이템 수 (기본 10개)
        max_retries: 최대 재시도 횟수
        
    Returns:
        제품 데이터 리스트
    """
    products = []
    
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                print(f"🎬 Netflix Top 10 크롤링 시작... (시도 {attempt + 1}/{max_retries})")
                
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='ko-KR',
                    timezone_id='Asia/Seoul'
                )
                
                page = await context.new_page()
                
                # Netflix Top 10 URL (tv 또는 films)
                url = f"https://top10.netflix.com/south-korea/{media_type}"
                print(f"📄 페이지 로딩 중: {url}")
                
                await page.goto(url, wait_until='networkidle', timeout=60000)
                
                # 테이블이 로드될 때까지 대기
                try:
                    await page.wait_for_selector("table tbody tr", timeout=30000)
                except:
                    print("⚠️ 테이블 셀렉터 대기 중 타임아웃 발생")
                
                await page.wait_for_timeout(3000)  # 추가 렌더링 대기
                
                # HTML 가져오기
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 테이블 행(Row) 선택
                rows = soup.select("table tbody tr")[:max_items]
                print(f"✅ {len(rows)}개 타이틀 발견!")
                
                if len(rows) == 0:
                    print(f"⚠️ 데이터를 찾지 못함 (시도 {attempt + 1}/{max_retries})")
                    await browser.close()
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5)
                        continue
                    else:
                        return products
                
                for i, row in enumerate(rows, 1):
                    try:
                        # 브라우저 분석 기반 셀렉터
                        rank_el = row.select_one("span.rank")
                        title_el = row.select_one("td.title button")
                        weeks_el = row.select_one("td[data-uia='top10-table-row-weeks']")
                        img_el = row.select_one("td.title img.desktop-only")
                        
                        rank_text = rank_el.get_text(strip=True) if rank_el else str(i)
                        title = title_el.get_text(strip=True) if title_el else f"Unknown Title {i}"
                        weeks = weeks_el.get_text(strip=True) if weeks_el else "1"
                        
                        # 이미지 URL 추출
                        image_url = img_el.get('src', '') if img_el else 'https://assets.nflxext.com/us/ffe/siteui/common/icons/nficon2016.png'
                        
                        # YouTube 트레일러 링크 생성
                        trailer_query = f"{title} trailer"
                        trailer_link = f"https://www.youtube.com/results?search_query={trailer_query.replace(' ', '+')}"
                        
                        # media_type에 따라 type 설정
                        item_type = 'TV Show' if media_type == 'tv' else 'Film'
                        default_tag = 'K-Drama' if media_type == 'tv' else 'Korean Film'
                        
                        item = {
                            'rank': int(rank_text) if rank_text.isdigit() else i,
                            'titleEn': title,
                            'titleKo': title,  # 이후 번역 단계에서 업데이트
                            'imageUrl': image_url,
                            'weeksInTop10': weeks,
                            'type': item_type,
                            'trailerLink': trailer_link,
                            'vpnLink': 'https://nordvpn.com/ko/',
                            'tags': [f"{weeks} Weeks in Top 10", default_tag],
                            'trend': 0
                        }
                        
                        products.append(item)
                        print(f"  {rank_text}위. {title} ({weeks}주 연속 Top 10)")
                        
                    except Exception as e:
                        print(f"⚠️ {i}위 파싱 오류: {e}")
                        continue
                
                await browser.close()
                print("✅ Netflix 크롤링 성공!")
                break
                
        except Exception as e:
            print(f"❌ 크롤링 오류 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
                continue
            else:
                import traceback
                traceback.print_exc()
    
    return products

async def translate_media_titles(model, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 미디어 제목(Netflix)을 한국어로 번역
    """
    print("\n🌐 Gemini AI로 미디어 제목 한국어 번역 중...")
    
    # 제목 리스트 생성
    titles = [f"{item['rank']}. {item['titleEn']}" for item in items]
    
    prompt = f"""
Translate the following Netflix TV Show/Film titles into their official Korean titles.
Some are already Korean dramas, so find their original Korean titles (e.g., 'Squid Game' -> '오징어 게임').
Exclude rank numbers from the translation.

Titles:
{chr(10).join(titles)}

Response format (JSON):
{{
  "translations": [
    {{"rank": 1, "titleKo": "한국어 제목"}},
    {{"rank": 2, "titleKo": "한국어 제목"}},
    ...
  ]
}}

JSON only.
"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱 (마크다운 코드 블록 제거)
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        translations = json.loads(result_text)
        
        # 번역 적용
        for trans in translations.get('translations', []):
            rank = trans.get('rank')
            title_ko = trans.get('titleKo')
            
            for item in items:
                if item['rank'] == rank:
                    item['titleKo'] = title_ko
                    break
        
        print("✅ 미디어 제목 번역 완료")
        
    except Exception as e:
        print(f"⚠️ Gemini 번역 오류: {e}")
    
    return items

async def calculate_media_trends(db, current_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """미디어 랭킹 트렌드 계산"""
    from datetime import timedelta
    
    try:
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        doc_id = f"{yesterday}_media"
        
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return current_items
        
        yesterday_items = doc.to_dict().get('items', [])
        
        for current in current_items:
            title = current['titleEn']
            yesterday_rank = next((item['rank'] for item in yesterday_items if item['titleEn'] == title), None)
            
            if yesterday_rank:
                current['trend'] = yesterday_rank - current['rank']
            else:
                current['trend'] = 0
                
        return current_items
    except Exception as e:
        print(f"⚠️ 미디어 트렌드 계산 오류: {e}")
        return current_items


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
    print("🇰🇷 K-Rank Scraper - Beauty & Media")
    print("=" * 60)
    
    # 커맨드 라인 인자 확인
    run_mode = sys.argv[1] if len(sys.argv) > 1 else "all"  # "beauty", "media", "all"
    
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
        
        # 3. Beauty 카테고리 크롤링
        if run_mode in ["beauty", "all"]:
            print("\n" + "=" * 60)
            print("💄 BEAUTY 카테고리 크롤링")
            print("=" * 60)
            
            for category_key, config in CATEGORY_MAPPING.items():
                print("\n" + "-" * 60)
                print(f"📦 {category_key.upper()} 카테고리 크롤링 시작")
                print("-" * 60)
                
                # 카테고리별 크롤링
                products = scrape_olive_young_by_category(
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
        
        # 4. Media 카테고리 크롤링
        if run_mode in ["media", "all"]:
            print("\n" + "=" * 60)
            print("🎬 MEDIA 카테고리 크롤링 (Netflix)")
            print("=" * 60)
            
            all_media_items = []
            
            # Netflix TV Shows Top 10 크롤링
            print("\n📺 Netflix TV Shows 크롤링 중...")
            tv_items = await scrape_netflix(media_type='tv', max_items=10)
            if tv_items:
                all_media_items.extend(tv_items)
                print(f"✅ TV Shows {len(tv_items)}개 수집 완료")
            else:
                print("⚠️ TV Shows 데이터를 찾지 못했습니다.")
            
            # Netflix Films Top 10 크롤링
            print("\n🎬 Netflix Films 크롤링 중...")
            film_items = await scrape_netflix(media_type='films', max_items=10)
            if film_items:
                all_media_items.extend(film_items)
                print(f"✅ Films {len(film_items)}개 수집 완료")
            else:
                print("⚠️ Films 데이터를 찾지 못했습니다.")
            
            if all_media_items:
                # 트렌드 계산
                all_media_items = await calculate_media_trends(db, all_media_items)
                
                # 한국어 제목 번역
                all_media_items = await translate_media_titles(model, all_media_items)
                
                # Media 저장 로직
                today = datetime.utcnow().strftime('%Y-%m-%d')
                doc_id = f"{today}_media"
                doc_ref = db.collection('daily_rankings').document(doc_id)
                
                data = {
                    'date': today,
                    'category': 'media',
                    'items': all_media_items,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
                
                doc_ref.set(data)
                print(f"✅ {len(all_media_items)}개 타이틀을 {doc_id} 문서에 저장 완료")
                print(f"   - TV Shows: {len(tv_items)}개")
                print(f"   - Films: {len(film_items)}개")
                total_products += len(all_media_items)
            else:
                print("⚠️ Netflix에서 데이터를 찾지 못했습니다.")
        
        print("\n" + "=" * 60)
        print("✅ 모든 크롤링 완료!")
        print("=" * 60)
        
        # 결과 요약
        print(f"\n📊 크롤링 결과:")
        print(f"  - 총 아이템 수: {total_products}개")
        print(f"  - 실행 모드: {run_mode.upper()}")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 사용법:
    # python scraper.py           # 모든 카테고리 실행
    # python scraper.py beauty    # Beauty만 실행
    # python scraper.py media     # Media만 실행
    asyncio.run(main())
