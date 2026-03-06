import json
import requests
import os
from xml.etree import ElementTree

def get_sector_news():
    """구글 뉴스 RSS를 통해 섹터별 뉴스를 긁어옵니다."""
    sectors = {
        "BIG TECH": "https://news.google.com/rss/search?q=Apple+Nvidia+Microsoft+Stock&hl=en-US&gl=US&ceid=US:en",
        "SEMICON": "https://news.google.com/rss/search?q=Semiconductor+TSMC+ASML&hl=en-US&gl=US&ceid=US:en",
        "FINANCE": "https://news.google.com/rss/search?q=JPMorgan+Goldman+Sachs+FED&hl=en-US&gl=US&ceid=US:en"
    }
    news_data = {}
    for name, url in sectors.items():
        try:
            print(f"📡 {name} 관련 뉴스 수집 중...")
            response = requests.get(url, timeout=10)
            tree = ElementTree.fromstring(response.content)
            items = []
            # 최신 뉴스 3개만 추출
            for item in tree.findall('.//item')[:3]:
                items.append({
                    "title": item.find('title').text,
                    "link": item.find('link').text,
                    "date": item.find('pubDate').text[:16]
                })
            news_data[name] = items
        except Exception as e:
            print(f"❌ {name} 뉴스 수집 실패: {e}")
            news_data[name] = []
    return news_data

def update_json_with_news():
    target_file = 'indicators.json'
    
    # 1. 기존 indicators.json 읽기 (분석 결과 보존용)
    if os.path.exists(target_file):
        with open(target_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except:
                data = {}
    else:
        # 파일이 아예 없으면 기본 틀 생성
        data = {"market_temp": "0.0", "indicators": []}

    # 2. 뉴스 데이터만 갱신
    data["sector_news"] = get_sector_news()

    # 3. 다시 저장
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ {target_file}에 뉴스 업데이트 완료!")

if __name__ == "__main__":
    update_json_with_news()