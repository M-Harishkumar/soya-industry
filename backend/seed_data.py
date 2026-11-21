import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from database import get_db, init_db, DB_PATH

def seed_database(force_reseed=False):
    if force_reseed and os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except:
            pass

    init_db()
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] > 0 and not force_reseed:
        conn.close()
        return

    print("Seeding SoyaSetu database with enterprise ABT-CPD baseline data (Units: INR/MT)...")

    # 1. Users
    users = [
        ("admin", "Rajesh Sharma", "Super Admin", "rajesh.admin@abt-cpd.com"),
        ("proc_head", "Vikramaditya Rao", "Procurement Head", "vikram.rao@abt-cpd.com"),
        ("proc_officer", "Ananya Deshmukh", "Procurement Officer", "ananya.d@abt-cpd.com"),
        ("quality_mgr", "Dr. Santosh Kulkarni", "Quality Manager", "santosh.k@abt-cpd.com"),
        ("inv_mgr", "Mahesh Patel", "Inventory Manager", "mahesh.p@abt-cpd.com"),
        ("fin_mgr", "Siddharth Jain", "Finance Manager", "siddharth.j@abt-cpd.com"),
        ("exec_viewer", "Gopalakrishnan Nair", "Executive Viewer", "g.nair@abt-cpd.com")
    ]
    cursor.executemany("INSERT INTO users (username, full_name, role, email) VALUES (?, ?, ?, ?)", users)

    # 2. Approved Quality Specifications
    specs = [
        ("Moisture Content", "%", None, 10.0, 1, "Max 10% allowed. Above 12% risks fungal heating and rancidity in silos."),
        ("Crude Protein (Dry Basis)", "%", 38.0, None, 1, "Min 38% required for premium high-protein de-oiled cake (DOC)."),
        ("Crude Oil Content", "%", 18.5, None, 1, "Min 18.5% required for standard solvent extraction plant yield."),
        ("Foreign Matter & Sand", "%", None, 2.0, 1, "Max 2.0% extraneous organic/inorganic matter."),
        ("Damaged & Weeviled Grains", "%", None, 3.0, 1, "Max 3.0% broken, insect-damaged or discolored seeds.")
    ]
    cursor.executemany("""
    INSERT INTO quality_specs (parameter_name, unit, min_limit, max_limit, is_mandatory, description)
    VALUES (?, ?, ?, ?, ?, ?)
    """, specs)

    # 3. Suppliers & Dealers
    suppliers = [
        ("Madhya Bharat Agro Co-op", "Indore Mandi, MP", "India", "Domestic", "sales@mb-agro.coop", 4.6, 92.5, 94.0, 88.0, 96.0, 98.0, 90.0, 48),
        ("Kisan Krishi Federation", "Latur APMC, Maharashtra", "India", "Domestic", "procure@kisankrishi.org", 4.3, 89.0, 91.0, 90.5, 93.0, 95.0, 88.0, 36),
        ("Mahavir Grain Traders", "Kota Mandi, Rajasthan", "India", "Domestic", "info@mahavirgrain.in", 3.8, 78.0, 82.0, 94.0, 85.0, 86.0, 85.0, 19),
        ("Cargill Brasil S/A", "Paranaguá / Santos", "Brazil", "International", "grain.desk.br@cargill.com", 4.8, 96.0, 89.0, 91.0, 98.0, 99.0, 92.0, 24),
        ("Bunge Agritrade SA", "Rosario Port", "Argentina", "International", "commercial.ar@bunge.com", 4.5, 94.0, 87.0, 92.0, 97.0, 98.0, 90.0, 18)
    ]
    cursor.executemany("""
    INSERT INTO suppliers (name, location, country, origin_type, contact_email, rating_overall, quality_score, delivery_score, price_score, fulfilment_score, compliance_score, commercial_score, transaction_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, suppliers)

    # 4. Active Quotations (Units: INR/MT and USD/MT)
    today = datetime.now().date()
    validity = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    quotes = [
        (1, today.strftime("%Y-%m-%d"), validity, 46200.0, "INR", 3500.0, 500.0, 5, "Net 15 Days", "FOR Crushing Plant", "Active"),
        (2, today.strftime("%Y-%m-%d"), validity, 45800.0, "INR", 2800.0, 500.0, 7, "Net 21 Days", "FOR Crushing Plant", "Active"),
        (3, today.strftime("%Y-%m-%d"), validity, 43500.0, "INR", 2000.0, 400.0, 6, "Advance 20%, Balance on Delivery", "Ex-Mandi Kota", "Active"), # CHEAP BUT POOR QUALITY
        (4, today.strftime("%Y-%m-%d"), validity, 485.0, "USD", 10000.0, 4500.0, 42, "Letter of Credit (LC) 90 Days", "CIF Nhava Sheva", "Active"),
        (5, today.strftime("%Y-%m-%d"), validity, 478.0, "USD", 8000.0, 4500.0, 45, "Letter of Credit (LC) 90 Days", "CIF Kandla", "Active")
    ]
    cursor.executemany("""
    INSERT INTO quotations (supplier_id, quote_date, valid_until, price_per_mt, currency, offered_qty_mt, min_order_qty_mt, lead_time_days, payment_terms, delivery_terms, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, quotes)

    # 5. Quality Batch Inspection Reports
    lab_reports = [
        ("BAT-2026-IND-091", 1, (today - timedelta(days=3)).strftime("%Y-%m-%d"), "Pre-Dispatch Sample", 9.4, 38.8, 19.1, 1.4, 2.1, "Passed", "SGS India Lab, Indore", 1200.0, 1200.0, 0.0, "Fully compliant with ABT-CPD Soya Sakthi standards."),
        ("BAT-2026-LAT-044", 2, (today - timedelta(days=5)).strftime("%Y-%m-%d"), "Arrival Sample", 9.8, 38.2, 18.9, 1.8, 2.7, "Passed", "Vimta Labs, Pune", 800.0, 800.0, 0.0, "Accepted. Moisture near upper boundary, process within 20 days."),
        ("BAT-2026-KOT-012", 3, (today - timedelta(days=2)).strftime("%Y-%m-%d"), "Arrival Sample", 13.4, 35.6, 17.2, 4.5, 5.8, "Rejected", "National Collateral Lab, Kota", 600.0, 0.0, 600.0, "HARD REJECT: Excessive moisture (13.4% > 10%) and foreign sand (4.5% > 2%). High FFA risk."),
        ("BAT-2026-BRZ-882", 4, (today - timedelta(days=12)).strftime("%Y-%m-%d"), "Pre-Shipment Discharge", 9.1, 39.4, 19.6, 1.1, 1.5, "Passed", "Bureau Veritas, Santos", 5000.0, 5000.0, 0.0, "Certified Non-GMO, export grade sound yellow soybean.")
    ]
    cursor.executemany("""
    INSERT INTO quality_reports (batch_id, supplier_id, sample_date, inspection_type, moisture_pct, protein_pct, oil_pct, foreign_matter_pct, damaged_pct, status, lab_name, inspected_qty_mt, accepted_qty_mt, rejected_qty_mt, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, lab_reports)

    # 6. Current Inventory Snapshot
    cursor.execute("""
    INSERT INTO inventory_records (date, physical_stock_mt, accepted_usable_mt, reserved_mt, available_usable_mt, daily_crush_mt, safety_stock_mt, max_capacity_mt, lead_time_domestic_days, lead_time_import_days)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (today.strftime("%Y-%m-%d"), 4800.0, 4200.0, 600.0, 3600.0, 300.0, 4500.0, 18000.0, 7, 45))

    # 7. Incoming Shipments Pipeline
    shipments = [
        ("PO-2026-DOM-104", 1, 1500.0, "Domestic", (today - timedelta(days=4)).strftime("%Y-%m-%d"), (today + timedelta(days=2)).strftime("%Y-%m-%d"), None, "In Transit", 48000.0),
        ("PO-2026-IMP-019", 4, 4500.0, "International", (today - timedelta(days=25)).strftime("%Y-%m-%d"), (today + timedelta(days=20)).strftime("%Y-%m-%d"), None, "On Vessel", 46000.0)
    ]
    cursor.executemany("""
    INSERT INTO incoming_shipments (po_number, supplier_id, order_qty_mt, source_type, order_date, expected_arrival_date, actual_arrival_date, status, landed_cost_mt)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, shipments)

    # 8. Historical & Current Market Prices (Last 120 Business Days)
    np.random.seed(42)
    dates = pd.date_range(end=today, periods=120, freq="B")
    price_records = []
    
    base_spot = 44500.0
    base_cbot = 475.0
    usd_inr = 86.5
    
    for i, d in enumerate(dates):
        d_str = d.strftime("%Y-%m-%d")
        day_of_year = d.dayofyear if hasattr(d, 'dayofyear') else d.day_of_year
        seasonality = -2800 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        spot_price = round(base_spot + seasonality + np.random.normal(0, 450), 1)
        cbot_price = round(base_cbot + (seasonality / 86.5) * 0.12 + np.random.normal(0, 6), 1)
        
        # Indore Domestic Spot
        price_records.append((d_str, "Indore Mandi (Spot)", spot_price, "INR", "MT", "Agmarknet Mandi Feed", "Actual", usd_inr, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        # CBOT Futures (Converted to $/MT)
        price_records.append((d_str, "CBOT Futures Active", cbot_price, "USD", "MT", "CBOT Benchmark Feed", "Actual", usd_inr, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    cursor.executemany("""
    INSERT INTO market_prices (date, origin, price, currency, unit, source, data_type, usd_inr, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, price_records)

    # 9. Initial Real-time Alerts
    alerts = [
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Inventory", "Critical", "Safety Stock Breach Looming", "Available usable stock is 3,600 MT (12.0 days coverage), which is below the mandatory 15-day safety buffer. Immediate domestic replenishment needed.", "Inventory Intelligence Agent", "Silo Complex A", "Active", None),
        ((datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), "Quality", "Critical", "Mandatory Quality Gate Triggered", "Batch BAT-2026-KOT-012 from Mahavir Grain Traders failed moisture spec (13.4% > 10.0%) and foreign matter (4.5% > 2.0%). Batch hard-rejected.", "Quality Intelligence Agent", "Mahavir Grain Traders", "Active", None),
        ((datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"), "Market", "Warning", "Post-Harvest Window Closing", "Indore Mandi arrivals tapering by 12% week-on-week. Spot prices projected to increase +4.8% over next 21 days.", "Market Intelligence Agent", "Indore APMC", "Active", None),
        ((datetime.now() - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S"), "Supplier", "Informational", "Quotation Update Received", "Cargill Brasil CIF Nhava Sheva quote updated to $485/MT with 90-day LC payment terms.", "Supplier Intelligence Agent", "Cargill Brasil", "Acknowledged", "Reviewed by Procurement Officer")
    ]
    cursor.executemany("""
    INSERT INTO alerts (timestamp, category, severity, title, message, source, affected_entity, status, resolution_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, alerts)

    # 10. Initial Active Recommendation
    alternatives = [
        {
            "plan_name": "Plan A: Immediate Domestic Spot Replenishment (Recommended)",
            "supplier": "Madhya Bharat Agro Co-op (Indore)",
            "quantity_mt": 2500,
            "channel": "Domestic Mandi",
            "est_tlc_mt": 48002.8,
            "lead_time_days": 5,
            "arrival_cover_days": 20.3,
            "trade_off": "Fastest fulfillment (5 days), fully restores 15-day safety cushion, lowest immediate cash lockup."
        },
        {
            "plan_name": "Plan B: Split Sourcing (60% Domestic + 40% International)",
            "supplier": "Kisan Krishi Fed (1,800 MT) + Cargill Brasil (4,500 MT)",
            "quantity_mt": 6300,
            "channel": "Hybrid Sourcing",
            "est_tlc_mt": 46900.0,
            "lead_time_days": 42,
            "arrival_cover_days": 35.0,
            "trade_off": "Hedges medium-term price spikes, but requires letter of credit commitment for 42-day vessel."
        },
        {
            "plan_name": "Plan C: Hand-to-Mouth Deferral",
            "supplier": "Daily Spot Purchases",
            "quantity_mt": 900,
            "channel": "Local Spot Only",
            "est_tlc_mt": 48150.0,
            "lead_time_days": 3,
            "arrival_cover_days": 13.0,
            "trade_off": "Avoids pre-buying, but exposes plant to imminent stockout risk if mandi supply is disrupted."
        }
    ]
    cursor.execute("""
    INSERT INTO recommendations (created_at, status, recommended_action, recommended_qty_mt, target_buy_date, target_arrival_date, sourcing_channel, supplier_id, estimated_tlc_mt, cost_per_usable_mt, current_stock_cover_days, projected_stock_cover_days, risk_level, why_preferred, alternatives_json, confidence_pct, approver_name, approver_role, approved_at, approval_notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        today.strftime("%Y-%m-%d %H:%M:%S"),
        "Submitted for Review",
        "PROCURE 2,500 MT DOMESTIC SPOT (CRITICAL SAFETY REPLENISHMENT)",
        2500.0,
        today.strftime("%Y-%m-%d"),
        (today + timedelta(days=5)).strftime("%Y-%m-%d"),
        "Domestic Mandi (Madhya Bharat Agro Co-op)",
        1,
        48002.8,
        48002.8,
        12.0,
        20.3,
        "Moderate",
        "Current usable inventory is at 12.0 days, breaching the 15-day critical safety stock. Domestic spot (TLC ₹48,002.80/MT) delivers in 5 days vs 42 days for sea vessels. While import TLC (₹46,000.80/MT) is ₹2,002 cheaper, an import consignment cannot prevent immediate plant idling. Mahavir Grain's cheaper quote was excluded due to failing mandatory moisture and sand thresholds.",
        json.dumps(alternatives),
        88.5,
        None,
        None,
        None,
        None
    ))

    # 11. Initial Audit Trail Logs
    logs = [
        (today.strftime("%Y-%m-%d 08:30:00"), "system", "System Engine", "SYSTEM_STARTUP", "Application", "1", "SoyaSetu core services initialized with database in WAL mode."),
        (today.strftime("%Y-%m-%d 09:15:00"), "Dr. Santosh Kulkarni", "Quality Manager", "QUALITY_INSPECTION_RECORDED", "Batch", "BAT-2026-KOT-012", "Recorded inspection: FAILED moisture (13.4%) and sand (4.5%). Marked batch as REJECTED."),
        (today.strftime("%Y-%m-%d 10:00:00"), "Ananya Deshmukh", "Procurement Officer", "QUOTATION_INGESTION", "Quotation", "1", "Ingested active quotation for Madhya Bharat Agro Co-op: ₹46,200/MT, valid for 7 days."),
        (today.strftime("%Y-%m-%d 10:45:00"), "system", "Agent Orchestrator", "RECOMMENDATION_GENERATED", "Recommendation", "1", "Orchestrator synthesized 6 agent findings into Recommendation #1.")
    ]
    cursor.executemany("""
    INSERT INTO audit_logs (timestamp, user_name, user_role, action, entity_type, entity_id, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, logs)

    conn.commit()
    conn.close()
    print("Database re-seeded successfully.")

if __name__ == "__main__":
    seed_database(force_reseed=True)
