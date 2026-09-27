import re
from datetime import date, datetime

CATEGORIES = [
    "Przeciwbólowe",
    "Antybiotyki",
    "Kardiologiczne",
    "Przeciwcukrzycowe",
    "Witaminy i suplementy",
    "Przeziębienie i grypa",
    "Alergia",
    "Układ pokarmowy",
    "Psychiatryczne",
    "Hormonalne",
]

FORMS = ["tabletki", "kapsułki", "syrop", "zawiesina", "maść", "krople", "aerozol", "saszetki"]

PAYMENT_METHODS = {"gotowka": "Gotówka", "karta": "Karta"}

EXPIRY_WARNING_DAYS = 30


def format_pln(grosze):
    if grosze is None:
        return "—"
    zl, gr = divmod(abs(int(grosze)), 100)
    sign = "-" if grosze < 0 else ""
    zl_str = f"{zl:,}".replace(",", " ")
    return f"{sign}{zl_str},{gr:02d} zł"


def parse_pln(text):
    """'12,50' / '12.5' / '12' -> 1250. Zwraca None, jeśli format jest niepoprawny."""
    if text is None:
        return None
    text = str(text).strip().replace(" ", "").replace("zł", "")
    if not re.fullmatch(r"\d+([.,]\d{1,2})?", text):
        return None
    zl, _, gr = text.replace(",", ".").partition(".")
    return int(zl) * 100 + int((gr + "00")[:2])


def today():
    return date.today()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def drug_status(drug):
    """Lista statusów leku wyliczana z danych: przeterminowany / kończy się ważność / niski stan."""
    statuses = []
    expiry = date.fromisoformat(drug["expiry_date"])
    days_left = (expiry - today()).days
    if days_left < 0:
        statuses.append("expired")
    elif days_left <= EXPIRY_WARNING_DAYS:
        statuses.append("expiring")
    if drug["stock"] <= drug["min_stock"]:
        statuses.append("low_stock")
    return statuses


def drug_to_dict(row):
    d = dict(row)
    d["rx"] = bool(d["rx"])
    d["price"] = d.pop("price_grosze") / 100
    d["statuses"] = drug_status(row)
    return d
