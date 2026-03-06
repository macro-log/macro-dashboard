import json
import re
import os
from collections import Counter

# 1. 추적할 핵심 경제 키워드 (THEIR, REMAINED 등 쓰레기 단어 완벽 차단)
TARGET_KEYWORDS = [
    "INFLATION", "EMPLOYMENT", "RATE", "ECONOMY", "LABOR", "PRICES", "GROWTH",
    "STABILITY", "RISKS", "DEMAND", "SUPPLY", "SPENDING", "WAGES", "HOUSING",
    "ENERGY", "TIGHTENING", "EASING", "GDP", "POLICY", "BANKING", "CREDIT"
]

# 2. 단어별 맥락 규칙
CONTEXT_RULES = {
    "SUPPLY": {
        "INCREASED": 2.5, "RECOVERY": 2.0, "LABOR": 1.5,
        "CONSTRAINTS": -4.5, "DISRUPTION": -5.0, "SHORTAGES": -4.0, "TIGHT": -3.0
    },
    "INFLATION": {
        "EASING": 5.0, "DECLINING": 4.0, "SLOWING": 3.5,
        "PERSISTENT": -5.0, "ELEVATED": -4.0, "HIGH": -3.5, "STUBBORN": -4.5
    },
    "RATE": {
        "HIKE": -5.0, "TIGHTENING": -4.0, "INCREASE": -3.5,
        "CUT": 5.0, "EASING": 4.5, "PAUSE": 2.5, "LOWER": 3.0
    },
    "LABOR": {
        "STRONG": 2.0, "BALANCED": 3.0, "COOLING": 2.5,
        "TIGHT": -3.5, "SHORTAGES": -3.0
    }
}

POS_WORDS = ["MODERATE", "RESILIENT", "SUPPORTIVE", "STABLE", "GRADUAL"]
NEG_WORDS = ["UNCERTAINTY", "VOLATILE", "CONCERNS", "WEAKENING", "DOWNSIDE"]

def analyze_sentence(word, sentence):
    word = word.upper()
    sentence = sentence.upper()
    score = 0
    found_rule = False

    if word in CONTEXT_RULES:
        for trigger, weight in CONTEXT_RULES[word].items():
            if trigger in sentence:
                score += weight
                found_rule = True
    
    for p in POS_WORDS:
        if p in sentence: score += 1.0
    for n in NEG_WORDS:
        if n in sentence: score -= 1.5
        
    return score, found_rule

def run_fomc_analysis():
    # [중요] 분석 대상 텍스트 파일 위치 확인
    if not os.path.exists('current_minutes.txt'):
        print("❌ current_minutes.txt 파일을 찾을 수 없습니다.")
        return

    with open('current_minutes.txt', 'r', encoding='utf-8') as f:
        text = f.read().upper()

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
            score, _ = analyze_sentence(word, sent)
            word_score += score
        
        avg_word_score = round(word_score / len(match_sents), 1)
        
        status = "NEUTRAL"
        if avg_word_score >= 2.0: status = "POSITIVE"
        elif avg_word_score <= -2.0: status = "NEGATIVE"

        indicators.append({
            "word": word,
            "sentiment_score": avg_word_score,
            "status": status,
            "display_score": f"+{avg_word_score}" if avg_word_score > 0 else str(avg_word_score),
            "count": count
        })
        total_sentiment += avg_word_score

    # [핵심 수정] 배포용 폴더인 PROJECT 내부의 json을 업데이트하도록 경로 변경
    target_file = 'PROJECT/indicators.json'
    
    if not os.path.exists('PROJECT'):
        os.makedirs('PROJECT')

    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
    except:
        current_data = {}

    avg_temp = round((total_sentiment / len(indicators)) * 10, 1) if indicators else 0.0
    current_data["market_temp"] = f"+{avg_temp}" if avg_temp > 0 else str(avg_temp)
    current_data["indicators"] = indicators
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 분석 완료! 결과가 {target_file}에 저장되었습니다. (온도: {avg_temp})")

if __name__ == "__main__":
    run_fomc_analysis()