import sqlite3
import datetime

DB_NAME = "spam_filter.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table for logs
    c.execute('''CREATE TABLE IF NOT EXISTS scan_history 
                 (id INTEGER PRIMARY KEY, message TEXT, result TEXT, 
                  detected_keywords TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def log_scan(message, result, keywords):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO scan_history (message, result, detected_keywords, timestamp) VALUES (?, ?, ?, ?)",
              (message, result, ",".join(keywords), datetime.datetime.now()))
    conn.commit()
    conn.close()

def get_recent_scans():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT message, result, detected_keywords, timestamp FROM scan_history ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows