import yfinance as yf
import json
import os

def calculate_master_score():
    print("🚀 SIGNAL 9 마스터 인덱스 산출 시작...")
    
    try:
        # 1. VIX 지수 (변동성/공포) 가져오기
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        # VIX 점수 환산 (VIX 15이하: 탐욕, 30이상: 공포)
        vix_score = max(0, min(100, 100 - ((vix - 10) * (100 / 30))))
        
        # 2. S&P 500 모멘텀 (125일 이동평균선 대비 위치)
        spy = yf.Ticker("SPY").history(period="150d")
        current_price = spy['Close'].iloc[-1]
        sma125 = spy['Close'].rolling(window=125).mean().iloc[-1]
        
        # 이격도 계산 (평균보다 높으면 탐욕, 낮으면 공포)
        ratio = (current_price / sma125) * 100
        # 90(공포) ~ 110(탐욕) 범위를 0~100 점수로 매핑
        momentum_score = max(0, min(100, (ratio - 90) * 5))
        
        # 3. 최종 마스터 점수 합산 (VIX 50% + 모멘텀 50%)
        final_score = int((vix_score * 0.5) + (momentum_score * 0.5))
        
        print(f"✅ 계산 완료! VIX: {vix:.2f}, 모멘텀: {ratio:.2f}%, 마스터 점수: {final_score}")
        return final_score

    except Exception as e:
        print(f"❌ 데이터 수집 중 에러 발생: {e}")
        return 50 # 에러 발생 시 중립 점수 반환

def update_json(new_score):
    # [핵심 수정] PROJECT 폴더 안의 파일을 가리키도록 경로 수정!
    file_path = 'PROJECT/indicators.json'
    
    # 기본 데이터 구조
    data = {
        "master_score": 50,
        "market_temp": 0,
        "indicators": [],
        "sector_news": {}
    }

    # 1. 기존 데이터 읽기 (PROJECT 폴더 내부 파일 탐색)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                print(f"📂 {file_path} 데이터를 성공적으로 불러왔습니다.")
            except:
                print("⚠️ 파일이 깨져있어 기본 구조로 시작합니다.")
    else:
        print(f"📢 {file_path} 파일이 없습니다. 새로 생성합니다.")

    # 2. 마스터 점수 업데이트 (형님이 쓴 85를 여기서 갈아치웁니다)
    data['master_score'] = new_score
    
    # 3. 안전하게 덮어쓰기
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"💾 {file_path} 업데이트 완료! (New Master Score: {new_score})")

if __name__ == "__main__":
    score = calculate_master_score()
    update_json(score)