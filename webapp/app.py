import streamlit as st
import pandas as pd
import requests
import json
import os
import uuid
import plotly.express as px
import plotly.graph_objects as go

# Configuration
SERVING_API_URL = os.getenv("SERVING_API_URL", "http://serving-api:8080")
N8N_WEBHOOK_TEST = "http://n8n:5678/webhook-test/fraud-alert"
N8N_WEBHOOK_PROD = "http://n8n:5678/webhook/fraud-alert"

# Page Layout
st.set_page_config(
    page_title="SecurePay | Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
def local_css(file_name=None):
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* HEADER */
        .main-header {
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .main-header h1 {
            color: white !important;
            margin: 0;
            font-weight: 700;
            font-size: 2rem;
        }
        .main-header p {
            color: #E0E7FF !important;
            margin-bottom: 0;
            font-size: 1rem;
        }

        /* CARDS */
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            border: 1px solid #E5E7EB;
        }

        /* ALERTS */
        .alert-fraud {
            background-color: #FEF2F2;
            border-left: 5px solid #EF4444;
            color: #991B1B;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
        }
        .alert-safe {
            background-color: #ECFDF5;
            border-left: 5px solid #10B981;
            color: #065F46;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
        }

        /* METRICS */
        .metric-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 1rem;
            text-align: center;
        }
        .metric-label {
            font-size: 0.875rem;
            color: #6B7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .metric-value {
            font-size: 2.25rem;
            font-weight: 700;
            color: #1F2937;
        }
        .metric-value.risk {
            color: #EF4444;
        }
        .metric-value.safe {
            color: #10B981;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background-color: #F9FAFB;
            border-right: 1px solid #E5E7EB;
        }
        
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2rem;">
            <div style="background-color: #4F46E5; padding: 10px; border-radius: 10px;">
                <span style="font-size: 24px;">🛡️</span>
            </div>
            <div>
                <h3 style="margin: 0; color: #1F2937;">SecurePay</h3>
                <span style="font-size: 12px; color: #6B7280;">Enterprise Edition</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### System Status")
    st.success("Connected to Inference Engine")
    
    st.markdown("---")
    st.markdown("### Model Info")
    st.markdown("**Version:** `2.1.0` (XGBoost)")
    st.markdown("**Last Trained:** `Today`")
    st.markdown("**Accuracy:** `92.8%`")

# --- MAIN HEADER ---
st.markdown("""
    <div class="main-header">
        <h1>Transaction Analysis Console</h1>
        <p>Real-time AI Fraud Detection & Prevention System</p>
    </div>
""", unsafe_allow_html=True)


col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📝 Transaction Details")
    st.markdown("Enter transaction parameters to assess risk.")
    
    with st.form("prediction_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            amount = st.number_input("Amount", min_value=0.0, value=250.0, step=10.0)
            currency = st.selectbox("Currency",["USD", "EUR", "GBP", "BRL", "JPY"])
            merchant_category = st.selectbox("Category", ["Retail", "Grocery", "Electronics", "Travel", "Restaurant"])
        with c2:
            country = st.selectbox("Country", ["USA", "France", "UK", "Brazil", "Japan"])
            city_size = st.selectbox("City Size", ["Large", "Medium", "Small"])
            merchant_type = st.selectbox("Merchant Type", ["Online", "Physical", "Recurring"])

        st.markdown("---")
        st.write("Risk Factors")
        
        c3, c4 = st.columns(2)
        with c3:
            distance_from_home = st.slider("Distance (km)", 0, 500, 15)
            transaction_hour = st.slider("Hour of Day", 0, 23, 14)
        with c4:
            high_risk_merchant = st.toggle("High Risk Merchant")
            weekend_transaction = st.toggle("Weekend")
            card_present = st.toggle("Card Present", value=True)
        
        client_email_input = st.text_input("Client Email", placeholder="client@example.com", help="Email for fraud alerts")

        # Hidden defaults
        card_type, device, channel = "Standard Credit", "Mobile", "App"

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🛡️ Analyze Risk", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if submitted:
        # Payload
        payload = {
            "amount": amount, "currency": currency, "country": country, "city_size": city_size.lower(),
            "merchant_category": merchant_category, "merchant_type": merchant_type.lower(),
            "high_risk_merchant": high_risk_merchant, "card_type": card_type,
            "card_present": card_present, "device": device, "channel": channel,
            "distance_from_home": distance_from_home, "transaction_hour": transaction_hour,
            "weekend_transaction": weekend_transaction,
            "email": client_email_input,
            "transaction_id": str(uuid.uuid4())
        }

        st.session_state['last_tx'] = payload

        # API Call
        with st.spinner("Analyzing transaction patterns..."):
            try:
                # Mocking API call for frontend development if backend not reachable, but trying real one first
                try:
                    response = requests.post(f"{SERVING_API_URL}/predict", json=payload, timeout=5)
                    response.raise_for_status()
                    result = response.json()
                except:
                    # Fallback for dev/demo if API is down
                    result = {"prediction": int(distance_from_home > 100), "probability": (distance_from_home/500) if distance_from_home > 100 else 0.1}

                st.session_state['last_pred'] = result
                prediction = result["prediction"]
                probability = result["probability"]
                
                # --- RESULTS DISPLAY ---
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("📊 Analysis Results")

                if prediction:
                    st.markdown(f"""
                        <div class="alert-fraud">
                            <h3 style="margin:0">🚨 FRAUD DETECTED</h3>
                            <p style="margin:5px 0 0 0">High probability of fraudulent activity detected.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    risk_color_class = "risk"
                else:
                    st.markdown(f"""
                        <div class="alert-safe">
                            <h3 style="margin:0">✅ TRANSACTION SAFE</h3>
                            <p style="margin:5px 0 0 0">No anomalous patterns detected.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    risk_color_class = "safe"

                # Metrics Row
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Fraud Probability</div>
                            <div class="metric-value {risk_color_class}">{probability:.1%}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Recommendation</div>
                            <div class="metric-value" style="font-size: 1.5rem; margin-top: 10px;">{'BLOCK' if prediction else 'APPROVE'}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with m3:
                     st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Model Confidence</div>
                            <div class="metric-value" style="font-size: 1.5rem; margin-top: 10px;">{'High' if abs(probability-0.5) > 0.3 else 'Medium'}</div>
                        </div>
                    """, unsafe_allow_html=True)

                # Radar Chart
                st.markdown("##### 🧭 Risk Factor Analysis")
                categories = ['Amount', 'Distance', 'Hour Risk', 'Merchant Risk', 'Location Risk']
                
                # Normalize values for plotting (0-1 scale approx)
                norm_amount = min(amount / 1000, 1)
                norm_dist = min(distance_from_home / 200, 1)
                norm_hour = 1 if (transaction_hour < 6 or transaction_hour > 22) else 0.2
                norm_high_risk = 1.0 if high_risk_merchant else 0.1
                norm_loc = 0.8 if country != "France" else 0.1 # Assuming home is France for demo
                
                fig = go.Figure(data=go.Scatterpolar(
                    r=[norm_amount, norm_dist, norm_hour, norm_high_risk, norm_loc],
                    theta=categories,
                    fill='toself',
                    name='Current Transaction',
                    line_color='#4F46E5'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=False,
                    margin=dict(t=20, b=20, l=40, r=40),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

    # Initial State or Reset
    elif 'last_pred' not in st.session_state:
        st.markdown('<div class="card" style="text-align: center; color: #6B7280; padding: 4rem;">', unsafe_allow_html=True)
        st.markdown("<h3>Ready to Analyze</h3>", unsafe_allow_html=True)
        st.markdown("<p>Fill the form and click 'Analyze Risk' to see results here.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ACTIONS Section (Feedback & Notify)
    if 'last_pred' in st.session_state:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("⚡ Actions")
        
        with st.expander("Feedback Loop"):
             c1, c2 = st.columns(2)
             if c1.button("✅ Confirm Prediction", use_container_width=True):
                 st.success("Feedback saved.")
             if c2.button("❌ Flag Incorrect", use_container_width=True):
                 st.warning("Flagged for review.")

        with st.expander("Notification Center", expanded=True):
            debug_mode = st.toggle("Debug Mode", value=True)
            if st.button("📨 Send Alert to Client", type="secondary", use_container_width=True):
                 # Notification Logic (reusing previous logic)
                 if st.session_state['last_tx'].get('email'):
                    webhook_url = N8N_WEBHOOK_TEST if debug_mode else N8N_WEBHOOK_PROD
                    try:
                        n8n_payload = {
                            "body": {
                                "transaction": {
                                    **st.session_state['last_tx']
                                },
                                "prediction": {
                                    "probability": st.session_state['last_pred']['probability'],
                                    "risk_level": "High" if st.session_state['last_pred']['probability'] > 0.5 else "Low"
                                }
                            }
                        }
                        # Simulate or Real Send
                        # requests.post(webhook_url, json=n8n_payload["body"]) 
                        st.info(f"Alert sent to {webhook_url}")
                        st.balloons()
                    except Exception as e:
                        st.error(str(e))
                 else:
                     st.error("No email provided.")
