"""
signals.py — Decide se comprare, vendere o aspettare.

Le regole sono semplici e trasparenti (nessuna "scatola nera"):

  BUY  → prezzo almeno 3% SOTTO la SMA20  E  RSI sotto 40
          Significa: il mercato è sceso molto e potrebbe rimbalzare.

  SELL → prezzo almeno 4% SOPRA la SMA20  E  RSI sopra 70
          Significa: il mercato è salito molto e potrebbe correggere.
       OPPURE VIX sopra 30 (paura estrema → meglio ridurre l'esposizione)

  HOLD → tutto il resto = nessun segnale forte, meglio aspettare.

Perché SMA e RSI insieme?
  Usarli insieme riduce i falsi segnali. Un RSI basso da solo potrebbe
  indicare un trend ribassista, non un'opportunità. Con la SMA confermi
  che siamo effettivamente lontani dalla media storica recente.
"""

# ── Soglie — modificale per cambiare la sensibilità del sistema ───────────────
SOGLIA_BUY_SMA   = -3.0   # il prezzo deve essere almeno il 3% sotto la SMA20
SOGLIA_BUY_RSI   = 40.0   # RSI deve essere sotto 40 (ipervenduto)
SOGLIA_SELL_SMA  = +4.0   # il prezzo deve essere almeno il 4% sopra la SMA20
SOGLIA_SELL_RSI  = 70.0   # RSI deve essere sopra 70 (ipercomprato)
SOGLIA_VIX_PAURA = 30.0   # VIX sopra 30 = paura estrema nel mercato


def calcola_segnale(pct_vs_sma20: float, rsi: float, vix: float | None) -> tuple[str, str]:
    """
    Riceve i valori degli indicatori e restituisce una coppia (azione, motivazione).

    Parametri:
      pct_vs_sma20 : quanto % il prezzo si discosta dalla SMA20 (negativo = sotto)
      rsi          : indice RSI da 0 a 100
      vix          : valore del VIX (può essere None se non disponibile)

    Ritorna:
      ("BUY",  "spiegazione...")
      ("SELL", "spiegazione...")
      ("HOLD", "spiegazione...")
    """
    # Prima cosa: controllo del VIX. Il rischio ha la precedenza sull'opportunità.
    if vix and vix > SOGLIA_VIX_PAURA:
        return (
            "SELL",
            f"VIX a {vix:.1f} — paura estrema nel mercato. Considera di ridurre l'esposizione."
        )

    # Mercato ipercomprato → possibile correzione in arrivo
    if pct_vs_sma20 >= SOGLIA_SELL_SMA and rsi >= SOGLIA_SELL_RSI:
        return (
            "SELL",
            f"Prezzo {pct_vs_sma20:+.1f}% sopra la media mobile, RSI a {rsi:.0f} — mercato ipercomprato."
        )

    # Mercato ipervenduto → possibile rimbalzo in arrivo
    if pct_vs_sma20 <= SOGLIA_BUY_SMA and rsi <= SOGLIA_BUY_RSI:
        return (
            "BUY",
            f"Prezzo {pct_vs_sma20:+.1f}% sotto la media mobile, RSI a {rsi:.0f} — potenziale opportunità."
        )

    # Nessun segnale forte
    return (
        "HOLD",
        f"Prezzo {pct_vs_sma20:+.1f}% rispetto alla media, RSI a {rsi:.0f} — nessun segnale forte."
    )


def genera_segnali(dati: dict) -> list[dict]:
    """
    Punto di ingresso del modulo: riceve i dati dal fetcher e genera un segnale
    per ogni area di mercato monitorata.

    Restituisce una lista di dizionari, uno per area:
    [
      {
        "nome":         "S&P 500",
        "azione":       "BUY",
        "motivo":       "Prezzo -3.5% sotto la media...",
        "rsi":          38.2,
        "pct_vs_sma20": -3.5,
      },
      ...
    ]
    """
    vix        = dati.get("vix")
    indicatori = dati.get("indicatori", {})

    # Le aree di mercato per cui vogliamo un segnale
    aree = [
        {"nome": "S&P 500",           "simbolo": "^GSPC"},
        {"nome": "Mercati Emergenti",  "simbolo": "EEM"},
    ]

    segnali = []
    for area in aree:
        ind = indicatori.get(area["simbolo"], {})

        # Se i dati non sono disponibili, segnaliamo HOLD con un avviso
        if ind.get("errore"):
            segnali.append({
                "nome":         area["nome"],
                "azione":       "HOLD",
                "motivo":       "Dati insufficienti — impossibile calcolare il segnale.",
                "rsi":          None,
                "pct_vs_sma20": None,
            })
            continue

        azione, motivo = calcola_segnale(
            pct_vs_sma20 = ind["pct_vs_sma20"],
            rsi          = ind["rsi"],
            vix          = vix,
        )

        segnali.append({
            "nome":         area["nome"],
            "azione":       azione,
            "motivo":       motivo,
            "rsi":          ind["rsi"],
            "pct_vs_sma20": ind["pct_vs_sma20"],
        })

    return segnali
