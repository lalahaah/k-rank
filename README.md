# K-Rank Leaderboard 🏆

실시간 한국 트렌드 리더보드 - K-Beauty, K-Food, K-Media의 인기 순위를 추적하는 데이터 기반 플랫폼

## ✨ 주요 기능

- **실시간 랭킹 추적**: Firestore 기반 실시간 제품 순위 업데이트
- **카테고리별 필터링**: Beauty, Food, Media 등 다양한 카테고리
- **서브 카테고리 세분화**: Skincare, Suncare, Masks, Makeup, Hair/Body 등
- **트렌드 분석**: 순위 변동 추이 시각화
- **반응형 디자인**: 모바일/데스크톱 최적화 UI

## 🎨 디자인 시스템

K-Rank 전용 디자인 토큰 적용:
- **Trust Blue** (#1768AC): 신뢰감을 전달하는 메인 브랜드 컬러
- **Canvas Gray** (#F7F7F9): 부드러운 배경색
- **Inter 폰트**: 모던하고 읽기 쉬운 타이포그래피

## 🛠 기술 스택

### Frontend
- **Next.js 14** (App Router) - React 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS v4** - 스타일링
- **shadcn-ui** - UI 컴포넌트
- **Lucide React** - 아이콘

### Backend & Database
- **Firebase Firestore** - 실시간 데이터베이스
- **Firebase Admin SDK** - 서버 사이드 작업
- **Google Gemini AI** - 데이터 분류 및 분석

### Data Collection
- **Playwright** - 웹 스크래핑
- **BeautifulSoup4** - HTML 파싱
- **Python 3.9+** - 스크래핑 스크립트

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/lalahaah/k-rank.git
cd k-rank
```

### 2. 의존성 설치
```bash
# Node.js 의존성
npm install

# Python 의존성
pip install -r scripts/requirements.txt

# Playwright 브라우저
playwright install chromium
```

### 3. 환경 변수 설정
`.env` 파일 생성:
```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Firebase Web SDK
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

Firebase Admin SDK를 위한 `serviceAccountKey.json` 파일을 프로젝트 루트에 추가하세요.

### 4. 개발 서버 실행
```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)를 엽니다.

## 🔥 Firebase 설정

### Firestore 보안 규칙
```
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    match /daily_rankings/{document=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

### 데이터 구조
```typescript
{
  date: "2026-01-16",
  category: "beauty",
  items: [
    {
      rank: 1,
      productName: "Torriden Dive-In Serum",
      brand: "Torriden",
      price: "19,900원",
      imageUrl: "https://...",
      tags: ["Moisturizing", "Hyaluronic Acid"],
      subcategory: "skincare",
      trend: 2  // 순위 변동 (양수=상승, 음수=하락)
    }
  ]
}
```

## 🤖 데이터 수집

Mock 데이터 생성:
```bash
python3 scripts/generate_mock_data.py
```

웹 스크래핑 (개발 중):
```bash
python3 scripts/scraper.py
```

## 📁 프로젝트 구조

```
k-rank-board/
├── src/
│   ├── app/              # Next.js App Router 페이지
│   ├── components/       # React 컴포넌트
│   │   ├── navbar.tsx
│   │   └── leaderboard-table.tsx
│   └── lib/              # 유틸리티 함수
│       ├── firebase.ts   # Firebase 초기화
│       └── data.ts       # 데이터 fetching
├── scripts/              # Python 스크립트
│   ├── scraper.py
│   └── generate_mock_data.py
├── docs/                 # 문서
│   ├── K_Rank_Design_System.md
│   └── K_Rank_Leaderboard_PRD.md
└── public/               # 정적 파일
```

## 🎯 로드맵

- [x] Next.js 프로젝트 초기화
- [x] K-Rank 디자인 시스템 구현
- [x] Firebase Firestore 연결
- [x] 서브 카테고리 필터 기능
- [x] 실시간 데이터 표시
- [ ] 올리브영 웹 스크래핑 완성
- [ ] 자동 데이터 업데이트 (Cron Job)
- [ ] 사용자 인증 기능
- [ ] Place & Media 카테고리 추가
- [ ] 검색 기능 구현
- [ ] 차트 및 트렌드 분석 페이지

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 📞 문의

프로젝트 링크: [https://github.com/lalahaah/k-rank](https://github.com/lalahaah/k-rank)

---

**Made with ❤️ for K-Culture enthusiasts**
