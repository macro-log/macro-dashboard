import json
import re
import os

# 감성 사전 보강 (연준 의사록 특화 단어)
SENTIMENT_CONFIG = {
    "PRICE": {
        "positive": ["easing", "slowing", "stable", "declining", "moderate", "cooling", "low", "subsided"], 
        "negative": ["persistent", "rising", "high", "inflationary", "elevated", "tighten", "upside"]
    },
    "GROWTH": {
        "positive": ["resilient", "strong", "improving", "robust", "growth", "solid", "expanding", "rebound"], 
        "negative": ["weakness", "slowing", "stalling", "declining", "contraction", "soften", "below"]
    },
    "GENERAL": {
        "positive": ["stable", "confident", "clear", "balanced", "supportive", "favorable"], 
        "negative": ["uncertainty", "risks", "volatile", "concerns", "tightening", "shocks"]
    }
}

def analyze_sentiment(text, keyword, category):
    if not text: return 0.0
    # 문장 단위 분리 및 키워드 포함 문장 추출 (대소문자 무시)
    sentences = [s.strip() for s in re.split(r'[.!?]', text.replace('\n', ' ')) if keyword.lower() in s.lower()]
    
    if not sentences:
        return 0.0
    
    total_score = 0
    config = SENTIMENT_CONFIG.get(category, SENTIMENT_CONFIG["GENERAL"])
    
    for sent in sentences:
        sent = sent.lower()
        for p in config["positive"]:
            if p in sent: total_score += 3.5
        for n in config["negative"]:
            if n in sent: total_score -= 4.5
            
    # 매칭된 문장이 있는데 점수가 0이면 아주 미세한 점수(0.1)라도 줘서 0점 방지
    final_score = total_score / len(sentences)
    if final_score == 0: final_score = 0.1
    
    return round(max(-10.0, min(10.0, final_score)), 1)

def run_analysis():
    # 데이터 로드 (파일 없을 시 샘플 데이터)
    curr_text = "Labor market is tight. Housing is slowing. Financial conditions are restrictive. Global stability risks are high."
    if os.path.exists('current_minutes.txt'):
        with open('current_minutes.txt', 'r', encoding='utf-8') as f: curr_text = f.read()

    target_keywords = [
        {"word": "Inflation", "cat": "PRICE"}, {"word": "Growth", "cat": "GROWTH"},
        {"word": "Labor Market", "cat": "GROWTH"}, {"word": "Interest Rate", "cat": "PRICE"},
        {"word": "Economic Outlook", "cat": "GENERAL"}, {"word": "Housing", "cat": "PRICE"},
        {"word": "Consumer Spending", "cat": "GROWTH"}, {"word": "Financial Conditions", "cat": "GENERAL"},
        {"word": "Global Stability", "cat": "GENERAL"}, {"word": "Unemployment", "cat": "GROWTH"}
    ]

    results = []
    print("\n--- FOMC Keyword Analysis ---")
    for item in target_keywords:
        score = analyze_sentiment(curr_text, item['word'], item['cat'])
        print(f"🔍 {item['word']}: {score}점")
        results.append({
            "word": item['word'],
            "sentiment_score": score,
            "score_diff": round(score * 0.1, 1),
            "type": "fomc"
        })

    avg_score = sum(r['sentiment_score'] for r in results) / len(results)
    market_temp = round(avg_score * 10, 1)

    final_data = {"market_temp": market_temp, "indicators": results}

    os.makedirs('PROJECT', exist_ok=True)
    with open('PROJECT/indicators.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 완료! 시장 온도: {market_temp}°\n")

if __name__ == "__main__":
    run_analysis()