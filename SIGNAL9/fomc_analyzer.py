import re
from collections import Counter
import pandas as pd
import json

# -----------------------------
# 텍스트 정리 (전처리) - 수정 없음
# -----------------------------
def clean_text(text):
    text = text.lower()
    # 영문자만 남기기
    text = re.sub(r'[^a-z\s]', ' ', text)
    words = text.split()

    # 금융 도메인 맞춤형 불용어 제거
    stopwords = set([
        "the","and","of","to","in","a","for","is","on",
        "that","with","as","by","at","an","be","this","it",
        "were","was","are","from","or","but","not","have",
        "had","has","their","they","them","its", "will", "would",
        "could", "should", "been", "been", "meeting", "committee", "fed", "federal"
    ])

    words = [w for w in words if w not in stopwords and len(w) > 3]
    return words

# -----------------------------
# 단어 빈도 계산 - 수정 없음
# -----------------------------
def get_word_freq(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        words = clean_text(text)
        return Counter(words)
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {filepath}")
        return Counter()

# -----------------------------
# [수정] 분석 및 통합 JSON 저장
# -----------------------------
def analyze_and_save(current_file, compare_file, output_json):
    print(f"\n[{output_json}] 분석 중...")
    
    current_freq = get_word_freq(current_file)
    compare_freq = get_word_freq(compare_file)
    
    if not current_freq or not compare_freq:
        print("데이터가 부족하여 분석을 건너뜁니다.")
        return

    rows = []
    all_words = set(current_freq.keys()).union(set(compare_freq.keys()))

    for word in all_words:
        cur = current_freq.get(word, 0)
        comp = compare_freq.get(word, 0)
        
        # 변화율 계산
        if comp == 0:
            change_rate = float('inf') if cur > 0 else 0
        else:
            change_rate = (cur - comp) / comp

        # [수정] 데이터 형태를 UI에 맞게 변경
        rows.append({
            "word": word, 
            "delta": f"{'+' if change_rate > 0 else ''}{change_rate:.2%}" # 변화율을 %로 표현
        })

    # 데이터프레임 변환 및 정렬 (변화폭이 가장 큰 단어순)
    df = pd.DataFrame(rows)
    df = df.sort_values(by="word", ascending=False) # 단어 순 정렬
    
    # 💡 웹사이트 연동 핵심: 모든 단어가 아닌 top 10만 추출
    top_words = df.head(10).to_dict(orient="records")
    
    # [수정] Scenario 데이터 임시 생성 (실제 구현시 자동화 필요)
    scenario_text = "이번 회의에서는 금리 인하에 대한 논의가 전월 대비 완화되었으며, 인플레이션 상승 위험이 높게 평가되었습니다."

    # [핵심] JSON 파일 구조 통합
    final_data = {
        "scenario": scenario_text,
        "keywords": top_words
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ {output_json} 파일 생성 완료!")

# -----------------------------
# 실행
# -----------------------------
if __name__ == "__main__":
    # 파일 경로 설정 (signal9 폴더 안에 있어야 함)
    current = "current_minutes.txt"
    previous = "previous_minutes.txt"

    # [수정] 💡 웹사이트는 indicators.json 만 필요함
    analyze_and_save(current, previous, "indicators.json")