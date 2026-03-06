import sqlite3

def create_table():

    conn = sqlite3.connect("watchlist.db")

    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS watchlist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_stock(symbol):

    conn = sqlite3.connect("watchlist.db")

    c = conn.cursor()

    c.execute("SELECT * FROM watchlist WHERE symbol=?", (symbol,))
    exists = c.fetchone()

    if not exists:
        c.execute("INSERT INTO watchlist(symbol) VALUES (?)",(symbol,))

    conn.commit()
    conn.close()

def get_watchlist():

    conn = sqlite3.connect("watchlist.db")

    c = conn.cursor()

    c.execute("SELECT symbol FROM watchlist")

    rows = c.fetchall()

    conn.close()

    return rows

def remove_stock(symbol):

    conn = sqlite3.connect("watchlist.db")

    cursor = conn.cursor()

    cursor.execute("DELETE FROM watchlist WHERE symbol=?", (symbol,))

    conn.commit()

    conn.close()