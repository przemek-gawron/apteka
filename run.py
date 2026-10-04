"""Start aplikacji: python run.py  (baza tworzy się automatycznie przy pierwszym uruchomieniu)."""
import os

from app import create_app
from app.db import init_db

app = create_app()


def ensure_db():
    with app.app_context():
        if not os.path.exists(app.config["DATABASE"]) or os.environ.get("RESET_DB") == "1":
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
