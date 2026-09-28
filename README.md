# kz-inflation-tracker

Tracking real food prices in Shymkent vs official CPI (stat.gov.kz).

## Research question

Do everyday grocery prices in Shymkent move the way official inflation statistics say they do?

## How it works

1. `scraper.py` collects prices of every product in a Shymkent supermarket's online catalog (via Glovo) once a day.
2. GitHub Actions runs it automatically at 09:17 Shymkent time. No computer needs to be on.
3. Each run adds rows to [`data/prices.csv`](data/prices.csv):

| column | meaning |
|---|---|
| date | collection date (Shymkent time) |
| store | store name |
| product_id | stable product ID in the catalog |
| name | product name as listed |
| price_kzt | price in tenge |
| subcategory | store's category (e.g. Молоко) |
| out_of_stock | product unavailable that day |
| on_promo | product on promotion that day |

## Planned

- Match products to official CPI categories (food basket of stat.gov.kz)
- Build a daily price index and compare it to the official monthly CPI for Shymkent
- Dashboard + short research note on methodology and findings

## Limitations

- Online delivery prices can differ from shelf prices; the index tracks *changes*, not levels.
- One store is not the whole city; more stores will be added.

Data is collected for non-commercial student research.
