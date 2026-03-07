# 파일명: news_ai_manager.py
import feedparser
import json
import os
from datetime import datetime
from translator_module import FinancialTranslator # 첫 번째 파일 불러오기

# 경로 설정 (형님의 실제 indicators.json 경로로 맞추세요)
TARGET_PATH = 'PROJECT/indicators.json'
f_trans = FinancialTranslator()

def update_news():
    url = 'https://news.google.com/rss/search?q=FED+FOMC+Interest+Rate&hl=en-US&gl=US&ceid=US:en'
    print(f"📡 [뉴스 수집 중...] {datetime.now().strftime('%H:%M:%S')}")
    
    feed = feedparser.parse(url)
    news_list = []
    
    for entry in feed.entries[:7]: # 상위 7개 뉴스
        ko_title = f_trans.translate(entry.title) # 오역 방지 번역기 사용!
        news_list.append({
            'title': ko_title,
            'link': entry.link,
            'date': entry.published
        })
        print(f"✅ 번역 완료: {ko_title[:25]}...")

    # 기존 데이터 로드 및 업데이트
    try:
        if os.path.exists(TARGET_PATH):
            with open(TARGET_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        data['news_list'] = news_list # 'news_list' 키에 저장
        
        with open(TARGET_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("🏁 모든 뉴스가 한글로 업데이트 되었습니다.")
    except Exception as e:
        print(f"❌ 저장 실패: {e}")

if __name__ == "__main__":
    update_news()