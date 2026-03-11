import yfinance as yf
import json
import os
import google.generativeai as genai

# [필수] GitHub Secrets에 등록한 API 키를 로봇이 가져옵니다
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def get_score(val, low, high, reverse=False):
    """점수를 0~100 사이로 환산하는 함수"""
    score = ((val - low) / (high - low)) * 100
    score = max(0, min(100, score))
    return 100 - score if reverse else score

def calculate_master_score():
    print("🚀 7대 엔진 가중치 분석 시작...")
    try:
        # 1. 데이터 수집
        tickers = {
            "VIX": "^VIX", "SPY": "SPY", "HYG": "HYG", 
            "IEF": "IEF", "GOLD": "GC=F", "UUP": "UUP", 
            "QQQ": "QQQ", "DIA": "DIA", "BTC": "BTC-USD"
        }
        # 분석을 위해 150일치 데이터를 긁어옵니다
        raw_data = {k: yf.Ticker(v).history(period="150d") for k, v in tickers.items()}

        # 2. 각 엔진별 점수 산출 (가중치 모델)
        # [Tier 1: 메인 - 각 20%]
        vix_now = raw_data["VIX"]['Close'].iloc[-1]
        s1 = get_score(vix_now, 12, 35, reverse=True) # 공포지수

        spy_now = raw_data["SPY"]['Close'].iloc[-1]
        spy_sma = raw_data["SPY"]['Close'].rolling(window=125).mean().iloc[-1]
        s2 = get_score(spy_now / spy_sma, 0.9, 1.1) # 시장 추세

        credit_ratio = raw_data["HYG"]['Close'].iloc[-1] / raw_data["IEF"]['Close'].iloc[-1]
        s3 = get_score(credit_ratio, 0.7, 0.9) # 신용 위험(하이일드)

        # [Tier 2: 백업 - 각 15%]
        uup_now = raw_data["UUP"]['Close'].iloc[-1]
        uup_sma = raw_data["UUP"]['Close'].rolling(window=125).mean().iloc[-1]
        s4 = get_score(uup_now / uup_sma, 0.95, 1.1, reverse=True) # 달러 강세

        risk_on_ratio = raw_data["QQQ"]['Close'].iloc[-1] / raw_data["DIA"]['Close'].iloc[-1]
        s5 = get_score(risk_on_ratio, 1.0, 1.3) # 기술주 선호도

        # [Tier 3: 센서 - 각 5%]
        gold_now = raw_data["GOLD"]['Close'].iloc[-1]
        gold_sma = raw_data["GOLD"]['Close'].rolling(window=125).mean().iloc[-1]
        s6 = get_score(gold_now / gold_sma, 0.95, 1.15, reverse=True) # 안전자산

        btc_now = raw_data["BTC"]['Close'].iloc[-1]
        btc_sma = raw_data["BTC"]['Close'].rolling(window=20).mean().iloc[-1]
        s7 = get_score(btc_now / btc_sma, 0.8, 1.2) # 투기 열기

        # 3. 가중치 합산 (최종 점수)
        final_score = int(
            (s1 * 0.20) + (s2 * 0.20) + (s3 * 0.20) + 
            (s4 * 0.15) + (s5 * 0.15) + 
            (s6 * 0.05) + (s7 * 0.05)
        )
        print(f"✅ 온도 체크 완료: {final_score}점")
        return final_score
    except Exception as e:
        print(f"❌ 계산 중 에러 발생: {e}")
        return 50

def get_ai_analysis(score):
    print("📰 뉴스 및 데이터 통합 AI 분석 중...")
    try:
        # 뉴스 가져오기
        spy = yf.Ticker("SPY")
        news_list = spy.news[:5]
        
        formatted_news = []
        news_text_for_ai = ""
        for n in news_list:
            formatted_news.append({"title": n['title'], "url": n['link']})
            news_text_for_ai += f"- {n['title']}\n"

        # Gemini AI 분석 (시상 상황 분석 로직 강화)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        [시장 데이터 분석 요청]
        1. 현재 시장 종합 점수: {score}/100 (0점에 가까울수록 공포, 100점에 가까울수록 탐욕)
        2. 주요 최신 뉴스:
        {news_text_for_ai}
        
        위 데이터를 바탕으로 **'현재 시장 상황에 대한 전문적인 분석'**을 수행해줘.
        단순히 뉴스를 요약하지 말고, 점수와 뉴스를 결합해 지금 시장의 '심리 상태'와 '위험도'가 어떤지 분석하는 것이 핵심이야.

        [보고 형식]
        - 현재 상황을 한 줄로 정의 (예: "폭풍 전야의 고요함입니다")
        - 데이터 기반 상황 분석 2줄 (지금 형님이 공격할 때인지 수비할 때인지 포함)
        - 씩씩하고 위트 있는 '형님' 말투로, 한국어로 작성해줘.
        """
        response = model.generate_content(prompt)
        return formatted_news, response.text
    except Exception as e:
        print(f"❌ AI 분석 실패: {e}")
        return [], "뉴스를 가져오는 데 실패했습니다. 직접 차트를 확인해 주십쇼 형님!"

def save_all(score, news, summary):
    file_path = 'PROJECT/indicators.json'
    data = {
        "master_score": score,
        "market_temp": score,
        "ai_summary": summary,
        "indicators": news,
        "sector_news": {} 
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 {file_path}에 모든 데이터 저장 완료!")

if __name__ == "__main__":
    current_score = calculate_master_score()
    news, ai_summary = get_ai_analysis(current_score)
    save_all(current_score, news, ai_summary)