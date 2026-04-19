# LinkedIn Post — Ready to Use

Three versions at different lengths. Pick one, tweak the voice to match yours, and post.

---

## Version 1 — Short & punchy (best for engagement)

```
I've been learning Power BI and wanted to build something that combines my
finance day-job with the new skillset.

So I built an investor-style dashboard benchmarking Ermenegildo Zegna Group
against its Italian luxury peer group — Brunello Cucinelli, Moncler, Prada,
Ferragamo, and Hugo Boss.

What makes it different from most Power BI portfolio projects:

→ Fully automated data pipeline (Python + yfinance + GitHub Actions)
→ Refreshes daily — the numbers you see are always current
→ Real analytical thesis, not just charts: is Zegna mispriced vs. peers?
→ 5 pages: exec summary, company deep-dive, peer benchmarking,
  stock & valuation, investment thesis

Key finding: Zegna's FY2025 profit grew 20% YoY despite a 1.5% revenue
decline — pure margin expansion driven by DTC channel mix (now 82% of
branded revenues). The balance sheet also flipped from €94M net debt to
€52M net cash in a single year.

Full project (code + build guide + dashboard) on GitHub:
[link]

Live dashboard:
[link]

Open to feedback from anyone who's deeper in BI / equity research —
especially on the DAX model and benchmarking approach.

#PowerBI #DataAnalytics #Finance #Luxury #DataVisualization
```

---

## Version 2 — Longer / storytelling (best for senior hiring signal)

```
When I started learning Power BI a few weeks ago, I didn't want to build
another generic sales dashboard. I wanted something that would show both
the technical skill and the finance brain I use every day as Head of
Finance at Estro.

So I built this: an investor-style dashboard that benchmarks Ermenegildo
Zegna Group (NYSE: ZGN) against its European luxury peers.

Why Zegna? Because it's a fascinating analytical story:
• Profit +20% YoY on flat revenue → textbook margin expansion
• DTC now 82% of branded revenues (up from 78%) → channel shift in action
• Balance sheet swung from €94M net debt to €52M net cash in one year
• Thom Browne revenue down 14.7% while Tom Ford is growing
• Analysts are split: UBS upgrade to Buy, BofA downgrade to Neutral

Stack:
• Python + yfinance pulls income statement, balance sheet, cash flow,
  and 5 years of daily prices for all 6 companies
• GitHub Actions runs the script daily at 06:00 UTC
• CSVs commit back to the repo
• Power BI Service pulls from the raw GitHub URLs on scheduled refresh
• Dashboard updates every morning without me touching anything

Dashboard covers:
1. Executive summary with peer-rank KPIs
2. Zegna deep-dive — P&L waterfall, margins, cash flow
3. Side-by-side peer benchmarking across growth, margins, valuation
4. Stock performance (5Y normalized) and valuation multiples
5. Investment thesis — my take on whether Zegna is undervalued

Everything is open source — code, build guide, DAX measures, the .pbix
file. If you're also learning Power BI or coming from a finance
background, feel free to fork it and adapt.

GitHub: [link]
Live dashboard: [link]

Curious to hear from people in BI, equity research, or luxury — what
would you add or do differently?

#PowerBI #DataAnalytics #EquityResearch #Finance #LuxuryIndustry
```

---

## Version 3 — Very short (best for busy feeds)

```
Built a Power BI dashboard benchmarking Zegna vs. its luxury peers
(Cucinelli, Moncler, Prada, Ferragamo, Hugo Boss).

Data refreshes daily via a Python + GitHub Actions pipeline, so the
numbers are always current — no manual updates.

Shows where Zegna sits on growth, margins, valuation, and stock
performance vs. the peer group, plus my own investment thesis on whether
it's mispriced.

Code + build guide + live dashboard → [link]

Feedback welcome.

#PowerBI #Finance #DataAnalytics
```

---

## Posting tips

**Timing**: Tuesday-Thursday, 8-10am CET gets the strongest engagement for finance/BI audiences.

**Visuals matter more than text**: attach 2-3 dashboard screenshots (Executive Summary, Peer Benchmarking, Stock Valuation). LinkedIn's algorithm heavily favors posts with images.

**First comment**: Immediately comment on your own post with the links (GitHub + live dashboard). LinkedIn suppresses external links in the main post but doesn't penalize them in comments.

**Engagement hack**: ask a specific question at the end (Version 1 and 2 do this). Posts that generate comments get shown to more people.

**Tag sparingly**: if you want to tag companies or people, keep it to 1-2 max. Over-tagging looks spammy.

**Hashtags**: 3-5 is the sweet spot. Too few = no discoverability; too many = algorithm flags as spam.

---

## Follow-up posts (after initial announcement)

If the first post lands well, these follow-ups keep you in the feed:

1. **1 week later**: "Most interesting insight I found building the dashboard — Zegna's DTC shift" (zoom in on one analytical finding with a chart)
2. **2 weeks later**: "The 5 DAX measures that did 80% of the analytical lifting" (technical, appeals to BI practitioners)
3. **3 weeks later**: "Why I used Python + GitHub Actions instead of just importing CSVs manually" (architecture post, appeals to data engineers)
4. **1 month later**: "Update: here's what the dashboard shows after Q1 2026 earnings" (evergreen hook — always something new)

Each of these works as a mini-post with 1 chart + 150-200 words. Rinse and repeat.
