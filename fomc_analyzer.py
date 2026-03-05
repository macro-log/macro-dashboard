import json
import re
import os
from collections import Counter

# 감성 사전 (긍정/부정 단어 뭉치)
POS_WORDS = ["easing", "slowing", "stable", "declining", "moderate", "cooling", "resilient", "strong", "growth", "robust", "supportive"]
NEG_WORDS = ["persistent", "rising", "high", "inflationary", "elevated", "tighten", "uncertainty", "risks", "volatile", "concerns"]

def run_analysis():
    # 1. 의사록 읽기
    text = "Labor market is strong but inflation remains elevated. Housing sector is cooling. Risks are rising."
    if os.path.exists('current_minutes.txt'):
        with open('current_minutes.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    
    # 2. 전처리 및 상위 키워드 추출 (불용어 제외)
    words = re.findall(r'\w+', text.lower())
    stop_words = ['the', 'and', 'to', 'of', 'in', 'that', 'is', 'for', 'on', 'with', 'as', 'was', 'were', 'at', 'by', 'it', 'from', 'be', 'an', 'has', 'have', 'committee', 'participants', 'noted', 'also', 'would', 'could', 'should']
    filtered_words = [w for w in words if w not in stop_words and len(w) > 4]
    
    # 가장 많이 언급된 상위 10개 단어
    top_10_counts = Counter(filtered_words).most_common(10)
    
    results = []
    total_sentiment = 0
    
    # 3. 각 키워드가 포함된 문장에서 감성 분석
    sentences = re.split(r'[.!?]', text.lower())
    
    for word, count in top_10_counts:
        word_score = 0
        match_sentences = [s for s in sentences if word in s]
        
        for sent in match_sentences:
            for pos in POS_WORDS:
                if pos in sent: word_score += 3
            for neg in NEG_WORDS:
                if neg in sent: word_score -= 4
        
        # 문장당 평균 점수 계산 (최소 -10, 최대 10)
        final_word_score = round(max(-10, min(10, word_score / (len(match_sentences) or 1))), 1)
        # 만약 언급은 됐는데 감성 단어가 없으면 중립(0.5)이라도 부여해서 0점 방지
        if final_word_score == 0: final_word_score = 0.5
        
        results.append({
            "word": word.upper(),
            "sentiment_score": final_word_score,
            "score_diff": round(final_word_score * 0.1, 1),
            "type": "fomc"
        })
        total_sentiment += final_word_score

    # 4. 시장 온도 계산
    market_temp = round((total_sentiment / 10) * 10, 1)
    
    final_data = {"market_temp": market_temp, "indicators": results}
    
    os.makedirs('PROJECT', exist_ok=True)
    with open('PROJECT/indicators.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 분석 완료! 빈도 기반 상위 10개 추출 완료. 온도: {market_temp}")

if __name__ == "__main__":
    run_analysis()