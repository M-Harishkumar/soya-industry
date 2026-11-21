// SoyaSetu API Client — Enterprise Dual-Mode (Live FastAPI + GitHub Pages Demo Fallback)
const API = {
  baseUrl: window.location.origin,

  async get(endpoint) {
    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      return await res.json();
    } catch (e) {
      console.warn(`[API] Live backend unreachable for GET ${endpoint}. Engaging client-side static engine...`);
      return this.getMockResponse(endpoint);
    }
  },

  async post(endpoint, data = {}) {
    try {
      const res = await fetch(`${this.baseUrl}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Request failed");
      }
      return await res.json();
    } catch (e) {
      console.warn(`[API] Live backend unreachable for POST ${endpoint}. Processing locally...`);
      return this.postMockResponse(endpoint, data);
    }
  },

  showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    if (!container) return;
    
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? "✓" : (type === "error" ? "✕" : "ℹ");
    toast.innerHTML = `<span style="font-weight:700; margin-right:4px;">${icon}</span><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  },

  // Client-side baseline database for standalone GitHub Pages deployments
  getMockResponse(endpoint) {
    const ep = endpoint.split("?")[0];

    if (ep === "/api/auth/roles") {
      return {
        current_user: { username: "ananya", full_name: "Ananya Sharma", role: "Procurement Head", email: "ananya.s@abt-cpd.com" },
        available_users: [
          { username: "ananya", full_name: "Ananya Sharma", role: "Procurement Head" },
          { username: "admin", full_name: "Rajesh Sharma", role: "Super Admin" },
          { username: "quality", full_name: "Dr. Vikram Patel", role: "Quality Manager" },
          { username: "exec", full_name: "Suresh Nambiar", role: "Executive Viewer" },
          { username: "proc_officer", full_name: "Ananya Deshmukh", role: "Procurement Officer" },
          { username: "inv_mgr", full_name: "Mahesh Patel", role: "Inventory Manager" },
          { username: "fin_mgr", full_name: "Siddharth Jain", role: "Finance Manager" }
        ]
      };
    }

    if (ep === "/api/dashboard/summary") {
      return {
        kpis: {
          available_usable_stock_mt: 3600,
          coverage_days: 12.0,
          domestic_tlc_inr: 48003,
          import_tlc_inr: 46001,
          parity_spread_inr: 2002,
          critical_alerts_count: 1
        },
        action_banner: {
          type: "critical",
          title: "SAFETY STOCK DEFICIT: IMMEDIATE DOMESTIC SPOT PURCHASE REQUIRED",
          description: "Available usable stock is 3,600 MT (12.0 days), which is below the mandatory 15.0-day safety buffer (4,500 MT). Domestic spot allocation from Madhya Bharat Agro Co-op recommended for 5-day arrival."
        },
        active_recommendation: {
          id: 1,
          status: "Submitted for Review",
          recommended_action: "PROCURE 2,500 MT DOMESTIC SPOT (CRITICAL SAFETY REPLENISHMENT)",
          why_preferred: "Triggered by silo coverage falling to 12.0 days. Domestic transit is 5 days vs. 42 days for sea imports, preventing severe stockout risk.",
          recommended_qty_mt: 2500,
          estimated_tlc_mt: 48003,
          target_arrival_date: "2026-11-26"
        }
      };
    }

    if (ep === "/api/market/history") {
      const dates = [];
      const spot = [];
      const cbot = [];
      const baseSpot = 47200;
      const baseCbot = 425;
      for (let i = 30; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        dates.push(d.toISOString().split("T")[0]);
        spot.push(Math.round(baseSpot + Math.sin(i / 3) * 600 + (30 - i) * 15));
        cbot.push(Math.round(baseCbot + Math.cos(i / 4) * 12 + (30 - i) * 0.4));
      }
      return { dates, domestic_spot: spot, cbot_usd: cbot };
    }

    if (ep === "/api/market/seasonality") {
      return {
        months: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        seasonality_pct: [-2.1, -1.4, 0.8, 1.9, 3.4, 4.2, 5.1, 3.8, 1.2, -4.5, -5.8, -3.2]
      };
    }

    if (ep === "/api/market/forecast") {
      const dates = [];
      const exp = [];
      const up = [];
      const low = [];
      let p = 47650;
      for (let i = 1; i <= 45; i++) {
        const d = new Date();
        d.setDate(d.getDate() + i);
        dates.push(d.toISOString().split("T")[0]);
        p += (Math.random() - 0.48) * 45;
        exp.push(Math.round(p));
        up.push(Math.round(p + i * 14 + 180));
        low.push(Math.round(p - i * 14 - 180));
      }
      return {
        forecast_dates: dates,
        expected_prices: exp,
        upper_bounds: up,
        lower_bounds: low,
        backtest_metrics: { "30d_mape_pct": 2.41, "30d_rmse_inr": 94.2, "directional_accuracy_pct": 84.6 }
      };
    }

    if (ep === "/api/suppliers") {
      return {
        suppliers: [
          { id: 1, name: "Madhya Bharat Agro Co-op", location: "Indore Mandi", country: "India", origin_type: "Domestic", rating_overall: 4.8, price_per_mt: 46500, currency: "INR", lead_time_days: 5, is_quality_qualified: true },
          { id: 2, name: "Cargill Agricola S.A.", location: "Paranaguá Port", country: "Brazil", origin_type: "International", rating_overall: 4.6, price_per_mt: 415, currency: "USD", lead_time_days: 42, is_quality_qualified: true },
          { id: 3, name: "ADM Do Brasil", location: "Santos Terminal", country: "Brazil", origin_type: "International", rating_overall: 4.5, price_per_mt: 420, currency: "USD", lead_time_days: 40, is_quality_qualified: true },
          { id: 4, name: "Bunge India Pvt Ltd", location: "Latur Mandi", country: "India", origin_type: "Domestic", rating_overall: 4.3, price_per_mt: 47100, currency: "INR", lead_time_days: 4, is_quality_qualified: true },
          { id: 5, name: "Mahavir Grain Traders", location: "Kota Mandi", country: "India", origin_type: "Domestic", rating_overall: 3.1, price_per_mt: 43500, currency: "INR", lead_time_days: 3, is_quality_qualified: false }
        ]
      };
    }

    if (ep.startsWith("/api/suppliers/")) {
      const id = parseInt(ep.split("/").pop());
      return {
        id,
        name: id === 1 ? "Madhya Bharat Agro Co-op" : (id === 5 ? "Mahavir Grain Traders" : "Cargill Agricola S.A."),
        origin_type: id === 2 || id === 3 ? "International" : "Domestic",
        location: id === 1 ? "Indore Mandi" : "Paranaguá Port",
        country: id === 2 || id === 3 ? "Brazil" : "India",
        rating_overall: id === 5 ? 3.1 : 4.8,
        quality_score: id === 5 ? 2.4 : 4.9,
        reliability_score: id === 5 ? 3.0 : 4.7,
        commercial_score: 4.6,
        payment_terms: "Net 30 Days LC",
        capacity_monthly_mt: 12000,
        lead_time_days: id === 2 ? 42 : 5,
        is_quality_qualified: id !== 5,
        quality_pass_rate_pct: id === 5 ? 62.5 : 97.4,
        total_inspected_mt: 8500,
        total_accepted_mt: id === 5 ? 5300 : 8280,
        quotations: [
          { quote_date: "2026-11-20", price_per_mt: id === 2 ? 415 : 46500, currency: id === 2 ? "USD" : "INR", available_quantity_mt: 3000, delivery_point: "Plant Gate Delivered", status: "Active" }
        ],
        quality_reports: [
          { batch_id: "MB-2026-B88", sample_date: "2026-11-19", moisture_pct: 9.4, protein_pct: 38.6, oil_pct: 19.2, foreign_matter_pct: 1.4, status: "Passed" }
        ]
      };
    }

    if (ep === "/api/quality/specs") {
      return {
        specs: [
          { parameter_name: "Moisture Content", unit: "%", min_limit: null, max_limit: 10.0, description: "Max permissible moisture to prevent aflatoxin and microbial deterioration." },
          { parameter_name: "Crude Protein (Dry Basis)", unit: "%", min_limit: 38.0, max_limit: null, description: "Essential protein density for high-yield de-oiled cake (DOC) production." },
          { parameter_name: "Crude Oil Content", unit: "%", min_limit: 18.5, max_limit: null, description: "Minimum extractable oil threshold for extraction profitability." },
          { parameter_name: "Foreign Matter & Sand", unit: "%", min_limit: null, max_limit: 2.0, description: "Inorganic stones, dust, and non-soy vegetative chaff." },
          { parameter_name: "Damaged & Weeviled Grains", unit: "%", min_limit: null, max_limit: 3.0, description: "Heat damaged, insect damaged, and immature green seeds." }
        ]
      };
    }

    if (ep === "/api/quality/reports") {
      return {
        reports: [
          { batch_id: "IND-2026-1104", supplier_name: "Madhya Bharat Agro Co-op", sample_date: "2026-11-20", moisture_pct: 9.4, protein_pct: 38.8, oil_pct: 19.2, foreign_matter_pct: 1.2, status: "Passed", notes: "Premium Malwa black soil seed with high protein extraction efficiency." },
          { batch_id: "LAT-2026-0941", supplier_name: "Bunge India Pvt Ltd", sample_date: "2026-11-18", moisture_pct: 9.8, protein_pct: 38.1, oil_pct: 18.9, foreign_matter_pct: 1.6, status: "Passed", notes: "Latur lot accepted under contract grade specifications." },
          { batch_id: "KOT-2026-0812", supplier_name: "Mahavir Grain Traders", sample_date: "2026-11-17", moisture_pct: 13.4, protein_pct: 35.6, oil_pct: 17.2, foreign_matter_pct: 4.5, status: "Rejected", notes: "HARD REJECTION: High moisture (13.4% > 10.0%) and heavy sand contamination." }
        ]
      };
    }

    if (ep === "/api/inventory/status") {
      return {
        physical_stock_mt: 4800,
        accepted_usable_mt: 3600,
        reserved_mt: 600,
        available_usable_mt: 3600,
        daily_crush_mt: 300,
        coverage_days: 12.0,
        safety_stock_days: 15,
        safety_stock_mt: 4500,
        rop_domestic_mt: 6000,
        net_requirement_30d_mt: 5400,
        incoming_shipments: [
          { po_number: "PO-DOM-8841", supplier_name: "Madhya Bharat Agro Co-op", order_qty_mt: 1200, source_type: "Domestic", expected_arrival_date: "2026-11-24", status: "In Transit", landed_cost_mt: 48003 },
          { po_number: "PO-IMP-2201", supplier_name: "Cargill Agricola S.A.", order_qty_mt: 3000, source_type: "International", expected_arrival_date: "2026-12-15", status: "On Vessel", landed_cost_mt: 45863 }
        ]
      };
    }

    if (ep === "/api/inventory/projection") {
      const timeline = [];
      let stock = 3600;
      for (let i = 0; i <= 30; i++) {
        const d = new Date();
        d.setDate(d.getDate() + i);
        if (i === 4) stock += 1200;
        if (i === 24) stock += 3000;
        stock -= 300;
        timeline.push({
          date: d.toISOString().split("T")[0],
          day_offset: i,
          projected_stock_mt: Math.max(0, stock),
          coverage_days: Number((Math.max(0, stock) / 300).toFixed(1)),
          safety_stock_mt: 4500,
          is_below_safety: stock < 4500
        });
      }
      return { timeline };
    }

    if (ep === "/api/landed-cost/parity") {
      return {
        domestic_tlc: {
          base_spot_mt: 46500,
          apmc_cess_pct: 1.5,
          apmc_cess_amount: 697.5,
          inland_freight_mt: 650,
          handling_per_mt: 110,
          insurance_amount: 45.3,
          total_landed_cost_mt: 48002.8
        },
        import_tlc: {
          cif_usd_mt: 415,
          usd_inr_rate: 86.5,
          cif_inr_mt: 35897.5,
          aidc_pct: 5.0,
          aidc_amount: 1794.9,
          port_cha_mt: 1150,
          port_to_plant_freight_mt: 1850,
          transit_finance_cost_mt: 538.5,
          total_landed_cost_mt: 46000.8
        },
        spread_analysis: {
          parity_spread_mt: 2002.0,
          is_arbitrage_open: true,
          domestic_preferred: false,
          rationale: "Import TLC is ₹2,002/MT cheaper than Domestic TLC on pure economics. However, Brazil lead time is 42 days, making rapid domestic spot procurement essential to protect the 15-day plant safety buffer."
        }
      };
    }

    if (ep === "/api/landed-cost/sensitivity") {
      const fx_headers = [84.0, 85.0, 86.5, 87.5, 89.0];
      const matrix = [390, 405, 415, 425, 440].map(cbot => ({
        cbot_usd: cbot,
        values: fx_headers.map(fx => {
          const imp = (cbot * fx) * 1.05 + 1150 + 1850 + (cbot * fx * 0.015);
          const spread = 48003 - imp;
          return { fx, import_tlc: Math.round(imp), spread: Math.round(spread), is_import_favorable: spread > 0 };
        })
      }));
      return { fx_headers, matrix };
    }

    if (ep === "/api/optimization/run") {
      return {
        recommended_action: "EXECUTE DOMESTIC REPLENISHMENT (2,500 MT)",
        sourcing_channel: "Domestic Spot (Madhya Bharat Agro)",
        recommended_qty_mt: 2500,
        estimated_tlc_mt: 48003,
        target_arrival_date: "2026-11-26",
        why_preferred: "Stockout mitigation: Plant silo cover is at 12.0 days (3,600 MT) against mandatory 15.0-day buffer (4,500 MT). Domestic spot arrives in 5 days vs 42-day ocean import voyage.",
        alternatives: [
          { plan_name: "Plan A: Split Sourcing (1,500 MT Dom + 3,000 MT Import)", quantity_mt: 4500, channel: "Hybrid Domestic / Import", est_tlc_mt: 46580, trade_off: "Captures ₹2,002/MT import arbitrage while ordering just enough domestic stock to survive until vessel arrival." },
          { plan_name: "Plan B: Maximum Domestic Buffer (4,000 MT)", quantity_mt: 4000, channel: "Domestic (Indore + Latur)", est_tlc_mt: 47910, trade_off: "Completely eliminates shipping and port delay risks, but foregoes international import cost arbitrage." }
        ]
      };
    }

    if (ep === "/api/agents/control-center") {
      return {
        agents: [
          { agent_name: "Market Intelligence Agent", agent_role: "Mandi & CBOT Trend Forecaster", confidence_score_pct: 94, findings: { "spot_trend": "Firm (+₹15/day)", "cbot_direction": "Stable ($415/MT)", "seasonality_dip": "Harvest arrivals peaking" }, risk_flags: ["Domestic mandi arrivals will dry up by mid-December"], recommendation_input: "Domestic purchase before post-harvest price recovery." },
          { agent_name: "Quality Gatekeeper Agent", agent_role: "Laboratory Compliance Auditor", confidence_score_pct: 98, findings: { "qualified_vendors": "4 of 5 suppliers", "last_inspected_pass_rate": "97.4%", "disqualified_entity": "Mahavir Grain Traders" }, risk_flags: ["Mahavir lot showed 13.4% moisture (hard reject)"], recommendation_input: "Route orders exclusively through Madhya Bharat Agro or Cargill." },
          { agent_name: "Inventory & Silo Agent", agent_role: "Crush Demand & Silo Custodian", confidence_score_pct: 96, findings: { "usable_silo_stock": "3,600 MT", "coverage_horizon": "12.0 Days", "safety_buffer": "15 Days (4,500 MT)" }, risk_flags: ["CRITICAL: Coverage breach (12.0d < 15.0d threshold)"], recommendation_input: "URGENT domestic spot order of 2,500 MT within 48 hours." },
          { agent_name: "Logistics & Freight Agent", agent_role: "Transit & Port Demurrage Analyst", confidence_score_pct: 91, findings: { "indore_transit_time": "5 Days", "nhava_sheva_lead_time": "42 Days", "ocean_freight": "$42 / MT" }, risk_flags: ["Nhava Sheva container congestion adds 4-day uncertainty"], recommendation_input: "Domestic trucking preferred due to lead time urgency." },
          { agent_name: "Macro & FX Risk Agent", agent_role: "Currency & Tariff Strategist", confidence_score_pct: 93, findings: { "usd_inr_rate": "₹86.50", "fx_volatility": "Low (RBI intervention)", "aidc_tariff": "5.0% unchanged" }, risk_flags: ["Potential rupee depreciation towards 87.20 in Q1"], recommendation_input: "Hedge import forward contracts if booking South American parcels." },
          { agent_name: "Executive Orchestrator", agent_role: "Multi-Agent Consensus Synthesizer", confidence_score_pct: 97, findings: { "consensus_vote": "Domestic Replenishment", "economic_arbitrage": "₹2,002/MT (Import favorable)", "operational_constraint": "12-day inventory breach" }, risk_flags: ["Lead time constraint overrides import cost advantage"], recommendation_input: "Procure 2,500 MT domestic spot immediately." }
        ],
        final_recommendation: {
          directive: "EXECUTE DOMESTIC REPLENISHMENT (2,500 MT @ ₹48,003/MT)",
          why_optimal: "Synthesis of 6 autonomous agents confirms that inventory survival outweighs cost arbitrage: 12-day stock cover cannot wait for 42-day South American shipments.",
          trade_off_resolution: [
            "Resolution 1: Accepted ₹2,002/MT higher domestic cost to prevent catastrophic plant shutdown costing ₹450,000/day in idle overheads.",
            "Resolution 2: Enforced laboratory compliance gate, disqualifying low-priced Mahavir quotes (₹43,500/MT) due to moisture failure."
          ]
        }
      };
    }

    if (ep === "/api/alerts") {
      return {
        alerts: [
          { id: 101, severity: "Critical", category: "Inventory", title: "Silo Buffer Deficit (12.0 Days)", message: "Plant 01 usable stock (3,600 MT) is below 15-day safety threshold. Imminent stockout risk in 7 days without domestic replenishment.", timestamp: "2026-11-21 08:30", source: "Inventory Agent", affected_entity: "Plant Silo 01", status: "Active" },
          { id: 102, severity: "Warning", category: "Market", title: "USD/INR Exchange Rate Tightening", message: "Spot USD/INR touched ₹86.50. Import parity advantage compressed by ₹180/MT over the last 72 hours.", timestamp: "2026-11-20 16:45", source: "Macro Risk Agent", affected_entity: "Import Parity", status: "Active" },
          { id: 103, severity: "Info", category: "Quality", title: "Batch IND-2026-1104 Accepted", message: "Madhya Bharat Agro Co-op 1,200 MT consignment cleared specification testing (38.8% protein, 9.4% moisture).", timestamp: "2026-11-20 11:20", source: "Lab QA Gate", affected_entity: "Batch IND-2026-1104", status: "Resolved" }
        ]
      };
    }

    if (ep === "/api/recommendations") {
      return {
        recommendations: [
          {
            id: 1,
            recommended_action: "PROCURE 2,500 MT DOMESTIC SPOT (CRITICAL SAFETY REPLENISHMENT)",
            sourcing_channel: "Domestic Spot (Madhya Bharat Agro Co-op)",
            recommended_qty_mt: 2500,
            estimated_tlc_mt: 48003,
            target_arrival_date: "2026-11-26",
            projected_stock_cover_days: 20.3,
            why_preferred: "Triggered by silo coverage falling to 12.0 days (3,600 MT). Domestic transit time is 5 days vs 42 days for sea imports, eliminating stockout risk.",
            status: "Submitted for Review",
            created_at: "2026-11-21 08:30:00",
            approver_name: null,
            approver_role: null,
            approved_at: null,
            approval_notes: null
          }
        ]
      };
    }

    if (ep === "/api/audit/logs") {
      return {
        logs: [
          { timestamp: "2026-11-21 15:45:12", user_name: "Ananya Sharma", user_role: "Procurement Head", action: "RECOMMENDATION_VIEW", entity_type: "Docket", entity_id: "1", details_json: "Reviewed 2,500 MT safety replenishment docket." },
          { timestamp: "2026-11-21 14:10:05", user_name: "Dr. Vikram Patel", user_role: "Quality Manager", action: "QUALITY_EVALUATION", entity_type: "Batch", entity_id: "KOT-0812", details_json: "Hard rejection: Moisture 13.4%, Foreign Matter 4.5%." },
          { timestamp: "2026-11-21 11:20:18", user_name: "Mahesh Patel", user_role: "Inventory Manager", action: "INVENTORY_CALIBRATION", entity_type: "Silo", entity_id: "Plant 01", details_json: "Calibrated physical stock: 4,800 MT (3,600 MT usable)." }
        ]
      };
    }

    return {};
  },

  postMockResponse(endpoint, data) {
    if (endpoint === "/api/auth/switch-role") {
      const u = (this.getMockResponse("/api/auth/roles").available_users.find(x => x.username === data.username)) || {
        username: data.username, full_name: "User", role: "Procurement Head"
      };
      return { status: "success", current_user: u };
    }

    if (endpoint === "/api/market/update-price") {
      return { status: "success", origin: data.origin, price_per_mt: data.price_per_mt };
    }

    if (endpoint === "/api/quality/evaluate-batch") {
      const reasons = [];
      if (data.moisture_pct > 10.0) reasons.push(`Moisture (${data.moisture_pct}% > 10.0%)`);
      if (data.protein_pct < 38.0) reasons.push(`Protein (${data.protein_pct}% < 38.0%)`);
      if (data.oil_pct < 18.5) reasons.push(`Oil (${data.oil_pct}% < 18.5%)`);
      if (data.foreign_matter_pct > 2.0) reasons.push(`Foreign Matter (${data.foreign_matter_pct}% > 2.0%)`);
      
      const status = reasons.length === 0 ? "Passed" : "Rejected";
      return { status, reasons };
    }

    if (endpoint === "/api/inventory/update") {
      return { status: "success", updated_stock_mt: data.accepted_usable_mt };
    }

    if (endpoint === "/api/scenarios/simulate") {
      const shock = data.domestic_price_shock_pct || 0;
      const duty = data.import_duty_pct || 0;
      const fx = data.usd_inr_rate || 86.5;
      const freight = data.ocean_freight_usd_mt || 42;
      const reject = data.quality_rejection_pct || 0;

      const baseDom = 46500 * (1 + shock / 100);
      const domTlc = baseDom * 1.015 + 650 + 110 + 45;
      const usableDom = domTlc / (1 - (reject / 100));

      const cifInr = (415 + (freight - 42)) * fx;
      const impTlc = cifInr * (1 + (duty + 5) / 100) + 1150 + 1850 + (cifInr * 0.015);
      const spread = usableDom - impTlc;

      const strat = spread > 1500 ? "STRATEGY: IMPORT ARBITRAGE EXPLOITATION" : (spread < -500 ? "STRATEGY: DOMESTIC MANDI SOURCING PREFERRED" : "STRATEGY: BALANCED HYBRID SOURCING");
      const summary = `Under simulated conditions (Domestic shock: ${shock > 0 ? '+' : ''}${shock}%, Duty: ${duty}%, FX: ₹${fx}, Reject: ${reject}%), Usable Domestic TLC is ₹${Math.round(usableDom).toLocaleString()}/MT vs Import TLC ₹${Math.round(impTlc).toLocaleString()}/MT (Spread: ₹${Math.round(spread).toLocaleString()}/MT).`;

      return {
        domestic_tlc_mt: domTlc,
        domestic_usable_cost_mt: usableDom,
        import_tlc_mt: impTlc,
        parity_spread_mt: spread,
        strategy: strat,
        impact_summary: summary
      };
    }

    if (endpoint.startsWith("/api/recommendations/") && endpoint.endsWith("/action")) {
      return { status: "success", action: data.action, notes: data.notes };
    }

    if (endpoint.startsWith("/api/alerts/") && endpoint.endsWith("/acknowledge")) {
      return { status: "success", acknowledged: true };
    }

    if (endpoint.startsWith("/api/alerts/") && endpoint.endsWith("/resolve")) {
      return { status: "success", resolved: true };
    }

    return { status: "success" };
  }
};
