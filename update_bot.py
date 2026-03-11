import yfinance as yf
import json
import os
import google.generativeai as genai
from datetime import datetime

# API 키 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_score(val, low, high, reverse=False):
    score = ((val - low) / (high - low)) * 100
    score = max(0, min(100, score))
    return 100 - score if reverse else score

def calculate_logic():
    print("🚀 데이터 생성 중...")
    try:
        tickers = {"VIX": "^VIX", "SPY": "SPY", "HYG": "HYG", "IEF": "IEF", "UUP": "UUP", "QQQ": "QQQ", "DIA": "DIA", "GOLD": "GC=F", "BTC": "BTC-USD"}
        raw = {k: yf.Ticker(v).history(period="150d") for k, v in tickers.items()}
        
        # 7대 엔진 점수 계산
        s1 = get_score(raw["VIX"]['Close'].iloc[-1], 12, 35, reverse=True)
        s2 = get_score(raw["SPY"]['Close'].iloc[-1] / raw["SPY"]['Close'].rolling(window=125).mean().iloc[-1], 0.9, 1.1)
        s3 = get_score(raw["HYG"]['Close'].iloc[-1] / raw["IEF"]['Close'].iloc[-1], 0.7, 0.9)
        s4 = get_score(raw["UUP"]['Close'].iloc[-1] / raw["UUP"]['Close'].rolling(window=125).mean().iloc[-1], 0.95, 1.1, reverse=True)
        s7 = get_score(raw["BTC"]['Close'].iloc[-1] / raw["BTC"]['Close'].rolling(window=20).mean().iloc[-1], 0.8, 1.2)

        master_score = int((s1*0.2) + (s2*0.2) + (s3*0.2) + (s4*0.15) + (s7*0.05))

        # [핵심] index.html의 i.word, i.count, i.display_score, i.sentiment_score와 100% 일치시킴
        indicators_data = [
            {"word": "시장 공포(VIX)", "sentiment_score": round((s1-50)/5, 1), "display_score": f"{int(s1)}점", "count": "Market"},
            {"word": "가격 추세(SPY)", "sentiment_score": round((s2-50)/5, 1), "display_score": f"{int(s2)}점", "count": "Price"},
            {"word": "기업 신용(HYG)", "sentiment_score": round((s3-50)/5, 1), "display_score": f"{int(s3)}점", "count": "Credit"},
            {"word": "달러 강세(UUP)", "sentiment_score": round((s4-50)/5, 1), "display_score": f"{int(s4)}점", "count": "Cash"},
            {"word": "코인 열기(BTC)", "sentiment_score": round((s7-50)/5, 1), "display_score": f"{int(s7)}점", "count": "Crypto"}
        ]
        return master_score, indicators_data
    except:
        return 50, []

def get_ai_and_news(score):
    try:
        spy = yf.Ticker("SPY")
        news = spy.news[:5]
        formatted_news = [{"title": n['title'], "link": n['link']} for n in news]
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        news_titles = "\n".join([n['title'] for n in news])
        prompt = f"현재 시장 점수 {score}/100. 뉴스: {news_titles}. 한국어로 3줄 요약해줘. 형님께 보고하듯 씩씩하게!"
        response = model.generate_content(prompt)
        return formatted_news, response.text
    except:
        return [], "데이터 로딩 실패"

if __name__ == "__main__":
    score, indicators = calculate_logic()
    news, summary = get_ai_and_news(score)
    
    # [최종] HTML이 기다리는 모든 주머니(Key)를 다 채워줌
    output = {
        "master_score": score,
        "market_temp": score,
        "ai_summary": summary,
        "indicators": indicators, # 상세 리스트 & 심리 분석 차트용
        "sector_news": { # 뉴스 터미널용
            "BIG TECH": news,
            "SEMICON": news,
            "FINANCE": news
        }
    }
    
    # 저장 경로는 무조건 대문자 PROJECT로 통일!
    os.makedirs('PROJECT', exist_ok=True)
    with open('PROJECT/indicators.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)