import yfinance as yf

# 미국 주식 정보를 가져와서 엑셀로 만들어라!
data = yf.download("QQQ", start="2025-01-01")
data.to_csv("QQQ_data.csv")

print("엑셀 파일(money_data.csv)을 다 만들었어요!")