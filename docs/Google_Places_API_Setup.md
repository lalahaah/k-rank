# Google Places API 설정 가이드

## 1. Google Cloud Console 설정

### API 활성화
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 또는 새로 생성
3. "APIs & Services" > "Enable APIs and Services" 클릭
4. "Places API" 검색 후 활성화

### API 키 생성
1. "APIs & Services" > "Credentials" 클릭
2. "+ CREATE CREDENTIALS" > "API key" 선택
3. 생성된 API 키 복사

### API 키 제한 (권장)
1. 생성된 API 키 클릭
2. "API restrictions" > "Restrict key" 선택
3. "Places API" 선택
4. 저장

## 2. 로컬 개발 환경 설정

`.env` 파일에 추가:
```bash
GOOGLE_PLACES_API_KEY=your_api_key_here
```

## 3. GitHub Secrets 설정

1. GitHub Repository > Settings > Secrets and variables > Actions
2. "New repository secret" 클릭
3. Name: `GOOGLE_PLACES_API_KEY`
4. Secret: 복사한 API 키 붙여넣기
5. "Add secret" 클릭

## 4. 비용 관리

### 무료 크레딧
- 월 $200 무료 크레딧 제공
- 약 17개월 무료 사용 가능

### 예상 월 비용
매일 1회 실행 기준:
- Place Search (Nearby): 6회/일 = 180회/월 = **$5.76**
- Place Details: 10회/일 = 300회/월 = **$5.10**
- **총 약 $10.86/월**

### 비용 모니터링
1. Google Cloud Console > Billing
2. "Budgets & alerts" 설정
3. 월 $20 예산 알림 설정 권장

## 5. 테스트

로컬에서 스크래퍼 실행:
```bash
cd /Users/lahahome/Desktop/project2026/k-rank
python3 scripts/scraper_food_google_places.py
```

성공 시 Firebase에 데이터 저장됨:
- Collection: `daily_rankings`
- Document: `YYYY-MM-DD_food`

## 6. 자동화 검증

GitHub Actions에서 수동 실행:
1. GitHub Repository > Actions
2. "Daily K-Rank Scraper" 워크플로우 선택
3. "Run workflow" 클릭
4. 완료 후 Firebase에서 데이터 확인
