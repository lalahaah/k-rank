"""
대한민국 구석구석 사이트에서 인기순 여행지 리스트를 스크래핑하는 스크립트  
Playwright를 사용하여 JavaScript 렌더링 완전 대기
"""
import asyncio
from playwright.async_api import async_playwright
import json
import re


async def scrape_popular_places(limit=30):
    """
    대한민국 구석구석 사이트에서 인기순 여행지 리스트 스크래핑
    
    Args:
        limit (int): 수집할 장소 개수
    
    Returns:
        list: 인기 여행지 정보 리스트
    """
    print(f"🌐 대한민국 구석구석 사이트에서 상위 {limit}개 인기 여행지를 스크래핑합니다...")
    
    async with async_playwright() as p:
        # Chromium 브라우저 실행
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        places = []
        
        try:
            # 페이지 접속 - networkidle 대기
            print("📍 페이지 로딩 중...")
            await page.goto('https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms', 
                          wait_until='networkidle',
                          timeout=60000)
            
            # 추가 대기
            await asyncio.sleep(3)
            
            # 인기순 정렬 설정 - URL에 srchType=3 파라미터 추가하여 재로드
            print("🔥 인기순으로 페이지 재로드...")
            await page.goto('https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms&srchType=3',
                          wait_until='networkidle',
                          timeout=60000)
            
            await asyncio.sleep(3)
            
            # 페이지 HTML 저장 for debugging
            html_content = await page.content()
            print(f"  ℹ️  페이지 HTML 길이: {len(html_content)} 문자")
            
            # 리스트 항목 찾기 시도
            items = await page.locator('ul.list_thumType li').all()
            
            if not items:
                print("  ⚠️  'ul.list_thumType li' 셀렉터로 항목을 찾지 못했습니다.")
                # 대안 셀렉터 시도
                items = await page.locator('li').all()
                print(f"  ℹ️  전체 li 태그: {len(items)}개")
                # strong 태그가 있는 li만 필터링
                filtered_items = []
                for item in items:
                    strong = await item.query_selector('strong')
                    if strong:
                        filtered_items.append(item)
                items = filtered_items
                print(f"  ℹ️  strong 태그가 있는 li: {len(items)}개")
            
            print(f"📄 총 {len(items)}개 항목 발견")
            
            for item in items:
                if len(places) >= limit:
                    break
                
                try:
                    # 제목
                    title_elem = await item.query_selector('strong.tit, strong')
                    name = await title_elem.inner_text() if title_elem else ""
                    name = name.strip()
                    
                    if not name:
                        continue
                    
                    # 지역
                    p_elems = await item.query_selector_all('p')
                    location = ""
                    if len(p_elems) > 0:
                        location_text = await p_elems[0].inner_text()
                        location = location_text.strip()
                    
                    # 설명
                    desc_elem = await item.query_selector('p.phrase')
                    description = ""
                    if desc_elem:
                        desc_text = await desc_elem.inner_text()
                        description = desc_text.strip()
                    elif len(p_elems) > 1:
                        desc_text = await p_elems[1].inner_text()
                        description = desc_text.strip()
                    
                    # 태그
                    tags = []
                    tag_container = await item.query_selector('p.tag')
                    if tag_container:
                        tag_elems = await tag_container.query_selector_all('span')
                        for tag_elem in tag_elems:
                            tag_text = await tag_elem.inner_text()
                            if tag_text:
                                tags.append(tag_text.strip())
                    
                    # 이미지
                    img_elem = await item.query_selector('img')
                    image_url = ""
                    if img_elem:
                        image_url = await img_elem.get_attribute('src')
                        if image_url and not image_url.startswith('http'):
                            image_url = f"https://korean.visitkorea.or.kr{image_url}"
                    
                    # Content ID
                    content_id = ""
                    link_elem = await item.query_selector('a[onclick]')
                    if link_elem:
                        onclick = await link_elem.get_attribute('onclick')
                        match = re.search(r"goDetail\('([^']+)'", onclick)
                        if match:
                            content_id = match.group(1)
                    
                    # 유효한 데이터만 추가
                    if name and location:
                        place_data = {
                            'name': name,
                            'location': location,
                            'description': description,
                            'tags': tags,
                            'image_url': image_url,
                            'content_id': content_id
                        }
                        places.append(place_data)
                        print(f"  ✅ {len(places)}. {name} ({location})")
                
                except Exception as e:
                    print(f"  ⚠️  항목 파싱 오류: {e}")
                    continue
            
            # 더 많은 항목이 필요하면 페이지 2로 이동
            if len(places) < limit:
                print(f"\n📄 추가 데이터 필요 - 페이지 2로 이동...")
                try:
                    # 페이지 2 URL로 직접 이동
                    await page.goto('https://korean.visitkorea.or.kr/list/travelinfo.do?service=ms&srchType=3&cPage=2',
                                  wait_until='networkidle',
                                  timeout=60000)
                    await asyncio.sleep(3)
                    
                    second_page_items = await page.locator('ul.list_thumType li').all()
                    if not second_page_items:
                        # 대안 셀렉터
                        all_lis = await page.locator('li').all()
                        second_page_items = []
                        for item in all_lis:
                            strong = await item.query_selector('strong')
                            if strong:
                                second_page_items.append(item)
                    
                    print(f"  ℹ️  페이지 2에서 {len(second_page_items)}개 항목 발견")
                    
                    for item in second_page_items:
                        if len(places) >= limit:
                            break
                        
                        try:
                            title_elem = await item.query_selector('strong.tit, strong')
                            name = await title_elem.inner_text() if title_elem else ""
                            name = name.strip()
                            
                            if not name:
                                continue
                            
                            p_elems = await item.query_selector_all('p')
                            location = ""
                            if len(p_elems) > 0:
                                location = (await p_elems[0].inner_text()).strip()
                            
                            desc_elem = await item.query_selector('p.phrase')
                            description = ""
                            if desc_elem:
                                description = (await desc_elem.inner_text()).strip()
                            elif len(p_elems) > 1:
                                description = (await p_elems[1].inner_text()).strip()
                            
                            tags = []
                            tag_container = await item.query_selector('p.tag')
                            if tag_container:
                                tag_elems = await tag_container.query_selector_all('span')
                                for tag_elem in tag_elems:
                                    tag_text = await tag_elem.inner_text()
                                    if tag_text:
                                        tags.append(tag_text.strip())
                            
                            img_elem = await item.query_selector('img')
                            image_url = ""
                            if img_elem:
                                image_url = await img_elem.get_attribute('src')
                                if image_url and not image_url.startswith('http'):
                                    image_url = f"https://korean.visitkorea.or.kr{image_url}"
                            
                            content_id = ""
                            link_elem = await item.query_selector('a[onclick]')
                            if link_elem:
                                onclick = await link_elem.get_attribute('onclick')
                                match = re.search(r"goDetail\('([^']+)'", onclick)
                                if match:
                                    content_id = match.group(1)
                            
                            if name and location:
                                place_data = {
                                    'name': name,
                                    'location': location,
                                    'description': description,
                                    'tags': tags,
                                    'image_url': image_url,
                                    'content_id': content_id
                                }
                                places.append(place_data)
                                print(f"  ✅ {len(places)}. {name} ({location})")
                        
                        except Exception as e:
                            print(f"  ⚠️  항목 파싱 오류: {e}")
                            continue
                
                except Exception as e:
                    print(f"⚠️  페이지 2 로드 실패: {e}")
        
        except Exception as e:
            print(f"❌ 스크래핑 오류: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
    
    print(f"\n✅ 총 {len(places)}개 장소 스크래핑 완료!")
    return places


async def main():
    """테스트 실행"""
    places = await scrape_popular_places(limit=30)
    
    # 결과 출력
    print("\n" + "="*80)
    print("📋 스크래핑 결과:")
    print("="*80)
    for i, place in enumerate(places, 1):
        print(f"\n{i}. {place['name']}")
        print(f"   지역: {place['location']}")
        if place['description']:
            desc_preview = place['description'][:50] + "..." if len(place['description']) > 50 else place['description']
            print(f"   설명: {desc_preview}")
        print(f"   태그: {', '.join(place['tags'])}")
        print(f"   Content ID: {place['content_id']}")
    
    # JSON 파일로 저장
    with open('popular_places.json', 'w', encoding='utf-8') as f:
        json.dump(places, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 결과가 'popular_places.json'에 저장되었습니다.")


if __name__ == "__main__":
    asyncio.run(main())
