import streamlit as st
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

st.set_page_config(page_title="Watch Data - Google Fit", layout="wide")

# Load Google OAuth Credentials
CLIENT_SECRETS_FILE = "client_secrets.json"

def authenticate_google_fit():
    """Authenticate user with Google Fit API"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=["https://www.googleapis.com/auth/fitness.activity.read"],
        redirect_uri="https://your-streamlit-app-url"  # Change this after deployment
    )
    
    auth_url, _ = flow.authorization_url(prompt='consent')
    st.session_state['flow'] = flow  # Save flow state
    return auth_url

def fetch_google_fit_data():
    """Fetch fitness data from Google Fit API"""
    if "credentials" not in st.session_state:
        st.error("Please authenticate first.")
        return None

    creds = Credentials.from_authorized_user_info(st.session_state["credentials"])
    service = build("fitness", "v1", credentials=creds)

    data = service.users().dataSources().list(userId="me").execute()
    return data

# Streamlit UI
st.title("Google Fit Watch Integration")

if "credentials" not in st.session_state:
    if st.button("Authenticate with Google Fit"):
        st.session_state["auth_url"] = authenticate_google_fit()
        st.write(f"[Click here to authenticate]({st.session_state['auth_url']})")

if "auth_url" in st.session_state:
    auth_code = st.text_input("Paste the authentication code here:")
    if auth_code:
        flow = st.session_state["flow"]
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        st.session_state["credentials"] = json.loads(creds.to_json())
        st.success("Authentication successful!")

if st.button("Fetch Google Fit Data"):
    data = fetch_google_fit_data()
    st.json(data)
