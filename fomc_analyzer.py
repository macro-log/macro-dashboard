import json
import os
import time
from openai import OpenAI

# ★ [보안 수정] 깃허브 보안 정책 위반 문자열을 완전히 제거했습니다 ★
# API 키는 GitHub Secrets에 등록한 OPENAI_API_KEY 환경 변수에서 안전하게 가져옵니다.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_with_openai(text, filename):
    """OpenAI GPT-4o-mini를 사용하여 의사록 심층 분석"""
    print(f"🤖 OpenAI 분석 중: {filename}...")
    
    # OpenAI는 문맥 파악 능력이 뛰어나므로 핵심 15,000자 정도를 보냅니다.
    safe_text = text[:15000] 

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 월스트리트의 시니어 연준 정책 분석가야. FOMC 의사록을 분석하여 정교한 데이터(JSON)를 제공해야 해."},
                {"role": "user", "content": f"""
                다음 FOMC 의사록 전문을 읽고 분석해줘.
                
                [명령어]
                1. 종합 점수: 매파적(금리인상 선호)이면 마이너스(-), 비둘기파적(금리인하 선호)이면 플러스(+)로 -10~+10점 사이로 매겨.
                2. 3줄 요약: 이번 의사록의 핵심을 한국어 3줄로 요약해.
                3. 테마 분석: 인플레이션, 고용, 금리 등 주요 키워드 6개에 대해 각각 점수와 뉘앙스를 추출해.

                [응답 포맷 - 반드시 JSON]
                {{
                  "total_score": float,
                  "summary": "3줄 요약문",
                  "themes": [
                    {{ "theme": "키워드", "score": float, "nuance": "뉘앙스 설명" }}
                  ]
                }}

                [의사록 전문]
                {safe_text}
                """}
            ],
            response_format={ "type": "json_object" } # JSON 모드 강제
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ {filename} 분석 실패: {e}")
        return None

def run_all_analysis():
    past_dir = 'past_minutes'
    project_dir = 'PROJECT'
    if not os.path.exists(project_dir): os.makedirs(project_dir)

    history_path = os.path.join(project_dir, 'historical_data.json')
    history_data = []
    
    # 이어하기 기능: 이미 분석된 파일은 건너뜁니다.
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except: pass

    done_dates = [item['date'] for item in history_data]
    files = sorted([f for f in os.listdir(past_dir) if f.endswith('.txt')])
    latest_analysis = None

    print(f"🚀 총 {len(files)}개의 의사록 분석을 시작합니다. (OpenAI GPT-4o-mini)")

    for filename in files:
        date_label = filename.replace('.txt', '')
        if date_label in done_dates:
            print(f"⏭️ {filename} 스킵")
            continue

        file_path = os.path.join(past_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        analysis = analyze_with_openai(content, filename)
        
        if analysis:
            score = analysis.get("total_score", 0.0)
            history_data.append({"date": date_label, "score": score})
            latest_analysis = analysis
            print(f"✅ 완료: {filename} (점수: {score})")
            
            # 파일 하나 끝날 때마다 즉시 저장
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        # OpenAI는 처리 속도가 매우 빠르므로 1~2초만 쉬어도 충분합니다.
        time.sleep(1)

    # indicators.json 업데이트 (메인 화면용 최신 정보 반영)
    if latest_analysis:
        try:
            with open(os.path.join(project_dir, 'indicators.json'), 'r', encoding='utf-8') as f_old:
                current_indicators = json.load(f_old)
        except: current_indicators = {}

        total_score = latest_analysis.get("total_score", 0.0)
        current_indicators["market_temp"] = f"+{total_score}" if total_score > 0 else str(total_score)
        current_indicators["fomc_summary"] = latest_analysis.get("summary", "요약 정보 없음")
        
        fomc_indicators = []
        for t in latest_analysis.get("themes", []):
            sc = t.get("score", 0.0)
            fomc_indicators.append({
                "word": t.get("theme", "알수없음").upper(),
                "sentiment_score": sc,
                "status": "POSITIVE" if sc >= 1.5 else ("NEGATIVE" if sc <= -1.5 else "NEUTRAL"),
                "display_score": f"+{sc}" if sc > 0 else str(sc),
                "count": 1
            })
        current_indicators["fomc_indicators"] = fomc_indicators
        with open(os.path.join(project_dir, 'indicators.json'), 'w', encoding='utf-8') as f_new:
            json.dump(current_indicators, f_new, ensure_ascii=False, indent=2)

    print(f"🏁 모든 분석 완료! {len(history_data)}개 데이터 동기화.")

if __name__ == "__main__":
    run_all_analysis()