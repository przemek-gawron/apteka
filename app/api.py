"""REST API (JSON). Autoryzacja przez cookie sesji — najpierw POST /api/login."""
import time

from flask import Blueprint, current_app, g, jsonify, request, session

from . import services
from .auth import authenticate, login_required, manager_required
from .db import init_db
from .utils import drug_to_dict

bp = Blueprint("api", __name__, url_prefix="/api")


def _int_arg(name, default, lo, hi):
    try:
        return min(max(int(request.args.get(name, default)), lo), hi)
    except ValueError:
        return default


def _stats_delay():
    delay = current_app.config["STATS_DELAY_MS"]
    if delay:
        time.sleep(delay / 1000)


# ---------------------------------------------------------------- auth

@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = authenticate(data.get("username", ""), data.get("password", ""))
    if user is None:
        return jsonify(error="Nieprawidłowy login lub hasło"), 401
    session.clear()
    session["user_id"] = user["id"]
    return jsonify(id=user["id"], username=user["username"], full_name=user["full_name"], role=user["role"])


@bp.post("/logout")
def logout():
    session.clear()
    return "", 204


@bp.get("/me")
@login_required
def me():
    return jsonify(dict(g.user))


# ---------------------------------------------------------------- leki

@bp.get("/drugs")
@login_required
def drugs_list():
    rows, total = services.list_drugs(
        q=request.args.get("q", ""),
        category=request.args.get("category", ""),
        rx=request.args.get("rx", ""),
        status=request.args.get("status", ""),
        sort=request.args.get("sort", "name"),
        order=request.args.get("order", "asc"),
    )
    return jsonify(total=total, items=[drug_to_dict(r) for r in rows])


@bp.get("/drugs/<int:drug_id>")
@login_required
def drugs_get(drug_id):
    drug = services.get_drug(drug_id)
    if drug is None:
        return jsonify(error="Nie znaleziono leku"), 404
    return jsonify(drug_to_dict(drug))


@bp.post("/drugs")
@login_required
def drugs_create():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Oczekiwano obiektu JSON"), 400
    clean, errors = services.validate_drug(data)
    if errors:
        return jsonify(errors=errors), 400
    drug_id = services.insert_drug(clean)
    return jsonify(drug_to_dict(services.get_drug(drug_id))), 201


@bp.route("/drugs/<int:drug_id>", methods=["PUT", "PATCH"])
@login_required
def drugs_update(drug_id):
    drug = services.get_drug(drug_id)
    if drug is None:
        return jsonify(error="Nie znaleziono leku"), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Oczekiwano obiektu JSON"), 400
    if request.method == "PATCH":
        current = drug_to_dict(drug)
        data = {k: data.get(k, current[k]) for k in services.DRUG_FIELDS}
    clean, errors = services.validate_drug(data, drug_id=drug_id)
    if errors:
        return jsonify(errors=errors), 400
    services.update_drug(drug_id, clean)
    return jsonify(drug_to_dict(services.get_drug(drug_id)))


@bp.delete("/drugs/<int:drug_id>")
@manager_required
def drugs_delete(drug_id):
    if services.get_drug(drug_id) is None:
        return jsonify(error="Nie znaleziono leku"), 404
    services.delete_drug(drug_id)
    return "", 204


@bp.get("/interactions")
@login_required
def interactions():
    """?drug_ids=1,2,3 -> interakcje pomiędzy tymi lekami."""
    try:
        ids = [int(x) for x in request.args.get("drug_ids", "").split(",") if x.strip()]
    except ValueError:
        return jsonify(error="drug_ids: lista liczb oddzielona przecinkami"), 400
    return jsonify(services.cart_interactions(ids))


# ---------------------------------------------------------------- sprzedaż

@bp.post("/sales")
@login_required
def sales_create():
    data = request.get_json(silent=True) or {}
    items = data.get("items") or []
    if not isinstance(items, list):
        return jsonify(errors=["items musi być listą"]), 400
    ids = [i.get("drug_id") for i in items if isinstance(i, dict)]
    interactions = services.cart_interactions(ids)
    if interactions and not data.get("confirm_interactions"):
        return jsonify(error="Wykryto interakcje — potwierdź flagą confirm_interactions",
                       interactions=interactions), 409
    cash = data.get("cash_received")
    cash_grosze = round(cash * 100) if isinstance(cash, (int, float)) else None
    try:
        sale_id = services.create_sale(items, data.get("payment_method"), cash_grosze, g.user["id"])
    except services.SaleError as e:
        return jsonify(errors=e.errors), 400
    return jsonify(services.sale_to_dict(*services.get_sale(sale_id))), 201


@bp.get("/sales/<int:sale_id>")
@login_required
def sales_get(sale_id):
    sale, items = services.get_sale(sale_id)
    if sale is None:
        return jsonify(error="Nie znaleziono sprzedaży"), 404
    return jsonify(services.sale_to_dict(sale, items))


# ---------------------------------------------------------------- statystyki (z opóźnieniem)

@bp.get("/stats/summary")
@login_required
def stats_summary():
    _stats_delay()
    s = services.stats_summary()
    for k in ("revenue_today", "avg_basket", "revenue_yesterday"):
        s[k] = s[k] / 100
    return jsonify(s)


@bp.get("/stats/revenue")
@login_required
def stats_revenue():
    _stats_delay()
    return jsonify(services.revenue_by_day(_int_arg("days", 30, 1, 90)))


@bp.get("/stats/top-drugs")
@login_required
def stats_top():
    _stats_delay()
    return jsonify(services.top_drugs(_int_arg("days", 30, 1, 90), _int_arg("limit", 5, 1, 20)))


@bp.get("/stats/categories")
@login_required
def stats_categories():
    _stats_delay()
    return jsonify(services.revenue_by_category(_int_arg("days", 30, 1, 90)))


# ---------------------------------------------------------------- tylko dla testów

@bp.post("/test/reset")
def test_reset():
    if current_app.config["APP_ENV"] != "test":
        return jsonify(error="Dostępne tylko przy APP_ENV=test"), 404
    init_db()
    return jsonify(status="ok")
