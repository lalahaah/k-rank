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
from scraper import (
    initialize_firebase, initialize_gemini, get_amazon_image,
    calculate_nik_index, BRAND_NAME_MAPPING, auto_romanize_korean,
    normalize_product_name, CATEGORY_MAPPING, save_cache, load_cache
)

# 설정
DATA_FILE = os.path.join(script_dir, 'editorial_ranking_v2_4.json')
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'
WRITE_TO_FIRESTORE = os.getenv('WRITE_TO_FIRESTORE', 'true').lower() == 'true'
PREVIOUS_DATA_FILE = os.path.join(script_dir, 'editorial_ranking_v2_3.json')

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
    if "images.unsplash.com" in url or "m.media-amazon.com" in url: return True
    
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
            
    # 2. 제형 및 타입 기반 태그 (Form & Type)
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
            
    # 3. 카테고리 기반 필수 태그
    if category_key == "all":
        tags.append("Bestseller")
    elif category_key == "suncare":
        tags.append("UV Protection")
    elif category_key == "haircare":
        tags.append("Hair Repair")
    elif category_key == "bodycare":
        tags.append("Body Nourishment")
        
    # 중복 제거 및 "Trending" 추가 (모든 제품)
    tags.append("Trending")
    return list(set(tags))

async def enrich_editorial_data(model, category_key: str, products_raw: List[Dict[str, Any]], previous_rank_map: Dict[str, int] = None) -> List[Dict[str, Any]]:
    """제품 리스트를 가공하고 Gemini로 강화 (트렌드 계산 및 기본 태그 포함)"""
    processed_products = []
    
    # 1. 기본 구조 생성
    for idx, item in enumerate(products_raw, 1):
        raw_name = item['name']
        price_val = str(item.get('price', 'N/A'))
        image_url = item.get('url', '')
        
        brand_ko, name_ko = parse_brand_and_product(raw_name)
        
        # 브랜드명 변환
        brand_en = BRAND_NAME_MAPPING.get(brand_ko, auto_romanize_korean(brand_ko))
        
        # 트렌드 계산 (v2.3 대비)
        trend = 0
        product_key = f"{brand_ko}_{name_ko}".replace(" ", "")
        if previous_rank_map and product_key in previous_rank_map:
            prev_rank = previous_rank_map[product_key]
            trend = prev_rank - item.get('rank', idx)
            
        product = {
            'rank': item.get('rank', idx),
            'brand': brand_en,
            'brandKo': brand_ko,
            'productName': name_ko,
            'productNameKo': name_ko,
            'original_raw': raw_name,
            'tags': generate_default_tags(category_key, raw_name),
            'subcategory': category_key,
            'trend': trend,
            'price': price_val,
            'imageUrl': image_url,
            'fixedImageUrl': image_url # JSON에서 온 이미지를 보존하기 위해 별도 필드 저장
        }
        processed_products.append(product)

    # 2. Gemini 일괄 번역 및 인덱싱/인사이트 생성 (영문 품질 강화)
    print(f"🌐 Gemini AI로 '{category_key}' 부문 데이터 강화 중 (Professional English Translation)...")
    
    product_names = [f"{p['rank']}. {p['brandKo']} {p['productNameKo']}" for p in processed_products]
    
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
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # JSON 파싱
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        
        translations = json.loads(result_text)
        
        if translations and "translations" in translations:
            for entry in translations["translations"]:
                rank = entry.get('rank')
                for p in processed_products:
                    if p['rank'] == rank:
                        p['productName'] = entry.get('productName', p['productName'])
                        p['nikIndex'] = entry.get('nikIndex', 95.0)
                        p['culturalContext'] = entry.get('culturalContext', "")
                        p['imageQuery'] = entry.get('imageQuery', f"{p['brand']} {p['productName']}")
                        # v2.3: 기존에 설정된 imageUrl(JSON에서 옴)이 있으면 유지
                        # (entry에 imageUrl이 없을 수 있으므로 덮어쓰지 않도록 주의)
                        
                        # Amazon URL
                        image_query = p['imageQuery']
                        p['buyUrl'] = f"https://www.amazon.com/s?k={image_query.replace(' ', '+')}&tag={os.getenv('NEXT_PUBLIC_AMAZON_AFFILIATE_ID', 'nextidealab-20')}"
                        break
    except Exception as e:
        print(f"⚠️ Gemini 강화 오류 ({category_key}): {e}")

    # 3. 이미지 연동 확인 (Amazon)
    print(f"📸 '{category_key}' 이미지 및 링크 최종 확인 중...")
    for p in processed_products:
        # JSON 제공 이미지 (v2.4 수동 업데이트된 고품질 이미지)가 있으면 최우선 사용
        target_img = p.get('fixedImageUrl')
        
        # JSON 이미지가 있으면 유효성 체크 없이 즉시 사용
        if target_img:
            # print(f"  ✨ Curated 이미지 사용: {p['original_raw']}")
            pass
        else:
            # 무효하거나 없으면 Amazon 검색
            search_query = p.get('imageQuery', f"{p['brand']} {p['productName']}")
            amazon_img = await get_amazon_image(search_query)
            if amazon_img:
                target_img = amazon_img
        
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
    
    # 3. 카테고리별 처리
    for cat_key, products_raw in master_data['categories'].items():
        print(f"\n📂 카테고리 처리 중: {cat_key.upper()} ({len(products_raw)} items)")
        
        # 트렌드 맵 가져오기
        prev_rank_map = prev_master_rank_map.get(cat_key)
        
        # 데이터 강화
        enriched_products = await enrich_editorial_data(model, cat_key, products_raw, prev_rank_map)
        
        # Firestore 저장
        firestore_category = CATEGORY_MAPPING.get(cat_key, {'firestore_category': cat_key})['firestore_category']
        doc_id = f"{today}_{firestore_category}"
        
        data = {
            'date': today,
            'category': firestore_category,
            'items': enriched_products,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'isEditorial': True,
            'reportTitle': "NIK Beauty Index: Weekly Editorial Report (v2.4)"
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
