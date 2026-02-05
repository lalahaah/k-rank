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
DATA_FILE = os.path.join(script_dir, 'editorial_ranking_v2_3.json')
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'
WRITE_TO_FIRESTORE = os.getenv('WRITE_TO_FIRESTORE', 'true').lower() == 'true'

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

async def enrich_editorial_data(model, category_key: str, products_raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """제품 리스트를 가공하고 Gemini로 강화 (v2.3 가격/이미지 우선 로직 포함)"""
    processed_products = []
    
    # 1. 기본 구조 생성
    for idx, item in enumerate(products_raw, 1):
        raw_name = item['name']
        price_val = item.get('price', 'N/A')
        image_url = item.get('url', '')
        
        brand_ko, name_ko = parse_brand_and_product(raw_name)
        
        # 브랜드명 변환
        brand_en = BRAND_NAME_MAPPING.get(brand_ko, auto_romanize_korean(brand_ko))
        
        product = {
            'rank': item.get('rank', idx),
            'brand': brand_en,
            'brandKo': brand_ko,
            'productName': name_ko,
            'productNameKo': name_ko,
            'original_raw': raw_name,
            'tags': [],
            'subcategory': category_key,
            'trend': 0,
            'price': price_val,
            'imageUrl': image_url
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
                        p['buyUrl'] = f"https://www.amazon.com/s?k={image_query.replace(' ', '+')}&tag={os.getenv('NEXT_PUBLIC_AMAZON_AFFILIATE_ID', 'krank-20')}"
                        break
    except Exception as e:
        print(f"⚠️ Gemini 강화 오류 ({category_key}): {e}")

    # 3. 이미지 연동 확인 (Amazon)
    print(f"📸 '{category_key}' 이미지 및 링크 최종 확인 중...")
    for p in processed_products:
        # JSON에 이미지가 있으면 그대로 사용, 없으면 검색
        if not p.get('imageUrl'):
            if DEV_MODE and p['rank'] > 3:
                p['imageUrl'] = "https://images.unsplash.com/photo-1596462502278-27bfdc4033c8?auto=format&fit=crop&q=80&w=400"
            else:
                search_query = p.get('imageQuery', f"{p['brand']} {p['productName']}")
                amazon_img = await get_amazon_image(search_query)
                p['imageUrl'] = amazon_img or "https://images.unsplash.com/photo-1596462502278-27bfdc4033c8?auto=format&fit=crop&q=80&w=400"

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
    
    # 3. 카테고리별 처리
    for cat_key, products_raw in master_data['categories'].items():
        print(f"\n📂 카테고리 처리 중: {cat_key.upper()} ({len(products_raw)} items)")
        
        # 데이터 강화
        enriched_products = await enrich_editorial_data(model, cat_key, products_raw)
        
        # Firestore 저장
        firestore_category = CATEGORY_MAPPING.get(cat_key, {'firestore_category': cat_key})['firestore_category']
        doc_id = f"{today}_{firestore_category}"
        
        data = {
            'date': today,
            'category': firestore_category,
            'items': enriched_products,
            'updatedAt': firestore.SERVER_TIMESTAMP,
            'isEditorial': True,
            'reportTitle': "NIK Beauty Index: Weekly Editorial Report (v2.3)"
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
