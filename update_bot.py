import yfinance as yf
import json
import os
import google.generativeai as genai
from datetime import datetime

# [필수] 깃허브 세팅에서 넣은 API 키를 로봇이 가져옵니다
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_score(val, low, high, reverse=False):
    """지표 값을 0~100 점수로 변환"""
    score = ((val - low) / (high - low)) * 100
    score = max(0, min(100, score))
    return 100 - score if reverse else score

def calculate_master_score():
    print("🚀 7대 엔진 가중치 분석 시작...")
    try:
        tickers = {
            "VIX": "^VIX", "SPY": "SPY", "HYG": "HYG", 
            "IEF": "IEF", "GOLD": "GC=F", "UUP": "UUP", 
            "QQQ": "QQQ", "DIA": "DIA", "BTC": "BTC-USD"
        }
        raw_data = {k: yf.Ticker(v).history(period="150d") for k, v in tickers.items()}

        # [각 엔진별 점수 계산]
        s1 = get_score(raw_data["VIX"]['Close'].iloc[-1], 12, 35, reverse=True) # 공포
        s2 = get_score(raw_data["SPY"]['Close'].iloc[-1] / raw_data["SPY"]['Close'].rolling(window=125).mean().iloc[-1], 0.9, 1.1) # 추세
        s3 = get_score(raw_data["HYG"]['Close'].iloc[-1] / raw_data["IEF"]['Close'].iloc[-1], 0.7, 0.9) # 신용
        s4 = get_score(raw_data["UUP"]['Close'].iloc[-1] / raw_data["UUP"]['Close'].rolling(window=125).mean().iloc[-1], 0.95, 1.1, reverse=True) # 달러
        s5 = get_score(raw_data["QQQ"]['Close'].iloc[-1] / raw_data["DIA"]['Close'].iloc[-1], 1.0, 1.3) # 기술주
        s6 = get_score(raw_data["GOLD"]['Close'].iloc[-1] / raw_data["GOLD"]['Close'].rolling(window=125).mean().iloc[-1], 0.95, 1.15, reverse=True) # 안전
        s7 = get_score(raw_data["BTC"]['Close'].iloc[-1] / raw_data["BTC"]['Close'].rolling(window=20).mean().iloc[-1], 0.8, 1.2) # 비트코인

        # 최종 가중치 합산 공식
        $$Master Score = (S1,2,3 \times 0.20) + (S4,5 \times 0.15) + (S6,7 \times 0.05)$$
        final_score = int((s1*0.2) + (s2*0.2) + (s3*0.2) + (s4*0.15) + (s5*0.15) + (s6*0.05) + (s7*0.05))

        # HTML 하단 차트용 데이터 (이름, 점수)
        chart_indicators = [
            {"word": "시장공포", "sentiment_score": (s1-50)/5, "display_score": f"{int(s1)}점", "count": "VIX"},
            {"word": "시장추세", "sentiment_score": (s2-50)/5, "display_score": f"{int(s2)}점", "count": "SPY"},
            {"word": "자금경색", "sentiment_score": (s3-50)/5, "display_score": f"{int(s3)}점", "count": "Credit"},
            {"word": "달러강세", "sentiment_score": (s4-50)/5, "display_score": f"{int(s4)}점", "count": "USD"},
            {"word": "코인열기", "sentiment_score": (s7-50)/5, "display_score": f"{int(s7)}점", "count": "BTC"}
        ]
        return final_score, chart_indicators
    except Exception as e:
        print(f"❌ 계산 에러: {e}")
        return 50, []

def get_market_analysis(score):
    print("📰 뉴스 수집 및 AI 시장 분석 중...")
    try:
        # 뉴스 5개 긁어오기 (영어 제목)
        spy = yf.Ticker("SPY")
        raw_news = spy.news[:5]
        
        # HTML 뉴스 터미널용 데이터 포맷
        news_data = [{"title": n['title'], "link": n['link']} for n in raw_news]
        news_titles = "\n".join([n['title'] for n in raw_news])

        # Gemini AI에게 분석 및 한글 요약 시키기
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        [금융 데이터 분석 보고]
        현재 시장 점수: {score}/100
        최신 뉴스 제목(영어):
        {news_titles}

        위 데이터를 바탕으로 현재 시장 상황을 분석해서 한국어로 3줄 요약해줘.
        단순 번역이 아니라, 점수와 뉴스를 결합해 지금 상황이 어떤지(공격/수비)를 알려주는 게 핵심이야.
        말투는 '형님'에게 보고하듯 씩씩하고 위트 있게 작성해줘.
        """
        response = model.generate_content(prompt)
        return news_data, response.text
    except Exception as e:
        return [], "형님, AI가 분석 중에 뻗었네요. 잠시 후 다시 시도하시죠! 🫡"

if __name__ == "__main__":
    # 1. 점수 계산
    score, chart_info = calculate_master_score()
    
    # 2. 뉴스 수집 및 AI 분석
    news_list, ai_summary = get_market_analysis(score)
    
    # 3. 모든 데이터를 하나로 묶기 (index.html이 찾는 이름들)
    final_json = {
        "master_score": score,
        "market_temp": score,
        "ai_summary": ai_summary,
        "indicators": chart_info,
        "sector_news": {
            "BIG TECH": news_list,
            "SEMICON": news_list,
            "FINANCE": news_list
        }
    }
    
    # 4. 저장 (PROJECT 폴더 안방으로!)
    with open('PROJECT/indicators.json', 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)
    
    print(f"💾 모든 데이터 업데이트 완료! 현재 온도: {score}°")