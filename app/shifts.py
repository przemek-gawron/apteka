from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from . import services
from .auth import login_required
from .utils import parse_pln

bp = Blueprint("shifts", __name__, url_prefix="/zmiana")


@bp.route("/")
@login_required
def index():
    shift = services.current_shift(g.user["id"])
    expected = services.expected_cash(g.user["id"], shift["opened_at"]) if shift else None
    closed = services.list_closed_shifts() if g.user["role"] == "kierownik" else []
    return render_template("shifts/index.html", shift=shift, expected=expected, closed=closed)


@bp.route("/otworz", methods=["POST"])
@login_required
def open_shift():
    services.open_shift(g.user["id"])
    flash("Zmiana otwarta.", "success")
    return redirect(url_for("shifts.index"))


@bp.route("/zamknij", methods=["POST"])
@login_required
def close_shift():
    cash = parse_pln(request.form.get("cash_counted", ""))
    error = services.close_shift(g.user["id"], cash)
    flash(error or "Zmiana zamknięta.", "error" if error else "success")
    return redirect(url_for("shifts.index"))
