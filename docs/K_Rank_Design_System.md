🎨 K-Rank: Design System (v2.0 - Leaderboard Edition)1. 디자인 철학 (Design Philosophy)Identity: "The OP.GG for K-Trends"Core Values:Data Density: 한 화면에 최대한 많은 정보를 깔끔하게 보여줍니다.Trustworthy: 금융/전적 사이트 같은 신뢰감을 주는 블루 톤을 사용합니다.Hierarchy: 순위(Rank)와 변화(Trend)가 가장 먼저 눈에 들어와야 합니다.2. 컬러 시스템 (Color System)신뢰를 상징하는 **'Tech Blue'**를 메인으로 하고, 데이터의 등락(상승/하락)을 직관적인 색상으로 표현합니다.Primary BrandTrust Blue (Brand Color)Hex: #5383E8 (Tailwind: blue-500 계열 조정)용도: 로고, 메인 버튼, 활성화된 탭, 강조 링크.Canvas Gray (Background)Hex: #F5F7FA (Tailwind: slate-50 계열)용도: 전체 페이지 배경 (완전한 흰색보다 눈이 편하고 구획이 잘 보임).Surface WhiteHex: #FFFFFF용도: 테이블, 카드, 검색창 배경.Data Visualization (Trend)Rising Red (상승/Hot)Hex: #EF4444 (Tailwind: red-500)용도: 순위 상승(▲), Hot 배지, 긍정적 지표.Falling Blue (하락/Cold)Hex: #3B82F6 (Tailwind: blue-500)용도: 순위 하락(▼), Cold 배지.Stable Gray (유지)Hex: #9CA3AF (Tailwind: gray-400)용도: 순위 변동 없음(-), 일반 태그.Text ColorsHeading: #111827 (Gray-900) - 강한 강조.Body: #374151 (Gray-700) - 일반 정보.Muted: #6B7280 (Gray-500) - 부가 정보, 라벨.3. 타이포그래피 (Typography)가독성이 최우선입니다. 장식적인 세리프(Serif)를 버리고, 숫자가 잘 읽히는 모던한 산세리프(Sans-serif)를 사용합니다.Font FamilyMain Font: Inter (숫자 가독성이 뛰어남, 구글 폰트).Alternative: Pretendard (한글/영문 혼용 시 최적).Type Scale (Compact)H1 (Logo): 24px / Bold / Tracking-tight.H2 (Page Title): 20px / Bold.Body (Table Text): 14px / Medium.Caption (Tags/Meta): 12px / Regular.Rank Number: 16px / Bold / Monospace (숫자 간격 일정하게).4. UI 컴포넌트 (Components)4.1 The Leaderboard Table (핵심)이 서비스의 얼굴입니다.Header Row:Bg: #F9FAFB (Gray-50).Text: 12px, Uppercase, Bold, Gray-500.Height: 40px.Data Row:Bg: #FFFFFF.Height: 64px (정보 밀도 유지).Hover Effect: 배경색 #EFF6FF (Blue-50) 변경 + 우측 끝에 'Action Button' 등장.Border: border-b border-gray-100 (행 간 구분선).4.2 Badges & ChipsRank Change Badge:Style: Rounded corners (rounded-md).Size: 24px x 24px Flex container.Content: Icon (Arrow) + Number.Keyword Chip (Tags):Style: bg-gray-100, text-gray-600, rounded-full, px-2 py-1, text-[10px].4.3 Search InputStyle: 크고 넓은 검색창.Shape: rounded-lg.Shadow: shadow-sm (기본) -> shadow-md & ring-2 ring-blue-500 (Focus 시).4.4 ButtonsPrimary (Action):Bg: Trust Blue.Text: White, Bold.Shape: rounded-md.Ghost (Icon):Bg: Transparent -> Hover: Gray-100.5. 아이콘 시스템 (Iconography)Lucide React 라이브러리를 사용하되, 의미 전달이 명확한 아이콘을 씁니다.Rank: 🥇(1st), 🥈(2nd), 🥉(3rd) - 컬러 아이콘 또는 텍스트+색상으로 처리.Trend: TrendingUp (상승), TrendingDown (하락), Minus (유지).Category: Sparkles (Beauty), Clapperboard (Media), Utensils (Food), MapPin (Place).Action: ShoppingCart, ExternalLink.6. Tailwind 설정 가이드 (tailwind.config.ts)개발 에이전트에게 아래 설정을 적용하라고 지시하십시오.import type { Config } from "tailwindcss"

const config = {
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          500: '#5383E8', // Trust Blue
          600: '#2563EB',
          900: '#1E3A8A',
        },
        trend: {
          up: '#EF4444',   // Red
          down: '#3B82F6', // Blue
          stable: '#9CA3AF', // Gray
        },
        bg: {
            DEFAULT: '#F5F7FA', // Canvas
            surface: '#FFFFFF'
        }
      },
      fontFamily: {
        sans: ['var(--font-inter)', "sans-serif"],
      },
    },
  },
}
export default config
7. 적용 예시 (Preview Code)// Table Row Example
<div className="flex items-center p-4 bg-white border-b border-gray-100 hover:bg-brand-50 transition-colors group">
  
  {/* Rank */}
  <div className="w-12 text-center font-bold text-gray-700">1</div>
  
  {/* Product */}
  <div className="flex-1 flex items-center gap-3">
    <img src="..." className="w-10 h-10 rounded-md border border-gray-200" />
    <div>
      <div className="font-bold text-gray-900">Torriden Dive-In Serum</div>
      <div className="flex gap-1 mt-1">
         <span className="bg-gray-100 text-gray-500 text-[10px] px-1.5 rounded">#Moisturizing</span>
      </div>
    </div>
  </div>

  {/* Trend */}
  <div className="w-24 flex justify-center">
    <span className="flex items-center gap-1 text-xs font-bold text-trend-up bg-red-50 px-2 py-1 rounded">
       <TrendingUp size={12} /> 2
    </span>
  </div>

  {/* Action */}
  <div className="w-20 text-right opacity-0 group-hover:opacity-100 transition-opacity">
    <Button size="sm" className="bg-brand-500 hover:bg-brand-600">Buy</Button>
  </div>
  
</div>
