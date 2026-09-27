import math

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from . import services
from .auth import login_required, manager_required
from .db import get_db
from .utils import CATEGORIES, FORMS, drug_status

bp = Blueprint("drugs", __name__, url_prefix="/leki")


def _page_arg():
    try:
        return max(int(request.args.get("page", 1)), 1)
    except ValueError:
        return 1


@bp.route("/")
@login_required
def index():
    filters = {
        "q": request.args.get("q", "").strip(),
        "category": request.args.get("category", ""),
        "rx": request.args.get("rx", ""),
        "status": request.args.get("status", ""),
        "sort": request.args.get("sort", "name"),
        "order": request.args.get("order", "asc"),
    }
    page_size = current_app.config["PAGE_SIZE"]
    page = _page_arg()
    drugs, total = services.list_drugs(page=page, page_size=page_size, **filters)
    pages = max(math.ceil(total / page_size), 1)
    if page > pages:
        return redirect(url_for("drugs.index", **dict(filters, page=pages)))
    return render_template(
        "drugs/list.html",
        drugs=drugs, total=total, page=page, pages=pages, filters=filters,
        categories=CATEGORIES, drug_status=drug_status,
    )


@bp.route("/nowy", methods=["GET", "POST"])
@login_required
def create():
    values, errors = {"form": "tabletki", "stock": "0", "min_stock": "10"}, {}
    if request.method == "POST":
        values = request.form.to_dict()
        clean, errors = services.validate_drug(values)
        if not errors:
            drug_id = services.insert_drug(clean)
            flash(f"Dodano lek {clean['name']}.", "success")
            return redirect(url_for("drugs.detail", drug_id=drug_id))
    return render_template("drugs/form.html", values=values, errors=errors, drug=None,
                           categories=CATEGORIES, forms=FORMS)


@bp.route("/<int:drug_id>")
@login_required
def detail(drug_id):
    drug = services.get_drug(drug_id) or abort(404)
    recent = get_db().execute(
        """SELECT s.id, s.created_at, i.quantity, i.unit_price_grosze
           FROM sale_items i JOIN sales s ON s.id = i.sale_id
           WHERE i.drug_id = ? ORDER BY s.created_at DESC LIMIT 10""",
        (drug_id,),
    ).fetchall()
    interactions = services.find_interactions(
        [drug["active_substance"]],
        [r[0] for r in get_db().execute("SELECT DISTINCT active_substance FROM drugs")],
    )
    return render_template("drugs/detail.html", drug=drug, recent=recent,
                           interactions=interactions, statuses=drug_status(drug))


@bp.route("/<int:drug_id>/edycja", methods=["GET", "POST"])
@login_required
def edit(drug_id):
    drug = services.get_drug(drug_id) or abort(404)
    values, errors = services.drug_form_values(drug), {}
    if request.method == "POST":
        values = request.form.to_dict()
        clean, errors = services.validate_drug(values, drug_id=drug_id)
        if not errors:
            services.update_drug(drug_id, clean)
            flash(f"Zapisano zmiany: {clean['name']}.", "success")
            return redirect(url_for("drugs.detail", drug_id=drug_id))
    return render_template("drugs/form.html", values=values, errors=errors, drug=drug,
                           categories=CATEGORIES, forms=FORMS)


@bp.route("/<int:drug_id>/dostawa", methods=["POST"])
@login_required
def restock(drug_id):
    drug = services.get_drug(drug_id) or abort(404)
    raw = request.form.get("quantity", "").strip()
    if not raw.isdigit() or not 1 <= int(raw) <= 1000:
        flash("Ilość w dostawie musi być liczbą od 1 do 1000.", "error")
    else:
        services.restock(drug_id, int(raw))
        flash(f"Przyjęto dostawę: {drug['name']} +{raw} szt.", "success")
    return redirect(url_for("drugs.detail", drug_id=drug_id))


@bp.route("/<int:drug_id>/usun", methods=["POST"])
@manager_required
def delete(drug_id):
    drug = services.get_drug(drug_id) or abort(404)
    services.delete_drug(drug_id)
    flash(f"Usunięto lek {drug['name']}.", "success")
    return redirect(url_for("drugs.index"))
