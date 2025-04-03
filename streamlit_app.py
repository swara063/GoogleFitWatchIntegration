import streamlit as st
import googlefit_auth as gfit
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Google Fit Watch Integration", layout="wide")

st.title("Google Fit Watch Integration")

# File Upload
st.title("Google Fit Watch Integration")
uploaded_file = st.file_uploader("Upload your Google Fit OAuth JSON file", type="json")

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("client_secret.json", "wb") as f:
        f.write(uploaded_file.getbuffer())


# Step 1: Authenticate User
if "credentials" not in st.session_state:
    if st.button("Authenticate with Google Fit"):
        auth_url, flow = gfit.authenticate_google_fit()
        st.session_state["auth_url"] = auth_url
        st.session_state["flow"] = flow
        st.write(f"[Click here to authenticate]({auth_url})")

if "auth_url" in st.session_state:
    auth_code = st.text_input("Paste the authentication code here:")
    if auth_code:
        creds_json = gfit.fetch_google_fit_token(auth_code, st.session_state["flow"])
        st.session_state["credentials"] = creds_json
        st.success("Authentication successful!")

# Step 2: Fetch & Display Data
if "credentials" in st.session_state:
    if st.button("Fetch Google Fit Data"):
        data = gfit.fetch_google_fit_data(st.session_state["credentials"])
        st.session_state["health_data"] = data
        st.success("Data fetched successfully!")

# Step 3: Real-Time Visualization
if "health_data" in st.session_state:
    st.subheader("📊 Live Health Data from Watch")
    
    # Layout with 3 columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="💓 Heart Rate (BPM)", value=data.get("Heart Rate", "N/A"))
    
    with col2:
        bp_data = data.get("Blood Pressure", "N/A")
        if isinstance(bp_data, list) and len(bp_data) > 1:
            bp_value = f"{bp_data[0]['fpVal']}/{bp_data[1]['fpVal']} mmHg"
        else:
            bp_value = "N/A"
        st.metric(label="🩸 Blood Pressure", value=bp_value)

    with col3:
        spo2_data = data.get("SpO2 (Oxygen)", "N/A")
        spo2_value = f"{spo2_data[0]['fpVal']}%" if isinstance(spo2_data, list) else "N/A"
        st.metric(label="🧬 SpO2 (Oxygen Level)", value=spo2_value)

    # Live updating section
    st.subheader("📈 Live Trends")
    
    # Graphing heart rate over time
    fig = go.Figure()
    heart_rate_values = [data.get("Heart Rate", 0)]
    
    fig.add_trace(go.Scatter(y=heart_rate_values, mode="lines+markers", name="Heart Rate"))
    
    fig.update_layout(title="Heart Rate Over Time",
                      xaxis_title="Time (Auto-refreshing)",
                      yaxis_title="Heart Rate (BPM)",
                      template="plotly_dark")
    
    chart_placeholder = st.empty()

    # Live Update Loop
    while st.button("Start Live Monitoring"):
        new_data = gfit.fetch_google_fit_data(st.session_state["credentials"])
        heart_rate_values.append(new_data.get("Heart Rate", 0))
        if len(heart_rate_values) > 50:
            heart_rate_values.pop(0)  # Keep last 50 data points
        
        fig.data[0].y = heart_rate_values
        chart_placeholder.plotly_chart(fig, use_container_width=True)
        time.sleep(5)  # Refresh every 5 seconds

