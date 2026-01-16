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
    return genai.GenerativeModel('gemini-1.5-flash')

async def scrape_olive_young(max_items: int = 20) -> List[Dict[str, Any]]:
    """
    올리브영 베스트 제품 크롤링
    
    Args:
        max_items: 크롤링할 최대 아이템 수
        
    Returns:
        제품 데이터 리스트
    """
    products = []
    
    async with async_playwright() as p:
        print("🌐 브라우저 시작 중...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 올리브영 베스트 페이지
        url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=1000000010001&fltDispCatNo=&prdSort=01&pageIdx=1&rowsPerPage=48"
        
        print(f"📄 페이지 로딩 중: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        # 페이지 로딩 대기
        await page.wait_for_timeout(3000)
        
        # HTML 가져오기
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # 제품 아이템 찾기
        # 올리브영 구조에 맞게 선택자 조정 필요
        items = soup.select('.prd_info')[:max_items]
        
        print(f"✅ {len(items)}개 제품 발견")
        
        for idx, item in enumerate(items, 1):
            try:
                # 제품명
                name_elem = item.select_one('.tx_name')
                name = name_elem.get_text(strip=True) if name_elem else f"Product {idx}"
                
                # 브랜드
                brand_elem = item.select_one('.tx_brand')
                brand = brand_elem.get_text(strip=True) if brand_elem else "Unknown"
                
                # 이미지
                img_elem = item.select_one('img')
                image_url = img_elem.get('src', '') if img_elem else ""
                if image_url and not image_url.startswith('http'):
                    image_url = 'https:' + image_url
                
                # 가격
                price_elem = item.select_one('.tx_price')
                price = price_elem.get_text(strip=True) if price_elem else "0"
                
                product = {
                    'rank': idx,
                    'productName': name,
                    'brand': brand,
                    'imageUrl': image_url or f"https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=100&h=100&fit=crop",
                    'price': price,
                    'tags': [],
                    'subcategory': 'skincare',  # 기본값, Gemini로 분류 예정
                    'trend': 0,  # 추후 계산
                }
                
                products.append(product)
                print(f"  {idx}. {brand} - {name}")
                
            except Exception as e:
                print(f"⚠️  제품 {idx} 파싱 오류: {e}")
                continue
        
        await browser.close()
    
    return products

async def classify_with_gemini(model, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gemini AI로 제품 카테고리 분류
    
    Args:
        model: Gemini 모델
        products: 제품 리스트
        
    Returns:
        분류된 제품 리스트
    """
    print("\n🤖 Gemini AI로 카테고리 분류 중...")
    
    # 제품 이름 리스트 생성
    product_names = [f"{p['rank']}. {p['productName']}" for p in products]
    
    prompt = f"""
다음은 K-Beauty 제품 목록입니다. 각 제품을 아래 카테고리 중 하나로 분류해주세요:

카테고리:
- skincare: 토너, 세럼, 크림, 에센스 등 스킨케어 제품
- suncare: 선크림, 선스틱 등 자외선 차단 제품  
- masks: 시트마스크, 팩, 필링패드 등
- makeup: 립스틱, 아이섀도우, 파운데이션 등 메이크업
- hair-body: 샴푸, 바디워시, 핸드크림 등

제품 목록:
{chr(10).join(product_names)}

응답 형식 (JSON):
{{
  "classifications": [
    {{"rank": 1, "subcategory": "skincare"}},
    {{"rank": 2, "subcategory": "suncare"}},
    ...
  ]
}}

JSON만 출력하세요.
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
        
        classifications = json.loads(result_text)
        
        # 제품에 카테고리 적용
        for item in classifications.get('classifications', []):
            rank = item.get('rank')
            subcategory = item.get('subcategory', 'skincare')
            
            for product in products:
                if product['rank'] == rank:
                    product['subcategory'] = subcategory
                    break
        
        print("✅ 카테고리 분류 완료")
        
    except Exception as e:
        print(f"⚠️  Gemini 분류 오류: {e}")
        print("기본 카테고리(skincare) 사용")
    
    return products

def save_to_firebase(db, products: List[Dict[str, Any]]):
    """
    Firebase Firestore에 데이터 저장
    
    Args:
        db: Firestore 클라이언트
        products: 제품 리스트
    """
    print("\n💾 Firebase에 저장 중...")
    
    # 오늘 날짜 (UTC)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    # 문서 ID는 날짜
    doc_ref = db.collection('daily_rankings').document(today)
    
    # 데이터 구조
    data = {
        'date': today,
        'category': 'beauty',
        'items': products,
        'updatedAt': firestore.SERVER_TIMESTAMP
    }
    
    # 저장
    doc_ref.set(data)
    
    print(f"✅ {len(products)}개 제품을 {today} 문서에 저장 완료")
    print(f"📁 컬렉션: daily_rankings")
    print(f"📄 문서 ID: {today}")

async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🇰🇷 K-Rank Beauty Scraper")
    print("=" * 60)
    
    try:
        # 1. Firebase 초기화
        print("\n📱 Firebase 초기화 중...")
        db = initialize_firebase()
        print("✅ Firebase 연결 완료")
        
        # 2. Gemini 초기화
        print("\n🧠 Gemini AI 초기화 중...")
        model = initialize_gemini()
        print("✅ Gemini API 연결 완료")
        
        # 3. 올리브영 크롤링
        products = await scrape_olive_young(max_items=20)
        
        if not products:
            print("❌ 크롤링된 제품이 없습니다.")
            return
        
        # 4. Gemini로 카테고리 분류
        products = await classify_with_gemini(model, products)
        
        # 5. Firebase에 저장
        save_to_firebase(db, products)
        
        print("\n" + "=" * 60)
        print("✅ 모든 작업 완료!")
        print("=" * 60)
        
        # 결과 요약
        print(f"\n📊 크롤링 결과:")
        print(f"  - 총 제품 수: {len(products)}")
        
        # 카테고리별 집계
        categories = {}
        for p in products:
            cat = p.get('subcategory', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"  - 카테고리별:")
        for cat, count in categories.items():
            print(f"    • {cat}: {count}개")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
