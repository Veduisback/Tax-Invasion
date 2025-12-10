import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import json

from sample_data import (
    BUSINESS_TYPES, LAND_RATES_BY_REGION, INDIAN_STATES, TYCOON_CONNECTION_LEVELS,
    FRAUD_TYPES, MAJOR_INDIAN_FRAUD_CASES, SMALL_VENDOR_TYPES, LIFESTYLE_INDICATORS,
    SMALL_VENDOR_FRAUD_PATTERNS
)
from fraud_detection import fraud_engine
from ai_analysis import generate_ai_fraud_analysis, get_investigation_checklist, generate_small_vendor_ai_analysis
from database import (
    init_db, save_analysis_result, get_all_analysis_records, get_analysis_by_id,
    get_risk_distribution, get_business_type_fraud_stats, get_state_wise_stats,
    save_vendor_analysis, get_vendor_analyses, save_field_investigation
)
from pdf_generator import generate_fraud_report_pdf, generate_vendor_report_pdf
from visual_intelligence import analyze_vendor_stall_photo, compare_declared_vs_visual, analyze_lifestyle_photos
from behavioral_analysis import analyze_income_lifestyle_gap, analyze_transaction_patterns
from network_analysis import FraudNetworkAnalyzer, build_vendor_network

st.set_page_config(
    page_title="Tax Fraud Detection System - Income Tax Department",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A5F;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #667eea;
        margin-bottom: 2rem;
    }
    .risk-critical { background-color: #721c24; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-weight: bold; }
    .risk-very-high { background-color: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-weight: bold; }
    .risk-high { background-color: #fd7e14; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-weight: bold; }
    .risk-moderate { background-color: #ffc107; color: black; padding: 0.5rem 1rem; border-radius: 5px; font-weight: bold; }
    .risk-low { background-color: #28a745; color: white; padding: 0.5rem 1rem; border-radius: 5px; font-weight: bold; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .fraud-pattern-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 5px 5px 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .vendor-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

st.sidebar.markdown("## Income Tax Department")
st.sidebar.markdown("### Fraud Detection System")

page = st.sidebar.radio(
    "Navigation",
    ["Business Analysis", "Small Vendor Analysis", "Field Officer Mode", 
     "Analysis History", "Dashboard", "Fraud Patterns", "About"]
)

if page == "Business Analysis":
    st.markdown('<h1 class="main-header">Tax Fraud Detection System</h1>', unsafe_allow_html=True)
    st.markdown("### Analyze Business for Potential Tax Fraud")
    
    with st.form("business_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Business Details")
            business_name = st.text_input("Business Name (Optional)", placeholder="Enter business name")
            business_type = st.selectbox("Business Type", BUSINESS_TYPES)
            num_outlets = st.number_input("Number of Outlets/Offices", min_value=1, max_value=1000, value=1)
            total_land_sqft = st.number_input("Total Land Area (sq ft)", min_value=0.0, value=1000.0, step=100.0)
            region = st.selectbox("Region", list(LAND_RATES_BY_REGION.keys()))
            state = st.selectbox("State", INDIAN_STATES)
            land_rate = st.number_input("Land Rate (Rs./sq ft)", min_value=0.0, value=5000.0, step=100.0)
        
        with col2:
            st.subheader("Financial Details")
            electricity_kwh = st.number_input("Monthly Electricity (kWh)", min_value=0.0, value=500.0, step=50.0)
            declared_revenue = st.number_input("Declared Annual Revenue (Rs.)", min_value=0.0, value=1000000.0, step=50000.0)
            declared_tax = st.number_input("Declared Tax Paid (Rs.)", min_value=0.0, value=150000.0, step=10000.0)
            num_employees = st.number_input("Number of Employees", min_value=0, max_value=10000, value=5)
            is_stock_listed = st.checkbox("Stock Market Listed")
            stock_cap = st.number_input("Market Cap (Rs.) if listed", min_value=0.0, value=0.0, step=1000000.0)
            tycoon_connection = st.selectbox("Connection with Business Tycoons", TYCOON_CONNECTION_LEVELS)
            years_operation = st.number_input("Years in Operation", min_value=0, max_value=100, value=5)
        
        additional_notes = st.text_area("Additional Notes", placeholder="Any additional information...")
        
        submitted = st.form_submit_button("Analyze for Fraud Risk", use_container_width=True)
    
    if submitted:
        business_data = {
            "business_type": business_type,
            "num_outlets": num_outlets,
            "total_land_sqft": total_land_sqft,
            "region": region,
            "state": state,
            "land_rate_per_sqft": land_rate,
            "electricity_consumption_kwh": electricity_kwh * 12,
            "declared_revenue": declared_revenue,
            "declared_tax_paid": declared_tax,
            "num_employees": num_employees,
            "is_stock_listed": is_stock_listed,
            "stock_market_cap": stock_cap,
            "tycoon_connection_level": tycoon_connection,
            "years_in_operation": years_operation,
            "additional_notes": additional_notes
        }
        
        with st.spinner("Analyzing business data with AI-powered fraud detection..."):
            result = fraud_engine.analyze_business(business_data)
            record_id = save_analysis_result(business_data, result, business_name)
        
        st.success(f"Analysis Complete! Record ID: {record_id}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Fraud Probability", f"{result['fraud_probability']:.1f}%")
        with col2:
            risk_class = f"risk-{result['risk_level'].lower().replace(' ', '-')}"
            st.markdown(f'<div class="{risk_class}">{result["risk_level"]}</div>', unsafe_allow_html=True)
        with col3:
            st.metric("ML Ensemble Score", f"{result['ml_score']:.1f}%")
        
        st.markdown("---")
        st.subheader("Recommendation")
        st.info(result['recommendation'])
        
        if result.get('matched_fraud_patterns'):
            st.subheader("Matched Fraud Patterns")
            for pattern in result['matched_fraud_patterns']:
                st.markdown(f"""
                <div class="fraud-pattern-card">
                    <strong>{pattern['type']}</strong> (Confidence: {pattern['score']}%)
                    <ul>
                    {''.join([f"<li>{ind}</li>" for ind in pattern.get('indicators', [])])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        
        if result.get('risk_factors'):
            st.subheader("Risk Factors")
            rf_df = pd.DataFrame(result['risk_factors'][:10])
            st.dataframe(rf_df, use_container_width=True)
        
        if result.get('similar_cases'):
            st.subheader("Similar Historical Cases")
            cases_df = pd.DataFrame(result['similar_cases'])
            st.dataframe(cases_df[['name', 'year', 'amount_crore', 'fraud_type', 'detection_method']], use_container_width=True)
        
        st.subheader("ML Model Scores")
        ml_scores = result.get('ml_scores_detail', {})
        fig = go.Figure(data=[
            go.Bar(
                x=['Isolation Forest', 'Random Forest', 'XGBoost', 'Ensemble'],
                y=[ml_scores.get('isolation_forest_score', 0), ml_scores.get('random_forest_score', 0),
                   ml_scores.get('xgboost_score', 0), ml_scores.get('ensemble_score', 0)],
                marker_color=['#667eea', '#764ba2', '#f093fb', '#1E3A5F']
            )
        ])
        fig.update_layout(title="ML Model Fraud Scores", yaxis_title="Score (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("AI Expert Analysis"):
            with st.spinner("Generating AI analysis..."):
                ai_analysis = generate_ai_fraud_analysis(business_data, result)
                st.markdown(ai_analysis)
        
        with st.expander("Investigation Checklist"):
            checklist = get_investigation_checklist(result['risk_level'], result.get('matched_fraud_patterns'))
            for i, item in enumerate(checklist, 1):
                st.checkbox(f"{i}. {item}", key=f"check_{i}")
        
        pdf_bytes = generate_fraud_report_pdf(business_data, result, business_name)
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"fraud_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

elif page == "Small Vendor Analysis":
    st.markdown('<h1 class="main-header">Small Vendor Fraud Detection</h1>', unsafe_allow_html=True)
    st.markdown("### Detect fraud by street vendors, hawkers, and small businesses with limited data")
    
    tab1, tab2, tab3 = st.tabs(["Visual Intelligence", "Lifestyle Analysis", "Network Analysis"])
    
    with tab1:
        st.subheader("Visual Intelligence Analysis")
        st.markdown("Upload a photo of the vendor stall for AI-powered analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            vendor_name = st.text_input("Vendor Name", key="vi_vendor_name")
            vendor_type = st.selectbox("Vendor Type", SMALL_VENDOR_TYPES, key="vi_vendor_type")
            location_desc = st.text_input("Location Description", placeholder="e.g., Near Railway Station, Main Market")
            declared_monthly = st.number_input("Declared Monthly Revenue (Rs.)", min_value=0.0, value=30000.0, step=1000.0)
        
        with col2:
            uploaded_photo = st.file_uploader("Upload Stall Photo", type=['jpg', 'jpeg', 'png'])
            
            if uploaded_photo:
                st.image(uploaded_photo, caption="Uploaded Stall Photo", use_container_width=True)
        
        if st.button("Analyze with Visual Intelligence", key="analyze_visual"):
            if uploaded_photo:
                with st.spinner("Analyzing photo with AI..."):
                    photo_bytes = uploaded_photo.read()
                    photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
                    
                    visual_result = analyze_vendor_stall_photo(photo_base64, vendor_type)
                    
                    st.session_state.visual_analysis = visual_result
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Estimated Stall Size", f"{visual_result.get('stall_size_estimate', 0)} sq ft")
                    with col2:
                        st.metric("Stock Value", f"Rs.{visual_result.get('stock_value_estimate', 0):,.0f}")
                    with col3:
                        st.metric("Legitimacy Score", f"{visual_result.get('legitimacy_score', 0)}/100")
                    
                    st.subheader("Daily Revenue Estimate")
                    daily_est = visual_result.get('daily_revenue_estimate', {})
                    st.write(f"Estimated: Rs.{daily_est.get('low', 0):,.0f} - Rs.{daily_est.get('high', 0):,.0f} per day")
                    
                    declared_data = {"declared_revenue": declared_monthly * 12, "total_land_sqft": 50}
                    comparison = compare_declared_vs_visual(declared_data, visual_result)
                    
                    if comparison.get('discrepancies'):
                        st.warning("Discrepancies Detected!")
                        for disc in comparison['discrepancies']:
                            st.markdown(f"- **[{disc['severity']}]** {disc.get('description', disc.get('type', 'Unknown'))}")
                    
                    red_flags = visual_result.get('red_flags', [])
                    if red_flags:
                        st.error("Red Flags from Visual Analysis:")
                        for flag in red_flags:
                            st.markdown(f"- {flag}")
            else:
                st.warning("Please upload a photo to analyze")
    
    with tab2:
        st.subheader("Lifestyle vs Income Analysis")
        st.markdown("Detect discrepancies between declared income and visible lifestyle")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Declared Income")
            vendor_name_ls = st.text_input("Vendor Name", key="ls_vendor_name")
            declared_annual = st.number_input("Declared Annual Income (Rs.)", min_value=0.0, value=300000.0, step=10000.0, key="ls_income")
        
        with col2:
            st.markdown("#### Lifestyle Indicators")
            vehicle = st.selectbox("Vehicle Ownership", LIFESTYLE_INDICATORS['vehicle_types'], key="ls_vehicle")
            property_type = st.selectbox("Property Ownership", LIFESTYLE_INDICATORS['property_ownership'], key="ls_property")
            education = st.selectbox("Children's Education", LIFESTYLE_INDICATORS['education_expense'], key="ls_education")
            num_children = st.number_input("Number of Children", min_value=0, max_value=10, value=2, key="ls_children")
            travel = st.selectbox("Travel Patterns", LIFESTYLE_INDICATORS['travel_patterns'], key="ls_travel")
            jewelry = st.selectbox("Jewelry Purchases", LIFESTYLE_INDICATORS['jewelry_purchases'], key="ls_jewelry")
            mobile = st.selectbox("Mobile Devices", LIFESTYLE_INDICATORS['mobile_devices'], key="ls_mobile")
        
        if st.button("Analyze Lifestyle Gap", key="analyze_lifestyle"):
            lifestyle_data = {
                "vehicle": vehicle,
                "property": property_type,
                "education": education,
                "num_children": num_children,
                "travel": travel,
                "jewelry": jewelry,
                "mobile_devices": mobile
            }
            
            with st.spinner("Analyzing lifestyle indicators..."):
                result = analyze_income_lifestyle_gap(declared_annual, lifestyle_data)
                st.session_state.lifestyle_analysis = result
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Estimated Annual Expenses", f"Rs.{result['estimated_annual_expense']:,.0f}")
                with col2:
                    st.metric("Income Gap", f"Rs.{result['income_gap']:,.0f}")
                with col3:
                    risk_class = f"risk-{result['risk_level'].lower()}"
                    st.markdown(f'<div class="{risk_class}">Risk: {result["risk_level"]}</div>', unsafe_allow_html=True)
                
                st.subheader("Expense Breakdown")
                expense_df = pd.DataFrame([
                    {"Category": k.replace("_", " ").title(), "Amount (Rs.)": v}
                    for k, v in result['expense_breakdown'].items()
                ])
                
                fig = px.pie(expense_df, values='Amount (Rs.)', names='Category', 
                            title='Estimated Annual Expenses by Category')
                st.plotly_chart(fig, use_container_width=True)
                
                if result['indicators']:
                    st.error("Risk Indicators Detected:")
                    for ind in result['indicators']:
                        st.markdown(f"- **[{ind['severity']}]** {ind['description']}")
                
                st.info(result['recommendation'])
    
    with tab3:
        st.subheader("Network Analysis")
        st.markdown("Map connections between vendors, suppliers, and businesses")
        
        st.markdown("#### Primary Vendor")
        primary_name = st.text_input("Vendor Name", key="net_vendor_name")
        primary_type = st.selectbox("Vendor Type", SMALL_VENDOR_TYPES, key="net_vendor_type")
        primary_risk = st.slider("Initial Risk Score", 0, 100, 30, key="net_risk")
        
        st.markdown("#### Connected Entities")
        st.markdown("Add entities connected to this vendor (suppliers, family, businesses)")
        
        if 'network_entities' not in st.session_state:
            st.session_state.network_entities = []
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            entity_name = st.text_input("Entity Name", key="add_entity_name")
        with col2:
            entity_type = st.selectbox("Type", ["person", "business", "supplier", "family", "bank"], key="add_entity_type")
        with col3:
            connection_type = st.selectbox("Connection", ["financial", "family", "business", "common_address"], key="add_conn_type")
        with col4:
            if st.button("Add Entity"):
                if entity_name:
                    st.session_state.network_entities.append({
                        "id": f"entity_{len(st.session_state.network_entities)}",
                        "name": entity_name,
                        "type": entity_type,
                        "connection_type": connection_type,
                        "risk_score": 20
                    })
        
        if st.session_state.network_entities:
            st.markdown("**Connected Entities:**")
            for i, entity in enumerate(st.session_state.network_entities):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"- {entity['name']} ({entity['type']}) - {entity['connection_type']}")
                with col2:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.network_entities.pop(i)
                        st.rerun()
        
        if st.button("Analyze Network", key="analyze_network"):
            if primary_name:
                with st.spinner("Building and analyzing network..."):
                    primary_vendor = {
                        "id": "primary",
                        "name": primary_name,
                        "business_type": primary_type,
                        "risk_score": primary_risk,
                        "declared_revenue": 300000
                    }
                    
                    network = build_vendor_network(primary_vendor, st.session_state.network_entities)
                    network_result = network.analyze_network()
                    st.session_state.network_analysis = network_result
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Entities", network_result['total_entities'])
                    with col2:
                        st.metric("Total Connections", network_result['total_connections'])
                    with col3:
                        st.metric("Network Risk Score", f"{network_result['network_risk_score']}/100")
                    
                    if network_result.get('suspicious_connections'):
                        st.error("Suspicious Connections Detected:")
                        for conn in network_result['suspicious_connections']:
                            st.markdown(f"- **[{conn['risk']}]** {conn['from_name']} → {conn['to_name']}: {conn['description']}")
                    
                    if network_result.get('high_risk_clusters'):
                        st.warning("High Risk Clusters:")
                        for cluster in network_result['high_risk_clusters']:
                            st.markdown(f"- Hub: {cluster['hub_name']} ({cluster['connection_count']} connections, Risk: {cluster['risk_score']}%)")
                    
                    viz_data = network.get_network_visualization_data()
                    if viz_data['nodes']:
                        nodes_df = pd.DataFrame(viz_data['nodes'])
                        fig = px.scatter(nodes_df, x='risk_score', y='size', 
                                        color='type', size='size', hover_name='label',
                                        title='Network Entity Risk Distribution')
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please enter vendor name")

elif page == "Field Officer Mode":
    st.markdown('<h1 class="main-header">Field Officer Interface</h1>', unsafe_allow_html=True)
    st.markdown("### Mobile-friendly interface for on-ground investigations")
    
    st.markdown("""
    <style>
    .field-card { background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #667eea; }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Quick Analysis", "Photo Capture", "Report Findings"])
    
    with tab1:
        st.subheader("Quick Vendor Assessment")
        
        vendor_name = st.text_input("Vendor Name", key="fo_vendor")
        vendor_type = st.selectbox("Type", SMALL_VENDOR_TYPES, key="fo_type")
        location = st.text_input("Location/GPS", key="fo_location")
        
        st.markdown("#### Quick Indicators")
        col1, col2 = st.columns(2)
        with col1:
            stall_size = st.select_slider("Stall Size", options=["Very Small", "Small", "Medium", "Large", "Very Large"])
            stock_quality = st.select_slider("Stock Quality", options=["Poor", "Basic", "Good", "Premium", "Luxury"])
        with col2:
            customer_flow = st.select_slider("Customer Flow", options=["None", "Low", "Medium", "High", "Very High"])
            visible_luxury = st.multiselect("Visible Luxury Items", 
                                           ["Expensive Phone", "Gold Jewelry", "Branded Clothes", "Expensive Watch", "Car Keys"])
        
        declared_monthly = st.number_input("Declared Monthly Income (Rs.)", value=30000.0, step=5000.0, key="fo_income")
        
        if st.button("Quick Risk Assessment", key="fo_assess", use_container_width=True):
            risk_score = 0
            indicators = []
            
            if stall_size in ["Very Small", "Small"] and declared_monthly > 50000:
                risk_score += 30
                indicators.append("High income for small stall")
            
            if stock_quality in ["Premium", "Luxury"] and declared_monthly < 50000:
                risk_score += 25
                indicators.append("Premium stock with low declared income")
            
            if len(visible_luxury) >= 2:
                risk_score += 20 * len(visible_luxury)
                indicators.append(f"{len(visible_luxury)} luxury items visible")
            
            if customer_flow == "None" and declared_monthly > 30000:
                risk_score += 25
                indicators.append("No customers but high declared revenue")
            
            risk_score = min(100, risk_score)
            
            if risk_score >= 70:
                risk_level = "CRITICAL"
                color = "#dc3545"
            elif risk_score >= 50:
                risk_level = "HIGH"
                color = "#fd7e14"
            elif risk_score >= 30:
                risk_level = "MODERATE"
                color = "#ffc107"
            else:
                risk_level = "LOW"
                color = "#28a745"
            
            st.markdown(f"""
            <div style="background-color: {color}; color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                <h2>Risk Score: {risk_score}/100</h2>
                <h3>Level: {risk_level}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if indicators:
                st.warning("Risk Indicators:")
                for ind in indicators:
                    st.markdown(f"- {ind}")
    
    with tab2:
        st.subheader("Photo Documentation")
        
        photo_type = st.selectbox("Photo Type", 
                                 ["Stall Front", "Stock/Inventory", "Transaction", "Lifestyle Item", "Document"])
        
        camera_photo = st.camera_input("Take Photo")
        
        if camera_photo:
            st.image(camera_photo, caption=f"{photo_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            photo_bytes = camera_photo.read()
            photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
            
            if st.button("Analyze Photo", key="fo_analyze_photo"):
                with st.spinner("Analyzing..."):
                    if photo_type == "Stall Front":
                        result = analyze_vendor_stall_photo(photo_base64)
                        st.json(result)
                    else:
                        st.info("Photo saved for documentation")
    
    with tab3:
        st.subheader("Report Findings")
        
        investigation_id = st.text_input("Investigation ID", key="fo_inv_id")
        officer_name = st.text_input("Officer Name", key="fo_officer")
        officer_id = st.text_input("Officer ID", key="fo_officer_id")
        
        findings = st.text_area("Investigation Findings", height=200, key="fo_findings")
        
        priority = st.select_slider("Priority", options=["Low", "Normal", "High", "Urgent", "Critical"])
        follow_up = st.checkbox("Follow-up Required")
        
        if st.button("Submit Report", key="fo_submit", use_container_width=True):
            if officer_name and findings:
                report_data = {
                    "officer_name": officer_name,
                    "officer_id": officer_id,
                    "investigation_status": "completed",
                    "priority": priority.lower(),
                    "notes": findings,
                    "follow_up_required": follow_up
                }
                
                report_id = save_field_investigation(report_data)
                if report_id:
                    st.success(f"Report submitted successfully! ID: {report_id}")
                else:
                    st.error("Error saving report")
            else:
                st.warning("Please fill in required fields")

elif page == "Analysis History":
    st.markdown('<h1 class="main-header">Analysis History</h1>', unsafe_allow_html=True)
    
    records = get_all_analysis_records()
    
    if records:
        st.subheader(f"Total Records: {len(records)}")
        
        df = pd.DataFrame(records)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_filter = st.multiselect("Filter by Risk Level", 
                                        ["LOW", "MODERATE", "HIGH", "VERY HIGH", "CRITICAL"],
                                        default=["HIGH", "VERY HIGH", "CRITICAL"])
        with col2:
            type_filter = st.multiselect("Filter by Business Type", df['business_type'].unique().tolist())
        with col3:
            vendor_only = st.checkbox("Show Small Vendors Only")
        
        filtered_df = df.copy()
        if risk_filter:
            filtered_df = filtered_df[filtered_df['risk_level'].isin(risk_filter)]
        if type_filter:
            filtered_df = filtered_df[filtered_df['business_type'].isin(type_filter)]
        if vendor_only:
            filtered_df = filtered_df[filtered_df['is_small_vendor'] == True]
        
        st.dataframe(
            filtered_df[['id', 'created_at', 'business_name', 'business_type', 
                        'fraud_probability', 'risk_level', 'is_small_vendor']],
            use_container_width=True
        )
        
        selected_id = st.selectbox("Select Record to View Details", filtered_df['id'].tolist())
        
        if selected_id:
            record = get_analysis_by_id(selected_id)
            if record:
                st.markdown("---")
                st.subheader(f"Details: {record.get('business_name', 'N/A')}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fraud Probability", f"{record['fraud_probability']:.1f}%")
                with col2:
                    st.metric("Risk Level", record['risk_level'])
                with col3:
                    st.metric("ML Score", f"{record['ml_score']:.1f}%")
                
                st.info(record.get('recommendation', 'No recommendation available'))
    else:
        st.info("No analysis records found. Start by analyzing a business.")

elif page == "Dashboard":
    st.markdown('<h1 class="main-header">Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    records = get_all_analysis_records()
    
    if records:
        df = pd.DataFrame(records)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="metric-card"><h3>Total Analyses</h3><h1>' + str(len(records)) + '</h1></div>', unsafe_allow_html=True)
        with col2:
            high_risk = len(df[df['risk_level'].isin(['HIGH', 'VERY HIGH', 'CRITICAL'])])
            st.markdown(f'<div class="metric-card"><h3>High Risk Cases</h3><h1>{high_risk}</h1></div>', unsafe_allow_html=True)
        with col3:
            avg_prob = df['fraud_probability'].mean()
            st.markdown(f'<div class="metric-card"><h3>Avg Fraud Prob</h3><h1>{avg_prob:.1f}%</h1></div>', unsafe_allow_html=True)
        with col4:
            vendor_count = len(df[df['is_small_vendor'] == True])
            st.markdown(f'<div class="metric-card"><h3>Vendor Cases</h3><h1>{vendor_count}</h1></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Risk Distribution")
            risk_dist = get_risk_distribution()
            if risk_dist:
                fig = px.pie(
                    values=list(risk_dist.values()),
                    names=list(risk_dist.keys()),
                    color=list(risk_dist.keys()),
                    color_discrete_map={
                        'LOW': '#28a745', 'MODERATE': '#ffc107', 
                        'HIGH': '#fd7e14', 'VERY HIGH': '#dc3545', 'CRITICAL': '#721c24'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Fraud Probability by Business Type")
            type_stats = get_business_type_fraud_stats()
            if type_stats:
                type_df = pd.DataFrame([
                    {"Business Type": k, "Avg Fraud Probability": v.get('avg_probability', 0), "Count": v['count']}
                    for k, v in type_stats.items()
                ]).sort_values('Avg Fraud Probability', ascending=False)
                
                fig = px.bar(type_df.head(10), x='Business Type', y='Avg Fraud Probability',
                            color='Avg Fraud Probability', color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("State-wise Analysis")
        state_stats = get_state_wise_stats()
        if state_stats:
            state_df = pd.DataFrame([
                {"State": k, "Cases": v['count'], "High Risk": v['high_risk_count'], 
                 "Avg Probability": v.get('avg_probability', 0)}
                for k, v in state_stats.items()
            ]).sort_values('High Risk', ascending=False)
            
            fig = px.bar(state_df.head(15), x='State', y=['Cases', 'High Risk'],
                        barmode='group', title='Cases by State')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Fraud Probability Trend")
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        trend_df = df.groupby('date')['fraud_probability'].mean().reset_index()
        
        fig = px.line(trend_df, x='date', y='fraud_probability', 
                     title='Average Fraud Probability Over Time')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for dashboard. Start by analyzing businesses.")

elif page == "Fraud Patterns":
    st.markdown('<h1 class="main-header">Fraud Patterns Library</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Known Patterns", "Small Vendor Patterns", "Historical Cases"])
    
    with tab1:
        st.subheader("Known Fraud Patterns")
        
        for fraud_type, details in FRAUD_TYPES.items():
            with st.expander(f"{details['name']} (Risk Weight: {details['risk_weight']})"):
                st.markdown(f"**Description:** {details['description']}")
                st.markdown("**Key Indicators:**")
                for indicator in details['key_indicators']:
                    st.markdown(f"- {indicator}")
    
    with tab2:
        st.subheader("Small Vendor Fraud Patterns")
        
        for pattern_type, details in SMALL_VENDOR_FRAUD_PATTERNS.items():
            with st.expander(f"{details['name']} (Risk Weight: {details['risk_weight']})"):
                st.markdown(f"**Description:** {details['description']}")
                st.markdown("**Key Indicators:**")
                for indicator in details['key_indicators']:
                    st.markdown(f"- {indicator}")
    
    with tab3:
        st.subheader("Major Historical Fraud Cases")
        
        cases_df = pd.DataFrame(MAJOR_INDIAN_FRAUD_CASES)
        cases_df = cases_df.sort_values('amount_crore', ascending=False)
        
        fig = px.bar(cases_df, x='name', y='amount_crore', color='fraud_type',
                    title='Major Fraud Cases by Amount (Rs. Crore)')
        st.plotly_chart(fig, use_container_width=True)
        
        for case in MAJOR_INDIAN_FRAUD_CASES:
            with st.expander(f"{case['name']} ({case['year']}) - Rs.{case['amount_crore']:,} Crore"):
                st.markdown(f"**Fraud Type:** {case['fraud_type']}")
                st.markdown(f"**Description:** {case['description']}")
                st.markdown(f"**Detection Method:** {case['detection_method']}")
                st.markdown("**Key Indicators:**")
                for indicator in case['key_indicators']:
                    st.markdown(f"- {indicator}")

elif page == "About":
    st.markdown('<h1 class="main-header">About This System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Tax Fraud Detection System
    ### Income Tax Department of India
    
    This advanced fraud detection system is designed to help tax officers identify potential tax fraud 
    and evasion cases across all business types, with special capabilities for detecting fraud by 
    small vendors and street vendors who operate with minimal documented business footprints.
    
    ### Key Features
    
    #### 1. Business Analysis
    - Multi-model ML ensemble (Isolation Forest, Random Forest, XGBoost)
    - Benchmark-based anomaly detection
    - Pattern matching against known fraud cases
    - AI-powered expert analysis
    
    #### 2. Small Vendor Detection
    - **Visual Intelligence**: AI analysis of vendor stall photos
    - **Lifestyle Analysis**: Income vs expenses gap detection
    - **Network Analysis**: Connection mapping for shell networks
    - **Cash Flow Estimation**: Alternative data for cash-heavy businesses
    
    #### 3. Field Officer Tools
    - Mobile-friendly interface
    - Photo capture and analysis
    - Quick assessment tools
    - Investigation reporting
    
    ### Fraud Types Detected
    - Shell Companies
    - Money Laundering
    - Black Money/Cash Hoarding
    - Circular Trading
    - Benami Property
    - Front Operations
    - Cash Layering Networks
    
    ### Legal Framework
    - Income Tax Act, 1961
    - Prevention of Money Laundering Act (PMLA)
    - Benami Transactions (Prohibition) Act
    - Black Money Act, 2015
    
    ---
    
    **Disclaimer**: This system is a decision-support tool designed to assist tax investigators. 
    All findings require verification through proper investigative procedures. The system's 
    assessments should not be considered definitive proof of any wrongdoing.
    
    **Version**: 2.0 (Enhanced Small Vendor Detection)
    **Last Updated**: December 2025
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("##### System Status")
st.sidebar.markdown("Database: Connected" if init_db() else "Database: Error")
st.sidebar.markdown(f"Records: {len(get_all_analysis_records())}")
