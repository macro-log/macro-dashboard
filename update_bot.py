import yfinance as yf
import json
import os
import requests
import google.generativeai as genai
from xml.etree import ElementTree

# [필수] API 키 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# 1. 7대 엔진 가중치 분석 (기존 로직 유지)
# ==========================================
def get_score(val, low, high, reverse=False):
    score = ((val - low) / (high - low)) * 100
    return max(0, min(100, 100 - score if reverse else score))

def calculate_logic():
    print("🚀 1단계: 7대 엔진 가중치 분석 시작...")
    try:
        tickers = {"VIX": "^VIX", "SPY": "SPY", "HYG": "HYG", "IEF": "IEF", "UUP": "UUP", "QQQ": "QQQ", "DIA": "DIA", "GOLD": "GC=F", "BTC": "BTC-USD"}
        raw = {k: yf.Ticker(v).history(period="150d") for k, v in tickers.items()}
        
        s1 = get_score(raw["VIX"]['Close'].iloc[-1], 12, 35, reverse=True)
        s2 = get_score(raw["SPY"]['Close'].iloc[-1] / raw["SPY"]['Close'].rolling(window=125).mean().iloc[-1], 0.9, 1.1)
        s3 = get_score(raw["HYG"]['Close'].iloc[-1] / raw["IEF"]['Close'].iloc[-1], 0.7, 0.9)
        s4 = get_score(raw["UUP"]['Close'].iloc[-1] / raw["UUP"]['Close'].rolling(window=125).mean().iloc[-1], 0.95, 1.1, reverse=True)
        s7 = get_score(raw["BTC"]['Close'].iloc[-1] / raw["BTC"]['Close'].rolling(window=20).mean().iloc[-1], 0.8, 1.2)

        master_score = int((s1*0.2) + (s2*0.2) + (s3*0.2) + (s4*0.15) + (s7*0.05))

        indicators_data = [
            {"word": "시장 공포(VIX)", "sentiment_score": round((s1-50)/5, 1), "display_score": f"{int(s1)}점", "count": "Market"},
            {"word": "가격 추세(SPY)", "sentiment_score": round((s2-50)/5, 1), "display_score": f"{int(s2)}점", "count": "Price"},
            {"word": "기업 신용(HYG)", "sentiment_score": round((s3-50)/5, 1), "display_score": f"{int(s3)}점", "count": "Credit"},
            {"word": "달러 강세(UUP)", "sentiment_score": round((s4-50)/5, 1), "display_score": f"{int(s4)}점", "count": "Cash"},
            {"word": "코인 열기(BTC)", "sentiment_score": round((s7-50)/5, 1), "display_score": f"{int(s7)}점", "count": "Crypto"}
        ]
        return master_score, indicators_data
    except Exception as e:
        print(f"❌ 점수 계산 에러: {e}")
        return 50, []

# ==========================================
# 2. 뉴스 전문 수집기 (news_crawler 기능 흡수)
# ==========================================
def fetch_sector_news():
    print("📰 2단계: 글로벌 섹터별 뉴스 크롤링 중...")
    sectors = {
        "BIG TECH": "https://news.google.com/rss/search?q=Apple+Nvidia+Microsoft+Stock&hl=en-US&gl=US&ceid=US:en",
        "SEMICON": "https://news.google.com/rss/search?q=Semiconductor+TSMC+ASML&hl=en-US&gl=US&ceid=US:en",
        "FINANCE": "https://news.google.com/rss/search?q=JPMorgan+Goldman+Sachs+FED&hl=en-US&gl=US&ceid=US:en"
    }
    news_data = {}
    for name, url in sectors.items():
        try:
            response = requests.get(url, timeout=10)
            tree = ElementTree.fromstring(response.content)
            items = []
            for item in tree.findall('.//item')[:4]: # 각 섹터별 4개씩 추출
                items.append({
                    "title": item.find('title').text,
                    "link": item.find('link').text,
                    "date": item.find('pubDate').text[:16]
                })
            news_data[name] = items
        except:
            news_data[name] = []
    return news_data

# ==========================================
# 3. AI 번역 및 3줄 요약 (news_ai_manager 기능 흡수)
# ==========================================
def generate_ai_briefing(score, news_dict):
    print("🤖 3단계: AI 번역 및 시장 상황 브리핑 작성 중...")
    try:
        # 주요 뉴스 제목들을 모아서 AI에게 전달
        top_titles = [n['title'] for n in news_dict.get("BIG TECH", [])[:2] + news_dict.get("FINANCE", [])[:2]]
        news_text = "\n".join(top_titles)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        [금융 분석 브리핑]
        - 현재 시장 점수: {score}/100점
        - 최신 영문 뉴스 헤드라인:
        {news_text}
        
        위 뉴스를 바탕으로 현재 시장 상황을 한국어로 자연스럽게 번역 및 요약해줘.
        단순 번역이 아니라, 3줄로 시장의 핵심 분위기(불장/조정장 등)를 파악해서 씩씩한 '형님' 말투로 보고해!
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ AI 분석 실패: {e}")
        return "형님, AI 서버가 잠시 지연 중입니다. 뉴스와 차트를 먼저 확인해 주십쇼!"

# ==========================================
# 4. 통합 실행 및 저장
# ==========================================
if __name__ == "__main__":
    # 데이터 수집 및 분석
    current_score, chart_data = calculate_logic()
    sector_news_data = fetch_sector_news()
    ai_summary_text = generate_ai_briefing(current_score, sector_news_data)
    
    # HTML이 기다리는 완벽한 JSON 구조
    final_output = {
        "master_score": current_score,
        "market_temp": current_score,
        "ai_summary": ai_summary_text,
        "indicators": chart_data,
        "sector_news": sector_news_data # 빅테크, 반도체, 금융 뉴스가 각각 들어감!
    }
    
    # PROJECT 폴더 안에 저장 (덮어쓰기 전쟁 종결)
    os.makedirs('PROJECT', exist_ok=True)
    with open('PROJECT/indicators.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 모든 데이터 통합 업데이트 완료! 깃허브로 전송 준비 끝!")