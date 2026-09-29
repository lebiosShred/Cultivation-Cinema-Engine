import json
json_path = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_results_2024_2026.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
today_draws = [d for d in data if d['Date'] == '2026-08-10' and d['Winning_Combination'] not in ('', 'N/A', None)]
if not today_draws:
    print("No valid draws found for 2026-08-10 yet.")
else:
    for d in today_draws:
        print(f"{d['Draw_Time']}: {d['Winning_Combination']}")
