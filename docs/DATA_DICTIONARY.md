# Data Dictionary

Reference for every column in every CSV produced by `scripts/fetch_data.py`.

---

## `company_info.csv`

One row per ticker. Static profile + current market cap snapshot.

| Column | Type | Description |
|---|---|---|
| `ticker` | string | Yahoo Finance ticker symbol (e.g. `ZGN`, `BC.MI`) |
| `company_name` | string | Human-readable company name |
| `country` | string | Country of headquarters |
| `is_focus` | bool | `True` for the focus company (Zegna), `False` for peers. Use this as a slicer/filter in Power BI. |
| `currency` | string | Reporting currency per Yahoo Finance |
| `exchange` | string | Exchange code (NYQ = NYSE, MIL = Milan, HKG = Hong Kong) |
| `sector` | string | GICS sector |
| `industry` | string | GICS industry |
| `website` | string | Company investor relations URL |
| `employees` | int | Full-time employee count |
| `market_cap` | int | Current market capitalization (in reporting currency) |
| `enterprise_value` | int | Enterprise value |
| `current_price` | float | Latest traded price |
| `52w_high` | float | 52-week high |
| `52w_low` | float | 52-week low |

---

## `key_metrics.csv`

One row per ticker. Valuation and profitability ratios (point-in-time snapshot — **not** time series).

| Column | Type | Description |
|---|---|---|
| `ticker` | string | Ticker symbol |
| `trailing_pe` | float | Trailing 12-month Price/Earnings ratio |
| `forward_pe` | float | Forward P/E (based on consensus estimates) |
| `price_to_sales` | float | Price / trailing 12-month revenue |
| `price_to_book` | float | Price / book value per share |
| `ev_to_revenue` | float | Enterprise Value / Revenue |
| `ev_to_ebitda` | float | Enterprise Value / EBITDA — standard luxury sector valuation multiple |
| `profit_margin` | float | Net margin (0-1, multiply by 100 for %) |
| `operating_margin` | float | Operating margin (0-1) |
| `gross_margin` | float | Gross margin (0-1) |
| `return_on_equity` | float | Return on Equity (0-1) |
| `return_on_assets` | float | Return on Assets (0-1) |
| `revenue_growth` | float | Most recent quarter YoY revenue growth |
| `earnings_growth` | float | Most recent quarter YoY earnings growth |
| `debt_to_equity` | float | Total debt / total equity (often reported as a %, e.g. 89.38 = 89.38%) |
| `current_ratio` | float | Current assets / current liabilities — short-term liquidity |
| `dividend_yield` | float | Annual dividend yield |
| `beta` | float | 5-year beta vs. market benchmark |

---

## `income_statement.csv`, `balance_sheet.csv`, `cash_flow.csv`

Long format — one row per (ticker, fiscal_date, metric). This schema makes Power BI modeling much easier than the native wide format from yfinance.

| Column | Type | Description |
|---|---|---|
| `ticker` | string | Ticker symbol |
| `statement` | string | One of `income_statement`, `balance_sheet`, `cash_flow` |
| `fiscal_date` | date | End-of-period date for the fiscal year (typically Dec 31) |
| `metric` | string | Line item name (e.g. "Total Revenue", "Net Income", "Free Cash Flow") |
| `value` | float | Value in the company's reporting currency |

### Common metric names you'll use in DAX

**Income Statement:**
- `Total Revenue`
- `Cost Of Revenue`
- `Gross Profit`
- `Operating Income` / `Operating Expense`
- `EBITDA`
- `EBIT`
- `Net Income`
- `Basic EPS`
- `Diluted EPS`

**Balance Sheet:**
- `Total Assets`
- `Total Liabilities Net Minority Interest`
- `Stockholders Equity`
- `Total Debt`
- `Cash And Cash Equivalents`
- `Net Debt`
- `Working Capital`

**Cash Flow:**
- `Operating Cash Flow`
- `Investing Cash Flow`
- `Financing Cash Flow`
- `Free Cash Flow`
- `Capital Expenditure`

> 💡 Exact metric names vary slightly between companies. If a DAX measure returns blank, open the CSV in Power Query and filter the `metric` column to see what's actually available for that ticker.

---

## `price_history.csv`

Long format — one row per (ticker, trading date). 5 years of daily bars.

| Column | Type | Description |
|---|---|---|
| `ticker` | string | Ticker symbol |
| `date` | date | Trading date |
| `open` | float | Opening price, auto-adjusted for splits and dividends |
| `high` | float | Intraday high |
| `low` | float | Intraday low |
| `close` | float | Closing price, auto-adjusted |
| `volume` | int | Shares traded |

Adjusted prices mean the 5-year series is directly comparable across time without manual split/dividend adjustments.

---

## `last_updated.csv`

Single-row metadata file.

| Column | Type | Description |
|---|---|---|
| `refreshed_at_utc` | datetime | When the pipeline last ran (ISO 8601 with timezone) |
| `tickers` | string | Comma-separated list of tickers in this refresh |

Use in Power BI to display a "Last refreshed: ..." footer on the dashboard.
