# **🍜 K-Food (Restaurants) Scraper Logic Design**

이 문서는 scripts/scraper\_food.py 구현을 위한 상세 로직 설계도입니다.

## **1\. 데이터 소스 및 수집 전략 (Data Sources)**

| 소스 (Source) | 수집 항목 | 수집 주기 | 기술 스택 |
| :---- | :---- | :---- | :---- |
| **CatchTable** | 인기 랭킹, 실시간 대기 팀 수, 예약 상태 | 매시간 (1h) | ScraperAPI \+ Playwright |
| **Naver Map** | 장소명, 주간 저장(Save) 수 변동, 구글 평점 대조 | 매일 (1d) | BeautifulSoup (Search API) |
| **Instagram** | 특정 장소 태그(\#성수맛집 등) 게시물 증가량 | 주간 (7d) | Graph API (또는 파싱) |

## **2\. 랭킹 산출 알고리즘 (NIK Index Calculation)**

단순한 나열이 아닌, 아래 공식을 통해 \*\*'지금 가장 핫한 순서'\*\*를 정합니다.

* ![][image1]**W (Wait Factor):** 캐치테이블 실시간 대기 팀 수 (대기 1팀당 1점, 최대 40점)  
* **S (Save Factor):** 네이버 맵 주간 저장 수 증가율 (상위 10%에게 30점 부여)  
* **V (Velocity):** 인스타그램 최근 24시간 내 게시물 생성 속도 (20점)  
* **E (Editorial):** 전문가 가중치 (미슐랭 선정 등, 10점)

## **3\. 파이썬 스크립트 구조 (scraper\_food.py)**

### **Step 1: 캐치테이블 데이터 수집 (Primary)**

def get\_catchtable\_hot\_list():  
    \# ScraperAPI를 통해 캐치테이블 '인기 랭킹' 페이지 렌더링  
    \# 1\. 랭킹 리스트 (식당명, 지역, 카테고리) 추출  
    \# 2\. 각 식당 상세 페이지 진입하여 '현재 대기 팀 수' 추출  
    return restaurant\_list

### **Step 2: 사회적 신호 보강 (Naver/SNS)**

def get\_social\_signals(restaurant\_name):  
    \# 네이버 맵 검색 API/크롤링을 통해 '저장 수' 확인  
    \# 구글 맵 평점(외국인 선호도) 데이터 수집  
    return social\_score

### **Step 3: AI 기반 데이터 가공 (Gemini 2.5 Flash)**

음식점 전용 **Enrichment Prompt**를 사용합니다.

* **Input:** 식당명, 메뉴 리스트, 한국어 리뷰 원문 30개.  
* **Task:** 1\. 영어 메뉴명 번역 및 'Best Seller' 선정.  
  2\. **'Order Tip'** 생성 (예: "Don't forget to get the truffle sauce").  
  3\. **'Hype Factor'** 요약 (예: "The birthplace of Seoul's bagel craze").

### **Step 4: Firestore 저장**

* **Collection:** rankings  
* **Document ID:** YYYY-MM-DD-food  
* **Field:** items (RankingItem 객체 배열)

## **4\. 데이터 스키마 (JSON Structure)**

{  
  "id": "food-1",  
  "rank": 1,  
  "name\_ko": "런던 베이글 뮤지엄 도산",  
  "name\_en": "London Bagel Museum",  
  "category": "Bakery / Cafe",  
  "location": "Dosan, Seoul",  
  "image\_url": "...",  
  "metrics": {  
    "wait\_time": "120 min",  
    "hype\_score": 98,  
    "status": "Hard to Book"  
  },  
  "ai\_insight": {  
    "summary": "The potato cheese bagel is a masterpiece.",  
    "tips": "Arrive before 8 AM for shorter queue.",  
    "tags": \["Aesthetic", "Viral", "Must Visit"\]  
  },  
  "links": {  
    "reservation": "\[https://catchtable.co.kr/\](https://catchtable.co.kr/)...",  
    "map": "\[https://maps.google.com/?q=\](https://maps.google.com/?q=)..."  
  }  
}

## **5\. 단계별 구현 계획 (Milestones)**

1. **Phase 1 (MVP):** 캐치테이블 인기 리스트 \+ Gemini 번역만으로 우선 구동 (1주일 내).  
2. **Phase 2 (Optimization):** 네이버 저장 수 데이터를 연동하여 랭킹의 정확도 향상.  
3. **Phase 3 (Expansion):** 지도 앱과 연동하여 지역별(성수, 한남 등) 필터 자동 생성.

## **💡 에디터의 핵심 제언**

대표님, 음식점 데이터의 핵심은 \*\*'사진의 퀄리티'\*\*입니다. 텍스트 정보가 아무리 좋아도 사진이 먹음직스럽지 않으면 클릭률이 떨어집니다. 스크래퍼가 이미지를 가져올 때 **가장 해상도가 높은 포털의 대표 이미지**를 우선순위로 가져오도록 설계했습니다.

[image1]: <data:image/png;base64,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>