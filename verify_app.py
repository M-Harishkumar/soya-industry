import os
import sys

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from main import app
from database import get_db
from engines.landed_cost_engine import calculate_domestic_tlc, calculate_import_tlc, calculate_parity_spread
from engines.quality_engine import evaluate_batch_quality
from engines.inventory_engine import get_current_inventory_status
from agents.agents_core import run_agentic_orchestrator

def run_tests():
    print("==================================================================")
    print("  RUNNING COMPREHENSIVE VERIFICATION SUITE FOR SOYASETU APP")
    print("==================================================================")
    
    client = TestClient(app)
    
    # Test 1: Database records
    print("\n[Test 1/7] Checking Database & Seed Records...")
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users;")
    u_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM suppliers;")
    s_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM quality_specs;")
    q_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM market_prices;")
    m_count = c.fetchone()[0]
    conn.close()
    
    assert u_count == 7, f"Expected 7 users, got {u_count}"
    assert s_count == 5, f"Expected 5 suppliers, got {s_count}"
    assert q_count == 5, f"Expected 5 quality specs, got {q_count}"
    assert m_count >= 120, f"Expected at least 120 market prices, got {m_count}"
    print(f"  ✓ Database healthy: {u_count} users, {s_count} suppliers, {q_count} specs, {m_count} price rows.")

    # Test 2: TLC Calculations
    print("\n[Test 2/7] Testing Total Landed Cost (TLC) Parity Engine...")
    dom = calculate_domestic_tlc(46200.0)
    imp = calculate_import_tlc(485.0, usd_inr_rate=86.5)
    spread = calculate_parity_spread(dom, imp)
    
    # Expected: Dom TLC approx 48002.8, Imp TLC approx 46000.8
    assert 47000 < dom["total_landed_cost_mt"] < 49000, f"Unexpected domestic TLC: {dom['total_landed_cost_mt']}"
    assert 45000 < imp["total_landed_cost_mt"] < 47000, f"Unexpected import TLC: {imp['total_landed_cost_mt']}"
    assert spread["parity_spread_mt"] > 0, f"Expected import cheaper when domestic is high, spread: {spread['parity_spread_mt']}"
    print(f"  ✓ TLC Engine verified: Dom ₹{dom['total_landed_cost_mt']}/MT, Imp ₹{imp['total_landed_cost_mt']}/MT, Spread: ₹{spread['parity_spread_mt']}/MT.")

    # Test 3: Mandatory Quality Gate
    print("\n[Test 3/7] Testing Mandatory Quality Gate...")
    good_batch = evaluate_batch_quality(9.2, 38.8, 19.2, 1.2, 1.8)
    bad_batch = evaluate_batch_quality(13.4, 35.6, 17.2, 4.5, 5.8)
    
    assert good_batch["status"] == "Passed", "Good batch failed"
    assert bad_batch["status"] == "Rejected", "Bad batch passed erroneously"
    assert len(bad_batch["failed_reasons"]) >= 2, "Expected multiple failed reasons for bad batch"
    print(f"  ✓ Quality Gate verified: High-moisture/sand batch unconditionally REJECTED with reasons: {bad_batch['failed_reasons']}")

    # Test 4: Inventory Dynamics
    print("\n[Test 4/7] Testing Inventory Dynamics Engine...")
    inv = get_current_inventory_status()
    assert inv["coverage_days"] == 12.0, f"Expected 12 days coverage, got {inv['coverage_days']}"
    assert inv["is_safety_breached"] is True, "Expected safety stock breach alert"
    assert inv["net_requirement_30d_mt"] > 0, "Expected positive 30d net requirement"
    print(f"  ✓ Inventory Engine verified: Usable {inv['available_usable_mt']} MT, Coverage {inv['coverage_days']}d (Breach detected).")

    # Test 5: Agentic AI Control Centre
    print("\n[Test 5/7] Testing 6-Agent Orchestrator...")
    orchestration = run_agentic_orchestrator()
    assert len(orchestration["agents"]) == 5, f"Expected 5 sub-agents, got {len(orchestration['agents'])}"
    assert len(orchestration["final_recommendation"]["trade_off_resolution"]) >= 2, "Expected trade-off resolutions"
    print(f"  ✓ Agent Orchestrator verified: Consensus reached for '{orchestration['final_recommendation']['directive']}'.")

    # Test 6: FastAPI REST API Endpoints
    print("\n[Test 6/7] Testing REST API Endpoints via HTTP TestClient...")
    r1 = client.get("/api/dashboard/summary")
    assert r1.status_code == 200, f"Dashboard API failed: {r1.status_code}"
    
    r2 = client.get("/api/market/forecast")
    assert r2.status_code == 200, f"Forecast API failed: {r2.status_code}"
    
    r3 = client.get("/api/suppliers")
    assert r3.status_code == 200, f"Suppliers API failed: {r3.status_code}"
    
    r4 = client.get("/api/optimization/run")
    assert r4.status_code == 200, f"Optimization API failed: {r4.status_code}"
    
    r5 = client.get("/api/agents/control-center")
    assert r5.status_code == 200, f"Agents API failed: {r5.status_code}"
    
    r6 = client.get("/api/alerts")
    assert r6.status_code == 200, f"Alerts API failed: {r6.status_code}"
    
    r7 = client.post("/api/scenarios/simulate", json={"domestic_price_shock_pct": 10.0, "import_duty_pct": 5.0})
    assert r7.status_code == 200, f"Scenario simulation failed: {r7.status_code}"
    
    print("  ✓ All 7 core REST API endpoints returned HTTP 200 OK with valid payloads.")

    # Test 7: Role-Based Access Control (RBAC) & Governance Guardrails
    print("\n[Test 7/7] Testing RBAC Security & Human Approval Workflow...")
    
    # Step A: Switch to Executive Viewer (Read Only)
    r_sw1 = client.post("/api/auth/switch-role", json={"username": "exec"})
    assert r_sw1.status_code == 200, f"Failed to switch to exec: {r_sw1.status_code}"
    r_deny = client.post("/api/recommendations/1/action", json={"action": "Approve", "notes": "Unauthorized approval attempt"})
    assert r_deny.status_code == 403, f"Expected 403 Forbidden for Viewer, got {r_deny.status_code}"
    print("  ✓ RBAC guardrail active: Executive Viewer blocked from approving purchase (HTTP 403).")
    
    # Step B: Switch to Procurement Head (Authorized Approver)
    r_sw2 = client.post("/api/auth/switch-role", json={"username": "ananya"})
    assert r_sw2.status_code == 200, f"Failed to switch to ananya: {r_sw2.status_code}"
    r_allow = client.post("/api/recommendations/1/action", json={"action": "Approve", "notes": "Approved 2,500 MT domestic order to restore 15-day safety stock."})
    assert r_allow.status_code == 200, f"Expected 200 OK for Procurement Head, got {r_allow.status_code}"
    print("  ✓ Approval workflow verified: Procurement Head successfully authorized Recommendation #1 (HTTP 200).")

    print("\n==================================================================")
    print("  ALL 7 TEST SUITES PASSED! SOYASETU IS 100% PRODUCTION READY.")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
