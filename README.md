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

## Dashboard

`app.py` is a Streamlit site (Russian / English) that shows:

- a daily food price index built from `data/prices.csv` (chained geometric mean of day-to-day price changes)
- price charts for every product
- a comparison with the official monthly CPI for Shymkent (`data/official_cpi.csv`, food products)
- auto-generated key findings

Run it locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Refresh official statistics (stat.gov.kz publishes at the start of each month):

```bash
python update_official_cpi.py
```

## Planned

- Match products to official CPI categories (food basket of stat.gov.kz) and weight them
- Add more stores

## Limitations

- Online delivery prices can differ from shelf prices; the index tracks *changes*, not levels.
- One store is not the whole city; more stores will be added.

Data is collected for non-commercial student research.
