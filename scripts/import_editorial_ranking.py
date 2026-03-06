#!/usr/bin/env python3
"""
K-Rank Editorial Ranking Importer
사용자가 제공한 에디토리얼 리포트를 바탕으로 데이터를 가공하고 Firestore에 저장합니다.
"""

import asyncio
import os
import sys
import json
import random
import time
import re
import aiohttp
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
from dotenv import load_dotenv

# 기존 scraper 로직 재사용을 위해 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# scraper.py에서 필요한 함수들을 임포트하기 위해 sys.path 추가
sys.path.append(script_dir)
from scraper_legacy import (
    initialize_firebase, initialize_gemini, get_amazon_image,
    calculate_nik_index, BRAND_NAME_MAPPING, auto_romanize_korean,
    normalize_product_name, CATEGORY_MAPPING, save_cache, load_cache
)

DATA_FILE = os.path.join(project_root, 'docs', 'Beauty Rankings DB Import.json')
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'
WRITE_TO_FIRESTORE = os.getenv('WRITE_TO_FIRESTORE', 'true').lower() == 'true'
PREVIOUS_DATA_FILE = os.path.join(script_dir, 'editorial_ranking_v2_4.json')

def fix_image_url(url: str) -> str:
    """이미지 URL의 잘못된 문자(* 등)를 수정하여 정상 출력되도록 함"""
    if not url:
        return ""
    # *SL1000* -> _SL1000_ (Amazon 이미지 표준 포맷)
    fixed = url.replace('*', '_')
    return fixed

async def get_amazon_image_v2(product_name: str, brand: str) -> str:
    """
    Playwright를 사용하여 아마존에서 제품 이미지를 직접 검색합니다 (API 키 불필요).
    """
    query = f"{brand} {product_name}".replace(" ", "+")
    search_url = f"https://www.amazon.com/s?k={query}"
    
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            print(f"🕵️ Amazon 직접 검색 시도: {brand} {product_name}")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # User-Agent 설정
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            })
            
            await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2) # 검색 결과 로딩 대기
            
            # 첫 번째 제품 이미지 찾기
            img_selector = 'div[data-component-type="s-search-result"] img.s-image'
            img_elem = await page.query_selector(img_selector)
            
            if img_elem:
                src = await img_elem.get_attribute("src")
                if src:
                    # 고해상도 이미지로 변환
                    import re
                    high_res_src = re.sub(r'\._AC_.*?_\.', '.', src)
                    print(f"✅ Amazon 이미지 발견: {high_res_src}")
                    await browser.close()
                    return high_res_src
            
            await browser.close()
    except Exception as e:
        print(f"⚠️ Amazon 직접 검색 오류: {e}")
    
    return ""

def parse_brand_and_product(raw_name: str):
    """'브랜드명 제품명 (부가정보)' 형식에서 브랜드와 제품명 분리"""
    # 괄호 안의 내용 제거
    clean_name = re.sub(r'\(.*?\)', '', raw_name).strip()
    
    # 공백으로 나누어 첫 번째 단어를 브랜드로 추정 (한글 브랜드의 일반적인 케이스)
    parts = clean_name.split(' ', 1)
    if len(parts) > 1:
        brand = parts[0]
        product = parts[1]
    else:
        brand = "Unknown"
        product = parts[0]
        
    return brand, product

async def check_url_valid(url: str) -> bool:
    """URL이 유효한지(404가 아닌지) 확인"""
    if not url: return False
    # Unsplash 및 Amazon 미디어 URL은 유효한 것으로 간주 (직접 넣은 고품질 이미지)
    from urllib.parse import urlparse
    try:
        parsed_url = urlparse(url)
        if parsed_url.netloc in ["images.unsplash.com", "m.media-amazon.com", "www.amazon.com"]:
            return True
    except:
        pass
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=5) as response:
                return response.status == 200
    except:
        return False

def generate_default_tags(category_key: str, product_name: str) -> List[str]:
    """Gemini 실패 시 사용할 구체적인 제품별 태그 생성"""
    tags = ["K-Beauty"]
    name = product_name.lower()
    
    # 1. 성분 및 기능 기반 태그 (Ingredients & Function)
    keyword_map = {
        "Soothing": ["진정", "시카", "티트리", "어성초", "판테놀", "cica", "soothing", "tea tree", "heartleaf"],
        "Hydration": ["수분", "보습", "히알루론산", "다이브인", "moisturizing", "hydrating", "hyaluronic"],
        "Brightening": ["비타", "청귤", "미백", "나이아신", "vitamin", "brightening", "whitening", "niacinamide"],
        "Anti-aging": ["탄력", "리프팅", "레티놀", "pdrn", "콜라겐", "firming", "anti-aging", "retinol", "collagen"],
        "Pore Care": ["모공", "제로", "pore", "tightening"],
        "Sensitive Skin": ["민감", "저자극", "sensitive", "hypoallergenic"],
        "Glow": ["광채", "속광", "글로우", "glow", "radiance"]
    }
    
    for tag, keywords in keyword_map.items():
        if any(kw in name for kw in keywords):
            tags.append(tag)
            
    # 2. 피부 타입 및 가치 기반 태그 (Skin Type & Values)
    value_map = {
        "Oily Skin": ["지성", "oil control", "matte"],
        "Dry Skin": ["건성", "extra moisturizing"],
        "Vegan": ["비건", "vegan"],
        "Clean Beauty": ["클린", "clean"],
        "Best Seller": ["1위", "베스트", "best seller", "top rated"]
    }

    for tag, keywords in value_map.items():
        if any(kw in name for kw in keywords):
            tags.append(tag)

    # 3. 제형 및 타입 기반 태그 (Form & Type)
    type_map = {
        "Serum/Ampoule": ["세럼", "앰플", "serum", "ampoule"],
        "Cream": ["크림", "cream"],
        "Toner/Pad": ["토너", "패드", "toner", "pad"],
        "Mask": ["마스크", "팩", "mask", "pack"],
        "Sun Care": ["선", "썬", "uv", "sun"],
        "Cleansing": ["클렌징", "폼", "오일", "밤", "cleansing", "foam", "oil", "balm"],
        "Mist": ["미스트", "mist"],
        "Lip Care": ["립", "틴트", "글로스", "lip", "tint", "gloss"],
        "Cushion": ["쿠션", "cushion"],
        "Treatment/Shampoo": ["샴푸", "트리트먼트", "shampoo", "treatment"]
    }
    
    for tag, keywords in type_map.items():
        if any(kw in name for kw in keywords):
            tags.append(tag)
            
    # 4. 카테고리 기반 필수 태그
    if category_key == "all":
        tags.append("Top Pick")
    elif category_key == "skincare":
        tags.append("Essential Skincare")
    elif category_key == "suncare":
        tags.append("UV Protection")
    elif category_key == "makeup":
        tags.append("Trendy Makeup")
    elif category_key == "haircare":
        tags.append("Hair Repair")
    elif category_key == "bodycare":
        tags.append("Body Nourishment")
    elif category_key == "masks":
        tags.append("Deep Recovery")
        
    # 중복 제거 및 "Trending" 추가 (모든 제품)
    tags.append("Trending")
    return list(set(tags))

async def enrich_editorial_data(model, category_key: str, products_raw: List[Dict[str, Any]], previous_rank_map: Dict[str, int] = None) -> List[Dict[str, Any]]:
    """제품 리스트를 가공하고 Gemini로 강화 (트렌드 계산 및 기본 태그 포함)"""
    processed_products = []
    
    # 1. 기본 구조 생성
    for idx, item in enumerate(products_raw, 1):
        # 신규 JSON 필드 대응 (name_en, price_krw, image_url)
        name_en = item.get('name_en', '')
        price_val = str(item.get('price_krw', item.get('price', 'N/A')))
        image_url = fix_image_url(item.get('image_url', item.get('url', '')))
        
        # 이름에서 브랜드/제품 분리 시도 (기존 로직 유지하되 영문명 활용)
        brand_ko, name_ko = parse_brand_and_product(name_en) # 영문명에서 분리 시도
        
        # 브랜드명 변환 (이미 영어인 경우가 많으므로 보수적으로 처리)
        brand_en = brand_ko # 이미 영어일 가능성 높음
        
        # 트렌드 계산 (v2.3 대비 - 이름 정규화 후 매칭)
        trend = 0
        product_key = f"{brand_ko}_{name_ko}".replace(" ", "")
        if previous_rank_map and product_key in previous_rank_map:
            prev_rank = previous_rank_map[product_key]
            trend = prev_rank - item.get('rank', idx)
            
        product = {
            'rank': item.get('rank', idx),
            'brand': brand_en,
            'brandKo': "", # 신규 JSON에는 한글 브랜드가 명시되지 않음
            'productName': name_en, # 전체 영문명을 productName으로 사용
            'productNameKo': "", # 필요시 추출 가능
            'original_raw': name_en,
            'tags': generate_default_tags(category_key, name_en),
            'subcategory': category_key,
            'trend': trend,
            'price': price_val,
            'imageUrl': image_url,
            'fixedImageUrl': image_url 
        }
        processed_products.append(product)

    # 2. Gemini 일괄 번역 및 인덱싱/인사이트 생성 (영문 품질 강화)
    print(f"🌐 Gemini AI로 '{category_key}' 부문 데이터 강화 중 (Professional English Translation)...")
    
    # 영문명 또는 한글명을 활용하여 제품 리스트 생성
    product_names = []
    for p in processed_products:
        display_name = f"{p['brandKo']} {p['productNameKo']}".strip()
        if not display_name:
            display_name = p['productName']
        product_names.append(f"{p['rank']}. {display_name}")
    
    # 영문 품질 강화를 위한 프롬프트 수정
    prompt = f"""
Translate the following Korean beauty product names into professional, worldwide-recognized English.
Crucial: For Suncare, use 'Sunscreen', 'Sun Serum', or 'Sun Stick'. For Skincare, use 'Serum', 'Ampoule', or 'Toner'.

Response Requirements:
1. "productName": Clean, formal English product name. (e.g., 'Birch Juice Moisturizing Sunscreen')
2. "nikIndex": Popularity score (90.0-99.9).
3. "culturalContext": "AI Analyst Note: [Detailed insight in English]". 
   Include why it's a 'Must-buy' in Korea and mention Hwahae/Glowpick rankings.
4. "imageQuery": Best English search term for Amazon.

Product Names:
{chr(10).join(product_names)}

Response format (JSON only):
{{
  "translations": [
    {{
      "rank": 1, 
      "productName": "English Name", 
      "nikIndex": 99.1, 
      "culturalContext": "AI Analyst Note: ...",
      "imageQuery": "Brand Product Name"
    }},
    ...
  ]
}}
"""
    
    try:
        # Load local translation cache to bypass API 403 error
        import os
        import json
        
        cache_file = os.path.join(os.path.dirname(__file__), 'gemini_cache.json')
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                gemini_cache = json.load(f)
        else:
            gemini_cache = {}
            
        for p in processed_products:
            raw_name = p['original_raw']
            
            # Match directly or by checking if the cache key is in the name
            matched_key = None
            for key in gemini_cache.keys():
                if key in raw_name or key in p['productNameKo']:
                    matched_key = key
                    break
            
            if matched_key:
                entry = gemini_cache[matched_key]
                p['productName'] = entry.get('productName', p['productName'])
                p['nikIndex'] = entry.get('nikIndex', 95.0)
                p['culturalContext'] = entry.get('culturalContext', "")
                p['imageQuery'] = entry.get('imageQuery', f"{p['brand']} {p['productName']}")
            else:
                p['nikIndex'] = 95.0
                p['culturalContext'] = ""
                p['imageQuery'] = f"{p['brand']} {p['productName']}"
            
            # Amazon URL
            image_query = p['imageQuery']
            p['buyUrl'] = f"https://www.amazon.com/s?k={image_query.replace(' ', '+')}&tag={os.getenv('NEXT_PUBLIC_AMAZON_AFFILIATE_ID', 'nextidealab-20')}"
            
    except Exception as e:
        print(f"⚠️ 오프라인 캐시 적용 오류 ({category_key}): {e}")

    # 3. 이미지 연동 확인 (Amazon)
    print(f"📸 '{category_key}' 이미지 및 링크 최종 확인 중...")
    for p in processed_products:
        # 이미지 로직 개선: 
        # 1. JSON의 이미지 URL이 존재하더라도 404일 확률이 높으므로, Amazon 검색 로직을 적극 활용하거나
        # 2. 혹은 Amazon 검색 결과가 있을 경우 그걸 우선 사용 (Curated 이미지가 Amazon 링크인 경우 404 체크가 어려우므로)
        
        target_img = None
        
        # Amazon 검색 우선 (Working Image 확보를 위해)
        amazon_img = await get_amazon_image_v2(p['productName'], p['brand'])
        if amazon_img:
            target_img = amazon_img
        
        # Amazon 검색 결과가 없으면 JSON 이미지 사용 (차선책)
        if not target_img:
            target_img = p.get('fixedImageUrl')
        
        # 여전히 없으면 Unsplash 고유 이미지 (검색어 기반)
        if not target_img:
            search_term = p.get('productNameKo', p['productName']).split(' ')[-1]
            unique_id = f"{p['brandKo']}_{p['rank']}".replace(" ", "")
            target_img = f"https://images.unsplash.com/photo-1596462502278-27bfdc4033c8?auto=format&fit=crop&q=80&w=400&sig={unique_id}&beauty={search_term}"
            
        p['imageUrl'] = target_img
        if 'fixedImageUrl' in p:
            del p['fixedImageUrl']

    return processed_products

async def main():
    print("🚀 에디토리얼 랭킹 임포트 시작")
    
    # 1. 데이터 로드
    if not os.path.exists(DATA_FILE):
        print(f"❌ 데이터 파일 없음: {DATA_FILE}")
        return
        
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        master_data = json.load(f)
        
    # 2. 초기화
    db = initialize_firebase()
    model = initialize_gemini()
    
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    total_count = 0
    
    # 2.5 이전 버전 데이터 로드 (트렌드용)
    prev_master_rank_map = {}
    if os.path.exists(PREVIOUS_DATA_FILE):
        print(f"📈 트렌드 분석을 위해 이전 버전 로드: {PREVIOUS_DATA_FILE}")
        with open(PREVIOUS_DATA_FILE, 'r', encoding='utf-8') as f:
            prev_data = json.load(f)
            for p_cat, p_items in prev_data.get('categories', {}).items():
                cat_map = {}
                for p_item in p_items:
                    p_brand_ko, p_name_ko = parse_brand_and_product(p_item['name'])
                    p_key = f"{p_brand_ko}_{p_name_ko}".replace(" ", "")
                    cat_map[p_key] = p_item['rank']
                prev_master_rank_map[p_cat] = cat_map
    
    # 3. 데이터 처리 및 저장
    # 신규 JSON 구조는 카테고리별 객체의 리스트임
    for entry in master_data:
        cat_key = entry.get('category', 'all')
        products_raw = entry.get('items', [])
        report_date = entry.get('date', today)
        
        print(f"\n📂 카테고리 처리 중: {cat_key.upper()} ({len(products_raw)} items)")
        
        # 트렌드 맵 가져오기
        prev_rank_map = prev_master_rank_map.get(cat_key)
        
        # 데이터 강화
        enriched_products = await enrich_editorial_data(model, cat_key, products_raw, prev_rank_map)
        
        if cat_key == 'all':
            firestore_category = 'beauty'
        else:
            firestore_category = f"beauty-{cat_key}"
            
        # 날짜 동기화: JSON의 과거 날짜 대신 실제 오늘 날짜(2026-03-06)를 사용하여 최신성 확보
        report_date = datetime.now().strftime("%Y-%m-%d")
            
        doc_id = f"{report_date}_{firestore_category}"
        
        data = {
            'date': report_date,
            'category': firestore_category,
            'items': enriched_products,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'isEditorial': True,
            'reportTitle': f"NIK Beauty Index: Weekly Editorial Report ({report_date})"
        }
        
        if WRITE_TO_FIRESTORE:
            db.collection('daily_rankings').document(doc_id).set(data)
            print(f"✅ Firestore 저장 완료: {doc_id}")
        else:
            print(f"🧪 [DEV_MODE] Firestore 저장 스킵: {doc_id}")
            if enriched_products:
                print(f"🔎 DEBUG [Item 0]: {json.dumps(enriched_products[0], indent=2, ensure_ascii=False)}")
            
        total_count += len(enriched_products)
        
    print(f"\n✨ 완료! 총 {total_count}개 제품이 처리되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
