import json
import csv
import os

json_src = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_results_2024_2026.json'
with open(json_src, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter strictly for 2:00 PM draws
pm2_records = [item for item in data if item.get('Draw_Time') == '2:00 PM']

output_csv = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_2pm_2024_2026.csv'
output_json = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_2pm_2024_2026.json'

# Format records cleanly preserving string leading zeros and integer digits
formatted_records = []
for item in pm2_records:
    comb = str(item['Winning_Combination']).zfill(3) if item['Winning_Combination'] not in (None, 'N/A', '') else 'N/A'
    d1 = int(item['Digit_1']) if item.get('Digit_1') not in (None, '') else ''
    d2 = int(item['Digit_2']) if item.get('Digit_2') not in (None, '') else ''
    d3 = int(item['Digit_3']) if item.get('Digit_3') not in (None, '') else ''
    
    formatted_records.append({
        'Date': item['Date'],
        'Draw_Time': item['Draw_Time'],
        'Winning_Combination': comb,
        'Digit_1': d1,
        'Digit_2': d2,
        'Digit_3': d3
    })

# Write CSV
fieldnames = ['Date', 'Draw_Time', 'Winning_Combination', 'Digit_1', 'Digit_2', 'Digit_3']
with open(output_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(formatted_records)

# Write JSON
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(formatted_records, f, indent=2)

print(f"Exported {len(formatted_records)} clean 2:00 PM records to CSV and JSON.")
