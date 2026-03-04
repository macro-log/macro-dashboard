import json
import re
import os

# 1. 카테고리별 감성 사전 (점수 가중치 방식 적용)
# 리스트 대신 딕셔너리로 써서 단어마다 파워를 조절할 수 있게 바꿨습니다.
SENTIMENT_CONFIG = {
    "PRICE": {
        "positive": {"easing": 4.0, "slowing": 3.0, "stable": 2.0, "declining": 5.0, "moderate": 2.0, "below": 2.0},
        "negative": {"persistent": -6.0, "rising": -4.0, "high": -3.0, "inflationary": -5.0, "above": -2.0, "stalling": -4.0}
    },
    "GROWTH": {
        "positive": {"rising": 3.0, "resilient": 5.0, "strong": 6.0, "improving": 4.0, "robust": 7.0, "growth": 3.0},
        "negative": {"weakness": -5.0, "slowing": -4.0, "stalling": -6.0, "declining": -7.0, "concerns": -3.0, "below": -2.0}
    },
    "GENERAL": {
        "negative": {"uncertainty": -5.0, "risks": -6.0, "volatile": -4.0, "concerns": -3.0, "unpredictable": -5.0}
    }
}

def analyze_sentiment(text, keyword, category):
    if not text: return 0.0, "데이터 없음"
    sentences = re.findall(r"([^.]*?" + re.escape(keyword) + r"[^.]*\.)", text, re.IGNORECASE)
    if not sentences: return 0.0, "Context not found"

    total_score = 0
    config = SENTIMENT_CONFIG.get(category, SENTIMENT_CONFIG["GENERAL"])
    
    for sent in sentences:
        words = sent.lower().split()
        # 개별 가중치 점수 합산
        for pos, score in config.get("positive", {}).items():
            if pos in words: total_score += score
        for neg, score in config.get("negative", {}).items():
            if neg in words: total_score += score
        for gen_neg, score in SENTIMENT_CONFIG["GENERAL"]["negative"].items():
            if gen_neg in words: total_score += (score * 0.5)

    final_score = max(-10.0, min(10.0, total_score / (len(sentences) or 1)))
    return round(final_score, 1), sentences[0].strip()[:100]

def run_analysis():
    # [핵심] 파일 읽기 로직 추가
    curr_text = ""
    prev_text = ""
    
    if os.path.exists('current_minutes.txt'):
        with open('current_minutes.txt', 'r', encoding='utf-8') as f: curr_text = f.read()
    else:
        print("⚠️ current_minutes.txt 파일이 없습니다! 예시 텍스트로 대체합니다.")
        curr_text = "Inflation remains rising. Growth is resilient."

    if os.path.exists('previous_minutes.txt'):
        with open('previous_minutes.txt', 'r', encoding='utf-8') as f: prev_text = f.read()

    target_keywords = [
        {"word": "Inflation", "cat": "PRICE", "type": "fomc"},
        {"word": "Growth", "cat": "GROWTH", "type": "fomc"},
        {"word": "Labor Market", "cat": "GROWTH", "type": "fomc"},
        {"word": "Economic Outlook", "cat": "GENERAL", "type": "fomc"},
        {"word": "Interest Rate", "cat": "PRICE", "type": "fomc"}
    ]

    results = []
    for item in target_keywords:
        # 현재 vs 과거 분석 실행
        curr_score, curr_context = analyze_sentiment(curr_text, item['word'], item['cat'])
        prev_score, _ = analyze_sentiment(prev_text, item['word'], item['cat'])
        
        # 격차 계산 (Delta)
        score_diff = round(curr_score - prev_score, 1)
        curr_count = curr_text.lower().count(item['word'].lower())
        prev_count = prev_text.lower().count(item['word'].lower())

        results.append({
            "word": item['word'],
            "sentiment_score": curr_score,
            "prev_score": prev_score,
            "score_diff": score_diff, # 지난번 대비 변화량
            "count": curr_count,
            "count_diff": curr_count - prev_count,
            "trend": "up" if score_diff >= 0 else "down",
            "impact": "High" if abs(curr_score) > 6 else "Mid",
            "context": curr_context,
            "type": item['type'],
            "source": "FOMC Analysis"
        })

    # [핵심] PROJECT 폴더 내부로 정확하게 배달
    save_path = os.path.join('PROJECT', 'indicators.json')
    
    # PROJECT 폴더가 없으면 에러날 수 있으니 자동 생성 로직 추가
    if not os.path.exists('PROJECT'):
        os.makedirs('PROJECT')

    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 분석 완료! 데이터가 '{save_path}'에 저장되었습니다.")

if __name__ == "__main__":
    run_analysis()