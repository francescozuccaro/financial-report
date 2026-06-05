"""
main.py — Punto di ingresso del programma.

Esegui con:   python main.py

Flusso completo:
  1. fetcher.get_dati_mercato()  → scarica prezzi e indicatori da Yahoo Finance
  2. signals.genera_segnali()    → calcola BUY / SELL / HOLD per ogni area
  3. stampa_report()             → mostra tutto in modo leggibile nel terminale
"""

import logging
from datetime import datetime

from fetcher import get_dati_mercato
from signals import genera_segnali

# Livello INFO: mostra solo messaggi importanti, non il debug interno
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


# ── Colori ANSI ────────────────────────────────────────────────────────────────
# I terminali moderni supportano i codici ANSI per colorare il testo.
# Formato: "\033[CODICEm" per attivare, "\033[0m" per resettare.
VERDE    = "\033[92m"
ROSSO    = "\033[91m"
GIALLO   = "\033[93m"
GRIGIO   = "\033[90m"
GRASSETTO = "\033[1m"
RESET    = "\033[0m"

# Colore associato a ogni azione
COLORE_AZIONE = {
    "BUY":  VERDE,
    "SELL": ROSSO,
    "HOLD": GIALLO,
}


def stampa_report(dati: dict, segnali: list[dict]) -> None:
    """
    Stampa il report completo nel terminale.

    Sezioni:
      1. Intestazione con data e ora
      2. Tabella dei prezzi di mercato
      3. Segnali di investimento con motivazione
      4. Disclaimer
    """
    ora_attuale = datetime.now().strftime("%d/%m/%Y  %H:%M")
    vix = dati.get("vix")

    # ── 1. Intestazione ────────────────────────────────────────────────────────
    print()
    print(f"{GRASSETTO}{'═' * 52}{RESET}")
    print(f"{GRASSETTO}  DAILY FINANCIAL REPORT  —  {ora_attuale}{RESET}")
    if vix:
        # VIX basso = mercato tranquillo, VIX alto = mercato in paura
        livello_vix = "ELEVATO ⚠" if vix > 25 else "nella norma"
        print(f"  VIX: {GRASSETTO}{vix:.1f}{RESET}  ({livello_vix})")
    print(f"{GRASSETTO}{'═' * 52}{RESET}")

    # ── 2. Tabella prezzi ──────────────────────────────────────────────────────
    print(f"\n{GRASSETTO}MERCATI{RESET}")
    print(f"{'─' * 48}")

    prezzi = dati.get("prezzi", {})
    for simbolo, q in prezzi.items():
        nome  = q.get("nome", simbolo)
        prz   = q.get("prezzo")
        pct   = q.get("variazione_pct")

        if prz is None:
            continue

        # Colora il valore positivo in verde, negativo in rosso
        if pct is not None and pct > 0:
            colore_pct = VERDE
            segno = "+"
        elif pct is not None and pct < 0:
            colore_pct = ROSSO
            segno = ""
        else:
            colore_pct = GRIGIO
            segno = ""

        pct_str = f"{colore_pct}{segno}{pct:.2f}%{RESET}" if pct is not None else f"{GRIGIO}N/D{RESET}"

        # Formattazione colonne: nome (18 char), prezzo (12 char), variazione%
        print(f"  {nome:<18} {prz:>10,.2f}   {pct_str}")

    # ── 3. Segnali ─────────────────────────────────────────────────────────────
    print(f"\n{GRASSETTO}SEGNALI DI INVESTIMENTO{RESET}")
    print(f"{'─' * 48}")

    for sig in segnali:
        azione  = sig["azione"]
        colore  = COLORE_AZIONE.get(azione, RESET)
        badge   = f"{colore}{GRASSETTO}[ {azione:<4} ]{RESET}"  # es. "[ BUY  ]"

        print(f"  {badge}  {GRASSETTO}{sig['nome']}{RESET}")
        print(f"           {sig['motivo']}")

        # Mostra i valori numerici degli indicatori se disponibili
        rsi = sig.get("rsi")
        pct = sig.get("pct_vs_sma20")
        if rsi is not None and pct is not None:
            print(f"           {GRIGIO}RSI: {rsi:.0f}   vs SMA20: {pct:+.1f}%{RESET}")
        print()

    # ── 4. Disclaimer ──────────────────────────────────────────────────────────
    print(f"{'─' * 48}")
    print(f"{GRIGIO}Dati: Yahoo Finance. Non costituisce consulenza finanziaria.{RESET}")
    print(f"{'═' * 52}\n")


def main() -> None:
    """Esegue il flusso completo: scarica → calcola → stampa."""
    # Passo 1: scarica tutti i dati da Yahoo Finance
    dati = get_dati_mercato()

    # Passo 2: calcola i segnali BUY/SELL/HOLD
    segnali = genera_segnali(dati)

    # Passo 3: stampa il report
    stampa_report(dati, segnali)


# Questo blocco garantisce che main() venga chiamata solo se esegui
# direttamente "python main.py", e non se importi questo modulo da un altro file.
if __name__ == "__main__":
    main()
