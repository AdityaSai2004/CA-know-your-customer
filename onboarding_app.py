import streamlit as st
import json
import onboarding_pipeline
import pandas as pd
from datetime import datetime
import re

def main():
    st.set_page_config(
        page_title="KYC Onboarding Dashboard", 
        layout="wide",
        page_icon="🏢",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced CSS styling
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #003366, #004d99);
            color: white;
            padding: 1.5em 2em;
            border-radius: 15px;
            margin-bottom: 1.5em;
            box-shadow: 0 4px 20px rgba(0,51,102,0.3);
        }
        .card {
            background: #ffffff;
            padding: 1.5em;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 1.5em;
            border-left: 4px solid #003366;
        }
        .risk-badge {
            font-size: 1.2em;
            font-weight: bold;
            padding: 0.5em 1.2em;
            border-radius: 25px;
            display: inline-block;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .metric-card {
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            padding: 1em;
            border-radius: 10px;
            text-align: center;
            margin: 0.5em 0;
        }
        .footer {
            text-align: center;
            color: #6c757d;
            margin-top: 3em;
            padding: 1em;
            border-top: 1px solid #dee2e6;
        }
        .search-hint {
            background: #e7f3ff;
            padding: 0.8em;
            border-radius: 8px;
            border-left: 4px solid #007bff;
            margin: 1em 0;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .success { background-color: #28a745; }
        .warning { background-color: #ffc107; }
        .danger { background-color: #dc3545; }
        </style>
    """, unsafe_allow_html=True)

    # Header with enhanced design
    st.markdown("""
        <div class='main-header'>
            <h1 style='margin-bottom:0; font-size: 2.2em;'>🏢 KYC Onboarding Dashboard</h1>
            <p style='margin-bottom:0; font-size:1.1em; opacity:0.9;'>Professional Due Diligence & Risk Assessment Platform</p>
        </div>
    """, unsafe_allow_html=True)

    # Enhanced sidebar with better organization
    with st.sidebar:
        st.markdown("### 🔍 Company Search")
        
        # Company mapping with more realistic data
        company_map = {
            "TriveniAgro": {
                "cin": "U01122MH2012PTC123456",
                "full_name": "Triveni Agro Products Pvt Ltd",
                "industry": "Agriculture"
            },
            "UrbanEdgeTech": {
                "cin": "AAB-1234",
                "full_name": "UrbanEdge Technologies LLP",
                "industry": "Technology"
            },
            "ShreeFinance": {
                "cin": "L65910DL2010PLC234567",
                "full_name": "Shree Finance & Leasing Ltd",
                "industry": "Financial Services"
            },
            "GreenLeafFoods": {
                "cin": "U15122TN2018PTC345678",
                "full_name": "GreenLeaf Foods Pvt Ltd",
                "industry": "Food Processing"
            },
            "ZenithInfra": {
                "cin": "U45201MH2012PLC456789",
                "full_name": "Zenith Infrastructure Projects Ltd",
                "industry": "Infrastructure"
            }
        }
        
        # Search options
        search_type = st.radio("Search by:", ["Company Name", "CIN", "Browse All"], horizontal=True)
        
        if search_type == "Company Name":
            company_input = st.text_input("Enter Company Name", placeholder="e.g., TriveniAgro, UrbanEdgeTech")
            cin_input = company_map.get(company_input, {}).get("cin", "") if company_input else ""
            
        elif search_type == "CIN":
            cin_input = st.text_input("Enter CIN", placeholder="e.g., U01122MH2012PTC123456")
            company_input = ""
            # Auto-detect company from CIN
            for name, data in company_map.items():
                if data["cin"] == cin_input:
                    company_input = name
                    break
                    
        else:  # Browse All
            st.markdown("#### Available Companies:")
            for name, data in company_map.items():
                if st.button(f"📊 {data['full_name']}", key=f"btn_{name}", use_container_width=True):
                    st.session_state.selected_company = name
            company_input = st.session_state.get('selected_company', '')
            cin_input = company_map.get(company_input, {}).get("cin", "")
        
        # Validation and hints
        if company_input and company_input in company_map:
            company_data = company_map[company_input]
            st.markdown(f"""
                <div class='search-hint'>
                    <strong>✓ Company Found</strong><br>
                    <strong>Full Name:</strong> {company_data['full_name']}<br>
                    <strong>CIN:</strong> {company_data['cin']}<br>
                    <strong>Industry:</strong> {company_data['industry']}
                </div>
            """, unsafe_allow_html=True)
        elif cin_input:
            # Validate CIN format
            cin_pattern = r'^[A-Z]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$'
            is_valid_cin = re.match(cin_pattern, cin_input) or cin_input == 'AAB-1234'
            validation_text = '✓ Valid format' if is_valid_cin else '⚠️ Check CIN format'
            
            st.markdown(f"""
                <div class='search-hint'>
                    <strong>CIN Entered:</strong> {cin_input}<br>
                    {validation_text}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📋 Quick Actions")
        export_format = st.selectbox("Export Format", ["PDF", "Excel", "JSON"])
        
        # Company statistics
        st.markdown("### 📊 Database Stats")
        st.metric("Companies", len(company_map))
        st.metric("Last Updated", datetime.now().strftime("%Y-%m-%d"))
    
    # Reverse mapping CIN to folder
    cin_to_folder = {data["cin"]: name for name, data in company_map.items()}

    # Display company name if found
    display_name = company_input
    full_company_name = "Unknown Company"
    if cin_input in cin_to_folder:
        display_name = cin_to_folder[cin_input]
        full_company_name = company_map[display_name]["full_name"]
    elif company_input in company_map:
        full_company_name = company_map[company_input]["full_name"]

    # Enhanced company header
    if display_name:
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.markdown(f"<h2 style='color:#003366; margin-bottom:0;'>{full_company_name}</h2>", unsafe_allow_html=True)
            if display_name in company_map:
                st.markdown(f"**Industry:** {company_map[display_name]['industry']} | **CIN:** {company_map[display_name]['cin']}")
        with col_header2:
            generate_report = st.button("🔍 Generate Report", type="primary", use_container_width=True)
    else:
        st.markdown("<h2 style='color:#6c757d;'>Select a company to begin analysis</h2>", unsafe_allow_html=True)
        generate_report = False

    if generate_report:
        import os
        folder = None
        # Priority: CIN search, then name
        if cin_input in cin_to_folder:
            folder = cin_to_folder[cin_input]
        elif company_input in company_map:
            folder = company_input
        if folder:
            data_path = f"{onboarding_pipeline.DATA_DIR}/{folder}"
            if not os.path.exists(data_path):
                st.error(f"❌ Company '{display_name}' not found in records.")
            else:
                with st.spinner("🔄 Analyzing company data..."):
                    try:
                        json_report, summary = onboarding_pipeline.generate_report(folder)
                        directors = onboarding_pipeline.load_directors(f"{onboarding_pipeline.DATA_DIR}/{folder}/directors.csv")

                        # --- Director Watchlist ---
                        watchlist = ["Meena Rathi", "Ritika Shah"]
                        flagged_directors = [d for d in directors if d in watchlist]

                        # --- Compliance Score Calculation ---
                        assets = json_report["financial_health"].get("assets", "0").replace('₹','').replace('Cr','').replace(',','')
                        liabilities = json_report["financial_health"].get("liabilities", "0").replace('₹','').replace('Cr','').replace(',','')
                        try:
                            assets_val = float(assets)
                            liab_val = float(liabilities)
                            debt_ratio = liab_val / assets_val if assets_val > 0 else 0
                        except:
                            debt_ratio = 0
                        pending_cases = len([case for case in json_report.get("legal_cases", []) if case.get("status", "").lower() == "pending"])
                        score = 100
                        score -= int(debt_ratio * 50)
                        score -= pending_cases * 10
                        score -= len(flagged_directors) * 20
                        score = max(0, min(100, score))
                        score_color = "#28a745" if score >= 70 else ("#ffc107" if score > 40 else "#dc3545")
                        # Set risk level from score
                        if score >= 70:
                            ui_risk_level = "Low"
                        elif score > 40:
                            ui_risk_level = "Medium"
                        else:
                            ui_risk_level = "High"

                        # --- Risk Trend Visualization (Mock Data) ---
                        years = [2021, 2022, 2023, 2024]
                        debt_trend = [debt_ratio * (0.8 + 0.05*i) for i in range(len(years))]
                        case_trend = [max(0, pending_cases - i) for i in range(len(years))]

                        st.success("✅ Analysis completed successfully!")
                        metrics_col1, metrics_col2, metrics_col3, metrics_col4, metrics_col5 = st.columns(5)
                        with metrics_col1:
                            risk_color_bg = {"Low": "#d4edda", "Medium": "#fff3cd", "High": "#f8d7da"}
                            risk_icon = {"Low": "✅", "Medium": "⚠️", "High": "❌"}
                            st.markdown(f"""
                                <div class='metric-card' style='background:{risk_color_bg.get(ui_risk_level, '#f8f9fa')};'>
                                    <h3 style='margin:0; color:#003366;'>{risk_icon.get(ui_risk_level, 'ℹ️')} {ui_risk_level}</h3>
                                    <p style='margin:0; font-size:0.9em;'>Risk Level</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with metrics_col2:
                            st.markdown(f"""
                                <div class='metric-card'>
                                    <h3 style='margin:0; color:#003366;'>{len(directors)}</h3>
                                    <p style='margin:0; font-size:0.9em;'>Active Directors</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with metrics_col3:
                            st.markdown(f"""
                                <div class='metric-card'>
                                    <h3 style='margin:0; color:#003366;'>{pending_cases}</h3>
                                    <p style='margin:0; font-size:0.9em;'>Pending Cases</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with metrics_col4:
                            flag_count = len(json_report.get("flags", []))
                            st.markdown(f"""
                                <div class='metric-card'>
                                    <h3 style='margin:0; color:#003366;'>{flag_count}</h3>
                                    <p style='margin:0; font-size:0.9em;'>Alert Flags</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with metrics_col5:
                            st.markdown(f"""
                                <div class='metric-card' style='background:{score_color}; color:white;'>
                                    <h3 style='margin:0;'>{score}</h3>
                                    <p style='margin:0; font-size:0.9em;'>Compliance Score</p>
                                </div>
                            """, unsafe_allow_html=True)

                        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Summary", "👥 Directors", "💰 Financials", "⚖️ Legal Cases", "📊 Raw Data"])
                        with tab1:
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                # Replace risk level in summary with UI risk level
                                summary_ui = re.sub(r"Risk Level: [A-Za-z]+", f"Risk Level: {ui_risk_level}", summary)
                                st.markdown(f"""
                                    <div class='card'>
                                        <h4>📋 Executive Summary</h4>
                                        {summary_ui.replace(chr(10), '<br>')}
                                        <br><br><b>Compliance Score:</b> <span style='color:{score_color}; font-weight:bold;'>{score}/100</span>
                                    </div>
                                """, unsafe_allow_html=True)
                            with col2:
                                if flagged_directors:
                                    st.markdown("<div class='card'><h4>🚨 Watchlist Directors</h4>", unsafe_allow_html=True)
                                    for d in flagged_directors:
                                        st.markdown(f"<div style='margin: 0.5em 0; padding: 0.5em; background: #f8d7da; border-radius: 5px;'><span class='status-indicator danger'></span>{d} <b>(Watchlist)</b></div>", unsafe_allow_html=True)
                                    st.markdown("</div>", unsafe_allow_html=True)
                                if json_report["flags"]:
                                    st.markdown("<div class='card'><h4>🚨 Alert Flags</h4>", unsafe_allow_html=True)
                                    for i, flag in enumerate(json_report["flags"]):
                                        status_class = "danger" if "fraud" in flag.lower() or "high" in flag.lower() else "warning"
                                        st.markdown(f"<div style='margin: 0.5em 0; padding: 0.5em; background: #fff3cd; border-radius: 5px;'><span class='status-indicator {status_class}'></span>{flag}</div>", unsafe_allow_html=True)
                                    st.markdown("</div>", unsafe_allow_html=True)
                        with tab2:
                            st.markdown("<div class='card'><h4>👥 Board of Directors</h4>", unsafe_allow_html=True)
                            directors_df = pd.read_csv(f"{onboarding_pipeline.DATA_DIR}/{folder}/directors.csv")
                            if not directors_df.empty:
                                directors_df['Status'] = directors_df['name'].apply(lambda x: '🔴 Watchlist' if x in watchlist else '🟢 Active')
                                st.dataframe(directors_df, use_container_width=True, hide_index=True)
                            else:
                                st.info("No director information available.")
                            st.markdown("</div>", unsafe_allow_html=True)
                        with tab3:
                            st.markdown("<div class='card'><h4>💰 Financial Health</h4>", unsafe_allow_html=True)
                            fin_col1, fin_col2, fin_col3 = st.columns(3)
                            financials = json_report["financial_health"]
                            assets = financials.get("assets", "N/A")
                            liabilities = financials.get("liabilities", "N/A")
                            net_worth = financials.get("net_worth", "N/A")
                            with fin_col1:
                                st.metric("Total Assets", assets)
                            with fin_col2:
                                st.metric("Total Liabilities", liabilities)
                            with fin_col3:
                                st.metric("Net Worth", net_worth)
                            try:
                                st.markdown(f"<div style='background: {'#f8d7da' if debt_ratio > 0.7 else '#d4edda'}; padding: 1em; border-radius: 8px; margin: 1em 0;'><strong>Debt-to-Asset Ratio: {debt_ratio:.2%}</strong><br><small>{'⚠️ Above recommended threshold' if debt_ratio > 0.7 else '✅ Within healthy range'}</small></div>", unsafe_allow_html=True)
                                st.line_chart(pd.DataFrame({"Debt Ratio": debt_trend}, index=years))
                            except:
                                pass
                            st.markdown("</div>", unsafe_allow_html=True)
                        with tab4:
                            st.markdown("<div class='card'><h4>⚖️ Legal Cases & Litigation</h4>", unsafe_allow_html=True)
                            if json_report["legal_cases"]:
                                for case in json_report["legal_cases"]:
                                    status_color = "#fff3cd" if case.get("status", "").lower() == "pending" else "#d4edda"
                                    st.markdown(f"<div style='background: {status_color}; padding: 1em; border-radius: 8px; margin: 0.5em 0; border-left: 4px solid #003366;'><strong>🏛️ {case.get('court', 'N/A')}</strong><br><strong>Case ID:</strong> {case.get('case_id', 'N/A')}<br><strong>Status:</strong> {case.get('status', 'N/A')}<br></div>", unsafe_allow_html=True)
                                st.line_chart(pd.DataFrame({"Pending Cases": case_trend}, index=years))
                            else:
                                st.info("✅ No pending legal cases found.")
                            st.markdown("</div>", unsafe_allow_html=True)
                        with tab5:
                            st.markdown("<div class='card'><h4>📊 Raw JSON Data</h4>", unsafe_allow_html=True)
                            st.json(json_report)
                            st.markdown("#### Export Options")
                            if st.button("📥 Download JSON Report"):
                                st.download_button(label="Download as JSON", data=json.dumps(json_report, indent=2), file_name=f"{folder}_kyc_report.json", mime="application/json")
                            st.markdown("</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ Error generating report: {str(e)}")
                        st.exception(e)
        else:
            st.error("❌ No matching company found for the given name or CIN.")

    # Enhanced footer with additional information
    current_date = datetime.now().strftime("%B %d, %Y")
    st.markdown(f"""
        <div class='footer'>
            <hr style='margin: 2em 0; border: none; height: 1px; background: #dee2e6;'>
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
                <div>
                    <strong>© 2025 NeuronWorks</strong> | KYC Onboarding Demo<br>
                    <small>Powered by AI-driven risk assessment</small>
                </div>
                <div style='text-align: right;'>
                    <small>
                        📊 Data Sources: MCA, NCLT, High Courts<br>
                        🔄 Last Updated: {current_date}
                    </small>
                </div>
            </div>
            <div style='text-align: center; margin-top: 1em; font-size: 0.8em; color: #6c757d;'>
                ⚠️ Demo purposes only. Real implementation requires proper API integration and compliance.
            </div>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
