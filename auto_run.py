import time
import subprocess
from datetime import datetime

print("🚀 SIGNAL 9 자동화 엔진이 가동되었습니다.")
print("이 창을 끄지 마세요. 1시간마다 뉴스를 자동으로 갱신합니다.")

while True:
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[{now}] 🔄 뉴스 업데이트를 시작합니다...")
        
        # news_ai_manager.py 실행
        subprocess.run(["python", "news_ai_manager.py"])
        
        print(f"✅ 업데이트 완료. 1시간 뒤에 다시 실행합니다.")
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
    
    # 3600초(1시간) 대기
    time.sleep(3600)