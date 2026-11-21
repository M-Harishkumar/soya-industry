from engines.landed_cost_engine import calculate_domestic_tlc, calculate_import_tlc, calculate_parity_spread, calculate_cost_per_usable_tonne
from engines.inventory_engine import get_current_inventory_status

def simulate_procurement_scenario(
    domestic_price_shock_pct: float = 0.0,
    import_duty_pct: float = 0.0,
    usd_inr_rate: float = 86.50,
    ocean_freight_usd_mt: float = 42.0,
    supplier_delay_days: int = 0,
    quality_rejection_pct: float = 0.0
) -> dict:
    # Baseline quotes in INR/MT and USD/MT
    base_spot = 46200.0
    base_cbot = 485.0
    
    # Apply shocks
    shocked_spot = base_spot * (1.0 + domestic_price_shock_pct / 100.0)
    shocked_cif_usd = base_cbot + (ocean_freight_usd_mt - 42.0)
    
    # Recalculate TLCs
    dom_tlc = calculate_domestic_tlc(shocked_spot)
    imp_tlc = calculate_import_tlc(
        cif_usd_mt=shocked_cif_usd,
        usd_inr_rate=usd_inr_rate,
        bcd_pct=import_duty_pct,
        aidc_pct=5.0,
        sea_transit_days=45 + supplier_delay_days
    )
    
    # Quality adjusted cost per usable tonne
    dom_usable_cost = calculate_cost_per_usable_tonne(dom_tlc["total_landed_cost_mt"], quality_rejection_pct)
    imp_usable_cost = calculate_cost_per_usable_tonne(imp_tlc["total_landed_cost_mt"], quality_rejection_pct)
    
    # Parity spread
    spread = calculate_parity_spread(dom_tlc, imp_tlc)
    
    # Assess inventory impact
    inv = get_current_inventory_status()
    current_cover = inv["coverage_days"] if inv else 12.0
    effective_lead_time_imp = 45 + supplier_delay_days
    stockout_vulnerability = (effective_lead_time_imp > current_cover)
    
    # Strategic conclusion
    if spread["is_arbitrage_open"] and not stockout_vulnerability:
        strategy = "IMPORT_PREFERRED"
        impact_summary = (
            f"Under this scenario, international import maintains an advantage of ₹{spread['parity_spread_mt']:,.2f}/MT. "
            f"Sufficient inventory cover permits executing sea shipments."
        )
    elif import_duty_pct > 10.0 or usd_inr_rate > 90.0:
        strategy = "DOMESTIC_LOCKIN"
        impact_summary = (
            f"High tariffs ({import_duty_pct}%) or currency depreciation (₹{usd_inr_rate}/$) have pushed Import TLC to ₹{imp_tlc['total_landed_cost_mt']:,.2f}/MT, "
            f"completely shutting down import viability. All sourcing must remain domestic."
        )
    elif domestic_price_shock_pct > 15.0:
        strategy = "IMPORT_ARBITRAGE_FORCED"
        impact_summary = (
            f"Severe domestic supply squeeze (+{domestic_price_shock_pct}%) has spiked local TLC to ₹{dom_tlc['total_landed_cost_mt']:,.2f}/MT. "
            f"Despite import costs, global sourcing is now essential to control processing inflation."
        )
    else:
        strategy = "BALANCED_DOMESTIC"
        impact_summary = (
            f"Domestic sourcing remains the most cost-effective and low-risk channel (TLC ₹{dom_tlc['total_landed_cost_mt']:,.2f}/MT vs Import ₹{imp_tlc['total_landed_cost_mt']:,.2f}/MT)."
        )
        
    return {
        "inputs": {
            "domestic_price_shock_pct": domestic_price_shock_pct,
            "import_duty_pct": import_duty_pct,
            "usd_inr_rate": usd_inr_rate,
            "ocean_freight_usd_mt": ocean_freight_usd_mt,
            "supplier_delay_days": supplier_delay_days,
            "quality_rejection_pct": quality_rejection_pct
        },
        "domestic_tlc_mt": dom_tlc["total_landed_cost_mt"],
        "import_tlc_mt": imp_tlc["total_landed_cost_mt"],
        "domestic_usable_cost_mt": dom_usable_cost,
        "import_usable_cost_mt": imp_usable_cost,
        "parity_spread_mt": spread["parity_spread_mt"],
        "strategy": strategy,
        "impact_summary": impact_summary,
        "stockout_vulnerability": stockout_vulnerability
    }
