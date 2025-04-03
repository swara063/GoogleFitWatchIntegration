import streamlit as st
import googlefit_auth as gfit
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Google Fit Watch Integration", layout="wide")
st.title("Google Fit Watch Integration")

# Step 1: Upload JSON file
uploaded_file = st.file_uploader("Upload your Google Fit OAuth JSON file", type="json")

if uploaded_file is not None:
    json_path = "client_secret.json"
    with open(json_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success("OAuth JSON uploaded successfully!")

    # Step 2: Authenticate Google Fit
    try:
        auth_url, flow = gfit.authenticate_google_fit(json_path)
        st.write("Click the link below to authenticate with Google Fit:")
        st.markdown(f"[Authenticate here]({auth_url})")
        st.session_state["flow"] = flow
    except Exception as e:
        st.error(f"Authentication failed: {e}")

# Step 3: Enter Authorization Code
if "flow" in st.session_state:
    auth_code = st.text_input("Paste the authentication code here:")
    if auth_code:
        try:
            creds_json = gfit.fetch_google_fit_token(auth_code, st.session_state["flow"])
            st.session_state["credentials"] = creds_json
            st.success("Authentication successful!")
        except Exception as e:
            st.error(f"Token exchange failed: {e}")

# Step 4: Fetch & Display Data
if "credentials" in st.session_state:
    if st.button("Fetch Google Fit Data"):
        data = gfit.fetch_google_fit_data(st.session_state["credentials"])
        st.session_state["health_data"] = data
        st.success("Data fetched successfully!")

# Step 5: Real-Time Visualization
if "health_data" in st.session_state:
    st.subheader("📊 Live Health Data from Watch")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="💓 Heart Rate (BPM)", value=st.session_state["health_data"].get("Heart Rate", "N/A"))
    
    with col2:
        bp_data = st.session_state["health_data"].get("Blood Pressure", "N/A")
        bp_value = f"{bp_data[0]['fpVal']}/{bp_data[1]['fpVal']} mmHg" if isinstance(bp_data, list) and len(bp_data) > 1 else "N/A"
        st.metric(label="🩸 Blood Pressure", value=bp_value)
    
    with col3:
        spo2_data = st.session_state["health_data"].get("SpO2 (Oxygen)", "N/A")
        spo2_value = f"{spo2_data[0]['fpVal']}%" if isinstance(spo2_data, list) else "N/A"
        st.metric(label="🧬 SpO2 (Oxygen Level)", value=spo2_value)

    st.subheader("📈 Live Trends")
    fig = go.Figure()
    heart_rate_values = [st.session_state["health_data"].get("Heart Rate", 0)]
    
    fig.add_trace(go.Scatter(y=heart_rate_values, mode="lines+markers", name="Heart Rate"))
    
    fig.update_layout(title="Heart Rate Over Time",
                      xaxis_title="Time (Auto-refreshing)",
                      yaxis_title="Heart Rate (BPM)",
                      template="plotly_dark")
    
    chart_placeholder = st.empty()

    if st.button("Start Live Monitoring"):
        while True:
            new_data = gfit.fetch_google_fit_data(st.session_state["credentials"])
            heart_rate_values.append(new_data.get("Heart Rate", 0))
            if len(heart_rate_values) > 50:
                heart_rate_values.pop(0)
            
            fig.data[0].y = heart_rate_values
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(5)

