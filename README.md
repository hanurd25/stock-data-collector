# stock-data-collector

Automated collection of stock price data using GitHub Actions and `yfinance`. Runs on a schedule, fetches minute-level price data for a configurable list of tickers across multiple exchanges, and commits the results as CSV files to this repo.

## How it works

- `.github/workflows/collect.yml` defines a scheduled GitHub Actions job (cron) that runs the collector automatically — no laptop or server needs to stay on.
- `scripts/fetch_prices.py` fetches 1-minute interval price data for each ticker via `yfinance` and saves it to `data/`.
- Each run commits its output CSV back to the repo, so data accumulates over time as a version-controlled history.


## Settings:
### Workflows

Workflow permissions

GitHub workflows needs
Read and write permissions 


## Repo structure

```
stock-data-collector/
├── .github/
│   └── workflows/
│       └── collect.yml       # schedule + CI steps
├── scripts/
│   └── fetch_prices.py       # the actual fetch logic
├── data/                     # CSVs land here (auto-committed)
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Push to GitHub via SSH (see [Authentication](#authentication) below if you hit issues).
3. In the GitHub repo, go to **Settings → Actions → General → Workflow permissions** and select **"Read and write permissions"** — this lets the workflow commit data back to the repo.
4. Go to the **Actions** tab and manually trigger the workflow once (`Run workflow`) to confirm it works before relying on the schedule.

## Adjustments

### Adding or removing tickers

Edit the `TICKERS` dictionary at the top of `scripts/fetch_prices.py`:

```python
TICKERS = {
    "ALFEN.AS": {"name": "Alfen N.V.", "exchange": "Euronext Amsterdam", "currency": "EUR"},
    "AAPL":     {"name": "Apple", "exchange": "Nasdaq", "currency": "USD"},
    # add a new ticker like this:
    "TSLA":     {"name": "Tesla", "exchange": "Nasdaq", "currency": "USD"},
}
```

To find the correct `yfinance` ticker symbol for a non-US stock, search the company on [finance.yahoo.com](https://finance.yahoo.com) and copy the symbol shown in the URL/quote page. Non-US exchanges typically need a suffix, e.g.:

| Exchange | Suffix | Example |
|---|---|---|
| Euronext Amsterdam | `.AS` | `ALFEN.AS` |
| Nasdaq Copenhagen | `.CO` | `NOVO-B.CO` |
| Nasdaq Stockholm | `.ST` | `AZA.ST` |
| NYSE / Nasdaq (US) | none | `AAPL`, `JPM` |

After editing, commit and push:
```bash
git add scripts/fetch_prices.py
git commit -m "Add TSLA to ticker list"
git push
```

### Adjusting the collection schedule

Edit the `cron` line in `.github/workflows/collect.yml`:



```yaml
# Can stop by commenting out the sceduele
# Excamples on sceduele:

on:
 schedule:
    - #
  # Every 5 minutes, 07:00-20:00 UTC, weekdays — very high density, ~1560 runs/month
  #- cron: "*/5 7-20 * * 1-5"
  # Every 10 minutes, 07:00-20:00 UTC, weekdays — high density, ~780 runs/month
  #- cron: "*/10 7-20 * * 1-5"
  # Every 15 minutes, 07:00-20:00 UTC, weekdays — moderate-high density, ~520 runs/month
  #- cron: "*/15 7-20 * * 1-5"  
  # Every 30 minutes, 07:00-20:00 UTC, weekdays — current setting, ~560 runs/month
  #- cron: "*/30 7-20 * * 1-5"
  # Once per hour, 07:00-20:00 UTC, weekdays — low density, ~280 runs/month
  #- cron: "0 7-20 * * 1-5"
  # Twice a day (market open + close snapshot), weekdays — minimal, ~40 runs/month
  #- cron: "0 7,20 * * 1-5"
  # Once per day at market close (20:00 UTC), weekdays — daily closing price only
  #- cron: "0 20 * * 1-5"
  # European session only, every 30 min, weekdays (excludes US market hours)
  #- cron: "*/30 7-15 * * 1-5"
  # US session only, every 30 min, weekdays (excludes European market hours)
  #- cron: "*/30 13-20 * * 1-5"
  # Every 30 min, all 7 days (in case you ever add crypto or 24/7 assets)
  #- cron: "*/30 7-20 * * *"
   - cron: "*/30 7-20 * * 1-5"
 workflow_dispatch:
```

Cron format: `minute hour day month day-of-week`, all in **UTC**. Some examples:

| Goal | Cron |
|---|---|
| Every 15 minutes, 07:00–20:00 UTC, weekdays | `*/15 7-20 * * 1-5` |
| Once per hour, weekdays | `0 7-20 * * 1-5` |
| Every 5 minutes (higher density, watch GitHub Actions usage limits) | `*/5 7-20 * * 1-5` |

Note: UTC market-hour windows shift slightly around daylight saving transitions in March/October, since US and EU clocks don't change on the same dates.

### Changing data frequency/resolution

`yf.download(ticker, period="1d", interval="1m", ...)` — the `interval` parameter controls resolution. Valid values include `1m`, `5m`, `15m`, `1h`, `1d`. Note: Yahoo Finance only retains `1m` data for the past ~7 days, so 1-minute historical backfill beyond that isn't possible via this method — the value of this pipeline is in accumulating your *own* history going forward, not backfilling.

### Adding more markets/timezones

If you add tickers from a new exchange, check that its trading hours fall within the workflow's cron window (currently `7-20` UTC, covering European + US sessions). If not, widen the range in `collect.yml`.

### Switching storage from CSV to a database

For higher ticker counts or longer retention, flat CSVs in `data/` become unwieldy. Consider migrating to a time-series database (e.g. TimescaleDB, InfluxDB, or a hosted Postgres like Supabase) — this would mean replacing the `combined.to_csv(...)` line in `fetch_prices.py` with a database insert, and storing connection credentials as a GitHub Actions secret (**Settings → Secrets and variables → Actions**) rather than in code.


## License

Personal research project — no license specified.