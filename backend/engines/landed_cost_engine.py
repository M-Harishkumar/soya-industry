def calculate_domestic_tlc(
    spot_price_mt: float,
    apmc_cess_pct: float = 1.50,
    handling_per_mt: float = 75.0,
    inland_freight_mt: float = 850.0,
    insurance_pct: float = 0.40,
    moisture_penalty_mt: float = 0.0
) -> dict:
    apmc_cess = spot_price_mt * (apmc_cess_pct / 100.0)
    insurance = spot_price_mt * (insurance_pct / 100.0)
    total_tlc = spot_price_mt + apmc_cess + handling_per_mt + inland_freight_mt + insurance - moisture_penalty_mt
    
    return {
        "channel": "Domestic (Indore / Latur)",
        "base_spot_mt": round(spot_price_mt, 2),
        "apmc_cess_pct": apmc_cess_pct,
        "apmc_cess_amount": round(apmc_cess, 2),
        "handling_per_mt": round(handling_per_mt, 2),
        "inland_freight_mt": round(inland_freight_mt, 2),
        "insurance_pct": insurance_pct,
        "insurance_amount": round(insurance, 2),
        "moisture_penalty_mt": round(moisture_penalty_mt, 2),
        "total_landed_cost_mt": round(total_tlc, 2),
        "lead_time_days": 5
    }

def calculate_import_tlc(
    cif_usd_mt: float,
    usd_inr_rate: float = 86.50,
    bcd_pct: float = 0.0,
    aidc_pct: float = 5.0,
    port_cha_mt: float = 380.0,
    port_to_plant_freight_mt: float = 950.0,
    sea_transit_days: int = 45,
    annual_interest_rate_pct: float = 12.0
) -> dict:
    cif_inr = cif_usd_mt * usd_inr_rate
    duty_amount = cif_inr * (bcd_pct / 100.0)
    aidc_amount = cif_inr * (aidc_pct / 100.0)
    # Transit financing cost on Letter of Credit: CIF * (rate/365) * transit_days
    transit_finance_cost = cif_inr * (annual_interest_rate_pct / 100.0) * (sea_transit_days / 365.0)
    
    total_tlc = cif_inr + duty_amount + aidc_amount + port_cha_mt + port_to_plant_freight_mt + transit_finance_cost
    
    return {
        "channel": "International (CIF Nhava Sheva / Kandla)",
        "cif_usd_mt": round(cif_usd_mt, 2),
        "usd_inr_rate": round(usd_inr_rate, 2),
        "cif_inr_mt": round(cif_inr, 2),
        "bcd_pct": bcd_pct,
        "bcd_amount": round(duty_amount, 2),
        "aidc_pct": aidc_pct,
        "aidc_amount": round(aidc_amount, 2),
        "port_cha_mt": round(port_cha_mt, 2),
        "port_to_plant_freight_mt": round(port_to_plant_freight_mt, 2),
        "sea_transit_days": sea_transit_days,
        "transit_finance_cost_mt": round(transit_finance_cost, 2),
        "total_landed_cost_mt": round(total_tlc, 2),
        "lead_time_days": sea_transit_days
    }

def calculate_cost_per_usable_tonne(total_tlc_mt: float, rejection_rate_pct: float = 0.0) -> float:
    usable_fraction = max(0.5, 1.0 - (rejection_rate_pct / 100.0))
    return round(total_tlc_mt / usable_fraction, 2)

def calculate_parity_spread(dom_tlc: dict, imp_tlc: dict) -> dict:
    spread = dom_tlc["total_landed_cost_mt"] - imp_tlc["total_landed_cost_mt"]
    
    # Import arbitrage requires at least Rs 800/MT advantage to justify 45-day sea transit & currency lockup
    is_arbitrage_open = spread > 800.0
    
    if is_arbitrage_open:
        recommendation = "IMPORT_ARBITRAGE_ACTIVE"
        rationale = f"Import landed cost (₹{imp_tlc['total_landed_cost_mt']:,.2f}/MT) is ₹{spread:,.2f}/MT cheaper than domestic (₹{dom_tlc['total_landed_cost_mt']:,.2f}/MT). Exceeds the ₹800/MT risk hurdle."
    elif spread > 0:
        recommendation = "MARGINAL_IMPORT_ADVANTAGE"
        rationale = f"Import is cheaper by ₹{spread:,.2f}/MT, but below the ₹800/MT buffer needed to compensate for 45-day maritime lead time risk."
    else:
        recommendation = "DOMESTIC_PREFERRED"
        rationale = f"Domestic sourcing is cheaper by ₹{abs(spread):,.2f}/MT with rapid 5-day delivery fulfillment."

    return {
        "parity_spread_mt": round(spread, 2),
        "is_arbitrage_open": is_arbitrage_open,
        "recommendation": recommendation,
        "rationale": rationale,
        "domestic_tlc": dom_tlc["total_landed_cost_mt"],
        "import_tlc": imp_tlc["total_landed_cost_mt"]
    }

def generate_parity_sensitivity_matrix(
    base_domestic_spot: float,
    fx_range: list = None,
    cbot_range: list = None
) -> dict:
    if fx_range is None:
        fx_range = [84.0, 85.5, 87.0, 88.5, 90.0]
    if cbot_range is None:
        cbot_range = [450.0, 475.0, 500.0, 525.0, 550.0]
        
    dom_tlc = calculate_domestic_tlc(base_domestic_spot)["total_landed_cost_mt"]
    matrix = []
    
    for cbot in cbot_range:
        row = {"cbot_usd": cbot, "values": []}
        for fx in fx_range:
            imp_tlc = calculate_import_tlc(cif_usd_mt=cbot, usd_inr_rate=fx)["total_landed_cost_mt"]
            spread = dom_tlc - imp_tlc
            row["values"].append({
                "fx_rate": fx,
                "import_tlc": imp_tlc,
                "spread": round(spread, 2),
                "is_import_favorable": spread > 800.0
            })
        matrix.append(row)
        
    return {
        "domestic_tlc": dom_tlc,
        "fx_headers": fx_range,
        "matrix": matrix
    }
