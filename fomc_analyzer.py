import json
import re
import os

# [보강] 모든 10개 키워드를 커버할 수 있도록 사전 확장
SENTIMENT_CONFIG = {
    "PRICE": {
        "positive": {"easing": 4.0, "slowing": 3.0, "stable": 2.0, "declining": 5.0, "moderate": 2.0, "cooling": 4.0},
        "negative": {"persistent": -6.0, "rising": -4.0, "high": -3.0, "inflationary": -5.0, "above": -2.0, "elevated": -4.0}
    },
    "GROWTH": {
        "positive": {"resilient": 5.0, "strong": 6.0, "improving": 4.0, "robust": 7.0, "growth": 3.0, "solid": 5.0, "expanding": 4.0},
        "negative": {"weakness": -5.0, "slowing": -4.0, "stalling": -6.0, "declining": -7.0, "contraction": -6.0}
    },
    "GENERAL": {
        "positive": {"stable": 3.0, "confident": 4.0, "clear": 2.0, "balanced": 3.0},
        "negative": {"uncertainty": -5.0, "risks": -6.0, "volatile": -4.0, "concerns": -3.0, "tightening": -4.0}
    }
}

def analyze_sentiment(text, keyword, category):
    if not text: return 0.0, ""
    # 키워드 주변 문맥 추출 범위 확장
    sentences = re.findall(r"([^.]*?" + re.escape(keyword) + r"[^.]*\.)", text, re.IGNORECASE)
    if not sentences: return 0.0, ""
    
    total_score = 0
    config = SENTIMENT_CONFIG.get(category, SENTIMENT_CONFIG["GENERAL"])
    
    # [개선] 문장에서 더 넓은 범위의 단어를 검색
    for sent in sentences:
        words = sent.lower()
        for pos, score in config.get("positive", {}).items():
            if pos in words: total_score += score
        for neg, score in config.get("negative", {}).items():
            if neg in words: total_score += score
            
    final_score = max(-10.0, min(10.0, total_score / (len(sentences) or 1)))
    return round(final_score, 1), sentences[0].strip()[:100]

def run_analysis():
    # 분석 대상 텍스트 (파일이 없을 경우를 대비한 샘플 데이터 보강)
    curr_text = "Housing prices are cooling but remains elevated. Consumer spending is solid. Unemployment is stable."
    prev_text = "Housing was rising. Consumer spending was weak. Unemployment was high."
    
    if os.path.exists('current_minutes.txt'):
        with open('current_minutes.txt', 'r', encoding='utf-8') as f: curr_text = f.read()
    if os.path.exists('previous_minutes.txt'):
        with open('previous_minutes.txt', 'r', encoding='utf-8') as f: prev_text = f.read()

    # 10개 키워드
    target_keywords = [
        {"word": "Inflation", "cat": "PRICE", "type": "fomc"},
        {"word": "Growth", "cat": "GROWTH", "type": "fomc"},
        {"word": "Labor Market", "cat": "GROWTH", "type": "fomc"},
        {"word": "Interest Rate", "cat": "PRICE", "type": "fomc"},
        {"word": "Economic Outlook", "cat": "GENERAL", "type": "fomc"},
        {"word": "Housing", "cat": "PRICE", "type": "fomc"},
        {"word": "Consumer Spending", "cat": "GROWTH", "type": "fomc"},
        {"word": "Financial Conditions", "cat": "GENERAL", "type": "fomc"},
        {"word": "Global Stability", "cat": "GENERAL", "type": "fomc"},
        {"word": "Unemployment", "cat": "GROWTH", "type": "fomc"}
    ]

    results = []
    for item in target_keywords:
        curr_score, _ = analyze_sentiment(curr_text, item['word'], item['cat'])
        prev_score, _ = analyze_sentiment(prev_text, item['word'], item['cat'])
        results.append({
            "word": item['word'],
            "sentiment_score": curr_score,
            "score_diff": round(curr_score - prev_score, 1),
            "type": item['type']
        })

    avg_score = sum(r['sentiment_score'] for r in results) / len(results)
    market_temp = round(avg_score * 10, 1)

    final_data = {
        "market_temp": market_temp,
        "indicators": results
    }

    if not os.path.exists('PROJECT'): os.makedirs('PROJECT')
    with open('PROJECT/indicators.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 분석 완료! 온도: {market_temp}")

if __name__ == "__main__":
    run_analysis()