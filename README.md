# Daily Financial Report

Un programma Python che scarica dati di mercato in tempo reale da Yahoo Finance,
calcola indicatori tecnici e genera segnali di investimento nel terminale.

## Cosa fa

- Scarica i prezzi aggiornati di S&P 500, NASDAQ, Dow Jones, VIX e mercati emergenti
- Calcola SMA20 (media mobile 20 giorni) e RSI (indice di forza relativa)
- Genera segnali **BUY / SELL / HOLD** basati su regole trasparenti
- Stampa il report nel terminale con colori

## Struttura del progetto

```
financial-report/
├── main.py          # punto di ingresso — esegui questo
├── fetcher.py       # scarica dati da Yahoo Finance e calcola SMA20/RSI
├── signals.py       # logica BUY/SELL/HOLD
└── requirements.txt # dipendenze
```

## Come eseguirlo

```bash
# 1. Crea l'ambiente virtuale e installa le dipendenze
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Avvia il programma
python main.py
```

## Logica dei segnali

| Segnale | Condizione |
|---------|-----------|
| **BUY** | Prezzo ≥ 3% sotto SMA20 **e** RSI < 40 |
| **SELL** | Prezzo ≥ 4% sopra SMA20 **e** RSI > 70 — oppure VIX > 30 |
| **HOLD** | Tutto il resto |

## Tecnologie usate

- [yfinance](https://github.com/ranaroussi/yfinance) — dati di mercato
- [pandas](https://pandas.pydata.org/) — calcolo indicatori tecnici
