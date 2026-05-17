import sqlite3
from datetime import date

DB_NAME="jobs.db"

def get_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.row_factory=sqlite3.Row #access columns by name
    return conn

def create_tables():
    conn=get_connection()  
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs(
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT,
                 company TEXT,
                 url TEXT UNIQUE,
                 source TEXT,
                 date_found TEXT,
                 score REAL
                 )""")
    conn.commit()
    conn.close()

def job_exists(url):
    conn=get_connection()
    row=conn.execute("SELECT 1 FROM jobs WHERE url=?", (url,)).fetchone()  
    conn.close()
    return row is not None

def save_job(job_dict):
    conn = get_connection()

    today = str(date.today())
    
    conn.execute(
        "INSERT OR IGNORE INTO jobs (title, company, url, source, date_found, score) VALUES (?, ?, ?, ?, ?, ?)",
        (
            job_dict["title"],
            job_dict["company"],
            job_dict["url"],
            job_dict["source"],
            today,
            0,       
        )
    )

    conn.commit() 
    conn.close()
