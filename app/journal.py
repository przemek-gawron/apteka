import math

from flask import Blueprint, current_app, render_template, request

from . import services
from .auth import login_required

bp = Blueprint("journal", __name__, url_prefix="/dziennik")


@bp.route("/")
@login_required
def index():
    action = request.args.get("action", "")
    if action not in services.AUDIT_ACTIONS:
        action = ""
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    page_size = current_app.config["PAGE_SIZE"]
    rows, total = services.list_audit(action=action, page=page, page_size=page_size)
    return render_template(
        "journal/list.html",
        rows=rows, total=total, action=action, actions=services.AUDIT_ACTIONS,
        page=page, pages=max(math.ceil(total / page_size), 1),
    )
