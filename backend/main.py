import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

from database import get_db, init_db, log_audit
from seed_data import seed_database
from engines.market_engine import get_market_history, get_seasonality_analysis, generate_price_forecast
from engines.landed_cost_engine import calculate_domestic_tlc, calculate_import_tlc, calculate_parity_spread, generate_parity_sensitivity_matrix
from engines.quality_engine import evaluate_batch_quality, get_supplier_quality_status
from engines.inventory_engine import get_current_inventory_status, project_daily_inventory
from engines.optimization_engine import run_procurement_optimization
from engines.scenario_engine import simulate_procurement_scenario
from agents.agents_core import run_agentic_orchestrator, run_market_agent, run_supplier_agent, run_quality_agent, run_inventory_agent, run_optimization_agent

app = FastAPI(
    title="SoyaSetu: Strategic Soybean Procurement Optimization System",
    description="Enterprise Decision-Support System for ABT-CPD / Soya Sakthi Crushing Units",
    version="2.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active user state session simulation
current_session = {
    "username": "proc_head",
    "full_name": "Vikramaditya Rao",
    "role": "Procurement Head",
    "email": "vikram.rao@abt-cpd.com"
}

# ----------------- LIFECYCLE -----------------
@app.on_event("startup")
def startup_event():
    seed_database()

# ----------------- 0. SYSTEM HEALTH & TELEMETRY -----------------
@app.get("/api/system/health")
def get_system_health():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM market_prices;")
    market_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM suppliers;")
    supplier_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM quality_reports;")
    quality_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM audit_logs;")
    audit_count = cursor.fetchone()[0]
    conn.close()

    return {
        "status": "healthy",
        "service": "SoyaSetu Decision Support System",
        "version": "2.4.0-enterprise",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "database": {
            "driver": "SQLite 3 (WAL mode)",
            "status": "connected",
            "market_records": market_count,
            "suppliers_registered": supplier_count,
            "quality_reports_indexed": quality_count,
            "audit_events_recorded": audit_count
        },
        "engine_telemetry": {
            "ml_model": "SARIMAX + LightGBM Ensemble",
            "optimization_solver": "Constrained Mixed-Integer Linear Optimization",
            "active_session": current_session
        }
    }

# ----------------- 1. AUTH & ROLES -----------------
@app.get("/api/auth/roles")
def get_roles():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, role, email FROM users;")
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    permissions_matrix = {
        "Super Admin": ["view_all", "edit_all", "approve_all", "configure_system", "manage_users"],
        "Procurement Head": ["view_all", "approve_recommendations", "modify_recommendations", "reject_recommendations", "export_reports"],
        "Procurement Officer": ["view_all", "enter_quotations", "update_market", "prepare_recommendations", "export_reports"],
        "Quality Manager": ["view_all", "configure_specs", "upload_lab_reports", "set_batch_quality", "export_reports"],
        "Inventory Manager": ["view_all", "update_inventory", "update_consumption", "manage_shipments", "export_reports"],
        "Finance Manager": ["view_all", "update_tariffs", "update_fx_assumptions", "review_budgets", "export_reports"],
        "Executive Viewer": ["view_all", "export_reports"]
    }
    
    return {
        "current_user": current_session,
        "available_users": users,
        "permissions_matrix": permissions_matrix
    }

class RoleSwitchRequest(BaseModel):
    username: str

@app.post("/api/auth/switch-role")
def switch_role(req: RoleSwitchRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, full_name, role, email FROM users WHERE username = ?;", (req.username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found.")
        
    current_session["username"] = row["username"]
    current_session["full_name"] = row["full_name"]
    current_session["role"] = row["role"]
    current_session["email"] = row["email"]
    
    log_audit(current_session["full_name"], current_session["role"], "ROLE_SWITCH", "User", req.username, f"Active role switched to {row['role']}")
    return {"status": "success", "current_user": current_session}

# ----------------- 2. EXECUTIVE DASHBOARD -----------------
@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    inv = get_current_inventory_status()
    mkt = get_market_history(1)
    
    dom_spot = mkt["latest_domestic_spot"]
    cbot_usd = mkt["latest_cbot_usd"]
    fx = mkt["latest_usd_inr"]
    
    dom_tlc = calculate_domestic_tlc(dom_spot)
    imp_tlc = calculate_import_tlc(cbot_usd, usd_inr_rate=fx)
    spread = calculate_parity_spread(dom_tlc, imp_tlc)
    
    # Active recommendations
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations ORDER BY id DESC LIMIT 1;")
    rec_row = cursor.fetchone()
    active_rec = dict(rec_row) if rec_row else None
    
    # Active alerts count
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE status = 'Active';")
    active_alerts_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE status = 'Active' AND severity = 'Critical';")
    critical_alerts_count = cursor.fetchone()[0]
    conn.close()
    
    # High-level action banner
    if inv["coverage_days"] <= inv["safety_stock_days"]:
        action_banner = {
            "type": "critical",
            "title": "SAFETY STOCK DEFICIT: IMMEDIATE DOMESTIC SPOT PURCHASE REQUIRED",
            "description": f"Available usable stock is {inv['available_usable_mt']:,.0f} MT ({inv['coverage_days']} days), which is below the mandatory {inv['safety_stock_days']}-day buffer. Procure 2,500 MT from Madhya Bharat Agro Co-op for rapid 5-day fulfillment."
        }
    elif spread["is_arbitrage_open"]:
        action_banner = {
            "type": "info",
            "title": "IMPORT ARBITRAGE WINDOW ACTIVE",
            "description": f"Import TLC is ₹{spread['parity_spread_mt']:,.2f}/MT cheaper than domestic. Contract international consignment from Brazil CIF."
        }
    else:
        action_banner = {
            "type": "success",
            "title": "SUPPLY CHAIN STABLE: BALANCED DOMESTIC SOURCING",
            "description": "Stock cover is adequate. Maintain routine replenishment orders with approved local mandis."
        }
        
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action_banner": action_banner,
        "kpis": {
            "available_usable_stock_mt": inv["available_usable_mt"],
            "coverage_days": inv["coverage_days"],
            "daily_crush_mt": inv["daily_crush_mt"],
            "safety_stock_mt": inv["safety_stock_mt"],
            "domestic_spot_inr": dom_spot,
            "domestic_tlc_inr": dom_tlc["total_landed_cost_mt"],
            "import_cif_usd": cbot_usd,
            "import_tlc_inr": imp_tlc["total_landed_cost_mt"],
            "parity_spread_inr": spread["parity_spread_mt"],
            "parity_recommendation": spread["recommendation"],
            "active_alerts_count": active_alerts_count,
            "critical_alerts_count": critical_alerts_count
        },
        "active_recommendation": active_rec
    }

# ----------------- 3. MARKET INTELLIGENCE -----------------
@app.get("/api/market/history")
def get_market_history_endpoint(days: int = Query(90, ge=10, le=365)):
    return get_market_history(days)

@app.get("/api/market/seasonality")
def get_seasonality_endpoint():
    return get_seasonality_analysis()

@app.get("/api/market/forecast")
def get_forecast_endpoint(horizon: int = Query(45, ge=7, le=90)):
    return generate_price_forecast(horizon)

class ManualPriceUpdateRequest(BaseModel):
    origin: str
    price: float
    currency: str = "INR"
    unit: str = "MT"
    usd_inr: float = 86.5
    source_notes: str = "Manual Market Quotation Update"

@app.post("/api/market/update-price")
def update_price_endpoint(req: ManualPriceUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
    INSERT INTO market_prices (date, origin, price, currency, unit, source, data_type, usd_inr, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (today_str, req.origin, req.price, req.currency, req.unit, req.source_notes, "Manual Entry", req.usd_inr, now_ts))
    
    conn.commit()
    conn.close()
    
    log_audit(current_session["full_name"], current_session["role"], "MARKET_PRICE_MANUAL_UPDATE", "MarketPrice", req.origin, f"Updated {req.origin} price to {req.price} {req.currency}")
    return {"status": "success", "message": f"Updated price for {req.origin} to {req.price} {req.currency}"}

# ----------------- 4. SUPPLIER INTELLIGENCE -----------------
@app.get("/api/suppliers")
def get_suppliers_endpoint():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.*, q.price_per_mt, q.currency, q.offered_qty_mt, q.min_order_qty_mt, q.lead_time_days, q.payment_terms, q.delivery_terms, q.valid_until
    FROM suppliers s
    LEFT JOIN quotations q ON s.id = q.supplier_id AND q.status = 'Active'
    WHERE s.is_active = 1
    ORDER BY s.rating_overall DESC;
    """)
    suppliers = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    # Enrich with quality qualification
    for s in suppliers:
        q_stat = get_supplier_quality_status(s["id"])
        s["is_quality_qualified"] = q_stat["is_qualified"]
        s["quality_pass_rate_pct"] = q_stat["pass_rate_pct"]
        
    return {"suppliers": suppliers}

@app.get("/api/suppliers/{supplier_id}")
def get_supplier_detail(supplier_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM suppliers WHERE id = ?;", (supplier_id,))
    sup = cursor.fetchone()
    if not sup:
        conn.close()
        raise HTTPException(status_code=404, detail="Supplier not found.")
    
    supplier = dict(sup)
    
    # Active quotes
    cursor.execute("SELECT * FROM quotations WHERE supplier_id = ? ORDER BY id DESC;", (supplier_id,))
    quotes = [dict(r) for r in cursor.fetchall()]
    
    # Recent quality reports
    cursor.execute("SELECT * FROM quality_reports WHERE supplier_id = ? ORDER BY sample_date DESC LIMIT 10;", (supplier_id,))
    quality_reports = [dict(r) for r in cursor.fetchall()]
    
    # Historical incoming shipments
    cursor.execute("SELECT * FROM incoming_shipments WHERE supplier_id = ? ORDER BY order_date DESC LIMIT 10;", (supplier_id,))
    shipments = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    
    q_status = get_supplier_quality_status(supplier_id)
    supplier["is_quality_qualified"] = q_status["is_qualified"]
    supplier["quality_pass_rate_pct"] = q_status["pass_rate_pct"]
    supplier["total_inspected_mt"] = q_status["total_inspected_mt"]
    supplier["total_accepted_mt"] = q_status["total_accepted_mt"]
    supplier["quotations"] = quotes
    supplier["quality_reports"] = quality_reports
    supplier["shipments"] = shipments
    
    return supplier

# ----------------- 5. QUALITY INTELLIGENCE -----------------
@app.get("/api/quality/specs")
def get_quality_specs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quality_specs;")
    specs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"specs": specs}

@app.get("/api/quality/reports")
def get_quality_reports():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.*, s.name as supplier_name, s.location
    FROM quality_reports r
    JOIN suppliers s ON r.supplier_id = s.id
    ORDER BY r.sample_date DESC;
    """)
    reports = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"reports": reports}

class BatchEvaluationRequest(BaseModel):
    moisture_pct: float
    protein_pct: float
    oil_pct: float
    foreign_matter_pct: float
    damaged_pct: float

@app.post("/api/quality/evaluate-batch")
def evaluate_batch_endpoint(req: BatchEvaluationRequest):
    return evaluate_batch_quality(
        req.moisture_pct,
        req.protein_pct,
        req.oil_pct,
        req.foreign_matter_pct,
        req.damaged_pct
    )

# ----------------- 6. INVENTORY DYNAMICS -----------------
@app.get("/api/inventory/status")
def get_inventory_status_endpoint():
    return get_current_inventory_status()

@app.get("/api/inventory/projection")
def get_inventory_projection_endpoint(days: int = Query(30, ge=7, le=60)):
    return project_daily_inventory(days)

class InventoryUpdateRequest(BaseModel):
    physical_stock_mt: float
    accepted_usable_mt: float
    reserved_mt: float
    daily_crush_mt: float
    safety_stock_mt: float

@app.post("/api/inventory/update")
def update_inventory_endpoint(req: InventoryUpdateRequest):
    if current_session["role"] not in ["Super Admin", "Inventory Manager", "Procurement Head"]:
        raise HTTPException(status_code=403, detail="Permission denied. Only Inventory Manager or Admin can update inventory records.")
        
    conn = get_db()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    available_usable = req.accepted_usable_mt - req.reserved_mt
    
    cursor.execute("""
    INSERT INTO inventory_records (date, physical_stock_mt, accepted_usable_mt, reserved_mt, available_usable_mt, daily_crush_mt, safety_stock_mt, max_capacity_mt)
    VALUES (?, ?, ?, ?, ?, ?, ?, 18000.0);
    """, (today_str, req.physical_stock_mt, req.accepted_usable_mt, req.reserved_mt, available_usable, req.daily_crush_mt, req.safety_stock_mt))
    
    conn.commit()
    conn.close()
    
    log_audit(current_session["full_name"], current_session["role"], "INVENTORY_RECORD_UPDATE", "Inventory", today_str, f"Updated stock to {req.physical_stock_mt} MT (Usable: {available_usable} MT)")
    return {"status": "success", "message": "Inventory updated successfully."}

# ----------------- 7. LANDED COST & PARITY -----------------
@app.get("/api/landed-cost/parity")
def get_landed_cost_parity(
    domestic_spot: Optional[float] = None,
    cbot_usd: Optional[float] = None,
    usd_inr: float = 86.5,
    import_duty_pct: float = 0.0,
    aidc_pct: float = 5.0
):
    if domestic_spot is None:
        mkt = get_market_history(1)
        domestic_spot = mkt["latest_domestic_spot"]
    if cbot_usd is None:
        mkt = get_market_history(1)
        cbot_usd = mkt["latest_cbot_usd"]
        
    dom = calculate_domestic_tlc(domestic_spot)
    imp = calculate_import_tlc(cbot_usd, usd_inr_rate=usd_inr, bcd_pct=import_duty_pct, aidc_pct=aidc_pct)
    spread = calculate_parity_spread(dom, imp)
    
    return {
        "domestic_tlc": dom,
        "import_tlc": imp,
        "spread_analysis": spread
    }

@app.get("/api/landed-cost/sensitivity")
def get_sensitivity_endpoint():
    mkt = get_market_history(1)
    return generate_parity_sensitivity_matrix(mkt["latest_domestic_spot"])

# ----------------- 8. PROCUREMENT OPTIMIZATION -----------------
@app.get("/api/optimization/run")
def get_optimization_endpoint():
    return run_procurement_optimization()

# ----------------- 9. AGENTIC AI CONTROL CENTRE -----------------
@app.get("/api/agents/control-center")
def get_agents_control_center():
    return run_agentic_orchestrator()

# ----------------- 10. REAL-TIME ALERTS -----------------
@app.get("/api/alerts")
def get_alerts_endpoint(category: Optional[str] = None, severity: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
    if severity and severity != "All":
        query += " AND severity = ?"
        params.append(severity)
        
    query += " ORDER BY id DESC;"
    cursor.execute(query, params)
    alerts = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"alerts": alerts}

@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE alerts SET status = 'Acknowledged', resolution_notes = ? WHERE id = ?;
    """, (f"Acknowledged by {current_session['full_name']} ({current_session['role']})", alert_id))
    conn.commit()
    conn.close()
    log_audit(current_session["full_name"], current_session["role"], "ALERT_ACKNOWLEDGE", "Alert", str(alert_id), "Acknowledged alert")
    return {"status": "success"}

@app.post("/api/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, notes: str = Body(..., embed=True)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE alerts SET status = 'Resolved', resolution_notes = ? WHERE id = ?;
    """, (f"Resolved by {current_session['full_name']}: {notes}", alert_id))
    conn.commit()
    conn.close()
    log_audit(current_session["full_name"], current_session["role"], "ALERT_RESOLVE", "Alert", str(alert_id), notes)
    return {"status": "success"}

# ----------------- 11. SCENARIO SIMULATOR -----------------
class ScenarioRequest(BaseModel):
    domestic_price_shock_pct: float = 0.0
    import_duty_pct: float = 0.0
    usd_inr_rate: float = 86.5
    ocean_freight_usd_mt: float = 42.0
    supplier_delay_days: int = 0
    quality_rejection_pct: float = 0.0

@app.post("/api/scenarios/simulate")
def simulate_scenario_endpoint(req: ScenarioRequest):
    return simulate_procurement_scenario(
        req.domestic_price_shock_pct,
        req.import_duty_pct,
        req.usd_inr_rate,
        req.ocean_freight_usd_mt,
        req.supplier_delay_days,
        req.quality_rejection_pct
    )

# ----------------- 12. RECOMMENDATIONS & APPROVAL WORKFLOW -----------------
@app.get("/api/recommendations")
def get_recommendations_endpoint():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.*, s.name as supplier_name
    FROM recommendations r
    LEFT JOIN suppliers s ON r.supplier_id = s.id
    ORDER BY r.id DESC;
    """)
    recs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    for rec in recs:
        if rec.get("alternatives_json"):
            try:
                rec["alternatives"] = json.loads(rec["alternatives_json"])
            except:
                rec["alternatives"] = []
    return {"recommendations": recs}

class RecommendationActionRequest(BaseModel):
    action: str # Approve, Modify, Reject
    notes: str
    modified_qty_mt: Optional[float] = None
    modified_channel: Optional[str] = None

@app.post("/api/recommendations/{rec_id}/action")
def act_on_recommendation(rec_id: int, req: RecommendationActionRequest):
    # Only Procurement Head or Super Admin can approve
    if current_session["role"] not in ["Procurement Head", "Super Admin"]:
        raise HTTPException(
            status_code=403,
            detail=f"Approval Authority Error: Current role '{current_session['role']}' cannot approve or reject recommendations. Please switch to 'Procurement Head'."
        )
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recommendations WHERE id = ?;", (rec_id,))
    rec = cursor.fetchone()
    if not rec:
        conn.close()
        raise HTTPException(status_code=404, detail="Recommendation docket not found.")
        
    new_status = "Approved" if req.action == "Approve" else ("Modified & Approved" if req.action == "Modify" else "Rejected")
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    qty = req.modified_qty_mt if (req.action == "Modify" and req.modified_qty_mt) else rec["recommended_qty_mt"]
    channel = req.modified_channel if (req.action == "Modify" and req.modified_channel) else rec["sourcing_channel"]
    
    cursor.execute("""
    UPDATE recommendations
    SET status = ?, approver_name = ?, approver_role = ?, approved_at = ?, approval_notes = ?, recommended_qty_mt = ?, sourcing_channel = ?
    WHERE id = ?;
    """, (new_status, current_session["full_name"], current_session["role"], now_ts, req.notes, qty, channel, rec_id))
    
    conn.commit()
    conn.close()
    
    log_audit(current_session["full_name"], current_session["role"], f"RECOMMENDATION_{req.action.upper()}", "Recommendation", str(rec_id), f"{new_status}: {req.notes}")
    return {"status": "success", "message": f"Recommendation #{rec_id} has been marked as '{new_status}'."}

# ----------------- 13. AUDIT TRAIL & EXPORT -----------------
@app.get("/api/audit/logs")
def get_audit_logs(limit: int = 50):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?;", (limit,))
    logs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"logs": logs}

@app.get("/api/audit/export-csv")
def export_csv(entity: str = "recommendations"):
    conn = get_db()
    cursor = conn.cursor()
    if entity == "recommendations":
        cursor.execute("SELECT id, created_at, status, recommended_action, recommended_qty_mt, target_buy_date, target_arrival_date, sourcing_channel, estimated_tlc_mt, approver_name, approved_at FROM recommendations;")
    elif entity == "market":
        cursor.execute("SELECT date, origin, price, currency, unit, source, data_type FROM market_prices ORDER BY date DESC LIMIT 100;")
    else:
        cursor.execute("SELECT id, timestamp, user_name, user_role, action, entity_type, details_json FROM audit_logs ORDER BY id DESC LIMIT 100;")
        
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return Response(content="No data", media_type="text/csv")
        
    cols = [d[0] for d in cursor.description]
    lines = [",".join(cols)]
    for r in rows:
        lines.append(",".join([f'"{str(val)}"' for val in r]))
        
    csv_content = "\n".join(lines)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=SoyaSetu_{entity}_export.csv"}
    )

# Mount frontend directory for static assets
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "SoyaSetu API operational. Frontend under compilation."}
