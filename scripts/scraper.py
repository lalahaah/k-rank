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
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import json
import math

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv
from hangul_romanize import Transliter
from hangul_romanize.rule import academic

# 환경변수 로드
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# 카테고리 매핑 정의 (무신사 뷰티 기준)
CATEGORY_MAPPING = {
    'all': {'url_param': '', 'firestore_category': 'beauty'},
    'skincare': {'url_param': '104001', 'firestore_category': 'beauty-skincare'},
    'suncare': {'url_param': '104002', 'firestore_category': 'beauty-suncare'},
    'masks': {'url_param': '104013', 'firestore_category': 'beauty-masks'},
    'makeup': {'url_param': '104014', 'firestore_category': 'beauty-makeup'},
    'haircare': {'url_param': '104006', 'firestore_category': 'beauty-haircare'},
    'bodycare': {'url_param': '104007', 'firestore_category': 'beauty-bodycare'},
}

# 브랜드명 영어 매핑
BRAND_NAME_MAPPING = {
    # 주요 브랜드
    '메디큐브': 'Medicube',
    '에스네이처': 'S.Nature',
    '에스트라': 'AESTURA',
    '이즈앤트리': 'Isntree',
    '웰라쥬': 'Wellage',
    '달바': "d'Alba",
    '메디힐': 'Mediheal',
    '설화수': 'Sulwhasoo',
    '라로슈포제': 'La Roche-Posay',
    '토리든': 'Torriden',
    '아누아': 'Anua',
    '차앤박': 'CHARMZONE',
    '블랑네이처': 'BLANC NATURE',
    '프리메라': 'Primera',
    '한율': 'Hanyul',
    '에이프릴스킨': 'April Skin',
    '마녀공장': "Ma:nyo",
    '헤라': 'HERA',
    'ENHYPEN': 'ENHYPEN',
    '스킨푸드': 'SKINFOOD',
    '메노킨': 'Menoquin',
    '쏘내추럴': 'So Natural',
    '크런틴': 'Crunchteen',
    '구달': 'GOODAL',
    '닥터지': 'Dr.G',
    '정샘물': 'JUNG SAEM MOOL',
    '클리오': 'CLIO',
    '롬앤': 'rom&nd',
    '페리페라': 'peripera',
    '어노브': 'UNOVE',
    '닥터그루트': 'Dr. GROOT',
    '미쟝센': 'MISE EN SCENE',
    '일리윤': 'illiyoon',
    '세타필': 'Cetaphil',
    
    # 글로벌 브랜드 (이미 영어인 경우도 포함)
    '라로슈포제': 'La Roche-Posay',
    
    # 추가 브랜드 (필요시 계속 확장)
}



# Firebase 초기화
def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    if not firebase_admin._apps:
        # 스크립트 위치와 상관없이 프로젝트 루트의 serviceAccountKey.json 사용
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
    # models/gemini-2.0-flash: 최신 고성능 모델이며 할당량이 안정적임
    return genai.GenerativeModel('models/gemini-2.0-flash')


async def get_amazon_image(query: str) -> str:
    """
    아마존 검색을 통해 제품 이미지 URL을 가져옵니다. (WebScraping.ai 사용)
    """
    api_key = os.getenv('WEBSCRAPING_AI_API_KEY')
    if not api_key:
        return ""
    
    search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
    
    try:
        params = {
            'api_key': api_key,
            'url': search_url,
            'proxy': 'residential',
            'country': 'us'
        }
        
        response = requests.get('https://api.webscraping.ai/html', params=params, timeout=60)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 아마존 검색 결과 이미지 선택자
            img_elem = soup.select_one('div[data-component-type="s-search-result"] img.s-image')
            if img_elem:
                return img_elem.get('src', '')
    except Exception as e:
        print(f"⚠️ Amazon 이미지 검색 오류 ({query}): {e}")
    
    return ""




def scrape_musinsa_beauty_by_category(category_code: str = '', max_items: int = 20, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    무신사 뷰티 카테고리별 베스트 제품 크롤링 (WebScraping.ai 사용)
    법적 안전성을 위해 상위 20개 제품만 수집합니다.
    """
    products = []
    
    api_key = os.getenv('WEBSCRAPING_AI_API_KEY')
    if not api_key:
        print("❌ WEBSCRAPING_AI_API_KEY not found in environment")
        return products
    # URL 생성 (무신사 뷰티 랭킹 페이지)
    if category_code:
        target_url = f"https://www.musinsa.com/main/beauty/ranking?categoryCode={category_code}"
    else:
        target_url = "https://www.musinsa.com/main/beauty/ranking"
    
    for attempt in range(max_retries):
        try:
            print(f"🌐 WebScraping.ai로 무신사 페이지 요청 중... (시도 {attempt + 1}/{max_retries})")
            
            params = {
                'api_key': api_key,
                'url': target_url,
                'proxy': 'residential',
                'country': 'kr',
                'js_render': 'true', 
                'wait_for': '.gtm-select-item'
            }
            
            response = requests.get('https://api.webscraping.ai/html', params=params, timeout=120)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 제품 파싱 (CSS 선택자 기반)
                # 무신사 뷰티 랭킹의 카드 컨테이너를 찾습니다.
                items = soup.select('div[class*="UIProductColumn__Wrap"]')[:max_items]
                
                if len(items) == 0:
                    # 백업 선택자 시도 (리뉴얼 대응)
                    items = soup.select('div[class*="UIProductColumn"]')[:max_items]
                
                if len(items) == 0:
                    # 최후의 수단: gtm 클래스 사용
                    items = soup.select('.gtm-select-item')[:max_items]
                
                print(f"✅ {len(items)}개 제품 발견")
                
                for idx, item in enumerate(items, 1):
                    try:
                        # 브랜드명
                        brand_elem = item.select_one('a.gtm-click-brand p') or item.select_one('a[class*="gtm-click-brand"] p')
                        brand = brand_elem.get_text(strip=True) if brand_elem else "Unknown"
                        
                        # 상품명
                        name_elem = item.select_one('a.gtm-select-item p') or item.select_one('a[class*="gtm-select-item"] p')
                        name = name_elem.get_text(strip=True) if name_elem else f"Product {idx}"
                        
                        # 가격 (정규표현식으로 추출)
                        price_elem = item.select_one('span[class*="UIProductColumn__PriceText"]') or item.select_one('span.text-body_13px_semi')
                        price = price_elem.get_text(strip=True) if price_elem else "0원"
                        
                        # 이미지 (무신사 썸네일 수집 - 아마존 검색 실패 시 폴백용)
                        img_elem = item.select_one('img')
                        musinsa_img = ""
                        if img_elem:
                            musinsa_img = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('lazy-src')
                        
                        product = {
                            'rank': idx,
                            'productName': name,
                            'brand': brand,
                            'imageUrl': musinsa_img or "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=100&h=100&fit=crop",
                            'price': price,
                            'buyUrl': f"https://www.amazon.com/s?k={brand}+{name}",
                            'tags': [],
                            'subcategory': 'beauty',
                            'trend': 0,
                            'nikIndex': 0,
                            'culturalContext': ""
                        }
                        
                        products.append(product)
                        
                    except Exception as e:
                        print(f"⚠️  제품 {idx} 파싱 오류: {e}")
                        continue
                
                if products:
                    print("✅ 무신사 제품 데이터 추출 완료")
                    break
                    
            else:
                print(f"❌ WebScraping.ai 요청 실패: HTTP {response.status_code}")
                time.sleep(10)
                    
        except Exception as e:
            print(f"❌ 크롤링 오류: {e}")
            time.sleep(5)
    
    return products
async def calculate_trends(db, category_key: str, current_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    이전 날짜 랭킹과 비교하여 트렌드 계산
    
    NOTE: 이 함수는 제품명이 영어로 번역된 후 호출되어야 합니다!
    
    Args:
        db: Firestore 클라이언트
        category_key: 카테고리 키
        current_products: 현재 제품 리스트 (영어 번역 완료된 상태)
        
    Returns:
        트렌드가 추가된 제품 리스트
    """
    from datetime import timedelta
    
    try:
        # 어제 날짜 (UTC)
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        firestore_category = CATEGORY_MAPPING[category_key]['firestore_category']
        doc_id = f"{yesterday}_{firestore_category}"
        
        print(f"\n📊 트렌드 계산 중... (어제: {yesterday}, 카테고리: {firestore_category})")
        
        # 어제 데이터 가져오기
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print(f"⚠️  어제 데이터 없음 (문서 ID: {doc_id})")
            print("💡 첫 실행이거나 어제 데이터가 없습니다. 트렌드 0으로 설정")
            # 어제 데이터 없으면 트렌드 0
            for product in current_products:
                product['trend'] = 0
            return current_products
        
        yesterday_items = doc.to_dict().get('items', [])
        print(f"✅ 어제 데이터 {len(yesterday_items)}개 발견")
        
        # 제품명으로 매칭하여 순위 변동 계산
        trend_changes = []
        matched_count = 0
        new_count = 0
        
        for current_item in current_products:
            current_rank = current_item['rank']
            product_name = current_item['productName']
            brand = current_item.get('brand', '')
            
            # 1차: 제품명으로 정확히 매칭
            yesterday_rank = None
            for old_item in yesterday_items:
                if old_item.get('productName') == product_name:
                    yesterday_rank = old_item.get('rank')
                    break
            
            # 2차: 제품명이 매칭 안되면 브랜드 + 순위 범위로 보조 매칭
            if yesterday_rank is None and brand:
                for old_item in yesterday_items:
                    # 브랜드가 같고 순위 차이가 ±3 이내
                    if (old_item.get('brand') == brand and 
                        abs(old_item.get('rank', 999) - current_rank) <= 3):
                        # 제품명 일부 유사성 체크 (간단한 단어 매칭)
                        old_name_words = set(old_item.get('productName', '').lower().split())
                        new_name_words = set(product_name.lower().split())
                        common_words = old_name_words & new_name_words
                        if len(common_words) >= 2:  # 2개 이상 단어 일치
                            yesterday_rank = old_item.get('rank')
                            print(f"  🔍 보조 매칭: {product_name[:30]}... (rank {current_rank} ≈ {yesterday_rank})")
                            break
            
            if yesterday_rank:
                # 트렌드 = 어제 순위 - 오늘 순위 (양수면 상승)
                trend = yesterday_rank - current_rank
                current_item['trend'] = trend
                trend_symbol = '+' if trend > 0 else ''
                trend_changes.append(f"  {product_name[:40]}: {yesterday_rank}위 → {current_rank}위 (변동: {trend_symbol}{trend})")
                matched_count += 1
            else:
                # 신규 진입
                current_item['trend'] = 0
                trend_changes.append(f"  {product_name[:40]}: 신규 진입 (변동: NEW)")
                new_count += 1
        
        # 트렌드 변화 로그 출력 (처음 5개만)
        if trend_changes:
            print("📈 트렌드 변화:")
            for change in trend_changes[:5]:
                print(change)
            if len(trend_changes) > 5:
                print(f"   ... 외 {len(trend_changes) - 5}개")
        
        print(f"📊 매칭 결과: 기존 {matched_count}개, 신규 {new_count}개")
        
        return current_products
        
    except Exception as e:
        print(f"⚠️  트렌드 계산 오류: {e}")
        import traceback
        traceback.print_exc()
        # 오류 발생 시 트렌드 0으로 설정
        for product in current_products:
            product['trend'] = 0
        return current_products
def auto_romanize_korean(text: str) -> str:
    """
    한글을 로마자로 자동 변환
    
    Args:
        text: 한글 또는 영어 텍스트
        
    Returns:
        로마자 변환된 텍스트 (이미 영어면 그대로 반환)
    """
    try:
        # 한글이 포함되어 있는지 확인
        has_korean = any('\u3131' <= c <= '\u3163' or '\uac00' <= c <= '\ud7a3' for c in text)
        
        if has_korean:
            # Transliter 인스턴스 생성
            transliter = Transliter(academic)
            # 한글을 로마자로 변환
            romanized = transliter.translit(text)
            # 각 단어의 첫 글자를 대문자로 (Title Case)
            return romanized.title()
        else:
            # 이미 영어인 경우 그대로 반환
            return text
    except Exception as e:
        # 변환 실패 시 원본 반환
        print(f"⚠️  Romanization 오류 ({text}): {e}")
        return text


def normalize_product_name(name: str) -> str:
    """
    제품명에서 불필요한 키워드 제거
    
    Args:
        name: 원본 제품명
        
    Returns:
        정규화된 제품명
    """
    # [기획], [단품], (증정) 등 제거
    name = re.sub(r'\[.*?\]', '', name)
    # 괄호 안 내용 제거 (일부만)
    name = re.sub(r'\([^)]*기획[^)]*\)', '', name)
    name = re.sub(r'\([^)]*증정[^)]*\)', '', name)
    # +로 시작하는 부분 제거
    name = re.sub(r'\+.*$', '', name)
    # 여러 공백을 하나로
    name = re.sub(r'\s+', ' ', name)
    
    return name.strip()

def translate_brand_names(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    브랜드명을 영어로 변환 (매핑 + 자동 romanization 하이브리드)
    
    Args:
        products: 제품 리스트
        
    Returns:
        브랜드명이 영어로 변환된 제품 리스트
    """
    print("\n🌐 브랜드명 영어 변환 및 제품명 정규화 중...")
    
    new_brands = {}
    
    for product in products:
        korean_brand = product['brand'].strip()
        
        # 1. 매핑 테이블에서 영어 브랜드명 찾기 (우선순위)
        if korean_brand in BRAND_NAME_MAPPING:
            product['brand'] = BRAND_NAME_MAPPING[korean_brand]
        else:
            # 2. 자동 romanization
            romanized = auto_romanize_korean(korean_brand)
            product['brand'] = romanized
            new_brands[korean_brand] = romanized
        
        # 제품명 정규화 (불필요한 키워드 제거)
        product['productName'] = normalize_product_name(product['productName'])
    
    # 새로운 브랜드 로깅 (자동 변환된 브랜드)
    if new_brands:
        print(f"🆕 새로운 브랜드 자동 변환 ({len(new_brands)}개):")
        for korean, english in list(new_brands.items())[:5]:
            print(f"   - {korean} → {english}")
        if len(new_brands) > 5:
            print(f"   ... 외 {len(new_brands) - 5}개")
    
    print("✅ 브랜드명 변환 완료")
    
    return products

# 이전 translate_to_english 함수는 위의 translate_brand_names로 대체됨

async def translate_product_names_batch(model, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 제품명을 일괄 번역 (Batch Processing)
    
    Args:
        model: Gemini 모델
        products: 제품 리스트
        
    Returns:
        제품명이 영어로 번역된 제품 리스트
    """
    print("\n🌐 Gemini AI로 제품명 일괄 번역 중...")
    
    # 제품명 리스트 생성
    product_names = [f"{p['rank']}. {p['productName']}" for p in products]
    
    prompt = f"""
Translate the following Korean beauty product names into English.
Keep brand names as they are (already in English).
Focus on translating the product description/name part accurately.
Use professional beauty industry terminology.

Additionally, for each product, generate:
1. "nikIndex": A proprietary popularity score from 85.0 to 99.9 based on current K-beauty viral trends.
2. "culturalContext": A very short (max 1 sentence) explanation of why this is trending in Korea (e.g., "Trending on Olive Young for deep hydration", "Viral on TikTok for glass skin finish").
3. "imageQuery": A clean English search term to find this product's image (e.g., "Medicube Zero Pore Pad 2.0").

Product Names:
{chr(10).join(product_names)}

Response format (JSON):
{{
  "translations": [
    {{
      "rank": 1, 
      "productName": "English Product Name", 
      "nikIndex": 98.5, 
      "culturalContext": "Explanation",
      "imageQuery": "Search Term"
    }},
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
        
        # 번역 및 AI 데이터 적용
        translated_count = 0
        for trans in translations.get('translations', []):
            rank = trans.get('rank')
            product_name = trans.get('productName')
            nik_index = trans.get('nikIndex', 0)
            cultural_context = trans.get('culturalContext', "")
            image_query = trans.get('imageQuery', "")
            
            for product in products:
                if product['rank'] == rank:
                    product['productName'] = product_name
                    product['nikIndex'] = nik_index
                    product['culturalContext'] = cultural_context
                    # image_query는 나중에 아마존 검색용으로 사용 가능
                    if image_query:
                        product['buyUrl'] = f"https://www.amazon.com/s?k={image_query.replace(' ', '+')}&tag={os.getenv('NEXT_PUBLIC_AMAZON_AFFILIATE_ID', 'krank-20')}"
                    
                    translated_count += 1
                    break
        
        print(f"✅ 제품명 번역 완료 ({translated_count}/{len(products)}개)")
        
    except Exception as e:
        print(f"⚠️ Gemini 번역 오류: {e}")
        print("💡 폴백: 자동 로마자 변환(Romanization) 시도")
        # AI 번역 실패 시 로마자 변환으로 대체하여 한글 노출 방지
        for product in products:
            if any('\u3131' <= c <= '\u3163' or '\uac00' <= c <= '\ud7a3' for c in product['productName']):
                product['productName'] = auto_romanize_korean(product['productName'])
    
    return products


async def generate_tags(model, products: List[Dict[str, Any]], category: str = 'all') -> List[Dict[str, Any]]:
    """
    Gemini AI로 제품별 태그 자동 생성
    
    Args:
        model: Gemini 모델
        products: 제품 리스트
        category: 카테고리
        
    Returns:
        태그가 추가된 제품 리스트
    """
    print("\n🏷️  Gemini AI로 제품 태그 자동 생성 중...")
    
    # 카테고리별 기본 태그 매핑
    category_tags = {
        'all': ['Korean Beauty', 'Best Seller'],
        'skincare': ['Skincare', 'K-Beauty'],
        'suncare': ['Suncare', 'UV Protection'],
        'masks': ['Face Mask', 'Sheet Mask'],
        'makeup': ['Makeup', 'Cosmetics'],
        'haircare': ['Haircare', 'Hair Treatment'],
        'bodycare': ['Bodycare', 'Body Care']
    }
    
    # 제품 이름 리스트 생성 (영어 번역된 이름 사용)
    product_info = [f"{p['rank']}. {p['brand']} - {p['productName']}" for p in products]
    
    prompt = f"""
Analyze each beauty product and generate 2-3 unique, relevant tags based on the product's actual characteristics.

IMPORTANT: Each product must have DIFFERENT tags based on its name and brand.
- Identify product type (mask, serum, cream, sunscreen, toner, cleanser, ampoule, essence, etc.)
- Identify key benefits (hydrating, brightening, anti-aging, pore care, soothing, acne care, firming, etc.)
- Identify special features (vegan, dermatologist-tested, sensitive skin, natural ingredients, etc.)

DO NOT use generic tags like "Korean Beauty" or "Best Seller" for all products.
Each product should have unique tags that describe what it actually is.

Examples:
- "Medicube Collagen Jelly Cream" → ["Anti-Aging", "Firming", "Collagen Boost"]
- "Isntree Hyaluronic Acid Toner" → ["Hydrating Toner", "Hyaluronic Acid", "Moisture"]
- "Mediheal Tea Tree Mask Pack 10" → ["Sheet Mask", "Acne Care", "Tea Tree"]
- "AESTURA Atobarrier 365 Cream 80ml" → ["Barrier Cream", "Sensitive Skin", "Moisturizing"]

Products:
{chr(10).join(product_info)}

Response format (JSON):
{{
  "tags": [
    {{"rank": 1, "tags": ["Hydrating Toner", "Hyaluronic Acid", "Moisture"]}},
    {{"rank": 2, "tags": ["Anti-Aging Serum", "Wrinkle Care", "Peptide"]}},
    {{"rank": 3, "tags": ["Sheet Mask", "Brightening", "Vitamin C"]}},
    ...
  ]
}}

JSON only. Make sure each product has DIFFERENT tags that reflect its actual characteristics.
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
        print(f"기본 카테고리 태그 사용: {category}")
        
        # Gemini 실패 시 기본 카테고리 태그 사용
        default_tags = category_tags.get(category, ['Korean Beauty', 'Trending'])
        for product in products:
            product['tags'] = default_tags.copy()
    
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
        
        print(f"✅ 미디어 제목 번역 완료")
        
    except Exception as e:
        print(f"⚠️  미디어 제목 번역 오류: {e}")
        # 실패 시 영어 제목을 그대로 사용
        for item in items:
            item['titleKo'] = item['titleEn']
            
    return items

def get_google_place_stats(name: str, address: str) -> Dict[str, Any]:
    """
    Google Places API (New)를 사용하여 장소의 상세 통계(평점, 리뷰 수)를 가져옴
    """
    api_key = os.getenv('GOOGLE_PLACES_API_KEY') or os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return {}
        
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.rating,places.userRatingCount,places.googleMapsUri,places.photos"
    }
    
    # "장소명 + 주소(일부)"로 검색하여 정확도 높임
    search_query = f"{name} {address.split()[:2]}" 
    data = {
        "textQuery": search_query,
        "languageCode": "en",
        "maxResultCount": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            places = response.json().get("places", [])
            if places:
                p = places[0]
                return {
                    "rating": p.get("rating", 0),
                    "userRatingCount": p.get("userRatingCount", 0),
                    "googleMapsUri": p.get("googleMapsUri", ""),
                    "photo_name": p.get("photos", [{}])[0].get("name", "") if p.get("photos") else ""
                }
    except Exception as e:
        print(f"⚠️ Google Places API 검색 중 오류 ({name}): {e}")
        
    return {}

async def scrape_tour_api(max_items: int = 50) -> List[Dict[str, Any]]:
    """
    한국관광공사 TourAPI를 통해 인기 여행지 정보 수집
    """
    api_key = os.getenv('TOUR_API_KEY')
    if not api_key:
        print("❌ TOUR_API_KEY not found in environment")
        return []

    # areaBasedList2 엔드포인트 (국문 서비스가 데이터가 가장 풍부함)
    base_url = "https://apis.data.go.kr/B551011/KorService2/areaBasedList2"
    
    # 공통 파라미터 (arrange=B: 인기순)
    common_params = f"&numOfRows={max_items}&pageNo=1&MobileOS=ETC&MobileApp=KRank&_type=json&arrange=B"

    content_types = [12, 14, 15]
    all_places = []
    
    for c_type in content_types:
        try:
            print(f"🌐 TourAPI 요청 중 (contentTypeId: {c_type})...")
            # serviceKey를 직접 포함한 URL 생성 (Double Encoding 방지)
            url = f"{base_url}?serviceKey={api_key}{common_params}&contentTypeId={c_type}"
            
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception:
                    print(f"❌ JSON 파싱 실패: {response.text[:200]}")
                    continue

                if not isinstance(data, dict):
                    print(f"❌ 예상치 못한 응답 형식: {data}")
                    continue

                # 안전하게 중첩된 데이터 추출
                response_obj = data.get("response", {})
                if not isinstance(response_obj, dict):
                    print(f"❌ TourAPI 응답 오류 (response가 dict 아님): {response_obj}")
                    continue
                
                body = response_obj.get("body", {})
                if not isinstance(body, dict):
                    if "resultCode" in data:
                        print(f"❌ TourAPI 비즈니스 오류: {data.get('resultMsg')} (Code: {data.get('resultCode')})")
                    else:
                        print(f"❌ TourAPI 응답 오류 (body가 dict 아님): {body}")
                    continue
                
                items_obj = body.get("items", {})
                items = []
                if isinstance(items_obj, dict):
                    items = items_obj.get("item", [])
                elif isinstance(items_obj, str) and not items_obj:
                    items = []
                
                if not items:
                    print(f"⚠️ contentTypeId {c_type}에 데이터가 없습니다.")
                    continue

                if isinstance(items, dict):
                    items = [items]
                
                for item in items:
                    title = item.get("title")
                    if not title: continue
                    
                    place = {
                        "name_ko": title,
                        "name_en": title, # Gemini 단계에서 번역됨
                        "address_ko": item.get("addr1", ""),
                        "location": item.get("addr1", "").split()[0] if item.get("addr1") else "Unknown",
                        "imageUrl": item.get("firstimage") or "https://images.unsplash.com/photo-1544273677-277914bd9466?w=800&fit=crop",
                        "mapx": item.get("mapx"),
                        "mapy": item.get("mapy"),
                        "content_id": item.get("contentid"),
                        "content_type": c_type,
                        "views": "N/A",  # TourAPI에서 직접 제공되지 않음
                        "category": "Culture", # Gemini 단계에서 업데이트 가능
                    }
                    all_places.append(place)
            else:
                print(f"❌ TourAPI 요청 실패 (HTTP {response.status_code})")
        except Exception as e:
            print(f"❌ TourAPI 오류: {e}")

    # 통합 후 조회수 기반으로 다시 정렬하거나 섞어서 상위 N개 추출 (여기서는 단순히 합침)
    # 실제로는 국문 서비스에서 조회수를 가져와야 정확하지만, 
    # EngService의 arrange=B도 어느 정도 작동함.
    return all_places[:max_items]

async def enrich_place_data(model, places: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 장소 정보 강화 (영문 번역, AI Story, Photo Spot, Klook Keyword)
    """
    if not places:
        return []

    print("\n🤖 Gemini AI로 장소 정보 강화 중...")
    
    enriched_places = []
    
    for i, place in enumerate(places, 1):
        prompt = f"""
Analyze this South Korean tourist spot: "{place['name_en']}" (Address: {place['address_ko']})
Generate the following information in JSON format:
1. "name_en": Official or well-known English name.
2. "ai_story": A fascinating 2-line story about its historical or cultural context.
3. "photo_spot": A specific tip for the best "Pro Photo Spot" angle (Instagrammable).
4. "tags": An array of 3 short keywords representing the vibe (e.g., ["Nature", "Hiking", "Autumn"]).
5. "category": One of these three categories: "Culture" (for palaces, temples, history), "Nature" (for mountains, beaches, parks), or "Modern" (for shopping, cafes, urban).
6. "hype_score": A score from 1-100 based on current SNS trend, Naver Map "Saves" level, and global search volume.
7. "klook_keyword": A search keyword for Klook (e.g., "Nami Island Tour").
8. "image_query": A high-quality English search keyword to find a representative photo of this place (e.g., "Gyeongbokgung Palace", "Myeongdong Night").

JSON only.
"""
        try:
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            ai_data = json.loads(result_text)
            
            place["name_en"] = ai_data.get("name_en", place["name_en"])
            place["ai_story"] = ai_data.get("ai_story", "")
            place["photo_spot"] = ai_data.get("photo_spot", "")
            place["tags"] = ai_data.get("tags", ["Must Visit", "South Korea", "Trending"])
            place["category"] = ai_data.get("category", "Culture")
            ai_hype_score = ai_data.get("hype_score", 50)
            # 2. Hybrid Verification with Google Places Data
            google_data = get_google_place_stats(place["name_en"], place["address_ko"])
            
            if google_data:
                g_rating = google_data.get("rating", 0)
                g_reviews = google_data.get("userRatingCount", 0)
                # Google Hype Score = (Rating/5) * log10(Reviews+1) * 20 
                # (최대 점수를 약 100으로 수렴하게 설계)
                google_hype = (g_rating / 5.0) * min(5, math.log10(g_reviews + 1)) * 20
                final_hype_score = int((google_hype * 0.7) + (ai_hype_score * 0.3))
                place["google_maps_url"] = google_data.get("googleMapsUri", "")
                print(f"    🔍 Google Verified: Rating {g_rating}, Reviews {g_reviews} -> Score: {int(google_hype)}")
            else:
                final_hype_score = ai_hype_score # Fallback to AI estimation
            
            # Commercial Match Bonus
            commercial_keywords = ["Palace", "Nami Island", "DMZ", "Seongsu", "Hannam", "Lotte World", "Everland"]
            commercial_bonus = 20 if any(kw.lower() in place["name_en"].lower() for kw in commercial_keywords) else 0
            
            # Final Score Calculation (Mixed Engine)
            # FinalScore = (TourAPI_Views_Index * 0.4) + (Hybrid_Hype_Score * 0.4) + (Commercial_Bonus * 0.2)
            try:
                base_views = int(place.get("views", 0)) if place.get("views") != "N/A" else 0
            except:
                base_views = 0
            
            # Normalize views index (relative)
            # 10,000 views -> approx 40 points in weighting
            views_weight = min(40, (base_views / 10000.0) * 40)
            
            place["final_score"] = views_weight + (final_hype_score * 0.4) + (commercial_bonus)
            place["hype_score"] = final_hype_score

            # Link & Data Generation
            klook_keyword = ai_data.get("klook_keyword", place["name_en"])
            place["klook_url"] = f"https://www.klook.com/en-US/search?query={klook_keyword.replace(' ', '%20')}&action=search"
            place["creatrip_url"] = f"https://www.creatrip.com/en/search?keyword={place['name_en'].replace(' ', '%20')}"
            
            # Determine priority_platform
            if place["category"] == "Culture":
                place["priority_platform"] = "Creatrip"
                place["booking_url"] = place["creatrip_url"]
            else:
                place["priority_platform"] = "Klook"
                place["booking_url"] = place["klook_url"]

            # Image logic enhancement: Use Google Photo > TourAPI > AI Fallback
            api_key = os.getenv('GOOGLE_PLACES_API_KEY') or os.getenv('GOOGLE_MAPS_API_KEY')
            
            # 1. Check if Google has a real photo
            if google_data and google_data.get("photo_name") and api_key:
                photo_ref = google_data["photo_name"]
                place["imageUrl"] = f"https://places.googleapis.com/v1/{photo_ref}/media?maxWidthPx=1200&maxHeightPx=800&key={api_key}"
                print(f"    📸 Image Source: Google Places (Verified)")
            # 2. If no Google photo, Check if TourAPI is valid
            elif not place.get("imageUrl") or "photo-1544273677-277914bd9466" in place["imageUrl"]:
                # 3. Last Resort: AI Guided category fallback
                print(f"    ⚠️ Image Source: AI Category Fallback (TourAPI/Google missing)")
                category_id_map = {
                    "Culture": "1544273677-277914bd9466",
                    "Nature": "1538332152395-65715509746e",
                    "Modern": "1538485399081-7191377e8241"
                }
                cid = category_id_map.get(place["category"], "1544273677-277914bd9466")
                place["imageUrl"] = f"https://images.unsplash.com/photo-{cid}?w=800&fit=crop"
            else:
                print(f"    🖼️ Image Source: TourAPI (External)")

            place["verified_by_mix"] = True
            enriched_places.append(place)
            print(f"  ✅ {i}. {place['name_en']} 강화 완료 (Hype: {ai_hype_score}, Bonus: {commercial_bonus})")
        except Exception as e:
            print(f"⚠️ {place['name_en']} 강화 중 오류: {e}")
            place["ai_story"] = "Discover the hidden gem of Korea."
            place["photo_spot"] = "Best captured at golden hour."
            place["tags"] = ["Must Visit", "South Korea"]
            place["booking_url"] = f"https://www.klook.com/en-US/search?query={place['name_en'].replace(' ', '%20')}&action=search"
            place["hype_score"] = 50
            place["final_score"] = 50
            place["verified_by_mix"] = False
            enriched_places.append(place)
            enriched_places.append(place)

    # Sort by final_score descending
    enriched_places.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    # Re-assign rank
    for i, place in enumerate(enriched_places, 1):
        place["rank"] = i
        
    return enriched_places

async def calculate_place_trends(db, current_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Place 랭킹 트렌드 계산"""
    from datetime import timedelta
    
    try:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        doc_id = f"{yesterday}_place"
        
        print(f"\n📊 Place 트렌드 계산 중... (어제: {yesterday})")
        
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            for item in current_items:
                item['trend'] = 0
            return current_items
        
        yesterday_items = doc.to_dict().get('items', [])
        
        for current in current_items:
            # 이름으로 매칭
            yesterday_rank = None
            for old_item in yesterday_items:
                if old_item.get('name_en') == current.get('name_en'):
                    yesterday_rank = old_item.get('rank')
                    break
            
            if yesterday_rank:
                current['trend'] = yesterday_rank - current['rank']
            else:
                current['trend'] = 0
                
        return current_items
    except Exception as e:
        print(f"⚠️ Place 트렌드 계산 오류: {e}")
        for item in current_items:
            item['trend'] = 0
        return current_items

async def calculate_media_trends(db, current_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """미디어 랭킹 트렌드 계산"""
    from datetime import timedelta
    
    try:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%Y-%m-%d')
        doc_id = f"{yesterday}_media"
        
        print(f"\n📊 Media 트렌드 계산 중... (어제: {yesterday})")
        
        doc_ref = db.collection('daily_rankings').document(doc_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            print(f"⚠️  어제 Media 데이터 없음 (문서 ID: {doc_id})")
            print("💡 첫 실행이거나 어제 데이터가 없습니다. 트렌드 0으로 설정")
            for item in current_items:
                item['trend'] = 0
            return current_items
        
        yesterday_items = doc.to_dict().get('items', [])
        print(f"✅ 어제 Media 데이터 {len(yesterday_items)}개 발견")
        
        trend_changes = []
        matched_count = 0
        new_count = 0
        
        for current in current_items:
            title_en = current.get('titleEn', '')
            title_ko = current.get('titleKo', '')
            current_rank = current['rank']
            
            # 영어 제목 또는 한국어 제목으로 매칭
            yesterday_rank = None
            for old_item in yesterday_items:
                if (old_item.get('titleEn') == title_en or 
                    old_item.get('titleKo') == title_ko):
                    yesterday_rank = old_item.get('rank')
                    break
            
            if yesterday_rank:
                trend = yesterday_rank - current_rank
                current['trend'] = trend
                trend_symbol = '+' if trend > 0 else ''
                trend_changes.append(f"  {title_ko or title_en}: {yesterday_rank}위 → {current_rank}위 (변동: {trend_symbol}{trend})")
                matched_count += 1
            else:
                current['trend'] = 0
                trend_changes.append(f"  {title_ko or title_en}: 신규 진입 (변동: NEW)")
                new_count += 1
        
        # 트렌드 변화 로그 출력
        if trend_changes:
            print("📈 Media 트렌드 변화:")
            for change in trend_changes[:5]:
                print(change)
            if len(trend_changes) > 5:
                print(f"   ... 외 {len(trend_changes) - 5}개")
        
        print(f"📊 매칭 결과: 기존 {matched_count}개, 신규 {new_count}개")
                
        return current_items
    except Exception as e:
        print(f"⚠️ 미디어 트렌드 계산 오류: {e}")
        import traceback
        traceback.print_exc()
        for item in current_items:
            item['trend'] = 0
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
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
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
    run_mode = sys.argv[1] if len(sys.argv) > 1 else "all"  # "beauty", "media", "place", "all"
    
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
                
                # 카테고리별 크롤링 (무신사 뷰티 상위 20개)
                products = scrape_musinsa_beauty_by_category(
                    category_code=config['url_param'],
                    max_items=20
                )
                
                if not products:
                    print(f"⚠️  {category_key} 카테고리에서 제품을 찾지 못했습니다.")
                    continue
                
                # 브랜드명 영어 변환 (먼저 실행)
                products = translate_brand_names(products)
                
                # 제품명 영어 번역 (Batch Processing)
                products = await translate_product_names_batch(model, products)
                
                # 아마존 이미지 연동
                print("\n📸 아마존에서 제품 이미지 검색 중...")
                for product in products:
                    search_query = f"{product['brand']} {product['productName']}"
                    amazon_img = await get_amazon_image(search_query)
                    if amazon_img:
                        product['imageUrl'] = amazon_img
                        print(f"  ✅ {product['rank']}위 이미지 매칭 성공")
                    else:
                        print(f"  ⚠️ {product['rank']}위 아마존 이미지 검색 실패")
                
                # 트렌드 계산 (번역 후 실행하여 영어 제품명으로 매칭)
                products = await calculate_trends(db, category_key, products)
                
                # 태그 자동 생성
                products = await generate_tags(model, products, category_key)
                
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
                # 한국어 제목 번역 (먼저 실행)
                all_media_items = await translate_media_titles(model, all_media_items)
                
                # 트렌드 계산 (번역 후 실행하여 영어/한국어 제목으로 매칭)
                all_media_items = await calculate_media_trends(db, all_media_items)
                
                # Media 저장 로직
                today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
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

        # 5. Place 카테고리 크롤링
        if run_mode in ["place", "all"]:
            print("\n" + "=" * 60)
            print("🗺️  PLACE 카테고리 크롤링 (TourAPI)")
            print("=" * 60)
            
            # TourAPI 수집
            place_items = await scrape_tour_api(max_items=50)
            
            if place_items:
                # Gemini AI 강화
                place_items = await enrich_place_data(model, place_items)
                
                # 트렌드 계산
                place_items = await calculate_place_trends(db, place_items)
                
                # 저장
                today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                doc_id = f"{today}_place"
                doc_ref = db.collection('daily_rankings').document(doc_id)
                
                data = {
                    'date': today,
                    'category': 'place',
                    'items': place_items,
                    'updatedAt': firestore.SERVER_TIMESTAMP
                }
                
                doc_ref.set(data)
                print(f"✅ {len(place_items)}개 명소를 {doc_id} 문서에 저장 완료")
                total_products += len(place_items)
            else:
                print("⚠️ TourAPI에서 데이터를 찾지 못했습니다.")
        
        print("\n" + "=" * 60)
        print("✅ 모든 크롤링 완료!")
        print("=" * 60)
        
        # 결과 요약
        print(f"\n📊 크롤링 결과:")
        print(f"  - 총 아이템 수: {total_products}개")
        print(f"  - 실행 모드: {run_mode.upper()}")

        # 데이터 검증: 수집된 데이터가 하나도 없으면 실패로 간주
        if total_products == 0:
            print(f"\n❌ [CRITICAL] {run_mode.upper()} 모드에서 수집된 데이터가 0개입니다.")
            print("💡 크롤링 대상 사이트의 구조가 변경되었거나 접근이 차단되었을 수 있습니다.")
            sys.exit(1)
        
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
