"""
Daily price collector for Shymkent grocery stores (via Glovo's public web catalog).

Each run appends one row per product to data/prices.csv:
    date, store, product_id, name, price_kzt, subcategory, out_of_stock, on_promo

Run locally:   python scraper.py
Run daily:     GitHub Actions (.github/workflows/daily.yml)
"""

import csv
import json
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

# ---------------------------------------------------------------- settings --

# Shymkent stores on Glovo. store_id / address_id come from the store page's
# network requests (api.glovoapp.com/v4/stores/<store_id>/addresses/<address_id>/...).
STORES = [
    {"name": "MaxMarket", "store_id": 366797, "address_id": 543199},
]

CITY_CODE = "CIT"  # Glovo's code for Shymkent
API = "https://api.glovoapp.com"
HEADERS = {
    "glovo-location-city-code": CITY_CODE,
    "glovo-app-platform": "web",
    "glovo-language-code": "ru",
    "User-Agent": "kz-inflation-tracker (student research project; github.com/Alibrhu/kz-inflation-tracker)",
    "Accept": "application/json",
}
PAUSE_SECONDS = 1.0  # be polite: one request per second
OUT_FILE = Path(__file__).parent / "data" / "prices.csv"
FIELDS = ["date", "store", "product_id", "name", "price_kzt",
          "subcategory", "out_of_stock", "on_promo"]

SHYMKENT_TZ = timezone(timedelta(hours=5))

# ------------------------------------------------------------------- logic --

session = requests.Session()
session.headers.update(HEADERS)


def get_json(path: str) -> dict:
    """GET an API path like /v4/stores/... and return parsed JSON."""
    time.sleep(PAUSE_SECONDS)
    r = session.get(API + path, timeout=30)
    r.raise_for_status()
    # parse_int=str keeps huge numeric IDs exact
    return json.loads(r.text, parse_int=str)


def find_tiles(node, out: list) -> None:
    """Recursively collect every PRODUCT_TILE's data dict."""
    if isinstance(node, dict):
        if node.get("type") == "PRODUCT_TILE" and isinstance(node.get("data"), dict):
            out.append(node["data"])
        for v in node.values():
            find_tiles(v, out)
    elif isinstance(node, list):
        for v in node:
            find_tiles(v, out)


def find_placeholders(node, out: list) -> None:
    """Collect contentUri of lazy-loaded sections (CONTENT_PLACEHOLDER)."""
    if isinstance(node, dict):
        if node.get("type") == "CONTENT_PLACEHOLDER":
            uri = (node.get("data") or {}).get("contentUri")
            if uri:
                out.append(uri)
        for v in node.values():
            find_placeholders(v, out)
    elif isinstance(node, list):
        for v in node:
            find_placeholders(v, out)


def category_paths(root: dict) -> list:
    """All 'parent-sc.123/child-c.456' category links in the store menu."""
    text = json.dumps(root, ensure_ascii=False)
    return sorted(set(re.findall(r"([a-z0-9-]+-sc\.\d+/[a-z0-9-]+-c\.\d+)", text)))


def scrape_store(store: dict) -> list:
    base = f"/v4/stores/{store['store_id']}/addresses/{store['address_id']}/content"
    root = get_json(base + "/main")
    paths = category_paths(root)
    print(f"[{store['name']}] {len(paths)} categories")

    products = {}
    for p in paths:
        try:
            page = get_json(f"{base}/main?nodeType=DEEP_LINK&link={requests.utils.quote(p, safe='')}")
        except requests.RequestException as e:
            print(f"  ! skip {p}: {e}")
            continue
        tiles, lazy = [], []
        find_tiles(page, tiles)
        find_placeholders(page, lazy)
        for uri in lazy:
            try:
                find_tiles(get_json(uri), tiles)
            except requests.RequestException as e:
                print(f"  ! skip section {uri}: {e}")
        for t in tiles:
            pid = str(t.get("externalId") or t.get("storeProductId") or t.get("id"))
            products[pid] = t  # dedupe: same product can appear in several categories

    today = datetime.now(SHYMKENT_TZ).strftime("%Y-%m-%d")
    rows = []
    for pid, t in products.items():
        price = t.get("price")
        if price in (None, ""):
            continue
        rows.append({
            "date": today,
            "store": store["name"],
            "product_id": pid,
            "name": " ".join(str(t.get("name", "")).split()),
            "price_kzt": price,
            "subcategory": (t.get("tracking") or {}).get("subCategory", ""),
            "out_of_stock": bool(t.get("outOfStock")),
            "on_promo": bool(t.get("promotions")),
        })
    print(f"[{store['name']}] {len(rows)} products")
    return rows


def already_collected(today: str) -> set:
    """Stores that already have rows for today (so re-runs don't duplicate)."""
    if not OUT_FILE.exists():
        return set()
    with OUT_FILE.open(encoding="utf-8") as f:
        return {r["store"] for r in csv.DictReader(f) if r["date"] == today}


def save(rows: list) -> None:
    OUT_FILE.parent.mkdir(exist_ok=True)
    new_file = not OUT_FILE.exists()
    with OUT_FILE.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        w.writerows(rows)


def main() -> int:
    today = datetime.now(SHYMKENT_TZ).strftime("%Y-%m-%d")
    done = already_collected(today)
    total = 0
    for store in STORES:
        if store["name"] in done:
            print(f"[{store['name']}] already collected today, skipping")
            continue
        try:
            rows = scrape_store(store)
        except requests.RequestException as e:
            print(f"[{store['name']}] FAILED: {e}")
            continue
        save(rows)
        total += len(rows)
    print(f"Saved {total} rows to {OUT_FILE}")
    # Fail loudly if nothing was collected and nothing was already there,
    # so GitHub emails you instead of silently saving nothing.
    return 0 if (total or done) else 1


if __name__ == "__main__":
    sys.exit(main())
