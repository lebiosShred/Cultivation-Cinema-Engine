import os
import re
import csv
import json
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Constants
START_DATE_STR = '2024-08-10'
END_DATE_STR = '2026-08-10'
OUTPUT_DIR = r'c:\Users\SkyDr\Documents\antigravity\elegant-mendeleev'
CSV_FILEPATH = os.path.join(OUTPUT_DIR, 'swertres_results_2024_2026.csv')
JSON_FILEPATH = os.path.join(OUTPUT_DIR, 'swertres_results_2024_2026.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

DRAW_TIMES = ['10:30 AM', '2:00 PM', '5:00 PM', '9:00 PM']

def clean_date_str(raw_date):
    """Normalize raw date strings into standard YYYY-MM-DD format."""
    if not raw_date or not isinstance(raw_date, str):
        return None
    # Remove non-alphanumeric prefix like '*'
    s = re.sub(r'^[^\w]+', '', raw_date).strip()
    s = s.replace('.', '').strip()
    if not s:
        return None

    # Fast-path and validate ISO format YYYY-MM-DD (with optional timestamp)
    iso_match = re.match(r'^(\d{4}-\d{2}-\d{2})(?:[T\s]\d{2}:\d{2}(?::\d{2})?)?', s)
    if iso_match:
        candidate_date = iso_match.group(1)
        try:
            dt = datetime.strptime(candidate_date, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            return None
    
    # Standardize month abbreviations
    s = re.sub(r'\bSept\b', 'Sep', s, flags=re.IGNORECASE)
    s = re.sub(r'\bJuly\b', 'Jul', s, flags=re.IGNORECASE)
    s = re.sub(r'\bJune\b', 'Jun', s, flags=re.IGNORECASE)
    s = re.sub(r'\bMarch\b', 'Mar', s, flags=re.IGNORECASE)
    s = re.sub(r'\bApril\b', 'Apr', s, flags=re.IGNORECASE)
    
    formats = [
        '%Y-%m-%d',
        '%b %d, %Y', '%B %d, %Y',
        '%b %d %Y', '%B %d %Y',
        '%m/%d/%Y', '%Y/%m/%d'
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None

def parse_combination(val):
    """
    Parse a winning combination string into 3 digits or return N/A if non-digit.
    Preserves leading zeros (e.g., '019' -> ('019', 0, 1, 9)).
    """
    if not val:
        return 'N/A', None, None, None
    
    # Strip spaces and non-digit characters
    digits_only = re.sub(r'[^\d]', '', str(val))
    if len(digits_only) == 3:
        d1 = int(digits_only[0])
        d2 = int(digits_only[1])
        d3 = int(digits_only[2])
        return digits_only, d1, d2, d3
    
    return 'N/A', None, None, None

def fetch_year_data(year):
    """Fetch and parse draw results for a specific year from pinoyswertres.net."""
    url = f'https://pinoyswertres.net/swertres-result-history-{year}/'
    logging.info(f'Fetching data from {url}...')
    data = {}
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            logging.error(f'Failed to fetch {url}, status: {res.status_code}')
            return data
        
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table:
            logging.warning(f'No table found on {url}')
            return data
        
        rows = table.find_all('tr')
        logging.info(f'Found {len(rows)} table rows for year {year}')
        
        for row in rows[1:]:
            cols = [td.text.strip() for td in row.find_all(['th', 'td'])]
            if len(cols) >= 4:
                date_str = clean_date_str(cols[0])
                if date_str:
                    data[date_str] = {
                        '2:00 PM': cols[1],
                        '5:00 PM': cols[2],
                        '9:00 PM': cols[3]
                    }
    except Exception as e:
        logging.error(f'Error fetching year {year}: {e}')
    
    return data

def fetch_lottopcso_supplement():
    """Fetch recent results from lottopcso.com as a secondary supplement."""
    url = 'https://www.lottopcso.com/swertres-results-today-history-and-summary/'
    logging.info(f'Fetching supplementary data from {url}...')
    data = {}
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            tables = soup.find_all('table')
            if tables:
                rows = tables[0].find_all('tr')
                for row in rows[1:]:
                    cols = [td.text.strip() for td in row.find_all(['th', 'td'])]
                    if len(cols) >= 4:
                        date_str = clean_date_str(cols[0])
                        if date_str:
                            data[date_str] = {
                                '2:00 PM': cols[1],
                                '5:00 PM': cols[2],
                                '9:00 PM': cols[3]
                            }
    except Exception as e:
        logging.warning(f'Could not fetch supplementary data: {e}')
    return data

def main():
    logging.info('Starting PCSO 3D Lotto (Swertres) Data Scraper...')
    
    # Gather data across target years
    all_web_data = {}
    for year in [2024, 2025, 2026]:
        year_data = fetch_year_data(year)
        all_web_data.update(year_data)
    
    # Supplement with lottopcso if missing any recent dates
    supp_data = fetch_lottopcso_supplement()
    for d, draws in supp_data.items():
        if d not in all_web_data:
            all_web_data[d] = draws
        else:
            # Fill in any missing draw time
            for t in ['2:00 PM', '5:00 PM', '9:00 PM']:
                if all_web_data[d].get(t) in ['*', 'N/D', '', 'N/A', None] and draws.get(t) not in ['*', 'N/D', '', 'N/A', None]:
                    all_web_data[d][t] = draws[t]
                    
    # Known typo correction: 2024-11-04 9:00 PM official result is 1-6-5
    if '2024-11-04' in all_web_data:
        if all_web_data['2024-11-04'].get('9:00 PM') == '28-30':
            all_web_data['2024-11-04']['9:00 PM'] = '1-6-5'

    start_dt = datetime.strptime(START_DATE_STR, '%Y-%m-%d')
    end_dt = datetime.strptime(END_DATE_STR, '%Y-%m-%d')

    dataset = []
    current_dt = start_dt

    valid_combo_count = 0
    na_combo_count = 0

    while current_dt <= end_dt:
        date_iso = current_dt.strftime('%Y-%m-%d')
        day_draws = all_web_data.get(date_iso, {})

        for draw_time in DRAW_TIMES:
            raw_val = day_draws.get(draw_time, 'N/A')
            combo, d1, d2, d3 = parse_combination(raw_val)
            
            if combo != 'N/A':
                valid_combo_count += 1
            else:
                na_combo_count += 1
                
            record = {
                'Date': date_iso,
                'Draw_Time': draw_time,
                'Winning_Combination': combo,
                'Digit_1': d1,
                'Digit_2': d2,
                'Digit_3': d3
            }
            dataset.append(record)

        current_dt += timedelta(days=1)

    logging.info(f'Total records generated: {len(dataset)}')
    logging.info(f'Valid combinations: {valid_combo_count}, N/A combinations: {na_combo_count}')

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Export to CSV
    fieldnames = ['Date', 'Draw_Time', 'Winning_Combination', 'Digit_1', 'Digit_2', 'Digit_3']
    with open(CSV_FILEPATH, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in dataset:
            # Format None values as empty strings in CSV
            formatted_row = {
                'Date': row['Date'],
                'Draw_Time': row['Draw_Time'],
                'Winning_Combination': row['Winning_Combination'],
                'Digit_1': '' if row['Digit_1'] is None else row['Digit_1'],
                'Digit_2': '' if row['Digit_2'] is None else row['Digit_2'],
                'Digit_3': '' if row['Digit_3'] is None else row['Digit_3']
            }
            writer.writerow(formatted_row)
    logging.info(f'Successfully exported CSV to {CSV_FILEPATH}')

    # Export to JSON
    with open(JSON_FILEPATH, 'w', encoding='utf-8') as json_file:
        json.dump(dataset, json_file, indent=2)
    logging.info(f'Successfully exported JSON to {JSON_FILEPATH}')

if __name__ == '__main__':
    main()
