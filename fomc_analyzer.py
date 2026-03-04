import json
import re
import os

SENTIMENT_CONFIG = {
    "PRICE": {
        "positive": {"easing": 4.0, "slowing": 3.0, "stable": 2.0, "declining": 5.0, "moderate": 2.0},
        "negative": {"persistent": -6.0, "rising": -4.0, "high": -3.0, "inflationary": -5.0, "above": -2.0}
    },
    "GROWTH": {
        "positive": {"resilient": 5.0, "strong": 6.0, "improving": 4.0, "robust": 7.0, "growth": 3.0},
        "negative": {"weakness": -5.0, "slowing": -4.0, "stalling": -6.0, "declining": -7.0}
    },
    "GENERAL": {
        "negative": {"uncertainty": -5.0, "risks": -6.0, "volatile": -4.0, "concerns": -3.0}
    }
}

def analyze_sentiment(text, keyword, category):
    if not text: return 0.0, ""
    sentences = re.findall(r"([^.]*?" + re.escape(keyword) + r"[^.]*\.)", text, re.IGNORECASE)
    if not sentences: return 0.0, ""
    total_score = 0
    config = SENTIMENT_CONFIG.get(category, SENTIMENT_CONFIG["GENERAL"])
    for sent in sentences:
        words = sent.lower().split()
        for pos, score in config.get("positive", {}).items():
            if pos in words: total_score += score
        for neg, score in config.get("negative", {}).items():
            if neg in words: total_score += score
    final_score = max(-10.0, min(10.0, total_score / (len(sentences) or 1)))
    return round(final_score, 1), sentences[0].strip()[:100]

def run_analysis():
    curr_text = "Inflation remains high. Growth is resilient. Labor market is strong. Interest rate path is uncertain."
    prev_text = "Inflation was rising. Growth was weak."
    
    if os.path.exists('current_minutes.txt'):
        with open('current_minutes.txt', 'r', encoding='utf-8') as f: curr_text = f.read()
    if os.path.exists('previous_minutes.txt'):
        with open('previous_minutes.txt', 'r', encoding='utf-8') as f: prev_text = f.read()

    # [수정] 10개 키워드로 확장
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
            "type": item['type'],
            "source": "FOMC Analysis"
        })

    # [추가] 1단계: 시장 온도 계산 (-100 ~ 100 범위)
    avg_score = sum(r['sentiment_score'] for r in results) / len(results)
    market_temp = round(avg_score * 10, 1)

    # [추가] 3단계: 지표 발표 후 미국 지수 변동성 (수동 업데이트용)
    market_reaction = {
        "SPY": "-0.55%", "QQQ": "-0.82%", "DIA": "-0.15%", "label": "HAWKISH REACTION"
    }

    final_data = {
        "market_temp": market_temp,
        "market_reaction": market_reaction,
        "indicators": results
    }

    if not os.path.exists('PROJECT'): os.makedirs('PROJECT')
    with open('PROJECT/indicators.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 분석 완료! 온도: {market_temp}")

if __name__ == "__main__":
    run_analysis()