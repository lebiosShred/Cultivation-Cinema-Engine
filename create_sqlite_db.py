import sqlite3
import json
import os

db_path = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_history.db'
json_path = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev\swertres_results_2024_2026.json'

with open(json_path, 'r', encoding='utf-8') as f:
    records = json.load(f)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table with constraints and indexes
cursor.execute('''
CREATE TABLE IF NOT EXISTS swertres_draws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    draw_date TEXT NOT NULL,
    draw_time TEXT NOT NULL,
    winning_combination TEXT NOT NULL,
    digit_1 INTEGER,
    digit_2 INTEGER,
    digit_3 INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(draw_date, draw_time)
);
''')

cursor.execute('CREATE INDEX IF NOT EXISTS idx_draw_date ON swertres_draws(draw_date);')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_winning_combination ON swertres_draws(winning_combination);')

# Insert or replace records
for r in records:
    d1 = int(r['Digit_1']) if r.get('Digit_1') not in (None, '') else None
    d2 = int(r['Digit_2']) if r.get('Digit_2') not in (None, '') else None
    d3 = int(r['Digit_3']) if r.get('Digit_3') not in (None, '') else None
    
    cursor.execute('''
    INSERT OR REPLACE INTO swertres_draws (draw_date, draw_time, winning_combination, digit_1, digit_2, digit_3)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (r['Date'], r['Draw_Time'], r['Winning_Combination'], d1, d2, d3))

conn.commit()

# Verify count
cursor.execute('SELECT COUNT(*) FROM swertres_draws;')
count = cursor.fetchone()[0]

conn.close()

db_size = os.path.getsize(db_path)
print(f"Successfully created SQLite database: {db_path}")
print(f"Total inserted records: {count}")
print(f"Database file size: {db_size / 1024:.2f} KB")
