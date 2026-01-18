# **🇰🇷📊 K-Rank Leaderboard: Product Requirements Document (v2.2)**

| 버전 | 날짜 | 작성자 | 내용 |  
| v2.2 | 2026-01-18 | 넥스트 엔진 | K-Media(넷플릭스) 확장 및 VPN 수익화 모델 구체화 |

## **1\. 개요 (Overview)**

### **1.1 제품 정체성 (Identity)**

"The OP.GG for Korean Trends."  
화려한 설명보다 \*\*데이터(순위, 등락, 수치)\*\*를 직관적으로 보여주는 한국 트렌드 전적 검색/랭킹 플랫폼.

### **1.2 확장 전략 (Expansion Strategy)**

* **Phase 1 (Active):** **K-Beauty** (올리브영 데이터) \- *커머스 수익 중심*  
* **Phase 2 (Next):** **K-Media** (넷플릭스 Top 10\) \- *트래픽 및 VPN 수익 중심*  
* **Phase 3 (Planned):** **K-Food & Place** \- *로컬 광고 및 예약 수익*

## **2\. 사용자 경험 (UX/UI Strategy)**

### **2.1 디자인 컨셉: "Data Density"**

* **Visuals:** 신뢰감을 주는 블루 계열 (\#5383E8)을 유지하되, Media 탭은 \*\*"넷플릭스 레드(\#E50914)"\*\*를 포인트 컬러로 활용하여 분위기 전환.

### **2.2 네비게이션 구조 (Global Navigation)**

* **GNB:** \[Beauty\] 탭 옆의 **\[Media\]** 탭 활성화 (Coming Soon 제거).

## **3\. 상세 기능 명세 (Functional Specifications)**

### **3.1 K-Media 랭킹 보드 (New)**

* **데이터 소스:** top10.netflix.com (South Korea \- TV & Films).  
* **컬럼 구조:**  
  * **Rank:** 시청 순위.  
  * **Title:** 포스터(세로형) \+ 영문 제목 \+ (작게) 한글 제목.  
  * **Type:** TV Show / Film 배지.  
  * **Weeks in Top 10:** 인기도 지속 기간 (Trend 지표).  
  * **Action:** **\[Watch Trailer\]** (Youtube) 또는 **\[Unlock in US\]** (VPN Affiliate).

## **4\. 데이터 파이프라인 (Data Pipeline)**

### **4.1 Media Scraper (Python)**

* **Target:** 넷플릭스 공식 Top 10 사이트 (크롤링 매우 쉬움, 차단 없음).  
* **AI Processing:** \* 이미 영문 제목이 있으므로 번역 불필요.  
  * **장르(Genre) 및 무드(Mood) 태그** 추출에 AI 활용 (예: \#Romance, \#Revenge).

## **5\. 데이터베이스 스키마 (Unified Schema)**

**Collection: rankings**

* date: YYYY-MM-DD  
* category: "media" (New)  
* items: Array of Objects  
  * rank: 1  
  * title\_en: "Squid Game"  
  * title\_ko: "오징어 게임"  
  * poster\_url: "..."  
  * platform: "Netflix"  
  * related\_products: \["dal-gona-set", "tracksuit"\] (추후 뷰티/굿즈 연동용 필드)

## **6\. 수익화 모델 (Monetization Strategy)**

### **6.1 K-Beauty (Commerce)**

* **Amazon Associates:** 화장품 직접 판매 수수료 (3\~5%).

### **6.2 K-Media (High Ticket Affiliate) \- New\!**

* **VPN Affiliate:** "한국 넷플릭스 접속"을 위한 VPN 가입 유도 (건당 $30+).  
  * *Call to Action:* "Not available in your country? Watch with NordVPN."  
* **Cross-Selling:** "드라마 속 그 화장품" 배너를 통해 Beauty 탭으로 유입 유도.

### **6.3 Display Ads (Volume)**

* 트래픽이 안정화되면 리스트 5위, 10위 사이에 구글 애드센스 자동 삽입.