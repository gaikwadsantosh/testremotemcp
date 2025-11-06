from fastmcp import FastMCP
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "FoodCardActions.db")

mcp = FastMCP("FoodCardTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS cardactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                cardnumber TEXT NOT NULL,
                cardaction TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

init_db()

@mcp.tool()
def add_card_action(date, cardnumber, cardaction, note=""):
    '''Add a new food card action to the database.'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO cardactions(date, cardnumber, cardaction, note) VALUES (?,?,?,?)",
            (date, cardnumber, cardaction, note)
        )
        return {"status": "ok", "id": cur.lastrowid}
    
@mcp.tool()
def list_card_actions(start_date, end_date):
    '''List food card entries within an inclusive date range.'''
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            SELECT id, date, cardnumber, cardaction, note
            FROM cardactions
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
            """,
            (start_date, end_date)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001) #http transport on port 8001 by default
