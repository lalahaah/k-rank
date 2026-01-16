#!/usr/bin/env python3
"""
K-Rank Beauty Data Generator (Mock)
실제 올리브영 크롤링 대신 Mock 데이터를 생성하여 Firebase에 저장합니다.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json')
        firebase_admin.initialize_app(cred)
    return firestore.client()

def create_mock_data() -> List[Dict[str, Any]]:
    """Mock 제품 데이터 생성"""
    products = [
        {
            'rank': 1,
            'productName': 'Torriden Dive-In Serum',
            'brand': 'Torriden',
            'imageUrl': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400',
            'price': '19,900원',
            'tags': ['Moisturizing', 'Hyaluronic Acid', 'Gentle'],
            'subcategory': 'skincare',
            'trend': -2,
        },
        {
            'rank': 2,
            'productName': 'Round Lab Birch Juice Sunscreen SPF50+',
            'brand': 'Round Lab',
            'imageUrl': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400',
            'price': '18,000원',
            'tags': ['SPF50+', 'Hydrating', 'Non-greasy'],
            'subcategory': 'suncare',
            'trend': -1,
        },
        {
            'rank': 3,
            'productName': 'COSRX Advanced Snail 96 Mucin Essence',
            'brand': 'COSRX',
            'imageUrl': 'https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400',
            'price': '23,000원',
            'tags': ['Anti-aging', 'Repair', '96% Snail'],
            'subcategory': 'skincare',
            'trend': 1,
        },
        {
            'rank': 4,
            'productName': 'Beauty of Joseon Relief Sun',
            'brand': 'Beauty of Joseon',
            'imageUrl': 'https://images.unsplash.com/photo-1571875257727-256c39da42af?w=400',
            'price': '16,500원',
            'tags': ['SPF50+', 'Korean Herbs', 'Lightweight'],
            'subcategory': 'suncare',
            'trend': 0,
        },
        {
            'rank': 5,
            'productName': 'Anua Heartleaf 77% Soothing Toner',
            'brand': 'Anua',
            'imageUrl': 'https://images.unsplash.com/photo-1616394584738-fc6e612e71b9?w=400',
            'price': '21,500원',
            'tags': ['Soothing', 'pH Balancing', '77% Heartleaf'],
            'subcategory': 'skincare',
            'trend': -3,
        },
        {
            'rank': 6,
            'productName': 'Innisfree Green Tea Seed Serum',
            'brand': 'Innisfree',
            'imageUrl': 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400',
            'price': '28,000원',
            'tags': ['Hydration', 'Green Tea', 'Antioxidant'],
            'subcategory': 'skincare',
            'trend': 2,
        },
        {
            'rank': 7,
            'productName': 'Laneige Lip Sleeping Mask',
            'brand': 'Laneige',
            'imageUrl': 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=400',
            'price': '23,000원',
            'tags': ['Overnight', 'Lip Care', 'Berry'],
            'subcategory': 'skincare',
            'trend': 1,
        },
        {
            'rank': 8,
            'productName': 'Etude House SoonJung pH 5.5 Foam Cleanser',
            'brand': 'Etude House',
            'imageUrl': 'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400',
            'price': '12,000원',
            'tags': ['Gentle', 'pH 5.5', 'Sensitive Skin'],
            'subcategory': 'skincare',
            'trend': 0,
        },
        {
            'rank': 9,
            'productName': 'Missha Time Revolution Night Repair Ampoule',
            'brand': 'Missha',
            'imageUrl': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400',
            'price': '35,000원',
            'tags': ['Anti-aging', 'Fermented', 'Night Care'],
            'subcategory': 'skincare',
            'trend': -1,
        },
        {
            'rank': 10,
            'productName': 'Some By Mi AHA BHA PHA 30 Days Miracle Toner',
            'brand': 'Some By Mi',
            'imageUrl': 'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=400',
            'price': '18,500원',
            'tags': ['Exfoliating', 'Acne Care', 'Tea Tree'],
            'subcategory': 'skincare',
            'trend': 1,
        },
        {
            'rank': 11,
            'productName': 'Mediheal N.M.F Aquaring Ampoule Mask',
            'brand': 'Mediheal',
            'imageUrl': 'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400',
            'price': '3,000원',
            'tags': ['Sheet Mask', 'Hydration', 'Single Use'],
            'subcategory': 'masks',
            'trend': 0,
        },
        {
            'rank': 12,
            'productName': 'CLIO Kill Cover Founwear Cushion',
            'brand': 'CLIO',
            'imageUrl': 'https://images.unsplash.com/photo-1588870889315-0a0b2bdc49dc?w=400',
            'price': '32,000원',
            'tags': ['Cushion', 'High Coverage', 'Long-lasting'],
            'subcategory': 'makeup',
            'trend': 2,
        },
        {
            'rank': 13,
            'productName': '3CE Velvet Lip Tint',
            'brand': '3CE',
            'imageUrl': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400',
            'price': '19,000원',
            'tags': ['Velvet', 'Long-lasting', 'Matte'],
            'subcategory': 'makeup',
            'trend': 1,
        },
        {
            'rank': 14,
            'productName': 'Romand Juicy Lasting Tint',
            'brand': 'Romand',
            'imageUrl': 'https://images.unsplash.com/photo-1603561596112-0a132b757442?w=400',
            'price': '15,000원',
            'tags': ['Glossy', 'Fruit Tint', 'Vibrant Color'],
            'subcategory': 'makeup',
            'trend': 3,
        },
        {
            'rank': 15,
            'productName': 'Aromatica Rosemary Scalp Scaling Shampoo',
            'brand': 'Aromatica',
            'imageUrl': 'https://images.unsplash.com/photo-1629475117670-c8e7c8c4f0b9?w=400',
            'price': '26,000원',
            'tags': ['Scalp Care', 'Vegan', 'Rosemary'],
            'subcategory': 'hair-body',
            'trend': -1,
        },
        {
            'rank': 16,
            'productName': 'Dr. Jart+ Cicapair Tiger Grass Cream',
            'brand': 'Dr. Jart+',
            'imageUrl': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400',
            'price': '42,000원',
            'tags': ['Redness Relief', 'Centella', 'Sensitive'],
            'subcategory': 'skincare',
            'trend': 0,
        },
        {
            'rank': 17,
            'productName': 'Too Cool For School Egg Cream Mask',
            'brand': 'Too Cool For School',
            'imageUrl': 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400',
            'price': '16,000원',
            'tags': ['Wash-off', 'Brightening', 'Egg Extract'],
            'subcategory': 'masks',
            'trend': 1,
        },
        {
            'rank': 18,
            'productName': 'Peripera Ink Velvet #8 Timeless Ruby',
            'brand': 'Peripera',
            'imageUrl': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400',
            'price': '12,000원',
            'tags': ['Velvet', 'Long-lasting', 'Affordable'],
            'subcategory': 'makeup',
            'trend': -2,
        },
        {
            'rank': 19,
            'productName': 'Banila Co Clean It Zero Cleansing Balm',
            'brand': 'Banila Co',
            'imageUrl': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400',
            'price': '22,000원',
            'tags': ['Cleansing Balm', 'Makeup Remover', 'Sherbet'],
            'subcategory': 'skincare',
            'trend': 0,
        },
        {
            'rank': 20,
            'productName': 'La Roche-Posay Anthelios Sunscreen',
            'brand': 'La Roche-Posay',
            'imageUrl': 'https://images.unsplash.com/photo-1571875257727-256c39da42af?w=400',
            'price': '45,000원',
            'tags': ['SPF50+', 'Dermatologist', 'Sensitive Skin'],
            'subcategory': 'suncare',
            'trend': 1,
        },
    ]
    
    return products

def save_to_firebase(db, products: List[Dict[str, Any]]):
    """Firebase Firestore에 데이터 저장"""
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

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🇰🇷 K-Rank Beauty Data Generator (Mock)")
    print("=" * 60)
    
    try:
        # 1. Firebase 초기화
        print("\n📱 Firebase 초기화 중...")
        db = initialize_firebase()
        print("✅ Firebase 연결 완료")
        
        # 2. Mock 데이터 생성
        print("\n📦 Mock 데이터 생성 중...")
        products = create_mock_data()
        print(f"✅ {len(products)}개 제품 데이터 생성 완료")
        
        # 3. Firebase에 저장
        save_to_firebase(db, products)
        
        print("\n" + "=" * 60)
        print("✅ 모든 작업 완료!")
        print("=" * 60)
        
        # 결과 요약
        print(f"\n📊 저장된 데이터:")
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
    main()
