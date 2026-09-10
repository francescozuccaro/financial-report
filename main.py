from datetime import datetime

from fetcher import MERCATI, get_dati_mercato
from signals import genera_segnali


VERDE = "\033[92m"
ROSSO = "\033[91m"
GIALLO = "\033[93m"
GRIGIO = "\033[90m"
GRASSETTO = "\033[1m"
RESET = "\033[0m"

COLORI_SEGNALI = {
    "BUY": VERDE,
    "SELL": ROSSO,
    "HOLD": GIALLO,
}


def scegli_mercati() -> list[str]:

    print(f"\n{GRASSETTO}DAILY FINANCIAL REPORT{RESET}")
    print("\nQuali mercati vuoi analizzare?\n")

    for numero, mercato in MERCATI.items():
        print(f"  {numero}. {mercato['nome']}")

    print(f"  {len(MERCATI) + 1}. Tutti")

    while True:
        scelta = input("\nInserisci uno o più numeri separati da una virgola: ")
        numeri = [numero.strip() for numero in scelta.split(",")]

        opzione_tutti = str(len(MERCATI) + 1)

        if opzione_tutti in numeri:
            return [mercato["simbolo"] for mercato in MERCATI.values()]

        if numeri and all(numero in MERCATI for numero in numeri):
            simboli = [MERCATI[numero]["simbolo"] for numero in numeri]

            # dict.fromkeys elimina eventuali duplicati mantenendo l'ordine.
            return list(dict.fromkeys(simboli))

        print("Scelta non valida. Riprova usando i numeri mostrati nel menu.")


def descrivi_vix(vix: float) -> str:

    if vix >= 30:
        return "volatilità elevata"
    if vix >= 20:
        return "volatilità moderata"
    return "volatilità contenuta"


def stampa_report(dati: dict, segnali: list[dict]) -> None:
    """Stampa prezzi, indicatori e segnali nel terminale."""

    ora_attuale = datetime.now().strftime("%d/%m/%Y %H:%M")
    vix = dati.get("vix")

    print(f"\n{GRASSETTO}{'=' * 58}{RESET}")
    print(f"{GRASSETTO}DAILY FINANCIAL REPORT - {ora_attuale}{RESET}")

    if vix is not None:
        descrizione = descrivi_vix(vix)
        print(f"VIX: {vix:.1f} ({descrizione})")

        if vix >= 30:
            print(
                f"{GIALLO}Attenzione: il mercato presenta "
                f"una volatilità elevata.{RESET}"
            )

    print(f"{GRASSETTO}{'=' * 58}{RESET}")

    print(f"\n{GRASSETTO}PREZZI DI MERCATO{RESET}")
    print("-" * 58)

    prezzi = dati.get("prezzi", {})

    for quotazione in prezzi.values():
        nome = quotazione["nome"]
        prezzo = quotazione.get("prezzo")
        variazione_pct = quotazione.get("variazione_pct")

        if prezzo is None:
            continue

        if variazione_pct is None:
            variazione_testo = f"{GRIGIO}N/D{RESET}"
        elif variazione_pct > 0:
            variazione_testo = (
                f"{VERDE}+{variazione_pct:.2f}%{RESET}"
            )
        elif variazione_pct < 0:
            variazione_testo = (
                f"{ROSSO}{variazione_pct:.2f}%{RESET}"
            )
        else:
            variazione_testo = f"{GRIGIO}0.00%{RESET}"

        print(f"{nome:<22} {prezzo:>12,.2f}   {variazione_testo}")

    print(f"\n{GRASSETTO}ANALISI TECNICA{RESET}")
    print("-" * 58)

    for segnale in segnali:
        azione = segnale["azione"]
        colore = COLORI_SEGNALI.get(azione, RESET)

        print(
            f"{colore}{GRASSETTO}[{azione}]{RESET} "
            f"{GRASSETTO}{segnale['nome']}{RESET}"
        )
        print(f"  {segnale['motivo']}")

        rsi = segnale.get("rsi")
        distanza_sma = segnale.get("pct_vs_sma20")

        if rsi is not None and distanza_sma is not None:
            print(
                f"  {GRIGIO}RSI: {rsi:.1f} | "
                f"distanza dalla SMA20: {distanza_sma:+.2f}%{RESET}"
            )

        print()

    print("-" * 58)
    print(
        f"{GRIGIO}Dati forniti da Yahoo Finance. "
        f"Il report ha esclusivamente finalità didattiche.{RESET}\n"
    )


def main() -> None:
    """Coordina le operazioni principali del programma."""

    simboli_scelti = scegli_mercati()
    dati = get_dati_mercato(simboli_scelti)
    segnali = genera_segnali(dati)

    stampa_report(dati, segnali)


if __name__ == "__main__":
    main()