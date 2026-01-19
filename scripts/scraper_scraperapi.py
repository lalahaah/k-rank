#!/usr/bin/env python3
"""
K-Rank Scraper with ScraperAPI
올리브영 및 Netflix 데이터를 ScraperAPI를 통해 크롤링합니다.
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta
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

def scrape_olive_young_with_scraperapi(category_code: str = None, max_items: int = 20, max_retries: int = 3) -> List[Dict[str, Any]]:
    """
    올리브영 베스트 제품을 ScraperAPI를 통해 크롤링
    
    Args:
        category_code: 카테고리 코드 (None이면 All)
        max_items: 최대 아이템 수
        max_retries: 최대 재시도 횟수
        
    Returns:
        제품 리스트
    """
    products = []
    
    #ScraperAPI 키 확인
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
            print(f"🌐 ScraperAPI로 페이지 요청... (시도 {attempt + 1}/{max_retries})")
            print(f"📄 URL: {target_url}")
            
            # ScraperAPI 요청
            params = {
                'api_key': scraperapi_key,
                'url': target_url,
                'country_code': 'kr',
                'render': 'true'
            }
            
            response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
            
            if response.status_code == 200:
                print("✅ 요청 성공!")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Cloudflare 체크
                page_title = soup.title.string if soup.title else ""
                if "잠시만" in page_title:
                    print("⚠️  Cloudflare 페이지 감지")
                    time.sleep(5)
                    continue
                
                print(f"✅ 페이지: {page_title}")
                
                # 제품 파싱
                items = soup.select('div.prd_info')[:max_items]
                print(f"✅ {len(items)}개 제품 발견")
                
                if len(items) == 0:
                    time.sleep(5)
                    continue
                
                for idx, item in enumerate(items, 1):
                    try:
                        name_elem = item.select_one('.prd_name .tx_name')
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
                        price = price_elem.get_text(strip=True) + "원" if price_elem else "0원"
                        
                        link_elem = item.select_one('a')
                        buy_url = link_elem.get('href', '') if link_elem else ''
                        if buy_url and not buy_url.startswith('http'):
                            buy_url = 'https://www.oliveyoung.co.kr' + buy_url
                        
                        products.append({
                            'rank': idx,
                            'productName': name,
                            'brand': brand,
                            'imageUrl': image_url or "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=100&h=100&fit=crop",
                            'price': price,
                            'buyUrl': buy_url,
                            'tags': [],
                            'subcategory': 'skincare',
                            'trend': 0
                        })
                        
                        print(f"  {idx}. {brand} - {name}")
                    except Exception as e:
                        print(f"⚠️  제품 {idx} 파싱 오류: {e}")
                
                print("✅ 크롤링 완료!")
                break
            else:
                print(f"❌ HTTP {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return products


# 나머지 함수들은 기존 코드 유지...
