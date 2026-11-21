// SoyaSetu Chart.js Renderers
const Charts = {
  instances: {},

  destroy(id) {
    if (this.instances[id]) {
      this.instances[id].destroy();
      delete this.instances[id];
    }
  },

  renderMarketChart(canvasId, dates, domPrices, cbotPrices) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: "Indore Mandi Spot (₹/MT)",
            data: domPrices,
            borderColor: "#0D9488",
            backgroundColor: "rgba(13, 148, 136, 0.08)",
            borderWidth: 2,
            tension: 0.2,
            yAxisID: "yDom",
            pointRadius: 0,
            pointHoverRadius: 4,
            fill: true
          },
          {
            label: "CBOT Soybean Active ($/MT)",
            data: cbotPrices,
            borderColor: "#3B82F6",
            borderDash: [5, 4],
            borderWidth: 1.8,
            tension: 0.2,
            yAxisID: "yIntl",
            pointRadius: 0,
            pointHoverRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { size: 11, family: "Inter" } } },
          tooltip: {
            padding: 10,
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.dataset.yAxisID === "yDom" ? "₹" : "$"}${ctx.parsed.y.toLocaleString()}`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10 }, maxTicksLimit: 8 } },
          yDom: {
            type: "linear",
            position: "left",
            title: { display: true, text: "Domestic Spot (₹/MT)", font: { size: 11 } },
            grid: { color: "#F1F5F9" }
          },
          yIntl: {
            type: "linear",
            position: "right",
            title: { display: true, text: "CBOT ($/MT)", font: { size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  },

  renderSeasonalityChart(canvasId, months, pctData) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const bgColors = pctData.map(v => v < 0 ? "#10B981" : "#EF4444");

    this.instances[canvasId] = new Chart(ctx, {
      type: "bar",
      data: {
        labels: months,
        datasets: [{
          label: "Seasonal Price Deviation from Annual Mean (%)",
          data: pctData,
          backgroundColor: bgColors,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `Deviation: ${ctx.parsed.y > 0 ? "+" : ""}${ctx.parsed.y}%`
            }
          }
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            title: { display: true, text: "% Deviation", font: { size: 11 } },
            grid: { color: "#F1F5F9" }
          }
        }
      }
    });
  },

  renderForecastChart(canvasId, dates, expected, upper, lower) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    this.instances[canvasId] = new Chart(ctx, {
      type: "line",
      data: {
        labels: dates,
        datasets: [
          {
            label: "Upper 95% Confidence Bound",
            data: upper,
            borderColor: "transparent",
            backgroundColor: "rgba(59, 130, 246, 0.12)",
            fill: "+1",
            pointRadius: 0
          },
          {
            label: "Lower 95% Confidence Bound",
            data: lower,
            borderColor: "transparent",
            fill: false,
            pointRadius: 0
          },
          {
            label: "Expected Domestic Spot (SARIMAX)",
            data: expected,
            borderColor: "#2563EB",
            borderWidth: 2.2,
            tension: 0.25,
            pointRadius: 0,
            pointHoverRadius: 5
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { labels: { boxWidth: 12, font: { size: 11 } } },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ₹${ctx.parsed.y.toLocaleString()}`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { maxTicksLimit: 7 } },
          y: {
            title: { display: true, text: "Price (₹/MT)", font: { size: 11 } },
            grid: { color: "#F1F5F9" }
          }
        }
      }
    });
  },

  renderInventoryChart(canvasId, timeline) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const list = Array.isArray(timeline) ? timeline : (timeline?.timeline || timeline?.projection || []);
    if (!list.length) return;

    const labels = list.map(t => t.date);
    const stock = list.map(t => t.stock_mt);
    const safety = list.map(t => t.safety_stock_mt);

    this.instances[canvasId] = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Projected Usable Stock (MT)",
            data: stock,
            borderColor: "#0F766E",
            backgroundColor: "rgba(15, 118, 110, 0.08)",
            borderWidth: 2.5,
            fill: true,
            tension: 0.15,
            pointRadius: 0,
            pointHoverRadius: 4
          },
          {
            label: "Mandatory Safety Stock Threshold",
            data: safety,
            borderColor: "#DC2626",
            borderDash: [6, 4],
            borderWidth: 2,
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString()} MT`
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
          y: {
            title: { display: true, text: "Inventory (MT)", font: { size: 11 } },
            grid: { color: "#F1F5F9" }
          }
        }
      }
    });
  }
};
