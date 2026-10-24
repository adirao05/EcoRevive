import os, sqlite3
from pathlib import Path
DB_PATH = Path(os.getenv("ECOREVIVE_DB", str(Path(__file__).resolve().parents[1] / "data" / "ecorevive.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def connect():
    c = sqlite3.connect(DB_PATH, timeout=20)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS products(
          product_id TEXT PRIMARY KEY, category TEXT NOT NULL, brand TEXT NOT NULL, model TEXT NOT NULL,
          manufacture_year INTEGER NOT NULL, region TEXT NOT NULL, battery_health REAL, repair_count INTEGER NOT NULL,
          functional_status TEXT NOT NULL, repair_cost REAL NOT NULL, resale_value REAL NOT NULL,
          material_value REAL NOT NULL, hazard_level REAL NOT NULL, lifecycle_status TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS predictions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL, return_probability REAL NOT NULL,
          pathway TEXT NOT NULL, pathway_confidence REAL NOT NULL, recovery_value REAL NOT NULL,
          priority_score REAL NOT NULL, model_version TEXT NOT NULL, created_at TEXT NOT NULL,
          FOREIGN KEY(product_id) REFERENCES products(product_id)
        );
        CREATE TABLE IF NOT EXISTS lifecycle_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL, event_type TEXT NOT NULL,
          actor TEXT NOT NULL, notes TEXT NOT NULL, evidence_hash TEXT NOT NULL, previous_hash TEXT NOT NULL,
          event_hash TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL,
          FOREIGN KEY(product_id) REFERENCES products(product_id)
        );
        CREATE TABLE IF NOT EXISTS collection_requests(
          id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL UNIQUE, region TEXT NOT NULL,
          latitude REAL NOT NULL, longitude REAL NOT NULL, status TEXT NOT NULL DEFAULT 'OPEN',
          priority_score REAL NOT NULL DEFAULT 0, assigned_facility TEXT, route_order INTEGER,
          FOREIGN KEY(product_id) REFERENCES products(product_id)
        );
        """)
