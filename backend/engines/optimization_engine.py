from datetime import datetime, timedelta
from database import get_db
from engines.inventory_engine import get_current_inventory_status
from engines.landed_cost_engine import calculate_domestic_tlc, calculate_import_tlc, calculate_parity_spread
from engines.quality_engine import get_supplier_quality_status

def run_procurement_optimization():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Get current inventory
    inv = get_current_inventory_status()
    if not inv:
        conn.close()
        return None
        
    daily_crush = inv["daily_crush_mt"]
    available_stock = inv["available_usable_mt"]
    safety_stock = inv["safety_stock_mt"]
    coverage_days = inv["coverage_days"]
    net_req_30d = inv["net_requirement_30d_mt"]
    
    # 2. Get active quotations
    cursor.execute("""
    SELECT q.id as quote_id, q.supplier_id, s.name as supplier_name, s.origin_type, s.rating_overall,
           q.price_per_mt, q.currency, q.offered_qty_mt, q.min_order_qty_mt, q.lead_time_days, q.payment_terms
    FROM quotations q
    JOIN suppliers s ON q.supplier_id = s.id
    WHERE q.status = 'Active';
    """)
    quotes = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    # 3. Apply Mandatory Quality Gate & Calculate TLC
    qualified_quotes = []
    disqualified_quotes = []
    
    for q in quotes:
        q_status = get_supplier_quality_status(q["supplier_id"])
        
        # Calculate TLC
        if q["currency"] == "INR":
            tlc_res = calculate_domestic_tlc(q["price_per_mt"])
        else:
            tlc_res = calculate_import_tlc(q["price_per_mt"], usd_inr_rate=86.5)
            
        tlc_val = tlc_res["total_landed_cost_mt"]
        
        # Quality check
        if not q_status["is_qualified"]:
            disqualified_quotes.append({
                **q,
                "tlc_mt": tlc_val,
                "disqualification_reason": "Failed Mandatory Quality Specification Gate (Batch moisture/sand violation)."
            })
        else:
            qualified_quotes.append({
                **q,
                "tlc_mt": tlc_val,
                "quality_pass_rate": q_status["pass_rate_pct"]
            })
            
    # Sort qualified by TLC ascending
    qualified_quotes.sort(key=lambda x: x["tlc_mt"])
    
    # 4. Formulate Recommendation Logic
    today = datetime.now().date()
    
    # Decision heuristics
    if coverage_days <= inv["safety_stock_days"]:
        # Emergency safety replenishment: must buy domestic due to rapid lead time
        best_domestic = next((q for q in qualified_quotes if q["origin_type"] == "Domestic"), None)
        rec_qty = max(2000.0, min(net_req_30d, 4000.0))
        target_buy = today.strftime("%Y-%m-%d")
        lead_time = best_domestic["lead_time_days"] if best_domestic else 5
        target_arrival = (today + timedelta(days=lead_time)).strftime("%Y-%m-%d")
        
        rec_action = f"PROCURE {rec_qty:,.0f} MT DOMESTIC SPOT (CRITICAL SAFETY REPLENISHMENT)"
        why_preferred = (
            f"Available stock ({coverage_days} days) is below mandatory safety cushion ({inv['safety_stock_days']} days). "
            f"Domestic supplier '{best_domestic['supplier_name']}' delivers in {lead_time} days at Landed Cost ₹{best_domestic['tlc_mt']:,.2f}/MT, "
            f"preventing plant stockout while import sea transit (42 days) would arrive too late. Cheaper non-compliant quotes were rejected at the quality gate."
        )
        sourcing_channel = f"Domestic Mandi ({best_domestic['supplier_name']})"
        est_tlc = best_domestic["tlc_mt"] if best_domestic else 48002.8
        supplier_id = best_domestic["supplier_id"] if best_domestic else 1
        
    else:
        # Check parity spread
        best_domestic = next((q for q in qualified_quotes if q["origin_type"] == "Domestic"), None)
        best_import = next((q for q in qualified_quotes if q["origin_type"] == "International"), None)
        
        if best_domestic and best_import:
            spread = best_domestic["tlc_mt"] - best_import["tlc_mt"]
            if spread > 800.0 and coverage_days >= 35:
                # Import window active!
                rec_qty = 4500.0 # Full vessel parcel
                target_buy = today.strftime("%Y-%m-%d")
                lead_time = best_import["lead_time_days"]
                target_arrival = (today + timedelta(days=lead_time)).strftime("%Y-%m-%d")
                rec_action = f"CONTRACT 4,500 MT IMPORT VESSEL (ARBITRAGE WINDOW ACTIVE)"
                why_preferred = (
                    f"Import TLC (₹{best_import['tlc_mt']:,.2f}/MT) is ₹{spread:,.2f}/MT cheaper than domestic. "
                    f"Current inventory ({coverage_days} days) comfortably absorbs 42-day sea voyage without stockout risk."
                )
                sourcing_channel = f"International CIF ({best_import['supplier_name']})"
                est_tlc = best_import["tlc_mt"]
                supplier_id = best_import["supplier_id"]
            else:
                rec_qty = 2500.0
                target_buy = today.strftime("%Y-%m-%d")
                lead_time = best_domestic["lead_time_days"]
                target_arrival = (today + timedelta(days=lead_time)).strftime("%Y-%m-%d")
                rec_action = f"PROCURE 2,500 MT DOMESTIC (TACTICAL REPLENISHMENT)"
                why_preferred = f"Domestic sourcing is economically preferable (₹{best_domestic['tlc_mt']:,.2f}/MT) with rapid {lead_time}-day turnaround."
                sourcing_channel = f"Domestic Mandi ({best_domestic['supplier_name']})"
                est_tlc = best_domestic["tlc_mt"]
                supplier_id = best_domestic["supplier_id"]
        else:
            rec_qty = 2000.0
            target_buy = today.strftime("%Y-%m-%d")
            target_arrival = (today + timedelta(days=5)).strftime("%Y-%m-%d")
            rec_action = "PROCURE 2,000 MT DOMESTIC SPOT"
            why_preferred = "Procuring baseline domestic requirement."
            sourcing_channel = "Domestic Spot"
            est_tlc = 48002.8
            supplier_id = 1
            
    projected_cover_after_arrival = round((available_stock + rec_qty) / daily_crush, 1)
    
    alternatives = [
        {
            "plan_name": "Plan A: Immediate Recommended Tranche",
            "quantity_mt": rec_qty,
            "channel": sourcing_channel,
            "est_tlc_mt": est_tlc,
            "trade_off": "Optimizes supply continuity and minimizes landed procurement spend."
        },
        {
            "plan_name": "Plan B: Staged Sourcing (50% Now + 50% in 14 Days)",
            "quantity_mt": rec_qty,
            "channel": "Split Tranche",
            "est_tlc_mt": round(est_tlc * 1.012, 2),
            "trade_off": "Smooths out market timing risk, but increases order handling overhead."
        },
        {
            "plan_name": "Plan C: Hand-to-Mouth Deferral (Daily Crush Buffer Only)",
            "quantity_mt": round(daily_crush * 7, 0),
            "channel": "Local Spot Only",
            "est_tlc_mt": round(est_tlc * 1.008, 2),
            "trade_off": "Minimizes working capital lockup, but vulnerable to unexpected mandi supply shutdowns."
        }
    ]
    
    return {
        "recommended_action": rec_action,
        "recommended_qty_mt": rec_qty,
        "target_buy_date": target_buy,
        "target_arrival_date": target_arrival,
        "sourcing_channel": sourcing_channel,
        "supplier_id": supplier_id,
        "estimated_tlc_mt": est_tlc,
        "cost_per_usable_mt": est_tlc,
        "current_stock_cover_days": coverage_days,
        "projected_stock_cover_days": projected_cover_after_arrival,
        "why_preferred": why_preferred,
        "alternatives": alternatives,
        "qualified_suppliers_count": len(qualified_quotes),
        "disqualified_suppliers_count": len(disqualified_quotes),
        "disqualified_suppliers": disqualified_quotes
    }

if __name__ == "__main__":
    opt = run_procurement_optimization()
    print("Action:", opt["recommended_action"])
    print("Why:", opt["why_preferred"])
    print("Disqualified:", len(opt["disqualified_suppliers"]))
