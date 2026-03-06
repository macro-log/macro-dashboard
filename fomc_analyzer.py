import json
import re
import os
from collections import Counter

# 1. 추적할 핵심 경제 키워드 (쓰레기 단어 필터링)
TARGET_KEYWORDS = [
    "INFLATION", "EMPLOYMENT", "RATE", "ECONOMY", "LABOR", "PRICES", "GROWTH",
    "STABILITY", "RISKS", "DEMAND", "SUPPLY", "SPENDING", "WAGES", "HOUSING",
    "ENERGY", "TIGHTENING", "EASING", "GDP", "POLICY", "BANKING", "CREDIT"
]

# 2. [핵심] 단어별 맥락 규칙 (형님이 나중에 여기에 단어를 추가하시면 됩니다)
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

# 3. 일반적인 긍/부정 단어 (보조 지표)
POS_WORDS = ["MODERATE", "RESILIENT", "SUPPORTIVE", "STABLE", "GRADUAL"]
NEG_WORDS = ["UNCERTAINTY", "VOLATILE", "CONCERNS", "WEAKENING", "DOWNSIDE"]

def analyze_sentence(word, sentence):
    """문장 내 맥락을 읽어 점수를 계산"""
    word = word.upper()
    sentence = sentence.upper()
    score = 0
    found_rule = False

    # 규칙 기반 분석
    if word in CONTEXT_RULES:
        for trigger, weight in CONTEXT_RULES[word].items():
            if trigger in sentence:
                score += weight
                found_rule = True
    
    # 일반 감성 분석 (보조)
    for p in POS_WORDS:
        if p in sentence: score += 1.0
    for n in NEG_WORDS:
        if n in sentence: score -= 1.5
        
    return score, found_rule

def run_fomc_analysis():
    # 파일 읽기
    if not os.path.exists('current_minutes.txt'):
        print("❌ current_minutes.txt 파일을 찾을 수 없습니다.")
        return

    with open('current_minutes.txt', 'r', encoding='utf-8') as f:
        text = f.read().upper()

    # 단어 추출 및 필터링
    all_words = re.findall(r'\w+', text)
    filtered_words = [w for w in all_words if w in TARGET_KEYWORDS]
    top_keywords = Counter(filtered_words).most_common(12)

    sentences = re.split(r'[.!?]', text)
    indicators = []
    total_sentiment = 0

    for word, count in top_keywords:
        word_score = 0
        match_sents = [s for s in sentences if word in s]
        
        if not match_sents:
            continue

        for sent in match_sents:
            score, _ = analyze_sentence(word, sent)
            word_score += score
        
        # 문장 수로 나눠서 평균값 산출
        avg_word_score = round(word_score / len(match_sents), 1)
        
        # [비판적 조언 적용] -2.0 ~ 2.0 사이는 'NEUTRAL(중립)'로 분류
        status = "NEUTRAL"
        if avg_word_score >= 2.0: status = "POSITIVE"
        elif avg_word_score <= -2.0: status = "NEGATIVE"

        indicators.append({
            "word": word,
            "sentiment_score": avg_word_score,
            "status": status, # 웹에서 색깔 정할 때 사용
            "display_score": f"+{avg_word_score}" if avg_word_score > 0 else str(avg_word_score),
            "count": count
        })
        total_sentiment += avg_word_score

    # 결과 저장 (기존 뉴스 데이터 보존)
    target_file = 'indicators.json'
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
    
    print(f"✅ 분석 완료! 온도: {avg_temp} / 키워드 {len(indicators)}개 추출")

if __name__ == "__main__":
    run_fomc_analysis()