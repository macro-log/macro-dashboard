import json
import re

# 1. 카테고리별 감성 사전 (알잘딱하게 분류)
SENTIMENT_CONFIG = {
    "PRICE": { # 물가 관련 (낮아져야 좋음)
        "positive": ["easing", "slowing", "stable", "declining", "moderate", "below"],
        "negative": ["persistent", "rising", "high", "inflationary", "above", "stalling"]
    },
    "GROWTH": { # 성장/고용 관련 (높아져야 좋음)
        "positive": ["rising", "resilient", "strong", "improving", "robust", "growth"],
        "negative": ["weakness", "slowing", "stalling", "declining", "concerns", "below"]
    },
    "GENERAL": { # 공통 (불확실성 등)
        "negative": ["uncertainty", "risks", "volatile", "concerns", "unpredictable"]
    }
}

def analyze_sentiment(text, keyword, category):
    sentences = re.findall(r"([^.]*?" + re.escape(keyword) + r"[^.]*\.)", text, re.IGNORECASE)
    if not sentences: return 0.0, "No context"

    total_score = 0
    config = SENTIMENT_CONFIG.get(category, SENTIMENT_CONFIG["GENERAL"])
    
    for sent in sentences:
        words = sent.lower().split()
        # 긍정 단어 체크
        for pos in config.get("positive", []):
            if pos in words: total_score += 3
        # 부정 단어 체크
        for neg in config.get("negative", []):
            if neg in words: total_score -= 4
        # 공통 부정어 체크
        for gen_neg in SENTIMENT_CONFIG["GENERAL"]["negative"]:
            if gen_neg in words: total_score -= 2

    # -10 ~ 10 사이로 정규화
    final_score = max(-10.0, min(10.0, total_score / (len(sentences) or 1)))
    return round(final_score, 1), sentences[0].strip()[:100]

def run_analysis():
    # 분석할 원문 (예시)
    fomc_text = """
    Inflation remains rising and persistent. However, economic growth is resilient and strong. 
    Labor market shows some weakness but stays stable. Geopolitical risks create uncertainty.
    """

    # 키워드별 카테고리 지정 (형이 원하는 거 여기서 추가!)
    target_keywords = [
        {"word": "Inflation", "cat": "PRICE", "type": "fomc"},
        {"word": "Growth", "cat": "GROWTH", "type": "fomc"},
        {"word": "Labor Market", "cat": "GROWTH", "type": "fomc"}, # 고용도 성장 관점
        {"word": "Economic Outlook", "cat": "GENERAL", "type": "fomc"}
    ]

    results = []
    for item in target_keywords:
        score, context = analyze_sentiment(fomc_text, item['word'], item['cat'])
        results.append({
            "word": item['word'],
            "count": fomc_text.lower().count(item['word'].lower()),
            "sentiment_score": score,
            "trend": "up" if score > 0 else "down",
            "impact": "High" if abs(score) > 6 else "Mid",
            "context": context,
            "type": item['type'],
            "source": "FOMC Analysis"
        })

    with open('indicators.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("✅ 멀티 카테고리 분석 완료!")

if __name__ == "__main__":
    run_analysis()