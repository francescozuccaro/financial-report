# Daily Financial Report

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)

A Python tool that fetches real-time market data from Yahoo Finance, computes technical indicators, and generates BUY/SELL/HOLD investment signals directly in the terminal.

## What it does

- Downloads live prices for S&P 500, NASDAQ, Dow Jones, VIX and Emerging Markets
- Computes SMA20 (20-day simple moving average) and RSI (relative strength index)
- Generates transparent BUY / SELL / HOLD signals based on clear rules
- Prints a color-coded report in the terminal

## Project structure

    financial-report/
    ├── main.py          # entry point — run this
    ├── fetcher.py       # fetches data from Yahoo Finance and computes SMA20/RSI
    ├── signals.py       # BUY/SELL/HOLD logic
    └── requirements.txt # dependencies

## How to run it

    # 1. Create virtual environment and install dependencies
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

    # 2. Run the program
    python main.py

## Signal logic

| Signal | Condition |
|--------|-----------|
| BUY  | Price ≥ 3% below SMA20 and RSI < 40 |
| SELL | Price ≥ 4% above SMA20 and RSI > 70 — or VIX > 30 |
| HOLD | Everything else |

## Technologies

- [yfinance](https://github.com/ranaroussi/yfinance) — market data
- [pandas](https://pandas.pydata.org/) — technical indicator computation

## Author

Built by Francesco Zuccaro — Computer Engineering student at Politecnico di Milano, interested in computer science and data-driven tools.
