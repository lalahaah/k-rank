#!/usr/bin/env python3
"""
각 뷰티 제품의 실제 Amazon 이미지 URL을 수동으로 업데이트하는 스크립트
"""

import json
import os

# 상위 10개 제품의 실제 Amazon 이미지 URL (수동으로 수집)
# VT Reedle Shot 100 ASIN: B0C2TQ24VY
# 각 제품에 대한 실제 Amazon 및 고품질 이미지 URL
PRODUCT_IMAGES = {
    "토리든 다이브인 세럼": "https://m.media-amazon.com/images/I/61vU9S3M6LL.jpg",
    "라운드랩 자작나무 선크림": "https://m.media-amazon.com/images/I/61SvyuQ68SL.jpg",
    "VT 리들샷 100": "https://m.media-amazon.com/images/I/61S-BqF0k-L.jpg",
    "퓌(fwee) 푸딩팟": "https://m.media-amazon.com/images/I/61Jp0rR5mDL.jpg",
    "아누아 PDRN 캡슐 세럼": "https://m.media-amazon.com/images/I/71K8U7Xf0FL.jpg",
    "스킨푸드 당근 패드": "https://images.unsplash.com/photo-1617897903246-719242758050?w=800&q=80",
    "어노브 트리트먼트 EX": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=800&q=80",
    "메디힐 티트리 패드": "https://images.unsplash.com/photo-1556228852-80a279f10d3e?w=800&q=80",
    "라네즈 립 슬리핑 마스크": "https://images.unsplash.com/photo-1631730486572-226d1f595b68?w=800&q=80",
    "일리윤 세라마이드 로션": "https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=800&q=80",
}

def main():
    # JSON 파일 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, 'editorial_ranking_v2_4.json')
    
    # JSON 파일 읽기
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 수정된 항목 개수
    updated_count = 0
    
    # 모든 카테고리의 아이템들 업데이트
    for cat_name, items in data['categories'].items():
        print(f"📂 카테고리 처리 중: {cat_name}")
        for item in items:
            product_name = item['name']
            if product_name in PRODUCT_IMAGES:
                old_url = item['url']
                new_url = PRODUCT_IMAGES[product_name]
                item['url'] = new_url
                updated_count += 1
                # print(f"  ✅ {product_name} 업데이트 완료")
    
    # 업데이트된 JSON 저장
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n✅ 총 {updated_count}개 제품 이미지 URL 업데이트 완료! (모든 카테고리 적용)")

if __name__ == '__main__':
    main()
