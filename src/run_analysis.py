
from pathlib import Path
import sqlite3


PROJECT_DIR = Path(__file__).resolve().parents[1]
DB_FILE = PROJECT_DIR / "data" / "analytics.db"
SQL_FILE = PROJECT_DIR / "sql" / "analysis.sql"


def main():
    sql_text = SQL_FILE.read_text(encoding="utf-8")

    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]

    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.cursor()

        for number, statement in enumerate(statements, start=1):
            # SQL-Kommentare entfernen
            query_lines = [
                line for line in statement.splitlines()
                if not line.strip().startswith("--")
            ]

            query = "\n".join(query_lines).strip()

            if not query:
                continue

            print(f"\n{'=' * 60}")
            print(f"ANALYSE {number}")
            print("=" * 60)

            cursor.execute(query)

            # Spaltennamen aus dem SQL-Ergebnis lesen
            columns = [description[0] for description in cursor.description]

            rows = cursor.fetchall()

            print(" | ".join(columns))
            print("-" * 60)

            for row in rows:
                print(" | ".join(str(value) for value in row))


if __name__ == "__main__":
    main()
