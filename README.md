# Daily Financial Report

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

A small Python project that downloads market data, calculates technical indicators and displays a financial report in the terminal.

The user can select one or more markets to analyze. The program then retrieves the latest available data from Yahoo Finance and generates a simple BUY, SELL or HOLD indication.

This project was developed for educational purposes while studying Computer Engineering.

## Features

- Interactive market selection
- Support for multiple markets in the same report
- Latest available prices and daily percentage changes
- 20-day simple moving average
- 14-period relative strength index
- BUY, SELL and HOLD technical indications
- VIX volatility information
- Color-coded terminal output
- Basic error handling for unavailable data

## Available markets

The program currently supports:

- S&P 500
- NASDAQ Composite
- Dow Jones Industrial Average
- iShares MSCI Emerging Markets ETF

The VIX is downloaded separately and used to describe the general level of market volatility.

## How it works

The program follows three main steps:

1. `main.py` asks the user which markets should be analyzed.
2. `fetcher.py` downloads prices and historical data from Yahoo Finance.
3. `signals.py` applies transparent rules based on SMA20 and RSI.

The results are then displayed in the terminal.

## Technical indicators

### SMA20

The SMA20 is the simple average of the last 20 closing prices.

It provides a reference for comparing the current price with its recent average. A price below the SMA20 has recently been weaker than its average, while a price above the SMA20 has recently been stronger.

### RSI

The RSI, or Relative Strength Index, is a momentum indicator that normally ranges from 0 to 100.

This project calculates the RSI over 14 periods using smoothed averages of recent gains and losses.

A lower RSI indicates stronger recent downward movements, while a higher RSI indicates stronger recent upward movements.

### VIX

The VIX represents the expected volatility of the US stock market.

In this project it is used only to describe market conditions:

- below 20: contained volatility
- from 20 to 30: moderate volatility
- 30 or above: high volatility

A high VIX does not automatically generate a SELL indication.

## Signal rules

| Indication | Conditions |
|---|---|
| BUY | Price at least 3% below SMA20 and RSI below 40 |
| SELL | Price at least 4% above SMA20 and RSI above 70 |
| HOLD | All other situations or insufficient data |

These thresholds are intentionally simple and are stored as constants in `signals.py`, so they can be easily changed and tested.

## Project structure

```text
financial-report/
├── main.py
├── fetcher.py
├── signals.py
├── test_signals.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

- `main.py`: handles user interaction and prints the report
- `fetcher.py`: downloads market data and calculates SMA20 and RSI
- `signals.py`: generates technical indications
- `test_signals.py`: tests the signal logic
- `requirements.txt`: lists the external Python packages
- `.gitignore`: excludes local and generated files
- `LICENSE`: contains the MIT license

## Installation

Clone the repository:

```bash
git clone https://github.com/francescozuccaro/financial-report.git
cd financial-report
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the program with:

```bash
python main.py
```

The program will display an interactive menu:

```text
Quali mercati vuoi analizzare?

1. S&P 500
2. NASDAQ
3. Dow Jones
4. Mercati emergenti
5. Tutti
```

One or more markets can be selected by entering numbers separated by commas.

Example:

```text
1,2,4
```

## Tests

The signal logic can be tested without downloading market data.

Run all tests with:

```bash
python -m unittest
```

The test suite verifies:

- BUY conditions
- SELL conditions
- HOLD conditions
- missing market data handling

## Technologies

- Python
- pandas
- yfinance
- Yahoo Finance market data

## What I learned

By developing and revising this project, I practiced:

- dividing a program into separate modules
- working with external financial data
- processing time series with pandas
- implementing SMA and RSI calculations
- handling missing data and network errors
- validating user input
- using Git to organize changes into commits

## Disclaimer

This project is intended exclusively for educational purposes.

The generated indications are based on simplified technical rules and do not constitute financial advice or investment recommendations.

## Author

Francesco Zuccaro  
Computer Engineering student at Politecnico di Milano