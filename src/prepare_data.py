
from pathlib import Path

import pandas as pd


# Projektpfade
PROJECT_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_DIR / "data" / "raw" / "claims_raw.csv"
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "claims_clean.csv"


def main():
    # Daten laden
    df = pd.read_csv(INPUT_FILE)

    print("=== AUSGANGSDATEN ===")
    print(f"Zeilen: {len(df)}")
    print(f"Spalten: {len(df.columns)}")

    # 1. Fehlende Werte prüfen
    print("\n=== FEHLENDE WERTE ===")
    print(df.isna().sum())

    # 2. Doppelte Fälle prüfen
    duplicate_cases = df["case_id"].duplicated().sum()
    print(f"\nDoppelte case_id-Werte: {duplicate_cases}")

    # 3. Fachliche Plausibilitätsprüfungen
    checks = {
        "Forderungsbetrag > 0": (df["claim_amount"] > 0).all(),
        "Rückgewonnener Betrag >= 0": (df["recovered_amount"] >= 0).all(),
        "Rückgewonnener Betrag <= Forderung": (
            df["recovered_amount"] <= df["claim_amount"]
        ).all(),
        "Forderungsalter zwischen 1 und 360 Tagen": (
            df["claim_age_days"].between(1, 360).all()
        ),
        "Kontaktversuche >= 0": (df["contact_attempts"] >= 0).all(),
        "Settled enthält nur 0 oder 1": (
            df["settled"].isin([0, 1]).all()
        ),
        "Vollständig bezahlte Fälle haben volle Rückzahlung": (
            df.loc[df["settled"] == 1, "recovered_amount"]
            .eq(df.loc[df["settled"] == 1, "claim_amount"])
            .all()
        ),
        "Keine Zahlung bedeutet kein Zahlungsdatum": (
            df.loc[df["recovered_amount"] == 0,
                   "days_to_first_payment"].isna().all()
        ),
    }

    print("\n=== QUALITÄTSPRÜFUNGEN ===")
    for description, passed in checks.items():
        print(f"{'OK' if passed else 'FEHLER'}: {description}")

    # Bei fehlerhaften Daten nicht unbemerkt weitermachen
    if not all(checks.values()) or duplicate_cases > 0:
        raise ValueError("Datenqualitätsprüfung fehlgeschlagen!")

    # 4. Analysespalten ergänzen
    df["recovery_rate"] = (
        df["recovered_amount"] / df["claim_amount"]
    ).round(4)

    df["claim_age_bucket"] = pd.cut(
        df["claim_age_days"],
        bins=[0, 30, 90, 180, 360],
        labels=["0-30 Tage", "31-90 Tage", "91-180 Tage", "181-360 Tage"]
    )

    # 5. Bereinigte Daten speichern
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n=== ERGEBNIS ===")
    print(f"Bereinigter Datensatz: {OUTPUT_FILE}")
    print(f"Zeilen: {len(df)}")
    print(f"Spalten: {len(df.columns)}")
    print("\nDatenqualität: Alle Prüfungen bestanden.")


if __name__ == "__main__":
    main()