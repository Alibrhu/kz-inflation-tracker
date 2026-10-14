"""
Downloads the official monthly CPI for Shymkent from stat.gov.kz and saves it
to data/official_cpi.csv:
    month, category, index_mom

index_mom = price index vs previous month, in percent (100.4 means +0.4%).
category  = all | food | nonfood | services

Run once a month (stat.gov.kz publishes around the 1st-3rd):
    python update_official_cpi.py
"""

import csv
import io
from pathlib import Path

import openpyxl
import requests

# "Индекс цен на потребительские товары и услуги", г. Шымкент, monthly table
# from https://stat.gov.kz/ru/region/shymkent/dynamic-tables/37/
URL = "https://stat.gov.kz/api/iblock/element/region/42742/file/ru/"
OUT_FILE = Path(__file__).parent / "data" / "official_cpi.csv"

SECTIONS = {
    "Товары и услуги": "all",
    "Продовольственные товары": "food",
    "Непродовольственные товары": "nonfood",
    "Платные услуги": "services",
}


def main() -> None:
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    ws = openpyxl.load_workbook(io.BytesIO(r.content), data_only=True)["ИПЦ"]

    rows, category = [], None
    for cells in ws.iter_rows(values_only=True):
        first = cells[0]
        if isinstance(first, str) and first.strip() in SECTIONS:
            category = SECTIONS[first.strip()]
        elif category and isinstance(first, int):
            for m, value in enumerate(cells[1:13], start=1):
                if isinstance(value, (int, float)):
                    rows.append({"month": f"{first}-{m:02d}", "category": category,
                                 "index_mom": value})

    if not rows:
        raise SystemExit("Nothing parsed: stat.gov.kz may have changed the table layout")
    with OUT_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["month", "category", "index_mom"])
        w.writeheader()
        w.writerows(rows)
    print(f"Saved {len(rows)} rows to {OUT_FILE} (latest: {rows[-1]['month']})")


if __name__ == "__main__":
    main()
