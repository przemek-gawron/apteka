"""Dane przykładowe. Losowość ma stałe ziarno, więc dane są powtarzalne
(daty liczone są względem dzisiejszego dnia)."""
import random
from datetime import date, datetime, time, timedelta

from werkzeug.security import generate_password_hash

USERS = [
    ("kierownik", "kierownik123", "Anna Nowak", "kierownik"),
    ("farmaceuta", "farmaceuta123", "Jan Kowalski", "farmaceuta"),
]

# name, substancja, postać, dawka, kategoria, cena [gr], stan, min, rx, ważność [dni od dziś], popularność
DRUGS = [
    ("Apap", "paracetamol", "tabletki", "500 mg", "Przeciwbólowe", 1299, 120, 30, 0, 400, 10),
    ("Ibuprom", "ibuprofen", "tabletki", "200 mg", "Przeciwbólowe", 1549, 95, 30, 0, 380, 9),
    ("Nurofen Forte", "ibuprofen", "tabletki", "400 mg", "Przeciwbólowe", 2199, 60, 20, 0, 300, 6),
    ("Polopiryna S", "kwas acetylosalicylowy", "tabletki", "300 mg", "Przeciwbólowe", 899, 70, 20, 0, 500, 5),
    ("Acard", "kwas acetylosalicylowy", "tabletki", "75 mg", "Kardiologiczne", 1050, 110, 30, 0, 450, 7),
    ("Ketonal", "ketoprofen", "kapsułki", "50 mg", "Przeciwbólowe", 1890, 8, 15, 1, 250, 3),
    ("Tramal", "tramadol", "kapsułki", "50 mg", "Przeciwbólowe", 2350, 25, 10, 1, 200, 2),
    ("Amotaks", "amoksycylina", "kapsułki", "500 mg", "Antybiotyki", 1720, 40, 15, 1, 220, 4),
    ("Augmentin", "amoksycylina z kwasem klawulanowym", "tabletki", "875 mg", "Antybiotyki", 3150, 30, 10, 1, 18, 4),
    ("Klacid", "klarytromycyna", "tabletki", "500 mg", "Antybiotyki", 4290, 12, 10, 1, 160, 2),
    ("Bisocard", "bisoprolol", "tabletki", "5 mg", "Kardiologiczne", 1190, 85, 25, 1, 600, 6),
    ("Polpril", "ramipryl", "kapsułki", "5 mg", "Kardiologiczne", 1420, 75, 25, 1, 540, 6),
    ("Atoris", "atorwastatyna", "tabletki", "20 mg", "Kardiologiczne", 2480, 65, 20, 1, 480, 5),
    ("Warfin", "warfaryna", "tabletki", "5 mg", "Kardiologiczne", 1675, 5, 10, 1, 330, 2),
    ("Metformax", "metformina", "tabletki", "850 mg", "Przeciwcukrzycowe", 980, 90, 30, 1, 700, 6),
    ("Diaprel MR", "gliklazyd", "tabletki", "60 mg", "Przeciwcukrzycowe", 2210, 35, 15, 1, 25, 2),
    ("Euthyrox N", "lewotyroksyna", "tabletki", "50 µg", "Hormonalne", 1030, 100, 30, 1, 520, 5),
    ("Sertagen", "sertralina", "tabletki", "50 mg", "Psychiatryczne", 1860, 40, 15, 1, 410, 3),
    ("Controloc", "pantoprazol", "tabletki", "20 mg", "Układ pokarmowy", 2090, 55, 20, 1, 350, 4),
    ("Stoperan", "loperamid", "kapsułki", "2 mg", "Układ pokarmowy", 1399, 45, 15, 0, 390, 3),
    ("Smecta", "diosmektyt", "saszetki", "3 g", "Układ pokarmowy", 1750, 30, 10, 0, -12, 2),
    ("Espumisan", "symetykon", "kapsułki", "40 mg", "Układ pokarmowy", 1590, 50, 15, 0, 460, 3),
    ("Zyrtec", "cetyryzyna", "tabletki", "10 mg", "Alergia", 1690, 60, 20, 0, 430, 5),
    ("Claritine", "loratadyna", "tabletki", "10 mg", "Alergia", 1840, 14, 20, 0, 370, 4),
    ("Fenistil", "dimetynden", "krople", "1 mg/ml", "Alergia", 2290, 22, 10, 0, 12, 2),
    ("Gripex Max", "paracetamol + pseudoefedryna", "tabletki", "500 mg", "Przeziębienie i grypa", 2450, 80, 25, 0, 300, 7),
    ("Theraflu Extra", "paracetamol + fenylefryna", "saszetki", "650 mg", "Przeziębienie i grypa", 2799, 45, 15, 0, 260, 4),
    ("Sudafed", "pseudoefedryna", "tabletki", "60 mg", "Przeziębienie i grypa", 1990, 3, 10, 0, 280, 3),
    ("Otrivin", "ksylometazolina", "aerozol", "0,1%", "Przeziębienie i grypa", 1650, 70, 20, 0, 510, 5),
    ("Rutinoscorbin", "rutyna + witamina C", "tabletki", "25 mg + 100 mg", "Witaminy i suplementy", 1149, 150, 40, 0, 620, 8),
    ("Magne B6", "magnez + witamina B6", "tabletki", "48 mg + 5 mg", "Witaminy i suplementy", 2350, 90, 25, 0, 540, 5),
    ("Vigantoletten", "cholekalcyferol", "tabletki", "1000 j.m.", "Witaminy i suplementy", 1990, 110, 30, 0, 590, 6),
]

INTERACTIONS = [
    ("warfaryna", "ibuprofen", "poważna",
     "Zwiększone ryzyko krwawienia z przewodu pokarmowego."),
    ("warfaryna", "kwas acetylosalicylowy", "poważna",
     "Sumowanie działania przeciwkrzepliwego — wysokie ryzyko krwawień."),
    ("warfaryna", "klarytromycyna", "poważna",
     "Klarytromycyna hamuje metabolizm warfaryny — wzrost INR."),
    ("warfaryna", "ketoprofen", "poważna",
     "Zwiększone ryzyko krwawienia."),
    ("atorwastatyna", "klarytromycyna", "poważna",
     "Wzrost stężenia statyny — ryzyko miopatii i rabdomiolizy."),
    ("sertralina", "tramadol", "poważna",
     "Ryzyko zespołu serotoninowego oraz obniżenia progu drgawkowego."),
    ("ramipryl", "ibuprofen", "umiarkowana",
     "NLPZ osłabiają działanie hipotensyjne i zwiększają ryzyko uszkodzenia nerek."),
    ("lewotyroksyna", "magnez + witamina B6", "umiarkowana",
     "Magnez zmniejsza wchłanianie lewotyroksyny — zachować 4 h odstępu."),
    ("bisoprolol", "pseudoefedryna", "umiarkowana",
     "Pseudoefedryna może podnosić ciśnienie i osłabiać działanie beta-blokera."),
    ("metformina", "kwas acetylosalicylowy", "łagodna",
     "Duże dawki salicylanów mogą nasilać działanie hipoglikemizujące."),
]

HISTORY_DAYS = 90


def seed(conn):
    rng = random.Random(42)
    today = date.today()

    conn.executemany(
        "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
        [(u, generate_password_hash(p, method="pbkdf2:sha256:1000"), n, r) for u, p, n, r in USERS],
    )

    for d in DRUGS:
        name, subst, form, strength, cat, price, stock, min_stock, rx, expiry_days, _ = d
        conn.execute(
            """INSERT INTO drugs (name, active_substance, form, strength, category, price_grosze,
                                  stock, min_stock, rx, expiry_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, subst, form, strength, cat, price, stock, min_stock, rx,
             (today + timedelta(days=expiry_days)).isoformat()),
        )

    conn.executemany(
        "INSERT INTO interactions (substance_a, substance_b, severity, description) VALUES (?, ?, ?, ?)",
        INTERACTIONS,
    )

    drugs = [(i + 1, d) for i, d in enumerate(DRUGS)]
    weights = [d[10] for d in DRUGS]
    now = datetime.now()
    sale_id = 0
    sales_rows, item_rows = [], []

    for day_offset in range(HISTORY_DAYS, -1, -1):
        day = today - timedelta(days=day_offset)
        base = 14 if day.weekday() >= 5 else 26
        # sezon: im bliżej dziś, tym więcej sprzedaży (jesienne przeziębienia)
        season = 1 + (HISTORY_DAYS - day_offset) / HISTORY_DAYS * 0.4
        for _ in range(int(base * season) + rng.randint(-4, 6)):
            ts = datetime.combine(day, time(8, 0)) + timedelta(minutes=rng.randint(0, 12 * 60 - 1))
            if ts > now:
                continue
            sale_id += 1
            total = 0
            n_items = rng.choices([1, 2, 3], weights=[60, 30, 10])[0]
            for drug_id, d in rng.choices(drugs, weights=weights, k=n_items):
                qty = rng.choices([1, 2, 3], weights=[75, 20, 5])[0]
                code = f"{rng.randint(0, 9999):04d}" if d[8] else None
                item_rows.append((sale_id, drug_id, d[0], d[4], qty, d[5], code))
                total += qty * d[5]
            method = rng.choices(["karta", "gotowka"], weights=[65, 35])[0]
            cash = None
            if method == "gotowka":
                cash = -(-total // 1000) * 1000  # zaokrąglenie w górę do 10 zł
            sales_rows.append((sale_id, ts.strftime("%Y-%m-%d %H:%M:%S"), rng.choice([1, 2]), total, method, cash))

    sales_rows.sort(key=lambda r: r[1])
    # numeracja sprzedaży chronologicznie
    remap = {old_id: new_id for new_id, old_id in enumerate((r[0] for r in sales_rows), start=1)}
    conn.executemany(
        """INSERT INTO sales (id, created_at, user_id, total_grosze, payment_method, cash_received_grosze)
           VALUES (?, ?, ?, ?, ?, ?)""",
        [(remap[r[0]],) + r[1:] for r in sales_rows],
    )
    conn.executemany(
        """INSERT INTO sale_items (sale_id, drug_id, drug_name, category, quantity, unit_price_grosze,
                                   prescription_code)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [(remap[r[0]],) + r[1:] for r in item_rows],
    )
