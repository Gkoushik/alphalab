# AlphaLab

A research framework for backtesting trading strategies and running experiments.

## Project Structure

```
alphalab/
├── data/                  ← fetched CSVs saved here (git-ignored)
├── scripts/
│   └── get_token.py       ← run daily to refresh Kite access token
├── src/
│   ├── data_fetcher.py    ← fetch OHLCV data via Yahoo Finance
│   ├── kite_fetcher.py    ← fetch data via Zerodha Kite Connect
│   ├── indicators.py      ← technical indicators (SMA, EMA, RSI, MACD, BBands, ATR)
│   ├── backtester.py      ← run_backtest() + BacktestResult (return, Sharpe, drawdown)
│   └── portfolio.py       ← multi-asset portfolio returns and stats
├── notebooks/
│   ├── strategy_experiment.ipynb
│   └── portfolio_analysis.ipynb
├── .env                   ← your API keys (never committed)
├── .env.example           ← copy this to .env and fill in your keys
└── requirements.txt
```

## Setup

### 1. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API keys

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

Edit `.env` and fill in your keys:

```
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here
```

> `.env` is git-ignored and will never be committed.

### 4. Generate Kite access token (run daily)

Kite access tokens expire every day at midnight. Run this each morning before using any Kite data:

```bash
python scripts/get_token.py
```

What it does:
1. Opens the Kite login page in your browser automatically
2. You log in and copy the `request_token` from the redirect URL
3. Paste it into the terminal prompt
4. The script generates the access token and **saves it to `.env` automatically**

No manual copy-pasting into `.env` needed.

## Running Notebooks

```bash
jupyter notebook
```

Then open `notebooks/strategy_experiment.ipynb` or `notebooks/portfolio_analysis.ipynb`.

## Usage

### Fetch data (Yahoo Finance)

```python
from src.data_fetcher import fetch
data = fetch("AAPL", start="2023-01-01", end="2024-01-01")
```

### Fetch data (Kite Connect)

```python
from src.kite_fetcher import fetch, search_instrument

# Find instrument token
search_instrument("RELIANCE")

# Fetch OHLCV
df = fetch(instrument_token=738561, from_date="2024-01-01", interval="day")
```

### Run a backtest

```python
from src.indicators import sma
from src.backtester import run_backtest
import pandas as pd

signals = pd.Series(0, index=data.index)
signals[sma(data["close"], 10) > sma(data["close"], 30)] = 1
signals[sma(data["close"], 10) <= sma(data["close"], 30)] = -1

result = run_backtest(signals, data, strategy_name="SMA Crossover")
print(result.summary())
```

### Available indicators

```python
from src.indicators import sma, ema, rsi, macd, bollinger_bands, atr
```
