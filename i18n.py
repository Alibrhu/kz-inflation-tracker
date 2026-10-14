"""All texts shown on the site, in Russian and English.

To change a text, edit it here. {curly} parts are filled in by app.py.
"""

MONTHS = {
    "ru": ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}

TEXTS = {
    "ru": {
        "page_title": "Инфляция в Шымкенте",
        "title": "Сколько на самом деле дорожают продукты в Шымкенте",
        "subtitle": "Каждый день собираем цены в онлайн-каталоге магазина и сравниваем с официальной инфляцией "
                    "Бюро национальной статистики (stat.gov.kz).",
        "updated": "Последний сбор цен: {date} · магазин: {stores}",

        "tab_overview": "Обзор",
        "tab_prices": "Цены на продукты",
        "tab_compare": "Сравнение с официальной",
        "tab_method": "Как это считается",

        "kpi_days": "Дней наблюдений",
        "kpi_products": "Товаров в каталоге",
        "kpi_real": "Наши цены, с начала",
        "kpi_official_yoy": "Официально, за год",
        "kpi_official_yoy_help": "Шымкент, продовольственные товары, за 12 месяцев (на {month}). Рассчитано по месячным индексам stat.gov.kz",
        "kpi_real_help": "Изменение нашего индекса цен на продукты с {start}",

        "index_title": "Индекс наших цен и официальный темп роста",
        "index_caption": "100 = цены в первый день сбора. Синяя линия — наши данные. "
                         "Оранжевая пунктирная — как росли бы цены, если бы дорожали ровно с официальной скоростью.",
        "index_axis": "Индекс",
        "series_real": "Наши цены (индекс)",
        "series_official_pace": "Официальный темп ({rate} в год)",

        "findings": "Выводы",
        "f_change": "За **{days} дн.** наблюдений цены на продукты в нашей выборке изменились на **{real}**. "
                    "При официальном темпе инфляции ({rate} в год) за это же время рост составил бы **{expected}**.",
        "f_faster": "Пока наши цены растут **быстрее** официального темпа.",
        "f_slower": "Пока наши цены растут **медленнее** официального темпа.",
        "f_same": "Пока наши цены растут **примерно с официальной скоростью**.",
        "f_changed_share": "Цена изменилась хотя бы раз у **{share}** продуктов, за которыми мы следим.",
        "f_up": "Сильнее всего подорожали: {items}.",
        "f_down": "Сильнее всего подешевели: {items}.",
        "f_caveat": "⚠️ Данных пока меньше {min_days} дней, поэтому выводы предварительные: "
                    "за короткий срок на результат сильно влияют случайные скидки и смена ассортимента.",
        "f_monthly": "Месячное сравнение: в {month} наши цены изменились на **{real}**, официальные — на **{official}**.",
        "f_monthly_wait": "Первое помесячное сравнение с официальной статистикой появится, "
                          "когда накопится хотя бы один полный месяц данных.",

        "cat_chart_title": "Изменение цен по категориям с начала сбора",
        "cat_chart_caption": "Учтены категории, где хотя бы {n} продуктов продаются весь период.",

        "prices_intro": "Выберите категорию и продукты, чтобы увидеть, как менялась их цена.",
        "category": "Категория",
        "all_food": "Все продукты",
        "products": "Продукты",
        "products_placeholder": "Выберите продукты",
        "products_help": "Можно выбрать до 8 продуктов. Начните печатать название, чтобы найти нужный.",
        "pick_products": "Выберите хотя бы один продукт выше.",
        "price_axis": "Цена, ₸",
        "movers_title": "Самые большие изменения цен",
        "movers_caption": "Первая и последняя цена каждого продукта за период наблюдений.",
        "col_product": "Продукт",
        "col_category": "Категория",
        "col_first": "Было, ₸",
        "col_last": "Стало, ₸",
        "col_change": "Изменение",
        "show_nonfood": "Показывать и непродовольственные товары (бытовая химия, корм и т. п.)",

        "compare_intro": "Официальная статистика выходит раз в месяц, поэтому сравниваем помесячно: "
                         "насколько цены выросли за месяц по сравнению с предыдущим.",
        "compare_title": "Рост цен на продукты за месяц, %",
        "series_official": "Официально (stat.gov.kz)",
        "series_real_monthly": "Наши данные",
        "monthly_axis": "Изменение к прошлому месяцу, %",
        "compare_wait": "Наши помесячные точки появятся, когда соберётся хотя бы {n} дней в двух месяцах подряд. "
                        "Сейчас видна только официальная линия.",
        "compare_table": "Таблица",
        "col_month": "Месяц",
        "col_official": "Официально",
        "col_real": "Наши данные",
        "official_source": "Источник: Бюро национальной статистики, «Индекс цен на потребительские товары и услуги», "
                           "г. Шымкент, продовольственные товары.",
        "yoy_title": "Официальная инфляция за 12 месяцев, Шымкент",
        "series_food": "Продукты",
        "series_all": "Все товары и услуги",
        "yoy_axis": "К тому же месяцу прошлого года, %",

        "method_md": """
### Откуда цены
Каждое утро программа (`scraper.py`) открывает онлайн-каталог магазина **{stores}** в Glovo и записывает
цены всех товаров. Это делает GitHub автоматически, в 09:17 по Шымкенту. Все цены лежат в файле
`data/prices.csv`.

### Как считается «наш» индекс
1. Берём только продукты питания: бытовую химию, гигиену, корм для животных и игрушки убираем.
2. Убираем товары, которых в этот день не было в наличии.
3. Для каждой пары соседних дней берём продукты, которые продавались **в оба дня**, и смотрим,
   во сколько раз изменилась цена каждого.
4. Усредняем эти изменения (среднее геометрическое; так дешёвая жвачка и дорогой кофе весят одинаково).
5. Перемножаем дневные изменения — получается индекс: 100 в первый день, 101 значит «на 1% дороже».

Так новые и пропавшие из каталога товары не искажают результат.

### Откуда официальные данные
С сайта Бюро национальной статистики: таблица «Индекс цен на потребительские товары и услуги»
по г. Шымкент, строка «Продовольственные товары». Её обновляет программа `update_official_cpi.py`.

### Ограничения
- Это **один магазин**, а не весь город. Официальная статистика собирает цены во многих местах.
- Онлайн-цены могут отличаться от цен на полке. Поэтому мы смотрим на **изменения** цен, а не на сами цены.
- У нас все продукты весят одинаково. В официальном индексе важнее то, на что люди тратят больше денег (хлеб, мясо).
- Пока наблюдений мало, на результат сильно влияют случайности.
""",
        "no_data": "Данных о ценах пока нет. Они появятся после первого автоматического сбора.",
        "too_little_data": "Пока собран только один день цен. Графики изменений появятся со второго дня.",
        "no_official": "Файл с официальной статистикой не найден. Запустите `python update_official_cpi.py`.",
        "footer": "Некоммерческий студенческий проект. Код и данные: [GitHub]({repo}).",
    },
    "en": {
        "page_title": "Shymkent inflation",
        "title": "How fast are food prices really rising in Shymkent?",
        "subtitle": "We collect prices from a supermarket's online catalog every day and compare them with the "
                    "official inflation figures from the Bureau of National Statistics (stat.gov.kz).",
        "updated": "Last price collection: {date} · store: {stores}",

        "tab_overview": "Overview",
        "tab_prices": "Food prices",
        "tab_compare": "Real vs official",
        "tab_method": "Methodology",

        "kpi_days": "Days observed",
        "kpi_products": "Products in catalog",
        "kpi_real": "Our prices since start",
        "kpi_official_yoy": "Official, 12 months",
        "kpi_official_yoy_help": "Shymkent, food products, over 12 months (as of {month}). Computed from stat.gov.kz monthly indices",
        "kpi_real_help": "Change of our food price index since {start}",

        "index_title": "Our price index vs the official pace",
        "index_caption": "100 = prices on the first day. Blue line: our data. "
                         "Dashed orange line: where prices would be if they rose exactly at the official rate.",
        "index_axis": "Index",
        "series_real": "Our prices (index)",
        "series_official_pace": "Official pace ({rate} per year)",

        "findings": "Key findings",
        "f_change": "Over **{days} days** of observation, food prices in our sample changed by **{real}**. "
                    "At the official inflation rate ({rate} per year) they would have changed by **{expected}**.",
        "f_faster": "So far our prices are rising **faster** than the official pace.",
        "f_slower": "So far our prices are rising **slower** than the official pace.",
        "f_same": "So far our prices are rising **at about the official pace**.",
        "f_changed_share": "**{share}** of the products we track changed price at least once.",
        "f_up": "Biggest price increases: {items}.",
        "f_down": "Biggest price decreases: {items}.",
        "f_caveat": "⚠️ We have fewer than {min_days} days of data, so these findings are preliminary: "
                    "over a short period random discounts and catalog changes matter a lot.",
        "f_monthly": "Monthly comparison: in {month} our prices changed by **{real}**, official ones by **{official}**.",
        "f_monthly_wait": "The first month-by-month comparison with official statistics will appear "
                          "once we have at least one full month of data.",

        "cat_chart_title": "Price change by category since start",
        "cat_chart_caption": "Only categories with at least {n} products sold throughout the period.",

        "prices_intro": "Pick a category and products to see how their prices changed.",
        "category": "Category",
        "all_food": "All food",
        "products": "Products",
        "products_placeholder": "Choose products",
        "products_help": "Up to 8 products. Start typing a name to find it.",
        "pick_products": "Pick at least one product above.",
        "price_axis": "Price, ₸",
        "movers_title": "Biggest price changes",
        "movers_caption": "First and last price of each product during the observation period.",
        "col_product": "Product",
        "col_category": "Category",
        "col_first": "Before, ₸",
        "col_last": "Now, ₸",
        "col_change": "Change",
        "show_nonfood": "Also show non-food items (household goods, pet food, etc.)",

        "compare_intro": "Official statistics come out once a month, so we compare month by month: "
                         "how much prices rose compared to the previous month.",
        "compare_title": "Monthly food price change, %",
        "series_official": "Official (stat.gov.kz)",
        "series_real_monthly": "Our data",
        "monthly_axis": "Change vs previous month, %",
        "compare_wait": "Our monthly points will appear once we have at least {n} days in two consecutive months. "
                        "For now only the official line is shown.",
        "compare_table": "Table",
        "col_month": "Month",
        "col_official": "Official",
        "col_real": "Our data",
        "official_source": "Source: Bureau of National Statistics, “Consumer price index”, Shymkent, food products.",
        "yoy_title": "Official 12-month inflation, Shymkent",
        "series_food": "Food",
        "series_all": "All goods and services",
        "yoy_axis": "Vs same month last year, %",

        "method_md": """
### Where prices come from
Every morning a script (`scraper.py`) opens the online catalog of **{stores}** on Glovo and records the price
of every product. GitHub runs it automatically at 09:17 Shymkent time. All prices are stored in
`data/prices.csv`.

### How “our” index is calculated
1. Keep food only: household chemicals, hygiene, pet food and toys are removed.
2. Drop products that were out of stock that day.
3. For each pair of consecutive days take the products sold **on both days** and compute how much each price changed.
4. Average those changes (geometric mean, so cheap gum and expensive coffee count equally).
5. Multiply the daily changes together. That gives an index: 100 on the first day, 101 means “1% more expensive”.

This way products appearing in or disappearing from the catalog don't distort the result.

### Where official data comes from
From the Bureau of National Statistics: the table “Consumer price index” for Shymkent, row “Food products”.
The script `update_official_cpi.py` refreshes it.

### Limitations
- This is **one store**, not the whole city. Official statistics collect prices in many places.
- Online prices can differ from shelf prices, so we look at price **changes**, not price levels.
- All products have equal weight here. The official index gives more weight to what people spend more on (bread, meat).
- With little data so far, random effects matter a lot.
""",
        "no_data": "No price data yet. It will appear after the first automatic collection.",
        "too_little_data": "Only one day of prices so far. Change charts will appear from the second day.",
        "no_official": "Official statistics file not found. Run `python update_official_cpi.py`.",
        "footer": "Non-commercial student project. Code and data: [GitHub]({repo}).",
    },
}
