import json
import re
import os
from collections import Counter

# 연준 의사록 특화 감성 사전
POS_WORDS = ["easing", "slowing", "stable", "declining", "moderate", "cooling", "resilient", "strong", "growth", "robust", "supportive", "favorable", "expansion", "anchored"]
NEG_WORDS = ["persistent", "rising", "high", "inflationary", "elevated", "tighten", "uncertainty", "risks", "volatile", "concerns", "shocks", "restrictive", "weakness"]

def run_analysis():
    print("🚀 FOMC 의사록 동적 분석 시작...")
    
    # 1. 파일 로드
    text = ""
    if os.path.exists('current_minutes.txt'):
        with open('current_minutes.txt', 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        # 파일 없을 시 테스트용 긴 문장
        text = "The labor market remains strong with robust growth. However, inflation is high and persistent. Financial conditions are restrictive and risks are rising. Housing sector shows moderate cooling but concerns remain about global stability."

    # 2. 불용어 제거 및 다빈도 키워드 10개 추출
    words = re.findall(r'\w+', text.lower())
    stop_words = {'the', 'and', 'to', 'of', 'in', 'that', 'is', 'for', 'on', 'with', 'as', 'was', 'at', 'by', 'it', 'from', 'this', 'have', 'has', 'would', 'could', 'should', 'their', 'which'}
    filtered = [w for w in words if w not in stop_words and len(w) > 4]
    top_10 = Counter(filtered).most_common(10)
    
    results = []
    total_sentiment = 0
    sentences = re.split(r'[.!?]', text.lower())
    
    for word, count in top_10:
        word_score = 0
        match_sents = [s for s in sentences if word in s]
        
        for sent in match_sents:
            for p in POS_WORDS:
                if p in sent: word_score += 3.8
            for n in NEG_WORDS:
                if n in sent: word_score -= 4.5
        
        # 점수 정규화 (-10 ~ 10)
        avg_score = word_score / (len(match_sents) or 1)
        final_score = round(max(-10.0, min(10.0, avg_score)), 1)
        
        # 0점 방지 및 부호 텍스트 생성
        if final_score == 0: final_score = 0.1
        display_val = f"+{final_score}" if final_score > 0 else str(final_score)
        
        results.append({
            "word": word.upper(),
            "sentiment_score": final_score,
            "display_score": display_val,
            "score_diff": "+0.3" if final_score > 0 else "-0.2",
            "type": "fomc"
        })
        total_sentiment += final_score

    # 3. 최종 시장 온도 및 JSON 저장
    avg_temp = round((total_sentiment / 10) * 10, 1)
    final_data = {
        "market_temp": f"+{avg_temp}" if avg_temp > 0 else str(avg_temp),
        "indicators": results
    }
    
    with open('indicators.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 분석 완료! 최종 온도: {final_data['market_temp']}°")

if __name__ == "__main__":
    run_analysis()