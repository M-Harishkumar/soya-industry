from datetime import datetime, timedelta
from database import get_db

def get_current_inventory_status():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT date, physical_stock_mt, accepted_usable_mt, reserved_mt, available_usable_mt, daily_crush_mt, safety_stock_mt, max_capacity_mt, lead_time_domestic_days, lead_time_import_days
    FROM inventory_records
    ORDER BY date DESC
    LIMIT 1;
    """)
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
        
    inv = dict(row)
    
    # Fetch confirmed incoming shipments
    cursor.execute("""
    SELECT s.po_number, s.supplier_id, sup.name as supplier_name, s.order_qty_mt, s.source_type, s.expected_arrival_date, s.status, s.landed_cost_mt
    FROM incoming_shipments s
    JOIN suppliers sup ON s.supplier_id = sup.id
    WHERE s.status IN ('In Transit', 'On Vessel', 'Confirmed');
    """)
    incoming = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    daily_crush = inv["daily_crush_mt"]
    available_usable = inv["available_usable_mt"]
    safety_stock = inv["safety_stock_mt"]
    
    # 1. Coverage Days
    coverage_days = round(available_usable / daily_crush, 1) if daily_crush > 0 else 0
    safety_stock_days = round(safety_stock / daily_crush, 1) if daily_crush > 0 else 0
    
    # 2. Reorder Point (Domestic Lead Time 7d)
    lead_time_dom = inv["lead_time_domestic_days"]
    lead_time_imp = inv["lead_time_import_days"]
    rop_domestic = (daily_crush * lead_time_dom) + safety_stock
    rop_import = (daily_crush * lead_time_imp) + safety_stock
    
    # 3. Urgency Flag
    is_safety_breached = (available_usable < safety_stock)
    is_below_dom_rop = (available_usable < rop_domestic)
    
    # 4. Total incoming confirmed
    total_incoming_mt = sum(item["order_qty_mt"] for item in incoming)
    
    # 5. Net Requirement over 30 days
    planning_horizon_days = 30
    demand_30d = daily_crush * planning_horizon_days
    desired_ending_stock = safety_stock
    net_requirement_30d = max(0.0, demand_30d + desired_ending_stock - available_usable - total_incoming_mt)
    
    return {
        "snapshot_date": inv["date"],
        "physical_stock_mt": inv["physical_stock_mt"],
        "accepted_usable_mt": inv["accepted_usable_mt"],
        "reserved_mt": inv["reserved_mt"],
        "available_usable_mt": available_usable,
        "daily_crush_mt": daily_crush,
        "safety_stock_mt": safety_stock,
        "max_capacity_mt": inv["max_capacity_mt"],
        "coverage_days": coverage_days,
        "safety_stock_days": safety_stock_days,
        "rop_domestic_mt": rop_domestic,
        "rop_import_mt": rop_import,
        "is_safety_breached": is_safety_breached,
        "is_below_dom_rop": is_below_dom_rop,
        "total_incoming_mt": total_incoming_mt,
        "net_requirement_30d_mt": round(net_requirement_30d, 1),
        "incoming_shipments": incoming
    }

def project_daily_inventory(days_ahead: int = 30):
    status = get_current_inventory_status()
    if not status:
        return []
        
    start_date = datetime.strptime(status["snapshot_date"], "%Y-%m-%d").date()
    daily_crush = status["daily_crush_mt"]
    safety_stock = status["safety_stock_mt"]
    current_stock = status["available_usable_mt"]
    incoming = status["incoming_shipments"]
    
    # Map incoming by arrival date
    incoming_by_date = {}
    for ship in incoming:
        arr_date = ship["expected_arrival_date"]
        incoming_by_date[arr_date] = incoming_by_date.get(arr_date, 0) + ship["order_qty_mt"]
        
    timeline = []
    sim_stock = current_stock
    stockout_date = None
    safety_breach_date = None
    
    for i in range(days_ahead):
        d = start_date + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        
        # Add incoming on that date
        shipment_in = incoming_by_date.get(d_str, 0)
        sim_stock += shipment_in
        
        # Subtract daily crush
        sim_stock -= daily_crush
        
        if sim_stock < safety_stock and not safety_breach_date:
            safety_breach_date = d_str
        if sim_stock <= 0 and not stockout_date:
            stockout_date = d_str
            
        timeline.append({
            "day": i + 1,
            "date": d_str,
            "stock_mt": round(max(0, sim_stock), 1),
            "safety_stock_mt": safety_stock,
            "incoming_mt": shipment_in,
            "coverage_days": round(max(0, sim_stock) / daily_crush, 1)
        })
        
    return {
        "timeline": timeline,
        "current_stock_mt": current_stock,
        "stockout_date": stockout_date,
        "safety_breach_date": safety_breach_date,
        "critical_alert": bool(stockout_date or safety_breach_date)
    }

if __name__ == "__main__":
    s = get_current_inventory_status()
    print("Coverage Days:", s["coverage_days"])
    print("Net Req 30d:", s["net_requirement_30d_mt"])
    p = project_daily_inventory(30)
    print("Safety Breach Date:", p["safety_breach_date"], "Stockout Date:", p["stockout_date"])
