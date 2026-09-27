from datetime import timedelta

from flask import Blueprint, render_template

from . import services
from .auth import login_required
from .db import get_db
from .utils import EXPIRY_WARNING_DAYS, today

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    db = get_db()
    low_stock = db.execute(
        "SELECT * FROM drugs WHERE stock <= min_stock ORDER BY stock - min_stock, name LIMIT 8"
    ).fetchall()
    expiring = db.execute(
        "SELECT * FROM drugs WHERE expiry_date <= ? ORDER BY expiry_date LIMIT 8",
        ((today() + timedelta(days=EXPIRY_WARNING_DAYS)).isoformat(),),
    ).fetchall()
    return render_template(
        "dashboard.html",
        summary=services.stats_summary(), low_stock=low_stock, expiring=expiring, today=today(),
    )
