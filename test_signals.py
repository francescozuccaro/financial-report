"""
Test automatici per la generazione dei segnali tecnici.
"""

import unittest

from signals import calcola_segnale, genera_segnali


class TestCalcolaSegnale(unittest.TestCase):

    def test_buy(self):
        azione, motivo = calcola_segnale(-3.5, 35.0)

        self.assertEqual(azione, "BUY")
        self.assertIsInstance(motivo, str)

    def test_sell(self):
        azione, motivo = calcola_segnale(4.5, 75.0)

        self.assertEqual(azione, "SELL")
        self.assertIsInstance(motivo, str)

    def test_hold(self):
        azione, motivo = calcola_segnale(-1.0, 50.0)

        self.assertEqual(azione, "HOLD")
        self.assertIsInstance(motivo, str)

    def test_dati_mancanti(self):
        dati = {
            "indicatori": {
                "^GSPC": {
                    "nome": "S&P 500",
                    "simbolo": "^GSPC",
                    "errore": True,
                }
            }
        }

        segnali = genera_segnali(dati)

        self.assertEqual(len(segnali), 1)
        self.assertEqual(segnali[0]["azione"], "HOLD")
        self.assertIsNone(segnali[0]["rsi"])
        self.assertIsNone(segnali[0]["pct_vs_sma20"])


if __name__ == "__main__":
    unittest.main()