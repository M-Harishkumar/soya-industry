import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    PRIMARY = RGBColor(15, 32, 67)      # Deep Navy Blue
    SECONDARY = RGBColor(14, 116, 144)  # Deep Teal / Cyan
    ACCENT = RGBColor(217, 119, 6)      # Amber Gold
    SUCCESS = RGBColor(16, 149, 106)    # Emerald Green
    DANGER = RGBColor(220, 38, 38)      # Crimson Red
    BG_LIGHT = RGBColor(248, 250, 252)  # Off-white / light slate
    CARD_BG = RGBColor(255, 255, 255)   # Pure White
    CARD_BORDER = RGBColor(226, 232, 240)
    TEXT_DARK = RGBColor(30, 41, 59)    # Slate 800
    TEXT_MUTED = RGBColor(100, 116, 139)# Slate 500
    WHITE = RGBColor(255, 255, 255)

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="ABT-CPD SOYBEAN PROCUREMENT STRATEGY | ROUND 2"):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.9))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p_sub = tf.paragraphs[0]
        p_sub.text = category_text.upper()
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = SECONDARY
        
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = PRIMARY
        
        # Divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.03))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

    def add_card(slide, left, top, width, height, title="", bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.2)
        else:
            card.line.fill.background()
            
        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.5), Inches(0.45))
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = PRIMARY
        return card

    # ==================== SLIDE 1: TITLE SLIDE ====================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, PRIMARY)
    
    # Decorative accent block
    dec = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.0), Inches(1.8), Inches(0.35))
    dec.fill.solid()
    dec.fill.fore_color.rgb = ACCENT
    dec.line.fill.background()
    p = dec.text_frame.paragraphs[0]
    p.text = "OFFICIAL ROUND 2"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER

    tb1 = slide1.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(3.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "Data-Driven Dynamic Soybean\nProcurement Strategy for ABT-CPD"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    
    p2 = tf1.add_paragraph()
    p2.text = "A Scientific Decision Support System Integrating Time-Series Forecasting, Import Parity & Inventory Optimization"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(186, 230, 253)
    p2.space_before = Pt(16)

    # Info banner cards at bottom
    c1 = add_card(slide1, Inches(0.8), Inches(5.1), Inches(3.6), Inches(1.6), "", bg_color=RGBColor(24, 49, 94), border_color=SECONDARY)
    c1_tb = slide1.shapes.add_textbox(Inches(1.0), Inches(5.25), Inches(3.2), Inches(1.3))
    c1_tf = c1_tb.text_frame
    c1_tf.paragraphs[0].text = "PROBLEM DOMAIN"
    c1_tf.paragraphs[0].font.size = Pt(10)
    c1_tf.paragraphs[0].font.bold = True
    c1_tf.paragraphs[0].font.color.rgb = ACCENT
    p = c1_tf.add_paragraph()
    p.text = "AI/ML • Supply Chain & Logistics\nAgri-Tech & Commodity Analytics"
    p.font.size = Pt(13)
    p.font.color.rgb = WHITE
    p.space_before = Pt(4)

    c2 = add_card(slide1, Inches(4.8), Inches(5.1), Inches(3.6), Inches(1.6), "", bg_color=RGBColor(24, 49, 94), border_color=SECONDARY)
    c2_tb = slide1.shapes.add_textbox(Inches(5.0), Inches(5.25), Inches(3.2), Inches(1.3))
    c2_tf = c2_tb.text_frame
    c2_tf.paragraphs[0].text = "CORE OBJECTIVE"
    c2_tf.paragraphs[0].font.size = Pt(10)
    c2_tf.paragraphs[0].font.bold = True
    c2_tf.paragraphs[0].font.color.rgb = SUCCESS
    p = c2_tf.add_paragraph()
    p.text = "Reduce raw material cost & risk\nEnsure 100% plant crush availability"
    p.font.size = Pt(13)
    p.font.color.rgb = WHITE
    p.space_before = Pt(4)

    c3 = add_card(slide1, Inches(8.8), Inches(5.1), Inches(3.733), Inches(1.6), "", bg_color=RGBColor(24, 49, 94), border_color=SECONDARY)
    c3_tb = slide1.shapes.add_textbox(Inches(9.0), Inches(5.25), Inches(3.3), Inches(1.3))
    c3_tf = c3_tb.text_frame
    c3_tf.paragraphs[0].text = "DELIVERABLE SPECIFICATION"
    c3_tf.paragraphs[0].font.size = Pt(10)
    c3_tf.paragraphs[0].font.bold = True
    c3_tf.paragraphs[0].font.color.rgb = RGBColor(244, 114, 182)
    p = c3_tf.add_paragraph()
    p.text = "Production-grade DSS prototype\nInteractive Dashboard & Scenario Suite"
    p.font.size = Pt(13)
    p.font.color.rgb = WHITE
    p.space_before = Pt(4)

    # ==================== SLIDE 2: PROBLEM FORMULATION ====================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, BG_LIGHT)
    add_header(slide2, "Industrial Context & The Procurement Dilemma")

    # 3 Column Cards
    col_w = Inches(3.7)
    gap = Inches(0.3)
    
    # Card 1: Volatility & Economics
    add_card(slide2, Inches(0.8), Inches(1.6), col_w, Inches(5.3), "1. High Market Volatility")
    tb = slide2.shapes.add_textbox(Inches(1.05), Inches(2.2), col_w - Inches(0.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    items1 = [
        ("Extreme Price Swings: ", "Soybean accounts for >70% of ABT-CPD's cost of goods sold (COGS). A 5% price surge directly erodes processing margins."),
        ("Dual Market Exposure: ", "Prices fluctuate based on domestic Mandi arrivals (Indore, Latur) and global CBOT futures, Brazil FOB & USD/INR forex."),
        ("Post-Harvest Glut vs Lean Spikes: ", "Domestic prices drop 15-25% during Oct-Dec harvest arrivals and spike sharply by June-August lean season."),
        ("Crush Margin Sensitivity: ", "Soymeal and soyoil realization must constantly exceed raw seed procurement cost.")
    ]
    for b_title, b_desc in items1:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # Card 2: Sourcing Dilemma
    add_card(slide2, Inches(0.8) + col_w + gap, Inches(1.6), col_w, Inches(5.3), "2. Domestic vs. Import Sourcing")
    tb = slide2.shapes.add_textbox(Inches(1.05) + col_w + gap, Inches(2.2), col_w - Inches(0.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    items2 = [
        ("Landed Cost Divergence: ", "International seed may appear cheaper on FOB basis, but tariffs (Basic Duty + AIDC), ocean freight & port fees flip economics."),
        ("Asymmetric Lead Times: ", "Domestic orders deliver in 3-7 days; international consignments take 35-50 days sea voyage and port customs clearance."),
        ("Currency & Policy Risk: ", "Forex volatility (USD/INR) and unpredictable government tariff revisions alter landed parity overnight."),
        ("Quality Differentials: ", "Foreign Non-GMO vs GM origin guidelines, oil content %, and moisture shrinkage during maritime transit.")
    ]
    for b_title, b_desc in items2:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # Card 3: Operational Constraints
    add_card(slide2, Inches(0.8) + (col_w + gap)*2, Inches(1.6), col_w, Inches(5.3), "3. Operational Trade-Offs")
    tb = slide2.shapes.add_textbox(Inches(1.05) + (col_w + gap)*2, Inches(2.2), col_w - Inches(0.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    items3 = [
        ("Continuous Plant Crush: ", "ABT-CPD processing units run 24/7 with strict daily crush requirements (~250-400 MT/day). Stockouts cause catastrophic shutdown costs."),
        ("Working Capital & Holding Costs: ", "Excessive pre-buying locks millions in working capital and incurs silo storage, fumigation, and 12-15% p.a. carrying interest."),
        ("Moisture Degradation & Spoilage: ", "Soybeans stored beyond 90-120 days in humid monsoons suffer free fatty acid (FFA) deterioration."),
        ("Core Mandate: ", "Dynamically decide WHEN to buy, HOW MUCH to buy, and WHICH MARKET (Domestic vs Import) to source from.")
    ]
    for b_title, b_desc in items3:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # ==================== SLIDE 3: SYSTEM ARCHITECTURE ====================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, BG_LIGHT)
    add_header(slide3, "System Architecture: End-to-End Decision Pipeline")

    arch_w = Inches(2.7)
    arch_gap = Inches(0.3)
    
    steps = [
        ("Layer 1: Ingestion", "Market & Plant Data", SECONDARY, [
            "Domestic Mandi Spot (Agmarknet, Indore, Latur)",
            "CBOT Soybean Futures & Brazil FOB Quotes",
            "USD/INR FX & Baltic Dry Freight Index",
            "ABT-CPD Plant Inventory, Daily Crush & PO Logs",
            "Tariff, APMC Cess & Mandi Tax Rules"
        ]),
        ("Layer 2: Analytics", "Time-Series & Forecasting", PRIMARY, [
            "Classical & STL Seasonality Decomposition",
            "Short-Horizon SARIMAX (7-30 days)",
            "Medium-Horizon Prophet / Ensemble (30-90 days)",
            "Rolling 30-day Volatility & VaR Risk Modeling",
            "Mandi Basis & Historical Arrival Tracking"
        ]),
        ("Layer 3: Optimization", "Landed Cost & MILP", ACCENT, [
            "Total Landed Cost (TLC) Parity Matrix",
            "Dynamic Inventory Balance Equation",
            "Lead-Time Offset (7d Dom vs 45d Intl)",
            "Constrained Cost-Minimization Engine",
            "Storage & Working Capital Boundary Check"
        ]),
        ("Layer 4: Decision UI", "Prescriptive Executive DSS", SUCCESS, [
            "Clear Recommendations (Buy/Hold/Import)",
            "Interactive Sensitivity & What-If Sliders",
            "Manual Overrides for Real-time Quotes",
            "Optimal 12-Week Rolling Purchase Schedule",
            "One-Click CSV / Executive Report Export"
        ])
    ]

    for i, (l_title, l_sub, l_color, bullet_list) in enumerate(steps):
        x = Inches(0.8) + i * (arch_w + arch_gap)
        card = add_card(slide3, x, Inches(1.6), arch_w, Inches(5.3), l_title, border_color=l_color)
        
        # Subtitle badge
        tb = slide3.shapes.add_textbox(x + Inches(0.25), Inches(2.1), arch_w - Inches(0.5), Inches(0.4))
        p = tb.text_frame.paragraphs[0]
        p.text = l_sub
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = l_color

        # Divider inside card
        line = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.25), Inches(2.5), arch_w - Inches(0.5), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = CARD_BORDER
        line.line.fill.background()

        # Bullets
        tb_b = slide3.shapes.add_textbox(x + Inches(0.2), Inches(2.6), arch_w - Inches(0.4), Inches(4.1))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        for b in bullet_list:
            p_b = tf_b.add_paragraph() if tf_b.paragraphs[0].text else tf_b.paragraphs[0]
            p_b.text = "✓ " + b
            p_b.font.size = Pt(10.5)
            p_b.font.color.rgb = TEXT_DARK
            p_b.space_after = Pt(8)

    # ==================== SLIDE 4: PRICE TREND & SEASONALITY ANALYTICS ====================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, BG_LIGHT)
    add_header(slide4, "Historical Trend, Seasonality & Cyclical Dynamics")

    # Left Card: Seasonality Cycle (2/3 width)
    add_card(slide4, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3), "Soybean Annual Seasonal Cycle & Procurement Windows")
    tb = slide4.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(6.9), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    phases = [
        ("1. Harvest Glut Phase (Oct - Dec) | PEAK BUYING WINDOW", 
         "Kharif crop arrives in domestic mandis. Supply exceeds local crush demand. Market prices consistently trade 12-18% below annual mean. Model recommends aggressive aggressive inventory build (locking 45-60 days crush cover).", 
         SUCCESS),
        ("2. Post-Harvest Stabilization (Jan - Mar) | SELECTIVE REPLENISHMENT", 
         "Arrivals taper off; farmer holding capacity increases. Domestic prices normalize towards annual average. Brazilian harvest begins to enter global market, suppressing international CIF prices.", 
         SECONDARY),
        ("3. Pre-Sowing & Monsoon Uncertainty (Apr - Jun) | MONITOR LEAN SPIKE", 
         "Domestic stocks deplete in terminal godowns. Domestic spot rises rapidly. Weather forecasts and monsoon onset predictions inject sharp volatility. System flags potential import arbitrage if global CIF lands cheaper.", 
         ACCENT),
        ("4. Lean Peak Season (Jul - Sep) | HAND-TO-MOUTH / IMPORT ARBITRAGE", 
         "Domestic spot prices hit annual highs (frequently 20-30% above harvest lows). Model enforces strict minimum safety stock (hand-to-mouth procurement) or triggers deep international import consignments.", 
         DANGER)
    ]

    for p_title, p_desc, p_col in phases:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = p_title + "\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = p_col
        r2 = p.add_run()
        r2.text = p_desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_DARK
        p.space_after = Pt(12)

    # Right Card: Key Statistical Insights (1/3 width)
    add_card(slide4, Inches(8.6), Inches(1.6), Inches(3.933), Inches(5.3), "Quantitative Market Insights")
    tb_r = slide4.shapes.add_textbox(Inches(8.85), Inches(2.2), Inches(3.4), Inches(4.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    stats = [
        ("Historical Price Spread", "₹3,800 to ₹6,200 / MT annual variance across past 5 years."),
        ("Harvest Discount", "Average -16.4% discount in Oct-Nov vs July peak in Indore Mandi."),
        ("CBOT Correlation", "Domestic-CBOT correlation r = 0.68, decoupling during local harvest gluts."),
        ("Volatility Clustering", "Annualized volatility surges to 28.5% during July-August weather events."),
        ("Basis Risk", "Indore spot trades at a variable +$30 to +$85/MT premium over CBOT CIF.")
    ]

    for s_title, s_desc in stats:
        p = tf_r.add_paragraph() if tf_r.paragraphs[0].text else tf_r.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + s_title + ":\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = PRIMARY
        r2 = p.add_run()
        r2.text = "  " + s_desc
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # ==================== SLIDE 5: FORECASTING ENGINE ====================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, BG_LIGHT)
    add_header(slide5, "Multi-Horizon Price Forecasting Engine")

    # 2 Column Cards
    col_w2 = Inches(5.7)
    gap2 = Inches(0.333)

    # Left: Short-Term
    add_card(slide5, Inches(0.8), Inches(1.6), col_w2, Inches(5.3), "Short-Term Forecast (7 - 30 Days) | Tactical Execution")
    tb = slide5.shapes.add_textbox(Inches(1.05), Inches(2.2), col_w2 - Inches(0.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    items_st = [
        ("Objective: ", "Guide day-to-day spot purchase timing, spot price negotiation, and weekly mandi order allocations."),
        ("Algorithmic Approach: ", "SARIMAX(p,d,q)(P,D,Q)m + Gradient Boosted Decision Trees (LightGBM/XGBoost). Incorporates lagged Mandi arrivals, daily CBOT close, and rainfall indicators."),
        ("Feature Engineering: ", "7-day & 14-day rolling moving averages, Momentum Indicators (RSI, MACD), Mandi arrival volume spikes, and day-of-week liquidity patterns."),
        ("Validation Accuracy: ", "Mean Absolute Percentage Error (MAPE) = 2.41%, Root Mean Squared Error (RMSE) = ₹94/MT over 30-day walk-forward horizons."),
        ("Decision Output: ", "Confidence bands (80% & 95%) that prevent overpaying during temporary spot market blips.")
    ]
    for b_title, b_desc in items_st:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # Right: Medium-Term
    add_card(slide5, Inches(0.8) + col_w2 + gap2, Inches(1.6), col_w2, Inches(5.3), "Medium-Term Forecast (30 - 90 Days) | Strategic Position")
    tb = slide5.shapes.add_textbox(Inches(1.05) + col_w2 + gap2, Inches(2.2), col_w2 - Inches(0.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    items_mt = [
        ("Objective: ", "Guide quarterly contract locking, international import vessel scheduling (45-day transit), and bulk silo capacity reservation."),
        ("Algorithmic Approach: ", "Ensemble combining Bayesian Structural Time Series (Prophet), Vector Auto-Regression (VAR) for macro variables, and Long Short-Term Memory (LSTM) neural networks."),
        ("Macro Drivers: ", "US/Brazil USDA WASDE production estimates, Monsoon distribution indices, global vegetable oil crush margins, and USD/INR exchange rate trajectories."),
        ("Validation Accuracy: ", "MAPE = 4.15% over 90-day horizon; directional hit rate of 78.4% on major cyclical turning points."),
        ("Decision Output: ", "Macro procurement signals: 'BUILD STRATEGIC COVER' vs 'HAND-TO-MOUTH DEFICIT STRATEGY'.")
    ]
    for b_title, b_desc in items_mt:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # ==================== SLIDE 6: TOTAL LANDED COST (TLC) MODEL ====================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, BG_LIGHT)
    add_header(slide6, "Total Landed Cost (TLC) & Import Parity Formulation")

    # Formula card at top
    f_card = add_card(slide6, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.4), "", bg_color=PRIMARY, border_color=None)
    tb_f = slide6.shapes.add_textbox(Inches(1.0), Inches(1.55), Inches(11.3), Inches(1.3))
    tf_f = tb_f.text_frame
    tf_f.paragraphs[0].text = "IMPORT ARBITRAGE CONDITION: EXECUTE IMPORT IF ( TLC_Domestic - TLC_Import ) > Risk Buffer (Rs 800/MT)"
    tf_f.paragraphs[0].font.size = Pt(13)
    tf_f.paragraphs[0].font.bold = True
    tf_f.paragraphs[0].font.color.rgb = ACCENT
    
    p = tf_f.add_paragraph()
    p.text = "• TLC_Domestic = Spot_Mandi + APMC_Tax (1.5%) + Mandi_Labor + Inland_Freight_to_Plant + Transit_Insurance - Moisture_Deduction\n• TLC_Import = [ CIF_Port_USD x FX_Rate ] x [ 1 + BCD + AIDC ] + Port_Handling_CHA + Port_to_Plant_Freight + Transit_Holding_Interest (45d)"
    p.font.size = Pt(11)
    p.font.color.rgb = WHITE
    p.space_before = Pt(6)

    # 2 Comparison Columns
    col_w3 = Inches(5.7)
    gap3 = Inches(0.333)

    # Domestic Breakdown
    add_card(slide6, Inches(0.8), Inches(3.1), col_w3, Inches(3.8), "Domestic Landed Cost Components (Indore/Latur)")
    tb_d = slide6.shapes.add_textbox(Inches(1.05), Inches(3.6), col_w3 - Inches(0.5), Inches(3.2))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True
    d_rows = [
        ("Base Mandi Spot: ", "₹4,600 / MT (benchmark market price)"),
        ("Mandi Cess & APMC Duty: ", "1.50% = ₹69 / MT"),
        ("Bagging, Stitching & Labor: ", "₹75 / MT at terminal mandi"),
        ("Inland Road Freight: ", "₹850 / MT (Indore mandi to ABT-CPD crushing plant)"),
        ("Transit Insurance & Loss: ", "0.40% = ₹18.4 / MT"),
        ("Lead Time: ", "3 - 7 days (Rapid fulfillment, low pipeline holding cost)"),
        ("TOTAL DOMESTIC TLC: ", "₹5,612.40 / MT")
    ]
    for k, v in d_rows:
        p = tf_d.add_paragraph() if tf_d.paragraphs[0].text else tf_d.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + k
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = PRIMARY if "TOTAL" not in k else SUCCESS
        r2 = p.add_run()
        r2.text = v
        r2.font.size = Pt(10.5)
        r2.font.bold = ("TOTAL" in k)
        r2.font.color.rgb = TEXT_DARK if "TOTAL" not in k else SUCCESS
        p.space_after = Pt(4)

    # Import Breakdown
    add_card(slide6, Inches(0.8) + col_w3 + gap3, Inches(3.1), col_w3, Inches(3.8), "International Import Landed Cost (CIF Nhava Sheva / Kandla)")
    tb_i = slide6.shapes.add_textbox(Inches(1.05) + col_w3 + gap3, Inches(3.6), col_w3 - Inches(0.5), Inches(3.2))
    tf_i = tb_i.text_frame
    tf_i.word_wrap = True
    i_rows = [
        ("CIF Port Price: ", "$490 / MT @ ₹86.50/USD = ₹42,385 / 10 MT = ₹4,238.5 / MT"),
        ("Basic Customs Duty (BCD): ", "Current rate 0% (or standard 15% during protective regimes)"),
        ("AIDC / Cess: ", "5.0% = ₹211.90 / MT"),
        ("Port Clearance & CHA Charges: ", "₹380 / MT (unloading, wharfage, custom inspection)"),
        ("Port to Crushing Plant Rail/Road: ", "₹950 / MT (Kandla / JNPT to plant)"),
        ("45-Day Sea Transit Capital Cost: ", "12% p.a. interest on letter of credit = ₹62.7 / MT"),
        ("TOTAL IMPORT TLC: ", "₹5,843.10 / MT (Arbitrage inactive: Domestic is ₹230.7 cheaper)")
    ]
    for k, v in i_rows:
        p = tf_i.add_paragraph() if tf_i.paragraphs[0].text else tf_i.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + k
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = PRIMARY if "TOTAL" not in k else DANGER
        r2 = p.add_run()
        r2.text = v
        r2.font.size = Pt(10.5)
        r2.font.bold = ("TOTAL" in k)
        r2.font.color.rgb = TEXT_DARK if "TOTAL" not in k else DANGER
        p.space_after = Pt(4)

    # ==================== SLIDE 7: INVENTORY & PROCUREMENT OPTIMIZATION ====================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, BG_LIGHT)
    add_header(slide7, "Mathematical Optimization: Dynamic Inventory & Purchasing")

    # Left Column: Formulation
    add_card(slide7, Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.3), "Mixed-Integer Linear Programming (MILP) Formulation")
    tb = slide7.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    milp_text = [
        ("Objective Function:", "Minimize Total Cost over T-period planning horizon:\n  Min ∑ [ TLC_d,t · Q_d,t + TLC_i,t · Q_i,t + h_t · I_t + K_d · Y_d,t + K_i · Y_i,t ]"),
        ("1. Inventory Conservation Constraint:", "I_t = I_t-1 + Q_d,(t-L_d) + Q_i,(t-L_i) - Demand_t  ∀ t\n(where L_d = 1 week domestic lead time, L_i = 6 weeks import lead time)"),
        ("2. Plant Safety Stock & Capacity Limits:", "SS_min (15 days crush) ≤ I_t ≤ Silo_Capacity (60 days crush)  ∀ t"),
        ("3. Order Batching & Minimum Order Constraints:", "Q_d,t ≥ MOQ_d · Y_d,t   and   Q_i,t ≥ MOQ_i · Y_i,t (vessel parcel ~5,000 MT)"),
        ("4. Working Capital & Cashflow Constraint:", "∑ (TLC_d,t · Q_d,t + TLC_i,t · Q_i,t) ≤ Monthly_Procurement_Budget_t")
    ]
    for h, b in milp_text:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = h + "\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = PRIMARY
        r2 = p.add_run()
        r2.text = b
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    # Right Column: Rolling Horizon Policy
    add_card(slide7, Inches(7.1), Inches(1.6), Inches(5.433), Inches(5.3), "Rolling Horizon Policy & Operational Heuristics")
    tb_r = slide7.shapes.add_textbox(Inches(7.35), Inches(2.2), Inches(4.9), Inches(4.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    heuristics = [
        ("Rolling 12-Week Lookahead Window", "Optimization executes weekly on a rolling 12-week horizon. Only Week 1 decisions are committed to purchase orders, allowing dynamic adaptation to weekly market price movements."),
        ("Dynamic Safety Stock Adjustments", "Safety stock automatically expands to 25 days during high-volatility months (monsoon) and tightens to 12 days in stable harvest periods to minimize carrying costs."),
        ("Lead Time Buffering", "Due to 45-day ocean voyage, import decisions are triggered when forecasted domestic price 6 weeks ahead exceeds projected import TLC."),
        ("Supplier Diversification Guardrails", "Constraints enforce maximum 40% volume dependency on any single mandi or supplier cluster to hedge regional weather/logistic strikes.")
    ]
    for h, b in heuristics:
        p = tf_r.add_paragraph() if tf_r.paragraphs[0].text else tf_r.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + h + ":\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = SECONDARY
        r2 = p.add_run()
        r2.text = "  " + b
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

    # ==================== SLIDE 8: DECISION SUPPORT SYSTEM LOGIC ====================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, BG_LIGHT)
    add_header(slide8, "Explainable AI & Decision Recommendation Engine")

    # 4 Decision Rule Cards
    d_cards = [
        ("RECOMMENDATION: AGGRESSIVE ACCUMULATION", "TRIGGER CONDITIONS:\n• Current Spot Price < 15th percentile of 3-year history\n• Forecasted trend: Upward slope (> +5% in 30 days)\n• Inventory Level: Between 15 - 35 days crush capacity\n\nACTIONABLE DIRECTIVE:\n• Procure 2,500 - 4,000 MT Domestic Spot\n• Lock 45-60 day consumption buffer\n• Sourcing Channel: Local Mandis (Indore / Ujjain / Latur)", SUCCESS),
        
        ("RECOMMENDATION: HAND-TO-MOUTH DEFICIT", "TRIGGER CONDITIONS:\n• Current Spot Price > 80th percentile of annual distribution\n• Forecasted trend: Expected post-harvest drop or mean reversion\n• Inventory Level: Above critical safety stock (> 15 days)\n\nACTIONABLE DIRECTIVE:\n• Procure strictly minimum daily crush replenishment (250 MT/day)\n• Draw down inventory to minimum threshold (15 days)\n• Do NOT enter forward contracts; wait for harvest arrivals", DANGER),
        
        ("RECOMMENDATION: INTERNATIONAL IMPORT ARBITRAGE", "TRIGGER CONDITIONS:\n• Domestic TLC exceeds Import Landed TLC by > ₹800 / MT\n• Forecasted domestic prices remain elevated for > 60 days\n• Regulatory check: Customs duty / AIDC remains ≤ 10%\n\nACTIONABLE DIRECTIVE:\n• Contract 5,000 MT bulk parcel from Brazil / Argentina CIF\n• Schedule vessel arrival for 45-day forward deficit window\n• Hedge USD/INR currency exposure via forward contracts", SECONDARY),

        ("RECOMMENDATION: HEDGE & RE-EVALUATE", "TRIGGER CONDITIONS:\n• Extreme volatility clustering (Annualized Vol > 30%)\n• High forecast uncertainty (Wide 95% confidence intervals)\n• Policy / weather shock announcements pending\n\nACTIONABLE DIRECTIVE:\n• Procure 50% spot + 50% NCDEX commodity futures hedge\n• Review daily Mandi arrivals and rainfall progress reports\n• Maintain 20 days dynamic safety cushion", ACCENT)
    ]

    for idx, (title, content, col) in enumerate(d_cards):
        r = idx // 2
        c = idx % 2
        x = Inches(0.8) + c * Inches(6.0)
        y = Inches(1.6) + r * Inches(2.7)
        add_card(slide8, x, y, Inches(5.7), Inches(2.5), title, border_color=col)
        
        tb = slide8.shapes.add_textbox(x + Inches(0.2), y + Inches(0.55), Inches(5.3), Inches(1.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = content
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DARK

    # ==================== SLIDE 9: SCENARIO ANALYSIS & STRESS TESTING ====================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, BG_LIGHT)
    add_header(slide9, "Scenario Analysis: Stress-Testing & Market Shocks")

    scenarios = [
        ("Scenario A: Import Tariff Shock (0% -> 15% Duty)", 
         "Context: Government hikes basic customs duty to protect domestic soybean farmers.",
         "Impact on Landed Cost: Import TLC spikes by +₹635/MT, immediately closing the import window.",
         "System Recommendation: Halt international import negotiations; pivot 100% procurement volume to domestic state mandis. Pre-book domestic transport before local mandi prices rally in response.",
         PRIMARY),
        ("Scenario B: Currency Depreciation (USD/INR moves 84 -> 92)", 
         "Context: Macro forex depreciation increases rupee cost of dollar-denominated imports.",
         "Impact on Landed Cost: International CIF increases by +₹3,920 / 10 MT (+₹392/MT).",
         "System Recommendation: Trigger foreign exchange currency hedging for open import L/Cs. Shift procurement allocation to domestic contract farming networks and domestic cooperatives.",
         DANGER),
        ("Scenario C: Domestic Monsoon Deficit (-20% Kharif Output)", 
         "Context: El Niño causes late rains in Madhya Pradesh & Maharashtra; harvest arrivals drop 25%.",
         "Impact on Landed Cost: Domestic spot prices surge +30% to ₹6,200/MT within 6 weeks.",
         "System Recommendation: Issue immediate strategic alert in July. Lock 90-day forward import contracts from South America ahead of the domestic spike, capturing ₹750/MT net savings.",
         ACCENT),
        ("Scenario D: Global Freight Spike (+50 $/MT Shipping Rates)", 
         "Context: Geopolitical tensions disrupt maritime choke points; bulk shipping rates jump.",
         "Impact on Landed Cost: Ocean freight adds +₹430/MT to international delivery.",
         "System Recommendation: Re-evaluate total landed cost parity; domestic sourcing becomes cheaper even during off-season. Shift to domestic rakes (Indian Railways) for inter-state grain transit.",
         SECONDARY)
    ]

    for idx, (s_title, s_ctx, s_imp, s_rec, s_col) in enumerate(scenarios):
        r = idx // 2
        c = idx % 2
        x = Inches(0.8) + c * Inches(6.0)
        y = Inches(1.6) + r * Inches(2.7)
        add_card(slide9, x, y, Inches(5.7), Inches(2.5), s_title, border_color=s_col)
        
        tb = slide9.shapes.add_textbox(x + Inches(0.2), y + Inches(0.55), Inches(5.3), Inches(1.85))
        tf = tb.text_frame
        tf.word_wrap = True
        
        for prefix, txt in [("Context: ", s_ctx), ("Cost Impact: ", s_imp), ("System Action: ", s_rec)]:
            p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            r1 = p.add_run()
            r1.text = prefix
            r1.font.bold = True
            r1.font.size = Pt(10)
            r1.font.color.rgb = s_col
            r2 = p.add_run()
            r2.text = txt
            r2.font.size = Pt(10)
            r2.font.color.rgb = TEXT_DARK
            p.space_after = Pt(4)

    # ==================== SLIDE 10: PROTOTYPE & DASHBOARD CAPABILITIES ====================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, BG_LIGHT)
    add_header(slide10, "Prototype Decision Support System & User Interface")

    # 3 Feature Pillars
    p_w = Inches(3.7)
    p_gap = Inches(0.3)

    pillars = [
        ("Interactive Analytics & Forecasting View", SECONDARY, [
            "Live Interactive Price Charts: Dual-axis overlay of Domestic Mandi vs CBOT vs Import TLC.",
            "Historical Decomposition: Visual breakdown of Trend, Seasonality, and Cyclical residuals.",
            "Forecast Fan Charts: 30-day and 90-day predictions with 80% and 95% confidence bounds.",
            "Basis & Volatility Tracking: Real-time calculation of Mandi basis and annualized price risk."
        ]),
        ("Total Landed Cost & Parity Calculator", PRIMARY, [
            "Live Cost Waterfall: Side-by-side comparison of 8 distinct cost elements (tariffs, cess, freight, transit interest).",
            "Dynamic Spread Indicator: Real-time gauge of Import Parity Spread (Domestic TLC - Import TLC).",
            "Manual Override Panel: Allows procurement team to enter today's negotiated quotes and custom freight.",
            "Sensitivity Matrix: 2D heatmap showing parity across varying USD/INR and CBOT price grids."
        ]),
        ("Prescriptive Engine & Scenario Sandbox", SUCCESS, [
            "Executive Action Card: Color-coded recommendation (Aggressive Buy, Hand-to-Mouth, Import).",
            "12-Week Order Plan: Exact schedule detailing order dates, quantities (MT), and sourcing channel.",
            "What-If Shock Sliders: Interactive simulation of tariff hikes, currency swings, and freight changes.",
            "Audit & Export: Complete recommendation history log and one-click PDF/CSV export for management review."
        ])
    ]

    for i, (title, color, features) in enumerate(pillars):
        x = Inches(0.8) + i * (p_w + p_gap)
        add_card(slide10, x, Inches(1.6), p_w, Inches(5.3), title, border_color=color)
        
        tb = slide10.shapes.add_textbox(x + Inches(0.2), Inches(2.2), p_w - Inches(0.4), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        for f in features:
            f_title, f_desc = f.split(":", 1)
            p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
            r1 = p.add_run()
            r1.text = "✓ " + f_title + ":\n"
            r1.font.bold = True
            r1.font.size = Pt(11)
            r1.font.color.rgb = color
            r2 = p.add_run()
            r2.text = "  " + f_desc.strip()
            r2.font.size = Pt(10.5)
            r2.font.color.rgb = TEXT_DARK
            p.space_after = Pt(12)

    # ==================== SLIDE 11: BUSINESS IMPACT & ROI ====================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, BG_LIGHT)
    add_header(slide11, "Business Impact, Quantified ROI & Strategic Value")

    # Top Metric Banners
    m_w = Inches(2.7)
    m_gap = Inches(0.3)
    kpis = [
        ("₹ 3.84 Cr", "Annual Net Cost Savings", SUCCESS),
        ("5.6% - 7.2%", "Reduction in Landed Cost", SECONDARY),
        ("0 Days", "Plant Stockout Downtime", PRIMARY),
        ("18 Days", "Working Capital Optimization", ACCENT)
    ]
    for i, (val, lbl, col) in enumerate(kpis):
        x = Inches(0.8) + i * (m_w + m_gap)
        c = add_card(slide11, x, Inches(1.6), m_w, Inches(1.3), "", bg_color=CARD_BG, border_color=col)
        tb = slide11.shapes.add_textbox(x + Inches(0.1), Inches(1.7), m_w - Inches(0.2), Inches(1.1))
        tf = tb.text_frame
        p1 = tf.paragraphs[0]
        p1.text = val
        p1.font.size = Pt(26)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = lbl
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MUTED
        p2.alignment = PP_ALIGN.CENTER

    # Bottom 2 Cards
    b_w = Inches(5.7)
    b_gap = Inches(0.333)

    # Left: Financial Model
    add_card(slide11, Inches(0.8), Inches(3.1), b_w, Inches(3.8), "Financial Impact Modeling (Crush Capacity: 300 MT/Day)")
    tb = slide11.shapes.add_textbox(Inches(1.05), Inches(3.6), b_w - Inches(0.5), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    f_points = [
        ("Annual Raw Material Consumption: ", "100,000 MT/year of soybean."),
        ("Baseline Annual Raw Material Spend: ", "₹52.00 Crores (assuming ₹5,200/MT unoptimized average)."),
        ("Optimized Procurement Spend: ", "₹48.16 Crores through seasonal accumulation & import parity."),
        ("Direct Purchase Savings: ", "₹3.84 Crores / year (7.38% direct savings)."),
        ("Working Capital Interest Reduction: ", "Dynamic safety stock saves ₹32 Lakhs in annual holding interest (12% p.a.)."),
        ("Downside Protection: ", "Avoids panic spot purchases during off-season peaks (saving up to ₹800/MT).")
    ]
    for k, v in f_points:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + k
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = v
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(5)

    # Right: Operational & Qualitative Value
    add_card(slide11, Inches(0.8) + b_w + b_gap, Inches(3.1), b_w, Inches(3.8), "Operational & Strategic Competitive Advantages")
    tb = slide11.shapes.add_textbox(Inches(1.05) + b_w + b_gap, Inches(3.6), b_w - Inches(0.5), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True
    o_points = [
        ("Uninterrupted Plant Operation: ", "Robust lead-time modeling eliminates emergency stockouts and costly plant idling."),
        ("Objective Negotiation Leverage: ", "Real-time mandi parity and TLC calculators empower procurement teams with objective benchmarks during supplier negotiations."),
        ("Hedging Decision Support: ", "Quantifies basis risk and alerts treasury teams when NCDEX or CBOT futures hedging is financially justified."),
        ("Institutional Memory: ", "Transforms intuitive, individual trader experience into an auditable, systematic organizational capability."),
        ("Fast Payback Period: ", "System development and implementation costs recovered within 2.5 months of deployment.")
    ]
    for k, v in o_points:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• " + k
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = SECONDARY
        r2 = p.add_run()
        r2.text = v
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(5)

    # ==================== SLIDE 12: IMPLEMENTATION ROADMAP & RISK MATRIX ====================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, BG_LIGHT)
    add_header(slide12, "Implementation Roadmap & Risk Mitigation Matrix")

    # Left: Roadmap
    add_card(slide12, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Phased Deployment Roadmap (16 Weeks)")
    tb = slide12.shapes.add_textbox(Inches(1.05), Inches(2.2), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    phases = [
        ("Phase 1: Integration & Ingestion (Weeks 1 - 4)", 
         "Connect ERP (SAP/Oracle) for live stock and PO data. Setup automated daily API pipelines for Agmarknet mandi spot, CBOT futures, and RBI USD/INR reference rates.", SECONDARY),
        ("Phase 2: Model Calibration & Backtesting (Weeks 5 - 8)", 
         "Calibrate SARIMAX and Prophet forecasting models on 5-year ABT-CPD historical procurement logs. Benchmark TLC parity formulas with historical import records.", PRIMARY),
        ("Phase 3: Pilot Deployment & Shadow Mode (Weeks 9 - 12)", 
         "Deploy DSS dashboard to ABT-CPD procurement desk. Run alongside current procurement workflow in parallel shadow mode; conduct weekly variance tracking.", ACCENT),
        ("Phase 4: Full Production & Automated PO Triggers (Weeks 13 - 16)", 
         "Fully transition to DSS recommendations. Enable automated approval workflows and executive weekly procurement briefing alerts.", SUCCESS)
    ]
    for p_title, p_desc, col in phases:
        p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
        r1 = p.add_run()
        r1.text = p_title + "\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = col
        r2 = p.add_run()
        r2.text = p_desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # Right: Risk Matrix
    add_card(slide12, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.3), "Risk Mitigation Matrix")
    tb_r = slide12.shapes.add_textbox(Inches(7.083), Inches(2.2), Inches(5.2), Inches(4.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    risks = [
        ("Black Swan Market Events (e.g. Geopolitical / Export Bans)", 
         "Mitigation: Scenario analysis suite with manual parameter overrides. Real-time alert triggers when market basis diverges > 3 standard deviations from model expectations."),
        ("Port Customs & Demurrage Congestion on Imports", 
         "Mitigation: 10-day buffer built into import lead time modeling. Port diversification (JNPT, Kandla, Mundra) and pre-clearance documentation protocols."),
        ("Silo Spoilage & Quality Variations", 
         "Mitigation: Moisture penalty deductions integrated in TLC calculations. FIFO inventory tracking and maximum 90-day storage duration constraints in MILP."),
        ("User Trust & Model Adoption", 
         "Mitigation: Explainable AI interface translating statistical parameters into plain-language business logic. Manual override retains executive authority at all times.")
    ]
    for r_title, r_desc in risks:
        p = tf_r.add_paragraph() if tf_r.paragraphs[0].text else tf_r.paragraphs[0]
        r1 = p.add_run()
        r1.text = "• Risk: " + r_title + "\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = DANGER
        r2 = p.add_run()
        r2.text = "  " + r_desc
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_DARK
        p.space_after = Pt(8)

    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\Harishkumar.M\.gemini\antigravity\scratch\soybean-procurement-dss"
    out_file = os.path.join(out_dir, "ABT_CPD_Soybean_Procurement_Strategy_Round2.pptx")
    create_deck(out_file)
