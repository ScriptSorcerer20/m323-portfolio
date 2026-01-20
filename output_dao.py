import sqlite3
import datetime
from output import Output

class OutputDAO:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def create_table(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS outputs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    category TEXT,
                    date TEXT,
                    description TEXT
                )
                """
            )

    def get_all(self):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, amount, category, date, description FROM outputs ORDER BY date DESC, id DESC"
            ).fetchall()

        # funktional: map -> Output
        return list(map(self._row_to_output, rows))

    def add(self, output: Output):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO outputs (amount, category, date, description) VALUES (?, ?, ?, ?)",
                (output.amount, output.category, output.date.isoformat(), output.description)
            )

    @staticmethod
    def _row_to_output(r: sqlite3.Row) -> Output:
        return Output(
            id=int(r["id"]),
            amount=float(r["amount"]),
            category=str(r["category"]),
            date=datetime.date.fromisoformat(r["date"]),
            description=str(r["description"] or "")
        )
