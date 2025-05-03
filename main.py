
# --------------------------------------------

import re
import os
import sqlite3
import configparser
from datetime import datetime
from pymongo import MongoClient
from dateutil import parser as date_parser

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read(r'Server-Log-Data-Extraction-and-User-History-Database-Update\config.ini')
cfg = config['DEFAULT']

# Constants from config file
MBOX_FILE = cfg['MBOX_FILE']
MONGO_URI = cfg['MONGO_URI']
MONGO_DB = cfg['MONGO_DB']
MONGO_COLLECTION = cfg['MONGO_COLLECTION']
SQLITE_DB = cfg['SQLITE_DB']

def extract_emails_dates(file_path):
   
    email_date_pairs = []
    date_pattern = re.compile(r'^Date: (.*)$', re.IGNORECASE)
    email_pattern = re.compile(r'\b[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,6}\b')

    with open(file_path, 'r') as f:
        current_date = None
        for line in f:
            if date_match := date_pattern.match(line):
                raw_date = date_match.group(1).strip()
                try:
                    current_date = date_parser.parse(raw_date)
                except (ValueError, OverflowError):
                    current_date = None
                continue

            for email in email_pattern.findall(line):
                if current_date:
                    email_date_pairs.append((email, current_date))
    return email_date_pairs


def transform_records(pairs):
    
    return [
        {'email': email, 'date': dt.strftime('%Y-%m-%d %H:%M:%S')}
        for email, dt in pairs
    ]


def save_to_mongodb(records):
    
    client = MongoClient(MONGO_URI)
    collection = client[MONGO_DB][MONGO_COLLECTION]
    collection.delete_many({})
    collection.insert_many(records)
    client.close()

def check_mongodb_connection(uri: str, timeout_ms: int = 5000) -> bool:
   
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
        client.admin.command('ping')
        client.close()
        print('MongoDB connection successful.')
        return True
    except Exception:
        print('MongoDB connection Failed.')
        return False

def fetch_from_mongodb():
    
    client = MongoClient(MONGO_URI)
    collection = client[MONGO_DB][MONGO_COLLECTION]
    docs = list(collection.find({}))
    client.close()
    return docs


def save_to_sqlite(records, db_path):
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            date TEXT NOT NULL
        );
    ''') 
    conn.commit()
    cur.execute('DELETE FROM user_history;')
    insert_query = 'INSERT INTO user_history (email, date) VALUES (?, ?);'
    cur.executemany(insert_query, [(r['email'], r['date']) for r in records])
    conn.commit()
    conn.close()

def run_sql_query(db_path: str, query: str):
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute(query).fetchall()
    conn.close()
    return rows


def main(): 

    pairs = extract_emails_dates(MBOX_FILE)
    if pairs:
        print(f"Extracted {len(pairs)} email-date pairs.")


    records = transform_records(pairs)
    if records:
        print(f"Transformed {len(records)} email-date pairs.")


    if not check_mongodb_connection(MONGO_URI):
        exit() 

    if save_to_mongodb(records):
        print("Saved records to MongoDB.")

    docs = fetch_from_mongodb()
    if docs:
        print("Fetched data from Mongodb")

    save_to_sqlite(docs, SQLITE_DB)
    print(f"Inserted into SQLite DB at {SQLITE_DB}.")

   
    queries = [
        ("Unique Emails", "SELECT DISTINCT email FROM user_history;"),
        ("Emails Per Day", "SELECT date(date) AS day, COUNT(*) FROM user_history GROUP BY day ORDER BY day;"),
        ("First and Last Dates per Email", "SELECT email, MIN(date), MAX(date) FROM user_history GROUP BY email;"),
        ("Count by Domain", "SELECT SUBSTR(email, INSTR(email, '@')+1) AS domain, COUNT(*) FROM user_history GROUP BY domain ORDER BY COUNT(*) DESC;")
    ]

    print("\nRunning all the queries...\n")
    while True:
        print("Select a query to run:")
        for idx, (label, _) in enumerate(queries, start=1):
            print(f"  {idx}. {label}")
        print(f"  {len(queries) + 1}. Exit")
        choice = input("Enter choice number: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(queries) + 1):
            print("Invalid choice, try again.")
            continue
        choice = int(choice)
        if choice == len(queries) + 1:
            break
        label, sql = queries[choice - 1]
        print(f"-- {label} --")
        rows = run_sql_query(SQLITE_DB, sql)
        for row in rows:
            print(' | '.join(str(item) for item in row))
        

    print("Finished")
if __name__ == '__main__':
    main()



