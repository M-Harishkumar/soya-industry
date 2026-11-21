// SoyaSetu Application Controller — Enterprise Production Grade
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});

const App = {
  currentView: "dashboard",
  currentUser: null,
  allUsers: [],
  kpis: null,

  async init() {
    this.bindNavigation();
    this.bindModals();
    this.bindScenarioSliders();
    this.updateClock();
    setInterval(() => this.updateClock(), 1000);

    await this.loadAuthRoles();
    await this.loadView(this.currentView);
  },

  updateClock() {
    const el = document.getElementById("system-clock");
    if (el) {
      const now = new Date();
      el.textContent = now.toLocaleDateString("en-IN", {
        weekday: "short", day: "2-digit", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit", second: "2-digit"
      });
    }
  },

  bindNavigation() {
    document.querySelectorAll(".nav-link").forEach(item => {
      item.addEventListener("click", () => {
        const view = item.getAttribute("data-view");
        if (view) {
          this.loadView(view);
          const sb = document.getElementById("app-sidebar");
          if (sb && window.innerWidth <= 900) {
            sb.classList.remove("open");
          }
        }
      });
    });
  },

  toggleSidebar() {
    const sb = document.getElementById("app-sidebar");
    if (sb) {
      sb.classList.toggle("open");
    }
  },

  async loadAuthRoles() {
    try {
      const data = await API.get("/api/auth/roles");
      this.currentUser = data.current_user;
      this.allUsers = data.available_users;

      const select = document.getElementById("role-selector");
      if (select) {
        select.innerHTML = "";
        data.available_users.forEach(u => {
          const opt = document.createElement("option");
          opt.value = u.username;
          opt.textContent = `${u.full_name} (${u.role})`;
          if (u.username === this.currentUser.username) opt.selected = true;
          select.appendChild(opt);
        });

        select.addEventListener("change", async (e) => {
          const res = await API.post("/api/auth/switch-role", { username: e.target.value });
          this.currentUser = res.current_user;
          API.showToast(`Switched active context to ${this.currentUser.role}`, "info");
          this.updateUserBadge();
          this.loadView(this.currentView);
        });
      }
      this.updateUserBadge();
    } catch (e) {
      console.error("Auth init error:", e);
    }
  },

  updateUserBadge() {
    if (!this.currentUser) return;
    const nameEl = document.getElementById("user-display-name");
    const roleEl = document.getElementById("user-display-role");
    const initEl = document.getElementById("user-display-initials");
    
    if (nameEl) nameEl.textContent = this.currentUser.full_name;
    if (roleEl) roleEl.textContent = this.currentUser.role;
    if (initEl) {
      const parts = this.currentUser.full_name.trim().split(" ");
      const initials = parts.length > 1 ? (parts[0][0] + parts[parts.length - 1][0]).toUpperCase() : parts[0].substring(0, 2).toUpperCase();
      initEl.textContent = initials;
    }
  },

  async loadView(viewName) {
    this.currentView = viewName;

    // Update active nav links
    document.querySelectorAll(".nav-link").forEach(n => {
      if (n.getAttribute("data-view") === viewName) {
        n.classList.add("active");
      } else {
        n.classList.remove("active");
      }
    });

    // Update breadcrumb
    const breadcrumbLabel = document.getElementById("active-breadcrumb-label");
    const viewTitles = {
      dashboard: "Executive Dashboard",
      market: "Market Intelligence",
      suppliers: "Supplier Intelligence",
      quality: "Quality Gate & Specs",
      inventory: "Inventory Dynamics",
      parity: "Landed Cost Parity",
      optimization: "Procurement Optimizer",
      agents: "Agent Control Centre",
      scenarios: "Scenario Sandbox",
      alerts: "Operational Alerts",
      approvals: "Purchase Authorization",
      audit: "Audit Logs & Security"
    };
    if (breadcrumbLabel && viewTitles[viewName]) {
      breadcrumbLabel.textContent = viewTitles[viewName];
    }

    // Toggle panels
    document.querySelectorAll(".view-panel").forEach(p => p.classList.add("hidden"));
    const activePanel = document.getElementById(`view-${viewName}`);
    if (activePanel) activePanel.classList.remove("hidden");

    switch (viewName) {
      case "dashboard":
        await this.renderDashboard();
        break;
      case "market":
        await this.renderMarket();
        break;
      case "suppliers":
        await this.renderSuppliers();
        break;
      case "quality":
        await this.renderQuality();
        break;
      case "inventory":
        await this.renderInventory();
        break;
      case "parity":
        await this.renderParity();
        break;
      case "optimization":
        await this.renderOptimization();
        break;
      case "agents":
        await this.renderAgents();
        break;
      case "alerts":
        await this.renderAlerts();
        break;
      case "scenarios":
        await this.renderScenarios();
        break;
      case "approvals":
        await this.renderApprovals();
        break;
      case "audit":
        await this.renderAudit();
        break;
    }
  },

  // ==================== 1. DASHBOARD ====================
  async renderDashboard() {
    try {
      const data = await API.get("/api/dashboard/summary");
      this.kpis = data.kpis;

      // Action banner
      const banner = document.getElementById("dashboard-action-banner");
      const bTitle = document.getElementById("dash-banner-title");
      const bDesc = document.getElementById("dash-banner-desc");
      if (banner && data.action_banner) {
        const bannerType = data.action_banner.type === 'critical' ? 'danger' : (data.action_banner.type === 'info' ? 'info' : 'success');
        banner.className = `notice-box ${bannerType}`;
        if (bTitle) bTitle.textContent = data.action_banner.title;
        if (bDesc) bDesc.textContent = data.action_banner.description;
      }

      // Metric elements
      const stockEl = document.getElementById("kpi-stock-val");
      const coverEl = document.getElementById("kpi-cover-val");
      const domTlcEl = document.getElementById("kpi-dom-tlc-val");
      const impTlcEl = document.getElementById("kpi-imp-tlc-val");
      const spreadEl = document.getElementById("kpi-spread-val");
      const alertsEl = document.getElementById("kpi-alerts-val");

      if (stockEl) stockEl.textContent = `${data.kpis.available_usable_stock_mt.toLocaleString()} MT`;
      if (coverEl) coverEl.textContent = `${data.kpis.coverage_days} Days`;
      if (domTlcEl) domTlcEl.textContent = `₹${Math.round(data.kpis.domestic_tlc_inr).toLocaleString()}`;
      if (impTlcEl) impTlcEl.textContent = `₹${Math.round(data.kpis.import_tlc_inr).toLocaleString()}`;
      if (spreadEl) spreadEl.textContent = `₹${Math.round(data.kpis.parity_spread_inr).toLocaleString()}`;
      if (alertsEl) alertsEl.textContent = data.kpis.critical_alerts_count;

      // Pending recommendation preview
      const rec = data.active_recommendation;
      const recContainer = document.getElementById("dashboard-active-rec");
      if (recContainer && rec) {
        recContainer.innerHTML = `
          <div style="border-left:3px solid var(--primary-color); padding-left:14px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span class="badge-pill warning">${rec.status}</span>
              <span class="num-mono" style="font-size:11.5px; color:var(--slate-500);">Docket #${rec.id}</span>
            </div>
            <h4 style="font-size:14.5px; font-weight:700; color:var(--slate-900); margin-bottom:6px;">${rec.recommended_action}</h4>
            <p style="font-size:12.5px; color:var(--slate-600); line-height:1.5; margin-bottom:12px;">${rec.why_preferred}</p>
            <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; background:var(--slate-50); padding:10px 12px; border-radius:var(--radius-sm); border:1px solid var(--border-default); font-size:12px;">
              <div>
                <div style="color:var(--slate-500); font-size:10.5px; text-transform:uppercase;">Volume</div>
                <div class="num-mono" style="font-weight:700; color:var(--primary-color); margin-top:2px;">${rec.recommended_qty_mt.toLocaleString()} MT</div>
              </div>
              <div>
                <div style="color:var(--slate-500); font-size:10.5px; text-transform:uppercase;">Estimated TLC</div>
                <div class="num-mono" style="font-weight:700; color:var(--slate-900); margin-top:2px;">₹${rec.estimated_tlc_mt.toLocaleString()}/MT</div>
              </div>
              <div>
                <div style="color:var(--slate-500); font-size:10.5px; text-transform:uppercase;">Target Arrival</div>
                <div class="num-mono" style="font-weight:600; color:var(--slate-900); margin-top:2px;">${rec.target_arrival_date}</div>
              </div>
            </div>
          </div>
        `;
      }

      // Mini market chart
      const mkt = await API.get("/api/market/history?days=30");
      Charts.renderMarketChart("chart-dashboard-market", mkt.dates, mkt.domestic_spot, mkt.cbot_usd);

    } catch (e) {
      console.error("Dashboard render error:", e);
    }
  },

  // ==================== 2. MARKET INTELLIGENCE ====================
  async renderMarket() {
    try {
      const hist = await API.get("/api/market/history?days=90");
      Charts.renderMarketChart("chart-market-history", hist.dates, hist.domestic_spot, hist.cbot_usd);

      const season = await API.get("/api/market/seasonality");
      Charts.renderSeasonalityChart("chart-market-seasonality", season.months, season.seasonality_pct);

      const forecast = await API.get("/api/market/forecast?horizon=45");
      Charts.renderForecastChart("chart-market-forecast", forecast.forecast_dates, forecast.expected_prices, forecast.upper_bounds, forecast.lower_bounds);

      // Backtest metrics
      const bm = forecast.backtest_metrics;
      const mapeEl = document.getElementById("mkt-mape");
      const rmseEl = document.getElementById("mkt-rmse");
      const accEl = document.getElementById("mkt-acc");

      if (mapeEl) mapeEl.textContent = `${bm["30d_mape_pct"]}%`;
      if (rmseEl) rmseEl.textContent = `₹${bm["30d_rmse_inr"]} / MT`;
      if (accEl) accEl.textContent = `${bm["directional_accuracy_pct"]}%`;

    } catch (e) {
      console.error("Market render error:", e);
    }
  },

  // ==================== 3. SUPPLIER INTELLIGENCE ====================
  async renderSuppliers() {
    try {
      const data = await API.get("/api/suppliers");
      const tbody = document.getElementById("suppliers-table-body");
      if (!tbody) return;
      tbody.innerHTML = "";

      data.suppliers.forEach(s => {
        const tr = document.createElement("tr");
        const qualBadge = s.is_quality_qualified 
          ? `<span class="badge-pill success">Verified / Qualified</span>`
          : `<span class="badge-pill danger">Disqualified</span>`;

        const originBadge = s.origin_type === 'Domestic' 
          ? `<span class="badge-pill neutral">Domestic</span>` 
          : `<span class="badge-pill info">International</span>`;

        tr.innerHTML = `
          <td style="font-weight:600; color:var(--slate-900);">${s.name}</td>
          <td>${s.location}, ${s.country}</td>
          <td>${originBadge}</td>
          <td class="num-mono" style="font-weight:600;">${s.rating_overall} / 5.0</td>
          <td class="num-mono">${s.price_per_mt ? `${s.currency === 'INR' ? '₹' : '$'}${s.price_per_mt.toLocaleString()}` : '-'}</td>
          <td class="num-mono">${s.lead_time_days ? `${s.lead_time_days} Days` : '-'}</td>
          <td>${qualBadge}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="App.viewSupplierDossier(${s.id})">
              Dossier & Audit
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) {
      console.error("Suppliers render error:", e);
    }
  },

  async viewSupplierDossier(id) {
    try {
      const data = await API.get(`/api/suppliers/${id}`);
      const modal = document.getElementById("modal-supplier-dossier");
      const titleEl = document.getElementById("dossier-vendor-name");
      const contentEl = document.getElementById("dossier-content");
      if (!modal || !contentEl) return;

      if (titleEl) titleEl.textContent = `${data.name} — Comprehensive Supplier Dossier`;

      const qualBadge = data.is_quality_qualified 
        ? `<span class="badge-pill success">Verified / Qualified</span>` 
        : `<span class="badge-pill danger">Disqualified (Lab Failure)</span>`;

      const quotesHtml = (data.quotations && data.quotations.length > 0)
        ? data.quotations.map(q => `
            <tr>
              <td class="num-mono">${q.quote_date}</td>
              <td class="num-mono" style="font-weight:600;">${q.currency === 'INR' ? '₹' : '$'}${q.price_per_mt.toLocaleString()}</td>
              <td class="num-mono">${q.available_quantity_mt.toLocaleString()} MT</td>
              <td>${q.delivery_point}</td>
              <td><span class="badge-pill ${q.status === 'Active' ? 'success' : 'neutral'}">${q.status}</span></td>
            </tr>
          `).join("")
        : `<tr><td colspan="5" style="text-align:center; color:var(--slate-500);">No recent quotations recorded.</td></tr>`;

      const qualityReportsHtml = (data.quality_reports && data.quality_reports.length > 0)
        ? data.quality_reports.map(qr => `
            <tr>
              <td class="num-mono">${qr.batch_id}</td>
              <td class="num-mono">${qr.sample_date}</td>
              <td class="num-mono">${qr.moisture_pct}%</td>
              <td class="num-mono">${qr.protein_pct}%</td>
              <td class="num-mono">${qr.oil_pct}%</td>
              <td class="num-mono">${qr.foreign_matter_pct}%</td>
              <td><span class="badge-pill ${qr.status === 'Passed' ? 'success' : 'danger'}">${qr.status}</span></td>
            </tr>
          `).join("")
        : `<tr><td colspan="7" style="text-align:center; color:var(--slate-500);">No laboratory inspections on record.</td></tr>`;

      contentEl.innerHTML = `
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:10px; margin-bottom:16px;">
          <div style="background:var(--slate-50); padding:10px; border-radius:var(--radius-sm); border:1px solid var(--border-default);">
            <div style="font-size:10.5px; color:var(--slate-500); font-weight:600; text-transform:uppercase;">Overall Score</div>
            <div class="num-mono" style="font-size:17px; font-weight:700; color:var(--slate-900); margin-top:2px;">${data.rating_overall} / 5.0</div>
          </div>
          <div style="background:var(--slate-50); padding:10px; border-radius:var(--radius-sm); border:1px solid var(--border-default);">
            <div style="font-size:10.5px; color:var(--slate-500); font-weight:600; text-transform:uppercase;">Quality Rating</div>
            <div class="num-mono" style="font-size:17px; font-weight:700; color:var(--slate-900); margin-top:2px;">${data.quality_score} / 5.0</div>
          </div>
          <div style="background:var(--slate-50); padding:10px; border-radius:var(--radius-sm); border:1px solid var(--border-default);">
            <div style="font-size:10.5px; color:var(--slate-500); font-weight:600; text-transform:uppercase;">Reliability</div>
            <div class="num-mono" style="font-size:17px; font-weight:700; color:var(--slate-900); margin-top:2px;">${data.reliability_score} / 5.0</div>
          </div>
          <div style="background:var(--slate-50); padding:10px; border-radius:var(--radius-sm); border:1px solid var(--border-default);">
            <div style="font-size:10.5px; color:var(--slate-500); font-weight:600; text-transform:uppercase;">Spec Pass Rate</div>
            <div class="num-mono" style="font-size:17px; font-weight:700; color:${data.quality_pass_rate_pct >= 90 ? 'var(--success-solid)' : 'var(--danger-solid)'}; margin-top:2px;">${data.quality_pass_rate_pct}%</div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px; background:var(--slate-50); padding:12px; border-radius:var(--radius-sm); border:1px solid var(--border-default); font-size:12px;">
          <div>
            <div style="color:var(--slate-500); margin-bottom:4px;">Origin & Classification: <strong>${data.origin_type} (${data.location}, ${data.country})</strong></div>
            <div style="color:var(--slate-500); margin-bottom:4px;">Compliance Gate: ${qualBadge}</div>
            <div style="color:var(--slate-500);">Monthly Capacity: <strong class="num-mono">${(data.capacity_monthly_mt || 0).toLocaleString()} MT</strong></div>
          </div>
          <div>
            <div style="color:var(--slate-500); margin-bottom:4px;">Standard Lead Time: <strong class="num-mono">${data.lead_time_days || '--'} Days</strong></div>
            <div style="color:var(--slate-500); margin-bottom:4px;">Payment Terms: <strong>${data.payment_terms || 'Net 30 Days'}</strong></div>
            <div style="color:var(--slate-500);">Total Inspected: <strong class="num-mono">${(data.total_inspected_mt || 0).toLocaleString()} MT (${(data.total_accepted_mt || 0).toLocaleString()} MT Usable)</strong></div>
          </div>
        </div>

        <h4 style="font-size:13px; font-weight:700; color:var(--slate-900); margin-bottom:8px;">Active Contract Quotes</h4>
        <div class="table-container" style="margin-bottom:16px;">
          <table class="data-table" style="font-size:12px;">
            <thead>
              <tr>
                <th>Date</th>
                <th>Price/MT</th>
                <th>Available Qty</th>
                <th>Delivery Point</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>${quotesHtml}</tbody>
          </table>
        </div>

        <h4 style="font-size:13px; font-weight:700; color:var(--slate-900); margin-bottom:8px;">Recent Quality Inspection Logs</h4>
        <div class="table-container">
          <table class="data-table" style="font-size:12px;">
            <thead>
              <tr>
                <th>Batch</th>
                <th>Sample Date</th>
                <th>Moisture</th>
                <th>Protein</th>
                <th>Oil</th>
                <th>Foreign Matter</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>${qualityReportsHtml}</tbody>
          </table>
        </div>
      `;

      this.openModal("modal-supplier-dossier");
    } catch (err) {
      API.showToast("Failed to load supplier dossier: " + err.message, "error");
    }
  },

  // ==================== 4. QUALITY GATE ====================
  async renderQuality() {
    try {
      const specsData = await API.get("/api/quality/specs");
      const specsBody = document.getElementById("quality-specs-body");
      if (specsBody) {
        specsBody.innerHTML = "";
        specsData.specs.forEach(sp => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td style="font-weight:600; color:var(--slate-900);">${sp.parameter_name}</td>
            <td>${sp.unit}</td>
            <td class="num-mono">${sp.min_limit !== null ? sp.min_limit : 'None'}</td>
            <td class="num-mono">${sp.max_limit !== null ? sp.max_limit : 'None'}</td>
            <td><span class="badge-pill success">Mandatory Gate</span></td>
            <td style="font-size:12px; color:var(--slate-600);">${sp.description}</td>
          `;
          specsBody.appendChild(tr);
        });
      }

      const repData = await API.get("/api/quality/reports");
      const repBody = document.getElementById("quality-reports-body");
      if (repBody) {
        repBody.innerHTML = "";
        repData.reports.forEach(r => {
          const tr = document.createElement("tr");
          const statusBadge = r.status === 'Passed' 
            ? `<span class="badge-pill success">Accepted</span>`
            : `<span class="badge-pill danger">Hard Rejected</span>`;

          tr.innerHTML = `
            <td class="num-mono" style="font-weight:600; color:var(--slate-900);">${r.batch_id}</td>
            <td>${r.supplier_name}</td>
            <td class="num-mono">${r.sample_date}</td>
            <td class="num-mono">${r.moisture_pct}%</td>
            <td class="num-mono">${r.protein_pct}%</td>
            <td class="num-mono">${r.oil_pct}%</td>
            <td class="num-mono">${r.foreign_matter_pct}%</td>
            <td>${statusBadge}</td>
            <td style="font-size:12px; color:${r.status === 'Rejected' ? 'var(--danger-solid)' : 'var(--slate-600)'};">${r.notes}</td>
          `;
          repBody.appendChild(tr);
        });
      }
    } catch (e) {
      console.error("Quality render error:", e);
    }
  },

  // ==================== 5. INVENTORY DYNAMICS ====================
  async renderInventory() {
    try {
      const inv = await API.get("/api/inventory/status");
      const physEl = document.getElementById("inv-physical");
      const usableEl = document.getElementById("inv-usable");
      const resEl = document.getElementById("inv-reserved");
      const availEl = document.getElementById("inv-available");
      const crushEl = document.getElementById("inv-crush");
      const safetyEl = document.getElementById("inv-safety");
      const ropEl = document.getElementById("inv-rop-dom");
      const netEl = document.getElementById("inv-net-req");

      if (physEl) physEl.textContent = `${inv.physical_stock_mt.toLocaleString()} MT`;
      if (usableEl) usableEl.textContent = `${inv.accepted_usable_mt.toLocaleString()} MT`;
      if (resEl) resEl.textContent = `${inv.reserved_mt.toLocaleString()} MT`;
      if (availEl) availEl.textContent = `${inv.available_usable_mt.toLocaleString()} MT`;
      if (crushEl) crushEl.textContent = `${inv.daily_crush_mt} MT / Day`;
      if (safetyEl) safetyEl.textContent = `${inv.safety_stock_mt.toLocaleString()} MT (${inv.safety_stock_days}d)`;
      if (ropEl) ropEl.textContent = `${inv.rop_domestic_mt.toLocaleString()} MT`;
      if (netEl) netEl.textContent = `${inv.net_requirement_30d_mt.toLocaleString()} MT`;

      // 30-day projection chart
      const proj = await API.get("/api/inventory/projection?days=30");
      Charts.renderInventoryChart("chart-inventory-projection", proj.timeline);

      // Incoming pipeline table
      const shipBody = document.getElementById("incoming-shipments-body");
      if (shipBody) {
        shipBody.innerHTML = "";
        inv.incoming_shipments.forEach(s => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td class="num-mono" style="font-weight:600; color:var(--slate-900);">${s.po_number}</td>
            <td>${s.supplier_name}</td>
            <td class="num-mono" style="font-weight:600;">${s.order_qty_mt.toLocaleString()} MT</td>
            <td><span class="badge-pill ${s.source_type === 'Domestic' ? 'neutral' : 'info'}">${s.source_type}</span></td>
            <td class="num-mono">${s.expected_arrival_date}</td>
            <td><span class="badge-pill warning">${s.status}</span></td>
            <td class="num-mono">₹${s.landed_cost_mt.toLocaleString()}</td>
          `;
          shipBody.appendChild(tr);
        });
      }
    } catch (e) {
      console.error("Inventory render error:", e);
    }
  },

  // ==================== 6. LANDED COST PARITY ====================
  async renderParity() {
    try {
      const parity = await API.get("/api/landed-cost/parity");
      const d = parity.domestic_tlc;
      const i = parity.import_tlc;
      const sp = parity.spread_analysis;

      document.getElementById("parity-dom-spot").textContent = `₹${d.base_spot_mt.toLocaleString()}`;
      document.getElementById("parity-dom-apmc").textContent = `₹${d.apmc_cess_amount.toLocaleString()} (${d.apmc_cess_pct}%)`;
      document.getElementById("parity-dom-freight").textContent = `₹${d.inland_freight_mt.toLocaleString()}`;
      document.getElementById("parity-dom-handling").textContent = `₹${d.handling_per_mt.toLocaleString()}`;
      document.getElementById("parity-dom-insurance").textContent = `₹${d.insurance_amount.toLocaleString()}`;
      document.getElementById("parity-dom-total").textContent = `₹${d.total_landed_cost_mt.toLocaleString()} / MT`;

      document.getElementById("parity-imp-cif-usd").textContent = `$${i.cif_usd_mt.toLocaleString()} / MT`;
      document.getElementById("parity-imp-cif-inr").textContent = `₹${i.cif_inr_mt.toLocaleString()} (@ ${i.usd_inr_rate})`;
      document.getElementById("parity-imp-duty").textContent = `₹${i.aidc_amount.toLocaleString()} (AIDC ${i.aidc_pct}%)`;
      document.getElementById("parity-imp-port").textContent = `₹${i.port_cha_mt.toLocaleString()}`;
      document.getElementById("parity-imp-freight").textContent = `₹${i.port_to_plant_freight_mt.toLocaleString()}`;
      document.getElementById("parity-imp-finance").textContent = `₹${i.transit_finance_cost_mt.toLocaleString()} (45d LC)`;
      document.getElementById("parity-imp-total").textContent = `₹${i.total_landed_cost_mt.toLocaleString()} / MT`;

      const spreadEl = document.getElementById("parity-spread-badge");
      if (spreadEl) {
        spreadEl.textContent = `₹${sp.parity_spread_mt.toLocaleString()} / MT (${sp.is_arbitrage_open ? 'Import Arbitrage Open' : 'Domestic Preferred'})`;
        spreadEl.className = `badge-pill ${sp.is_arbitrage_open ? 'info' : 'success'}`;
      }
      document.getElementById("parity-rationale-text").textContent = sp.rationale;

      // Sensitivity matrix table
      const sens = await API.get("/api/landed-cost/sensitivity");
      const sHead = document.getElementById("sensitivity-head");
      const sBody = document.getElementById("sensitivity-body");
      if (sHead && sBody) {
        sHead.innerHTML = `<th>CBOT CIF \\ USD/INR</th>` + sens.fx_headers.map(fx => `<th>₹${fx}</th>`).join("");
        sBody.innerHTML = "";
        sens.matrix.forEach(row => {
          const tr = document.createElement("tr");
          tr.innerHTML = `<td class="num-mono" style="font-weight:700;">$${row.cbot_usd}/MT</td>` + row.values.map(v => `
            <td class="num-mono" style="color:${v.is_import_favorable ? 'var(--primary-color)' : 'var(--slate-600)'}; font-weight:${v.is_import_favorable ? '700' : 'normal'};">
              ₹${Math.round(v.import_tlc).toLocaleString()} <span style="font-size:10px; color:var(--slate-400);">(${v.spread > 0 ? '+' : ''}${Math.round(v.spread)})</span>
            </td>
          `).join("");
          sBody.appendChild(tr);
        });
      }
    } catch (e) {
      console.error("Parity render error:", e);
    }
  },

  // ==================== 7. PROCUREMENT OPTIMIZER ====================
  async renderOptimization() {
    try {
      const opt = await API.get("/api/optimization/run");
      document.getElementById("opt-action-title").textContent = opt.recommended_action;
      document.getElementById("opt-channel").textContent = opt.sourcing_channel;
      document.getElementById("opt-qty").textContent = `${opt.recommended_qty_mt.toLocaleString()} MT`;
      document.getElementById("opt-tlc").textContent = `₹${opt.estimated_tlc_mt.toLocaleString()} / MT`;
      document.getElementById("opt-target-arrival").textContent = opt.target_arrival_date;
      document.getElementById("opt-why-text").textContent = opt.why_preferred;

      const altContainer = document.getElementById("opt-alternatives-container");
      if (altContainer) {
        altContainer.innerHTML = "";
        opt.alternatives.forEach(alt => {
          const card = document.createElement("div");
          card.className = "card";
          card.style.padding = "14px";
          card.innerHTML = `
            <div style="font-weight:700; font-size:13.5px; color:var(--slate-900); margin-bottom:4px;">${alt.plan_name}</div>
            <div style="font-size:12px; color:var(--primary-color); font-weight:600; margin-bottom:6px;">
              ${alt.quantity_mt.toLocaleString()} MT &bull; ${alt.channel} &bull; Est. ₹${alt.est_tlc_mt.toLocaleString()}/MT
            </div>
            <div style="font-size:12px; color:var(--slate-600); line-height:1.4;">${alt.trade_off}</div>
          `;
          altContainer.appendChild(card);
        });
      }
    } catch (e) {
      console.error("Optimization render error:", e);
    }
  },

  // ==================== 8. AGENT CONTROL CENTRE ====================
  async renderAgents() {
    try {
      const data = await API.get("/api/agents/control-center");
      const grid = document.getElementById("agents-grid");
      if (grid) {
        grid.innerHTML = "";
        data.agents.forEach(ag => {
          const card = document.createElement("div");
          card.className = "card";
          card.style.display = "flex";
          card.style.flexDirection = "column";
          card.style.gap = "8px";
          card.style.padding = "16px";

          let findingsHtml = Object.entries(ag.findings).map(([k, v]) => `
            <div style="font-size:11.5px; display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid var(--border-subtle);">
              <span style="color:var(--slate-500); text-transform:capitalize;">${k.replace(/_/g, ' ')}:</span>
              <span class="num-mono" style="font-weight:600; color:var(--slate-900);">${v}</span>
            </div>
          `).join("");

          let risksHtml = ag.risk_flags.map(r => `
            <div style="font-size:11px; color:var(--danger-solid); margin-bottom:2px;">&bull; ${r}</div>
          `).join("");

          card.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-default); padding-bottom:10px;">
              <div>
                <div style="font-weight:700; font-size:13.5px; color:var(--slate-900);">${ag.agent_name}</div>
                <div style="font-size:11px; color:var(--slate-500);">${ag.agent_role}</div>
              </div>
              <span class="badge-pill success">${ag.confidence_score_pct}% Confidence</span>
            </div>
            <div style="margin-top:6px;">${findingsHtml}</div>
            ${ag.risk_flags.length ? `<div style="background:var(--danger-subtle); padding:6px 8px; border-radius:var(--radius-sm); margin-top:6px; border:1px solid #FECACA;">${risksHtml}</div>` : ''}
            <div style="font-size:11.5px; background:var(--slate-50); padding:10px; border-radius:var(--radius-sm); margin-top:auto; font-weight:500; border-left:3px solid var(--primary-color);">
              <span style="font-weight:700; color:var(--slate-700);">Agent Vote:</span> ${ag.recommendation_input}
            </div>
          `;
          grid.appendChild(card);
        });
      }

      // Orchestrator Synthesis Panel
      const rec = data.final_recommendation;
      const dirEl = document.getElementById("orc-directive");
      const whyEl = document.getElementById("orc-why");
      const tfContainer = document.getElementById("orc-tradeoffs");

      if (dirEl) dirEl.textContent = rec.directive;
      if (whyEl) whyEl.textContent = rec.why_optimal;
      if (tfContainer) {
        tfContainer.innerHTML = rec.trade_off_resolution.map(t => `<li style="margin-bottom:6px; font-size:12.5px; color:var(--slate-700); line-height:1.4;">${t}</li>`).join("");
      }

    } catch (e) {
      console.error("Agents render error:", e);
    }
  },

  // ==================== 9. OPERATIONAL ALERTS ====================
  async renderAlerts() {
    try {
      const data = await API.get("/api/alerts");
      const container = document.getElementById("alerts-feed-container");
      if (!container) return;
      container.innerHTML = "";

      data.alerts.forEach(a => {
        const item = document.createElement("div");
        item.className = "card";
        const borderCol = a.severity === 'Critical' ? 'var(--danger-solid)' : (a.severity === 'Warning' ? 'var(--warning-solid)' : 'var(--primary-color)');
        item.style.borderLeft = `4px solid ${borderCol}`;
        item.style.marginBottom = "10px";
        item.style.padding = "14px 16px";

        const badgeClass = a.severity === 'Critical' ? 'danger' : (a.severity === 'Warning' ? 'warning' : 'info');

        item.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
            <div>
              <span class="badge-pill ${badgeClass}" style="margin-right:8px;">${a.severity}</span>
              <span class="badge-pill neutral">${a.category}</span>
              <strong style="margin-left:8px; font-size:13.5px; color:var(--slate-900);">${a.title}</strong>
            </div>
            <span class="num-mono" style="font-size:11px; color:var(--slate-400);">${a.timestamp}</span>
          </div>
          <p style="font-size:12.5px; color:var(--slate-600); line-height:1.4; margin-bottom:10px;">${a.message}</p>
          <div style="display:flex; justify-content:space-between; align-items:center; font-size:11.5px; color:var(--slate-500);">
            <span>Origin: <strong>${a.source}</strong> &bull; Scope: <strong>${a.affected_entity || 'Global'}</strong></span>
            <div>
              ${a.status === 'Active' ? `
                <button onclick="App.acknowledgeAlert(${a.id})" class="btn btn-secondary btn-sm" style="margin-right:6px;">Acknowledge</button>
                <button onclick="App.resolveAlert(${a.id})" class="btn btn-primary btn-sm">Mark Resolved</button>
              ` : `<span class="badge-pill neutral">${a.status}</span>`}
            </div>
          </div>
        `;
        container.appendChild(item);
      });
    } catch (e) {
      console.error("Alerts render error:", e);
    }
  },

  async acknowledgeAlert(id) {
    await API.post(`/api/alerts/${id}/acknowledge`);
    API.showToast(`Alert #${id} acknowledged.`);
    this.renderAlerts();
  },

  async resolveAlert(id) {
    const notes = prompt("Enter resolution notes for this operational alert:", "Investigated and verified root cause.");
    if (notes) {
      await API.post(`/api/alerts/${id}/resolve`, { notes });
      API.showToast(`Alert #${id} marked as resolved.`);
      this.renderAlerts();
    }
  },

  // ==================== 10. SCENARIOS SANDBOX ====================
  bindScenarioSliders() {
    const ids = ["scn-dom-shock", "scn-duty", "scn-fx", "scn-freight", "scn-delay", "scn-reject"];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener("input", () => this.runScenarioSimulation());
      }
    });
  },

  async runScenarioSimulation() {
    const dom_shock = parseFloat(document.getElementById("scn-dom-shock")?.value || 0);
    const duty = parseFloat(document.getElementById("scn-duty")?.value || 0);
    const fx = parseFloat(document.getElementById("scn-fx")?.value || 86.5);
    const freight = parseFloat(document.getElementById("scn-freight")?.value || 42);
    const delay = parseInt(document.getElementById("scn-delay")?.value || 0);
    const reject = parseFloat(document.getElementById("scn-reject")?.value || 0);

    // Update value indicators
    const vShock = document.getElementById("val-dom-shock");
    const vDuty = document.getElementById("val-duty");
    const vFx = document.getElementById("val-fx");
    const vFreight = document.getElementById("val-freight");
    const vDelay = document.getElementById("val-delay");
    const vReject = document.getElementById("val-reject");

    if (vShock) vShock.textContent = `${dom_shock > 0 ? '+' : ''}${dom_shock}%`;
    if (vDuty) vDuty.textContent = `${duty}%`;
    if (vFx) vFx.textContent = `₹${fx}`;
    if (vFreight) vFreight.textContent = `$${freight}/MT`;
    if (vDelay) vDelay.textContent = `+${delay} Days`;
    if (vReject) vReject.textContent = `${reject}%`;

    const res = await API.post("/api/scenarios/simulate", {
      domestic_price_shock_pct: dom_shock,
      import_duty_pct: duty,
      usd_inr_rate: fx,
      ocean_freight_usd_mt: freight,
      supplier_delay_days: delay,
      quality_rejection_pct: reject
    });

    const resDom = document.getElementById("scn-res-dom-tlc");
    const resImp = document.getElementById("scn-res-imp-tlc");
    const resSpread = document.getElementById("scn-res-spread");
    const resUsable = document.getElementById("scn-res-usable");
    const resStrat = document.getElementById("scn-res-strategy");
    const resSum = document.getElementById("scn-res-summary");

    if (resDom) resDom.textContent = `₹${Math.round(res.domestic_tlc_mt).toLocaleString()}`;
    if (resImp) resImp.textContent = `₹${Math.round(res.import_tlc_mt).toLocaleString()}`;
    if (resSpread) resSpread.textContent = `₹${Math.round(res.parity_spread_mt).toLocaleString()}`;
    if (resUsable) resUsable.textContent = `₹${Math.round(res.domestic_usable_cost_mt).toLocaleString()}`;
    if (resStrat) resStrat.textContent = res.strategy.replace(/_/g, ' ');
    if (resSum) resSum.textContent = res.impact_summary;
  },

  async renderScenarios() {
    this.runScenarioSimulation();
  },

  // ==================== 11. PURCHASE AUTHORIZATION ====================
  async renderApprovals() {
    try {
      const data = await API.get("/api/recommendations");
      const container = document.getElementById("approvals-list-container");
      if (!container) return;
      container.innerHTML = "";

      data.recommendations.forEach(r => {
        const item = document.createElement("div");
        item.className = "card";
        item.style.marginBottom = "14px";
        item.style.padding = "16px";

        const badgeClass = r.status.includes('Approved') ? 'success' : (r.status === 'Rejected' ? 'danger' : 'warning');

        item.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
            <div>
              <span class="badge-pill ${badgeClass}" style="margin-right:8px;">${r.status}</span>
              <span class="num-mono" style="font-size:11.5px; color:var(--slate-500);">Docket #${r.id} &bull; ${r.created_at}</span>
              <h3 style="font-size:15px; font-weight:700; color:var(--slate-900); margin-top:4px;">${r.recommended_action}</h3>
            </div>
            <div style="text-align:right;">
              <div style="font-size:11px; color:var(--slate-500); text-transform:uppercase;">Estimated Total Commitment</div>
              <div class="num-mono" style="font-size:18px; font-weight:700; color:var(--slate-900); margin-top:2px;">₹${Math.round(r.recommended_qty_mt * r.estimated_tlc_mt).toLocaleString()}</div>
            </div>
          </div>
          <p style="font-size:13px; color:var(--slate-700); line-height:1.5; margin-bottom:12px;">${r.why_preferred}</p>
          <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:12px; background:var(--slate-50); padding:10px 14px; border-radius:var(--radius-sm); border:1px solid var(--border-default); font-size:12px; margin-bottom:12px;">
            <div><span style="color:var(--slate-500);">Volume:</span> <strong class="num-mono">${r.recommended_qty_mt.toLocaleString()} MT</strong></div>
            <div><span style="color:var(--slate-500);">Unit TLC:</span> <strong class="num-mono">₹${r.estimated_tlc_mt.toLocaleString()}/MT</strong></div>
            <div><span style="color:var(--slate-500);">Target Delivery:</span> <strong class="num-mono">${r.target_arrival_date}</strong></div>
            <div><span style="color:var(--slate-500);">Cover Extension:</span> <strong class="num-mono">${r.projected_stock_cover_days} Days</strong></div>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-default); padding-top:12px;">
            <div style="font-size:12px; color:var(--slate-500);">
              ${r.approver_name ? `Authorized by: <strong style="color:var(--slate-900);">${r.approver_name} (${r.approver_role})</strong> on ${r.approved_at}` : 'Status: Pending executive decision'}
            </div>
            <div>
              ${r.status === 'Submitted for Review' ? `
                <button onclick="App.openApprovalModal(${r.id}, 'Approve')" class="btn btn-primary btn-sm" style="margin-right:6px;">Approve Plan</button>
                <button onclick="App.openApprovalModal(${r.id}, 'Modify')" class="btn btn-secondary btn-sm" style="margin-right:6px;">Adjust Volume</button>
                <button onclick="App.openApprovalModal(${r.id}, 'Reject')" class="btn btn-danger btn-sm">Reject</button>
              ` : `<span style="font-size:12px; color:var(--slate-500);"><em>Sign-off note: ${r.approval_notes || 'None'}</em></span>`}
            </div>
          </div>
        `;
        container.appendChild(item);
      });
    } catch (e) {
      console.error("Approvals render error:", e);
    }
  },

  openApprovalModal(id, action) {
    if (this.currentUser.role !== "Procurement Head" && this.currentUser.role !== "Super Admin") {
      API.showToast(`Role Barrier: Only Procurement Head or Super Admin can authorize purchases. Please switch active user context in top bar.`, "error");
      return;
    }
    const modal = document.getElementById("approval-modal");
    if (modal) {
      document.getElementById("modal-rec-id").value = id;
      document.getElementById("modal-action-type").value = action;
      document.getElementById("modal-action-title").textContent = `${action} Procurement Docket #${id}`;
      document.getElementById("modal-modify-fields").style.display = (action === "Modify") ? "block" : "none";
      this.openModal("approval-modal");
    }
  },

  // ==================== 12. AUDIT TRAIL ====================
  async renderAudit() {
    try {
      const data = await API.get("/api/audit/logs?limit=50");
      const tbody = document.getElementById("audit-table-body");
      if (!tbody) return;
      tbody.innerHTML = "";

      data.logs.forEach(l => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="num-mono" style="font-size:11.5px; color:var(--slate-500);">${l.timestamp}</td>
          <td style="font-weight:600; color:var(--slate-900);">${l.user_name}</td>
          <td><span class="badge-pill neutral">${l.user_role}</span></td>
          <td class="num-mono" style="color:var(--primary-color); font-weight:600;">${l.action}</td>
          <td>${l.entity_type} ${l.entity_id ? `(#${l.entity_id})` : ''}</td>
          <td class="num-mono" style="font-size:11.5px; color:var(--slate-700);">${l.details_json}</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) {
      console.error("Audit render error:", e);
    }
  },

  // ==================== MODAL HELPERS ====================
  closeAllModals() {
    document.querySelectorAll(".modal-overlay").forEach(m => {
      m.classList.add("hidden");
      m.style.display = "none";
    });
  },

  openModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) {
      m.classList.remove("hidden");
      m.style.display = "flex";
    }
  },

  bindModals() {
    // Close modal buttons
    document.querySelectorAll(".modal-close-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        this.closeAllModals();
      });
    });

    // Close on backdrop click
    document.querySelectorAll(".modal-overlay").forEach(overlay => {
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) {
          this.closeAllModals();
        }
      });
    });

    // Close on Escape
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.closeAllModals();
      }
    });

    // Approval form submit
    const approvalForm = document.getElementById("approval-form");
    if (approvalForm) {
      approvalForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.getElementById("modal-rec-id").value;
        const action = document.getElementById("modal-action-type").value;
        const notes = document.getElementById("modal-notes").value;
        const modQty = parseFloat(document.getElementById("modal-mod-qty")?.value || 0);

        try {
          await API.post(`/api/recommendations/${id}/action`, {
            action,
            notes,
            modified_qty_mt: modQty > 0 ? modQty : null
          });
          API.showToast(`Procurement Docket #${id} ${action.toLowerCase()}d successfully.`);
          this.closeAllModals();
          this.renderApprovals();
        } catch (err) {
          API.showToast(err.message, "error");
        }
      });
    }
  },

  // ==================== OPERATIONAL FORM HANDLERS ====================
  async handlePriceUpdate() {
    try {
      const origin = document.getElementById("manual-origin").value;
      const price = parseFloat(document.getElementById("manual-price").value);
      const fx = parseFloat(document.getElementById("manual-fx").value);
      const source = document.getElementById("manual-source").value;

      await API.post("/api/market/update-price", {
        origin,
        price_per_mt: price,
        usd_inr_rate: fx,
        source
      });

      API.showToast(`Spot quote of ₹${price.toLocaleString()}/MT persisted.`);
      this.closeAllModals();
      await this.loadView(this.currentView);
    } catch (err) {
      API.showToast("Failed to record price quote: " + err.message, "error");
    }
  },

  async handleBatchTest() {
    try {
      const moisture = parseFloat(document.getElementById("test-moisture").value);
      const protein = parseFloat(document.getElementById("test-protein").value);
      const oil = parseFloat(document.getElementById("test-oil").value);
      const fm = parseFloat(document.getElementById("test-fm").value);
      const damaged = parseFloat(document.getElementById("test-damaged").value);

      const res = await API.post("/api/quality/evaluate-batch", {
        moisture_pct: moisture,
        protein_pct: protein,
        oil_pct: oil,
        foreign_matter_pct: fm,
        damaged_pct: damaged
      });

      const box = document.getElementById("test-result-box");
      if (box) {
        box.style.display = "block";
        if (res.status === "Passed") {
          box.className = "notice-box success";
          box.innerHTML = `<strong>SPECIFICATION GATE PASSED</strong>: Batch complies with all contract parameters (Moisture ${moisture}%, Protein ${protein}%, Oil ${oil}%, FM ${fm}%).`;
        } else {
          box.className = "notice-box danger";
          box.innerHTML = `<strong>HARD SPECIFICATION REJECTION</strong>: ${res.reasons.join("; ")}. Batch cannot be received into plant silos.`;
        }
      }
    } catch (err) {
      API.showToast("Batch evaluation failed: " + err.message, "error");
    }
  },

  async handleInventoryUpdate() {
    try {
      const physical = parseFloat(document.getElementById("upd-physical").value);
      const usable = parseFloat(document.getElementById("upd-usable").value);
      const crush = parseFloat(document.getElementById("upd-crush").value);
      const safety = parseFloat(document.getElementById("upd-safety").value);

      await API.post("/api/inventory/update", {
        physical_stock_mt: physical,
        accepted_usable_mt: usable,
        daily_crush_mt: crush,
        safety_stock_mt: safety
      });

      API.showToast(`Silo stock calibrated: ${usable.toLocaleString()} MT usable @ ${crush} MT/day crush.`);
      this.closeAllModals();
      await this.loadView(this.currentView);
    } catch (err) {
      API.showToast("Failed to update inventory: " + err.message, "error");
    }
  }
};
