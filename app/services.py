"""Logika biznesowa współdzielona przez widoki HTML i REST API."""
import re
from datetime import date, timedelta

from .db import get_db
from .utils import CATEGORIES, EXPIRY_WARNING_DAYS, FORMS, PAYMENT_METHODS, now_str, parse_pln, today

# ---------------------------------------------------------------- leki

DRUG_FIELDS = ["name", "active_substance", "form", "strength", "category", "price", "stock",
               "min_stock", "rx", "expiry_date"]

SORTABLE = {
    "name": "name COLLATE NOCASE",
    "price": "price_grosze",
    "stock": "stock",
    "expiry": "expiry_date",
}


def _parse_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    value = str(value if value is not None else "").strip()
    return int(value) if re.fullmatch(r"-?\d+", value) else None


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).lower() in ("1", "true", "on", "tak", "yes")


def validate_drug(data, drug_id=None):
    """Waliduje dane leku (z formularza lub JSON). Zwraca (clean, errors)."""
    errors, clean = {}, {}

    name = str(data.get("name") or "").strip()
    if not name:
        errors["name"] = "Nazwa jest wymagana."
    elif len(name) < 2 or len(name) > 60:
        errors["name"] = "Nazwa musi mieć od 2 do 60 znaków."
    else:
        dup = get_db().execute(
            "SELECT id FROM drugs WHERE lower(name) = lower(?) AND id IS NOT ?", (name, drug_id)
        ).fetchone()
        if dup:
            errors["name"] = "Lek o tej nazwie już istnieje."
    clean["name"] = name

    substance = str(data.get("active_substance") or "").strip()
    if not substance:
        errors["active_substance"] = "Substancja czynna jest wymagana."
    clean["active_substance"] = substance.lower()

    form = str(data.get("form") or "").strip()
    if form not in FORMS:
        errors["form"] = "Wybierz postać leku."
    clean["form"] = form

    strength = str(data.get("strength") or "").strip()
    if not strength:
        errors["strength"] = "Dawka jest wymagana (np. 500 mg)."
    clean["strength"] = strength

    category = str(data.get("category") or "").strip()
    if category not in CATEGORIES:
        errors["category"] = "Wybierz kategorię."
    clean["category"] = category

    raw_price = data.get("price")
    price = round(raw_price * 100) if isinstance(raw_price, (int, float)) and not isinstance(raw_price, bool) \
        else parse_pln(raw_price)
    if raw_price in (None, ""):
        errors["price"] = "Cena jest wymagana."
    elif price is None:
        errors["price"] = "Niepoprawna cena (np. 12,50)."
    elif price <= 0:
        errors["price"] = "Cena musi być większa od zera."
    elif price > 100000:
        errors["price"] = "Cena nie może przekraczać 1000 zł."
    clean["price_grosze"] = price

    for field, label in (("stock", "Stan magazynowy"), ("min_stock", "Stan minimalny")):
        value = _parse_int(data.get(field))
        if value is None:
            errors[field] = f"{label} musi być liczbą całkowitą."
        elif value < 0:
            errors[field] = f"{label} nie może być ujemny."
        elif value > 10000:
            errors[field] = f"{label} nie może przekraczać 10000."
        clean[field] = value

    clean["rx"] = 1 if _parse_bool(data.get("rx", False)) else 0

    raw_expiry = str(data.get("expiry_date") or "").strip()
    try:
        expiry = date.fromisoformat(raw_expiry)
        if drug_id is None and expiry < today():
            errors["expiry_date"] = "Data ważności nie może być w przeszłości."
        clean["expiry_date"] = expiry.isoformat()
    except ValueError:
        errors["expiry_date"] = "Podaj poprawną datę ważności."
        clean["expiry_date"] = raw_expiry

    return clean, errors


def insert_drug(clean):
    cur = get_db().execute(
        """INSERT INTO drugs (name, active_substance, form, strength, category, price_grosze,
                              stock, min_stock, rx, expiry_date)
           VALUES (:name, :active_substance, :form, :strength, :category, :price_grosze,
                   :stock, :min_stock, :rx, :expiry_date)""",
        clean,
    )
    get_db().commit()
    return cur.lastrowid


def update_drug(drug_id, clean):
    get_db().execute(
        """UPDATE drugs SET name=:name, active_substance=:active_substance, form=:form,
               strength=:strength, category=:category, price_grosze=:price_grosze, stock=:stock,
               min_stock=:min_stock, rx=:rx, expiry_date=:expiry_date
           WHERE id=:id""",
        dict(clean, id=drug_id),
    )
    get_db().commit()


def delete_drug(drug_id):
    get_db().execute("DELETE FROM drugs WHERE id = ?", (drug_id,))
    get_db().commit()


def get_drug(drug_id):
    return get_db().execute("SELECT * FROM drugs WHERE id = ?", (drug_id,)).fetchone()


def drug_form_values(drug):
    """Wiersz z bazy -> wartości do wypełnienia formularza."""
    values = dict(drug)
    values["price"] = f"{drug['price_grosze'] / 100:.2f}".replace(".", ",")
    return values


def list_drugs(q="", category="", rx="", status="", sort="name", order="asc", page=None, page_size=10):
    where, params = [], []
    if q:
        where.append("(name LIKE ? OR active_substance LIKE ?)")
        params += [f"%{q}%", f"%{q}%"]
    if category:
        where.append("category = ?")
        params.append(category)
    if rx == "rx":
        where.append("rx = 1")
    elif rx == "otc":
        where.append("rx = 0")
    if status == "low_stock":
        where.append("stock <= min_stock")
    elif status == "expiring":
        where.append("expiry_date BETWEEN ? AND ?")
        params += [today().isoformat(), (today() + timedelta(days=EXPIRY_WARNING_DAYS)).isoformat()]
    elif status == "expired":
        where.append("expiry_date < ?")
        params.append(today().isoformat())

    sql_where = ("WHERE " + " AND ".join(where)) if where else ""
    order_by = SORTABLE.get(sort, SORTABLE["name"]) + (" DESC" if order == "desc" else " ASC")
    db = get_db()
    total = db.execute(f"SELECT COUNT(*) FROM drugs {sql_where}", params).fetchone()[0]
    sql = f"SELECT * FROM drugs {sql_where} ORDER BY {order_by}, id"
    if page is not None:
        sql += " LIMIT ? OFFSET ?"
        params = params + [page_size, (page - 1) * page_size]
    return db.execute(sql, params).fetchall(), total


def restock(drug_id, quantity):
    get_db().execute("UPDATE drugs SET stock = stock + ? WHERE id = ?", (quantity, drug_id))
    get_db().commit()


# ---------------------------------------------------------------- sprzedaż


class SaleError(Exception):
    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = errors


def check_item(drug, quantity, prescription_code, already_in_cart=0):
    """Zwraca komunikat błędu albo None, jeśli pozycję można sprzedać."""
    if drug is None:
        return "Nie znaleziono leku."
    if quantity is None or quantity < 1:
        return "Ilość musi być liczbą większą od zera."
    if date.fromisoformat(drug["expiry_date"]) < today():
        return f"{drug['name']}: lek przeterminowany — sprzedaż zablokowana."
    available = drug["stock"] - already_in_cart
    if quantity > available:
        return f"{drug['name']}: niewystarczający stan magazynowy (dostępne: {max(available, 0)})."
    if drug["rx"]:
        if not prescription_code:
            return f"{drug['name']}: lek na receptę — podaj kod recepty."
        if not re.fullmatch(r"\d{4}", prescription_code):
            return "Kod recepty musi składać się z 4 cyfr."
    return None


def find_interactions(substances_a, substances_b):
    """Interakcje pomiędzy dwiema grupami substancji."""
    if not substances_a or not substances_b:
        return []
    rows = get_db().execute("SELECT * FROM interactions").fetchall()
    found = []
    for r in rows:
        pair = {r["substance_a"], r["substance_b"]}
        for a in substances_a:
            for b in substances_b:
                if a != b and {a, b} == pair and dict(r) not in found:
                    found.append(dict(r))
    return found


def cart_interactions(drug_ids):
    """Wszystkie interakcje w obrębie listy leków."""
    db = get_db()
    substances = [
        db.execute("SELECT active_substance FROM drugs WHERE id = ?", (i,)).fetchone()
        for i in drug_ids
    ]
    substances = sorted({s[0] for s in substances if s})
    return find_interactions(substances, substances)


def create_sale(items, payment_method, cash_received_grosze, user_id):
    """items: [{drug_id, quantity, prescription_code}]. Zwraca id sprzedaży albo rzuca SaleError."""
    errors = []
    if not items:
        raise SaleError(["Koszyk jest pusty."])
    if payment_method not in PAYMENT_METHODS:
        errors.append("Wybierz metodę płatności.")

    db = get_db()
    used, lines, total = {}, [], 0
    for item in items:
        drug = get_drug(item.get("drug_id"))
        qty = _parse_int(item.get("quantity"))
        code = (item.get("prescription_code") or "").strip() or None
        err = check_item(drug, qty, code, used.get(item.get("drug_id"), 0))
        if err:
            errors.append(err)
            continue
        used[drug["id"]] = used.get(drug["id"], 0) + qty
        lines.append((drug, qty, code))
        total += qty * drug["price_grosze"]

    if payment_method == "gotowka" and not errors:
        if cash_received_grosze is None:
            errors.append("Podaj kwotę otrzymaną od klienta.")
        elif cash_received_grosze < total:
            errors.append("Otrzymana kwota jest mniejsza niż do zapłaty.")
    if errors:
        raise SaleError(errors)

    cur = db.execute(
        """INSERT INTO sales (created_at, user_id, total_grosze, payment_method, cash_received_grosze)
           VALUES (?, ?, ?, ?, ?)""",
        (now_str(), user_id, total, payment_method,
         cash_received_grosze if payment_method == "gotowka" else None),
    )
    sale_id = cur.lastrowid
    for drug, qty, code in lines:
        db.execute(
            """INSERT INTO sale_items (sale_id, drug_id, drug_name, category, quantity,
                                       unit_price_grosze, prescription_code)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (sale_id, drug["id"], drug["name"], drug["category"], qty, drug["price_grosze"], code),
        )
        db.execute("UPDATE drugs SET stock = stock - ? WHERE id = ?", (qty, drug["id"]))
    db.commit()
    return sale_id


def get_sale(sale_id):
    db = get_db()
    sale = db.execute(
        """SELECT s.*, u.full_name AS seller FROM sales s JOIN users u ON u.id = s.user_id
           WHERE s.id = ?""",
        (sale_id,),
    ).fetchone()
    if sale is None:
        return None, []
    items = db.execute("SELECT * FROM sale_items WHERE sale_id = ? ORDER BY id", (sale_id,)).fetchall()
    return sale, items


def sale_to_dict(sale, items):
    d = {
        "id": sale["id"],
        "created_at": sale["created_at"],
        "seller": sale["seller"],
        "payment_method": sale["payment_method"],
        "total": sale["total_grosze"] / 100,
        "items": [
            {
                "drug_id": i["drug_id"],
                "drug_name": i["drug_name"],
                "quantity": i["quantity"],
                "unit_price": i["unit_price_grosze"] / 100,
                "prescription_code": i["prescription_code"],
            }
            for i in items
        ],
    }
    if sale["cash_received_grosze"] is not None:
        d["cash_received"] = sale["cash_received_grosze"] / 100
        d["change"] = (sale["cash_received_grosze"] - sale["total_grosze"]) / 100
    return d


def list_sales(date_from="", date_to="", payment="", page=None, page_size=10):
    where, params = [], []
    if date_from:
        where.append("date(s.created_at) >= ?")
        params.append(date_from)
    if date_to:
        where.append("date(s.created_at) <= ?")
        params.append(date_to)
    if payment in PAYMENT_METHODS:
        where.append("s.payment_method = ?")
        params.append(payment)
    sql_where = ("WHERE " + " AND ".join(where)) if where else ""
    db = get_db()
    total_count, total_sum = db.execute(
        f"SELECT COUNT(*), COALESCE(SUM(total_grosze), 0) FROM sales s {sql_where}", params
    ).fetchone()
    sql = f"""SELECT s.*, u.full_name AS seller,
                     (SELECT SUM(quantity) FROM sale_items WHERE sale_id = s.id) AS items_count
              FROM sales s JOIN users u ON u.id = s.user_id
              {sql_where} ORDER BY s.created_at DESC, s.id DESC"""
    if page is not None:
        sql += " LIMIT ? OFFSET ?"
        params = params + [page_size, (page - 1) * page_size]
    return db.execute(sql, params).fetchall(), total_count, total_sum


# ---------------------------------------------------------------- statystyki


def stats_summary():
    db = get_db()
    t = today()
    yesterday = t - timedelta(days=1)

    def day_totals(d):
        return db.execute(
            "SELECT COUNT(*), COALESCE(SUM(total_grosze), 0) FROM sales WHERE date(created_at) = ?",
            (d.isoformat(),),
        ).fetchone()

    count_today, revenue_today = day_totals(t)
    _, revenue_yesterday = day_totals(yesterday)
    low_stock = db.execute("SELECT COUNT(*) FROM drugs WHERE stock <= min_stock").fetchone()[0]
    expiring = db.execute(
        "SELECT COUNT(*) FROM drugs WHERE expiry_date BETWEEN ? AND ?",
        (t.isoformat(), (t + timedelta(days=EXPIRY_WARNING_DAYS)).isoformat()),
    ).fetchone()[0]
    expired = db.execute("SELECT COUNT(*) FROM drugs WHERE expiry_date < ?", (t.isoformat(),)).fetchone()[0]
    return {
        "revenue_today": revenue_today,
        "sales_today": count_today,
        "avg_basket": revenue_today // count_today if count_today else 0,
        "revenue_yesterday": revenue_yesterday,
        "low_stock": low_stock,
        "expiring": expiring,
        "expired": expired,
    }


def revenue_by_day(days):
    start = today() - timedelta(days=days - 1)
    rows = get_db().execute(
        """SELECT date(created_at) AS day, SUM(total_grosze) AS revenue, COUNT(*) AS sales
           FROM sales WHERE date(created_at) >= ? GROUP BY day""",
        (start.isoformat(),),
    ).fetchall()
    by_day = {r["day"]: r for r in rows}
    result = []
    for i in range(days):
        d = (start + timedelta(days=i)).isoformat()
        r = by_day.get(d)
        result.append({
            "date": d,
            "revenue": (r["revenue"] if r else 0) / 100,
            "sales": r["sales"] if r else 0,
        })
    return result


def top_drugs(days, limit):
    start = today() - timedelta(days=days - 1)
    rows = get_db().execute(
        """SELECT i.drug_name AS name, SUM(i.quantity) AS quantity,
                  SUM(i.quantity * i.unit_price_grosze) AS revenue
           FROM sale_items i JOIN sales s ON s.id = i.sale_id
           WHERE date(s.created_at) >= ?
           GROUP BY i.drug_name ORDER BY quantity DESC, name LIMIT ?""",
        (start.isoformat(), limit),
    ).fetchall()
    return [{"name": r["name"], "quantity": r["quantity"], "revenue": r["revenue"] / 100} for r in rows]


def revenue_by_category(days):
    start = today() - timedelta(days=days - 1)
    rows = get_db().execute(
        """SELECT i.category, SUM(i.quantity * i.unit_price_grosze) AS revenue
           FROM sale_items i JOIN sales s ON s.id = i.sale_id
           WHERE date(s.created_at) >= ?
           GROUP BY i.category ORDER BY revenue DESC""",
        (start.isoformat(),),
    ).fetchall()
    return [{"category": r["category"], "revenue": r["revenue"] / 100} for r in rows]
