import sqlite3

db_path = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_history.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Recent 2:00 PM Draws ---")
cursor.execute("SELECT draw_date, draw_time, winning_combination, digit_1, digit_2, digit_3 FROM swertres_draws WHERE draw_date >= '2026-08-01' ORDER BY draw_date DESC;")
for row in cursor.fetchall():
    print(row)

print("\n--- Frequency of Winning Combinations (Top 5) ---")
cursor.execute("SELECT winning_combination, COUNT(*) as frequency FROM swertres_draws WHERE winning_combination != 'N/A' GROUP BY winning_combination ORDER BY frequency DESC LIMIT 5;")
for row in cursor.fetchall():
    print(f"Combination: {row[0]} | Appeared: {row[1]} times")

conn.close()
