# **🍜 K-Food: The "Real-Time Dining" Guide PRD (v1.0)**

| 버전 | 날짜 | 작성자 | 상태 |
| :---- | :---- | :---- | :---- |
| v1.0 | 2026-01-24 | 넥스트 엔진 | 기획안 확정 (Pivot: Convenience Store → Restaurants) |

## **1\. 제품 비전 (Vision)**

**"Don't just eat, experience the hype."**  
관광객용 맛집이 아닌, 데이터가 증명하는 \*\*'한국 현지인들의 진짜 랭킹'\*\*을 제공하여 외국인 관광객의 미식 경험을 혁신한다.

## **2\. 핵심 가치 및 차별화 요소 (Core Value)**

1. **Social Signal Data:** 광고가 아닌 캐치테이블(웨이팅), 네이버 맵(저장 수) 등 실제 행동 데이터를 지표화함.  
2. **Hype Analysis (AI):** 단순 설명이 아닌 "왜 이곳에 줄을 서는가?"에 대한 트렌드 맥락(Context)을 제공.  
3. **Booking Gateway:** 정보를 보는 것에서 그치지 않고 외국인 전용 예약 서비스로 즉시 연결.

## **3\. 랭킹 로직 및 지표 (Ranking Logic)**

음식점은 판매량이 없으므로 다음의 \*\*'Social Signals'\*\*를 합산하여 \*\*NIK Index(가칭)\*\*를 산출합니다.

* **지표 A: CatchTable Queue (40%)** \- 실시간 대기 팀 수 및 예약 마감 속도.  
* **지표 B: Naver Map Saves (30%)** \- '내 장소' 저장 수의 주간 증가율.  
* **지표 C: Social Media Velocity (20%)** \- 인스타그램/틱톡 내 영문/한글 해시태그 생성 속도.  
* **지표 D: Editorial Score (10%)** \- K-RANK 에디터의 트렌드 적합성 평가.

## **4\. 주요 기능 명세 (Feature Specs)**

### **4.1. Place Card (음식점 전용 카드 UI)**

기존 뷰티 섹션의 조밀한 리스트와 달리, **시각적 임팩트**를 강조한 카드 형태를 도입합니다.

* **Visuals:** 매장 전경 또는 대표 메뉴 고해상도 이미지.  
* **The "Wait" Badge:** "Avg. Wait: 90min", "Reservations Only" 등 희소성 표시.  
* **AI Insight:** "Local's Favorite: Must order the 'Truffle Potato' here." (제미나이 기반 요약)  
* **Action Button:** \* **\[Reserve via CatchTable Global\]**: 예약 대행 연결.  
  * **\[Get Directions\]**: 구글 맵 또는 네이버 맵 연동.

### **4.2. Location-Based Filter (지역별 필터링)**

전체 랭킹보다 \*\*'내가 지금 갈 수 있는 곳'\*\*이 중요합니다.

* **Hot Areas:** 성수(Seongsu), 한남(Hannam), 홍대(Hongdae), 도산(Dosan) 등 주요 핫플별 필터.  
* **Concept:** "Best for Solo Dining", "Nightlife Vibe", "Vegan Friendly".

### **4.3. NIK Interactive Map (지도 뷰)**

* 리스트 뷰와 지도 뷰를 스위칭하는 기능.  
* 랭킹 상위권 장소들을 지도 위에 핀으로 표시하여 여행 동선 최적화 지원.

## **5\. 수익화 모델 (Monetization 2.0)**

1. **Travel Platform Affiliate:** \* **Creatrip / Klook / Trazy:** 외국인 대상 예약금 결제 시 커미션 수취.  
   * **K-Pass:** 맛집 할인 및 프리패스권 판매 연동.  
2. **In-App Display Ads:** \* 특정 지역 랭킹 페이지 내에 해당 지역의 다른 매장 광고 노출.  
3. **Sponsored Content (Rising Star):** \* 데이터 점수는 낮지만 화제성이 있는 신규 오픈 매장을 'Rising Star' 섹션에 유료 노출.

## **6\. 데이터 파이프라인 (Data Pipeline)**

### **6.1. 수집 전략 (Scraping Strategy)**

* **CatchTable:** 공식 웹사이트의 인기 랭킹 및 실시간 대기 현황 크롤링.  
* **Naver Map:** 특정 장소 ID의 저장 수(Save count) 변동 추적.  
* **Google Maps API:** 외국인들의 평점 및 리뷰 키워드 대조.

### **6.2. AI Enricher (Gemini 2.5 Flash)**

* **Input:** 한국어 리뷰 50개 \+ 캐치테이블 정보 \+ 메뉴판 사진.  
* **Output:** 1\. 영문 메뉴명 번역.  
  2\. "주문 팁(Order Tip)" 생성 (예: '이곳은 2인 세트보다 단품 3개가 유리함').  
  3\. 웨이팅 난이도 평가.

## **7\. 성공 지표 (Success Metrics)**

1. **CTR (Click-Through Rate):** 예약 서비스(Creatrip 등)로 넘어가는 클릭률.  
2. **Social Shares:** "Seoul Food Ranking" 페이지의 SNS 공유 횟수.  
3. **Retention:** 여행 중 재방문율 (지도 뷰 활용 빈도).

## **💡 에디터의 제언**

음식점 섹션은 \*\*'이미지'\*\*가 8할입니다. 저작권 이슈를 피하기 위해 인스타그램 API를 활용한 사용자 게시물 임베딩이나, 제휴 플랫폼에서 제공하는 공식 이미지를 활용하는 전략이 필요합니다.