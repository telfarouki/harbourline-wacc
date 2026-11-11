# Harbourline WACC — weekly reference-data file

One file per week: `weekly/<ISO year>-W<ISO week>.json`. It holds the inputs the WACC engine otherwise has to look up
on every query. Countries are keyed by the ISO3 codes of `countries.js` (96 countries) — use only those codes.

```json
{
  "week": "2026-W46",
  "as_of": "2026-11-14",                      // date of the run, YYYY-MM-DD
  "global": {
    "us10y_pct": 4.21,                        // US 10-year Treasury yield (FRED DGS10), latest daily value
    "us10y_date": "2026-11-12",
    "us10y_source_url": "https://fred.stlouisfed.org/series/DGS10",
    "damodaran_update": "July 2026",          // date shown on Damodaran's country risk premium page
    "mature_erp_pct": 4.3,                    // Damodaran implied ERP for a mature market, same page
    "damodaran_source_url": "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html"
  },
  "countries": {
    "AGO": {
      "ratings": {                            // long-term foreign-currency sovereign rating; null when the agency does not rate
        "moodys": { "rating": "B3",  "outlook": "stable", "as_of": "2025-11-21", "source_url": "https://..." },
        "sp":     { "rating": "B-",  "outlook": "stable", "as_of": "2025-08-08", "source_url": "https://..." },
        "fitch":  { "rating": "B-",  "outlook": "stable", "as_of": "2025-06-13", "source_url": "https://..." }
      },
      "corporate_tax_pct": 25,                // standard corporate income tax rate
      "tax_source_url": "https://taxsummaries.pwc.com/angola/corporate/taxes-on-corporate-income",
      "eurobond": {                           // most liquid USD sovereign bond near 10 years; null if none trades
        "yield_pct": 9.9, "instrument": "Angola 8.75% 2032 USD", "as_of": "2026-11-12", "source_url": "https://..."
      },
      "project_spread_pct": 3.0,              // documented margin over the sovereign for infrastructure/project loans; null if nothing documented
      "project_spread_basis": "one sentence on the transaction or lender the figure comes from",
      "project_spread_source_url": "https://...",
      "checked": "2026-11-14",                // last date this country was verified
      "note": ""                              // e.g. "in default", "unrated — agent equivalent CCC", sanctions, missing data
    }
  },
  "changes": [                                 // what moved since the previous weekly file
    { "iso3": "AGO", "what": "Fitch revised outlook to positive", "date": "2026-11-10", "source_url": "https://..." }
  ]
}
```

## Rules
- Outlook is one of `positive`, `stable`, `negative`, `watch`, or `null`.
- Percentages are plain numbers (25, not 0.25 and not "25%").
- Every figure needs a real `source_url` actually fetched or seen in search results. Prefer primary sources: the rating
  agencies, finance ministries / debt offices, central banks, PwC Worldwide Tax Summaries, KPMG, EY, IMF, World Bank,
  exchange or official bond data. Secondary aggregators (tradingeconomics, cbonds, countryeconomy) are acceptable for
  ratings and yields only when no primary page is reachable.
- Never invent a number. Unknown = `null`, with a word in `note`.
- All 96 countries of `countries.js` must be present every week. A country with nothing new keeps last week's values
  and its old `checked` date.
