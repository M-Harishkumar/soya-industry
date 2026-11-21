from database import get_db

def evaluate_batch_quality(
    moisture_pct: float,
    protein_pct: float,
    oil_pct: float,
    foreign_matter_pct: float,
    damaged_pct: float
) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT parameter_name, min_limit, max_limit, is_mandatory FROM quality_specs;")
    specs = {row["parameter_name"]: row for row in cursor.fetchall()}
    conn.close()
    
    results = []
    is_overall_passed = True
    failed_reasons = []
    
    checks = [
        ("Moisture Content", moisture_pct, specs.get("Moisture Content")),
        ("Crude Protein (Dry Basis)", protein_pct, specs.get("Crude Protein (Dry Basis)")),
        ("Crude Oil Content", oil_pct, specs.get("Crude Oil Content")),
        ("Foreign Matter & Sand", foreign_matter_pct, specs.get("Foreign Matter & Sand")),
        ("Damaged & Weeviled Grains", damaged_pct, specs.get("Damaged & Weeviled Grains"))
    ]
    
    for param_name, measured_val, spec in checks:
        if not spec:
            continue
        min_l = spec["min_limit"]
        max_l = spec["max_limit"]
        is_mand = bool(spec["is_mandatory"])
        
        passed = True
        reason = ""
        if min_l is not None and measured_val < min_l:
            passed = False
            reason = f"Below minimum limit {min_l}%"
        if max_l is not None and measured_val > max_l:
            passed = False
            reason = f"Exceeds maximum limit {max_l}%"
            
        if not passed:
            is_overall_passed = False
            failed_reasons.append(f"{param_name} ({measured_val}% vs allowed {min_l or '0'}-{max_l or '100'}%)")
            
        results.append({
            "parameter": param_name,
            "measured_value": measured_val,
            "min_limit": min_l,
            "max_limit": max_l,
            "is_mandatory": is_mand,
            "status": "Pass" if passed else "Fail",
            "reason": reason
        })
        
    return {
        "status": "Passed" if is_overall_passed else "Rejected",
        "is_qualified_for_procurement": is_overall_passed,
        "failed_reasons": failed_reasons,
        "parameter_results": results
    }

def get_supplier_quality_status(supplier_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT batch_id, sample_date, inspection_type, moisture_pct, protein_pct, oil_pct, foreign_matter_pct, damaged_pct, status, inspected_qty_mt, accepted_qty_mt, rejected_qty_mt
    FROM quality_reports
    WHERE supplier_id = ?
    ORDER BY sample_date DESC;
    """, (supplier_id,))
    batches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not batches:
        return {
            "has_records": False,
            "is_qualified": False,
            "reason": "No approved lab inspection reports available for this supplier.",
            "pass_rate_pct": 0.0,
            "batches": []
        }
        
    total_inspected = sum(b["inspected_qty_mt"] for b in batches)
    total_accepted = sum(b["accepted_qty_mt"] for b in batches)
    pass_rate = (total_accepted / total_inspected * 100.0) if total_inspected > 0 else 0.0
    
    # Check latest batch
    latest_batch = batches[0]
    is_latest_passed = (latest_batch["status"] == "Passed")
    
    return {
        "has_records": True,
        "is_qualified": is_latest_passed and pass_rate >= 80.0,
        "pass_rate_pct": round(pass_rate, 1),
        "total_inspected_mt": total_inspected,
        "total_accepted_mt": total_accepted,
        "latest_batch": latest_batch,
        "batches": batches
    }

if __name__ == "__main__":
    test_eval = evaluate_batch_quality(9.5, 38.5, 19.0, 1.5, 2.0)
    print("Good Batch Status:", test_eval["status"])
    bad_eval = evaluate_batch_quality(13.4, 35.6, 17.2, 4.5, 5.8)
    print("Bad Batch Status:", bad_eval["status"], bad_eval["failed_reasons"])
