import csv
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "hot-100-80s.csv"
DB_PATH = BASE_DIR / "hot100-80s.db"


def nullable_int(value):
    value = (value or "").strip()
    if value.upper() == "NA":
        return None
    return int(value) if value else None


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Could not find {CSV_PATH.name}")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DROP TABLE IF EXISTS hot100")
        conn.execute(
            """
            CREATE TABLE hot100 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chart_week TEXT NOT NULL,
                year INTEGER NOT NULL,
                current_week INTEGER NOT NULL,
                title TEXT NOT NULL,
                performer TEXT NOT NULL,
                last_week INTEGER,
                peak_pos INTEGER,
                wks_on_chart INTEGER
            )
            """
        )

        with CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            rows = [
                (
                    row["chart_week"],
                    int(row["chart_week"][:4]),
                    int(row["current_week"]),
                    row["title"].strip(),
                    row["performer"].strip(),
                    nullable_int(row["last_week"]),
                    nullable_int(row["peak_pos"]),
                    nullable_int(row["wks_on_chart"]),
                )
                for row in reader
            ]

        conn.executemany(
            """
            INSERT INTO hot100 (
                chart_week,
                year,
                current_week,
                title,
                performer,
                last_week,
                peak_pos,
                wks_on_chart
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.execute("CREATE INDEX idx_hot100_year ON hot100 (year)")
        conn.execute(
            "CREATE INDEX idx_hot100_song ON hot100 (title, performer, chart_week)"
        )
        conn.execute("CREATE INDEX idx_hot100_week ON hot100 (chart_week)")

    print(f"Loaded {len(rows):,} chart rows into {DB_PATH.name}")


if __name__ == "__main__":
    main()
