import json
import re
import os
from collections import Counter

# 1. 핵심 키워드 및 맥락 규칙 (내가 고도화하신 그 로직 그대로)
TARGET_KEYWORDS = ["INFLATION", "EMPLOYMENT", "RATE", "ECONOMY", "LABOR", "PRICES", "GROWTH", "STABILITY", "RISKS", "DEMAND", "SUPPLY", "SPENDING", "WAGES", "HOUSING", "ENERGY", "TIGHTENING", "EASING", "GDP", "POLICY", "BANKING", "CREDIT"]

CONTEXT_RULES = {
    "SUPPLY": {"INCREASED": 2.5, "RECOVERY": 2.0, "LABOR": 1.5, "CONSTRAINTS": -4.5, "DISRUPTION": -5.0, "SHORTAGES": -4.0, "TIGHT": -3.0},
    "INFLATION": {"EASING": 5.0, "DECLINING": 4.0, "SLOWING": 3.5, "PERSISTENT": -5.0, "ELEVATED": -4.0, "HIGH": -3.5, "STUBBORN": -4.5},
    "RATE": {"HIKE": -5.0, "TIGHTENING": -4.0, "INCREASE": -3.5, "CUT": 5.0, "EASING": 4.5, "PAUSE": 2.5, "LOWER": 3.0},
    "LABOR": {"STRONG": 2.0, "BALANCED": 3.0, "COOLING": 2.5, "TIGHT": -3.5, "SHORTAGES": -3.0}
}

POS_WORDS = ["MODERATE", "RESILIENT", "SUPPORTIVE", "STABLE", "GRADUAL"]
NEG_WORDS = ["UNCERTAINTY", "VOLATILE", "CONCERNS", "WEAKENING", "DOWNSIDE"]

def analyze_core_logic(text):
    """[통합 뇌] 현재와 과거 분석에 공통으로 사용되는 핵심 엔진"""
    text = text.upper()
    all_words = re.findall(r'\w+', text)
    filtered_words = [w for w in all_words if w in TARGET_KEYWORDS]
    top_keywords = Counter(filtered_words).most_common(12)
    sentences = re.split(r'[.!?]', text)
    
    indicators = []
    total_sentiment = 0

    for word, count in top_keywords:
        word_score = 0
        match_sents = [s for s in sentences if word in s]
        if not match_sents: continue

        for sent in match_sents:
            # 맥락 규칙 적용
            score = 0
            if word in CONTEXT_RULES:
                for trigger, weight in CONTEXT_RULES[word].items():
                    if trigger in sent: score += weight
            for p in POS_WORDS:
                if p in sent: score += 1.0
            for n in NEG_WORDS:
                if n in sent: score -= 1.5
            word_score += score
        
        avg_word_score = round(word_score / len(match_sents), 1)
        status = "NEUTRAL"
        if avg_word_score >= 2.0: status = "POSITIVE"
        elif avg_word_score <= -2.0: status = "NEGATIVE"

        indicators.append({
            "word": word, "sentiment_score": avg_word_score, "status": status,
            "display_score": f"+{avg_word_score}" if avg_word_score > 0 else str(avg_word_score),
            "count": count
        })
        total_sentiment += avg_word_score

    avg_temp = round((total_sentiment / len(indicators)) * 10, 1) if indicators else 0.0
    return {"temp": f"+{avg_temp}" if avg_temp > 0 else str(avg_temp), "indicators": indicators, "raw_temp": avg_temp}

def run_all_analysis():
    # 폴더 체크
    if not os.path.exists('PROJECT'): os.makedirs('PROJECT')
    if not os.path.exists('past_minutes'): os.makedirs('past_minutes')

    # --- 1. 현재 데이터 분석 ---
    if os.path.exists('current_minutes.txt'):
        with open('current_minutes.txt', 'r', encoding='utf-8') as f:
            analysis = analyze_core_logic(f.read())
            # 기존 indicators.json (뉴스 데이터 유지하며 업데이트)
            target_path = 'PROJECT/indicators.json'
            try:
                with open(target_path, 'r', encoding='utf-8') as f_old:
                    current_data = json.load(f_old)
            except:
                current_data = {}
            
            current_data["market_temp"] = analysis["temp"]
            current_data["indicators"] = analysis["indicators"]
            
            with open(target_path, 'w', encoding='utf-8') as f_new:
                json.dump(current_data, f_new, ensure_ascii=False, indent=2)
            print(f"✅ 현재 데이터 분석 완료 (PROJECT/indicators.json)")

    # --- 2. 과거 데이터 일괄 분석 ---
    history = []
    files = sorted([f for f in os.listdir('past_minutes') if f.endswith('.txt')])
    for filename in files:
        with open(os.path.join('past_minutes', filename), 'r', encoding='utf-8') as f:
            analysis = analyze_core_logic(f.read())
            history.append({
                "date": filename.replace('.txt', '').replace('_', '-'),
                "score": analysis["raw_temp"]
            })
            print(f"📊 과거 데이터 처리 중: {filename}")
    
    with open('PROJECT/historical_data.json', 'w', encoding='utf-8') as f_hist:
        json.dump(history, f_hist, ensure_ascii=False, indent=2)
    print(f"🚀 총 {len(history)}개의 과거 데이터 동기화 완료 (PROJECT/historical_data.json)")

if __name__ == "__main__":
    run_all_analysis()