from flask import Blueprint, abort, flash, g, redirect, render_template, url_for

from . import services
from .auth import login_required

bp = Blueprint("orders", __name__, url_prefix="/zamowienia")


@bp.route("/")
@login_required
def index():
    return render_template("orders/list.html", orders=services.list_orders(), statuses=services.ORDER_STATUSES)


@bp.route("/z-brakow", methods=["POST"])
@login_required
def from_shortages():
    order_id = services.create_order_from_shortages(g.user["id"])
    if order_id is None:
        flash("Nie ma leków poniżej stanu minimalnego.", "info")
        return redirect(url_for("orders.index"))
    flash("Utworzono szkic zamówienia.", "success")
    return redirect(url_for("orders.detail", order_id=order_id))


@bp.route("/<int:order_id>")
@login_required
def detail(order_id):
    order, items = services.get_order(order_id)
    if order is None:
        abort(404)
    return render_template(
        "orders/detail.html", order=order, items=items, statuses=services.ORDER_STATUSES,
        next_status=services.ORDER_NEXT.get(order["status"]),
    )


@bp.route("/<int:order_id>/dalej", methods=["POST"])
@login_required
def advance(order_id):
    status, error = services.advance_order(order_id)
    if error:
        flash(error, "error")
    elif status == "wyslane":
        flash("Zamówienie wysłane do hurtowni.", "success")
    else:
        flash("Przyjęto dostawę z zamówienia. Stany magazynowe zostały zwiększone.", "success")
    return redirect(url_for("orders.detail", order_id=order_id))
