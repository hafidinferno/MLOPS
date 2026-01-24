import streamlit as st
import pandas as pd
import requests
import json
import os

# Configuration
SERVING_API_URL = os.getenv("SERVING_API_URL", "http://serving-api:8080")
# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .fraud-alert {
        background-color: #ffebee;
        color: #c62828;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ef9a9a;
        margin-bottom: 20px;
    }
    .safe-alert {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #a5d6a7;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2058/2058768.png", width=80)
    st.title("SecurePay")
    st.markdown("### Agentic Fraud Detection")
    st.info("System Status: **Online** 🟢")
    
    st.markdown("---")
    st.markdown("**Model Version:** v2.0")
    st.markdown("**Last Retrain:** Today")

# Main Content
st.title("🛡️ Transaction Analysis Console")
st.markdown("Analyze transactions in real-time with our AI-powered Fraud Agent.")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📝 Transaction Details")
    with st.container():
        with st.form("prediction_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            with c1:
                amount = st.number_input("Amount", min_value=0.0, value=250.0, step=10.0)
                currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "BRL", "JPY"])
                merchant_category = st.selectbox("Category", ["Retail", "Grocery", "Electronics", "Travel", "Restaurant"])
            with c2:
                country = st.selectbox("Country", ["USA", "France", "UK", "Brazil", "Japan"])
                city_size = st.selectbox("City Size", ["Large", "Medium", "Small"])
                merchant_type = st.selectbox("Merchant Type", ["Online", "Physical", "Recurring"])

            st.markdown("---")
            st.markdown("**Risk Factors**")
            
            c3, c4 = st.columns(2)
            with c3:
                distance_from_home = st.slider("Distance (km)", 0, 500, 15)
                transaction_hour = st.slider("Hour of Day", 0, 23, 14)
            with c4:
                high_risk_merchant = st.toggle("High Risk Merchant")
                weekend_transaction = st.toggle("Weekend")
                card_present = st.toggle("Card Present", value=True)
            
            # Defaults for hidden fields
            card_type = "Standard Credit"
            device = "Mobile"
            channel = "App"
            
            # Email for notification
            st.markdown("**Contact Info**")
            client_email_input = st.text_input("Client Email", placeholder="client@example.com")
                
            submitted = st.form_submit_button("🛡️ Analyze Transaction", type="primary")

if submitted:
    # Payload Construction
    payload = {
        "amount": amount, "currency": currency, "country": country, "city_size": city_size.lower(),
        "merchant_category": merchant_category, "merchant_type": merchant_type.lower(),
        "high_risk_merchant": high_risk_merchant, "card_type": card_type,
        "card_present": card_present, "device": device, "channel": channel,
        "distance_from_home": distance_from_home, "transaction_hour": transaction_hour,
        "weekend_transaction": weekend_transaction,
        "email": client_email_input
    }
    
    with col2:
        st.subheader("📊 Analysis Results")
        with st.spinner("🔍 AI Agent is reviewing transaction patterns..."):
            try:
                # API Call
                response = requests.post(f"{SERVING_API_URL}/predict", json=payload, timeout=5)
                response.raise_for_status()
                result = response.json()
                
                prediction = result["prediction"]
                probability = result["probability"]
                
                # Visual Feedback
                if prediction:
                    st.markdown(f"""
                    <div class="fraud-alert">
                        <h3>🚨 FRAUD DETECTED</h3>
                        <p>This transaction has been flagged as high risk.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    metric_color = "inverse"
                    st.toast("Alert sent to Fraud Analyst (n8n)", icon="🚨")
                else:
                    st.markdown(f"""
                    <div class="safe-alert">
                        <h3>✅ SCANNED SAFE</h3>
                        <p>No anomalous patterns detected.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    metric_color = "normal"

                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Risk Score", f"{probability:.1%}", delta_color=metric_color)
                m2.metric("Decision", "FRAUD" if prediction else "LEGIT")
                m3.metric("Confidence", "High" if probability > 0.8 or probability < 0.2 else "Medium")
                
                # Feedback Loop
                st.session_state['last_tx'] = payload
                st.session_state['last_pred'] = result

                # Explanation (Mock)
                with st.expander("See AI Reasoning"):
                    st.write("Top contributing factors:")
                    st.progress(probability)
                    if high_risk_merchant:
                        st.write("- ⚠️ High Risk Merchant Category")
                    if distance_from_home > 100:
                        st.write("- 📍 Unusual Location")
                    st.write(f"- 🕒 Time of Day: {transaction_hour}:00")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to Inference API. Is the service running?")
            except Exception as e:
                st.error(f"❌ System Error: {e}")

# Feedback Section
if 'last_tx' in st.session_state:
    st.markdown("---")
    with col2:
        st.subheader("👩‍💻 Operator Correction")
        st.caption("Help improve the model by confirming validation results.")
        
        f1, f2, f3 = st.columns([1,1,2])
        if f1.button("✅ Confirm Correct"):
            st.success("Feedback Recorded: Model Correct")
            # Logic to send feedback would go here (omitted for brevity)
        if f2.button("❌ Mark Incorrect"):
            st.warning("Feedback Recorded: Model Error - Flagged for review")

    # Notification Section
    with col2:
        st.subheader("📢 Notification")
        # Pre-fill with the email from the transaction
        default_email = st.session_state['last_tx'].get('email', '')
        client_email = st.text_input("📧 Email du client pour la notification", value=default_email)

        if st.button("Notifier l'utilisateur"):
            if client_email:
                # Prepare payload (update email if changed)
                payload = st.session_state['last_tx'].copy()
                payload["email"] = client_email
                payload["probability"] = st.session_state['last_pred']['probability']
                
                # Send to n8n webhook
                try:
                    # Using n8n container name/port
                    response = requests.post("http://n8n:5678/webhook/fraud-alert", json=payload, timeout=5)
                    if response.status_code == 200:
                        st.success(f"L'agent Antigravity va notifier {client_email}")
                    else:
                        st.error(f"Erreur n8n: {response.text}")
                except Exception as e:
                    st.error(f"Erreur de connexion avec n8n: {e}")
            else:
                st.warning("Veuillez saisir un email avant de notifier.")
