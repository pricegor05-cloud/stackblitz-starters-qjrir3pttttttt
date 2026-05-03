from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import random
import datetime

app = FastAPI()

WATCHLIST = ["AAPL", "TSLA", "NVDA", "AMD", "SPY"]


# -----------------------------
# INDICATORS
# -----------------------------

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def vwap(df):
    return (df["Close"] * df["Volume"]).cumsum() / df["Volume"].cumsum()


# -----------------------------
# MARKET REGIME DETECTION
# -----------------------------

def market_regime(df):
    sma_fast = df["Close"].rolling(10).mean()
    sma_slow = df["Close"].rolling(30).mean()

    volatility = df["Close"].pct_change().rolling(10).std().iloc[-1]

    if volatility > 0.03:
        return "HIGH_VOLATILITY"

    if sma_fast.iloc[-1] > sma_slow.iloc[-1]:
        return "UPTREND"

    if sma_fast.iloc[-1] < sma_slow.iloc[-1]:
        return "DOWNTREND"

    return "CHOP"


# -----------------------------
# NEWS IMPACT FILTER (SIMULATED)
# -----------------------------

def news_impact(ticker):
    # simulate news events (replace with real API later)
    events = ["NONE", "LOW", "HIGH"]

    # bias certain tickers slightly
    if ticker in ["TSLA", "NVDA"]:
        return random.choice(["LOW", "HIGH"])

    return random.choice(events)


# -----------------------------
# OPTIONS FLOW PROXY
# -----------------------------

def options_flow(df):
    vol_spike = df["Volume"].iloc[-1] > df["Volume"].rolling(20).mean().iloc[-1] * 2
    candle_size = abs(df["Close"].iloc[-1] - df["Open"].iloc[-1])

    if vol_spike and candle_size > 1:
        return "UNUSUAL"

    return "NORMAL"


# -----------------------------
# SNIPER ENTRY SYSTEM
# -----------------------------

def sniper(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if last["Close"] > prev["High"] and last["Volume"] > prev["Volume"]:
        return "BREAKOUT"

    if last["Close"] < prev["Low"] and last["Volume"] > prev["Volume"]:
        return "BREAKDOWN"

    return "WAIT"


# -----------------------------
# AI BIAS MODEL (simple scoring)
# -----------------------------

def ai_bias(df):
    score = 0

    if df["RSI"].iloc[-1] > 60:
        score += 1
    elif df["RSI"].iloc[-1] < 40:
        score -= 1

    if df["Close"].iloc[-1] > df["VWAP"].iloc[-1]:
        score += 1
    else:
        score -= 1

    if score >= 2:
        return "BULLISH"
    if score <= -2:
        return "BEARISH"
    return "NEUTRAL"


# -----------------------------
# SLIPPAGE HANDLING
# -----------------------------

def apply_slippage(price, regime):
    if regime == "HIGH_VOLATILITY":
        return price * 1.01  # worse fill
    elif regime == "CHOP":
        return price * 1.002
    else:
        return price * 1.0005


# -----------------------------
# MAIN ENGINE
# -----------------------------

@app.get("/scan")
def scan_market():
    results = {}

    for ticker in WATCHLIST:

        df = yf.download(ticker, period="5d", interval="5m")
        if df.empty:
            continue

        df["RSI"] = rsi(df["Close"])
        df["VWAP"] = vwap(df)

        price = df["Close"].iloc[-1]

        regime = market_regime(df)
        news = news_impact(ticker)
        flow = options_flow(df)
        entry = sniper(df)
        bias = ai_bias(df)

        signal = "HOLD"
        confidence = "LOW"

        # -----------------------------
        # NEWS FILTER (block trades)
        # -----------------------------
        if news == "HIGH":
            signal = "HOLD"

        # -----------------------------
        # CORE LOGIC
        # -----------------------------
        if entry == "BREAKOUT" and bias == "BULLISH":
            signal = "CALL"
            confidence = "HIGH"

        if entry == "BREAKDOWN" and bias == "BEARISH":
            signal = "PUT"
            confidence = "HIGH"

        # -----------------------------
        # APPLY SLIPPAGE MODEL
        # -----------------------------
        exec_price = apply_slippage(price, regime)

        results[ticker] = {
            "price": float(price),
            "executed_price": float(exec_price),
            "signal": signal,
            "confidence": confidence,
            "regime": regime,
            "news": news,
            "flow": flow,
            "entry": entry
        }

    return results

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows StackBlitz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scan")
def scan():
    return {"status": "running"}
