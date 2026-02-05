# GitHub Secrets 설정 가이드

GitHub Actions가 크롤링 스크립트를 실행하려면 다음 환경 변수들을 GitHub Secrets에 추가해야 합니다.

## 설정 방법

### 1. GitHub 저장소 설정 페이지 열기

1. 브라우저에서 GitHub 저장소(`https://github.com/lalahaah/k-rank`) 접속
2. 상단의 **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭

### 2. Secret 추가하기

**"New repository secret"** 버튼을 클릭하여 다음 2개의 secret을 추가하세요:

---

#### Secret 1: `GEMINI_API_KEY`

**Name**: `GEMINI_API_KEY`

**Secret**: `.env` 파일에 있는 Gemini API 키를 복사하여 붙여넣기

```
your-gemini-api-key-here
```

> ⚠️ **보안**: 실제 API 키는 절대 GitHub에 커밋하지 마세요. `.env` 파일에서 복사하세요.

---

#### Secret 2: `FIREBASE_SERVICE_ACCOUNT`

**Name**: `FIREBASE_SERVICE_ACCOUNT`

**Secret**: `serviceAccountKey.json` 파일의 전체 내용을 복사하여 붙여넣기

현재 프로젝트의 `serviceAccountKey.json` 파일을 열어서 전체 내용을 복사하세요. JSON 형식 그대로 붙여넣으면 됩니다. 다음과 같은 형식입니다:

```json
{
  "type": "service_account",
  "project_id": "k-rank-c5bad",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  ...
}
```

---

## 설정 완료 후

두 개의 secret이 모두 추가되면:
1. GitHub Actions 탭으로 이동
2. "Daily K-Rank Scraper" workflow 선택
3. "Run workflow" 버튼 클릭하여 수동 테스트 실행
4. 실행 로그를 확인하여 정상 작동 확인

## 예상 결과

- ✅ 크롤링 성공 시: Firestore에 데이터 저장됨
- ✅ 매일 오전 9시 (KST)에 자동 실행
- ❌ 실패 시: GitHub에서 이메일 알림 발송

## 보안 주의사항

- Secret은 한 번 저장하면 다시 볼 수 없습니다 (편집만 가능)
- Secret은 절대 코드에 직접 작성하지 마세요
- GitHub Actions 로그에도 자동으로 마스킹 처리됩니다
