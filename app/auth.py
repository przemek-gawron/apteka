import functools

from flask import Blueprint, abort, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__)


def authenticate(username, password):
    user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user is None or not check_password_hash(user["password_hash"], password):
        return None
    return user


@bp.before_app_request
def load_user():
    user_id = session.get("user_id")
    g.user = None
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, full_name, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            if request.path.startswith("/api/"):
                return jsonify(error="Wymagane logowanie"), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(**kwargs)

    return wrapped


def manager_required(view):
    @functools.wraps(view)
    @login_required
    def wrapped(**kwargs):
        if g.user["role"] != "kierownik":
            if request.path.startswith("/api/"):
                return jsonify(error="Brak uprawnień — wymagana rola kierownika"), 403
            abort(403)
        return view(**kwargs)

    return wrapped


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None:
        return redirect(url_for("dashboard.index"))

    error = None
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            error = "Podaj login i hasło."
        else:
            user = authenticate(username, password)
            if user is None:
                error = "Nieprawidłowy login lub hasło."
            else:
                session.clear()
                session["user_id"] = user["id"]
                next_url = request.args.get("next", "")
                if not next_url.startswith("/") or next_url.startswith("//"):
                    next_url = url_for("dashboard.index")
                return redirect(next_url)

    return render_template("login.html", error=error, username=username)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Wylogowano.", "info")
    return redirect(url_for("auth.login"))


@bp.app_errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, message="Brak uprawnień do tej strony."), 403


@bp.app_errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify(error="Nie znaleziono"), 404
    return render_template("error.html", code=404, message="Nie znaleziono strony."), 404
