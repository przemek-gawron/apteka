"""Start aplikacji: python run.py  (baza tworzy się automatycznie przy pierwszym uruchomieniu)."""
import os
import sqlite3

from app import create_app
from app.db import SCHEMA_VERSION, init_db

app = create_app()


def _db_version(path):
    if not os.path.exists(path):
        return -1
    conn = sqlite3.connect(path)
    try:
        return conn.execute("PRAGMA user_version").fetchone()[0]
    finally:
        conn.close()


def ensure_db():
    with app.app_context():
        path = app.config["DATABASE"]
        stale = _db_version(path) != SCHEMA_VERSION
        if not os.path.exists(path) or os.environ.get("RESET_DB") == "1" or stale:
            init_db()
            return True
    return False


# Vercel importuje moduł i nie odpala __main__, więc bazę trzeba zasiać przy starcie funkcji.
if os.environ.get("VERCEL") == "1":
    ensure_db()

if __name__ == "__main__":
    if ensure_db():
        print("Utworzono bazę z danymi przykładowymi.")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("APP_ENV", "dev") == "dev")
