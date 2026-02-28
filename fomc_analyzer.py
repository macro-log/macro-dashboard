import re
from collections import Counter
import pandas as pd
import json

# -----------------------------
# 텍스트 정리 (전처리)
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
        "could", "should", "been", "been"
    ])

    words = [w for w in words if w not in stopwords and len(w) > 3]
    return words

# -----------------------------
# 단어 빈도 계산
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
# 변화율 계산 및 JSON 저장
# -----------------------------
def analyze_and_save(current_file, compare_file, output_json):
    print(f"\n[{output_json}] 분석 중...")
    
    current_freq = get_word_freq(current_file)
    compare_freq = get_word_freq(compare_file)
    
    if not current_freq or not compare_freq:
        print("데이터가 부족하여 분석을 건너뜁니다.")
        return

    rows = []
    # 두 의사록의 모든 단어 집합
    all_words = set(current_freq.keys()).union(set(compare_freq.keys()))

    for word in all_words:
        cur = current_freq.get(word, 0)
        comp = compare_freq.get(word, 0)
        
        # 변화율 계산 (분모가 0일 경우 처리)
        if comp == 0:
            change_rate = float('inf') if cur > 0 else 0
        else:
            change_rate = (cur - comp) / comp

        rows.append({"word": word, "current": cur, "compare": comp, "change_rate": change_rate})

    # 데이터프레임 변환 및 정렬 (변화폭이 가장 큰 단어순)
    df = pd.DataFrame(rows)
    df = df.sort_values(by="change_rate", key=lambda x: x.abs(), ascending=False)
    
    # 💡 웹사이트 연동 핵심: JSON 파일로 저장
    top_words = df.head(50) # 상위 50개만 저장
    top_words.to_json(output_json, orient="records", force_ascii=False)
    print(f"✅ {output_json} 파일 생성 완료!")

# -----------------------------
# 실행
# -----------------------------
if __name__ == "__main__":
    # 파일 경로 설정 (signal9 폴더 안에 있어야 함)
    current = "current_minutes.txt"
    previous = "previous_minutes.txt"
    last_year = "last_year_minutes.txt"

    # 1. 직전 의사록 대비 분석
    analyze_and_save(current, previous, "change_vs_previous.json")
    
    # 2. 1년 전 대비 분석
    analyze_and_save(current, last_year, "change_vs_last_year.json")