import csv
import io
import math

from flask import (Blueprint, Response, abort, current_app, flash, g, redirect, render_template, request,
                   session, url_for)

from . import services
from .auth import login_required
from .db import get_db
from .utils import PAYMENT_METHODS, parse_pln

bp = Blueprint("sales", __name__)


def _cart():
    return session.setdefault("cart", [])


def _cart_lines(cart):
    lines, total = [], 0
    for index, item in enumerate(cart):
        drug = services.get_drug(item["drug_id"])
        if drug is None:
            continue
        subtotal = drug["price_grosze"] * item["quantity"]
        total += subtotal
        lines.append({"index": index, "drug": drug, "quantity": item["quantity"],
                      "prescription_code": item.get("prescription_code"), "subtotal": subtotal})
    return lines, total


def _render_pos(pending=None, interactions=None, form=None, error=None, status=200):
    cart = _cart()
    lines, total = _cart_lines(cart)
    drugs = get_db().execute("SELECT * FROM drugs ORDER BY name COLLATE NOCASE").fetchall()
    return render_template(
        "sales/pos.html",
        drugs=drugs, lines=lines, total=total, pending=pending, interactions=interactions or [],
        form=form or {}, error=error, payment_methods=PAYMENT_METHODS,
        cart_interactions=services.cart_interactions([i["drug_id"] for i in cart]),
    ), status


@bp.route("/kasa")
@login_required
def pos():
    return _render_pos()


@bp.route("/kasa/dodaj", methods=["POST"])
@login_required
def add_to_cart():
    form = request.form.to_dict()
    try:
        drug_id = int(form.get("drug_id", ""))
    except ValueError:
        return _render_pos(form=form, error="Wybierz lek.", status=400)
    quantity = services._parse_int(form.get("quantity"))
    code = form.get("prescription_code", "").strip() or None
    drug = services.get_drug(drug_id)

    cart = _cart()
    in_cart = sum(i["quantity"] for i in cart if i["drug_id"] == drug_id)
    error = services.check_item(drug, quantity, code, in_cart)
    if error:
        return _render_pos(form=form, error=error, status=400)

    if form.get("confirm_interaction") != "1":
        cart_substances = [
            services.get_drug(i["drug_id"])["active_substance"] for i in cart if services.get_drug(i["drug_id"])
        ]
        interactions = services.find_interactions([drug["active_substance"]], cart_substances)
        if interactions:
            return _render_pos(pending={"drug": drug, "quantity": quantity, "prescription_code": code},
                               interactions=interactions, form=form)

    cart.append({"drug_id": drug_id, "quantity": quantity, "prescription_code": code})
    session.modified = True
    flash(f"Dodano do koszyka: {drug['name']} × {quantity}.", "success")
    return redirect(url_for("sales.pos"))


@bp.route("/kasa/usun/<int:index>", methods=["POST"])
@login_required
def remove_from_cart(index):
    cart = _cart()
    if 0 <= index < len(cart):
        cart.pop(index)
        session.modified = True
    return redirect(url_for("sales.pos"))


@bp.route("/kasa/wyczysc", methods=["POST"])
@login_required
def clear_cart():
    session["cart"] = []
    flash("Koszyk wyczyszczony.", "info")
    return redirect(url_for("sales.pos"))


@bp.route("/kasa/zaplac", methods=["POST"])
@login_required
def checkout():
    method = request.form.get("payment_method", "")
    raw_cash = request.form.get("cash_received", "")
    cash = parse_pln(raw_cash) if method == "gotowka" and raw_cash.strip() else None
    if method == "gotowka" and raw_cash.strip() and cash is None:
        return _render_pos(form=request.form.to_dict(), error="Niepoprawna kwota otrzymana.", status=400)
    try:
        sale_id = services.create_sale(_cart(), method, cash, g.user["id"])
    except services.SaleError as e:
        return _render_pos(form=request.form.to_dict(), error=" ".join(e.errors), status=400)
    session["cart"] = []
    flash(f"Sprzedaż nr {sale_id} zakończona.", "success")
    return redirect(url_for("sales.receipt", sale_id=sale_id))


@bp.route("/sprzedaze/<int:sale_id>")
@login_required
def receipt(sale_id):
    sale, items = services.get_sale(sale_id)
    if sale is None:
        abort(404)
    return render_template("sales/receipt.html", sale=sale, items=items, payment_methods=PAYMENT_METHODS)


def _history_filters():
    return {
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "payment": request.args.get("payment", ""),
    }


@bp.route("/sprzedaze")
@login_required
def history():
    filters = _history_filters()
    page_size = current_app.config["PAGE_SIZE"]
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    error = None
    if filters["date_from"] and filters["date_to"] and filters["date_from"] > filters["date_to"]:
        error = "Data „od” nie może być późniejsza niż data „do”."
        sales, count, total_sum = [], 0, 0
    else:
        sales, count, total_sum = services.list_sales(page=page, page_size=page_size, **filters)
    return render_template(
        "sales/history.html",
        sales=sales, count=count, total_sum=total_sum, filters=filters, page=page,
        pages=max(math.ceil(count / page_size), 1), payment_methods=PAYMENT_METHODS, error=error,
    )


@bp.route("/sprzedaze/eksport.csv")
@login_required
def export_csv():
    sales, _, _ = services.list_sales(**_history_filters())
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["id", "data", "sprzedawca", "platnosc", "liczba_sztuk", "kwota"])
    for s in sales:
        writer.writerow([s["id"], s["created_at"], s["seller"], s["payment_method"], s["items_count"],
                         f"{s['total_grosze'] / 100:.2f}"])
    return Response(
        "﻿" + buf.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=sprzedaze.csv"},
    )
