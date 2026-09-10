import logging

import pandas as pd
import yfinance as yf


log = logging.getLogger(__name__)

MERCATI = {
    "1": {"nome": "S&P 500", "simbolo": "^GSPC"},
    "2": {"nome": "NASDAQ", "simbolo": "^IXIC"},
    "3": {"nome": "Dow Jones", "simbolo": "^DJI"},
    "4": {"nome": "Mercati emergenti", "simbolo": "EEM"},
}

SIMBOLO_VIX = "^VIX"


def trova_nome(simbolo: str) -> str:

    for mercato in MERCATI.values():
        if mercato["simbolo"] == simbolo:
            return mercato["nome"]

    return simbolo


def get_quotazione(simbolo: str) -> dict | None:

    try:
        ticker = yf.Ticker(simbolo)
        informazioni = ticker.fast_info

        prezzo = float(informazioni.last_price)
        chiusura_precedente = float(informazioni.previous_close)

        if chiusura_precedente == 0:
            raise ValueError("la chiusura precedente è uguale a zero")

        variazione = prezzo - chiusura_precedente
        variazione_pct = variazione / chiusura_precedente * 100

        return {
            "simbolo": simbolo,
            "nome": trova_nome(simbolo),
            "prezzo": round(prezzo, 2),
            "variazione": round(variazione, 2),
            "variazione_pct": round(variazione_pct, 2),
        }

    except Exception as errore:
        log.warning(
            "Impossibile scaricare la quotazione di %s: %s",
            simbolo,
            errore,
        )
        return None


def calcola_rsi(chiusure: pd.Series, periodo: int = 14) -> float:

    variazioni = chiusure.diff()

    guadagni = variazioni.clip(lower=0)
    perdite = -variazioni.clip(upper=0)

    media_guadagni = guadagni.ewm(
        alpha=1 / periodo,
        min_periods=periodo,
        adjust=False,
    ).mean()

    media_perdite = perdite.ewm(
        alpha=1 / periodo,
        min_periods=periodo,
        adjust=False,
    ).mean()

    ultimo_guadagno = float(media_guadagni.iloc[-1])
    ultima_perdita = float(media_perdite.iloc[-1])

    if ultimo_guadagno == 0 and ultima_perdita == 0:
        return 50.0

    if ultima_perdita == 0:
        return 100.0

    forza_relativa = ultimo_guadagno / ultima_perdita
    return 100 - (100 / (1 + forza_relativa))


def get_indicatori(simbolo: str) -> dict:

    try:
        dati_storici = yf.download(
            simbolo,
            period="3mo",
            auto_adjust=True,
            progress=False,
        )

        if dati_storici.empty:
            raise ValueError("Yahoo Finance non ha restituito dati storici")

        if isinstance(dati_storici.columns, pd.MultiIndex):
            dati_storici.columns = dati_storici.columns.get_level_values(0)

        chiusure = dati_storici["Close"].dropna()

        if isinstance(chiusure, pd.DataFrame):
            chiusure = chiusure.iloc[:, 0]

        chiusure = chiusure.astype(float)

        if len(chiusure) < 20:
            raise ValueError("sono disponibili meno di 20 chiusure")

        prezzo_recente = float(chiusure.iloc[-1])
        sma20 = float(chiusure.tail(20).mean())
        distanza_sma20 = (prezzo_recente - sma20) / sma20 * 100
        rsi = calcola_rsi(chiusure)

        return {
            "nome": trova_nome(simbolo),
            "simbolo": simbolo,
            "prezzo": round(prezzo_recente, 2),
            "sma20": round(sma20, 2),
            "pct_vs_sma20": round(distanza_sma20, 2),
            "rsi": round(rsi, 1),
            "errore": False,
        }

    except Exception as errore:
        log.warning(
            "Impossibile calcolare gli indicatori di %s: %s",
            simbolo,
            errore,
        )

        return {
            "nome": trova_nome(simbolo),
            "simbolo": simbolo,
            "errore": True,
        }


def get_dati_mercato(simboli_scelti: list[str]) -> dict:

    prezzi = {}
    indicatori = {}

    print("\nConnessione a Yahoo Finance...\n")

    for simbolo in simboli_scelti:
        nome = trova_nome(simbolo)

        print(f"Scarico {nome}...", end=" ", flush=True)
        quotazione = get_quotazione(simbolo)

        if quotazione is None:
            print("ERRORE")
        else:
            prezzi[simbolo] = quotazione
            print("OK")

        print(f"Calcolo gli indicatori di {nome}...", end=" ", flush=True)
        indicatori[simbolo] = get_indicatori(simbolo)

        if indicatori[simbolo]["errore"]:
            print("ERRORE")
        else:
            print("OK")

    print("Scarico il VIX...", end=" ", flush=True)
    quotazione_vix = get_quotazione(SIMBOLO_VIX)

    if quotazione_vix is None:
        vix = None
        print("ERRORE")
    else:
        vix = quotazione_vix["prezzo"]
        print("OK")

    return {
        "prezzi": prezzi,
        "indicatori": indicatori,
        "vix": vix,
    }