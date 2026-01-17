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
    return genai.GenerativeModel('models/gemini-2.5-flash')

async def scrape_olive_young(max_items: int = 20, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    올리브영 베스트 제품 크롤링
    
    Args:
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
                
                # 올리브영 베스트 랭킹 페이지
                url = "https://www.oliveyoung.co.kr/store/main/getBestList.do"
                
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
