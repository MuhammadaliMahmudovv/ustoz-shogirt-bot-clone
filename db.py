import sqlite3

def init_db():
    conn = sqlite3.connect("applications.db")
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        category TEXT,
        name TEXT,
        technology TEXT,
        phone_number TEXT,
        region TEXT,
        cost TEXT,
        work_or_study TEXT,
        time TEXT,
        purpose TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)
    conn.commit()
    conn.close()

def save_application(user_id, username, category, data: dict):
    conn = sqlite3.connect("applications.db")
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO applications (user_id, username, category, name, technology, phone_number,
                              region, cost, work_or_study, time, purpose)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, username, category,
        data.get("name"),
        data.get("technology"),
        data.get("phone_number"),
        data.get("region"),
        data.get("cost"),
        data.get("work_or_study"),
        data.get("time"),
        data.get("purpose")
    ))
    conn.commit()
    conn.close()
