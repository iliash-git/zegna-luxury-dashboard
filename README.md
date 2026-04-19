# Zegna vs. Luxury Peers — Power BI Dashboard

[![Daily Data Refresh](https://img.shields.io/badge/data-auto--refreshed%20daily-brightgreen)](.github/workflows/refresh_data.yml)
[![Power BI](https://img.shields.io/badge/built%20with-Power%20BI-F2C811)](https://powerbi.microsoft.com)
[![Python](https://img.shields.io/badge/pipeline-Python%203.12-blue)](scripts/fetch_data.py)

> An investor-style Power BI dashboard benchmarking **Ermenegildo Zegna Group (NYSE: ZGN)** against its Italian/European luxury peers, backed by an automated Python data pipeline that refreshes daily via GitHub Actions.

---

## 📊 Live Dashboard

🔗 **[Interactive Dashboard](https://app.powerbi.com/view?r=YOUR_LINK_HERE)** (Publish-to-Web link — replace with yours after publishing)

![Executive Summary](screenshots/01_executive_summary.png)

---

## 🎯 The Question

Zegna is navigating a complex transition: DTC growth now 82% of revenues, Thom Browne revenue down 14.7%, Tom Ford integration ongoing, €10M Saks Global Chapter 11 provision, and a return to net cash position. **Is the market pricing Zegna correctly relative to its Italian luxury peer group?**

## 🏢 Peer Group

| Ticker | Company | Country | Role |
|---|---|---|---|
| **ZGN** | Ermenegildo Zegna | 🇮🇹 Italy | **Focus** |
| BC.MI | Brunello Cucinelli | 🇮🇹 Italy | Closest pure-play peer |
| MONC.MI | Moncler | 🇮🇹 Italy | Italian mid-cap luxury |
| 1913.HK | Prada | 🇮🇹 Italy | Premium-tier comparator |
| SFER.MI | Salvatore Ferragamo | 🇮🇹 Italy | Similar revenue band |
| BOSS.DE | Hugo Boss | 🇩🇪 Germany | Premium menswear comparator |

## 📐 Architecture

```
┌─────────────────┐    cron daily    ┌──────────────────┐
│ Yahoo Finance   │ ───────────────▶ │  GitHub Actions  │
│   (yfinance)    │                  │ fetch_data.py    │
└─────────────────┘                  └────────┬─────────┘
                                              │ commits CSVs
                                              ▼
                                     ┌──────────────────┐
                                     │  GitHub repo     │
                                     │  /data/*.csv     │
                                     └────────┬─────────┘
                                              │ raw URLs
                                              ▼
                                     ┌──────────────────┐
                                     │  Power BI Service│
                                     │  scheduled refresh│
                                     └──────────────────┘
```

## 📁 Repository Structure

```
zegna-luxury-dashboard/
├── .github/workflows/refresh_data.yml   Daily GitHub Actions workflow
├── data/                                Auto-generated CSVs (7 files)
│   ├── company_info.csv                 Static profile + market cap snapshot
│   ├── key_metrics.csv                  Valuation & profitability ratios
│   ├── income_statement.csv             Annual P&L, 4 years, long format
│   ├── balance_sheet.csv                Annual balance sheet, 4 years
│   ├── cash_flow.csv                    Annual cash flow, 4 years
│   ├── price_history.csv                5-year daily prices
│   └── last_updated.csv                 Refresh timestamp
├── scripts/
│   └── fetch_data.py                    yfinance pipeline (the data layer)
├── report/
│   └── Zegna_Luxury_Dashboard.pbix      Power BI file (commit after building)
├── docs/
│   ├── POWERBI_BUILD_GUIDE.md           Step-by-step Power BI build instructions
│   └── DATA_DICTIONARY.md               Column reference for all CSVs
├── screenshots/                         Dashboard page exports
├── requirements.txt                     Python dependencies
└── README.md                            This file
```

## 🚀 Quick Start

### Run the pipeline locally

```bash
git clone https://github.com/YOUR_USERNAME/zegna-luxury-dashboard.git
cd zegna-luxury-dashboard
pip install -r requirements.txt
python scripts/fetch_data.py
```

Output: 7 CSV files in `data/`, populated with live Yahoo Finance data.

### Build the Power BI dashboard

Follow **[docs/POWERBI_BUILD_GUIDE.md](docs/POWERBI_BUILD_GUIDE.md)** — full step-by-step walkthrough from connecting the CSVs to publishing the final dashboard.

### Fork & auto-refresh

1. Fork this repo
2. Go to **Actions** tab → enable workflows
3. The daily cron will commit fresh data to your fork every day at 06:00 UTC
4. Point your Power BI dataset at the raw URLs from your fork

## 📈 Dashboard Pages

| Page | Purpose |
|---|---|
| **1. Executive Summary** | One-screen snapshot: Zegna KPIs, peer ranks, 5-year relative price |
| **2. Zegna Deep-Dive** | Revenue trends, P&L waterfall, margin evolution, cash position |
| **3. Peer Benchmarking** | Side-by-side revenue, growth, margins, valuation vs. all 6 peers |
| **4. Stock & Valuation** | Normalized price index, valuation multiples, market cap, volume |
| **5. Investment Thesis** | Bull/bear case synthesis — the analyst's take |

## 🔑 Key Insights (FY2025 data)

- **Profit grew 20% YoY** to €109.5M despite revenue declining 1.5% — a classic margin-expansion story
- **Gross margin reached 67.5%** (+90 bps), driven by DTC channel mix shift to 82% of branded revenues
- **Balance sheet transformed** from €94M net debt to €52M net cash surplus in a single year
- **Adjusted EBIT margin compressed** to 8.5% from 9.5% — reflecting Thom Browne softness and Saks Global provision
- **Analyst views diverged sharply**: UBS upgraded to Buy (€11.50 PT), BofA downgraded to Neutral, Morgan Stanley Equal-Weight ([Finviz](https://finviz.com/quote.ashx?t=ZGN))

## 🛠️ Tech Stack

- **Python 3.12** + `yfinance` + `pandas` for the data layer
- **GitHub Actions** for scheduled daily refresh
- **Power BI Desktop** for the report authoring
- **Power BI Service** for hosting and scheduled dataset refresh

## ⚠️ Caveats & Limitations

- **Currency**: yfinance reports each company in its native reporting currency (EUR for Italian peers, USD for Zegna ADR). Direct revenue comparisons should be read with this in mind — the dashboard notes this explicitly.
- **Segment breakdown**: yfinance provides consolidated financials only. Segment data (ZEGNA brand / Thom Browne / Tom Ford) is sourced from the [FY2025 press release](https://www.businesswire.com/news/home/20260320107465/en/) and embedded as static callouts.
- **Not investment advice**: this project is a portfolio exercise, not a recommendation.

## 📚 Data Sources

- Financial data: [Yahoo Finance](https://finance.yahoo.com) via [yfinance](https://github.com/ranaroussi/yfinance)
- Company filings: [Zegna IR](https://ir.zegnagroup.com), [SEC EDGAR](https://www.sec.gov/edgar)
- Analyst data (manually curated): [Finviz](https://finviz.com/quote.ashx?t=ZGN)

## 👤 About

Built by Ilisa Habbasov as a Power BI portfolio project. I'm Head of Finance at Estro (ecommerce fashion), learning Power BI to deepen my analytics toolkit.

Connect with me on [LinkedIn](https://www.linkedin.com/in/YOUR_PROFILE/).

## 📄 License

MIT — feel free to fork, adapt, and build your own.
