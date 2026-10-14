"""Look of the site: colors, cards, animations.

Colors are taken from the flag of Kazakhstan (sky blue + gold).
Each function returns a piece of HTML that app.py shows with st.markdown.
"""

import html
import re

CSS = """
<style>
:root {
  --kz-sky: #00a3c4;
  --kz-deep: #0b4f7c;
  --kz-gold: #f2b705;
  --ink: #0f2433;
  --muted: #5b6b78;
  --card: #ffffff;
  --shadow: 0 6px 24px rgba(11, 79, 124, 0.08);
}

/* page background: soft sky gradient instead of plain white */
.stApp {
  background:
    radial-gradient(1200px 500px at 90% -10%, rgba(0, 163, 196, 0.16), transparent 60%),
    radial-gradient(900px 400px at -10% 10%, rgba(242, 183, 5, 0.12), transparent 60%),
    #f4f8fb;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1200px; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes float { from { transform: translateY(0); } to { transform: translateY(-14px); } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(242, 183, 5, .7); } 100% { box-shadow: 0 0 0 12px rgba(242, 183, 5, 0); } }

/* ---------- hero banner ---------- */
.hero {
  position: relative; overflow: hidden;
  border-radius: 28px; padding: 44px 44px 40px;
  background: linear-gradient(120deg, var(--kz-deep) 0%, #0a7aa6 45%, var(--kz-sky) 100%);
  color: #fff; box-shadow: 0 18px 50px rgba(11, 79, 124, 0.28);
  animation: fadeUp .7s ease-out both;
}
.hero h1 { color: #fff; font-size: clamp(1.8rem, 4vw, 2.9rem); line-height: 1.15; margin: 14px 0 12px; max-width: 760px; padding: 0; }
.hero p { color: rgba(255, 255, 255, .9); font-size: 1.08rem; max-width: 720px; margin: 0 0 18px; }
.hero .meta { font-size: .9rem; color: rgba(255, 255, 255, .78); }
.hero .badge {
  display: inline-flex; align-items: center; gap: 10px;
  background: rgba(255, 255, 255, .14); border: 1px solid rgba(255, 255, 255, .28);
  padding: 6px 14px; border-radius: 999px; font-size: .85rem; backdrop-filter: blur(6px);
}
.hero .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--kz-gold); animation: pulse 1.8s infinite; }
/* the sun from the flag, slowly turning */
.hero .sun {
  position: absolute; right: -40px; top: -40px; width: 300px; height: 300px; opacity: .33;
  background: repeating-conic-gradient(var(--kz-gold) 0 5deg, transparent 5deg 15deg);
  -webkit-mask: radial-gradient(circle, transparent 38%, #000 39%, #000 70%, transparent 71%);
          mask: radial-gradient(circle, transparent 38%, #000 39%, #000 70%, transparent 71%);
  animation: spin 80s linear infinite;
}
.hero .sun-core {
  position: absolute; right: 50px; top: 50px; width: 120px; height: 120px; border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #ffe07a, var(--kz-gold)); opacity: .45;
  animation: float 5s ease-in-out infinite alternate;
}

/* ---------- KPI cards ---------- */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 6px 0 10px; }
@media (max-width: 900px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 520px) { .kpi-grid { grid-template-columns: 1fr; } .hero { padding: 30px 22px; } }
.kpi {
  background: var(--card); border-radius: 20px; padding: 18px 20px; box-shadow: var(--shadow);
  border-top: 5px solid var(--accent); animation: fadeUp .6s ease-out both;
  transition: transform .2s ease, box-shadow .2s ease;
}
.kpi:hover { transform: translateY(-4px); box-shadow: 0 14px 34px rgba(11, 79, 124, .14); }
.kpi .top { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: .92rem; }
.kpi .icon {
  width: 36px; height: 36px; border-radius: 12px; display: grid; place-items: center; font-size: 1.15rem;
  background: color-mix(in srgb, var(--accent) 16%, white);
}
.kpi .value { font-size: 2.1rem; font-weight: 800; color: var(--ink); margin: 10px 0 2px; letter-spacing: -.02em; }
.kpi .sub { font-size: .8rem; color: var(--muted); line-height: 1.35; }

/* ---------- section titles & cards ---------- */
.sec { display: flex; align-items: center; gap: 12px; font-size: 1.35rem; font-weight: 750; color: var(--ink); margin: 26px 0 10px; animation: fadeUp .6s ease-out both; }
.sec .bar { width: 6px; height: 26px; border-radius: 6px; background: linear-gradient(var(--kz-sky), var(--kz-gold)); }
.findings {
  background: var(--card); border-radius: 20px; padding: 20px 22px; box-shadow: var(--shadow);
  border-left: 6px solid var(--kz-gold);
}
.findings ul { margin: 0; padding-left: 0; list-style: none; }
.findings li { position: relative; padding: 8px 0 8px 30px; color: var(--ink); line-height: 1.5; animation: fadeUp .5s ease-out both; }
.findings li + li { border-top: 1px dashed #e3eaf0; }
.findings li::before { content: "◆"; position: absolute; left: 4px; top: 8px; color: var(--kz-sky); font-size: .85rem; }
.findings .warn { margin-top: 12px; background: #fff7dc; border-radius: 12px; padding: 10px 14px; color: #6b5200; font-size: .9rem; }

/* charts sit on white cards */
[data-testid="stPlotlyChart"] {
  background: var(--card); border-radius: 20px; padding: 14px 10px 6px; box-shadow: var(--shadow);
  animation: fadeUp .7s ease-out both;
}

/* ---------- tabs as pills ---------- */
.stTabs [role="tablist"] { gap: 8px; flex-wrap: wrap; margin: 18px 0 8px; }
.stTabs [role="tab"] {
  background: #fff; border-radius: 999px; padding: 8px 18px; height: auto; box-shadow: var(--shadow);
  transition: background .2s, color .2s, transform .2s;
}
.stTabs [role="tab"]:hover { transform: translateY(-2px); }
.stTabs [role="tab"][aria-selected="true"] { background: linear-gradient(120deg, var(--kz-deep), var(--kz-sky)); color: #fff; }
.stTabs [role="tab"][aria-selected="true"] p { color: #fff; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [role="tabpanel"] { animation: fadeUp .45s ease-out both; }

/* tables, alerts, method text */
[data-testid="stDataFrame"], [data-testid="stExpander"] { border-radius: 16px; overflow: hidden; box-shadow: var(--shadow); background: #fff; }
.st-key-method { background: var(--card); border-radius: 20px; padding: 8px 28px 20px; box-shadow: var(--shadow); }

.footer { text-align: center; color: var(--muted); font-size: .88rem; padding: 26px 0 8px; }
.footer a { color: var(--kz-deep); font-weight: 600; }

@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style>
"""


def md_inline(text: str) -> str:
    """Escape text for HTML, then turn **bold** and `code` into tags."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", text)


def hero(title: str, subtitle: str, badge: str, meta: str) -> str:
    return f"""
<div class="hero">
  <div class="sun"></div><div class="sun-core"></div>
  <span class="badge"><span class="dot"></span>{html.escape(badge)}</span>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
  <div class="meta">{html.escape(meta)}</div>
</div>"""


def kpi_cards(cards: list) -> str:
    """cards: list of (icon, label, value, sub, accent_color)."""
    items = []
    for i, (icon, label, value, sub, accent) in enumerate(cards):
        items.append(f"""
  <div class="kpi" style="--accent:{accent}; animation-delay:{0.08 * i + 0.1:.2f}s">
    <div class="top"><span class="icon">{icon}</span>{html.escape(label)}</div>
    <div class="value">{html.escape(str(value))}</div>
    <div class="sub">{html.escape(sub)}</div>
  </div>""")
    return f'<div class="kpi-grid">{"".join(items)}</div>'


def section(title: str) -> str:
    return f'<div class="sec"><span class="bar"></span>{html.escape(title)}</div>'


def findings(notes: list, warning: str = "") -> str:
    lis = "".join(f'<li style="animation-delay:{0.1 * i + 0.2:.2f}s">{md_inline(n)}</li>' for i, n in enumerate(notes))
    warn = f'<div class="warn">{md_inline(warning)}</div>' if warning else ""
    return f'<div class="findings"><ul>{lis}</ul>{warn}</div>'


def footer(text_html: str) -> str:
    return f'<div class="footer">{text_html}</div>'
