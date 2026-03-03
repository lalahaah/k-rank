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

# 환경변수 로드
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# 개발 모드 및 제한 설정
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'
DEV_LIMIT = 5  # 개발 모드일 때 처리할 아이템 수
WRITE_TO_FIRESTORE = os.getenv('WRITE_TO_FIRESTORE', 'true').lower() == 'true'
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


async def main():
    """메인 실행 함수 - Media 데이터만 자동 크롤링"""
    print("=" * 60)
    print("🇰🇷 K-Rank Scraper - Media")
    print("=" * 60)
    
    # 커맨드 라인 인자 확인
    run_mode = sys.argv[1] if len(sys.argv) > 1 else "media"  # "media"
    
    # Beauty는 이제 import_editorial_ranking.py를 통해 수동으로 관리됨
    if run_mode == "beauty":
        print("\n" + "=" * 60)
        print("⚠️  Beauty 카테고리는 더 이상 자동 크롤링되지 않습니다.")
        print("📝 대신 scripts/import_editorial_ranking.py를 사용하세요.")
        print("=" * 60)
        sys.exit(0)
    
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
        
        # 4. Media 카테고리 크롤링
        if run_mode == "media":
            print("\n" + "=" * 60)
            print("🎬 MEDIA 카테고리 크롤링 (Netflix)")
            print("=" * 60)
            
            all_media_items = []
            
            # Netflix TV Shows Top 10 크롤링
            print("\n📺 Netflix TV Shows 크롤링 중...")
            actual_limit = DEV_LIMIT if DEV_MODE else 10
            tv_items = await scrape_netflix(media_type='tv', max_items=actual_limit)
            if tv_items:
                all_media_items.extend(tv_items)
                print(f"✅ TV Shows {len(tv_items)}개 수집 완료")
            else:
                print("⚠️ TV Shows 데이터를 찾지 못했습니다.")
            
            # Netflix Films Top 10 크롤링
            print("\n🎬 Netflix Films 크롤링 중...")
            film_items = await scrape_netflix(media_type='films', max_items=actual_limit)
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
                
                if WRITE_TO_FIRESTORE:
                    doc_ref.set(data)
                    print(f"✅ {len(all_media_items)}개 타이틀을 {doc_id} 문서에 저장 완료")
                else:
                    print(f"🧪 [DEV_MODE] Firebase Media 저장 스킵 ({len(all_media_items)}개)")
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
    # python scraper.py media     # Media만 실행
    # 
    # Beauty 데이터는 scripts/import_editorial_ranking.py를 사용하세요
    asyncio.run(main())
