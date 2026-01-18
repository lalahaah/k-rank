# **🎨 K-Rank: Design System (v2.1 \- Color Spectrum Update)**

## **1\. 디자인 철학 (Design Philosophy)**

* **Identity:** "Multiverse of Trends"  
* **Rule:** 메인 플랫폼은 **Blue**를 유지하되, 각 카테고리 진입 시 테마 컬러가 전환되어 사용자에게 명확한 맥락(Context)을 제공합니다.

## **2\. 컬러 시스템 (Color System)**

### **Brand Identity (Platform)**

* **Trust Blue (Main)**  
  * Hex: \#5383E8 (Tailwind: brand-500)  
  * 용도: 랜딩 페이지, 로고, 공통 버튼, 푸터.

### **Category Spectrum (Sub-brands)**

* **Beauty: Glam Rose**  
  * Hex: \#E11D48 (Tailwind: beauty-500)  
  * 느낌: 세련됨, 여성적이지 않으면서도 강렬한 뷰티 무드.  
* **Media: Streaming Red**  
  * Hex: \#E50914 (Tailwind: media-500)  
  * 느낌: 영화적 긴장감, 넷플릭스 오리지널.  
* **Food: Savory Orange**  
  * Hex: \#F97316 (Tailwind: food-500)  
  * 느낌: 따뜻함, 맛있는 음식, 활기.  
* **Place: Map Green**  
  * Hex: \#10B981 (Tailwind: place-500)  
  * 느낌: 공간, 위치, 발견, 맑음.

### **Data Visualization**

* (기존 Trend Color 유지: Rising Red, Falling Blue)

## **3\. Tailwind 설정 가이드 (Updated)**

theme: {  
  extend: {  
    colors: {  
      brand: { 500: '\#5383E8', 600: '\#4169E1', 50: '\#EFF6FF' },  
      // New Category Colors  
      beauty: { 500: '\#E11D48', 600: '\#BE123C', 50: '\#FFF1F2' }, // Rose  
      media:  { 500: '\#E50914', 600: '\#B20710', 50: '\#FEF2F2' }, // Red  
      food:   { 500: '\#F97316', 600: '\#EA580C', 50: '\#FFF7ED' }, // Orange  
      place:  { 500: '\#10B981', 600: '\#059669', 50: '\#ECFDF5' }, // Emerald  
      // ... existing bg & trend colors  
    }  
  }  
}  
