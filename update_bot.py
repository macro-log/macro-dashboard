import yfinance as yf
import json
import os

def get_score(val, low, high, reverse=False):
    # 점수를 0~100 사이로 환산하는 함수
    score = ((val - low) / (high - low)) * 100
    score = max(0, min(100, score))
    return 100 - score if reverse else score

def calculate_master_score():
    print("🚀 SIGNAL 9 [프로 가중치 모델] 엔진 가동...")
    try:
        # 데이터 수집 (7대 전사)
        tickers = {
            "VIX": "^VIX", "SPY": "SPY", "HYG": "HYG", 
            "IEF": "IEF", "GOLD": "GC=F", "UUP": "UUP", 
            "QQQ": "QQQ", "DIA": "DIA", "BTC": "BTC-USD"
        }
        data = {k: yf.Ticker(v).history(period="150d") for k, v in tickers.items()}

        # 1. 공포 (VIX) - 20%
        vix_now = data["VIX"]['Close'].iloc[-1]
        s1 = get_score(vix_now, 12, 35, reverse=True)

        # 2. 추세 (SPY) - 20%
        spy_now = data["SPY"]['Close'].iloc[-1]
        spy_sma = data["SPY"]['Close'].rolling(window=125).mean().iloc[-1]
        s2 = get_score(spy_now / spy_sma, 0.9, 1.1)

        # 3. 신용 (CREDIT) - 20%
        credit_ratio = data["HYG"]['Close'].iloc[-1] / data["IEF"]['Close'].iloc[-1]
        s3 = get_score(credit_ratio, 0.7, 0.9)

        # 4. 현금 (UUP) - 15%
        uup_now = data["UUP"]['Close'].iloc[-1]
        uup_sma = data["UUP"]['Close'].rolling(window=125).mean().iloc[-1]
        s4 = get_score(uup_now / uup_sma, 0.95, 1.1, reverse=True)

        # 5. 공격성 (QQQ/DIA) - 15%
        risk_on_ratio = data["QQQ"]['Close'].iloc[-1] / data["DIA"]['Close'].iloc[-1]
        s5 = get_score(risk_on_ratio, 1.0, 1.3)

        # 6. 안전 (GOLD) - 5%
        gold_now = data["GOLD"]['Close'].iloc[-1]
        gold_sma = data["GOLD"]['Close'].rolling(window=125).mean().iloc[-1]
        s6 = get_score(gold_now / gold_sma, 0.95, 1.15, reverse=True)

        # 7. 투기 (BTC) - 5%
        btc_now = data["BTC"]['Close'].iloc[-1]
        btc_sma = data["BTC"]['Close'].rolling(window=20).mean().iloc[-1]
        s7 = get_score(btc_now / btc_sma, 0.8, 1.2)

        # [가중치 적용 합산]
        final_score = int(
            (s1 * 0.20) + (s2 * 0.20) + (s3 * 0.20) + 
            (s4 * 0.15) + (s5 * 0.15) + 
            (s6 * 0.05) + (s7 * 0.05)
        )
        
        print(f"✅ 분석 완료! 최종 마스터 점수: {final_score}")
        return final_score

    except Exception as e:
        print(f"❌ 분석 중 에러: {e}")
        return 50

def update_json(new_score):
    file_path = 'PROJECT/indicators.json'
    data = {"master_score": 50, "market_temp": 0, "indicators": [], "sector_news": {}}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except: pass
    data['master_score'] = new_score
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"💾 {file_path} 업데이트 완료!")

if __name__ == "__main__":
    score = calculate_master_score()
    update_json(score)