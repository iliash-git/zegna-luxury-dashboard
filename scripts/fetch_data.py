"""
Zegna vs. Luxury Peers — Data Pipeline
----------------------------------------
Fetches income statement, balance sheet, cash flow, key metrics, and price history
for Ermenegildo Zegna and its peer group from Yahoo Finance via yfinance.

Outputs:
  data/company_info.csv       - Static company profile (name, sector, country, market cap)
  data/income_statement.csv   - Annual income statements, 4 years
  data/balance_sheet.csv      - Annual balance sheets, 4 years
  data/cash_flow.csv          - Annual cash flow statements, 4 years
  data/key_metrics.csv        - Current valuation & financial ratios
  data/price_history.csv      - 5 years of daily prices, all tickers
  data/last_updated.csv       - Refresh timestamp

Scheduled daily via GitHub Actions. Run locally with:
    python scripts/fetch_data.py
"""

from __future__ import annotations

import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

# Peer group. The focus company (Zegna) is tagged so Power BI can filter.
# Note: Tod's Group (TOD.MI) was taken private in 2024 and delisted, so we use
# Prada (1913.HK) as a similarly-sized Italian luxury peer instead.
PEERS: dict[str, dict[str, str | bool]] = {
    "ZGN":     {"name": "Ermenegildo Zegna",    "country": "Italy",   "is_focus": True},
    "BC.MI":   {"name": "Brunello Cucinelli",   "country": "Italy",   "is_focus": False},
    "MONC.MI": {"name": "Moncler",              "country": "Italy",   "is_focus": False},
    "1913.HK": {"name": "Prada",                "country": "Italy",   "is_focus": False},
    "SFER.MI": {"name": "Salvatore Ferragamo",  "country": "Italy",   "is_focus": False},
    "BOSS.DE": {"name": "Hugo Boss",            "country": "Germany", "is_focus": False},
}

PRICE_HISTORY_PERIOD = "5y"    # yfinance period string
INCOME_PERIODS = 4             # years of annual financial statements
REQUEST_DELAY_SECONDS = 1.5    # polite pause between tickers to avoid rate limiting

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("zegna-pipeline")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def safe_get(info: dict, key: str, default=None):
    """yfinance .info dicts can be flaky — return default if key missing.

    Handles scalar values and occasionally returned pandas Series/arrays
    without raising ambiguous-truth-value errors.
    """
    value = info.get(key, default)
    if value is None:
        return default
    # Some yfinance versions return pandas Series for certain fields
    if hasattr(value, "iloc") and hasattr(value, "empty"):
        if value.empty:
            return default
        try:
            value = value.iloc[0]
        except Exception:
            return default
    if isinstance(value, str) and value.strip() in ("", "N/A"):
        return default
    return value


def unpivot_statement(df: pd.DataFrame, ticker: str, statement_type: str) -> pd.DataFrame:
    """
    yfinance returns financial statements with dates as columns and metrics as rows.
    Power BI prefers a long format: one row per (ticker, date, metric).
    """
    if df is None or df.empty:
        log.warning("  %s %s is empty", ticker, statement_type)
        return pd.DataFrame()

    df = df.copy()
    # yfinance occasionally returns duplicate metric rows which break reshapes.
    df = df[~df.index.duplicated(keep="first")]
    df.index.name = "metric"

    # Cast all values to numeric; non-numeric rows become NaN and get dropped below
    df = df.apply(pd.to_numeric, errors="coerce")

    # Manual long-format reshape (avoiding melt which has edge cases with
    # yfinance DataFrames). Iterate over each date column and stack.
    records: list[dict] = []
    for date_col in df.columns:
        for metric, value in df[date_col].items():
            if pd.isna(value):
                continue
            records.append({
                "ticker":      ticker,
                "statement":   statement_type,
                "fiscal_date": pd.to_datetime(date_col, errors="coerce"),
                "metric":      metric,
                "value":       float(value),
            })

    if not records:
        return pd.DataFrame()

    long_df = pd.DataFrame(records)
    long_df["fiscal_date"] = long_df["fiscal_date"].dt.date
    long_df = long_df.dropna(subset=["fiscal_date"])
    return long_df[["ticker", "statement", "fiscal_date", "metric", "value"]]


# ----------------------------------------------------------------------------
# Data fetchers
# ----------------------------------------------------------------------------

def fetch_company_info(ticker: str, meta: dict) -> dict:
    """Static company profile + current market cap / price snapshot."""
    stock = yf.Ticker(ticker)
    info = stock.info or {}
    return {
        "ticker":          ticker,
        "company_name":    meta["name"],
        "country":         meta["country"],
        "is_focus":        meta["is_focus"],
        "currency":        safe_get(info, "currency"),
        "exchange":        safe_get(info, "exchange"),
        "sector":          safe_get(info, "sector"),
        "industry":        safe_get(info, "industry"),
        "website":         safe_get(info, "website"),
        "employees":       safe_get(info, "fullTimeEmployees"),
        "market_cap":      safe_get(info, "marketCap"),
        "enterprise_value": safe_get(info, "enterpriseValue"),
        "current_price":   safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice"),
        "52w_high":        safe_get(info, "fiftyTwoWeekHigh"),
        "52w_low":         safe_get(info, "fiftyTwoWeekLow"),
    }


def fetch_key_metrics(ticker: str) -> dict:
    """Valuation multiples and profitability ratios (point-in-time snapshot)."""
    stock = yf.Ticker(ticker)
    info = stock.info or {}
    return {
        "ticker":              ticker,
        "trailing_pe":         safe_get(info, "trailingPE"),
        "forward_pe":          safe_get(info, "forwardPE"),
        "price_to_sales":      safe_get(info, "priceToSalesTrailing12Months"),
        "price_to_book":       safe_get(info, "priceToBook"),
        "ev_to_revenue":       safe_get(info, "enterpriseToRevenue"),
        "ev_to_ebitda":        safe_get(info, "enterpriseToEbitda"),
        "profit_margin":       safe_get(info, "profitMargins"),
        "operating_margin":    safe_get(info, "operatingMargins"),
        "gross_margin":        safe_get(info, "grossMargins"),
        "return_on_equity":    safe_get(info, "returnOnEquity"),
        "return_on_assets":    safe_get(info, "returnOnAssets"),
        "revenue_growth":      safe_get(info, "revenueGrowth"),
        "earnings_growth":     safe_get(info, "earningsGrowth"),
        "debt_to_equity":      safe_get(info, "debtToEquity"),
        "current_ratio":       safe_get(info, "currentRatio"),
        "dividend_yield":      safe_get(info, "dividendYield"),
        "beta":                safe_get(info, "beta"),
    }


def fetch_financial_statements(ticker: str) -> pd.DataFrame:
    """Income statement + balance sheet + cash flow, annual, long format."""
    stock = yf.Ticker(ticker)
    frames = []
    for statement_type, attr in [
        ("income_statement", "financials"),
        ("balance_sheet",    "balance_sheet"),
        ("cash_flow",        "cashflow"),
    ]:
        raw = getattr(stock, attr)
        long_df = unpivot_statement(raw, ticker, statement_type)
        if not long_df.empty:
            # Keep only the latest N fiscal years to keep file sizes reasonable
            latest_dates = sorted(long_df["fiscal_date"].unique(), reverse=True)[:INCOME_PERIODS]
            long_df = long_df[long_df["fiscal_date"].isin(latest_dates)]
            frames.append(long_df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def fetch_price_history(ticker: str) -> pd.DataFrame:
    """5-year daily price history — for stock chart + normalized peer comparison."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=PRICE_HISTORY_PERIOD, auto_adjust=True)
    if hist.empty:
        log.warning("  %s has no price history", ticker)
        return pd.DataFrame()

    hist = hist.reset_index()
    hist["ticker"] = ticker
    # Standardize column names for Power BI
    hist = hist.rename(columns={
        "Date":   "date",
        "Open":   "open",
        "High":   "high",
        "Low":    "low",
        "Close":  "close",
        "Volume": "volume",
    })
    hist["date"] = pd.to_datetime(hist["date"]).dt.date
    return hist[["ticker", "date", "open", "high", "low", "close", "volume"]]


# ----------------------------------------------------------------------------
# Orchestration
# ----------------------------------------------------------------------------

def run_pipeline() -> None:
    log.info("=" * 64)
    log.info("Zegna Luxury Peers — data refresh starting")
    log.info("Tickers: %s", ", ".join(PEERS.keys()))
    log.info("=" * 64)

    company_rows: list[dict] = []
    metrics_rows: list[dict] = []
    statement_frames: list[pd.DataFrame] = []
    price_frames: list[pd.DataFrame] = []

    for ticker, meta in PEERS.items():
        log.info("Fetching %s (%s)", ticker, meta["name"])
        try:
            company_rows.append(fetch_company_info(ticker, meta))
            metrics_rows.append(fetch_key_metrics(ticker))
            statement_frames.append(fetch_financial_statements(ticker))
            price_frames.append(fetch_price_history(ticker))
        except Exception as exc:  # noqa: BLE001 — we want the pipeline to continue
            log.error("  Failed to fetch %s: %s", ticker, exc)
        time.sleep(REQUEST_DELAY_SECONDS)

    # --- Write outputs --------------------------------------------------------
    pd.DataFrame(company_rows).to_csv(DATA_DIR / "company_info.csv", index=False)
    pd.DataFrame(metrics_rows).to_csv(DATA_DIR / "key_metrics.csv", index=False)

    # Only concatenate non-empty frames
    non_empty_statements = [f for f in statement_frames if not f.empty]
    if non_empty_statements:
        all_statements = pd.concat(non_empty_statements, ignore_index=True)
        # Split into three separate files for cleaner Power BI modeling
        for st in ["income_statement", "balance_sheet", "cash_flow"]:
            subset = all_statements[all_statements["statement"] == st]
            subset.to_csv(DATA_DIR / f"{st}.csv", index=False)
            log.info("  Wrote %s.csv — %d rows", st, len(subset))
    else:
        log.warning("No financial statements retrieved for any ticker")

    non_empty_prices = [f for f in price_frames if not f.empty]
    if non_empty_prices:
        all_prices = pd.concat(non_empty_prices, ignore_index=True)
        all_prices.to_csv(DATA_DIR / "price_history.csv", index=False)
        log.info("  Wrote price_history.csv — %d rows", len(all_prices))

    # Refresh stamp
    pd.DataFrame([{
        "refreshed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tickers":          ",".join(PEERS.keys()),
    }]).to_csv(DATA_DIR / "last_updated.csv", index=False)

    log.info("=" * 64)
    log.info("Pipeline complete. Files written to %s", DATA_DIR)
    log.info("=" * 64)


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as exc:  # noqa: BLE001
        log.exception("Pipeline failed: %s", exc)
        sys.exit(1)
