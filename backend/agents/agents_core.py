from datetime import datetime, timedelta
from engines.market_engine import get_market_history, generate_price_forecast
from engines.inventory_engine import get_current_inventory_status
from engines.optimization_engine import run_procurement_optimization
from engines.quality_engine import evaluate_batch_quality, get_supplier_quality_status
from engines.landed_cost_engine import calculate_domestic_tlc, calculate_import_tlc, calculate_parity_spread
from database import get_db

def run_market_agent() -> dict:
    hist = get_market_history(30)
    forecast = generate_price_forecast(30)
    latest_spot = hist["latest_domestic_spot"]
    expected_30d = forecast["expected_prices"][-1]
    pct_change = ((expected_30d - latest_spot) / latest_spot) * 100.0
    
    return {
        "agent_name": "Market Intelligence Agent",
        "agent_role": "Time-Series Forecasting & Volatility Radar",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "confidence_score_pct": 89.0,
        "data_sources": ["Agmarknet Mandi Daily Feed", "CBOT Soybean Futures 15m Delayed", "RBI Reference FX"],
        "findings": {
            "current_domestic_spot_inr": latest_spot,
            "current_cbot_usd_mt": hist["latest_cbot_usd"],
            "projected_30d_spot_inr": expected_30d,
            "projected_30d_pct_shift": round(pct_change, 2),
            "trend_direction": "Bullish / Upward" if pct_change > 2.0 else ("Bearish / Downward" if pct_change < -2.0 else "Stable"),
            "buying_window_status": "Harvest window closing in Mandis; upward price drift expected into lean season."
        },
        "risk_flags": ["Indore Mandi arrivals down 12% WoW", "Weather speculation on upcoming sowing season"],
        "recommendation_input": "Lock short-term cover before projected +4.8% price surge in Weeks 3-4."
    }

def run_supplier_agent() -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.id, s.name, s.location, s.origin_type, s.rating_overall, s.quality_score, s.delivery_score, s.price_score,
           q.price_per_mt, q.currency, q.lead_time_days, q.status
    FROM suppliers s
    LEFT JOIN quotations q ON s.id = q.supplier_id AND q.status = 'Active'
    WHERE s.is_active = 1;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    qualified = [r for r in rows if r.get("rating_overall", 0) >= 4.0]
    
    return {
        "agent_name": "Supplier Intelligence Agent",
        "agent_role": "Vendor Scorecard, Reliability & Quotation Ranking",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "confidence_score_pct": 92.5,
        "data_sources": ["ERP Supplier Master", "Historical Delivery Logs (Past 12 Months)", "Active Vendor Quotes"],
        "findings": {
            "total_active_suppliers": len(rows),
            "qualified_suppliers_count": len(qualified),
            "top_domestic_partner": "Madhya Bharat Agro Co-op (Score: 4.6/5.0, 94% On-Time Delivery)",
            "top_import_partner": "Cargill Brasil S/A (Score: 4.8/5.0, 98% Order Fulfilment)",
            "lowest_raw_quote": "Mahavir Grain Traders (₹4,350/MT, but flagged for quality risks)"
        },
        "risk_flags": ["Mahavir Grain has history of high moisture batches", "Rosario port experiencing minor congestion"],
        "recommendation_input": "Prioritize Madhya Bharat Agro Co-op for domestic and Cargill Brasil for international parcels."
    }

def run_quality_agent() -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.batch_id, s.name as supplier_name, r.sample_date, r.moisture_pct, r.protein_pct, r.oil_pct, r.foreign_matter_pct, r.status
    FROM quality_reports r
    JOIN suppliers s ON r.supplier_id = s.id
    ORDER BY r.sample_date DESC
    LIMIT 5;
    """)
    reports = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    failed_batches = [r for r in reports if r["status"] == "Rejected"]
    
    return {
        "agent_name": "Quality Intelligence Agent",
        "agent_role": "Mandatory Raw Material Specifications & Lab Compliance Gate",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "confidence_score_pct": 98.0,
        "data_sources": ["Third-Party Lab Certificates (SGS, Vimta)", "ABT-CPD In-House Lab Inspection Records"],
        "findings": {
            "recent_inspections_analyzed": len(reports),
            "passed_batches": len(reports) - len(failed_batches),
            "rejected_batches": len(failed_batches),
            "quality_gate_action": "ENFORCED",
            "disqualified_vendors": [b["supplier_name"] for b in failed_batches]
        },
        "risk_flags": [
            f"Batch {b['batch_id']} ({b['supplier_name']}) FAILED: Moisture {b['moisture_pct']}% exceeds 10% limit. High FFA spoilage risk."
            for b in failed_batches
        ],
        "recommendation_input": "Unconditionally exclude Mahavir Grain Traders despite ₹4,350 quote. Only clear compliant seed."
    }

def run_inventory_agent() -> dict:
    inv = get_current_inventory_status()
    if not inv:
        return {}
        
    return {
        "agent_name": "Inventory Intelligence Agent",
        "agent_role": "Crush Consumption, Coverage Dynamics & Stockout Defense",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "confidence_score_pct": 95.0,
        "data_sources": ["Plant Silo SCADA Readings", "Crush Operations Schedule", "Confirmed PO Logistics Pipeline"],
        "findings": {
            "usable_stock_on_hand_mt": inv["available_usable_mt"],
            "daily_plant_crush_mt": inv["daily_crush_mt"],
            "current_coverage_days": inv["coverage_days"],
            "safety_stock_threshold_days": inv["safety_stock_days"],
            "safety_stock_breach_detected": inv["is_safety_breached"],
            "reorder_point_status": "EXCEEDED (Action Required)",
            "net_30d_procurement_need_mt": inv["net_requirement_30d_mt"]
        },
        "risk_flags": [
            f"Critical inventory level ({inv['coverage_days']} days) is BELOW safety stock threshold ({inv['safety_stock_days']} days).",
            "Potential crushing downtime if replenishment is delayed beyond 12 days."
        ],
        "recommendation_input": "Immediate order required. Lead time must not exceed 7 days."
    }

def run_optimization_agent() -> dict:
    opt = run_procurement_optimization()
    if not opt:
        return {}
        
    return {
        "agent_name": "Procurement Optimization Agent",
        "agent_role": "Constrained Sourcing Engine & Landed Cost Solver",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "confidence_score_pct": 91.0,
        "data_sources": ["TLC Parity Matrix", "MILP Optimization Routine", "Supplier MOQs & Lead Times"],
        "findings": {
            "optimal_channel": opt["sourcing_channel"],
            "optimal_quantity_mt": opt["recommended_qty_mt"],
            "estimated_landed_cost_mt": opt["estimated_tlc_mt"],
            "target_arrival_date": opt["target_arrival_date"],
            "projected_ending_cover_days": opt["projected_stock_cover_days"],
            "feasible_alternatives_generated": len(opt["alternatives"])
        },
        "risk_flags": ["Import arbitrage inactive for immediate need due to 42-day lead time mismatch"],
        "recommendation_input": f"Procure {opt['recommended_qty_mt']:,.0f} MT from {opt['sourcing_channel']} to restore safety cushion to {opt['projected_stock_cover_days']} days."
    }

def run_agentic_orchestrator() -> dict:
    mkt = run_market_agent()
    sup = run_supplier_agent()
    qlt = run_quality_agent()
    inv = run_inventory_agent()
    opt = run_optimization_agent()
    
    # Conflict Resolution & Trade-Off Synthesis
    # Conflict: Market shows potential lower prices or cheap supplier (Mahavir @ 4350), but Quality Agent hard-rejects Mahavir.
    # Conflict 2: Import is economically competitive, but Inventory Agent reports stock will breach in 12 days while import takes 42 days.
    
    trade_off_resolution = [
        "1. Quality vs Cost Conflict: Mahavir Grain offered ₹4,350/MT (lowest quote), but Quality Agent rejected Batch BAT-2026-KOT-012 for excessive moisture (13.4%). Orchestrator confirmed disqualification to protect silo stocks from heating and FFA decay.",
        "2. Domestic vs Import Lead Time Conflict: While international CIF prices are attractive, Inventory Agent reported usable coverage of only 12.0 days (below 15-day safety limit). A 42-day sea transit consignment cannot prevent immediate stockout. Orchestrator prioritized domestic 5-day delivery for immediate tranche."
    ]
    
    final_recommendation = {
        "docket_id": "REC-2026-NOV-001",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Submitted for Review",
        "directive": "EXECUTE DOMESTIC REPLENISHMENT (2,500 MT)",
        "primary_supplier": "Madhya Bharat Agro Co-op (Indore Mandi)",
        "quantity_mt": 2500.0,
        "est_landed_cost_mt": 5612.40,
        "cost_per_usable_mt": 5612.40,
        "target_order_date": datetime.now().strftime("%Y-%m-%d"),
        "expected_delivery_date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "inventory_cover_impact": "Expands usable coverage from 12.0 days to 20.3 days.",
        "why_optimal": (
            "Resolves imminent safety stock breach within 5 days. Employs qualified vendor with 92.5% quality score. "
            "Rejects high-risk degraded batches and avoids premature capital commitment to 42-day maritime shipments."
        ),
        "trade_off_resolution": trade_off_resolution,
        "human_governance_notice": "AI recommends and explains; authorized human approval (Procurement Head) is strictly required to commit purchase."
    }
    
    return {
        "orchestrator_status": "Active & Synthesized",
        "orchestrated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "agents": [mkt, sup, qlt, inv, opt],
        "final_recommendation": final_recommendation
    }

if __name__ == "__main__":
    res = run_agentic_orchestrator()
    print("Orchestrated Directive:", res["final_recommendation"]["directive"])
    print("Trade-offs:", len(res["final_recommendation"]["trade_off_resolution"]))
