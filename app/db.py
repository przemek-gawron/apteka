import sqlite3

import click
from flask import current_app, g

SCHEMA_VERSION = 8

SCHEMA = """
DROP TABLE IF EXISTS return_items;
DROP TABLE IF EXISTS returns;
DROP TABLE IF EXISTS sale_allocations;
DROP TABLE IF EXISTS sale_items;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS batches;
DROP TABLE IF EXISTS shifts;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS interactions;
DROP TABLE IF EXISTS drugs;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('kierownik', 'farmaceuta'))
);

CREATE TABLE drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    active_substance TEXT NOT NULL,
    form TEXT NOT NULL,
    strength TEXT NOT NULL,
    category TEXT NOT NULL,
    price_grosze INTEGER NOT NULL,
    stock INTEGER NOT NULL,
    min_stock INTEGER NOT NULL,
    rx INTEGER NOT NULL DEFAULT 0,
    expiry_date TEXT NOT NULL,
    daily_limit INTEGER
);

CREATE TABLE batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL REFERENCES drugs (id) ON DELETE CASCADE,
    lot TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users (id),
    status TEXT NOT NULL CHECK (status IN ('szkic', 'wyslane', 'przyjete'))
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    drug_id INTEGER NOT NULL REFERENCES drugs (id),
    drug_name TEXT NOT NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    substance_a TEXT NOT NULL,
    substance_b TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users (id),
    total_grosze INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    cash_received_grosze INTEGER,
    invoice_nip TEXT,
    invoice_company TEXT
);

CREATE TABLE sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales (id) ON DELETE CASCADE,
    drug_id INTEGER REFERENCES drugs (id) ON DELETE SET NULL,
    drug_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_grosze INTEGER NOT NULL,
    prescription_code TEXT
);

CREATE TABLE returns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales (id),
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users (id),
    reason TEXT NOT NULL,
    total_grosze INTEGER NOT NULL
);

CREATE TABLE return_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id INTEGER NOT NULL REFERENCES returns (id) ON DELETE CASCADE,
    sale_item_id INTEGER NOT NULL REFERENCES sale_items (id),
    drug_id INTEGER REFERENCES drugs (id) ON DELETE SET NULL,
    drug_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price_grosze INTEGER NOT NULL
);

CREATE TABLE sale_allocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_item_id INTEGER NOT NULL REFERENCES sale_items (id) ON DELETE CASCADE,
    batch_id INTEGER REFERENCES batches (id) ON DELETE SET NULL,
    lot TEXT NOT NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users (id),
    opened_at TEXT NOT NULL,
    closed_at TEXT,
    cash_counted_grosze INTEGER,
    expected_cash_grosze INTEGER
);

CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    user_id INTEGER REFERENCES users (id),
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id INTEGER,
    details TEXT NOT NULL
);

CREATE INDEX idx_sales_created ON sales (created_at);
CREATE INDEX idx_audit_created ON audit_log (created_at);
CREATE INDEX idx_batches_drug ON batches (drug_id, expiry_date);
CREATE INDEX idx_items_sale ON sale_items (sale_id);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    from .seed import seed

    conn = get_db()
    conn.executescript(SCHEMA)
    seed(conn)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    conn.commit()


@click.command("init-db")
def init_db_command():
    """Tworzy bazę od zera i wypełnia ją danymi przykładowymi."""
    init_db()
    click.echo("Baza zainicjalizowana.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
