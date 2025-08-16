import streamlit as st
import json
import onboarding_pipeline

def main():
    st.set_page_config(page_title="KYC Onboarding Dashboard", layout="wide")
    st.markdown("""
        <style>
        .main-header {background:#003366; color:white; padding:1em 2em; border-radius:10px; margin-bottom:1em;}
        .card {background:#f8f9fa; padding:1em; border-radius:10px; box-shadow:0 2px 8px #eee; margin-bottom:1em;}
        .risk-badge {font-size:1.2em; font-weight:bold; padding:0.3em 1em; border-radius:20px; display:inline-block;}
        .footer {text-align:center; color:#888; margin-top:2em;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-header'><h1 style='margin-bottom:0;'>KYC Onboarding Dashboard</h1><span style='font-size:1.1em;'>Professional Due Diligence Demo</span></div>", unsafe_allow_html=True)


    st.sidebar.title("Company Search")
    company_input = st.sidebar.text_input("Enter Company Name", "CompanyA")
    unique_id = st.sidebar.text_input("Enter Unique Identifier (CIN/GSTIN)", "U12345MH2025PTC000001")
    st.sidebar.markdown("---")
    st.sidebar.write("Type a company name and unique ID to simulate real-world lookup.")

    st.markdown(f"<h2 style='color:#003366;'>{company_input} Pvt Ltd</h2>", unsafe_allow_html=True)

    if st.button("Generate Report", use_container_width=True):
        # Simulate lookup: check if folder exists
        import os
        data_path = f"{onboarding_pipeline.DATA_DIR}/{company_input}"
        if not os.path.exists(data_path):
            st.error(f"Company '{company_input}' not found in records.")
        else:
            json_report, summary = onboarding_pipeline.generate_report(company_input)
            directors = onboarding_pipeline.load_directors(f"{onboarding_pipeline.DATA_DIR}/{company_input}/directors.csv")

            # Layout: 3 columns for summary, risk, directors
            col1, col2, col3 = st.columns([2,1,2])

            with col1:
                st.markdown("<div class='card'><b>Summary & Recommendation</b><br>" + summary.replace("\n","<br>") + "</div>", unsafe_allow_html=True)

            with col2:
                risk_color = {"Low": "#27ae60", "Medium": "#f1c40f", "High": "#e74c3c"}
                risk_icon = {"Low": "✅", "Medium": "⚠️", "High": "❌"}
                st.markdown(f"<div class='card'><span class='risk-badge' style='background:{risk_color.get(json_report['risk_level'],'#eee')}; color:#fff;'>{risk_icon.get(json_report['risk_level'],'ℹ️')} {json_report['risk_level']}</span></div>", unsafe_allow_html=True)
                if json_report["flags"]:
                    for flag in json_report["flags"]:
                        st.markdown(f"<div class='card' style='background:#fffbe6;'><b>⚠️ {flag}</b></div>", unsafe_allow_html=True)

            with col3:
                st.markdown("<div class='card'><b>Directors</b></div>", unsafe_allow_html=True)
                st.table([{"Name": d} for d in directors])

            # Financials and Legal Cases in two columns
            col4, col5 = st.columns(2)
            with col4:
                st.markdown("<div class='card'><b>Financial Health</b></div>", unsafe_allow_html=True)
                st.table(json_report["financial_health"])
            with col5:
                st.markdown("<div class='card'><b>Pending Legal Cases</b></div>", unsafe_allow_html=True)
                if json_report["legal_cases"]:
                    st.table(json_report["legal_cases"])
                else:
                    st.write("No pending cases.")

            # Toggle for JSON
            with st.expander("Show Raw JSON Report"):
                st.json(json_report)

    st.markdown("<div class='footer'>© 2025 NeuronWorks | Demo Dashboard</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
