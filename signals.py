SOGLIA_BUY_SMA = -3.0
SOGLIA_BUY_RSI = 40.0

SOGLIA_SELL_SMA = 4.0
SOGLIA_SELL_RSI = 70.0


def calcola_segnale(
    distanza_sma20: float,
    rsi: float,
) -> tuple[str, str]:
    """Restituisce un segnale e la relativa spiegazione."""

    if distanza_sma20 <= SOGLIA_BUY_SMA and rsi < SOGLIA_BUY_RSI:
        return (
            "BUY",
            "Prezzo sotto la media recente e momentum debole.",
        )

    if distanza_sma20 >= SOGLIA_SELL_SMA and rsi > SOGLIA_SELL_RSI:
        return (
            "SELL",
            "Prezzo sopra la media recente e momentum elevato.",
        )

    return (
        "HOLD",
        "Gli indicatori non mostrano un segnale tecnico forte.",
    )


def genera_segnali(dati: dict) -> list[dict]:

    indicatori = dati.get("indicatori", {})
    segnali = []

    for indicatore in indicatori.values():
        nome = indicatore.get("nome", "Mercato non disponibile")
        simbolo = indicatore.get("simbolo", "")

        if indicatore.get("errore"):
            segnali.append(
                {
                    "nome": nome,
                    "simbolo": simbolo,
                    "azione": "HOLD",
                    "motivo": "Dati insufficienti per calcolare gli indicatori.",
                    "rsi": None,
                    "pct_vs_sma20": None,
                }
            )
            continue

        distanza_sma20 = indicatore["pct_vs_sma20"]
        rsi = indicatore["rsi"]

        azione, motivo = calcola_segnale(
            distanza_sma20,
            rsi,
        )

        segnali.append(
            {
                "nome": nome,
                "simbolo": simbolo,
                "azione": azione,
                "motivo": motivo,
                "rsi": rsi,
                "pct_vs_sma20": distanza_sma20,
            }
        )

    return segnali