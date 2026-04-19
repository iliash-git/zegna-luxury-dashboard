# Power BI Build Guide — Zegna vs. Luxury Peers

This guide walks you from a fresh Power BI Desktop install to a finished, publishable, auto-refreshing dashboard. Follow the sections in order.

---

## 0. Prerequisites

- **Power BI Desktop** (free) — [download here](https://powerbi.microsoft.com/desktop/)
- **Power BI Service** account (free) — sign up at [app.powerbi.com](https://app.powerbi.com) with a work email
- **GitHub repo** hosting this project (public, so Power BI can read the raw CSVs)
- Python pipeline has run at least once (check `data/` for CSVs)

> 💡 You need a work/school email for Power BI Service. Personal Gmail/Outlook won't work. If you don't have one, you can still build locally and share screenshots + the .pbix on GitHub.

---

## 1. Connect Power BI to the GitHub-hosted CSVs

The pipeline commits fresh CSVs to your GitHub repo daily. Power BI can read them directly via the "raw" GitHub URL.

### Find your raw CSV URLs

After pushing the repo to GitHub, each CSV has a raw URL pattern:

```
https://raw.githubusercontent.com/<your-username>/zegna-luxury-dashboard/main/data/<filename>.csv
```

For example:
```
https://raw.githubusercontent.com/johndoe/zegna-luxury-dashboard/main/data/company_info.csv
```

### Load each CSV into Power BI

In Power BI Desktop:

1. **Home → Get Data → Web**
2. Paste the raw URL for `company_info.csv`
3. Click **OK** → **Transform Data** (opens Power Query Editor)
4. In the preview, click **Use First Row as Headers** if not already set
5. Check data types in the column headers — Power BI should auto-detect, but verify:
   - `market_cap`, `enterprise_value`, `current_price` → **Decimal Number**
   - `is_focus` → **True/False**
   - Everything else → **Text**
6. Rename the query to `CompanyInfo` (right panel → Name)
7. **Close & Apply**

Repeat for the other six files:

| CSV file | Rename query to | Key column types |
|---|---|---|
| `company_info.csv` | `CompanyInfo` | See above |
| `key_metrics.csv` | `KeyMetrics` | All numeric columns → Decimal Number |
| `income_statement.csv` | `IncomeStatement` | `fiscal_date` → Date, `value` → Decimal Number |
| `balance_sheet.csv` | `BalanceSheet` | `fiscal_date` → Date, `value` → Decimal Number |
| `cash_flow.csv` | `CashFlow` | `fiscal_date` → Date, `value` → Decimal Number |
| `price_history.csv` | `PriceHistory` | `date` → Date, price columns → Decimal Number |
| `last_updated.csv` | `LastUpdated` | `refreshed_at_utc` → Date/Time |

---

## 2. Build the Data Model

Open **Model View** (left sidebar, third icon).

### Create a Date dimension table

A dedicated date table is essential for time intelligence. In **Table View → New Table**, paste:

```dax
DimDate =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2020, 1, 1 ), TODAY () ),
    "Year", YEAR ( [Date] ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" ),
    "Year-Quarter", FORMAT ( [Date], "YYYY" ) & "-Q" & FORMAT ( [Date], "Q" ),
    "Month", FORMAT ( [Date], "MMM YYYY" ),
    "MonthStart", DATE ( YEAR ( [Date] ), MONTH ( [Date] ), 1 ),
    "MonthNumber", MONTH ( [Date] ),
    "FiscalYear", YEAR ( [Date] )
)
```

Then in **Model View**: select `DimDate` → **Mark as date table** (right panel) → choose `Date` column.

### Create relationships

Drag these lines in Model View (all one-to-many, single direction, `DimDate` is the "one" side):

- `DimDate[Date]` → `PriceHistory[date]`
- `DimDate[Date]` → `IncomeStatement[fiscal_date]`
- `DimDate[Date]` → `BalanceSheet[fiscal_date]`
- `DimDate[Date]` → `CashFlow[fiscal_date]`

And `CompanyInfo` as the dimension for tickers (one-to-many, single direction):

- `CompanyInfo[ticker]` → `KeyMetrics[ticker]`
- `CompanyInfo[ticker]` → `PriceHistory[ticker]`
- `CompanyInfo[ticker]` → `IncomeStatement[ticker]`
- `CompanyInfo[ticker]` → `BalanceSheet[ticker]`
- `CompanyInfo[ticker]` → `CashFlow[ticker]`

The final model is a **star schema**: `DimDate` and `CompanyInfo` at the center, fact tables around them.

---

## 3. DAX Measures

Create a new empty table called `_Measures` (Enter Data → create empty column, rename table). This is just a home for your measures — keeps them organized.

Click `_Measures` → **New measure** for each of the following. Copy-paste the formula exactly.

### 3.1 Price & market cap measures

```dax
Latest Close =
VAR MaxDate = CALCULATE ( MAX ( PriceHistory[date] ), ALLEXCEPT ( CompanyInfo, CompanyInfo[ticker] ) )
RETURN CALCULATE ( SUM ( PriceHistory[close] ), PriceHistory[date] = MaxDate )
```

```dax
Price 1Y Ago =
VAR TargetDate = TODAY () - 365
RETURN
    CALCULATE (
        SUM ( PriceHistory[close] ),
        PriceHistory[date] = CALCULATE ( MAX ( PriceHistory[date] ), PriceHistory[date] <= TargetDate )
    )
```

```dax
Price YoY % =
DIVIDE ( [Latest Close] - [Price 1Y Ago], [Price 1Y Ago] )
```

```dax
Market Cap (Bn) =
DIVIDE ( SUM ( CompanyInfo[market_cap] ), 1e9 )
```

### 3.2 Revenue & profitability measures

Because `IncomeStatement` is in long format, we filter by `metric` name:

```dax
Revenue =
CALCULATE (
    SUM ( IncomeStatement[value] ),
    IncomeStatement[metric] = "Total Revenue"
)
```

```dax
Gross Profit =
CALCULATE (
    SUM ( IncomeStatement[value] ),
    IncomeStatement[metric] = "Gross Profit"
)
```

```dax
Operating Income =
CALCULATE (
    SUM ( IncomeStatement[value] ),
    IncomeStatement[metric] = "Operating Income"
)
```

```dax
Net Income =
CALCULATE (
    SUM ( IncomeStatement[value] ),
    IncomeStatement[metric] = "Net Income"
)
```

```dax
EBITDA =
CALCULATE (
    SUM ( IncomeStatement[value] ),
    IncomeStatement[metric] = "EBITDA"
)
```

### 3.3 Margin measures

```dax
Gross Margin % = DIVIDE ( [Gross Profit], [Revenue] )
Operating Margin % = DIVIDE ( [Operating Income], [Revenue] )
Net Margin % = DIVIDE ( [Net Income], [Revenue] )
EBITDA Margin % = DIVIDE ( [EBITDA], [Revenue] )
```

### 3.4 Growth measures

```dax
Revenue Prior Year =
CALCULATE ( [Revenue], DATEADD ( DimDate[Date], -1, YEAR ) )
```

```dax
Revenue YoY % =
DIVIDE ( [Revenue] - [Revenue Prior Year], [Revenue Prior Year] )
```

```dax
Revenue 3Y CAGR =
VAR RevNow = [Revenue]
VAR Rev3YAgo = CALCULATE ( [Revenue], DATEADD ( DimDate[Date], -3, YEAR ) )
RETURN IF ( Rev3YAgo > 0, ( RevNow / Rev3YAgo ) ^ ( 1/3 ) - 1 )
```

### 3.5 Peer ranking measures

These are the "money" measures that make the dashboard feel analytical:

```dax
Revenue Rank =
RANKX ( ALL ( CompanyInfo[ticker] ), [Revenue],, DESC, DENSE )
```

```dax
Gross Margin Rank =
RANKX ( ALL ( CompanyInfo[ticker] ), [Gross Margin %],, DESC, DENSE )
```

```dax
Revenue Growth Rank =
RANKX ( ALL ( CompanyInfo[ticker] ), [Revenue YoY %],, DESC, DENSE )
```

### 3.6 Valuation measures (from KeyMetrics snapshot)

```dax
P/E (TTM) = SUM ( KeyMetrics[trailing_pe] )
Forward P/E = SUM ( KeyMetrics[forward_pe] )
EV/EBITDA = SUM ( KeyMetrics[ev_to_ebitda] )
P/S = SUM ( KeyMetrics[price_to_sales] )
ROE % = SUM ( KeyMetrics[return_on_equity] )
```

### 3.7 Normalized price index (for peer comparison chart)

```dax
Normalized Price =
VAR FirstDate = CALCULATE ( MIN ( PriceHistory[date] ), ALLSELECTED ( PriceHistory ) )
VAR BasePrice =
    CALCULATE (
        SUM ( PriceHistory[close] ),
        PriceHistory[date] = FirstDate,
        ALLEXCEPT ( CompanyInfo, CompanyInfo[ticker] )
    )
RETURN DIVIDE ( SUM ( PriceHistory[close] ), BasePrice ) * 100
```

### 3.8 Refresh timestamp display

```dax
Last Refreshed Text =
"Data refreshed: " & FORMAT ( MAX ( LastUpdated[refreshed_at_utc] ), "dd MMM yyyy HH:mm" ) & " UTC"
```

---

## 4. Dashboard Pages

Set each page background to a clean color (white or very light gray — `#F7F7F7`) and use Power BI's default slicer/filter pane on the right.

### Color palette (suggested)

- Zegna (focus): `#1A1A1A` (charcoal — matches their brand)
- Peers: `#9CA3AF` (gray) — makes the focus company pop
- Accent / positive: `#16A34A`
- Accent / negative: `#DC2626`
- Headers: `#1A1A1A` text on white

### Page 1 — Executive Summary

Visuals (left to right, top to bottom):

1. **Title text box**: "Ermenegildo Zegna — Investor Dashboard" + `[Last Refreshed Text]` measure as subtitle
2. **KPI cards (4 cards)**:
   - Current Price: `[Latest Close]` + `[Price YoY %]` as delta
   - Market Cap: `[Market Cap (Bn)]`
   - FY Revenue: `[Revenue]` with `[Revenue YoY %]` delta
   - Net Margin: `[Net Margin %]`
   - Filter all cards by `CompanyInfo[is_focus] = TRUE`
3. **Peer rank table**: columns = Company name, Revenue Rank, Margin Rank, Growth Rank
4. **Line chart**: Normalized Price (5 years, all 6 peers, Zegna highlighted)
5. **Text box (right side)**: 2-3 sentence summary — your one-liner takeaway

### Page 2 — Zegna Deep-Dive

Filter the whole page to Zegna only: page-level filter `CompanyInfo[ticker] = "ZGN"`.

1. **Stacked bar chart**: Revenue over 4 years
   - Use `IncomeStatement` directly with metric filter = "Total Revenue"
   - Can't split by segment from yfinance — add a **text callout** explaining Zegna's reported segment mix (ZEGNA brand 62%, Thom Browne 14%, Tom Ford 24%) from their [FY2025 press release](https://www.businesswire.com/news/home/20260320107465/en/)
2. **Waterfall chart**: P&L FY2025
   - Categories: Revenue, COGS, Gross Profit, SG&A, Operating Income, Tax, Net Income
   - Build with a calculated table or manual entry from the IncomeStatement data
3. **Line chart**: Margins over time
   - Y-axis: Gross Margin %, Operating Margin %, Net Margin %
   - X-axis: DimDate[Year]
4. **Card**: Free Cash Flow (from CashFlow table, metric = "Free Cash Flow")
5. **Card**: Net Debt / Cash Surplus (from BalanceSheet, metric = "Net Debt")

### Page 3 — Peer Benchmarking

No page-level filter — shows all 6 companies.

1. **Horizontal bar chart**: Revenue by company (latest year)
   - Conditional formatting: Zegna in `#1A1A1A`, peers in gray
2. **Clustered column chart**: Growth rates side-by-side (Revenue YoY %, 3Y CAGR)
3. **Heatmap matrix**: Rows = companies, Columns = margin metrics (Gross, Operating, Net), Values = % with color scale
4. **Scatter plot**: X = EV/EBITDA, Y = Revenue Growth, Bubble size = Market Cap
   - Zegna highlighted in charcoal

### Page 4 — Stock & Valuation

1. **Line chart**: Normalized price index (full 5 years, all 6 peers)
2. **Column chart**: Current valuation multiples side-by-side (P/E, Forward P/E, EV/EBITDA, P/S)
3. **Card grid (3x2)**: Each peer's market cap, YTD return, current P/E
4. **Area chart**: Trading volume for ZGN over time

### Page 5 — Investment Thesis

Mostly text + a few supporting visuals. Use text boxes, not a fancy template.

1. **Your thesis paragraph** (2-3 sentences): Is Zegna undervalued vs. peers? What's the bull case, bear case?
2. **Bull case bullet list**: DTC 82% of revenue, net cash position, margin expansion, analyst upgrades
3. **Bear case bullet list**: Thom Browne declining, Saks Global exposure, China luxury softness
4. **Small visual**: Analyst price target distribution (data you curate manually from [Finviz](https://finviz.com/quote.ashx?t=ZGN))
5. **Sources footer**: Link to Zegna IR, SEC filings, Yahoo Finance

---

## 5. Publish & Set Up Auto-Refresh

### Publish to Power BI Service

1. In Power BI Desktop: **File → Save** (save as `Zegna_Luxury_Dashboard.pbix` in the `report/` folder)
2. **Home → Publish** → pick your workspace (usually "My workspace")
3. The dashboard is now live at [app.powerbi.com](https://app.powerbi.com)

### Configure scheduled refresh

In Power BI Service:

1. Go to your workspace → find the **dataset** (not the report)
2. Click the three dots → **Settings** → **Scheduled refresh**
3. Set frequency: **Daily**
4. Pick a time shortly after 06:00 UTC (when GitHub Actions finishes the data refresh) — e.g. 07:00 UTC
5. Under **Data source credentials**: GitHub raw URLs are anonymous access → select **Anonymous**
6. **Apply**

That's it. Every day at 07:00 UTC, Power BI will pull fresh CSVs from your GitHub repo.

### Share with the world

**Option A: Publish to web (free, public)**
- Report view → **File → Embed report → Publish to web**
- ⚠️ This makes the dashboard **publicly accessible to anyone with the link** — good for LinkedIn, but never use for confidential data
- Requires a Pro license (some orgs have this disabled)

**Option B: Share the .pbix file via GitHub**
- Commit `report/Zegna_Luxury_Dashboard.pbix` to the repo
- Include 3-5 screenshots in `screenshots/` and embed them in the README

**Option C: Record a Loom walkthrough**
- 2-3 minute video narrating the dashboard
- Embed the Loom link in your LinkedIn post — this drives engagement

---

## 6. Polishing Checklist

Before posting to LinkedIn, verify:

- [ ] All numbers display with proper formatting (no "12345678.9" — use thousands separators, currency symbols)
- [ ] Percentages show % suffix, not decimals (e.g. "14.4%" not "0.144")
- [ ] Page navigation is clear (title + subtitle on every page)
- [ ] No broken visuals (red exclamation marks in corners)
- [ ] Color palette is consistent across all pages
- [ ] `[Last Refreshed Text]` appears on Page 1
- [ ] Focus company (Zegna) visually stands out in every peer comparison
- [ ] Every page has a clear takeaway — not just data, but insight
- [ ] Fonts are consistent (pick one — Segoe UI is the Power BI default)
- [ ] Export a PDF of the full dashboard for screenshots in your README

---

## 7. Troubleshooting

**Q: My DAX measure returns blank for Revenue**
A: The metric name in yfinance data is "Total Revenue" — exact string match. Open `IncomeStatement` in Table View and filter the `metric` column to see available names. Names occasionally differ: "Net Income Common Stockholders" vs "Net Income" etc.

**Q: Power BI Service refresh fails with "couldn't parse"**
A: Check that your GitHub repo is **public**. Private repos need a personal access token, which is much harder to set up.

**Q: My GitHub Actions workflow doesn't run**
A: Actions are disabled by default on forked repos. Go to the Actions tab and click "I understand my workflows, enable them".

**Q: My Zegna data shows EUR but peers show different currencies**
A: That's correct — yfinance reports in each company's reporting currency. For direct revenue comparison, either (a) note the caveat in your dashboard, or (b) add a currency conversion step in the Python pipeline using `yfinance.Ticker("EURUSD=X").history()`.

---

## 8. What Makes This Portfolio-Worthy

When you post this on LinkedIn, hiring managers look for:

- ✅ **Real data** (not a toy dataset)
- ✅ **Automated pipeline** (not copy-pasted CSVs)
- ✅ **Clear business question** (not just "here's a dashboard")
- ✅ **Analytical insight** (not just charts)
- ✅ **Polished presentation** (fonts, colors, alignment)
- ✅ **Domain knowledge** (finance/luxury signals — you have both)

All six are covered here if you execute. Good luck.
