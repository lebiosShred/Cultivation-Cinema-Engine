import sqlite3

db_path = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_history.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("==================================================")
print(" 📊 ADVANCED STATISTICAL SQL ANALYSIS: SWERTRES 3D")
print("==================================================\n")

# 1. The "Coldest" Numbers (Longest Drought for Drawn Numbers)
print("--- 1. Longest Drought (Numbers that haven't appeared in the longest time) ---")
cursor.execute("""
    SELECT winning_combination, MAX(draw_date) as last_seen 
    FROM swertres_draws 
    WHERE winning_combination != 'N/A'
    GROUP BY winning_combination 
    ORDER BY last_seen ASC 
    LIMIT 5;
""")
for row in cursor.fetchall():
    print(f"Combo: {row[0]} | Last Seen: {row[1]}")

print("\n--- 2. Frequency of 'Triples' (e.g., 000, 777, 999) ---")
cursor.execute("""
    SELECT winning_combination, COUNT(*) as frequency 
    FROM swertres_draws 
    WHERE winning_combination != 'N/A' 
      AND digit_1 = digit_2 
      AND digit_2 = digit_3 
    GROUP BY winning_combination 
    ORDER BY frequency DESC;
""")
triples = cursor.fetchall()
if triples:
    for row in triples:
        print(f"Triple: {row[0]} | Frequency: {row[1]}")
else:
    print("No triples have been drawn in the 2:00 PM slot over the last 2 years!")

print("\n--- 3. Monthly Draw Volume Analysis (Which month had the most non-N/A draws?) ---")
cursor.execute("""
    SELECT strftime('%Y-%m', draw_date) as month, COUNT(*) as total_draws
    FROM swertres_draws
    WHERE winning_combination != 'N/A'
    GROUP BY month
    ORDER BY total_draws DESC
    LIMIT 5;
""")
for row in cursor.fetchall():
    print(f"Month: {row[0]} | Valid Draws: {row[1]}")

print("\n--- 4. Sum of Digits Frequency (The Bell Curve Peaks) ---")
cursor.execute("""
    SELECT (digit_1 + digit_2 + digit_3) as combo_sum, COUNT(*) as frequency
    FROM swertres_draws
    WHERE winning_combination != 'N/A'
    GROUP BY combo_sum
    ORDER BY frequency DESC
    LIMIT 5;
""")
for row in cursor.fetchall():
    print(f"Sum of Digits: {row[0]} | Appeared {row[1]} times")

print("\n==================================================")
conn.close()
