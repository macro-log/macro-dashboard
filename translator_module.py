# 파일명: translator_module.py
from googletrans import Translator
import re

class FinancialTranslator:
    def __init__(self):
        self.translator = Translator()
        # 오역 방지 사전 (필요한 단어를 계속 추가하세요)
        self.glossary = {
            'Hawkish': '매파적(긴축 선호)',
            'Dovish': '비둘기파적(완화 선호)',
            'Rate Hike': '금리 인상',
            'Rate Cut': '금리 인하',
            'Fed': '연준',
            'FOMC Minutes': 'FOMC 의사록',
            'Benchmark': '기준 금리',
            'Tightening': '긴축',
            'Easing': '완화'
        }

    def clean_text(self, text):
        # 언론사명 제거 (예: - Reuters, | CNBC)
        text = re.sub(r'[-|]\s.*$', '', text)
        return text.strip()

    def translate(self, text):
        cleaned_text = self.clean_text(text)
        try:
            # 1차 구글 번역
            result = self.translator.translate(cleaned_text, src='en', dest='ko').text
            # 2차 금융 용어 강제 보정
            for eng, kor in self.glossary.items():
                if eng == 'Hawkish':
                    result = result.replace('매의', kor).replace('매와 같은', kor)
                elif eng == 'Dovish':
                    result = result.replace('비둘기', kor)
                else:
                    result = result.replace(eng, kor)
            return result
        except:
            return cleaned_text