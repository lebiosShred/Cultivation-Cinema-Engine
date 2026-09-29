import json
import csv
import os

directory = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev'

# Load original 2 PM clean data from swertres_2pm_2024_2026.json
src_json = os.path.join(directory, 'swertres_2pm_2024_2026.json')
with open(src_json, 'r', encoding='utf-8') as f:
    records_2pm = json.load(f)

# Overwrite main CSV and JSON files to strictly contain 2 PM draws
main_csv = os.path.join(directory, 'swertres_results_2024_2026.csv')
main_json = os.path.join(directory, 'swertres_results_2024_2026.json')

fieldnames = ['Date', 'Draw_Time', 'Winning_Combination', 'Digit_1', 'Digit_2', 'Digit_3']

with open(main_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records_2pm)

with open(main_json, 'w', encoding='utf-8') as f:
    json.dump(records_2pm, f, indent=2)

# Remove 5 PM and 9 PM files and unnecessary scripts
files_to_remove = [
    'swertres_200PM_2024_2026.csv',
    'swertres_500PM_2024_2026.csv',
    'swertres_900PM_2024_2026.csv',
    'split_dataset.py'
]

for fname in files_to_remove:
    fpath = os.path.join(directory, fname)
    if os.path.exists(fpath):
        os.remove(fpath)
        print(f"Removed: {fname}")

print(f"Main datasets updated to contain strictly 2:00 PM draws ({len(records_2pm)} records).")
