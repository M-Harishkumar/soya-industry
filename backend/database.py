import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "soyasetu.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Enable WAL mode for high concurrency
    cursor.execute("PRAGMA journal_mode=WAL;")
    
    # 1. Users & Roles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    );
    """)
    
    # 2. Market Prices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        origin TEXT NOT NULL,
        price REAL NOT NULL,
        currency TEXT NOT NULL,
        unit TEXT NOT NULL,
        source TEXT NOT NULL,
        data_type TEXT NOT NULL,
        usd_inr REAL DEFAULT 86.5,
        created_at TEXT NOT NULL
    );
    """)
    
    # 3. Suppliers & Dealers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        location TEXT NOT NULL,
        country TEXT NOT NULL,
        origin_type TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        rating_overall REAL NOT NULL,
        quality_score REAL NOT NULL,
        delivery_score REAL NOT NULL,
        price_score REAL NOT NULL,
        fulfilment_score REAL NOT NULL,
        compliance_score REAL NOT NULL,
        commercial_score REAL NOT NULL,
        transaction_count INTEGER NOT NULL,
        is_active INTEGER DEFAULT 1
    );
    """)
    
    # 4. Supplier Quotations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quotations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER NOT NULL,
        quote_date TEXT NOT NULL,
        valid_until TEXT NOT NULL,
        price_per_mt REAL NOT NULL,
        currency TEXT NOT NULL,
        offered_qty_mt REAL NOT NULL,
        min_order_qty_mt REAL NOT NULL,
        lead_time_days INTEGER NOT NULL,
        payment_terms TEXT NOT NULL,
        delivery_terms TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    );
    """)
    
    # 5. Quality Specifications (Approved by ABT-CPD)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quality_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parameter_name TEXT UNIQUE NOT NULL,
        unit TEXT NOT NULL,
        min_limit REAL,
        max_limit REAL,
        is_mandatory INTEGER NOT NULL,
        description TEXT
    );
    """)
    
    # 6. Quality Batch Inspection Reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quality_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT UNIQUE NOT NULL,
        supplier_id INTEGER NOT NULL,
        sample_date TEXT NOT NULL,
        inspection_type TEXT NOT NULL,
        moisture_pct REAL NOT NULL,
        protein_pct REAL NOT NULL,
        oil_pct REAL NOT NULL,
        foreign_matter_pct REAL NOT NULL,
        damaged_pct REAL NOT NULL,
        status TEXT NOT NULL,
        lab_name TEXT NOT NULL,
        inspected_qty_mt REAL NOT NULL,
        accepted_qty_mt REAL NOT NULL,
        rejected_qty_mt REAL NOT NULL,
        notes TEXT,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    );
    """)
    
    # 7. Inventory Snapshots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        physical_stock_mt REAL NOT NULL,
        accepted_usable_mt REAL NOT NULL,
        reserved_mt REAL NOT NULL,
        available_usable_mt REAL NOT NULL,
        daily_crush_mt REAL NOT NULL,
        safety_stock_mt REAL NOT NULL,
        max_capacity_mt REAL NOT NULL,
        lead_time_domestic_days INTEGER DEFAULT 7,
        lead_time_import_days INTEGER DEFAULT 45
    );
    """)
    
    # 8. Incoming Shipments (Pipeline)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incoming_shipments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_number TEXT UNIQUE NOT NULL,
        supplier_id INTEGER NOT NULL,
        order_qty_mt REAL NOT NULL,
        source_type TEXT NOT NULL,
        order_date TEXT NOT NULL,
        expected_arrival_date TEXT NOT NULL,
        actual_arrival_date TEXT,
        status TEXT NOT NULL,
        landed_cost_mt REAL NOT NULL,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    );
    """)
    
    # 9. Procurement Recommendations & Approval Docket
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL,
        recommended_action TEXT NOT NULL,
        recommended_qty_mt REAL NOT NULL,
        target_buy_date TEXT NOT NULL,
        target_arrival_date TEXT NOT NULL,
        sourcing_channel TEXT NOT NULL,
        supplier_id INTEGER,
        estimated_tlc_mt REAL NOT NULL,
        cost_per_usable_mt REAL NOT NULL,
        current_stock_cover_days REAL NOT NULL,
        projected_stock_cover_days REAL NOT NULL,
        risk_level TEXT NOT NULL,
        why_preferred TEXT NOT NULL,
        alternatives_json TEXT NOT NULL,
        confidence_pct REAL NOT NULL,
        approver_name TEXT,
        approver_role TEXT,
        approved_at TEXT,
        approval_notes TEXT,
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    );
    """)
    
    # 10. Real-time Alerts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        source TEXT NOT NULL,
        affected_entity TEXT,
        status TEXT NOT NULL,
        resolution_notes TEXT
    );
    """)
    
    # 11. Immutable Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_name TEXT NOT NULL,
        user_role TEXT NOT NULL,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT,
        details_json TEXT
    );
    """)
    
    conn.commit()
    conn.close()

def log_audit(user_name, user_role, action, entity_type, entity_id=None, details=None):
    conn = get_db()
    cursor = conn.cursor()
    details_str = json.dumps(details) if isinstance(details, (dict, list)) else (details or "")
    cursor.execute("""
    INSERT INTO audit_logs (timestamp, user_name, user_role, action, entity_type, entity_id, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_name, user_role, action, entity_type, str(entity_id) if entity_id else "", details_str))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
