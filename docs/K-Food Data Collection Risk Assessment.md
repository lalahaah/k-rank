# **🍜 K-Food Scraper: 기술적 제약사항 및 우회 전략 보고서**

캐치테이블 및 네이버 데이터 수집 시 예상되는 기술적 병목 현상과 이에 대한 현실적인 대안을 제시합니다.

## **1\. 핵심 제약사항 분석 (Risk Analysis)**

### **1.1. Cloudflare & Bot Detection**

* **현황:** 캐치테이블은 Cloudflare의 'Under Attack Mode' 또는 고급 봇 차단 솔루션을 사용합니다.  
* **증상:** 일반적인 Requests는 물론, 표준 설정의 Playwright도 'Access Denied (403)' 또는 무한 'Verify you are human' 루프에 빠집니다.

### **1.2. 공식 API 부재 및 DOM 가변성**

* **현황:** 공식적인 데이터 API가 없으며, 웹 사이트는 React 기반의 SPA(Single Page Application)로 구조가 복잡합니다.  
* **증상:** 사이트 업데이트 시 CSS Selector가 변경되어 스크래퍼가 자주 깨질 수 있습니다 (유지보수 비용 발생).

## **2\. 기술적 우회 전략 (Technical Workarounds)**

### **전략 A: ScraperAPI "Ultra Mode" 활용 (추천)**

우리가 이미 사용 중인 **ScraperAPI**의 고급 기능을 활용합니다.

* **JS Rendering (render=true):** 자바스크립트를 실행하여 SPA 데이터를 불러옵니다.  
* **Anti-Bot Bypass (antibot=true):** ScraperAPI가 자동으로 Cloudflare의 TLS Fingerprinting과 챌린지를 우회합니다.  
* **Residential Proxies:** 데이터센터 IP가 아닌 실제 한국 가정집 IP로 위장하여 차단을 방지합니다.

### **전략 B: 모바일 웹(m.catchtable.co.kr) 타겟팅**

* PC용 웹사이트보다 모바일 웹 페이지가 보안 검사가 상대적으로 느슨하거나 HTML 구조가 단순한 경우가 많습니다. 모바일 사용자 에이전트(User-Agent)를 사용하여 접근합니다.

### **전략 C: 데이터 소스의 이중화 (Hybrid Approach)**

캐치테이블이 막힐 경우를 대비해 **데이터의 무게중심을 분산**합니다.

1. **Base Data (Naver/Google):** 식당 이름, 주소, 평점은 상대적으로 차단이 덜한 네이버 맵이나 구글 맵을 통해 확보합니다.  
2. **Point Data (CatchTable):** '실시간 웨이팅 수'와 '예약 상태' 딱 두 가지만 캐치테이블에서 핀포인트로 긁어옵니다. (전체 페이지를 긁는 것보다 감지 확률이 낮습니다.)

## **3\. 수정된 데이터 수집 프로세스 (Revised Pipeline)**

1. **Seed List 확보:** 네이버 '요즘 뜨는 식당' 또는 '저장 많은 곳' 리스트를 먼저 확보 (1차 필터링).  
2. **Stealth 요청:** ScraperAPI를 통해 캐치테이블 상세 페이지 접속.  
   * *헤더 설정:* referer, accept-language 등을 실제 한국 브라우저처럼 정교하게 세팅.  
3. **Fail-safe 로직:** 만약 캐치테이블 수집 실패 시, 랭킹에서 제외하는 대신 **"Live Status Unavailable"** 상태로 표시하고 기존 DB 데이터를 보여줌 (서비스 가용성 유지).

## **4\. 법적/정책적 고려사항 (Policy)**

* **Robots.txt 준수:** 수집 주기를 최소화(1시간 1회 이상 지양)하여 서버 부하를 주지 않음을 증명합니다.  
* **데이터의 가공:** 수집한 로우 데이터를 그대로 보여주지 않고, \*\*Gemini AI가 재해석한 'Insight'\*\*를 제공함으로써 "단순 복제"가 아닌 "부가가치 창출 서비스"임을 명확히 합니다.

## **💡 넥스트 엔진의 최종 판단**

기술적으로 \*\*"100% 자력 봇(Playwright)으로 뚫는 것은 어렵지만, ScraperAPI 같은 유료 우회 서비스를 통하면 95% 이상 성공 가능"\*\*합니다.  
우선 **무료 크레딧 내에서 ScraperAPI의 'Ultra Mode' 테스트**를 먼저 진행해보고, 만약 차단율이 높다면 **네이버 맵 저장 수**를 메인 지표로 삼고 캐치테이블은 보조 지표로 사용하는 \*\*'플랜 B'\*\*로 즉시 전환할 것을 권장합니다.