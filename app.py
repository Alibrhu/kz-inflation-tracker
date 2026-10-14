"""
Website (Streamlit dashboard) for kz-inflation-tracker.

Run locally:   streamlit run app.py
Texts in both languages live in i18n.py.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import ui
from i18n import LANGUAGES, MONTHS, TEXTS

DATA_DIR = Path(__file__).parent / "data"
PRICES_FILE = DATA_DIR / "prices.csv"
OFFICIAL_FILE = DATA_DIR / "official_cpi.csv"
REPO_URL = "https://github.com/Alibrhu/kz-inflation-tracker"

# Store subcategories that are not food. They are excluded from the food index.
NON_FOOD = {
    "Для ванной и туалетов", "Прокладки и тампоны", "Ручки, карандаши, фломастеры, замазки",
    "Шампуни", "Игрушки", "Корм для кошек", "Порошки и гели", "Зубная паста",
    "Гели, муссы для душа", "Зубные щетки и аксессуары", "Бальзамы, кондиционеры, маски",
    "Дезодоранты и антиперспиранты", "Подгузники", "Ватные диски и палочки",
    "Кондиционеры, ополаскиватели", "Влажные салфетки", "Капсулы для стирки",
    "Топ недели",  # store's promo shelf, mixes everything
}

MIN_DAYS_RELIABLE = 60    # below this the findings carry a "preliminary" warning
MIN_DAYS_PER_MONTH = 15   # a month needs this many days to get its own monthly point
MAX_DAILY_JUMP = 3.0      # price ×3 or ÷3 in one day is treated as a data error / pack change
MIN_CATEGORY_PRODUCTS = 3

BLUE, ORANGE = "#2a78d6", "#eb6834"  # "our data" vs "official", same in every chart
CHART_CONFIG = {"displayModeBar": False}
# colorblind-safe order for several products on one chart
PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]


# ------------------------------------------------------------------ data --

@st.cache_data(ttl=3600)
def load_prices() -> pd.DataFrame:
    if not PRICES_FILE.exists():
        return pd.DataFrame()
    df = pd.read_csv(PRICES_FILE, dtype={"product_id": str})
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["subcategory"] = df["subcategory"].fillna("").str.strip()
    df["is_food"] = ~df["subcategory"].isin(NON_FOOD)
    return df.drop_duplicates(["date", "store", "product_id"], keep="last")


@st.cache_data(ttl=3600)
def load_official() -> pd.DataFrame:
    if not OFFICIAL_FILE.exists():
        return pd.DataFrame()
    df = pd.read_csv(OFFICIAL_FILE)
    df["month"] = pd.PeriodIndex(df["month"], freq="M")
    return df.pivot(index="month", columns="category", values="index_mom").sort_index()


def wide_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Table: one row per day, one column per product, in-stock prices only."""
    in_stock = df[~df["out_of_stock"] & (df["price_kzt"] > 0)]
    return in_stock.pivot_table(index="date", columns="product_id", values="price_kzt", aggfunc="last")


def chain_index(wide: pd.DataFrame) -> pd.Series:
    """Chained Jevons index: geometric mean of day-to-day price ratios, 100 on day one."""
    ratios = wide / wide.shift(1)
    ratios = ratios.where((ratios < MAX_DAILY_JUMP) & (ratios > 1 / MAX_DAILY_JUMP))
    daily = np.exp(np.log(ratios).mean(axis=1, skipna=True)).fillna(1.0)
    daily.iloc[0] = 1.0
    return 100 * daily.cumprod()


@st.cache_data(ttl=3600)
def compute(df: pd.DataFrame) -> dict:
    food = df[df["is_food"]]
    wide = wide_prices(food)
    index = chain_index(wide)

    # category indices (only categories with enough products present on the first and last day)
    cats = {}
    for cat, g in food.groupby("subcategory"):
        w = wide_prices(g)
        if len(w) >= 2 and w.iloc[[0, -1]].notna().all().sum() >= MIN_CATEGORY_PRODUCTS:
            cats[cat] = chain_index(w).iloc[-1] - 100
    cat_change = pd.Series(cats, dtype=float).sort_values()

    # share of products whose price changed at least once
    seen_twice = wide.loc[:, wide.notna().sum() >= 2]
    changed = (seen_twice.nunique() > 1).mean() if not seen_twice.empty else 0.0

    # monthly change of our index (average index level per month)
    by_month = index.groupby(index.index.to_period("M")).agg(["mean", "count"])
    full = by_month[by_month["count"] >= MIN_DAYS_PER_MONTH]
    prev = by_month["mean"].shift(1)
    prev_ok = by_month["count"].shift(1) >= MIN_DAYS_PER_MONTH
    monthly = ((by_month["mean"] / prev - 1) * 100)[prev_ok].reindex(full.index).dropna()

    return {"index": index, "cat_change": cat_change, "changed_share": changed, "monthly": monthly}


# --------------------------------------------------------------- helpers --

def pct(x: float, lang: str, signed: bool = True, digits: int = 1) -> str:
    s = f"{x:+.{digits}f}%" if signed else f"{x:.{digits}f}%"
    s = s.replace("-", "−")
    return s if lang == "en" else s.replace(".", ",")  # ru/kk use a decimal comma


def month_label(p: pd.Period, lang: str) -> str:
    return f"{MONTHS[lang][p.month - 1]} {p.year}"


def day_label(d: pd.Timestamp, lang: str) -> str:
    return f"{d.day} {MONTHS[lang][d.month - 1]}"


def style(fig: go.Figure, y_title: str, height: int = 380) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=8, b=8), hovermode="x unified", colorway=PALETTE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title=y_title, xaxis_title=None,
    )
    fig.update_xaxes(showgrid=False)
    return fig


def official_yoy(official: pd.DataFrame, col: str) -> pd.Series:
    """12-month inflation (%) from monthly indices."""
    return ((official[col] / 100).rolling(12).apply(np.prod, raw=True) - 1) * 100


# ------------------------------------------------------------------ page --

st.set_page_config(page_title="Shymkent inflation tracker", page_icon="🛒", layout="wide")

st.markdown(ui.CSS, unsafe_allow_html=True)

_, lang_col = st.columns([3, 2])
with lang_col:
    lang_label = st.segmented_control(
        "Language", list(LANGUAGES), default=next(iter(LANGUAGES)),
        label_visibility="collapsed", key="lang_choice",
    )
lang = LANGUAGES.get(lang_label, "kk")
T = TEXTS[lang]

prices = load_prices()
official = load_official()

if prices.empty:
    st.markdown(ui.hero(T["title"], T["subtitle"], T["badge"], ""), unsafe_allow_html=True)
    st.info(T["no_data"])
    st.stop()

stores = ", ".join(sorted(prices["store"].unique()))
last_day = prices["date"].max()
meta = T["updated"].format(date=day_label(last_day, lang) + f" {last_day.year}", stores=stores)
st.markdown(ui.hero(T["title"], T["subtitle"], T["badge"], meta), unsafe_allow_html=True)

n_days = prices["date"].nunique()
if n_days < 2:
    st.info(T["too_little_data"])
    st.stop()

res = compute(prices)
index = res["index"]
real_change = index.iloc[-1] - 100
days_span = (index.index[-1] - index.index[0]).days

has_official = not official.empty
if has_official:
    food_yoy = official_yoy(official, "food").dropna()
    latest_month = food_yoy.index[-1]
    yoy_rate = food_yoy.iloc[-1]
    daily_rate = (1 + yoy_rate / 100) ** (1 / 365)
    expected = (daily_rate ** days_span - 1) * 100

tab_overview, tab_prices, tab_compare, tab_method = st.tabs(
    [T["tab_overview"], T["tab_prices"], T["tab_compare"], T["tab_method"]]
)

# ------------------------------------------------------------- overview --
with tab_overview:
    cards = [
        ("📅", T["kpi_days"], n_days, T["kpi_days_sub"].format(start=day_label(index.index[0], lang)), "#00a3c4"),
        ("🛒", T["kpi_products"], int((prices["date"] == last_day).sum()), stores, "#0b4f7c"),
        ("📈", T["kpi_real"], pct(real_change, lang),
         T["kpi_real_help"].format(start=day_label(index.index[0], lang)), BLUE),
    ]
    if has_official:
        cards.append(("🏛️", T["kpi_official_yoy"], pct(yoy_rate, lang),
                      T["kpi_official_yoy_help"].format(month=month_label(latest_month, lang)), "#f2b705"))
    st.markdown(ui.kpi_cards(cards), unsafe_allow_html=True)

    chart_col, text_col = st.columns([3, 2], gap="large")

    with chart_col:
        st.markdown(ui.section(T["index_title"]), unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_scatter(x=index.index, y=index.values, name=T["series_real"], mode="lines+markers",
                        line=dict(color=BLUE, width=2), marker=dict(size=7),
                        hovertemplate="%{y:.2f}<extra></extra>")
        if has_official:
            pace = 100 * daily_rate ** (index.index - index.index[0]).days
            fig.add_scatter(x=index.index, y=pace, name=T["series_official_pace"].format(rate=pct(yoy_rate, lang, False)),
                            mode="lines", line=dict(color=ORANGE, width=2, dash="dash"),
                            hovertemplate="%{y:.2f}<extra></extra>")
        fig.add_hline(y=100, line_width=1, line_color="rgba(128,128,128,0.5)")
        fig.update_xaxes(tickformat="%d.%m")
        st.plotly_chart(style(fig, T["index_axis"]), use_container_width=True, config=CHART_CONFIG)
        st.caption(T["index_caption"])

    with text_col:
        st.markdown(ui.section(T["findings"]), unsafe_allow_html=True)
        notes = []
        if has_official:
            notes.append(T["f_change"].format(days=days_span, real=pct(real_change, lang),
                                              rate=pct(yoy_rate, lang, False), expected=pct(expected, lang)))
            gap = real_change - expected
            notes.append(T["f_same"] if abs(gap) < 0.3 else T["f_faster"] if gap > 0 else T["f_slower"])
        notes.append(T["f_changed_share"].format(share=pct(res["changed_share"] * 100, lang, False, 0)))
        cat_change = res["cat_change"]
        ups = cat_change[cat_change > 0].sort_values(ascending=False).head(3)
        downs = cat_change[cat_change < 0].head(3)
        if not ups.empty:
            notes.append(T["f_up"].format(items=", ".join(f"{c} ({pct(v, lang)})" for c, v in ups.items())))
        if not downs.empty:
            notes.append(T["f_down"].format(items=", ".join(f"{c} ({pct(v, lang)})" for c, v in downs.items())))
        monthly = res["monthly"]
        if has_official and not monthly.empty:
            m = monthly.index[-1]
            if m in official.index:
                notes.append(T["f_monthly"].format(month=month_label(m, lang), real=pct(monthly.iloc[-1], lang),
                                                   official=pct(official.loc[m, "food"] - 100, lang)))
        else:
            notes.append(T["f_monthly_wait"])
        caveat = T["f_caveat"].format(min_days=MIN_DAYS_RELIABLE) if n_days < MIN_DAYS_RELIABLE else ""
        st.markdown(ui.findings(notes, caveat), unsafe_allow_html=True)

    if (cat_change.abs() >= 0.05).any():
        st.markdown(ui.section(T["cat_chart_title"]), unsafe_allow_html=True)
        moved = cat_change[cat_change.abs() >= 0.05]
        shown = pd.concat([moved.head(8), moved.tail(8)])
        shown = shown[~shown.index.duplicated()].sort_values()
        fig = go.Figure(go.Bar(
            x=shown.values, y=shown.index, orientation="h",
            marker=dict(color=[ORANGE if v > 0 else BLUE for v in shown.values], cornerradius=4),
            hovertemplate="%{y}: %{x:+.1f}%<extra></extra>",
        ))
        fig.add_vline(x=0, line_width=1, line_color="rgba(128,128,128,0.6)")
        fig.update_layout(hovermode="closest", bargap=0.35)
        fig.update_xaxes(ticksuffix="%", showgrid=True)
        st.plotly_chart(style(fig, None, height=max(300, 26 * len(shown))), use_container_width=True, config=CHART_CONFIG)
        st.caption(T["cat_chart_caption"].format(n=MIN_CATEGORY_PRODUCTS))

# --------------------------------------------------------------- prices --
with tab_prices:
    st.markdown(T["prices_intro"])
    show_nonfood = st.toggle(T["show_nonfood"], value=False)
    pool = prices if show_nonfood else prices[prices["is_food"]]

    c1, c2 = st.columns([1, 2])
    cats = sorted(pool["subcategory"].unique())
    cat = c1.selectbox(T["category"], [T["all_food"]] + cats)
    in_cat = pool if cat == T["all_food"] else pool[pool["subcategory"] == cat]

    # latest name per product; most frequently seen products first
    names = in_cat.sort_values("date").groupby("product_id")["name"].last()
    order = in_cat["product_id"].value_counts().index
    names = names.reindex(order)
    first_last = in_cat[~in_cat["out_of_stock"]].sort_values("date").groupby("product_id")["price_kzt"].agg(["first", "last"])
    biggest = (first_last["last"] / first_last["first"] - 1).abs().sort_values(ascending=False)
    picked = c2.multiselect(T["products"], names.index, default=list(biggest.index[:3]), max_selections=8,
                            format_func=lambda pid: names[pid], help=T["products_help"],
                            placeholder=T["products_placeholder"], key=f"picked_{cat}")

    if picked:
        fig = go.Figure()
        for i, pid in enumerate(picked):
            g = in_cat[(in_cat["product_id"] == pid) & ~in_cat["out_of_stock"]].sort_values("date")
            fig.add_scatter(x=g["date"], y=g["price_kzt"], name=names[pid], mode="lines+markers",
                            line=dict(width=2, shape="hv"), marker=dict(size=7),
                            hovertemplate="%{y:,.0f} ₸<extra>" + names[pid][:40] + "</extra>")
        fig.update_xaxes(tickformat="%d.%m")
        fig.update_yaxes(tickformat=",.0f")
        st.plotly_chart(style(fig, T["price_axis"], height=420), use_container_width=True, config=CHART_CONFIG)
    else:
        st.info(T["pick_products"])

    st.markdown(ui.section(T["movers_title"]), unsafe_allow_html=True)
    st.caption(T["movers_caption"])
    in_stock = in_cat[~in_cat["out_of_stock"]].sort_values("date")
    g = in_stock.groupby("product_id")
    movers = pd.DataFrame({
        T["col_product"]: g["name"].last(),
        T["col_category"]: g["subcategory"].last(),
        T["col_first"]: g["price_kzt"].first(),
        T["col_last"]: g["price_kzt"].last(),
    })
    movers[T["col_change"]] = (movers[T["col_last"]] / movers[T["col_first"]] - 1) * 100
    movers = movers[movers[T["col_change"]].abs() > 0.01]
    movers = movers.reindex(movers[T["col_change"]].abs().sort_values(ascending=False).index)
    st.dataframe(
        movers.head(50), hide_index=True, use_container_width=True,
        column_config={
            T["col_first"]: st.column_config.NumberColumn(format="%.0f"),
            T["col_last"]: st.column_config.NumberColumn(format="%.0f"),
            T["col_change"]: st.column_config.NumberColumn(format="%+.1f%%"),
        },
    )

# -------------------------------------------------------------- compare --
with tab_compare:
    if not has_official:
        st.warning(T["no_official"])
    else:
        st.markdown(T["compare_intro"])
        monthly = res["monthly"]
        recent = official.loc[official.index >= official.index[-1] - 23]
        months = recent.index.union(monthly.index)
        labels = [month_label(m, lang) for m in months]

        st.markdown(ui.section(T["compare_title"]), unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_scatter(x=labels, y=(recent["food"].reindex(months) - 100).values, name=T["series_official"],
                        mode="lines+markers", line=dict(color=ORANGE, width=2), marker=dict(size=8),
                        hovertemplate="%{y:+.1f}%<extra></extra>")
        if not monthly.empty:
            fig.add_scatter(x=labels, y=monthly.reindex(months).values, name=T["series_real_monthly"],
                            mode="markers", marker=dict(color=BLUE, size=12, line=dict(width=2, color="white")),
                            hovertemplate="%{y:+.1f}%<extra></extra>")
        fig.add_hline(y=0, line_width=1, line_color="rgba(128,128,128,0.6)")
        fig.update_yaxes(ticksuffix="%")
        fig.update_xaxes(tickangle=0, tickvals=labels[::3])
        st.plotly_chart(style(fig, T["monthly_axis"]), use_container_width=True, config=CHART_CONFIG)
        if monthly.empty:
            st.info(T["compare_wait"].format(n=MIN_DAYS_PER_MONTH))
        st.caption(T["official_source"])

        with st.expander(T["compare_table"]):
            table = pd.DataFrame({
                T["col_month"]: labels,
                T["col_official"]: (recent["food"].reindex(months) - 100).round(1).values,
                T["col_real"]: monthly.reindex(months).round(1).values,
            }).iloc[::-1]
            st.dataframe(table, hide_index=True, use_container_width=True,
                         column_config={c: st.column_config.NumberColumn(format="%+.1f%%")
                                        for c in (T["col_official"], T["col_real"])})

        st.markdown(ui.section(T["yoy_title"]), unsafe_allow_html=True)
        yoy = pd.DataFrame({"food": official_yoy(official, "food"), "all": official_yoy(official, "all")}).dropna()
        yoy = yoy[yoy.index >= yoy.index[-1] - 35]
        x = [month_label(m, lang) for m in yoy.index]
        fig = go.Figure()
        fig.add_scatter(x=x, y=yoy["food"], name=T["series_food"], mode="lines",
                        line=dict(color=ORANGE, width=2), hovertemplate="%{y:.1f}%<extra></extra>")
        fig.add_scatter(x=x, y=yoy["all"], name=T["series_all"], mode="lines",
                        line=dict(color="#8a8984", width=2), hovertemplate="%{y:.1f}%<extra></extra>")
        fig.update_yaxes(ticksuffix="%", rangemode="tozero")
        fig.update_xaxes(tickangle=0, tickvals=x[::4])
        st.plotly_chart(style(fig, T["yoy_axis"], height=340), use_container_width=True, config=CHART_CONFIG)

# -------------------------------------------------------------- method --
with tab_method:
    with st.container(key="method"):
        st.markdown(T["method_md"].format(stores=stores))

st.markdown(ui.footer(T["footer"].format(repo=f'<a href="{REPO_URL}" target="_blank">GitHub</a>')),
            unsafe_allow_html=True)
