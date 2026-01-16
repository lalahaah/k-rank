#!/usr/bin/env python3
"""
K-Rank Beauty Scraper (Debug Version)
올리브영 페이지 HTML 구조 확인용
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def debug_olive_young():
    """올리브영 페이지 HTML 구조 확인"""
    
    async with async_playwright() as p:
        print("🌐 브라우저 시작...")
        browser = await p.chromium.launch(headless=False)  # headless=False로 브라우저 보기
        page = await browser.new_page()
        
        url = "https://www.oliveyoung.co.kr/store/display/getMCategoryList.do?dispCatNo=1000000010001&fltDispCatNo=&prdSort=01&pageIdx=1&rowsPerPage=48"
        
        print(f"📄 페이지 로딩: {url}")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        # 페이지 로딩 대기
        await page.wait_for_timeout(5000)
        
        # 스크린샷 저장
        await page.screenshot(path='oliveyoung_debug.png', full_page=True)
        print("📸 스크린샷 저장: oliveyoung_debug.png")
        
        # HTML 가져오기
        content = await page.content()
        
        # HTML 파일로 저장
        with open('oliveyoung_debug.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("💾 HTML 저장: oliveyoung_debug.html")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(content, 'html.parser')
        
        # 다양한 선택자 시도
        selectors_to_try = [
            '.prd_info',
            '.prod_list li',
            '.prd-item',
            '[class*="product"]',
            '[class*="prd"]',
            '.item',
            '[data-ref-goodsno]',
        ]
        
        print("\n🔍 선택자 테스트:")
        for selector in selectors_to_try:
            items = soup.select(selector)
            print(f"  {selector}: {len(items)}개 발견")
            if items and len(items) > 0:
                print(f"    첫 번째 아이템 HTML (앞 200자):")
                print(f"    {str(items[0])[:200]}...")
        
        print("\n⏳ 10초 후 브라우저 종료...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_olive_young())
