
from pathlib import Path

import numpy as np
import pandas as pd


# Reproduzierbare Zufallsdaten
rng = np.random.default_rng(42)

N = 10_000
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "claims_raw.csv"

# Kategorien für die synthetischen Fälle
segments = ["Privatkunde", "Kleingewerbe", "Mittelstand"]
channels = ["Brief", "E-Mail", "Telefon"]

# Grunddaten
df = pd.DataFrame({
    "case_id": np.arange(1, N + 1),
    "customer_id": rng.integers(1, 7501, size=N),
    "claim_amount": np.round(
        rng.lognormal(mean=5.1, sigma=0.8, size=N), 2
    ),
    "claim_age_days": rng.integers(1, 361, size=N),
    "customer_segment": rng.choice(
        segments, size=N, p=[0.70, 0.20, 0.10]
    ),
    "contact_attempts": rng.poisson(lam=2.5, size=N),
    "contact_channel": rng.choice(
        channels, size=N, p=[0.45, 0.35, 0.20]
    ),
    "previous_payments": rng.poisson(lam=0.7, size=N),
})

# Künstlich definierte Zusammenhänge für die Simulation:
# Diese Regeln sind Annahmen und keine empirischen Erkenntnisse.
score = (
    1.1
    - df["claim_age_days"] / 180
    - np.log1p(df["claim_amount"]) / 5
    + df["previous_payments"] * 0.45
    + np.where(df["customer_segment"] == "Mittelstand", 0.25, 0)
    - np.where(df["customer_segment"] == "Privatkunde", 0.10, 0)
)

# Wahrscheinlichkeit einer vollständigen Zahlung innerhalb
# des simulierten Beobachtungszeitraums
payment_probability = 1 / (1 + np.exp(-score))
settled = rng.binomial(1, payment_probability)

# Rückgewonnener Betrag:
# Bei vollständiger Zahlung 100 %, sonst gegebenenfalls Teilzahlung
partial_payment_share = rng.beta(a=1.5, b=5, size=N)
recovery_share = np.where(settled == 1, 1.0, partial_payment_share)

# Einige Fälle ohne Zahlung erhalten tatsächlich 0 Euro
no_payment = (settled == 0) & (rng.random(N) < 0.35)
recovery_share = np.where(no_payment, 0.0, recovery_share)

df["settled"] = settled
df["recovered_amount"] = np.round(
    df["claim_amount"] * recovery_share, 2
)

# Zeit bis zur ersten Zahlung; bei Fällen ohne Zahlung leer
payment_days = rng.integers(1, 91, size=N)
df["days_to_first_payment"] = np.where(
    df["recovered_amount"] > 0,
    payment_days,
    np.nan
)

# CSV-Datei schreiben
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT, index=False)

print("Datensatz erfolgreich erstellt!")
print(f"Speicherort: {OUTPUT}")
print(f"Anzahl Fälle: {len(df):,}")
print("\nErste fünf Zeilen:")
print(df.head())
print("\nZusammenfassung:")
print(df.describe(include="all"))