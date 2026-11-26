from pathlib import Path
import sqlite3

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_DIR / "data" / "processed" / "claims_clean.csv"
DB_FILE = PROJECT_DIR / "data" / "analytics.db"


def main():
    # Bereinigte CSV laden
    df = pd.read_csv(INPUT_FILE)

    # Datenbankverzeichnis sicherstellen
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Verbindung zur SQLite-Datenbank herstellen
    with sqlite3.connect(DB_FILE) as connection:
        # Tabelle aus dem DataFrame erstellen
        df.to_sql(
            "claims",
            connection,
            if_exists="replace",
            index=False
        )

        # Index für häufig verwendete Abfragen
        connection.execute(
            "CREATE INDEX idx_claims_age ON claims(claim_age_days)"
        )
        connection.execute(
            "CREATE INDEX idx_claims_segment ON claims(customer_segment)"
        )

        # Kontrolle: Anzahl der gespeicherten Datensätze
        result = connection.execute(
            "SELECT COUNT(*) FROM claims"
        ).fetchone()

    print("SQLite-Datenbank erfolgreich erstellt!")
    print(f"Speicherort: {DB_FILE}")
    print(f"Gespeicherte Fälle: {result[0]:,}")


if __name__ == "__main__":
    main()
