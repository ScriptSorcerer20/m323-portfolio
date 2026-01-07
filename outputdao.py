import sqlite3
from output import Output

class OutputDAO:
    def __init__(self, db_path="database.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS outputs (id INTEGER PRIMARY KEY AUTOINCREMENT, amount INTEGER, category TEXT, date DATE, description TEXT)''')
        self.conn.commit()

    def get_all(self):
        self.cursor.execute("SELECT id, amount, category, date, description FROM outputs")
        rows = self.cursor.fetchall()

        self.conn.close()

        return list(
            map(lambda r: Output(*r), rows)
        )

    def add(self, output):
        self.cursor.execute(
            "INSERT INTO outputs (amount, category, date, description) VALUES (?, ?, ?, ?)",
            (output.amount, output.category, output.date, output.description)
        )

        self.conn.commit()
        self.conn.close()
