"""
fetcher.py — Scarica i dati di mercato da Yahoo Finance.

Questo modulo ha due compiti:
  1. get_prezzo(simbolo)    → prezzo attuale e variazione giornaliera
  2. get_indicatori(simbolo) → SMA20 e RSI, usati per generare i segnali
  3. get_dati_mercato()     → chiama le due funzioni per tutti i titoli
                              e restituisce un unico dizionario con tutto
"""

import logging
# pyrefly: ignore [missing-import]
import yfinance as yf

# Il logger scrive messaggi di avviso nel terminale (es. se un titolo non risponde)
log = logging.getLogger(__name__)

# ── Titoli che vogliamo monitorare ─────────────────────────────────────────────
# Il formato è: "Nome leggibile" → "simbolo Yahoo Finance"
TITOLI = {
    "S&P 500":    "^GSPC",
    "NASDAQ":     "^IXIC",
    "Dow Jones":  "^DJI",
    "VIX":        "^VIX",   # indice di paura del mercato (volatility index)
    "EEM":        "EEM",    # ETF sui mercati emergenti
}


def get_prezzo(simbolo: str) -> dict | None:
    """
    Scarica il prezzo attuale e la variazione rispetto alla chiusura di ieri.

    Restituisce un dizionario con:
      - prezzo:         prezzo attuale
      - variazione:     differenza in punti/dollari rispetto a ieri
      - variazione_pct: differenza in percentuale

    Restituisce None se qualcosa va storto (es. nessuna connessione).
    """
    try:
        ticker = yf.Ticker(simbolo)
        info = ticker.fast_info   # "fast_info" è più veloce di "info" completo

        prezzo         = float(info.last_price)
        chiusura_prec  = float(info.previous_close)
        variazione     = prezzo - chiusura_prec
        variazione_pct = (variazione / chiusura_prec) * 100

        return {
            "simbolo":       simbolo,
            "prezzo":        round(prezzo, 2),
            "variazione":    round(variazione, 2),
            "variazione_pct": round(variazione_pct, 2),
        }
    except Exception as e:
        log.warning("Impossibile scaricare prezzo per %s: %s", simbolo, e)
        return None


def get_indicatori(simbolo: str) -> dict:
    """
    Calcola due indicatori tecnici partendo dagli ultimi 3 mesi di dati storici:

    SMA20 (Simple Moving Average a 20 giorni):
      Media dei prezzi di chiusura degli ultimi 20 giorni.
      Se il prezzo attuale è molto sotto la SMA20, il mercato potrebbe
      essere ipervenduto → potenziale segnale di acquisto.

    RSI (Relative Strength Index, 14 periodi):
      Misura la velocità e la forza del movimento dei prezzi, da 0 a 100.
      Sotto 40 = ipervenduto (mercato caduto molto, potrebbe rimbalzare).
      Sopra 70 = ipercomprato (mercato salito molto, potrebbe correggere).

    Restituisce un dizionario con i valori calcolati, oppure {"errore": True}
    se i dati sono insufficienti.
    """
    try:
        # Scarica la serie storica degli ultimi 3 mesi (OHLCV = Open/High/Low/Close/Volume)
        df = yf.download(simbolo, period="3mo", auto_adjust=True, progress=False)

        if df.empty or len(df) < 20:
            log.warning("Dati insufficienti per gli indicatori di %s", simbolo)
            return {"errore": True}

        # yfinance a volte restituisce colonne con doppio livello (es. "Close"/"^GSPC")
        # Questo le appiattisce al solo primo livello
        if hasattr(df.columns, "get_level_values"):
            df.columns = df.columns.get_level_values(0)

        chiusure = df["Close"].dropna().astype(float)

        # ── SMA20 ──────────────────────────────────────────────────────────────
        # .rolling(20).mean() calcola la media degli ultimi 20 valori per ogni giorno
        # .iloc[-1] prende solo l'ultimo valore (quello di oggi)
        sma20  = float(chiusure.rolling(20).mean().iloc[-1])
        prezzo = float(chiusure.iloc[-1])

        # Quanto % il prezzo attuale si discosta dalla SMA20
        pct_vs_sma20 = (prezzo - sma20) / sma20 * 100

        # ── RSI con metodo di Wilder ───────────────────────────────────────────
        # 1. Calcola le differenze giorno per giorno
        delta = chiusure.diff()

        # 2. Separa i giorni positivi (guadagni) dai negativi (perdite)
        guadagni = delta.clip(lower=0)   # mantieni solo i valori > 0
        perdite  = -delta.clip(upper=0)  # mantieni solo i valori < 0, poi cambia segno

        # 3. Calcola la media esponenziale di guadagni e perdite (periodo 14)
        #    ewm(alpha=1/14) è la formula di Wilder, lo standard per l'RSI
        media_guadagni = guadagni.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        media_perdite  = perdite.ewm(alpha=1/14, min_periods=14, adjust=False).mean()

        # 4. RS = rapporto tra forza rialzista e ribassista
        rs = media_guadagni / media_perdite.replace(0, float("nan"))

        # 5. Formula finale dell'RSI
        rsi = float((100 - 100 / (1 + rs)).iloc[-1])

        return {
            "prezzo":        round(prezzo, 2),
            "sma20":         round(sma20, 2),
            "pct_vs_sma20":  round(pct_vs_sma20, 2),
            "rsi":           round(rsi, 1),
            "errore":        False,
        }

    except Exception as e:
        log.warning("Errore nel calcolo indicatori per %s: %s", simbolo, e)
        return {"errore": True}


def get_dati_mercato() -> dict:
    """
    Funzione principale del modulo: scarica prezzi e indicatori per tutti i titoli.

    Restituisce un unico dizionario con questa struttura:
    {
        "prezzi": {
            "^GSPC": {"simbolo": ..., "prezzo": ..., "variazione_pct": ..., "nome": ...},
            ...
        },
        "indicatori": {
            "^GSPC": {"prezzo": ..., "sma20": ..., "pct_vs_sma20": ..., "rsi": ...},
            "EEM":   {...}
        },
        "vix": 18.3   ← valore numerico del VIX, estratto dai prezzi
    }
    """
    print("Connessione a Yahoo Finance...")

    # ── Prezzi per tutti i titoli ──────────────────────────────────────────────
    prezzi = {}
    for nome, simbolo in TITOLI.items():
        print(f"  Scarico {nome} ({simbolo})...", end=" ", flush=True)
        dati = get_prezzo(simbolo)
        if dati:
            prezzi[simbolo] = {**dati, "nome": nome}  # aggiunge "nome" al dizionario
            print("OK")
        else:
            print("ERRORE")

    # ── Indicatori tecnici (solo per i titoli usati nei segnali) ──────────────
    print("\nCalcolo indicatori tecnici (SMA20 e RSI)...")
    TITOLI_SEGNALI = ["^GSPC", "EEM"]  # S&P 500 e mercati emergenti
    indicatori = {}

    for simbolo in TITOLI_SEGNALI:
        # Trova il nome leggibile del simbolo
        nome = next((n for n, s in TITOLI.items() if s == simbolo), simbolo)
        print(f"  {nome}...", end=" ", flush=True)
        indicatori[simbolo] = get_indicatori(simbolo)
        print("OK" if not indicatori[simbolo].get("errore") else "ERRORE")

    # ── VIX ────────────────────────────────────────────────────────────────────
    # Il VIX lo usiamo solo come numero grezzo, non ci calcoliamo indicatori sopra
    vix = prezzi.get("^VIX", {}).get("prezzo")

    return {
        "prezzi":     prezzi,
        "indicatori": indicatori,
        "vix":        vix,
    }
